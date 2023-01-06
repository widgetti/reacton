from typing import Any, Callable, cast

import ipyvue

import reacton as react
from reacton.core import get_render_context


def use_event(el: react.core.Element, event_and_modifiers, callback: Callable[[Any], Any]):
    # to avoid add_event_handler having a stale reference to callback
    callback_ref = react.use_ref(callback)
    callback_ref.current = callback

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
