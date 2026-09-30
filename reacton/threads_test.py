import logging
import threading

import pytest

import reacton
import reacton.ipywidgets as w

TIMEOUT = 10


def test_state_change_from_another_thread_after_the_last_check_is_rendered():
    # A setter on another thread leaves the render to a running render loop. When it runs just
    # after the loop took its last look at _rerender_needed, its change must still be rendered.
    setters = {}

    @reacton.component
    def Test():
        a, setters["a"] = reacton.use_state(0)
        b, setters["b"] = reacton.use_state(0)
        return w.Button(description=f"{a} {b}")

    box, rc = reacton.render(Test(), handle_error=False)
    other = threading.Thread(target=lambda: setters["b"](1))

    def set_b_on_other_thread():
        rc._on_render_loop_done = None
        other.start()
        # the setter returns at once when it leaves the render to us,
        # or it waits for our render lock when it renders the change itself
        other.join(0.5)

    rc._on_render_loop_done = set_b_on_other_thread
    setters["a"](1)
    other.join(TIMEOUT)
    assert not other.is_alive()
    assert box.children[0].description == "1 1"
    rc.close()


def test_state_changes_from_another_thread_are_not_a_render_loop():
    # Another thread changes state once during each render pass (a progress bar, for instance),
    # more often than the "Too many renders" limit allows for a render loop.
    n = 60
    setters = {}
    remaining = [0]
    go, done = threading.Semaphore(0), threading.Semaphore(0)

    @reacton.component
    def Test():
        trigger, setters["trigger"] = reacton.use_state(0)
        progress, setters["progress"] = reacton.use_state(0)
        if remaining[0] > 0:
            go.release()  # the other thread changes state during this pass
            assert done.acquire(timeout=TIMEOUT)
        return w.Button(description=f"{trigger} {progress}")

    box, rc = reacton.render(Test(), handle_error=False)

    def report_progress():
        for i in range(n):
            assert go.acquire(timeout=TIMEOUT)
            setters["progress"](i + 1)
            remaining[0] -= 1
            done.release()

    other = threading.Thread(target=report_progress)
    other.start()
    remaining[0] = n
    setters["trigger"](1)
    other.join(TIMEOUT)
    assert not other.is_alive()
    assert box.children[0].description == f"1 {n}"
    rc.close()


@pytest.mark.parametrize("request_render", ["set_state", "update", "render", "force_update"])
def test_render_request_while_holding_a_user_lock_does_not_deadlock(request_render):
    # Another thread holds its own lock while it asks for a render (a state change, update(), render()
    # or force_update()), and the render on this thread takes that lock in an effect. If the other
    # thread waits for the render lock (held by this thread), this thread waits for the user lock
    # (held by the other thread): a deadlock. The effect uses a timeout to break it.
    user_lock = threading.RLock()
    deadlocked = []
    setters = {}

    @reacton.component
    def Test(label=""):
        a, setters["a"] = reacton.use_state(0)
        b, setters["b"] = reacton.use_state(0)

        def effect():
            if user_lock.acquire(timeout=2):
                user_lock.release()
            else:
                deadlocked.append(True)

        reacton.use_effect(effect, [a])
        return w.Button(description=f"{label}{a} {b}")

    box, rc = reacton.render(Test(), handle_error=False)
    requests = {
        "set_state": lambda: setters["b"](1),
        "update": lambda: rc.update(Test(label="new ")),
        "render": lambda: rc.render(Test(label="new ")),
        "force_update": lambda: rc.force_update(),
    }
    expected = {"set_state": "1 1", "update": "new 1 0", "render": "new 1 0", "force_update": "1 0"}

    def request_holding_user_lock():
        with user_lock:
            requests[request_render]()

    other = threading.Thread(target=request_holding_user_lock)

    class RequestAtRenderStart(logging.Filter):
        # "Render phase: " is logged after the render took the render lock, but before it renders
        def filter(self, record):
            if str(record.msg).startswith("Render phase: ") and other.ident is None:
                other.start()
                # returns at once when the other thread does not wait for the render lock
                other.join(0.5)
            return True

    logger = logging.getLogger("reacton")
    level = logger.level
    request = RequestAtRenderStart()
    logger.setLevel(logging.INFO)
    logger.addFilter(request)
    try:
        setters["a"](1)
    finally:
        logger.removeFilter(request)
        logger.setLevel(level)
    other.join(TIMEOUT)
    assert not other.is_alive()
    assert not deadlocked, "the other thread waited for the render lock while it held the user lock"
    assert box.children[0].description == expected[request_render]
    rc.close()
