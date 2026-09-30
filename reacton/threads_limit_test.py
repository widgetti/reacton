"""The "too many renders" limit counts only a thread's own render loop; a caller is not held
by other threads' updates (the budget and the helper); an explicit render() is not starved."""

# ruff: noqa: F811  the fixture names shadow the pytest fixture parameters of the same names

import threading
import time

import pytest

import reacton
import reacton.ipywidgets as w
from reacton import core

from ._threads_test_utils import TIMEOUT, Worker, call_in_thread, helper_errors, log_hook, stacks, text, wait_until  # noqa: F401


@pytest.mark.parametrize("derive", ["none", "effect", "render"])
def test_updates_from_another_thread_do_not_count_as_a_render_loop(derive):
    """T changes state once during each of K's render passes, 60 times.
    Before: K raises "Too many renders triggered" after about 50 passes.
    derive="effect": an effect derives state from T's value, so every pass for T is followed by
    an own pass. derive="render": the component derives it while it renders, so the render
    phase does not settle while T keeps changing state; at the limit the holder commits what it
    has instead of raising (T's requests are pending). Fails on 40a90a8."""
    n = 60
    setters = {}
    remaining = [n]
    go, done = threading.Semaphore(0), threading.Semaphore(0)
    armed = threading.Event()

    @reacton.component
    def Test():
        trigger, setters["trigger"] = reacton.use_state(0)
        progress, setters["progress"] = reacton.use_state(0)
        derived, set_derived = reacton.use_state(0)
        if derive == "effect":
            reacton.use_effect(lambda: set_derived(progress), [progress])
        if derive == "render" and derived != progress:
            set_derived(progress)
        if armed.is_set() and threading.current_thread().name != "T" and remaining[0] > 0:  # K, or the helper
            go.release()  # T reports progress once during this pass
            assert done.acquire(timeout=TIMEOUT)
        return w.Button(description=f"{trigger} {progress} {derived}")

    box, rc = reacton.render(Test(), handle_error=False)

    def t_target():
        for i in range(n):
            assert go.acquire(timeout=TIMEOUT)
            setters["progress"](i + 1)
            remaining[0] -= 1
            done.release()

    def k_target():
        armed.set()
        setters["trigger"](1)

    t = Worker(t_target, "T")
    t.start()
    finished, k = call_in_thread(k_target, "K", timeout=TIMEOUT * 2)
    t.join(TIMEOUT)
    assert finished and not t.is_alive(), stacks()
    assert k.error is None, repr(k.error)[:300]
    assert t.error is None, repr(t.error)[:300]
    expected = f"1 {n} {n if derive != 'none' else 0}"
    assert wait_until(lambda: text(box) == expected, 5), text(box)
    rc.close()


@pytest.mark.parametrize("n", [80, 200])
def test_foreign_updates_seen_by_an_effect_are_not_a_render_loop(n, helper_errors):
    """T changes state inside every reconcile of the renderer (inside an effect), n times;
    the effect derives own state from T's value. Not a render loop: no "Too many renders", also
    not on the helper that renders after K's budget (n=200). Fails on 40a90a8."""
    setters = {}
    go, done = threading.Semaphore(0), threading.Semaphore(0)
    armed = threading.Event()
    remaining = [n]

    @reacton.component
    def Test():
        trigger, setters["trigger"] = reacton.use_state(0)
        progress, setters["progress"] = reacton.use_state(0)
        derived, set_derived = reacton.use_state(0)

        def effect():
            set_derived(progress)
            if armed.is_set() and threading.current_thread().name != "T" and remaining[0] > 0:
                go.release()
                done.acquire(timeout=TIMEOUT)

        reacton.use_effect(effect, [progress, trigger])
        return w.Button(description=f"{trigger} {progress} {derived}")

    box, rc = reacton.render(Test(), handle_error=False)

    def t_target():
        for i in range(n):
            assert go.acquire(timeout=TIMEOUT)
            setters["progress"](i + 1)
            remaining[0] -= 1
            done.release()

    def k_target():
        armed.set()
        setters["trigger"](1)

    t = Worker(t_target, "T")
    t.start()
    finished, k = call_in_thread(k_target, "K", timeout=30)
    t.join(30)
    assert finished, stacks()
    assert k.error is None, repr(k.error)[:300]
    assert t.error is None, repr(t.error)[:300]
    ok = wait_until(lambda: text(box) == f"1 {n} {n}", 10)
    assert not helper_errors, repr(helper_errors[0])[:300]
    assert ok, text(box)
    rc.close()


def test_own_render_loop_is_still_detected():
    """A component that changes its own state on every render still raises. Passes on
    40a90a8 (a guard)."""

    @reacton.component
    def Infinite():
        state, set_state = reacton.use_state(0)
        set_state(state + 1)
        return w.Button(description=str(state))

    rc = core._RenderContext(Infinite(), handle_error=False)
    finished, k = call_in_thread(lambda: rc.render(rc.element), "K", timeout=TIMEOUT)
    assert finished, stacks()
    assert isinstance(k.error, RuntimeError) and "Too many renders triggered" in str(k.error), repr(k.error)
    finished, _c = call_in_thread(rc.close, "C", timeout=TIMEOUT)
    assert finished, stacks()


def test_renderer_caller_is_not_held_by_a_stream_of_foreign_updates():
    """K renders because of its own state change. T changes state once during every render
    pass, until K's call returned (a task that reports progress until the user clicks cancel,
    a click that K must process). K's call must return without an error, and T's last value
    (made after K returned) must be rendered. Fails on 40a90a8 ("Too many renders")."""
    setters = {}
    streaming, k_returned = threading.Event(), threading.Event()
    go, done = threading.Semaphore(0), threading.Semaphore(0)

    @reacton.component
    def Test():
        trigger, setters["trigger"] = reacton.use_state(0)
        progress, setters["progress"] = reacton.use_state(0)
        if streaming.is_set() and not k_returned.is_set() and threading.current_thread().name != "T":
            go.release()
            done.acquire(timeout=1)  # T reports progress during this pass
        return w.Button(description=f"{trigger} {progress}")

    box, rc = reacton.render(Test(), handle_error=False)
    count = [0]

    def t_target():
        deadline = time.monotonic() + 40
        while not k_returned.is_set() and time.monotonic() < deadline:
            if go.acquire(timeout=0.1):
                count[0] += 1
                setters["progress"](count[0])
                done.release()
        count[0] += 1
        setters["progress"](count[0])  # after K returned: must be rendered too

    def k_target():
        streaming.set()
        setters["trigger"](1)

    t = Worker(t_target, "T")
    t.start()
    finished, k = call_in_thread(k_target, "K", timeout=10)
    k_returned.set()
    k.join(45)
    t.join(45)
    assert finished, f"K's set() did not return while T kept changing state ({count[0]} updates so far)\n" + stacks()
    assert k.error is None, repr(k.error)
    assert t.error is None, repr(t.error)
    assert wait_until(lambda: text(box) == f"1 {count[0]}", 10), f"lost: shows {text(box)!r}, expected '1 {count[0]}'"
    rc.close()


def test_explicit_render_is_not_starved_by_a_stream():
    """A holder renders a stream of T's updates (one per pass, until W's render() returned).
    W calls rc.render() (solara: app.py on a hot reload). It must return.
    On 40a90a8 K raises "Too many renders" first. With a real scheduler the blocked waiter
    usually wins the lock when the holder releases it between holds."""
    setters = {}
    streaming, w_returned = threading.Event(), threading.Event()
    go, done = threading.Semaphore(0), threading.Semaphore(0)

    @reacton.component
    def Test(label="old"):
        trigger, setters["trigger"] = reacton.use_state(0)
        progress, setters["progress"] = reacton.use_state(0)
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
    assert wait_until(lambda: count[0] >= 60, 20), "the stream did not start"  # past the hand-over to a helper
    finished, wt = call_in_thread(lambda: rc.render(Test(label="new")), "W", timeout=10)
    w_returned.set()
    wt.join(45)
    k.join(45)
    t.join(45)
    assert finished, f"W's render() waited while another thread kept rendering T's updates ({count[0]})\n" + stacks()
    assert wait_until(lambda: text(box).startswith("new 1"), 5), text(box)
    rc.close()
