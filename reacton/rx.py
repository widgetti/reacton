import reactivex

from . import use_effect, use_state


def use_observable_state(obserable: reactivex.Observable, initial_valie):
    value, set_value = use_state(initial_valie)

    def init():
        d = obserable.subscribe(on_next=set_value, on_error=print)
        # d = obserable.on_next(set_value)
        return d.dispose

    use_effect(init, [])
    return value
