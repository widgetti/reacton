"""close(): not starved, no render after it, no self-deadlock, requests during it dropped."""

# ruff: noqa: F811  the fixture names shadow the pytest fixture parameters of the same names

import sys
import threading
from typing import List

import pytest

import reacton
import reacton.ipywidgets as w
from reacton import core

from ._threads_test_utils import TIMEOUT, Injected, Worker, call_in_thread, helper_errors, log_hook, stacks, wait_until  # noqa: F401


def test_close_with_batch_in_cleanup_does_not_deadlock():
    """A cleanup enters and leaves a batch (solara's store fire() does `with rc:`) while a render
    request is still marked. Before: the batch exit called render() on close()'s own thread,
    which waited for its own lock forever. Fails on 40a90a8."""
    setters = {}

    @reacton.component
    def Test():
        fail, setters["fail"] = reacton.use_state(False)
        rc = core.get_render_context()

        def effect():
            def cleanup():
                with rc:
                    pass

            return cleanup

        reacton.use_effect(effect, [])
        if fail:
            raise ValueError("component fails")
        return w.Button()

    _box, rc = reacton.render(Test(), handle_error=False)
    with pytest.raises(ValueError):
        setters["fail"](True)  # leaves a render marked (handle_error=False)
    finished, _closer = call_in_thread(rc.close, "C", timeout=TIMEOUT)
    assert finished, "close() deadlocked on its own render lock\n" + stacks()


def test_close_is_not_starved_and_nothing_renders_after_close():
    """K renders, T changes state during every pass (a fast progress reporter), C closes.
    close() must not wait for T to stop, and no render pass may start after close() began
    (the pass in flight may finish). Fails on 40a90a8."""
    setters = {}
    stop = threading.Event()
    renders_after_close = []
    closing = threading.Event()
    go, done = threading.Semaphore(0), threading.Semaphore(0)
    armed = threading.Event()

    @reacton.component
    def Test():
        trigger, setters["trigger"] = reacton.use_state(0)
        progress, setters["progress"] = reacton.use_state(0)
        if closing.is_set():
            renders_after_close.append(progress)
        if armed.is_set() and threading.current_thread().name != "T" and not stop.is_set():
            go.release()
            done.acquire(timeout=TIMEOUT)
        return w.Button(description=f"{trigger} {progress}")

    _box, rc = reacton.render(Test(), handle_error=False)
    running = threading.Event()

    def t_target():
        i = 0
        while not stop.is_set():
            if not go.acquire(timeout=0.1):
                continue
            i += 1
            setters["progress"](i)
            if i == 3:
                running.set()
            done.release()

    t = Worker(t_target, "T")
    t.start()
    armed.set()
    k = Worker(lambda: setters["trigger"](1), "K")
    k.start()
    assert running.wait(TIMEOUT)

    def close():
        closing.set()
        rc.close()

    finished, c = call_in_thread(close, "C", timeout=TIMEOUT)
    stop.set()
    k.join(TIMEOUT)
    t.join(TIMEOUT)
    assert finished, "close() waited for the progress reporter to stop\n" + stacks()
    assert c.error is None, c.error
    assert len(renders_after_close) <= 1, renders_after_close
    assert k.error is None, k.error


def test_close_from_own_render_raises_instead_of_hanging():
    """Fails on 40a90a8 (hangs)."""
    errors = []

    @reacton.component
    def Test():
        rc = core.get_render_context()

        def effect():
            try:
                rc.close()
            except RuntimeError as e:
                errors.append(e)

        reacton.use_effect(effect, [])
        return w.Button()

    finished, _t = call_in_thread(lambda: reacton.render(Test(), handle_error=False), "K", timeout=TIMEOUT)
    assert finished, "close() inside a render waited for its own lock\n" + stacks()
    assert errors


@pytest.mark.parametrize("what", ["close", "render"])
def test_close_or_render_from_a_cleanup_during_close_does_not_hang(what):
    """Fails on 40a90a8 (hangs)."""
    rcs: dict = {}

    @reacton.component
    def Test():
        def effect():
            def cleanup():
                rc = rcs["rc"]
                if what == "close":
                    rc.close()
                else:
                    rc.render(Test())

            return cleanup

        reacton.use_effect(effect, [])
        return w.Button(description="x")

    _box, rc = reacton.render(Test(), handle_error=False)
    rcs["rc"] = rc
    finished, c = call_in_thread(rc.close, "C", timeout=TIMEOUT)
    assert finished, f"close() hung when a cleanup called rc.{what}()\n" + stacks()
    assert c.error is None, repr(c.error)


def test_close_between_the_decision_to_render_again_and_the_pass(log_hook):
    """K reconciled, an effect set state, K decided to render again; close() sets _closing
    right then. K must not reconcile without a render pass (KeyError '/'), and close() must
    finish. Fails on 40a90a8 (close() sets _closing only after it got the lock, and the
    re-decision to render is not guarded)."""
    setters = {}

    @reacton.component
    def Test():
        trigger, setters["trigger"] = reacton.use_state(0)
        derived, set_derived = reacton.use_state(0)
        reacton.use_effect(lambda: set_derived(trigger), [trigger])
        return w.Button(description=f"{trigger} {derived}")

    _box, rc = reacton.render(Test(), handle_error=False)
    k_paused, resume = threading.Event(), threading.Event()

    def k_target():
        log_hook.on(threading.current_thread(), "Need rerender after reconsolidation", lambda: (k_paused.set(), resume.wait(TIMEOUT * 3)))  # type: ignore[func-returns-value]
        setters["trigger"](1)

    k = Worker(k_target, "K")
    k.start()
    assert k_paused.wait(TIMEOUT)
    c = Worker(rc.close, "C")
    c.start()
    assert wait_until(lambda: rc._closing, TIMEOUT)
    resume.set()
    k.join(TIMEOUT)
    c.join(TIMEOUT)
    assert not k.is_alive() and not c.is_alive(), stacks()
    assert k.error is None, k.error_tb or repr(k.error)
    assert c.error is None, repr(c.error)


def test_interrupted_close_can_be_retried():
    """An interrupt after close() marks closing must not make every later close() return."""
    setters = {}
    k_paused, k_resume = threading.Event(), threading.Event()
    cleanups = []

    @reacton.component
    def Test():
        value, setters["value"] = reacton.use_state(0)

        def effect():
            return lambda: cleanups.append("cleanup")

        reacton.use_effect(effect, [])
        if value == 1 and threading.current_thread().name == "K":
            k_paused.set()
            k_resume.wait(TIMEOUT)
        return w.Button(description=str(value))

    _box, rc = reacton.render(Test(), handle_error=False)
    k = Worker(lambda: setters["value"](1), "K")
    k.start()
    assert k_paused.wait(TIMEOUT)
    close_code = core._RenderContext.close.__code__
    fired: List[str] = []

    def trace(frame, event, arg):
        if not fired and frame.f_code is close_code and rc._closing and rc.thread_lock.locked():
            fired.append(event)
            raise Injected()
        return trace

    def interrupted_close():
        sys.settrace(trace)
        try:
            rc.close()
        finally:
            sys.settrace(None)

    finished, c = call_in_thread(interrupted_close, "C", timeout=TIMEOUT)
    assert finished, "the interrupted close() waited for the render lock\n" + stacks()
    assert isinstance(c.error, Injected), repr(c.error)
    assert fired, "the probe did not fire"
    assert cleanups == []
    k_resume.set()
    k.join(TIMEOUT)
    assert k.error is None, repr(k.error)
    finished, c2 = call_in_thread(rc.close, "C2", timeout=TIMEOUT)
    assert finished and c2.error is None, (c2.error, stacks())
    assert cleanups == ["cleanup"]
    finished, c3 = call_in_thread(rc.close, "C3", timeout=TIMEOUT)
    assert finished and c3.error is None, (c3.error, stacks())
    assert cleanups == ["cleanup"]


def test_batched_set_from_another_thread_while_close_runs_cleanups(log_hook):
    """The close ABBA. T is inside a setter (past the _closing check) when K starts close().
    K's cleanup waits for T's batch to end (in solara: a store lock). Before: T's batch exit
    waited for the render lock that close() holds: deadlock. Fails on 40a90a8."""
    setters = {}
    t_batch_done, t_paused, t_go = threading.Event(), threading.Event(), threading.Event()
    cleanup_waited = []

    @reacton.component
    def Test():
        value, setters["value"] = reacton.use_state(0)

        def effect():
            def cleanup():
                t_go.set()
                cleanup_waited.append(t_batch_done.wait(TIMEOUT))

            return cleanup

        reacton.use_effect(effect, [])
        return w.Button(description=str(value))

    _box, rc = reacton.render(Test(), handle_error=False)

    def t_target():
        log_hook.on(threading.current_thread(), "Set state = ", lambda: (t_paused.set(), t_go.wait(TIMEOUT)))  # type: ignore[func-returns-value]
        with rc:  # like a solara listener batch
            setters["value"](1)
        t_batch_done.set()

    def k_target():
        assert t_paused.wait(TIMEOUT)
        rc.close()

    t, k = Worker(t_target, "T"), Worker(k_target, "K")
    t.start()
    k.start()
    k.join(TIMEOUT * 2)
    t.join(TIMEOUT * 2)
    assert not k.is_alive() and not t.is_alive(), "deadlock between close() and a batched set\n" + stacks()
    assert k.error is None and t.error is None, (k.error, t.error)
    assert cleanup_waited == [True], "the cleanup waited for T's batch, and T's batch exit waited for close()"


def test_second_concurrent_close_does_not_deadlock_against_cleanup_lock():
    ext = threading.RLock()
    in_cleanup, c2_has_ext = threading.Event(), threading.Event()

    @reacton.component
    def Test():
        def effect():
            def cleanup():
                in_cleanup.set()
                assert c2_has_ext.wait(TIMEOUT)
                with ext:
                    pass

            return cleanup

        reacton.use_effect(effect, [])
        return w.Button(description="x")

    _box, rc = reacton.render(Test(), handle_error=False)

    def c2_target():
        assert in_cleanup.wait(TIMEOUT)
        with ext:
            c2_has_ext.set()
            rc.close()

    c1, c2 = Worker(rc.close, "C1"), Worker(c2_target, "C2")
    c1.start()
    c2.start()
    c1.join(TIMEOUT)
    c2.join(TIMEOUT)
    assert not c1.is_alive() and not c2.is_alive(), "two close() calls deadlocked across a cleanup lock\n" + stacks()
    assert c1.error is None and c2.error is None, (c1.error, c2.error)


def test_requests_during_close_are_dropped_and_render_after_close_is_ignored(log_hook):
    """Fails on 40a90a8 (T's requests wait for close())."""
    setters = {}
    rendered = []

    @reacton.component
    def Test():
        value, setters["value"] = reacton.use_state(0)
        rendered.append(value)
        return w.Button(description=str(value))

    box, rc = reacton.render(Test(), handle_error=False)
    k_paused, k_go = threading.Event(), threading.Event()

    def k_target():
        log_hook.on(threading.current_thread(), "Removing elements...", lambda: (k_paused.set(), k_go.wait(TIMEOUT * 3)))  # type: ignore[func-returns-value]
        rc.close()

    def t_target():
        assert k_paused.wait(TIMEOUT)
        setters["value"](1)  # must return at once and never render
        rc.force_update()
        rc.update(Test())

    k = Worker(k_target, "K")
    k.start()
    finished, t = call_in_thread(t_target, "T", timeout=TIMEOUT)
    k_go.set()
    k.join(TIMEOUT)
    t.join(TIMEOUT)
    assert finished, "a request on a closing context waited for close()\n" + stacks()
    assert t.error is None and k.error is None, (t.error, k.error)
    assert rendered == [0]
    finished, r = call_in_thread(lambda: rc.render(Test(), box), "R", timeout=TIMEOUT)
    assert finished and r.error is None, (r.error, stacks())
    assert rendered == [0]


def test_recursive_render_is_still_detected():
    """A guard (passes on 40a90a8)."""

    @reacton.component
    def Page():
        rc = core.get_render_context()
        rc.render(rc.element, rc.container)
        return w.Button(description="never")

    finished, k = call_in_thread(lambda: reacton.render(Page(), handle_error=True), "K", timeout=TIMEOUT)
    assert finished, stacks()
    box, rc = k.result
    assert "Recursive render detected" in box.children[0].value
    rc.close()
