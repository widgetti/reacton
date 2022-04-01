import unittest.mock
from typing import List, TypeVar

import ipywidgets
import ipywidgets as widgets
import numpy as np
import pytest
import traitlets

import react_ipywidgets as react
from react_ipywidgets.core import component, use_side_effect

from . import logging  # noqa: F401
from . import bqplot
from . import ipyvuetify as v
from . import ipywidgets as w

T = TypeVar("T")


def first(container: List[T]) -> T:
    return container[0]


def clear():
    widgets.Widget.widgets = {}


def count():
    return len(widgets.Widget.widgets)


@component
def MyComponent():
    return w.Button()


def test_create_element():
    clear()
    button: react.core.Element[widgets.Button] = react.core.Element[widgets.Button](MyComponent)
    hbox = widgets.HBox()
    assert count() == 2
    react.render(button, hbox, "children")
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Button)
    assert count() == 2 + 3  # button + button layout + button style


def test_monkey_patch():
    # TODO: we do really want to have the Widget.component class method?
    button = widgets.Button.element(description="Hi")
    hbox = widgets.HBox()
    react.render(button, hbox, "children")
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Button)
    assert hbox.children[0].description == "Hi"


def test_component_function():
    clear()
    hbox = widgets.HBox()
    assert count() == 2

    @react.component
    def button_or_label(make_button):
        if make_button:
            return w.Button(description="Button")
        else:
            return w.Label(description="Label")

    react.render(button_or_label(make_button=False), hbox, "children")
    assert count() == 2 + 3  # label + label layout + label style
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Label)
    assert hbox.children[0].description == "Label"

    assert count() == 2 + 3
    react.render(button_or_label(make_button=True), hbox, "children")
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Button)
    assert hbox.children[0].description == "Button"
    assert count() == 2 + 3 + 3  # button + label


def test_component_yield():
    hbox = widgets.HBox()

    @react.component
    def button_and_label(make_button):
        yield w.Button(description="Button")
        yield w.Label(description="Label")

    react.render(button_and_label(make_button=False), hbox, "children")
    assert len(hbox.children) == 2
    assert isinstance(hbox.children[0], widgets.Button)
    assert isinstance(hbox.children[1], widgets.Label)


def test_state():
    clear()
    hbox = widgets.HBox()
    assert count() == 2

    @react.component
    def slider_text():
        value, set_value = react.use_state(0.0)
        description, set_description = react.use_state("Not changed")

        def on_value(value: float):
            set_description(f"Value = {value}")
            set_value(value)

        return w.FloatSlider(value=value, on_value=on_value, description=description)

    react.render(slider_text(), hbox, "children")
    assert count() == 2 + 3

    assert len(hbox.children) == 1
    slider = hbox.children[0]
    assert isinstance(slider, widgets.FloatSlider)

    assert slider.description == "Not changed"

    assert slider.value == 0
    slider.value = 1
    # we should update, not replace
    assert slider is hbox.children[0]
    assert slider.description == "Value = 1.0"
    assert count() == 2 + 3


def test_restore_default():
    @react.component
    def Slider(value):
        return w.IntSlider(value=value, description=f"Value {value}")

    slider, rc = react.render_fixed(Slider(2))
    assert slider.description == "Value 2"
    assert slider.value == 2

    rc.render(Slider(0))
    assert slider.description == "Value 0"
    assert slider.value == 0

    rc.render(Slider(2))
    assert slider.description == "Value 2"
    assert slider.value == 2

    # now start with the default

    slider, rc = react.render_fixed(Slider(0))
    assert slider.description == "Value 0"
    assert slider.value == 0

    rc.render(Slider(2))
    assert slider.description == "Value 2"
    assert slider.value == 2

    rc.render(Slider(0))
    assert slider.description == "Value 0"
    assert slider.value == 0


def test_state_complicated():
    hbox = widgets.HBox()

    @react.component
    def slider_text():
        value, set_value = react.use_state(0.0)
        description, set_description = react.use_state("Initial value")
        set_description(f"Value = {value}")

        def on_value(value: float):
            set_value(value)
            set_description(f"Value = {value}")

        return w.FloatSlider(value=value, on_value=on_value, description=description)

    react.render(slider_text(), hbox, "children")
    slider = hbox.children[0]

    assert slider.description == "Value = 0.0"
    assert slider.value == 0

    slider.value = 1
    assert slider.description == "Value = 1.0"


def test_state_outside():
    clear()
    hbox = widgets.HBox()
    checkbox = widgets.Checkbox(value=False, description="Show button?")
    assert count() == 2 + 3

    @react.component
    def button_or_label(checkbox):
        show_button = react.use_state_widget(checkbox, "value")
        if show_button:
            return w.Button(description="Button")
        else:
            return w.Label(description="Label")

    el = button_or_label(checkbox=checkbox)
    react.render(el, hbox, "children")
    assert count() == 2 + 3 + 3  # added label
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Label)
    assert hbox.children[0].description == "Label"

    before = dict(ipywidgets.Widget.widgets)
    checkbox.value = True
    after = dict(ipywidgets.Widget.widgets)
    diff = set(after) - set(before)
    extra = list(diff)
    assert count() == 2 + 3 + 3 + 3  # added button and button style (layout is not reused, because we are not aware of it being created)
    assert len(extra) == 3
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Button)
    assert hbox.children[0].description == "Button"

    before = dict(ipywidgets.Widget.widgets)
    checkbox.value = False
    after = dict(ipywidgets.Widget.widgets)
    diff = set(after) - set(before)
    extra = list(diff)
    assert len(extra) == 3
    assert count() == 2 + 3 + 3 + 3 + 3  # Label and Layout gets created, TODO: reuse it
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Label)
    assert hbox.children[0].description == "Label"


def test_children():
    clear()
    hbox = widgets.HBox()
    slider = widgets.IntSlider(value=2, description="How many buttons?")
    assert count() == 2 + 3

    @react.component
    def buttons(slider):
        buttons = react.use_state_widget(slider, "value")
        return [w.Button(description=f"Button {i}") for i in range(buttons)]

    el = buttons(slider)
    rc = react.render(el, hbox, "children")
    assert count() == 2 + 3 + 2 * 3  # added 2 buttons
    assert len(hbox.children) == 2
    assert isinstance(hbox.children[0], widgets.Button)
    assert isinstance(hbox.children[1], widgets.Button)
    assert hbox.children[0] != hbox.children[1]
    assert hbox.children[0].description == "Button 0"
    assert hbox.children[1].description == "Button 1"

    slider.value = 3
    assert count() == 2 + 3 + 2 * 3 + 3  # added 1 button
    assert len(hbox.children) == 3
    assert isinstance(hbox.children[0], widgets.Button)
    assert isinstance(hbox.children[1], widgets.Button)
    assert isinstance(hbox.children[2], widgets.Button)
    assert hbox.children[0] != hbox.children[1]
    assert hbox.children[0] != hbox.children[2]
    assert hbox.children[1] != hbox.children[2]
    assert hbox.children[0].description == "Button 0"
    assert hbox.children[1].description == "Button 1"
    assert hbox.children[2].description == "Button 2"

    slider.value = 2
    assert count() == 2 + 3 + 2 * 3 + 3  # nothing added, just 1 unused
    assert len(rc.pool) == 1  # which is added to the pool
    assert len(hbox.children) == 2
    assert isinstance(hbox.children[0], widgets.Button)
    assert isinstance(hbox.children[1], widgets.Button)


def test_display():
    slider = widgets.IntSlider(value=2, description="How many buttons?")

    @react.component
    def buttons(slider):
        buttons = react.use_state_widget(slider, "value")
        return w.Button(description=f"Button {buttons}")

    react.display(buttons(slider))


def test_box():
    clear()
    hbox = widgets.HBox()
    slider = widgets.IntSlider(value=2, description="How many buttons?")
    assert count() == 2 + 3

    @react.component
    def buttons(slider):
        buttons = react.use_state_widget(slider, "value")
        return w.VBox(children=[w.Button(description=f"Button {i}") for i in range(buttons)])

    el = buttons(slider)
    react.render(el, hbox, "children")
    assert count() == 2 + 3 + 2 + 2 * 3  # add vbox and 2 buttons
    assert len(hbox.children[0].children) == 2
    assert isinstance(hbox.children[0].children[0], widgets.Button)
    assert isinstance(hbox.children[0].children[1], widgets.Button)

    slider.value = 3
    assert count() == 2 + 3 + 2 + 2 * 3 + 3  # add 1 button
    assert len(hbox.children[0].children) == 3
    assert isinstance(hbox.children[0].children[0], widgets.Button)
    assert isinstance(hbox.children[0].children[1], widgets.Button)
    assert isinstance(hbox.children[0].children[2], widgets.Button)

    slider.value = 2
    assert count() == 2 + 3 + 2 + 2 * 3 + 3  # nothing should happen
    assert len(hbox.children[0].children) == 2
    assert isinstance(hbox.children[0].children[0], widgets.Button)
    assert isinstance(hbox.children[0].children[1], widgets.Button)


def test_shared_instance():
    clear()
    hbox = widgets.HBox()
    slider = widgets.IntSlider(value=2, description="How many buttons?")
    checkbox = widgets.Checkbox(value=True, description="Share button")
    assert count() == 2 + 3 + 3

    @react.component
    def Buttons(slider, checkbox):
        buttons = react.use_state_widget(slider, "value")
        share = react.use_state_widget(checkbox, "value")
        if share:
            button_shared = w.Button(description="Button shared", tooltip="shared")
            return w.VBox(children=[button_shared, button_shared])
        else:
            return w.VBox(children=[w.Button(description=f"Button {i}") for i in range(buttons)])

    react.render(Buttons(slider, checkbox), hbox, "children")
    vbox = hbox.children[0]
    assert vbox.children[0] is vbox.children[1]
    assert vbox.children[0].description == "Button shared"
    assert vbox.children[0].tooltip == "shared"
    assert count() == 2 + 3 + 3 + 2 + 3  # 1 vbox, 1 button

    checkbox.value = False
    assert count() == 2 + 3 + 3 + 2 + 3 + 3  # 1 extra button
    assert vbox.children[0] is not vbox.children[1]
    assert vbox.children[0].description == "Button 0"
    assert vbox.children[1].description == "Button 1"
    # TODO: fix
    # assert vbox.children[0].tooltip is None
    assert vbox.children[1].tooltip == ""


def test_shared_instance_via_component():
    clear()

    @react.component
    def Child(button):
        return button

    @react.component
    def Buttons():
        button = w.Button(description="Button shared")
        return w.VBox(children=[Child(button), Child(button)])

    vbox, rc = react.render_fixed(Buttons())
    assert vbox.children[0].description == "Button shared"
    assert vbox.children[1].description == "Button shared"
    assert vbox.children[0] is vbox.children[1]


def test_bqplot():
    clear()

    hbox = widgets.HBox()
    exponent = widgets.FloatSlider(min=0.1, max=2, value=1.0, description="Exponent")
    assert count() == 2 + 3

    @react.component
    def Plot(exponent, x, y):
        exponent_value = react.use_state_widget(exponent, "value")
        x = x**exponent_value
        print(x)
        x_scale = bqplot.LinearScale(allow_padding=False)
        y_scale = bqplot.LinearScale(allow_padding=False)
        lines = bqplot.Lines(x=x, y=y, scales={"x": x_scale, "y": y_scale}, stroke_width=3, colors=["red"], display_legend=True, labels=["Line chart"])
        x_axis = bqplot.Axis(scale=x_scale)
        y_axis = bqplot.Axis(scale=y_scale)
        axes = [x_axis, y_axis]
        return bqplot.Figure(axes=axes, marks=[lines], scale_x=x_scale, scale_y=y_scale)

    x = np.arange(4)
    y = x**exponent.value
    react.render(Plot(exponent, x, y), hbox, "children")
    widgets_initial = count()

    figure = hbox.children[0]
    import bqplot as bq  # type: ignore

    assert isinstance(figure.axes[0], bq.Axis)
    assert figure.marks[0].x.tolist() == x.tolist()
    assert figure.axes[0] is not figure.axes[1]
    assert figure.axes[0].scale is not figure.axes[1].scale
    assert figure.axes[0].scale is figure.marks[0].scales["x"]

    before = dict(ipywidgets.Widget.widgets)
    exponent.value = 2
    after = dict(ipywidgets.Widget.widgets)
    diff = set(after) - set(before)
    extra = list(diff)
    assert extra == []

    before = dict(ipywidgets.Widget.widgets)

    assert count() == widgets_initial  # nothing should be recreated
    # figure = box.children[0]
    assert figure.marks[0].x.tolist() == (x**2).tolist()


def test_use_side_effect():
    clear()
    hbox = widgets.HBox()
    assert count() == 2

    @react.component
    def Button2():
        clicks, set_clicks = react.use_state(0)

        def add_event_handler():
            button: widgets.Button = react.core.get_widget(button_el)

            def handler(change):
                set_clicks(clicks + 1)

            button.on_click(handler)
            return lambda: button.on_click(handler, remove=True)

        react.use_side_effect(add_event_handler)
        button_el = w.Button(description=f"Clicked {clicks} times")
        return button_el

    react.render(Button2(), hbox, "children")
    assert count() == 2 + 3  # label + button
    button = hbox.children[0]
    assert button.description == "Clicked 0 times"
    button.click()
    assert len(button._click_handlers.callbacks) == 1
    assert button.description == "Clicked 1 times"


def test_use_side_effect_no_deps():
    clear()
    hbox = widgets.HBox()
    assert count() == 2

    calls = 0
    cleanups = 0

    @react.component
    def TestNoDeps(a, b):
        def test_side_effect():
            def cleanup():
                nonlocal cleanups
                cleanups += 1

            nonlocal calls
            calls += 1
            return cleanup

        react.use_side_effect(test_side_effect)
        return w.Button()

    rc = react.render(TestNoDeps(a=1, b=1), hbox, "children")
    assert calls == 1
    assert cleanups == 0
    rc.render(TestNoDeps(a=1, b=1), hbox)
    assert calls == 2
    assert cleanups == 1


def test_use_side_effect_once():
    clear()
    hbox = widgets.HBox()
    assert count() == 2

    calls = 0
    cleanups = 0

    @react.component
    def TestNoDeps(a, b):
        def test_side_effect():
            def cleanup():
                nonlocal cleanups
                cleanups += 1

            nonlocal calls
            calls += 1
            return cleanup

        react.use_side_effect(test_side_effect, [])
        return w.Button()

    rc = react.render(TestNoDeps(a=1, b=1), hbox, "children")
    assert calls == 1
    assert cleanups == 0
    rc.render(TestNoDeps(a=1, b=1), hbox)
    assert calls == 1
    assert cleanups == 0


def test_use_side_effect_deps():
    clear()
    hbox = widgets.HBox()
    assert count() == 2

    calls = 0
    cleanups = 0

    @react.component
    def TestNoDeps(a, b):
        def test_side_effect():
            def cleanup():
                nonlocal cleanups
                cleanups += 1

            nonlocal calls
            calls += 1
            return cleanup

        react.use_side_effect(test_side_effect, [a, b])
        return w.Button()

    rc = react.render(TestNoDeps(a=1, b=1), hbox, "children")
    assert calls == 1
    assert cleanups == 0
    rc.render(TestNoDeps(a=1, b=1), hbox)
    assert calls == 1
    assert cleanups == 0

    rc.render(TestNoDeps(a=1, b=2), hbox)
    assert calls == 2
    assert cleanups == 1


def test_use_button():
    clear()
    hbox = widgets.HBox()
    assert count() == 2

    @react.component
    def ButtonClicks():
        clicks, set_clicks = react.use_state(0)
        return w.Button(description=f"Clicked {clicks} times", on_click=lambda: set_clicks(clicks + 1))

    react.render(ButtonClicks(), hbox, "children")
    assert count() == 2 + 3  # label + button
    button = hbox.children[0]
    assert button.description == "Clicked 0 times"
    button.click()
    assert len(button._click_handlers.callbacks) == 1
    assert button.description == "Clicked 1 times"


def test_key():
    @react.component
    def ButtonClicks(nr, **kwargs):
        clicks, set_clicks = react.use_state(0)
        return w.Button(description=f"{nr}: Clicked {clicks} times", on_click=lambda: set_clicks(clicks + 1), **kwargs)

    @react.component
    def Buttons():
        count, set_count = react.use_state(3)
        reverse, set_reverse = react.use_state(False)
        slider = w.IntSlider(value=count, description="How many?", on_value=set_count)
        checkbox = w.Checkbox(value=reverse, on_value=lambda x: set_reverse(x), description="Reverse?")
        buttons = [ButtonClicks(i, __key__=f"button-{i}") for i in range(count)]
        if reverse:
            buttons = buttons[::-1]
        buttons_box = w.VBox(children=buttons)
        return w.HBox(children=[slider, checkbox, buttons_box])

    box = react.make(Buttons())
    slider, checkbox, buttons = box.children[0].children
    assert buttons.children[0].description == "0: Clicked 0 times"
    assert buttons.children[1].description == "1: Clicked 0 times"
    assert buttons.children[2].description == "2: Clicked 0 times"
    buttons.children[0].click()
    assert buttons.children[0].description == "0: Clicked 1 times"
    assert buttons.children[1].description == "1: Clicked 0 times"
    assert buttons.children[2].description == "2: Clicked 0 times"
    checkbox.value = True
    assert buttons.children[0].description == "2: Clicked 0 times"
    assert buttons.children[1].description == "1: Clicked 0 times"
    assert buttons.children[2].description == "0: Clicked 1 times"

    slider.value = 2
    assert buttons.children[0].description == "1: Clicked 0 times"
    assert buttons.children[1].description == "0: Clicked 1 times"

    slider.value = 3
    assert buttons.children[0].description == "2: Clicked 0 times"
    assert buttons.children[1].description == "1: Clicked 0 times"
    assert buttons.children[2].description == "0: Clicked 1 times"


def test_vue():
    @react.component
    def Single():
        clicks, set_clicks = react.use_state(0)
        btn = v.Btn(children=[f"Clicks {clicks}"])
        v.use_event(btn, "click", lambda *_ignore: set_clicks(clicks + 1))
        return btn

    btn, _rc = react.render_fixed(Single())
    btn.fire_event("click", {})
    assert btn.children[0] == "Clicks 1"
    assert len(btn._event_handlers_map["click"].callbacks) == 1


def test_interactive():
    @react.component_interactive(count=3)
    def f(count):
        print("COUNT")
        return [w.Button(description=f"Button {i}") for i in range(count)]

    control = f.children[0]
    slider = control.children[0]
    assert isinstance(slider, widgets.IntSlider)
    box = f.children[1]
    button0 = box.children[0]
    assert button0.description == "Button 0"


def test_use_reducer():
    hbox = widgets.HBox()

    def click_reducer(state, action):
        if action == "increment":
            state = state + 1
        return state

    @react.component
    def Button():
        clicks, dispatch = react.use_reducer(click_reducer, 0)
        return w.Button(description=f"Clicked {clicks} times", on_click=lambda: dispatch("increment"))

    react.render(Button(), hbox, "children")
    button = hbox.children[0]
    assert button.description == "Clicked 0 times"
    button.click()
    assert button.description == "Clicked 1 times"
    button.click()
    assert button.description == "Clicked 2 times"


def test_context():
    clear()
    hbox = widgets.HBox()

    def click_reducer(state, action):
        if action == "increment":
            state = state + 1
        return state

    @react.component
    def SubChild2():
        clicks, _dispatch = react.use_context("store")
        return w.Button(description=f"Child2: Clicked {clicks} times")

    @react.component
    def Child2():
        return SubChild2()

    @react.component
    def Child1():
        clicks, dispatch = react.use_context("store")
        return w.Button(description=f"Child1: Clicked {clicks} times", on_click=lambda: dispatch("increment"))

    @react.component
    def App():
        clicks, dispatch = react.use_reducer(click_reducer, 0)
        react.provide_context("store", (clicks, dispatch))
        return [Child1(), Child2()]

    react.render(App(), hbox, "children")
    button1 = hbox.children[0]
    button2 = hbox.children[1]
    assert button1.description == "Child1: Clicked 0 times"
    assert button2.description == "Child2: Clicked 0 times"
    button1.click()
    assert button1.description == "Child1: Clicked 1 times"
    assert button2.description == "Child2: Clicked 1 times"
    button2.click()  # not attached
    assert button1.description == "Child1: Clicked 1 times"
    assert button2.description == "Child2: Clicked 1 times"
    button1.click()
    assert button1.description == "Child1: Clicked 2 times"
    assert button2.description == "Child2: Clicked 2 times"


def test_memo():
    calls_ab = 0
    calls_ac = 0

    @react.component
    def TestMemo(a, b, c):
        def expensive_ab(i, j):
            nonlocal calls_ab
            calls_ab += 1
            return i + j

        @react.use_memo
        def expensive_ac(i, j):
            nonlocal calls_ac
            calls_ac += 1
            return i + j * 2

        x = react.use_memo(expensive_ab, args=[a], kwargs={"j": b})
        y = expensive_ac(a, c)
        return w.Label(value=f"{x} - {y}")

    label, rc = react.render_fixed(TestMemo(a=1, b=2, c=3))
    assert calls_ab == 1
    assert calls_ac == 1
    assert label.value == "3 - 7"

    rc.render(TestMemo(a=1, b=20, c=3))
    assert calls_ab == 2
    assert calls_ac == 1
    assert label.value == "21 - 7"

    rc.render(TestMemo(a=1, b=20, c=30))
    assert calls_ab == 2
    assert calls_ac == 2
    assert label.value == "21 - 61"

    rc.render(TestMemo(a=10, b=20, c=30))
    assert calls_ab == 3
    assert calls_ac == 3
    assert label.value == "30 - 70"


def test_container_context_simple():
    @react.component
    def ContainerContext():
        with w.HBox() as box:
            w.Label(value="in container")
            w.Button(description="button")
        return box

    box, rc = react.render_fixed(ContainerContext())
    assert len(box.children) == 2
    assert box.children[0]


def test_container_context_bqplot():
    @react.component
    def ContainerContext(exponent=1.2):
        x = np.arange(4)
        y = x**1.2
        with w.HBox() as box:
            x_scale = bqplot.LinearScale(allow_padding=False)
            y_scale = bqplot.LinearScale(allow_padding=False)
            lines = bqplot.Lines(x=x, y=y, scales={"x": x_scale, "y": y_scale}, stroke_width=3, colors=["red"], display_legend=True, labels=["Line chart"])
            x_axis = bqplot.Axis(scale=x_scale)
            y_axis = bqplot.Axis(scale=y_scale)
            axes = [x_axis, y_axis]
            bqplot.Figure(axes=axes, marks=[lines], scale_x=x_scale, scale_y=y_scale)
        return box

    box, rc = react.render_fixed(ContainerContext())
    assert len(box.children) == 1
    # assert isinstance(box.children[0],


def test_get_widget():

    button = None

    @component
    def Multiple():
        def get_widgets():
            nonlocal button
            button = react.core.get_widget(button1el)

        use_side_effect(get_widgets)
        with w.VBox() as main:
            button1el = w.Button(description="1")
        return main

    box, _rc = react.render_fixed(Multiple())
    assert box.children[0] is button


def test_on_argument():
    # since we have special treatment with on_, lets test special cases
    # like an argument with the same name
    @component
    def Test(on_test):
        on_test("hi")
        return w.Button()

    mock = unittest.mock.Mock()
    box, _rc = react.render_fixed(Test(on_test=mock))
    mock.assert_called()


def test_on_trait():
    # similar to an argument, but now a trait that happens to start with on_
    class SomeWidget(widgets.Button):
        on_hover = traitlets.traitlets.Callable(None, allow_none=True)

    mock = unittest.mock.Mock()
    widget, _rc = react.render_fixed(SomeWidget.element(on_hover=mock))
    assert widget.on_hover is mock
    # mock.assert_called()


def test_other_event_handlers():
    # previously, we used unobserve_all, which removed event handlers not attached via on_ arguments
    mock = unittest.mock.Mock()

    @component
    def Test():
        value, set_value = react.use_state("hi")
        text = w.Text(value=value, on_value=set_value)

        def add_my_own_event_handler():
            widget = react.get_widget(text)

            def event_handler(change):
                mock(change.new)

            # react is not aware of this event handler, and should not
            # remove it
            widget.observe(event_handler, "value")
            return lambda: None

        use_side_effect(add_my_own_event_handler, [])  # only add it once
        return text

    text, _rc = react.render_fixed(Test())
    # first time, it's always ok
    text.value = "hallo"
    mock.assert_called()
    mock.reset_mock()
    # second time, we executed the render loop again, did we remove the event handler?
    text.value = "ola"
    mock.assert_called()


def test_state_leak_different_components():
    @react.component
    def SliderComponent():
        value, set_value = react.use_state(1)
        return w.IntSlider(value=value, on_value=set_value)

    @react.component
    def OtherComponent():
        value, set_value = react.use_state(10)
        return w.IntText(value=value, on_value=set_value)

    set_show_other = None

    @react.component
    def Test():
        nonlocal set_show_other
        show_other, set_show_other = react.use_state(False)
        with w.VBox() as main:
            if show_other:
                OtherComponent()
            else:
                SliderComponent()
        return main

    test, _rc = react.render_fixed(Test())
    assert set_show_other is not None
    assert test.children[0].value == 1
    set_show_other(True)
    assert test.children[0].value == 10
    test.children[0].value = 11
    set_show_other(False)
    assert test.children[0].value == 1
    test.children[0].value = 2
    set_show_other(True)
    # the state should be reset, if the component was detached
    assert test.children[0].value == 10
    set_show_other(False)
    assert test.children[0].value == 1


def test_exceptions(capsys):
    @react.component
    def Test():
        return w.Button()

    with pytest.raises(TypeError):
        test, _rc = react.render_fixed(Test(non_existing_arg=1), handle_error=False)  # type: ignore
    assert react.render_fixed(Test(non_existing_arg=1), handle_error=True)[0] is None  # type: ignore
    out = str(capsys.readouterr().out)
    # put in
    # extra lines
    # to avoid the stderr
    # to in include the next line
    assert "non_existing_arg" in out


def test_mime_bundle():
    @react.component(mime_bundle={"text/plain": "text"})
    def Test(a=1):
        return w.Button()

    el = Test()
    assert el.mime_bundle["text/plain"] == "text"


def test_use_state_with_function():
    @react.component
    def ButtonClick(label="Hi"):
        clicks, set_clicks = react.use_state(0)

        def update_click(click):
            return click + 1

        return w.Button(description=f"{label}: Clicked {clicks} times", on_click=lambda: set_clicks(update_click))

    clicker, _rc = react.render_fixed(ButtonClick())
    clicker.click()
    assert clicker.description == "Hi: Clicked 1 times"
