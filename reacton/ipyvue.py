from typing import Any, Callable, cast

import ipyvue

import reacton as react
from reacton.core import _event_handler_exception_wrapper_and_batch


def use_event(el: react.core.Element, event_and_modifiers, callback: Callable[[Any], Any]):
    # to avoid add_event_handler having a stale reference to callback
    callback_ref = react.use_ref(callback)
    callback_ref.current = callback

    def add_event_handler():
        vue_widget = cast(ipyvue.VueWidget, react.core.get_widget(el))

        def wrapper(*args):
            callback_ref.current(*args)

        vue_widget.on_event(event_and_modifiers, _event_handler_exception_wrapper_and_batch(wrapper))

        def cleanup():
            vue_widget.on_event(event_and_modifiers, wrapper, remove=True)

        return cleanup

    react.use_effect(add_event_handler, [event_and_modifiers])
