import threading

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
