"""Widget construction does not hold a shared lock: it does not block other render contexts or
other threads, and a widget that renders in its constructor does not hang. Fail on 40a90a8."""

import threading

import ipywidgets
import pytest

import reacton
import reacton.ipywidgets as w

from ._threads_test_utils import TIMEOUT, Worker, call_in_thread, helper_errors, log_hook, stacks  # noqa: F401


class BlockingButton(ipywidgets.Button):
    """A widget whose construction blocks on thread "A", like comm_open to a slow client."""

    entered = threading.Event()
    release = threading.Event()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if threading.current_thread().name == "A":
            BlockingButton.entered.set()
            assert BlockingButton.release.wait(TIMEOUT)


@pytest.fixture
def blocking_button():
    BlockingButton.entered.clear()
    BlockingButton.release.clear()
    yield BlockingButton
    BlockingButton.release.set()


def test_widget_construction_does_not_block_other_render_contexts(blocking_button):
    """Before: one process-wide lock around every widget construction; a construction that
    blocks (a send to a slow client) stops every other render context. Side-effect widgets
    (Layout, Style) are still attributed to their own render context."""
    BlockingButtonElement = reacton.core.ComponentWidget(blocking_button)

    @reacton.component
    def Slow():
        return BlockingButtonElement(description="slow")

    @reacton.component
    def Fast():
        return w.Button(description="fast")

    a = Worker(lambda: reacton.render(Slow(), handle_error=False), "A")
    a.start()
    assert blocking_button.entered.wait(TIMEOUT)
    finished, b = call_in_thread(lambda: reacton.render(Fast(), handle_error=False), "B")
    blocking_button.release.set()
    a.join(TIMEOUT)
    b.join(TIMEOUT)
    assert finished, "widget creation waited for another render context's widget construction\n" + stacks()
    assert a.error is None and b.error is None, (a.error, b.error)
    (box_a, rc_a), (box_b, rc_b) = a.result, b.result  # type: ignore[misc]
    button_a, button_b = box_a.children[0], box_b.children[0]
    assert rc_a._orphans[button_a.model_id] == {button_a.layout.model_id, button_a.style.model_id}
    assert rc_b._orphans[button_b.model_id] == {button_b.layout.model_id, button_b.style.model_id}
    rc_a.close()
    rc_b.close()


def test_widget_created_by_another_thread_is_not_an_orphan(blocking_button):
    """Before: the construction recording was global, so a widget that another thread creates
    while a render constructs a widget became an orphan of that widget, and was closed with it."""
    BlockingButtonElement = reacton.core.ComponentWidget(blocking_button)

    @reacton.component
    def Slow():
        return BlockingButtonElement(description="slow")

    a = Worker(lambda: reacton.render(Slow(), handle_error=False), "A")
    a.start()
    assert blocking_button.entered.wait(TIMEOUT)
    finished, u = call_in_thread(ipywidgets.IntSlider, "U")  # user code on another thread
    blocking_button.release.set()
    a.join(TIMEOUT)
    assert finished, "creating a plain widget waited for another thread's widget construction\n" + stacks()
    assert a.error is None, a.error
    _box, rc = a.result  # type: ignore[misc]
    rc.close()
    unrelated = u.result
    assert unrelated.comm is not None, "a widget of another thread was closed as an orphan"
    unrelated.close()


def test_widget_that_renders_in_its_constructor():
    """Before: a widget class whose constructor renders reacton (ComponentFunction.widget_class)
    used as an element took the non-reentrant create_lock twice on one thread: hang."""

    @reacton.component
    def Inner(label: str = "x"):
        return w.Button(description=label)

    InnerWidget = Inner.widget_class()  # type: ignore[attr-defined]

    @reacton.component
    def Outer():
        return InnerWidget.element(label="nested")

    finished, t = call_in_thread(lambda: reacton.render(Outer(), handle_error=False), "K", timeout=TIMEOUT)
    assert finished, "nested widget construction deadlocked\n" + stacks()
    assert t.error is None, t.error
    box, rc = t.result
    assert box.children[0].children[0].description == "nested"
    rc.close()
