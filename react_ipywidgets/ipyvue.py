from typing import cast

import ipyvue

import react_ipywidgets as react


def use_event(el: react.core.Element, event_and_modifiers, callback):
    def add_event_handler():
        vue_widget = cast(ipyvue.VueWidget, react.core.get_widget(el))

        def handler(*args):
            callback(*args)

        vue_widget.on_event(event_and_modifiers, handler)

        def cleanup():
            vue_widget.on_event(event_and_modifiers, handler, remove=True)

        return cleanup

    react.use_side_effect(add_event_handler)
