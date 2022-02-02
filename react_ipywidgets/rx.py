import rx

from . import use_side_effect, use_state


def use_observable_state(obserable: rx.Observable, initial_valie):
    value, set_value = use_state(initial_valie)

    def init(widget):
        d = obserable.subscribe(on_next=set_value, on_error=print)
        # d = obserable.on_next(set_value)
        return d.dispose

    use_side_effect(init, [])
    return value
