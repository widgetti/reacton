import traceback
import unittest.mock
from typing import List, TypeVar

import ipywidgets
import ipywidgets as widgets
import numpy as np
import pytest
import traitlets

import react_ipywidgets as react
from react_ipywidgets.core import component, use_effect

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


# components used for testing


@component
def MyComponent():
    return w.Button()


@react.component
def ButtonComponentFunction(**kwargs):
    return w.Button(**kwargs)


@react.component
def ButtonNumber(value):
    # to test state reuse
    value, set_value = react.use_state(value)
    return w.Button(description=str(value))


@react.component
def ButtonNumber2(value):
    # to test state reuse
    value, set_value = react.use_state(value)
    return w.Button(description=str(value))


@react.component
def Container(children=[]):
    return w.HBox(children=children)


@pytest.fixture(autouse=True)
def cleanup_guard():
    before = set(widgets.Widget.widgets)
    yield
    after = set(widgets.Widget.widgets)
    leftover = after - before
    if leftover:
        leftover_widgets = [widgets.Widget.widgets[k] for k in leftover]
        assert not leftover_widgets
        # raise RuntimeError(f"{leftover_widgets}")


# @pytest.fixture(params=["ButtonComponentWidget", "ButtonComponentFunction"])
@pytest.fixture(params=["ButtonComponentWidget"])
def ButtonComponent(request):
    return dict(ButtonComponentWidget=w.Button, ButtonComponentFunction=ButtonComponentFunction)[request.param]


def test_internals():
    @react.component
    def Child():
        return w.VBox()

    @react.component
    def App():
        return Child().key("child")  # type: ignore

    app = App()

    # root_context:
    #     element: App
    #     children:
    #     - '/':
    widget, rc = react.render_fixed(app, handle_error=False)
    assert rc.context_root.root_element == app
    assert list(rc.context_root.children_next) == []
    assert list(rc.context_root.children) == ["App/"]

    app_context = rc.context_root.children["App/"]
    assert list(app_context.children_next) == []
    assert list(app_context.children) == ["child"]
    assert app_context.invoke_element is app

    rc.close()

    # assert app_context.children["child"].invoke_element is app_context.elements["child"]
    # assert list(rc.context_root.children["/"].children["child"].invoke_element) == ["child"]


def test_create_element():
    clear()
    button: react.core.Element[widgets.Button] = react.core.Element[widgets.Button](MyComponent)
    assert count() == 0
    hbox, rc = react.render(button, handle_error=False)
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Button)
    assert count() == 2 + 3  # button + button layout + button style
    rc.close()


def test_monkey_patch():
    button = widgets.Button.element(description="Hi")
    hbox, rc = react.render(button)
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Button)
    assert hbox.children[0].description == "Hi"
    rc.close()


def test_component_function():
    clear()
    assert count() == 0

    @react.component
    def button_or_label(make_button):
        if make_button:
            return w.Button(description="Button")
        else:
            return w.Label(description="Label")

    hbox, rc = react.render(button_or_label(make_button=False))
    assert count() == 2 + 3  # label + label layout + label style
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Label)
    assert hbox.children[0].description == "Label"
    rc.close()

    assert count() == 0
    hbox, rc = react.render(button_or_label(make_button=True), hbox, "children")
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Button)
    assert hbox.children[0].description == "Button"
    assert count() == 3  # button + label
    rc.close()


def test_state_simple():
    clear()

    @react.component
    def slider_text():
        value, set_value = react.use_state(0.0)
        description, set_description = react.use_state("Not changed")

        def on_value(value: float):
            set_description(f"Value = {value}")
            set_value(value)

        return w.FloatSlider(value=value, on_value=on_value, description=description)

    hbox, rc = react.render(slider_text())
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
    rc.close()


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
    rc.close()

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
    rc.close()


def test_state_complicated():
    @react.component
    def slider_text():
        value, set_value = react.use_state(0.0)
        description, set_description = react.use_state("Initial value")
        set_description(f"Value = {value}")

        def on_value(value: float):
            set_value(value)
            set_description(f"Value = {value}")

        return w.FloatSlider(value=value, on_value=on_value, description=description)

    slider, rc = react.render_fixed(slider_text())

    assert slider.description == "Value = 0.0"
    assert slider.value == 0

    slider.value = 1
    assert slider.description == "Value = 1.0"
    rc.close()


def test_state_outside():
    clear()
    checkbox = widgets.Checkbox(value=False, description="Show button?")
    assert count() == 3

    @react.component
    def button_or_label(checkbox):
        show_button = react.use_state_widget(checkbox, "value")
        if show_button:
            return w.Button(description="Button")
        else:
            return w.Label(description="Label")

    el = button_or_label(checkbox=checkbox)
    hbox, rc = react.render(el)

    assert count() == 3 + 2 + 3  # checkbox, box, label
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Label)
    assert hbox.children[0].description == "Label"

    before = dict(ipywidgets.Widget.widgets)
    checkbox.value = True
    after = dict(ipywidgets.Widget.widgets)
    diff = set(after) - set(before)
    extra = list(diff)
    assert count() == 3 + 2 + 3  # similar
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
    assert count() == 3 + 2 + 3
    assert len(hbox.children) == 1
    assert isinstance(hbox.children[0], widgets.Label)
    assert hbox.children[0].description == "Label"
    rc.close()
    checkbox.layout.close()
    checkbox.style.close()
    checkbox.close()


def test_children():
    clear()
    # hbox = widgets.HBox()
    # slider = widgets.IntSlider(value=2, description="How many buttons?")

    @react.component
    def buttons():
        buttons, set_buttons = react.use_state(2)
        with w.HBox() as main:
            _ = w.IntSlider(value=buttons, on_value=set_buttons, description="How many buttons?")
            _ = [w.Button(description=f"Button {i}") for i in range(buttons)]
        return main

    hbox, rc = react.render_fixed(buttons())
    slider = hbox.children[0]
    # hbox + slider: 2 + 3
    assert count() == 2 + 3 + 2 * 3  # added 2 buttons
    assert len(hbox.children) == 1 + 2
    assert isinstance(hbox.children[1], widgets.Button)
    assert isinstance(hbox.children[2], widgets.Button)
    assert hbox.children[1] != hbox.children[2]
    assert hbox.children[1].description == "Button 0"
    assert hbox.children[2].description == "Button 1"

    slider.value = 3
    assert len(hbox.children) == 1 + 3
    assert count() == 2 + 3 + 2 * 3 + 3  # added 1 button
    assert isinstance(hbox.children[1], widgets.Button)
    assert isinstance(hbox.children[2], widgets.Button)
    assert isinstance(hbox.children[3], widgets.Button)
    assert hbox.children[1] != hbox.children[2]
    assert hbox.children[1] != hbox.children[3]
    assert hbox.children[2] != hbox.children[3]
    assert hbox.children[1].description == "Button 0"
    assert hbox.children[2].description == "Button 1"
    assert hbox.children[3].description == "Button 2"

    slider.value = 2
    assert count() == 2 + 3 + 2 * 3  # nothing added, just 1 unused
    # TODO: what do we do with pool?
    # assert len(rc.pool) == 1  # which is added to the pool
    assert len(hbox.children) == 1 + 2
    assert isinstance(hbox.children[1], widgets.Button)
    assert isinstance(hbox.children[2], widgets.Button)
    rc.close()


def test_display():
    slider = widgets.IntSlider(value=2, description="How many buttons?")

    @react.component
    def buttons(slider):
        buttons = react.use_state_widget(slider, "value")
        return w.Button(description=f"Button {buttons}")

    react.display(buttons(slider))
    assert react.core._last_rc is not None
    react.core._last_rc.close()
    slider.style.close()
    slider.layout.close()
    slider.close()


def test_box():
    hbox = widgets.HBox()
    slider = widgets.IntSlider(value=2, description="How many buttons?")
    assert count() == 2 + 3

    @react.component
    def buttons(slider):
        buttons = react.use_state_widget(slider, "value")
        return w.VBox(children=[w.Button(description=f"Button {i}") for i in range(buttons)])

    el = buttons(slider)
    hbox, rc = react.render(el, hbox, "children")
    assert count() == 2 + 3 + 2 + 2 * 3  # add vbox and 2 buttons
    assert len(hbox.children[0].children) == 2
    assert isinstance(hbox.children[0].children[0], widgets.Button)
    assert isinstance(hbox.children[0].children[1], widgets.Button)

    slider.value = 3
    rc.force_update()
    assert count() == 2 + 3 + 2 + 2 * 3 + 3  # add 1 button
    assert len(hbox.children[0].children) == 3
    assert isinstance(hbox.children[0].children[0], widgets.Button)
    assert isinstance(hbox.children[0].children[1], widgets.Button)
    assert isinstance(hbox.children[0].children[2], widgets.Button)

    slider.value = 2
    rc.force_update()
    assert count() == 2 + 3 + 2 + 2 * 3  # should clean up
    assert len(hbox.children[0].children) == 2
    assert isinstance(hbox.children[0].children[0], widgets.Button)
    assert isinstance(hbox.children[0].children[1], widgets.Button)
    rc.close()
    slider.style.close()
    slider.layout.close()
    slider.close()


def test_shared_instance(ButtonComponent):
    checkbox = widgets.Checkbox(value=True, description="Share button")

    @react.component
    def Buttons(checkbox):
        share = react.use_state_widget(checkbox, "value", "share")
        if share:
            button_shared = ButtonComponent(description="Button shared", tooltip="shared")
            return w.VBox(children=[button_shared, button_shared])
        else:
            return w.VBox(children=[ButtonComponent(description=f"Button {i}") for i in range(2)])

    hbox, rc = react.render(Buttons(checkbox))
    vbox = hbox.children[0]
    assert vbox.children[0] is vbox.children[1]
    assert vbox.children[0].description == "Button shared"
    assert vbox.children[0].tooltip == "shared"

    checkbox.value = False
    rc.force_update()
    assert vbox.children[0] is not vbox.children[1]
    assert vbox.children[0].description == "Button 0"
    assert vbox.children[1].description == "Button 1"
    assert vbox.children[0].tooltip == ""
    assert vbox.children[1].tooltip == ""
    rc.close()
    checkbox.style.close()
    checkbox.layout.close()
    checkbox.close()


def test_shared_instance_via_component(ButtonComponent):
    @react.component
    def Child(button):
        return button

    @react.component
    def Buttons():
        button = ButtonComponent(description="Button shared")
        return w.VBox(children=[Child(button), Child(button)])

    vbox, rc = react.render_fixed(Buttons())
    assert vbox.children[0].description == "Button shared"
    assert vbox.children[1].description == "Button shared"
    assert vbox.children[0] is vbox.children[1]
    rc.close()


def test_bqplot():
    clear()

    exponent = widgets.FloatSlider(min=0.1, max=2, value=1.0, description="Exponent")
    assert count() == 3

    @react.component
    def Plot(exponent, x, y):
        exponent_value = react.use_state_widget(exponent, "value")
        x = x**exponent_value
        x_scale = bqplot.LinearScale(allow_padding=False)
        y_scale = bqplot.LinearScale(allow_padding=False)
        lines = bqplot.Lines(x=x, y=y, scales={"x": x_scale, "y": y_scale}, stroke_width=3, colors=["red"], display_legend=True, labels=["Line chart"])
        x_axis = bqplot.Axis(scale=x_scale)
        y_axis = bqplot.Axis(scale=y_scale)
        axes = [x_axis, y_axis]
        return bqplot.Figure(axes=axes, marks=[lines], scale_x=x_scale, scale_y=y_scale)

    x = np.arange(4)
    y = x**exponent.value
    hbox, rc = react.render(Plot(exponent, x, y))
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
    exponent.style.close()
    exponent.layout.close()
    exponent.close()
    rc.close()


def test_use_effect():
    @react.component
    def Button2():
        clicks, set_clicks = react.use_state(0)

        def add_event_handler():
            button: widgets.Button = react.core.get_widget(button_el)

            def handler(change):
                set_clicks(clicks + 1)

            button.on_click(handler)
            return lambda: button.on_click(handler, remove=True)

        react.use_effect(add_event_handler)
        button_el = w.Button(description=f"Clicked {clicks} times")
        return button_el

    hbox, rc = react.render(Button2())
    assert count() == 2 + 3  # label + button
    button = hbox.children[0]
    assert button.description == "Clicked 0 times"
    button.click()
    assert len(button._click_handlers.callbacks) == 1
    assert button.description == "Clicked 1 times"
    rc.close()


def test_use_effect_no_deps():
    calls = 0
    cleanups = 0

    @react.component
    def TestNoDeps(a, b):
        def test_effect():
            def cleanup():
                nonlocal cleanups
                cleanups += 1

            nonlocal calls
            calls += 1
            return cleanup

        react.use_effect(test_effect)
        return w.Button()

    hbox, rc = react.render(TestNoDeps(a=1, b=1))
    assert calls == 1
    assert cleanups == 0
    rc.render(TestNoDeps(a=1, b=1), hbox)
    assert calls == 2
    assert cleanups == 1
    rc.close()


def test_use_effect_once():
    calls = 0
    cleanups = 0
    counters_seen = []

    @react.component
    def TestNoDeps(a, b):
        counter, set_counter = react.use_state(0)

        def test_effect():
            def cleanup():
                nonlocal cleanups
                cleanups += 1

            nonlocal calls
            calls += 1
            # we should only be executed after the last render
            # when counter is 1
            counters_seen.append(counter)
            return cleanup

        # this forces a rerender, but the use_effect should
        # still be called just once
        if counter == 0:
            set_counter(1)

        react.use_effect(test_effect, [])
        return w.Button()

    hbox, rc = react.render(TestNoDeps(a=1, b=1))
    assert calls == 1
    assert cleanups == 0
    assert counters_seen == [1]
    rc.render(TestNoDeps(a=1, b=1), hbox)
    assert calls == 1
    assert cleanups == 0
    rc.close()


def test_use_effect_deps():
    calls = 0
    cleanups = 0

    @react.component
    def TestNoDeps(a, b):
        def test_effect():
            def cleanup():
                nonlocal cleanups
                cleanups += 1

            nonlocal calls
            calls += 1
            return cleanup

        react.use_effect(test_effect, [a, b])
        return w.Button()

    hbox, rc = react.render(TestNoDeps(a=1, b=1))
    assert calls == 1
    assert cleanups == 0
    rc.render(TestNoDeps(a=1, b=1), hbox)
    assert calls == 1
    assert cleanups == 0

    rc.render(TestNoDeps(a=1, b=2), hbox)
    assert calls == 2
    assert cleanups == 1
    rc.close()


@react.component
def ButtonClicks(**kwargs):
    clicks, set_clicks = react.use_state(0)
    return w.Button(description=f"Clicked {clicks} times", on_click=lambda: set_clicks(clicks + 1), **kwargs)


def test_use_button():
    hbox, rc = react.render(ButtonClicks())
    assert count() == 2 + 3  # label + button
    button = hbox.children[0]
    assert button.description == "Clicked 0 times"
    button.click()
    assert len(button._click_handlers.callbacks) == 1
    assert button.description == "Clicked 1 times"
    rc.close()


def test_key_widget():
    set_reverse = None

    @react.component
    def Buttons():
        nonlocal set_reverse
        reverse, set_reverse = react.use_state(False)
        with w.VBox() as main:
            if reverse:
                widgets.IntSlider.element(value=4).key("slider")
                widgets.Button.element(description="Hi").key("btn")
            else:
                widgets.Button.element(description="Hi").key("btn")
                widgets.IntSlider.element(value=4).key("slider")
        return main

    box = react.make(Buttons(), handle_error=False)
    assert react.core._last_rc
    rc = react.core._last_rc
    assert set_reverse is not None
    button1, slider1 = box.children[0].children
    assert isinstance(button1, widgets.Button)
    assert isinstance(slider1, widgets.IntSlider)
    set_reverse(True)
    rc.force_update()
    slider2, button2 = box.children[0].children
    assert isinstance(button2, widgets.Button)
    assert isinstance(slider2, widgets.IntSlider)
    assert button1 is button2
    assert slider1 is slider2
    assert react.core._last_rc
    rc.close()


def test_key_root():
    @react.component
    def Buttons():
        return widgets.Button.element(description="Hi").key("btn")

    box = react.make(Buttons(), handle_error=False)
    button = box.children[0]
    assert isinstance(button, widgets.Button)
    assert react.core._last_rc
    react.core._last_rc.close()


def test_key_component_function():
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
        buttons = [ButtonClicks(i).key(f"button-{i}") for i in range(count)]
        if reverse:
            buttons = buttons[::-1]
        buttons_box = w.VBox(children=buttons)
        return w.HBox(children=[slider, checkbox, buttons_box])

    box = react.make(Buttons(), handle_error=False)
    assert react.core._last_rc
    rc = react.core._last_rc
    slider, checkbox, buttons = box.children[0].children
    assert buttons.children[0].description == "0: Clicked 0 times"
    assert buttons.children[1].description == "1: Clicked 0 times"
    assert buttons.children[2].description == "2: Clicked 0 times"
    buttons.children[0].click()
    rc.force_update()
    assert buttons.children[0].description == "0: Clicked 1 times"
    assert buttons.children[1].description == "1: Clicked 0 times"
    assert buttons.children[2].description == "2: Clicked 0 times"
    checkbox.value = True
    rc.force_update()
    assert buttons.children[0].description == "2: Clicked 0 times"
    assert buttons.children[1].description == "1: Clicked 0 times"
    assert buttons.children[2].description == "0: Clicked 1 times"

    slider.value = 2
    rc.force_update()
    assert buttons.children[0].description == "1: Clicked 0 times"
    assert buttons.children[1].description == "0: Clicked 1 times"

    slider.value = 3
    rc.force_update()
    assert buttons.children[0].description == "2: Clicked 0 times"
    assert buttons.children[1].description == "1: Clicked 0 times"
    assert buttons.children[2].description == "0: Clicked 1 times"
    rc.close()


def test_key_collision():
    @react.component
    def Child():
        return w.Button()

    @react.component
    def Test():
        with w.HBox() as main:
            Child().key("collide")  # type: ignore
            Child().key("collide")  # type: ignore
        return main

    with pytest.raises(KeyError, match="Duplicate"):
        hbox, _rc = react.render_fixed(Test(), handle_error=False)


def test_vue():
    @react.component
    def Single():
        clicks, set_clicks = react.use_state(0)
        btn = v.Btn(children=[f"Clicks {clicks}"])
        v.use_event(btn, "click", lambda *_ignore: set_clicks(clicks + 1))
        return btn

    btn, rc = react.render_fixed(Single())
    btn.fire_event("click", {})
    assert btn.children[0] == "Clicks 1"
    assert len(btn._event_handlers_map["click"].callbacks) == 1
    rc.force_update()
    rc.close()


def test_interactive():
    @react.component_interactive(count=3)
    def f(count):
        with w.HBox() as main:
            [w.Button(description=f"Button {i}") for i in range(count)]
        return main

    control = f.children[0]
    slider = control.children[0]
    assert isinstance(slider, widgets.IntSlider)
    box = f.children[1]
    hbox = box.children[0]
    button0 = hbox.children[0]
    assert button0.description == "Button 0"
    assert react.core._last_rc is not None
    react.core._last_rc.close()
    for widget in control.children:
        if hasattr(widget, "layout"):
            widget.layout.close()
        if hasattr(widget, "style"):
            widget.style.close()
        widget.close()
    control.close()
    control.layout.close()
    assert react.core._last_interactive_vbox is not None
    react.core._last_interactive_vbox.layout.close()
    react.core._last_interactive_vbox.close()


def test_use_reducer():
    def click_reducer(state, action):
        if action == "increment":
            state = state + 1
        return state

    @react.component
    def Button():
        clicks, dispatch = react.use_reducer(click_reducer, 0)
        return w.Button(description=f"Clicked {clicks} times", on_click=lambda: dispatch("increment"))

    hbox, rc = react.render(Button())
    button = hbox.children[0]
    assert button.description == "Clicked 0 times"
    button.click()
    assert button.description == "Clicked 1 times"
    button.click()
    assert button.description == "Clicked 2 times"
    rc.close()


def test_context():
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
        with w.HBox() as main:
            Child1()
            Child2()
        return main

    hbox, rc = react.render_fixed(App())
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
    rc.close()


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
    rc.close()


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
    rc.close()


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
    rc.close()


def test_get_widget():

    button1 = None
    button2 = None

    @component
    def Multiple():
        def get_widgets():
            nonlocal button1
            nonlocal button2
            button1 = react.core.get_widget(button1el)
            button2 = react.core.get_widget(button2el)

        use_effect(get_widgets)
        with w.VBox() as main:
            button1el = w.Button(description="1")
            button2el = w.Button(description="2")
        return main

    box, rc = react.render_fixed(Multiple())
    assert box.children[0] is button1
    assert box.children[1] is button2
    rc.close()


def test_get_widget_multi_render():
    button = None

    @component
    def Multiple():
        value, set_value = react.use_state(0)

        def get_widgets():
            nonlocal button
            button = react.core.get_widget(button_el)

        use_effect(get_widgets, [])
        if value < 3:
            set_value(value + 1)
        with w.VBox() as main:
            button_el = w.Button(description="1")
        return main

    box, rc = react.render_fixed(Multiple())
    assert box.children[0] is button
    rc.close()


def test_on_argument():
    # since we have special treatment with on_, lets test special cases
    # like an argument with the same name
    @component
    def Test(on_test):
        on_test("hi")
        return w.Button()

    mock = unittest.mock.Mock()
    box, rc = react.render_fixed(Test(on_test=mock))
    mock.assert_called()
    rc.close()


def test_on_trait():
    # similar to an argument, but now a trait that happens to start with on_
    class SomeWidget(widgets.Button):
        on_hover = traitlets.traitlets.Callable(None, allow_none=True)

    mock = unittest.mock.Mock()
    widget, rc = react.render_fixed(SomeWidget.element(on_hover=mock))
    assert widget.on_hover is mock
    # mock.assert_called()
    rc.close()


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

        use_effect(add_my_own_event_handler, [])  # only add it once
        return text

    text, rc = react.render_fixed(Test())
    # first time, it's always ok
    text.value = "hallo"
    mock.assert_called()
    mock.reset_mock()
    # second time, we executed the render loop again, did we remove the event handler?
    text.value = "ola"
    mock.assert_called()
    rc.close()


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

    test, rc = react.render_fixed(Test())
    assert set_show_other is not None
    assert test.children[0].value == 1
    set_show_other(True)
    rc.force_update()
    assert test.children[0].value == 10
    test.children[0].value = 11
    set_show_other(False)
    rc.force_update()
    assert test.children[0].value == 1
    test.children[0].value = 2
    set_show_other(True)
    rc.force_update()
    # the state should be reset, if the component was detached
    assert test.children[0].value == 10
    set_show_other(False)
    rc.force_update()
    assert test.children[0].value == 1
    rc.close()


@pytest.mark.skipif(not react.core.DEBUG, reason="only works in debug mode")
def test_exceptions():
    @react.component
    def Test():
        return w.Button()

    try:
        test, _rc = react.render_fixed(Test(non_existing_arg=1))  # type: ignore
    except TypeError as e:
        formatted = traceback.format_tb(e.__traceback__)
        assert "Test" in formatted[3]
        assert "non_existing_arg" in formatted[3]
    else:
        assert False, "no error occurred"


@pytest.mark.skipif(not react.core.DEBUG, reason="only works in debug mode")
def test_exceptions_debug_in_render_function():
    @react.component
    def Child():
        # the stacktrace should include the next line
        a = non_existing  # type: ignore # noqa
        return w.Button()

    @react.component
    def Test():
        return Child()  # but also this line, which is not an actual part of the stack trace

    try:
        test, rc = react.render_fixed(Test())  # type: ignore
    except NameError as e:
        formatted = traceback.format_tb(e.__traceback__)
        assert "Child" in formatted[3]
        assert "non_existing" in formatted[4]
    else:
        assert False, "no error occurred"


@pytest.mark.skipif(not react.core.DEBUG, reason="only works in debug mode")
def test_exceptions_debug_in_consolidate():
    set_value = None

    @react.component
    def Child():
        nonlocal set_value
        value, set_value = react.use_state("label")
        return w.Button(description=value)  # we'd like to see this line

    @react.component
    def Test():
        return Child()

    test, rc = react.render_fixed(Test())  # type: ignore
    assert set_value is not None
    try:
        set_value(1)  # type: ignore
    except Exception as e:
        formatted = traceback.format_tb(e.__traceback__)
        assert "Child" in formatted[3]
        assert "Button" in formatted[4]
    rc.close()


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

    clicker, rc = react.render_fixed(ButtonClick())
    clicker.click()
    assert clicker.description == "Hi: Clicked 1 times"
    rc.close()


def test_use_ref():
    last = None

    @react.component
    def ButtonClick(label="Hi"):
        nonlocal last
        clicks, set_clicks = react.use_state(0)
        ref = react.use_ref({"hi": 1})
        last = ref.current
        return w.Button(description=f"{label}: Clicked {clicks} times", on_click=lambda: set_clicks(clicks + 1))

    clicker, rc = react.render_fixed(ButtonClick())
    clicker.click()
    last1 = last
    clicker.click()
    assert last is last1
    rc.close()


def test_render_many_consolidate_once():
    set_value = None

    @react.component
    def Test():
        nonlocal set_value
        value, set_value = react.use_state(0)
        if value >= 5 and value < 15:  # force 10 renders
            set_value(value + 1)
        return w.IntSlider(value=value)

    mock = unittest.mock.Mock()
    slider, rc = react.render_fixed(Test())
    assert set_value is not None
    slider.observe(lambda change: mock(change.new), "value")
    set_value(4)
    mock.assert_called_once_with(4)
    set_value(5)
    assert slider.value == 15
    # even though we had many renders (from 5 to 15), we only reconsolidated once (i.e. 1 extra call)
    mock.assert_has_calls([unittest.mock.call(4), unittest.mock.call(15)])
    rc.close()


def test_recover_exception(capsys):
    set_fail = None

    @react.component
    def Test():
        nonlocal set_fail
        fail, set_fail = react.use_state(False)
        if fail:
            raise Exception("fail")
        return w.IntSlider()

    # with pytest.raises(Exception):
    slider, rc = react.render_fixed(Test())
    assert set_fail is not None
    with pytest.raises(Exception, match="fail"):
        set_fail(True)
    set_fail(False)
    rc.close()
    assert isinstance(slider, ipywidgets.IntSlider)


def test_state_get():
    set_value = None

    @react.component
    def Test():
        nonlocal set_value
        value, set_value = react.use_state(0)
        return w.IntSlider(value=value)

    slider, rc = react.render_fixed(Test())
    assert set_value is not None
    state = rc.state_get()
    assert state == {"children": {"Test/": {"state": {"0": 0}}}, "state": {}}
    set_value(42)
    assert state == {"children": {"Test/": {"state": {"0": 42}}}, "state": {}}
    assert slider.value == 42
    rc.close()

    box = widgets.VBox()
    hbox, rc = react.render(Test(), box, initial_state=state, handle_error=False)
    assert box.children[0].value == 42
    rc.close()


def test_cleanup():
    set_count = None

    @react.component
    def Test():
        nonlocal set_count
        count, set_count = react.use_state(1)
        with w.VBox() as main:
            for i in range(count):
                ButtonClicks()
        return main

    # with pytest.raises(Exception):
    box, rc = react.render_fixed(Test())
    assert set_count is not None

    buttons = box.children
    assert len(buttons) == 1
    buttons[0].click()
    assert buttons[0].description == "Clicked 1 times"

    set_count(2)
    rc.force_update()
    buttons = box.children
    assert len(buttons) == 2
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].description == "Clicked 0 times"
    buttons[1].click()
    buttons[1].click()
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].description == "Clicked 2 times"

    set_count(1)
    rc.force_update()
    buttons = box.children
    assert len(buttons) == 1
    assert buttons[0].description == "Clicked 1 times"

    set_count(2)
    rc.force_update()
    buttons = box.children
    assert len(buttons) == 2
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].description == "Clicked 0 times"
    rc.close()


# same, but to react a different component
@react.component
def ButtonClicks2():
    clicks, set_clicks = react.use_state(0)
    with w.VBox() as main:
        w.Label()
        w.Text()
        w.Button(description=f"Clicked {clicks} times", on_click=lambda: set_clicks(clicks + 1))
        w.VBox(children=[ButtonClicks3()])
        w.VBox(children=[w.Checkbox()])
    return main


@react.component
def ButtonClicks3():
    clicks, set_clicks = react.use_state(0)
    with w.VBox() as main:
        w.Button(description=f"Clicked {clicks} times", on_click=lambda: set_clicks(clicks + 1))
    return main


def test_insert_no_key():
    set_insert = None

    @react.component
    def Test():
        nonlocal set_insert
        insert, set_insert = react.use_state(False)
        with w.VBox() as main:
            ButtonClicks()
            if insert:
                ButtonClicks2()
                w.Text()
            ButtonClicks3()
        return main

    # with pytest.raises(Exception):
    box, rc = react.render_fixed(Test(), handle_error=False)
    assert set_insert is not None
    # rc.force_update()

    buttons = box.children
    assert len(buttons) == 2
    buttons[0].click()
    buttons[1].children[0].click()
    buttons[1].children[0].click()
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[0].description == "Clicked 2 times"
    rc.force_update()

    set_insert(True)
    buttons = box.children
    assert len(buttons) == 4
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[2].description == "Clicked 0 times"
    assert buttons[3].children[0].description == "Clicked 0 times"
    buttons[1].children[2].click()
    buttons[1].children[2].click()
    buttons[1].children[2].click()
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[2].description == "Clicked 3 times"
    assert buttons[3].children[0].description == "Clicked 0 times"
    rc.force_update()

    set_insert(False)
    buttons = box.children
    assert len(buttons) == 2
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[0].description == "Clicked 0 times"
    rc.force_update()

    set_insert(True)
    buttons = box.children
    assert len(buttons) == 4
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[2].description == "Clicked 0 times"
    assert buttons[3].children[0].description == "Clicked 0 times"
    rc.force_update()
    rc.close()


def test_insert_with_key():
    set_insert = None

    @react.component
    def Test():
        nonlocal set_insert
        insert, set_insert = react.use_state(False)
        with w.VBox() as main:
            ButtonClicks().key("1")  # type: ignore
            if insert:
                ButtonClicks2().key("2")  # type: ignore
            ButtonClicks3().key("3")  # type: ignore
        return main

    # with pytest.raises(Exception):
    box, rc = react.render_fixed(Test())
    assert set_insert is not None
    rc.force_update()

    buttons = box.children
    assert len(buttons) == 2
    buttons[0].click()
    buttons[1].children[0].click()
    buttons[1].children[0].click()
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[0].description == "Clicked 2 times"
    rc.force_update()

    set_insert(True)
    buttons = box.children
    assert len(buttons) == 3
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[2].description == "Clicked 0 times"
    assert buttons[2].children[0].description == "Clicked 2 times"
    buttons[1].children[2].click()
    buttons[1].children[2].click()
    buttons[1].children[2].click()
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[2].description == "Clicked 3 times"
    assert buttons[2].children[0].description == "Clicked 2 times"
    rc.force_update()

    set_insert(False)
    buttons = box.children
    assert len(buttons) == 2
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[0].description == "Clicked 2 times"
    rc.force_update()

    set_insert(True)
    buttons = box.children
    assert len(buttons) == 3
    assert buttons[0].description == "Clicked 1 times"
    assert buttons[1].children[2].description == "Clicked 0 times"
    assert buttons[2].children[0].description == "Clicked 2 times"
    rc.force_update()
    rc.close()


def test_vue_orphan_not_close():
    import ipyvue

    class MyTemplate(ipyvue.VueTemplate):
        template_file = (__file__, "test.vue")

    @react.component
    def Test():
        return MyTemplate.element()

    box, rc = react.render(Test())
    template = box.children[0].template
    rc.close()
    # make sure we can render after close (close should not close the template widget)
    box2, rc2 = react.render(Test())
    rc2.close()
    template.close()


@pytest.mark.parametrize("in_container", [False, True])
def test_switch_component(in_container):
    @react.component
    def Child1():
        with Container() as main:
            w.Button(description="1")
        return main

    @react.component
    def Child2():
        with Container() as main:
            ButtonNumber(2)
        return main

    @react.component
    def Child3():
        with Container() as main:
            ButtonNumber(3)
        return main

    set_value = None

    @react.component
    def Test():
        nonlocal set_value
        value, set_value = react.use_state(1)
        children = [None, Child1, Child2, Child3]
        component = children[value]
        assert component is not None
        if in_container:
            return Container(children=[component()])
        else:
            return component()

    box, rc = react.render(Test())

    def get_description():
        if in_container:
            button = box.children[0].children[0].children[0]
        else:
            button = box.children[0].children[0]
        return button.description

    assert get_description() == "1"
    assert set_value is not None
    # set_value(2)
    # assert get_description() == "2"
    rc.force_update()
    set_value(3)
    rc.force_update()
    assert get_description() == "3"
    set_value(1)
    rc.force_update()
    assert get_description() == "1"
    set_value(3)
    rc.force_update()
    assert get_description() == "3"
    set_value(2)
    rc.force_update()
    assert get_description() == "2"
    set_value(1)
    rc.force_update()
    assert get_description() == "1"
    rc.close()


def test_switch_simple():
    set_value = None

    @react.component
    def Test():
        nonlocal set_value
        value, set_value = react.use_state(True)
        if value:
            return Container(children=[w.Button(description="button")])
        else:
            return Container(children=[w.IntSlider(description="slider")])

    box, rc = react.render(Test())
    assert set_value is not None
    assert box.children[0].children[0].description == "button"
    rc.force_update()
    set_value(False)
    rc.force_update()
    assert box.children[0].children[0].description == "slider"
    rc.force_update()
    rc.close()


def test_switch_widget_and_component():
    set_value = None

    effect = unittest.mock.Mock()
    cleanup = unittest.mock.Mock()

    @react.component
    def Child():
        def my_effect():
            effect()
            return cleanup

        use_effect(my_effect, [])
        return w.Button(description="child")

    @react.component
    def Test():
        nonlocal set_value
        value, set_value = react.use_state(True)
        with Container() as main:
            if value:
                w.Button(description="widget")
            else:
                Child()
        return main

    box, rc = react.render_fixed(Test())
    assert set_value is not None
    assert box.children[0].description == "widget"
    rc.force_update()

    set_value(False)
    effect.assert_called_once()
    cleanup.assert_not_called()
    rc.force_update()
    effect.assert_called_once()
    cleanup.assert_not_called()
    assert box.children[0].description == "child"

    set_value(True)
    assert box.children[0].description == "widget"
    cleanup.assert_called_once()
    rc.force_update()
    cleanup.assert_called_once()

    rc.force_update()
    rc.close()


def test_switch_component_key():
    set_value = None

    effect = unittest.mock.Mock()
    cleanup = unittest.mock.Mock()

    @react.component
    def Child(value):
        def my_effect():
            effect()
            return cleanup

        use_effect(my_effect, [])
        return w.Button(description=value)

    @react.component
    def Test():
        nonlocal set_value
        value, set_value = react.use_state("1")
        with Container() as main:
            Child(value=value).key(value)
        return main

    box, rc = react.render_fixed(Test())
    assert set_value is not None
    assert box.children[0].description == "1"
    effect.assert_called_once()
    cleanup.assert_not_called()
    rc.force_update()

    set_value("2")
    assert box.children[0].description == "2"
    effect.assert_has_calls([unittest.mock.call(), unittest.mock.call()])
    cleanup.assert_called_once()
    rc.force_update()
    effect.assert_has_calls([unittest.mock.call(), unittest.mock.call()])
    cleanup.assert_called_once()

    set_value("3")
    assert box.children[0].description == "3"
    effect.assert_has_calls([unittest.mock.call(), unittest.mock.call(), unittest.mock.call()])
    cleanup.assert_has_calls([unittest.mock.call(), unittest.mock.call()])
    rc.force_update()
    effect.assert_has_calls([unittest.mock.call(), unittest.mock.call(), unittest.mock.call()])
    cleanup.assert_has_calls([unittest.mock.call(), unittest.mock.call()])

    rc.force_update()
    rc.close()
    cleanup.assert_has_calls([unittest.mock.call(), unittest.mock.call(), unittest.mock.call()])


def test_render_twice_different_element():
    set_action = None

    @react.component
    def Test():
        nonlocal set_action
        action, set_action = react.use_state(0)
        if action == 0:
            return w.Button()
        elif action == 1:
            # render float slider, and text in the same render phase
            set_action(2)
            return w.FloatSlider()
        else:
            return w.Text()

    box = react.make(Test())
    assert isinstance(box.children[0], widgets.Button)
    assert set_action is not None
    set_action(1)

    assert isinstance(box.children[0], widgets.Text)
    assert react.core._last_rc is not None
    react.core._last_rc.close()
