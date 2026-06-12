from typing import Any, Callable, cast

import ipyvue

import reacton as react
from reacton.core import ComponentWidget, get_render_context


def use_event(el: react.core.Element, event_and_modifiers, callback: Callable[[Any], Any]):
    # to avoid add_event_handler having a stale reference to callback
    callback_ref = react.use_ref(callback)
    callback_ref.current = callback

    # Put the event name in the widget constructor arguments: the synced _events
    # trait then goes along with the comm open message. The later on_event call
    # (in the effect below) only updates _events when the event set differs, so
    # this saves one update message per widget per event. When the element is
    # reused from a previous render (memoized) and the widget already exists,
    # on_event falls back to syncing _events itself.
    if isinstance(el.component, ComponentWidget) and issubclass(el.component.widget, ipyvue.VueWidget):
        events = el.kwargs.get("_events")
        if events is None:
            el.kwargs["_events"] = [event_and_modifiers]
        elif event_and_modifiers not in events:
            # do not mutate the list, it could be shared with a previous element
            el.kwargs["_events"] = [*events, event_and_modifiers]

    def add_event_handler():
        vue_widget = cast(ipyvue.VueWidget, react.core.get_widget(el))
        # we are basically copying the logic from reacton.core._event_handler_exception_wrapper
        rc = get_render_context()
        context = rc.context
        assert context is not None

        def handler(*args):
            try:
                callback_ref.current(*args)
            except Exception as e:
                assert context is not None
                # because widgets don't have a context, but are a child of a component
                # we add it to exceptions_children, not exception_self
                # this allows a component to catch the exception of a direct child
                context.exceptions_children.append(e)
                rc.force_update()

        vue_widget.on_event(event_and_modifiers, handler)

        def cleanup():
            vue_widget.on_event(event_and_modifiers, handler, remove=True)

        return cleanup

    react.use_effect(add_event_handler, [event_and_modifiers])
