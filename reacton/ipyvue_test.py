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
    # falls back to syncing _events from the effect
    assert btn._events == ["click"]
    btn.fire_event("click", {})
    on_click.assert_called_once()
    rc.close()
