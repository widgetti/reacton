from typing import List, Union, cast

import ipyvue

import react_ipywidgets as react


def use_event(event_and_modifiers, callback):
    def add_event_handler(children: Union[List[ipyvue.VueWidget], ipyvue.VueWidget]):
        if isinstance(children, list):
            vue_widgets = cast(List[ipyvue.VueWidget], children)
        else:
            vue_widgets = [cast(ipyvue.VueWidget, children)]

        def handler(*args):
            callback(*args)

        for vue_widget in vue_widgets:
            vue_widget.on_event(event_and_modifiers, handler)

        def cleanup():
            for vue_widget in vue_widgets:
                vue_widget.on_event(event_and_modifiers, handler, remove=True)

        return cleanup

    react.use_side_effect(add_event_handler)
