import unittest.mock

import ipyvuetify
import ipyvue

import reacton as react

from . import ipyvuetify as v
from .ipyvue import use_event


def test_use_event_no_sync_messages():
    """The _events trait should be set at construction and never re-assigned.

    Re-assigning it (by on_event during the effect, or on_event(remove=True)
    during close) sends one widget update message per widget per event.
    """
    on_click = unittest.mock.Mock()

    @react.component
    def Test():
        btn = v.Btn(children=["click me"])
        use_event(btn, "click", on_click)
        return btn

    box, rc = react.render(Test(), handle_error=False)
    btn = rc.find(ipyvuetify.Btn).widget

    events_changes = unittest.mock.Mock()
    btn.observe(events_changes, "_events")

    # the event name went along with the constructor arguments
    assert btn._events == ["click"]
    # and the handler works
    btn.fire_event("click", {})
    on_click.assert_called_once()

    rc.force_update()
    events_changes.assert_not_called()

    rc.close()
    events_changes.assert_not_called()


def test_use_event_removed_on_rerender():
    """When the widget persists but the event changes, _events must sync."""
    on_event = unittest.mock.Mock()
    set_event_name = None

    @react.component
    def Test():
        nonlocal set_event_name
        event_name, set_event_name = react.use_state("click")
        btn = v.Btn(children=["click me"])
        use_event(btn, event_name, on_event)
        return btn

    box, rc = react.render(Test(), handle_error=False)
    btn = rc.find(ipyvuetify.Btn).widget
    assert btn._events == ["click"]
    assert set_event_name is not None
    set_event_name("dblclick")
    assert btn._events == ["dblclick"]
    btn.fire_event("dblclick", {})
    on_event.assert_called_once()
    rc.close()


def test_use_event_component_element():
    """use_event on a component element (not a widget element) keeps working."""
    on_click = unittest.mock.Mock()

    @react.component
    def Button():
        return v.Btn(children=["click me"])

    @react.component
    def Test():
        btn = Button()
        use_event(btn, "click", on_click)
        return btn

    box, rc = react.render(Test(), handle_error=False)
    btn = rc.find(ipyvuetify.Btn).widget
    assert isinstance(btn, ipyvue.VueWidget)
    # falls back to syncing _events from on_event
    assert btn._events == ["click"]
    btn.fire_event("click", {})
    on_click.assert_called_once()
    rc.close()


def test_use_event_latest_callback():
    """The handler is registered once, and calls the callback of the latest render."""
    calls = []
    set_count = None

    @react.component
    def Test():
        nonlocal set_count
        count, set_count = react.use_state(0)
        btn = v.Btn(children=[f"count {count}"])
        use_event(btn, "click", lambda *_ignore: calls.append(count))
        return btn

    box, rc = react.render(Test(), handle_error=False)
    btn = rc.find(ipyvuetify.Btn).widget
    btn.fire_event("click", {})
    assert set_count is not None
    set_count(1)
    set_count(2)
    btn.fire_event("click", {})
    # one handler, not one per render
    assert calls == [0, 2]
    assert len(btn._event_handlers_map["click"].callbacks) == 1
    rc.close()


def test_use_event_removed_when_component_goes():
    """A child registers an event on a widget of its parent; when the child goes, the handler goes."""
    on_click = unittest.mock.Mock()
    set_show = None

    @react.component
    def Child(btn):
        use_event(btn, "click", on_click)
        return v.Html(tag="span", children=["child"])

    @react.component
    def Test():
        nonlocal set_show
        show, set_show = react.use_state(True)
        btn = v.Btn(children=["click me"])
        children = [btn, Child(btn)] if show else [btn]
        return v.Html(tag="div", children=children)

    box, rc = react.render(Test(), handle_error=False)
    btn = rc.find(ipyvuetify.Btn).widget
    btn.fire_event("click", {})
    assert on_click.call_count == 1
    assert set_show is not None
    set_show(False)
    assert rc.find(ipyvuetify.Btn).widget is btn
    # the handler is gone (the old use_event could not do this: its effect only looked for
    # the widget in the subtree of the component, and raised)
    assert "click" not in btn._event_handlers_map
    assert on_click.call_count == 1
    rc.close()


def test_use_event_widget_replaced():
    """When the element's widget is replaced (another key), the handler moves to the new widget."""
    on_click = unittest.mock.Mock()
    set_key = None

    @react.component
    def Test():
        nonlocal set_key
        key, set_key = react.use_state("a")
        btn = v.Btn(children=["click me"]).key(key)
        use_event(btn, "click", on_click)
        return v.Html(tag="div", children=[btn])

    box, rc = react.render(Test(), handle_error=False)
    first = rc.find(ipyvuetify.Btn).widget
    assert set_key is not None
    set_key("b")
    second = rc.find(ipyvuetify.Btn).widget
    assert second is not first
    second.fire_event("click", {})
    on_click.assert_called_once()
    rc.close()


def test_use_event_on_existing_widget():
    """A new child hooks into an element (and widget) of its parent that exists already."""
    on_click = unittest.mock.Mock()
    set_show = None

    @react.component
    def Child(btn):
        use_event(btn, "click", on_click)
        return v.Html(tag="span", children=["child"])

    @react.component
    def Test():
        nonlocal set_show
        show, set_show = react.use_state(False)
        btn = react.use_memo(lambda: v.Btn(children=["click me"]), [])
        children = [btn, Child(btn)] if show else [btn]
        return v.Html(tag="div", children=children)

    box, rc = react.render(Test(), handle_error=False)
    btn = rc.find(ipyvuetify.Btn).widget
    assert set_show is not None
    set_show(True)
    assert rc.find(ipyvuetify.Btn).widget is btn
    btn.fire_event("click", {})
    on_click.assert_called_once()
    set_show(False)
    assert "click" not in btn._event_handlers_map
    rc.close()


def test_use_event_target_changes_kind():
    """The element changes between a widget and a component element: the hook counts stay equal."""
    on_click = unittest.mock.Mock()
    set_kind = None

    @react.component
    def Card(children=[]):
        return v.Btn(children=children)

    @react.component
    def Test():
        nonlocal set_kind
        kind, set_kind = react.use_state("widget")
        target = v.Btn(children=["widget"]) if kind == "widget" else Card(children=["component"])
        use_event(target, "click", on_click)
        return v.Html(tag="div", children=[target])

    box, rc = react.render(Test(), handle_error=False)
    assert set_kind is not None
    for kind in ["component", "widget", "component", "widget"]:
        before = rc.find(ipyvuetify.Btn).widget
        set_kind(kind)
        btn = rc.find(ipyvuetify.Btn).widget
        assert btn is not before
        assert btn.children == [kind]
        on_click.reset_mock()
        btn.fire_event("click", {})
        on_click.assert_called_once()
    rc.close()


def test_use_event_not_registered_after_removal():
    """A removed hook does not come back when the element (kept by a parent) gets a new widget."""
    on_click = unittest.mock.Mock()
    set_show = None

    @react.component
    def Child(btn):
        use_event(btn, "click", on_click)
        return v.Html(tag="span", children=["child"])

    @react.component
    def Test():
        nonlocal set_show
        show, set_show = react.use_state(True)
        btn = react.use_memo(lambda: v.Btn(children=["click me"]), [])
        # the button moves (another default key) when the child goes: a new widget
        children = [btn, Child(btn)] if show else [v.Html(tag="span", children=["x"]), btn]
        return v.Html(tag="div", children=children)

    box, rc = react.render(Test(), handle_error=False)
    first = rc.find(ipyvuetify.Btn).widget
    first.fire_event("click", {})
    on_click.assert_called_once()
    assert set_show is not None
    set_show(False)
    btn = rc.find(ipyvuetify.Btn).widget
    assert btn is not first
    assert "click" not in btn._event_handlers_map
    rc.close()


def test_use_event_component_element_widget_changes():
    """On a component element, the handler goes to the widget of the element its body returns
    (also through a nested component), and moves when that widget changes."""
    on_click = unittest.mock.Mock()
    set_key = None

    @react.component
    def Inner():
        nonlocal set_key
        key, set_key = react.use_state("a")
        return v.Btn(children=[key]).key(key)

    @react.component
    def Outer():
        return Inner()

    @react.component
    def Test():
        target = Outer()
        use_event(target, "click", on_click)
        return v.Html(tag="div", children=[target])

    box, rc = react.render(Test(), handle_error=False)
    first = rc.find(ipyvuetify.Btn).widget
    first.fire_event("click", {})
    on_click.assert_called_once()
    assert set_key is not None
    set_key("b")
    second = rc.find(ipyvuetify.Btn).widget
    assert second is not first
    on_click.reset_mock()
    second.fire_event("click", {})
    on_click.assert_called_once()
    rc.close()
