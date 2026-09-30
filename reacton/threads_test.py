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


def _run_in_thread(target):
    # a thread that is still alive after TIMEOUT hangs; errors[0] is what target raised, if anything
    errors: list = []

    def run():
        try:
            target()
        except BaseException as e:
            errors.append(e)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    thread.join(TIMEOUT)
    return thread, errors


def test_close_from_its_own_render_raises_instead_of_hanging():
    # close() waits for the render lock, which its own render holds: it would wait for itself
    close_errors: list = []
    setters = {}

    @reacton.component
    def Test():
        a, setters["a"] = reacton.use_state(0)

        def effect():
            if a == 1:
                try:
                    rc.close()
                except RuntimeError as e:
                    close_errors.append(e)

        reacton.use_effect(effect, [a])
        return w.Button(description=f"{a}")

    box, rc = reacton.render(Test(), handle_error=False)
    thread, errors = _run_in_thread(lambda: setters["a"](1))
    assert not thread.is_alive(), "close() from its own render hangs"
    assert not errors, errors
    assert len(close_errors) == 1
    rc.close()


def test_close_during_or_after_close_returns():
    # an effect cleanup, which runs during close(), calls close() again: that must not wait for the
    # render lock that the first close() holds. A close() after close() is a no-op as well.
    @reacton.component
    def Test():
        reacton.use_effect(lambda: lambda: rc.close(), [])  # the cleanup calls close()
        return w.Button()

    box, rc = reacton.render(Test(), handle_error=False)
    thread, errors = _run_in_thread(rc.close)
    assert not thread.is_alive(), "close() from a cleanup during close() hangs"
    assert not errors, errors
    rc.close()


def test_render_loop_for_another_thread_is_bounded():
    # Another thread changes state during every render pass, and does not stop (a loop without a
    # pause). The thread that renders must not keep rendering those changes forever: it would not
    # return, and close() waits for it. It stops with "Too many renders", which names the cause.
    setters = {}
    stop = threading.Event()
    go, done = threading.Semaphore(0), threading.Semaphore(0)

    @reacton.component
    def Test():
        trigger, setters["trigger"] = reacton.use_state(0)
        progress, setters["progress"] = reacton.use_state(0)
        if trigger and not stop.is_set():
            go.release()  # the other thread changes state during this pass
            done.acquire(timeout=TIMEOUT)
        return w.Button(description=f"{trigger} {progress}")

    box, rc = reacton.render(Test(), handle_error=False)

    def report_progress():
        i = 0
        while not stop.is_set():
            if go.acquire(timeout=0.1):
                i += 1
                setters["progress"](i)
                done.release()

    other = threading.Thread(target=report_progress, daemon=True)
    other.start()
    thread, errors = _run_in_thread(lambda: setters["trigger"](1))
    returned_by_itself = not thread.is_alive()
    stop.set()
    thread.join(TIMEOUT)
    other.join(TIMEOUT)
    assert returned_by_itself, "the render kept rendering the changes of another thread"
    assert len(errors) == 1 and "another thread" in str(errors[0]).lower(), errors
    rc.close()


def test_many_changes_after_the_last_look_in_a_row_do_not_recurse():
    # A change after the last look of the render loop is rendered after the render lock is released
    # (see the lost-update test above). When that happens many times in a row, the renders must not
    # nest (a RecursionError).
    setters = {}

    @reacton.component
    def Test():
        a, setters["a"] = reacton.use_state(0)
        return w.Button(description=f"{a}")

    box, rc = reacton.render(Test(), handle_error=False)
    n = 2000

    def change_after_the_last_look():
        a = int(box.children[0].description)
        if 0 < a < n:
            setters["a"](a + 1)  # a render is running: this only marks _rerender_needed

    rc._on_render_loop_done = change_after_the_last_look
    setters["a"](1)
    assert box.children[0].description == f"{n}"
    rc.close()


def test_own_render_loop_stops_after_about_50_passes():
    # A component that changes its own state on every render: "Too many renders" after about 50
    # passes. The higher limit is only for changes from other threads, not for every render that a
    # state change (from outside a render) started.
    renders = []
    setters = {}

    @reacton.component
    def Test():
        a, setters["a"] = reacton.use_state(0)
        renders.append(a)
        if a > 0:
            setters["a"](a + 1)  # never stops
        return w.Button(description=f"{a}")

    box, rc = reacton.render(Test(), handle_error=False)
    renders.clear()
    with pytest.raises(RuntimeError, match="Too many renders"):
        setters["a"](1)
    assert len(renders) < 60, len(renders)
    rc.close()
