"""A render request (state change, update(), force_update(), batch exit) never waits for the
render lock, and is never lost. Fails on 40a90a8 unless noted."""

# ruff: noqa: F811  the fixture names shadow the pytest fixture parameters of the same names

import sys
import threading

import reacton
import reacton.ipywidgets as w
from reacton import core

from ._threads_test_utils import (  # noqa: F401
    SHORT,
    TIMEOUT,
    Injected,
    Worker,
    call_in_thread,
    helper_errors,
    log_hook,
    pause_at_line,
    render_loop_function,
    source_line,
    stacks,
    text,
    wait_until,
)


def make_ab():
    setters = {}

    @reacton.component
    def Test(label=""):
        a, setters["a"] = reacton.use_state(0)
        b, setters["b"] = reacton.use_state(0)
        return w.Button(description=f"{label}{a} {b}")

    return Test, setters


def test_state_change_does_not_wait_for_a_render_on_another_thread_prologue(log_hook):
    _test_state_change_does_not_wait(log_hook, "Render phase: ")


def test_state_change_does_not_wait_for_a_render_on_another_thread_epilogue(log_hook):
    _test_state_change_does_not_wait(log_hook, "Done with render phase")


def _test_state_change_does_not_wait(log_hook, window):
    """K holds the render lock outside its render loop (prologue or epilogue).
    Before: T's setter waits for the render lock for the rest of K's render.
    After: T's setter returns at once, and K renders T's change after it released the lock."""
    Test, setters = make_ab()
    box, rc = reacton.render(Test(), handle_error=False)
    k_paused, t_done = threading.Event(), threading.Event()

    def k_target():
        log_hook.on(threading.current_thread(), window, lambda: (k_paused.set(), t_done.wait(TIMEOUT)))  # type: ignore[func-returns-value]
        setters["a"](1)

    k = Worker(k_target, "K")
    k.start()
    assert k_paused.wait(TIMEOUT)
    finished, t = call_in_thread(lambda: setters["b"](1), "T")
    t_done.set()
    k.join(TIMEOUT)
    t.join(TIMEOUT)
    assert finished, "the state change waited for another thread's render\n" + stacks()
    assert k.error is None and t.error is None, (k.error, t.error)
    assert text(box) == "1 1", "the state change from T was not rendered"
    rc.close()


def _pause_after_stable(on_pause):
    fn = render_loop_function()
    return pause_at_line(fn, source_line(fn, "self._is_rendering = False", after="stable = True"), on_pause)


def test_state_change_after_the_last_check_is_not_lost():
    """Lost wakeup. K has decided its render is stable and still holds the lock; T sets state
    then. Before: T only marks, K releases, nobody renders T's change.
    After: K checks again after it released the lock."""
    Test, setters = make_ab()
    box, rc = reacton.render(Test(), handle_error=False)
    k_paused, t_done = threading.Event(), threading.Event()
    tracer = _pause_after_stable(lambda: (k_paused.set(), t_done.wait(TIMEOUT)))  # type: ignore[func-returns-value]

    def k_target():
        sys.settrace(tracer)
        try:
            setters["a"](1)
        finally:
            sys.settrace(None)

    k = Worker(k_target, "K")
    k.start()
    assert k_paused.wait(TIMEOUT)
    finished, t = call_in_thread(lambda: setters["b"](1), "T")
    t_done.set()
    k.join(TIMEOUT)
    t.join(TIMEOUT)
    assert finished and k.error is None and t.error is None, (k.error, t.error, stacks())
    assert text(box) == "1 1", "the state change from T was lost"
    rc.close()


def test_state_change_after_the_last_check_of_an_explicit_render_is_not_lost():
    """The same window, in an explicit render(): render() must check again after its release."""
    Test, setters = make_ab()
    box, rc = reacton.render(Test(), handle_error=False)
    w_paused, t_done = threading.Event(), threading.Event()
    tracer = _pause_after_stable(lambda: (w_paused.set(), t_done.wait(TIMEOUT)))  # type: ignore[func-returns-value]

    def w_target():
        sys.settrace(tracer)
        try:
            rc.render(Test(label="b"))
        finally:
            sys.settrace(None)

    wt = Worker(w_target, "W")
    wt.start()
    assert w_paused.wait(TIMEOUT)
    finished, t = call_in_thread(lambda: setters["b"](1), "T")
    t_done.set()
    wt.join(TIMEOUT)
    t.join(TIMEOUT)
    assert finished and wt.error is None and t.error is None, (wt.error, t.error, stacks())
    assert wait_until(lambda: text(box) == "b0 1", 2), f"the state change from T was lost: {text(box)!r}"
    rc.close()


def test_lock_held_around_a_state_change_does_not_deadlock_with_an_effect(log_hook):
    """A user lock (a solara store lock, init lock or context.lock behave the same).
    T holds L while it sets state; K's render runs an effect that takes L.
    Before: T waits for the render lock while it holds L, K waits for L: deadlock."""
    user_lock = threading.RLock()
    setters = {}

    @reacton.component
    def Test():
        a, setters["a"] = reacton.use_state(0)
        b, setters["b"] = reacton.use_state(0)

        def effect():
            if a == 1:
                with user_lock:
                    pass

        reacton.use_effect(effect, [a])
        return w.Button(description=f"{a} {b}")

    box, rc = reacton.render(Test(), handle_error=False)
    k_paused, never = threading.Event(), threading.Event()

    def k_target():
        # pause in the render prologue: lock held, not yet rendering
        log_hook.on(threading.current_thread(), "Render phase: ", lambda: (k_paused.set(), never.wait(SHORT)))  # type: ignore[func-returns-value]
        setters["a"](1)

    def t_target():
        with user_lock:
            setters["b"](1)

    k = Worker(k_target, "K")
    k.start()
    assert k_paused.wait(TIMEOUT)
    t = Worker(t_target, "T")
    t.start()
    k.join(TIMEOUT)
    t.join(TIMEOUT)
    assert not k.is_alive() and not t.is_alive(), "deadlock\n" + stacks()
    assert k.error is None and t.error is None, (k.error, t.error)
    assert text(box) == "1 1"
    rc.close()


def _root_element_read():
    """(function, line): the line where the first pass of a hold reads the root element."""
    RC = core._RenderContext
    if hasattr(RC, "_render_locked"):
        fn = RC._render_locked
        for needle in ("self.element = self._element_requested", "self.element = element"):
            try:
                return fn, source_line(fn, needle)
            except StopIteration:
                pass
    return RC.render, source_line(RC.render, "self.element = element")


def test_update_from_another_thread_at_the_start_of_a_pass_is_not_lost():
    """K has just read the root element for its pass; T calls rc.update() with a new root.
    T's element must be rendered (the pass start clears the request mark before it reads the
    root element). Passes on 40a90a8 (T waits for the lock)."""
    setters = {}

    @reacton.component
    def Test(label="old"):
        a, setters["a"] = reacton.use_state(0)
        return w.Button(description=f"{label} {a}")

    box, rc = reacton.render(Test(), handle_error=False)
    fn, lineno = _root_element_read()
    k_paused, t_done = threading.Event(), threading.Event()
    tracer = pause_at_line(fn, lineno, lambda: (k_paused.set(), t_done.wait(SHORT)), after_line=True)  # type: ignore[func-returns-value]

    def k_target():
        sys.settrace(tracer)
        try:
            setters["a"](1)
        finally:
            sys.settrace(None)

    k = Worker(k_target, "K")
    k.start()
    assert k_paused.wait(TIMEOUT)
    finished, t = call_in_thread(lambda: rc.update(Test(label="new")), "T", timeout=SHORT)
    t_done.set()
    k.join(TIMEOUT)
    t.join(TIMEOUT)
    assert k.error is None and t.error is None, (k.error, t.error)
    assert wait_until(lambda: text(box) == "new 1", 2), f"the update() from T was lost: {text(box)!r} (T returned at once: {finished})"
    rc.close()


def test_update_from_an_effect_of_the_render_is_rendered():
    """rc.update() from an effect of the render in progress (same thread): the next pass of
    that render must use the new root element. Passes on 40a90a8."""
    calls: list = []

    @reacton.component
    def Test(label="old"):
        rc = core.get_render_context()

        def effect():
            if label == "old" and not calls:
                calls.append(1)
                rc.update(Test(label="new"))

        reacton.use_effect(effect, [label])
        return w.Button(description=label)

    finished, k = call_in_thread(lambda: reacton.render(Test(), handle_error=False), "K", timeout=TIMEOUT)
    assert finished and k.error is None, (k.error, stacks())
    box, rc = k.result
    assert text(box) == "new"
    rc.close()


def test_a_reconcile_commits_a_settled_render_only():
    """A component derives state while it renders (`if b != a: set_b(a)`), so the pass after a
    change of `a` is not settled. T asks for a render during that pass. The holder must still
    finish its render phase before it reconciles: no effect may run on (a=1, b=0). Passes on
    40a90a8."""
    setters = {}
    seen = []
    k_in_pass, k_go = threading.Event(), threading.Event()

    @reacton.component
    def Test():
        a, setters["a"] = reacton.use_state(0)
        b, set_b = reacton.use_state(0)
        x, setters["x"] = reacton.use_state(0)
        if b != a:
            if threading.current_thread().name == "K" and not k_in_pass.is_set():
                k_in_pass.set()
                k_go.wait(TIMEOUT)
            set_b(a)
        reacton.use_effect(lambda: seen.append((a, b)), [a, b])
        return w.Button(description=f"{a} {b} {x}")

    box, rc = reacton.render(Test(), handle_error=False)
    k = Worker(lambda: setters["a"](1), "K")
    k.start()
    assert k_in_pass.wait(TIMEOUT)
    _finished, t = call_in_thread(lambda: setters["x"](1), "T", timeout=SHORT * 2)
    k_go.set()
    k.join(TIMEOUT)
    t.join(TIMEOUT)
    assert k.error is None and t.error is None, (k.error, t.error)
    assert wait_until(lambda: text(box) == "1 1 1", 3), text(box)
    assert (1, 0) not in seen, f"an effect ran on a render that was not settled: {seen}"
    rc.close()


def test_request_during_a_batch_on_another_thread_renders_at_batch_exit():
    """While any thread is inside `with rc:`, a state change only marks, and the thread that
    leaves the last batch renders. Passes on 40a90a8 (a guard)."""
    Test, setters = make_ab()
    box, rc = reacton.render(Test(), handle_error=False)
    rc.__enter__()
    finished, t = call_in_thread(lambda: setters["a"](1), "T")
    assert finished and t.error is None
    assert text(box) == "0 0", "rendered inside a batch"
    rc.__exit__(None, None, None)
    assert text(box) == "1 0"
    rc.close()


def test_exception_injected_right_after_the_lock_is_taken_does_not_leak_it():
    """Models a KeyboardInterrupt, or solara's cancel_guard (a trace function that raises on a
    traced line while the context is not rendering): it fires once, at the first traced event
    in reacton/core.py after the thread took the render lock. The lock must not leak.
    Passes on 40a90a8."""
    Test, setters = make_ab()
    _box, rc = reacton.render(Test(), handle_error=False)
    corefile = core.__file__
    fired: list = []

    def trace(frame, event, arg):
        if not fired and frame.f_code.co_filename == corefile and rc.thread_lock.locked() and not rc._is_rendering:
            fired.append((frame.f_code.co_name, frame.f_lineno, event))
            raise Injected()
        return trace

    def t_target():
        sys.settrace(trace)
        try:
            setters["a"](1)
        finally:
            sys.settrace(None)

    finished, t = call_in_thread(t_target, "T", timeout=TIMEOUT)
    assert finished
    assert isinstance(t.error, Injected), (t.error, fired)
    assert not rc.thread_lock.locked(), f"the render lock leaked after an exception at {fired}"
    finished, _c = call_in_thread(rc.close, "C", timeout=TIMEOUT)
    assert finished, stacks()


def test_concurrent_writers_never_hang_raise_or_lose_a_render():
    """Stress, no pauses: K changes `trigger` (its effect writes `b` under a user lock), T writes
    `a` under the same lock. No deadlock, no exception, the last state is shown (a helper may
    render it a moment after the writers returned)."""
    lock = threading.RLock()
    setters = {}

    @reacton.component
    def Test():
        trigger, setters["trigger"] = reacton.use_state(0)
        a, setters["a"] = reacton.use_state(0)
        b, set_b = reacton.use_state(0)

        def effect():
            with lock:  # like a solara store listener that holds the store lock
                set_b(trigger)

        reacton.use_effect(effect, [trigger])
        return w.Button(description=f"{trigger} {a} {b}")

    box, rc = reacton.render(Test(), handle_error=False)
    n = 2000
    errors = []

    def run(f):
        try:
            for i in range(1, n + 1):
                f(i)
        except BaseException as e:  # noqa
            errors.append(e)

    def write_a(i):
        with lock:
            setters["a"](i)

    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        k = Worker(lambda: run(setters["trigger"]), "K")
        t = Worker(lambda: run(write_a), "T")
        k.start()
        t.start()
        k.join(60)
        t.join(60)
    finally:
        sys.setswitchinterval(old)
    assert not k.is_alive() and not t.is_alive(), "deadlock\n" + stacks()
    assert not errors, errors
    assert wait_until(lambda: text(box) == f"{n} {n} {n}", 10), text(box)
    rc.close()
