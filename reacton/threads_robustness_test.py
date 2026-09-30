"""Robustness of the render hand-off: an exception in a waiter's batch exit or in a failing
hold must not leak the render lock or lose a request, an explicit render() is not starved by a
stream of derived own-state re-renders, and a foreign request consumed by an own pass is not
a render loop."""

# ruff: noqa: F811  the fixture names shadow the pytest fixture parameters of the same names

import sys
import threading
import time

import reacton
import reacton.ipywidgets as w
from reacton import core

from ._threads_test_utils import (  # noqa: F401
    SHORT,
    TIMEOUT,
    EveryTimeHook,
    Injected,
    Worker,
    call_in_thread,
    helper_errors,
    install,
    log_hook,
    source_line,
    stacks,
    text,
    wait_until,
)


def test_exception_in_the_waiters_batch_exit_does_not_leak_the_lock():
    """W waits in render() while K holds the lock (K is paused in a component body). When K
    releases, W gets the lock and then leaves its waiting batch. An exception there (a
    KeyboardInterrupt, a trace function) must not leak the lock or the batch count."""
    setters = {}
    k_in_body, k_resume = threading.Event(), threading.Event()

    @reacton.component
    def Test(label="a"):
        a, setters["a"] = reacton.use_state(0)
        if a == 1 and threading.current_thread().name == "K":
            k_in_body.set()
            k_resume.wait(TIMEOUT)
        return w.Button(description=f"{label} {a}")

    box, rc = reacton.render(Test(), handle_error=False)
    k = Worker(lambda: setters["a"](1), "K")
    k.start()
    assert k_in_body.wait(TIMEOUT)
    exit_code = core._RenderContext.__exit__.__code__
    hold_code = core._RenderContext._hold_and_render.__code__
    fired: list = []

    def trace(frame, event, arg):
        if not fired and frame.f_code is exit_code and rc.thread_lock.locked() and not rc._is_rendering and k_resume.is_set():
            fired.append(event)
            raise Injected()
        if (
            not fired
            and frame.f_code is hold_code
            and rc.thread_lock.locked()
            and rc._batch_counter.current() == 0
            and not rc._is_rendering
            and k_resume.is_set()
        ):
            fired.append(event)
            raise Injected()
        return trace

    def w_target():
        sys.settrace(trace)
        try:
            rc.render(Test(label="b"))
        finally:
            sys.settrace(None)

    wt = Worker(w_target, "W")
    wt.start()
    assert wait_until(lambda: rc._batch_counter.current() == 1, TIMEOUT), "W did not start waiting"
    k_resume.set()
    k.join(TIMEOUT)
    wt.join(TIMEOUT)
    assert not k.is_alive() and not wt.is_alive(), stacks()
    assert fired, "the probe did not fire"
    assert isinstance(wt.error, Injected), repr(wt.error)
    assert not rc.thread_lock.locked(), "the render lock leaked after an exception in the waiter's batch exit"
    assert rc._batch_counter.current() == 0, "the waiter's batch count leaked"
    setters["a"](2)
    assert wait_until(lambda: text(box).endswith(" 2"), TIMEOUT), text(box)
    finished, _c = call_in_thread(rc.close, "C", timeout=TIMEOUT)
    assert finished, "close() hangs on the leaked lock\n" + stacks()


def test_request_during_a_failing_hold_is_rendered(log_hook, helper_errors):
    """handle_error=False. A's pass fails (a component raises); A pauses after its render loop,
    still holding the lock, before it raises. B asks for a recovery render (B's try fails, B
    returns). A raises and releases. B's request must still be rendered after the holder raises."""
    setters = {}

    @reacton.component
    def Test():
        fail, setters["fail"] = reacton.use_state(False)
        if fail:
            raise ValueError("fail")
        return w.Button(description=f"ok {fail}")

    box, rc = reacton.render(Test(), handle_error=False)
    a_paused, a_resume = threading.Event(), threading.Event()

    def a_target():
        log_hook.on(threading.current_thread(), "Done with render phase", lambda: (a_paused.set(), a_resume.wait(TIMEOUT * 3)))  # type: ignore[func-returns-value]
        setters["fail"](True)

    a = Worker(a_target, "A")
    a.start()
    assert a_paused.wait(TIMEOUT)
    finished, b = call_in_thread(lambda: setters["fail"](False), "B", timeout=SHORT * 2)
    a_resume.set()
    assert finished and b.error is None, ("B's state change waited for A's render", b.error, stacks())
    a.join(TIMEOUT)
    assert isinstance(a.error, ValueError), repr(a.error)
    assert wait_until(
        lambda: not rc.thread_lock.locked() and not getattr(rc, "_render_requested", False) and text(box) == "ok False", 3
    ), f"B's recovery request is still pending: _render_requested={getattr(rc, '_render_requested', None)}, shows {text(box)!r}"
    assert not helper_errors, helper_errors
    rc.close()


def test_request_after_explicit_render_hold_survives_interrupt(helper_errors):
    setters = {}
    arm, b_done = threading.Event(), threading.Event()

    @reacton.component
    def Test(label="old"):
        value, setters["value"] = reacton.use_state(0)

        def effect():
            if arm.is_set():
                arm.clear()

                def b_target():
                    setters["value"](1)
                    b_done.set()

                threading.Thread(target=b_target, name="B", daemon=True).start()
                b_done.wait(TIMEOUT)

        reacton.use_effect(effect)
        return w.Button(description=f"{label} {value}")

    box, rc = reacton.render(Test(), handle_error=False)
    drain_line = source_line(core._RenderContext.render, "self._drain_render_requests()")

    def trace(frame, event, arg):
        if event == "line" and frame.f_code is core._RenderContext.render.__code__ and frame.f_lineno == drain_line:
            raise Injected()
        return trace

    def a_target():
        arm.set()
        sys.settrace(trace)
        try:
            rc.render(Test(label="new"))
        finally:
            sys.settrace(None)

    a = Worker(a_target, "A")
    a.start()
    a.join(TIMEOUT)
    assert not a.is_alive(), stacks()
    assert isinstance(a.error, Injected), repr(a.error)
    assert b_done.is_set(), "the request during A's hold did not run"
    assert wait_until(
        lambda: not getattr(rc, "_render_requested", False) and text(box) == "new 1", TIMEOUT
    ), f"the request stayed pending: _render_requested={getattr(rc, '_render_requested', None)}, shows {text(box)!r}"
    assert not helper_errors, helper_errors
    rc.close()


def test_explicit_render_is_not_starved_by_derived_own_state():
    """An effect derives own state from the streamed value, so every pass is followed by an own
    re-render. Once the render budget hands the stream over to a helper, W's render() must
    still return."""
    setters = {}
    streaming, w_returned = threading.Event(), threading.Event()
    go, done = threading.Semaphore(0), threading.Semaphore(0)

    @reacton.component
    def Test(label="old"):
        trigger, setters["trigger"] = reacton.use_state(0)
        progress, setters["progress"] = reacton.use_state(0)
        _derived, set_derived = reacton.use_state(0)
        reacton.use_effect(lambda: set_derived(progress), [progress])
        if streaming.is_set() and not w_returned.is_set() and threading.current_thread().name != "T":
            go.release()
            done.acquire(timeout=1)
        return w.Button(description=f"{label} {trigger} {progress}")

    box, rc = reacton.render(Test(), handle_error=False)
    count = [0]

    def t_target():
        deadline = time.monotonic() + 40
        while not w_returned.is_set() and time.monotonic() < deadline:
            if go.acquire(timeout=0.1):
                count[0] += 1
                setters["progress"](count[0])
                done.release()

    def k_target():
        streaming.set()
        setters["trigger"](1)

    t = Worker(t_target, "T")
    t.start()
    k = Worker(k_target, "K")
    k.start()
    assert wait_until(lambda: count[0] >= 150, 30), "the stream did not start"  # past the hand-over to a helper
    finished, wt = call_in_thread(lambda: rc.render(Test(label="new")), "W", timeout=10)
    w_returned.set()
    wt.join(45)
    k.join(45)
    t.join(45)
    assert finished, f"W's render() waited while a helper kept rendering ({count[0]} updates)\n" + stacks()
    assert wait_until(lambda: text(box).startswith("new 1"), 5), text(box)
    rc.close()


def test_foreign_request_consumed_by_an_own_pass_is_not_a_render_loop(helper_errors):
    """An effect derives own state from T's value, so the renderer renders own passes. T changes
    state at the start of every pass (at the log calls "Render phase: " and "Entering nested
    render phase"). 60 times. That is not a render loop: no "Too many renders", and T's last
    value is rendered."""
    n = 60
    setters = {}
    go, done = threading.Semaphore(0), threading.Semaphore(0)
    remaining = [n]
    armed = threading.Event()

    @reacton.component
    def Test():
        trigger, setters["trigger"] = reacton.use_state(0)
        progress, setters["progress"] = reacton.use_state(0)
        derived, set_derived = reacton.use_state(0)
        reacton.use_effect(lambda: set_derived(progress + trigger), [progress, trigger])
        return w.Button(description=f"{trigger} {progress} {derived}")

    box, rc = reacton.render(Test(), handle_error=False)

    def at_pass_start():
        if armed.is_set() and remaining[0] > 0:
            go.release()
            done.acquire(timeout=TIMEOUT)

    uninstall = install(EveryTimeHook(["Entering nested render phase", "Render phase: "], at_pass_start, skip="T"))

    def t_target():
        for i in range(n):
            assert go.acquire(timeout=TIMEOUT)
            setters["progress"](i + 1)
            remaining[0] -= 1
            done.release()

    def k_target():
        armed.set()
        setters["trigger"](1)

    try:
        t = Worker(t_target, "T")
        t.start()
        finished, k = call_in_thread(k_target, "K", timeout=60)
        t.join(60)
        assert finished, stacks()
        assert k.error is None, repr(k.error)[:300]
        assert t.error is None, repr(t.error)[:300]
        ok = wait_until(lambda: text(box) == f"1 {n} {n + 1}", 10)
        assert not helper_errors, repr(helper_errors[0])[:300]
        assert ok, text(box)
    finally:
        uninstall()
    rc.close()
