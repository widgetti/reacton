import datetime
import typing
from typing import Any, Dict, Sequence, Union

import ipywidgets
import ipywidgets as widgets
import ipywidgets.widgets.widget_description
import ipywidgets.widgets.widget_int

import react_ipywidgets
import react_ipywidgets as react
from react_ipywidgets.core import Element

from .utils import without_default

# def use_on_click(on_click):
#     def add_event_handler(button: widgets.Button):
#         def handler(change):
#             on_click()

#         def cleanup():
#             button.on_click(handler, remove=True)

#         button.on_click(handler)
#         return cleanup

#     react.use_side_effect(add_event_handler)


def slider_int(value=1, description="", min=0, max=100, key=None, **kwargs):
    key = key or str(value) + str(description)
    value, set_value = react.use_state(value, key)
    IntSlider(value=value, description=description, min=min, max=max, on_value=set_value, **kwargs)
    return value


def text_int(value=1, description="", key=None, **kwargs):
    key = key or str(value) + str(description)
    value, set_value = react.use_state(value, key)
    IntText(value=value, description=description, on_value=set_value, **kwargs)
    return value


def slider_float(value=1, description="", min=0, max=100, key=None, **kwargs):
    key = key or str(value) + str(description)
    value, set_value = react.use_state(value, key)
    FloatSlider(value=value, description=description, min=min, max=max, on_value=set_value, **kwargs)
    return value


def checkbox(value=True, description="", key=None, **kwargs):
    key = key or str(value) + str(description)
    value, set_value = react.use_state(value, key)
    Checkbox(value=value, description=description, on_value=set_value)
    return value


def color(value="red", description="", key=None, **kwargs):
    key = key or str(value) + str(description)
    value, set_value = react.use_state(value, key)
    ColorPicker(value=value, description=description, on_value=set_value)
    return value


def text(value="Hi there", description="", key=None, **kwargs):
    key = key or str(value) + str(description)
    value, set_value = react.use_state(value, key)
    Text(value=value, description=description, on_value=set_value)
    return value


def dropdown(value="foo", options=["foo", "bar"], description="", key=None, **kwargs):
    key = key or str(value) + str(description) + str(options)
    value, set_value = react.use_state(value, key)

    def set_index(index):
        set_value(options[index])

    Dropdown(value=value, description=description, options=options, on_index=set_index)
    return value


# @react.component
# def ButtonWithClick(on_click=None, **kwargs):
#     if on_click is not None:
#         # TODO: in react, we cannot do this conditionally, we can appearently
#         use_on_click(on_click)
#     return Button(**kwargs)


class ButtonElement(react.core.Element):
    def split_kwargs(self, kwargs: dict):

        if "on_click" in kwargs:
            kwargs = kwargs.copy()
            on_click = kwargs.pop("on_click")
            normal_kwargs, listeners = super().split_kwargs(kwargs)
            listeners["on_click"] = on_click
            return normal_kwargs, listeners
        else:
            return super().split_kwargs(kwargs)

    def handle_custom_kwargs(self, widget: ipywidgets.Widget, kwargs: dict):
        if "on_click" in kwargs:
            kwargs = kwargs.copy()
            on_click = kwargs.pop("on_click")

            def add_event_handler():
                button: widgets.Button = react.core.get_widget(self)

                def handler(change):
                    on_click()

                def cleanup():
                    button.on_click(handler, remove=True)

                button.on_click(handler)
                return cleanup

            react.use_side_effect(add_event_handler)

        super().handle_custom_kwargs(widget, kwargs)


extra_arguments = {ipywidgets.Button: [("on_click", None, typing.Callable[[], Any])]}
element_classes = {ipywidgets.Button: ButtonElement}

if __name__ == "__main__":
    from .generate import generate

    current_module = __import__(__name__)

    generate(__file__, [widgets, ipywidgets.widgets.widget_description, ipywidgets.widgets.widget_int], module_output=current_module)


def ViewcountVBox(on_view_count) -> Element[ipywidgets.widgets.widget_box.VBox]:
    """Exposes the Widget._view_count throught a VBox, which is not exposed in any widget"""
    widget_cls = ipywidgets.widgets.widget_box.VBox
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, _view_count=0, on__view_count=on_view_count)


# generated code:


def Accordion(
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    selected_index: int = 0,
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_selected_index: typing.Callable[[int], Any] = None,
) -> Element[ipywidgets.widgets.widget_selectioncontainer.Accordion]:
    """Displays children each on a separate accordion page.
    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    :param selected_index: The index of the selected page. This is either an integer selecting a particular sub-widget, or None to have no widgets selected.
    """
    kwargs: Dict[Any, Any] = without_default(Accordion, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_selectioncontainer.Accordion
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def AppLayout(
    align_items: str = None,
    box_style: str = "",
    center: Element[ipywidgets.Widget] = None,
    children: Sequence[Element[ipywidgets.Widget]] = (),
    footer: Element[ipywidgets.Widget] = None,
    grid_gap: str = None,
    header: Element[ipywidgets.Widget] = None,
    height: str = None,
    justify_content: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    left_sidebar: Element[ipywidgets.Widget] = None,
    merge: bool = True,
    pane_heights: tuple = ("1fr", "3fr", "1fr"),
    pane_widths: tuple = ("1fr", "2fr", "1fr"),
    right_sidebar: Element[ipywidgets.Widget] = None,
    width: str = None,
    on_align_items: typing.Callable[[str], Any] = None,
    on_box_style: typing.Callable[[str], Any] = None,
    on_center: typing.Callable[[Element[ipywidgets.Widget]], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_footer: typing.Callable[[Element[ipywidgets.Widget]], Any] = None,
    on_grid_gap: typing.Callable[[str], Any] = None,
    on_header: typing.Callable[[Element[ipywidgets.Widget]], Any] = None,
    on_height: typing.Callable[[str], Any] = None,
    on_justify_content: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_left_sidebar: typing.Callable[[Element[ipywidgets.Widget]], Any] = None,
    on_merge: typing.Callable[[bool], Any] = None,
    on_pane_heights: typing.Callable[[tuple], Any] = None,
    on_pane_widths: typing.Callable[[tuple], Any] = None,
    on_right_sidebar: typing.Callable[[Element[ipywidgets.Widget]], Any] = None,
    on_width: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_templates.AppLayout]:
    """Define an application like layout of widgets.

    Parameters
    ----------

    header: instance of Widget
    left_sidebar: instance of Widget
    center: instance of Widget
    right_sidebar: instance of Widget
    footer: instance of Widget
        widgets to fill the positions in the layout

    merge: bool
        flag to say whether the empty positions should be automatically merged

    pane_widths: list of numbers/strings
        the fraction of the total layout width each of the central panes should occupy
        (left_sidebar,
        center, right_sidebar)

    pane_heights: list of numbers/strings
        the fraction of the width the vertical space that the panes should occupy
         (left_sidebar, center, right_sidebar)

    grid_gap : str
        CSS attribute used to set the gap between the grid cells

    justify_content : str, in ['flex-start', 'flex-end', 'center', 'space-between', 'space-around']
        CSS attribute used to align widgets vertically

    align_items : str, in ['top', 'bottom', 'center', 'flex-start', 'flex-end', 'baseline', 'stretch']
        CSS attribute used to align widgets horizontally

    width : str
    height : str
        width and height

    Examples
    --------


    :param align_items: The align-items CSS attribute.
    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    :param grid_gap: The grid-gap CSS attribute.
    :param height: The width CSS attribute.
    :param justify_content: The justify-content CSS attribute.
    :param width: The width CSS attribute.
    """
    kwargs: Dict[Any, Any] = without_default(AppLayout, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_templates.AppLayout
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Audio(
    autoplay: bool = True,
    controls: bool = True,
    format: str = "mp3",
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    loop: bool = True,
    value: bytes = b"",
    on_autoplay: typing.Callable[[bool], Any] = None,
    on_controls: typing.Callable[[bool], Any] = None,
    on_format: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_loop: typing.Callable[[bool], Any] = None,
    on_value: typing.Callable[[bytes], Any] = None,
) -> Element[ipywidgets.widgets.widget_media.Audio]:
    """Displays a audio as a widget.

    The `value` of this widget accepts a byte string.  The byte string is the
    raw audio data that you want the browser to display.  You can explicitly
    define the format of the byte string using the `format` trait (which
    defaults to "mp3").

    If you pass `"url"` to the `"format"` trait, `value` will be interpreted
    as a URL as bytes encoded in UTF-8.

    :param autoplay: When true, the audio starts when it's displayed
    :param controls: Specifies that audio controls should be displayed (such as a play/pause button etc)
    :param format: The format of the audio.
    :param loop: When true, the audio will start from the beginning after finishing
    :param value: The media data as a byte string.
    """
    kwargs: Dict[Any, Any] = without_default(Audio, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_media.Audio
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def BoundedFloatText(
    continuous_update: bool = False,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: float = 100.0,
    min: float = 0.0,
    step: float = None,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: float = 0.0,
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_step: typing.Callable[[float], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[float], Any] = None,
) -> Element[ipywidgets.widgets.widget_float.BoundedFloatText]:
    """Displays a float value within a textbox. Value must be within the range specified.

    For a textbox in which the value doesn't need to be within a specific range, use FloatText.

    Parameters
    ----------
    value : float
        value displayed
    min : float
        minimal value of the range of possible values displayed
    max : float
        maximal value of the range of possible values displayed
    step : float
        step of the increment (if None, any step is allowed)
    description : str
        description displayed next to the textbox

    :param continuous_update: Update the value as the user types. If False, update on submission, e.g., pressing Enter or navigating away.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param max: Max value
    :param min: Min value
    :param step: Minimum step to increment the value
    :param style: Styling customizations
    :param value: Float value
    """
    kwargs: Dict[Any, Any] = without_default(BoundedFloatText, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_float.BoundedFloatText
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def BoundedIntText(
    continuous_update: bool = False,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: int = 100,
    min: int = 0,
    step: int = 1,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: int = 0,
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[int], Any] = None,
    on_min: typing.Callable[[int], Any] = None,
    on_step: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[int], Any] = None,
) -> Element[ipywidgets.widgets.widget_int.BoundedIntText]:
    """Textbox widget that represents an integer bounded from above and below.

    :param continuous_update: Update the value as the user types. If False, update on submission, e.g., pressing Enter or navigating away.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param max: Max value
    :param min: Min value
    :param step: Minimum step to increment the value
    :param style: Styling customizations
    :param value: Int value
    """
    kwargs: Dict[Any, Any] = without_default(BoundedIntText, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int.BoundedIntText
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Box(
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
) -> Element[ipywidgets.widgets.widget_box.Box]:
    """Displays multiple widgets in a group.

    The widgets are laid out horizontally.

    Parameters
    ----------
    children: iterable of Widget instances
        list of widgets to display

    box_style: str
        one of 'success', 'info', 'warning' or 'danger', or ''.
        Applies a predefined style to the box. Defaults to '',
        which applies no pre-defined style.

    Examples
    --------
    >>> import ipywidgets as widgets
    >>> title_widget = widgets.HTML('<em>Box Example</em>')
    >>> slider = widgets.IntSlider()
    >>> widgets.Box([title_widget, slider])

    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    """
    kwargs: Dict[Any, Any] = without_default(Box, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_box.Box
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Button(
    button_style: str = "",
    description: str = "",
    disabled: bool = False,
    icon: str = "",
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_button.ButtonStyle]] = {},
    tooltip: str = "",
    on_button_style: typing.Callable[[str], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_icon: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_button.ButtonStyle]]], Any] = None,
    on_tooltip: typing.Callable[[str], Any] = None,
    on_click: typing.Callable[[], typing.Any] = None,
) -> Element[ipywidgets.widgets.widget_button.Button]:
    """Button widget.

    This widget has an `on_click` method that allows you to listen for the
    user clicking on the button.  The click event itself is stateless.

    Parameters
    ----------
    description: str
       description displayed next to the button
    tooltip: str
       tooltip caption of the toggle button
    icon: str
       font-awesome icon name
    disabled: bool
       whether user interaction is enabled

    :param button_style: Use a predefined styling for the button.
    :param description: Button label.
    :param disabled: Enable or disable user changes.
    :param icon: Font-awesome icon name, without the 'fa-' prefix.
    :param tooltip: Tooltip caption of the button.
    """
    kwargs: Dict[Any, Any] = without_default(Button, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = ButtonStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_button.Button
    comp = react.core.ComponentWidget(widget=widget_cls)
    return ButtonElement(comp, **kwargs)


###
def ButtonStyle(
    button_color: str = None,
    font_weight: str = "",
    on_button_color: typing.Callable[[str], Any] = None,
    on_font_weight: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_button.ButtonStyle]:
    """Button style widget.
    :param button_color: Color of the button
    :param font_weight: Button text font weight.
    """
    kwargs: Dict[Any, Any] = without_default(ButtonStyle, locals())

    widget_cls = ipywidgets.widgets.widget_button.ButtonStyle
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Checkbox(
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    indent: bool = True,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: bool = False,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_indent: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[bool], Any] = None,
) -> Element[ipywidgets.widgets.widget_bool.Checkbox]:
    """Displays a boolean `value` in the form of a checkbox.

    Parameters
    ----------
    value : {True,False}
        value of the checkbox: True-checked, False-unchecked
    description : str
            description displayed next to the checkbox
    indent : {True,False}
        indent the control to align with other controls with a description. The style.description_width attribute controls this width for consistence with other controls.

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes.
    :param indent: Indent the control to align with other controls with a description.
    :param style: Styling customizations
    :param value: Bool value
    """
    kwargs: Dict[Any, Any] = without_default(Checkbox, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_bool.Checkbox
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def ColorPicker(
    concise: bool = False,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: str = "black",
    on_concise: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_color.ColorPicker]:
    """
    :param concise: Display short version with just a color selector.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes.
    :param style: Styling customizations
    :param value: The color value.
    """
    kwargs: Dict[Any, Any] = without_default(ColorPicker, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_color.ColorPicker
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Combobox(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    ensure_option: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    options: Sequence[str] = (),
    placeholder: str = "\u200b",
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: str = "",
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_ensure_option: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_options: typing.Callable[[Sequence[str]], Any] = None,
    on_placeholder: typing.Callable[[str], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_string.Combobox]:
    """Single line textbox widget with a dropdown and autocompletion.

    :param continuous_update: Update the value as the user types. If False, update on submission, e.g., pressing Enter or navigating away.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param ensure_option: If set, ensure value is in options. Implies continuous_update=False.
    :param options: Dropdown options for the combobox
    :param placeholder: Placeholder text to display when nothing has been typed
    :param style: Styling customizations
    :param value: String value
    """
    kwargs: Dict[Any, Any] = without_default(Combobox, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_string.Combobox
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Controller(
    axes: Sequence[Element[ipywidgets.widgets.widget_controller.Axis]] = (),
    buttons: Sequence[Element[ipywidgets.widgets.widget_controller.Button]] = (),
    connected: bool = False,
    index: int = 0,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    mapping: str = "",
    name: str = "",
    timestamp: float = 0.0,
    on_axes: typing.Callable[[Sequence[Element[ipywidgets.widgets.widget_controller.Axis]]], Any] = None,
    on_buttons: typing.Callable[[Sequence[Element[ipywidgets.widgets.widget_controller.Button]]], Any] = None,
    on_connected: typing.Callable[[bool], Any] = None,
    on_index: typing.Callable[[int], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_mapping: typing.Callable[[str], Any] = None,
    on_name: typing.Callable[[str], Any] = None,
    on_timestamp: typing.Callable[[float], Any] = None,
) -> Element[ipywidgets.widgets.widget_controller.Controller]:
    """Represents a game controller.
    :param axes: The axes on the gamepad.
    :param buttons: The buttons on the gamepad.
    :param connected: Whether the gamepad is connected.
    :param index: The id number of the controller.
    :param mapping: The name of the control mapping.
    :param name: The name of the controller.
    :param timestamp: The last time the data from this gamepad was updated.
    """
    kwargs: Dict[Any, Any] = without_default(Controller, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_controller.Controller
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def CoreWidget() -> Element[ipywidgets.widgets.widget_core.CoreWidget]:
    """ """
    kwargs: Dict[Any, Any] = without_default(CoreWidget, locals())

    widget_cls = ipywidgets.widgets.widget_core.CoreWidget
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def DOMWidget(
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
) -> Element[ipywidgets.widgets.domwidget.DOMWidget]:
    """Widget that can be inserted into the DOM"""
    kwargs: Dict[Any, Any] = without_default(DOMWidget, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.domwidget.DOMWidget
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def DatePicker(
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: datetime.date = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[datetime.date], Any] = None,
) -> Element[ipywidgets.widgets.widget_date.DatePicker]:
    """
    Display a widget for picking dates.

    Parameters
    ----------

    value: datetime.date
        The current value of the widget.

    disabled: bool
        Whether to disable user changes.

    Examples
    --------

    >>> import datetime
    >>> import ipywidgets as widgets
    >>> date_pick = widgets.DatePicker()
    >>> date_pick.value = datetime.date(2019, 7, 9)

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes.
    :param style: Styling customizations
    """
    kwargs: Dict[Any, Any] = without_default(DatePicker, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_date.DatePicker
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Dropdown(
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    index: int = None,
    label: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    options: Any = (),
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: Any = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_index: typing.Callable[[int], Any] = None,
    on_label: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_options: typing.Callable[[Any], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[Any], Any] = None,
) -> Element[ipywidgets.widgets.widget_selection.Dropdown]:
    """Allows you to select a single item from a dropdown.

    Parameters
    ----------
    options: list
        The options for the dropdown. This can either be a list of values, e.g.
        ``['Galileo', 'Brahe', 'Hubble']`` or ``[0, 1, 2]``, or a list of
        (label, value) pairs, e.g.
        ``[('Galileo', 0), ('Brahe', 1), ('Hubble', 2)]``.

    index: int
        The index of the current selection.

    value: any
        The value of the current selection. When programmatically setting the
        value, a reverse lookup is performed among the options to check that
        the value is valid. The reverse lookup uses the equality operator by
        default, but another predicate may be provided via the ``equals``
        keyword argument. For example, when dealing with numpy arrays, one may
        set ``equals=np.array_equal``.

    label: str
        The label corresponding to the selected value.

    disabled: bool
        Whether to disable user changes.

    description: str
        Label for this input group. This should be a string
        describing the widget.

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param index: Selected index
    :param label: Selected label
    :param options: Iterable of values, (label, value) pairs, or a mapping of {label: value} pairs that the user can select.

        The labels are the strings that will be displayed in the UI, representing the
        actual Python choices, and should be unique.

    :param style: Styling customizations
    :param value: Selected value
    """
    kwargs: Dict[Any, Any] = without_default(Dropdown, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_selection.Dropdown
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def FileUpload(
    accept: str = "",
    button_style: str = "",
    data: list = [],
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    error: str = "",
    icon: str = "upload",
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    metadata: list = [],
    multiple: bool = False,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_button.ButtonStyle]] = {},
    value: dict = {},
    on_accept: typing.Callable[[str], Any] = None,
    on_button_style: typing.Callable[[str], Any] = None,
    on_data: typing.Callable[[list], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_error: typing.Callable[[str], Any] = None,
    on_icon: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_metadata: typing.Callable[[list], Any] = None,
    on_multiple: typing.Callable[[bool], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_button.ButtonStyle]]], Any] = None,
    on_value: typing.Callable[[dict], Any] = None,
) -> Element[ipywidgets.widgets.widget_upload.FileUpload]:
    """
    Upload file(s) from browser to Python kernel as bytes

    :param accept: File types to accept, empty string for all
    :param button_style: Use a predefined styling for the button.
    :param data: List of file content (bytes)
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable button
    :param error: Error message
    :param icon: Font-awesome icon name, without the 'fa-' prefix.
    :param metadata: List of file metadata
    :param multiple: If True, allow for multiple files upload
    """
    kwargs: Dict[Any, Any] = without_default(FileUpload, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = ButtonStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_upload.FileUpload
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def FloatLogSlider(
    base: float = 10.0,
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: float = 4.0,
    min: float = 0.0,
    orientation: str = "horizontal",
    readout: bool = True,
    readout_format: str = ".3g",
    step: float = 0.1,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]] = {},
    value: float = 1.0,
    on_base: typing.Callable[[float], Any] = None,
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_readout: typing.Callable[[bool], Any] = None,
    on_readout_format: typing.Callable[[str], Any] = None,
    on_step: typing.Callable[[float], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]]], Any] = None,
    on_value: typing.Callable[[float], Any] = None,
) -> Element[ipywidgets.widgets.widget_float.FloatLogSlider]:
    """Slider/trackbar of logarithmic floating values with the specified range.

    Parameters
    ----------
    value : float
        position of the slider
    base : float
        base of the logarithmic scale. Default is 10
    min : float
        minimal position of the slider in log scale, i.e., actual minimum is base ** min
    max : float
        maximal position of the slider in log scale, i.e., actual maximum is base ** max
    step : float
        step of the trackbar, denotes steps for the exponent, not the actual value
    description : str
        name of the slider
    orientation : {'horizontal', 'vertical'}
        default is 'horizontal', orientation of the slider
    readout : {True, False}
        default is True, display the current value of the slider next to it
    readout_format : str
        default is '.3g', specifier for the format function used to represent
        slider value for human consumption, modeled after Python 3's format
        specification mini-language (PEP 3101).

    :param base: Base for the logarithm
    :param continuous_update: Update the value of the widget as the user is holding the slider.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param max: Max value for the exponent
    :param min: Min value for the exponent
    :param orientation: Vertical or horizontal.
    :param readout: Display the current value of the slider next to it.
    :param readout_format: Format for the readout
    :param step: Minimum step in the exponent to increment the value
    :param value: Float value
    """
    kwargs: Dict[Any, Any] = without_default(FloatLogSlider, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = SliderStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_float.FloatLogSlider
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def FloatProgress(
    bar_style: str = "",
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: float = 100.0,
    min: float = 0.0,
    orientation: str = "horizontal",
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.ProgressStyle]] = {},
    value: float = 0.0,
    on_bar_style: typing.Callable[[str], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.ProgressStyle]]], Any] = None,
    on_value: typing.Callable[[float], Any] = None,
) -> Element[ipywidgets.widgets.widget_float.FloatProgress]:
    """Displays a progress bar.

    Parameters
    -----------
    value : float
        position within the range of the progress bar
    min : float
        minimal position of the slider
    max : float
        maximal position of the slider
    description : str
        name of the progress bar
    orientation : {'horizontal', 'vertical'}
        default is 'horizontal', orientation of the progress bar
    bar_style: {'success', 'info', 'warning', 'danger', ''}
        color of the progress bar, default is '' (blue)
        colors are: 'success'-green, 'info'-light blue, 'warning'-orange, 'danger'-red

    :param bar_style: Use a predefined styling for the progess bar.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param max: Max value
    :param min: Min value
    :param orientation: Vertical or horizontal.
    :param value: Float value
    """
    kwargs: Dict[Any, Any] = without_default(FloatProgress, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = ProgressStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_float.FloatProgress
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def FloatRangeSlider(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: float = 100.0,
    min: float = 0.0,
    orientation: str = "horizontal",
    readout: bool = True,
    readout_format: str = ".2f",
    step: float = 0.1,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]] = {},
    value: tuple = (0.0, 1.0),
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_readout: typing.Callable[[bool], Any] = None,
    on_readout_format: typing.Callable[[str], Any] = None,
    on_step: typing.Callable[[float], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]]], Any] = None,
    on_value: typing.Callable[[tuple], Any] = None,
) -> Element[ipywidgets.widgets.widget_float.FloatRangeSlider]:
    """Slider/trackbar that represents a pair of floats bounded by minimum and maximum value.

    Parameters
    ----------
    value : float tuple
        range of the slider displayed
    min : float
        minimal position of the slider
    max : float
        maximal position of the slider
    step : float
        step of the trackbar
    description : str
        name of the slider
    orientation : {'horizontal', 'vertical'}
        default is 'horizontal'
    readout : {True, False}
        default is True, display the current value of the slider next to it
    readout_format : str
        default is '.2f', specifier for the format function used to represent
        slider value for human consumption, modeled after Python 3's format
        specification mini-language (PEP 3101).

    :param continuous_update: Update the value of the widget as the user is sliding the slider.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param max: Max value
    :param min: Min value
    :param orientation: Vertical or horizontal.
    :param readout: Display the current value of the slider next to it.
    :param readout_format: Format for the readout
    :param step: Minimum step to increment the value
    :param value: Tuple of (lower, upper) bounds
    """
    kwargs: Dict[Any, Any] = without_default(FloatRangeSlider, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = SliderStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_float.FloatRangeSlider
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def FloatSlider(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: float = 100.0,
    min: float = 0.0,
    orientation: str = "horizontal",
    readout: bool = True,
    readout_format: str = ".2f",
    step: float = 0.1,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]] = {},
    value: float = 0.0,
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_readout: typing.Callable[[bool], Any] = None,
    on_readout_format: typing.Callable[[str], Any] = None,
    on_step: typing.Callable[[float], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]]], Any] = None,
    on_value: typing.Callable[[float], Any] = None,
) -> Element[ipywidgets.widgets.widget_float.FloatSlider]:
    """Slider/trackbar of floating values with the specified range.

    Parameters
    ----------
    value : float
        position of the slider
    min : float
        minimal position of the slider
    max : float
        maximal position of the slider
    step : float
        step of the trackbar
    description : str
        name of the slider
    orientation : {'horizontal', 'vertical'}
        default is 'horizontal', orientation of the slider
    readout : {True, False}
        default is True, display the current value of the slider next to it
    readout_format : str
        default is '.2f', specifier for the format function used to represent
        slider value for human consumption, modeled after Python 3's format
        specification mini-language (PEP 3101).

    :param continuous_update: Update the value of the widget as the user is holding the slider.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param max: Max value
    :param min: Min value
    :param orientation: Vertical or horizontal.
    :param readout: Display the current value of the slider next to it.
    :param readout_format: Format for the readout
    :param step: Minimum step to increment the value
    :param value: Float value
    """
    kwargs: Dict[Any, Any] = without_default(FloatSlider, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = SliderStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_float.FloatSlider
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def FloatText(
    continuous_update: bool = False,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    step: float = None,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: float = 0.0,
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_step: typing.Callable[[float], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[float], Any] = None,
) -> Element[ipywidgets.widgets.widget_float.FloatText]:
    """Displays a float value within a textbox. For a textbox in
    which the value must be within a specific range, use BoundedFloatText.

    Parameters
    ----------
    value : float
        value displayed
    step : float
        step of the increment (if None, any step is allowed)
    description : str
        description displayed next to the text box

    :param continuous_update: Update the value as the user types. If False, update on submission, e.g., pressing Enter or navigating away.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param step: Minimum step to increment the value
    :param style: Styling customizations
    :param value: Float value
    """
    kwargs: Dict[Any, Any] = without_default(FloatText, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_float.FloatText
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def GridBox(
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
) -> Element[ipywidgets.widgets.widget_box.GridBox]:
    """Displays multiple widgets in rows and columns using the grid box model.

    Parameters
    ----------
    {box_params}

    Examples
    --------
    >>> import ipywidgets as widgets
    >>> title_widget = widgets.HTML('<em>Grid Box Example</em>')
    >>> slider = widgets.IntSlider()
    >>> button1 = widgets.Button(description='1')
    >>> button2 = widgets.Button(description='2')
    >>> # Create a grid with two columns, splitting space equally
    >>> layout = widgets.Layout(grid_template_columns='1fr 1fr')
    >>> widgets.GridBox([title_widget, slider, button1, button2], layout=layout)

    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    """
    kwargs: Dict[Any, Any] = without_default(GridBox, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_box.GridBox
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def GridspecLayout(
    align_items: str = None,
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    grid_gap: str = None,
    height: str = None,
    justify_content: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    n_columns: int = 0,
    n_rows: int = 0,
    width: str = None,
    on_align_items: typing.Callable[[str], Any] = None,
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_grid_gap: typing.Callable[[str], Any] = None,
    on_height: typing.Callable[[str], Any] = None,
    on_justify_content: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_n_columns: typing.Callable[[int], Any] = None,
    on_n_rows: typing.Callable[[int], Any] = None,
    on_width: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_templates.GridspecLayout]:
    """Define a N by M grid layout

    Parameters
    ----------

    n_rows : int
        number of rows in the grid

    n_columns : int
        number of columns in the grid

    grid_gap : str
        CSS attribute used to set the gap between the grid cells

    justify_content : str, in ['flex-start', 'flex-end', 'center', 'space-between', 'space-around']
        CSS attribute used to align widgets vertically

    align_items : str, in ['top', 'bottom', 'center', 'flex-start', 'flex-end', 'baseline', 'stretch']
        CSS attribute used to align widgets horizontally

    width : str
    height : str
        width and height

    Examples
    --------

    >>> from ipywidgets import GridspecLayout, Button, Layout
    >>> layout = GridspecLayout(n_rows=4, n_columns=2, height='200px')
    >>> layout[:3, 0] = Button(layout=Layout(height='auto', width='auto'))
    >>> layout[1:, 1] = Button(layout=Layout(height='auto', width='auto'))
    >>> layout[-1, 0] = Button(layout=Layout(height='auto', width='auto'))
    >>> layout[0, 1] = Button(layout=Layout(height='auto', width='auto'))
    >>> layout

    :param align_items: The align-items CSS attribute.
    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    :param grid_gap: The grid-gap CSS attribute.
    :param height: The width CSS attribute.
    :param justify_content: The justify-content CSS attribute.
    :param width: The width CSS attribute.
    """
    kwargs: Dict[Any, Any] = without_default(GridspecLayout, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_templates.GridspecLayout
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def HBox(
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
) -> Element[ipywidgets.widgets.widget_box.HBox]:
    """Displays multiple widgets horizontally using the flexible box model.

    Parameters
    ----------
    children: iterable of Widget instances
        list of widgets to display

    box_style: str
        one of 'success', 'info', 'warning' or 'danger', or ''.
        Applies a predefined style to the box. Defaults to '',
        which applies no pre-defined style.

    Examples
    --------
    >>> import ipywidgets as widgets
    >>> title_widget = widgets.HTML('<em>Horizontal Box Example</em>')
    >>> slider = widgets.IntSlider()
    >>> widgets.HBox([title_widget, slider])

    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    """
    kwargs: Dict[Any, Any] = without_default(HBox, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_box.HBox
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def HTML(
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    placeholder: str = "\u200b",
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: str = "",
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_placeholder: typing.Callable[[str], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_string.HTML]:
    """Renders the string `value` as HTML.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param placeholder: Placeholder text to display when nothing has been typed
    :param style: Styling customizations
    :param value: String value
    """
    kwargs: Dict[Any, Any] = without_default(HTML, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_string.HTML
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def HTMLMath(
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    placeholder: str = "\u200b",
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: str = "",
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_placeholder: typing.Callable[[str], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_string.HTMLMath]:
    """Renders the string `value` as HTML, and render mathematics.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param placeholder: Placeholder text to display when nothing has been typed
    :param style: Styling customizations
    :param value: String value
    """
    kwargs: Dict[Any, Any] = without_default(HTMLMath, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_string.HTMLMath
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Image(
    format: str = "png",
    height: str = "",
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    value: bytes = b"",
    width: str = "",
    on_format: typing.Callable[[str], Any] = None,
    on_height: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_value: typing.Callable[[bytes], Any] = None,
    on_width: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_media.Image]:
    """Displays an image as a widget.

    The `value` of this widget accepts a byte string.  The byte string is the
    raw image data that you want the browser to display.  You can explicitly
    define the format of the byte string using the `format` trait (which
    defaults to "png").

    If you pass `"url"` to the `"format"` trait, `value` will be interpreted
    as a URL as bytes encoded in UTF-8.

    :param format: The format of the image.
    :param height: Height of the image in pixels. Use layout.height for styling the widget.
    :param value: The media data as a byte string.
    :param width: Width of the image in pixels. Use layout.width for styling the widget.
    """
    kwargs: Dict[Any, Any] = without_default(Image, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_media.Image
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def IntProgress(
    bar_style: str = "",
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: int = 100,
    min: int = 0,
    orientation: str = "horizontal",
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.ProgressStyle]] = {},
    value: int = 0,
    on_bar_style: typing.Callable[[str], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[int], Any] = None,
    on_min: typing.Callable[[int], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.ProgressStyle]]], Any] = None,
    on_value: typing.Callable[[int], Any] = None,
) -> Element[ipywidgets.widgets.widget_int.IntProgress]:
    """Progress bar that represents an integer bounded from above and below.

    :param bar_style: Use a predefined styling for the progess bar.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param max: Max value
    :param min: Min value
    :param orientation: Vertical or horizontal.
    :param value: Int value
    """
    kwargs: Dict[Any, Any] = without_default(IntProgress, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = ProgressStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int.IntProgress
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def IntRangeSlider(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: int = 100,
    min: int = 0,
    orientation: str = "horizontal",
    readout: bool = True,
    readout_format: str = "d",
    step: int = 1,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]] = {},
    value: tuple = (0, 1),
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[int], Any] = None,
    on_min: typing.Callable[[int], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_readout: typing.Callable[[bool], Any] = None,
    on_readout_format: typing.Callable[[str], Any] = None,
    on_step: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]]], Any] = None,
    on_value: typing.Callable[[tuple], Any] = None,
) -> Element[ipywidgets.widgets.widget_int.IntRangeSlider]:
    """Slider/trackbar that represents a pair of ints bounded by minimum and maximum value.

    Parameters
    ----------
    value : int tuple
        The pair (`lower`, `upper`) of integers
    min : int
        The lowest allowed value for `lower`
    max : int
        The highest allowed value for `upper`

    :param continuous_update: Update the value of the widget as the user is sliding the slider.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param max: Max value
    :param min: Min value
    :param orientation: Vertical or horizontal.
    :param readout: Display the current value of the slider next to it.
    :param readout_format: Format for the readout
    :param step: Minimum step that the value can take
    :param style: Slider style customizations.
    :param value: Tuple of (lower, upper) bounds
    """
    kwargs: Dict[Any, Any] = without_default(IntRangeSlider, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = SliderStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int.IntRangeSlider
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def IntSlider(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: int = 100,
    min: int = 0,
    orientation: str = "horizontal",
    readout: bool = True,
    readout_format: str = "d",
    step: int = 1,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]] = {},
    value: int = 0,
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[int], Any] = None,
    on_min: typing.Callable[[int], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_readout: typing.Callable[[bool], Any] = None,
    on_readout_format: typing.Callable[[str], Any] = None,
    on_step: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_int.SliderStyle]]], Any] = None,
    on_value: typing.Callable[[int], Any] = None,
) -> Element[ipywidgets.widgets.widget_int.IntSlider]:
    """Slider widget that represents an integer bounded from above and below.

    :param continuous_update: Update the value of the widget as the user is holding the slider.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param max: Max value
    :param min: Min value
    :param orientation: Vertical or horizontal.
    :param readout: Display the current value of the slider next to it.
    :param readout_format: Format for the readout
    :param step: Minimum step to increment the value
    :param value: Int value
    """
    kwargs: Dict[Any, Any] = without_default(IntSlider, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = SliderStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int.IntSlider
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def IntText(
    continuous_update: bool = False,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    step: int = 1,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: int = 0,
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_step: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[int], Any] = None,
) -> Element[ipywidgets.widgets.widget_int.IntText]:
    """Textbox widget that represents an integer.
    :param continuous_update: Update the value as the user types. If False, update on submission, e.g., pressing Enter or navigating away.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param step: Minimum step to increment the value
    :param style: Styling customizations
    :param value: Int value
    """
    kwargs: Dict[Any, Any] = without_default(IntText, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int.IntText
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Label(
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    placeholder: str = "\u200b",
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: str = "",
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_placeholder: typing.Callable[[str], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_string.Label]:
    """Label widget.

    It also renders math inside the string `value` as Latex (requires $ $ or
    $$ $$ and similar latex tags).

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param placeholder: Placeholder text to display when nothing has been typed
    :param style: Styling customizations
    :param value: String value
    """
    kwargs: Dict[Any, Any] = without_default(Label, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_string.Label
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Layout(
    align_content: str = None,
    align_items: str = None,
    align_self: str = None,
    border: str = None,
    bottom: str = None,
    display: str = None,
    flex: str = None,
    flex_flow: str = None,
    grid_area: str = None,
    grid_auto_columns: str = None,
    grid_auto_flow: str = None,
    grid_auto_rows: str = None,
    grid_column: str = None,
    grid_gap: str = None,
    grid_row: str = None,
    grid_template_areas: str = None,
    grid_template_columns: str = None,
    grid_template_rows: str = None,
    height: str = None,
    justify_content: str = None,
    justify_items: str = None,
    left: str = None,
    margin: str = None,
    max_height: str = None,
    max_width: str = None,
    min_height: str = None,
    min_width: str = None,
    object_fit: str = None,
    object_position: str = None,
    order: str = None,
    overflow: str = None,
    overflow_x: str = None,
    overflow_y: str = None,
    padding: str = None,
    right: str = None,
    top: str = None,
    visibility: str = None,
    width: str = None,
    on_align_content: typing.Callable[[str], Any] = None,
    on_align_items: typing.Callable[[str], Any] = None,
    on_align_self: typing.Callable[[str], Any] = None,
    on_border: typing.Callable[[str], Any] = None,
    on_bottom: typing.Callable[[str], Any] = None,
    on_display: typing.Callable[[str], Any] = None,
    on_flex: typing.Callable[[str], Any] = None,
    on_flex_flow: typing.Callable[[str], Any] = None,
    on_grid_area: typing.Callable[[str], Any] = None,
    on_grid_auto_columns: typing.Callable[[str], Any] = None,
    on_grid_auto_flow: typing.Callable[[str], Any] = None,
    on_grid_auto_rows: typing.Callable[[str], Any] = None,
    on_grid_column: typing.Callable[[str], Any] = None,
    on_grid_gap: typing.Callable[[str], Any] = None,
    on_grid_row: typing.Callable[[str], Any] = None,
    on_grid_template_areas: typing.Callable[[str], Any] = None,
    on_grid_template_columns: typing.Callable[[str], Any] = None,
    on_grid_template_rows: typing.Callable[[str], Any] = None,
    on_height: typing.Callable[[str], Any] = None,
    on_justify_content: typing.Callable[[str], Any] = None,
    on_justify_items: typing.Callable[[str], Any] = None,
    on_left: typing.Callable[[str], Any] = None,
    on_margin: typing.Callable[[str], Any] = None,
    on_max_height: typing.Callable[[str], Any] = None,
    on_max_width: typing.Callable[[str], Any] = None,
    on_min_height: typing.Callable[[str], Any] = None,
    on_min_width: typing.Callable[[str], Any] = None,
    on_object_fit: typing.Callable[[str], Any] = None,
    on_object_position: typing.Callable[[str], Any] = None,
    on_order: typing.Callable[[str], Any] = None,
    on_overflow: typing.Callable[[str], Any] = None,
    on_overflow_x: typing.Callable[[str], Any] = None,
    on_overflow_y: typing.Callable[[str], Any] = None,
    on_padding: typing.Callable[[str], Any] = None,
    on_right: typing.Callable[[str], Any] = None,
    on_top: typing.Callable[[str], Any] = None,
    on_visibility: typing.Callable[[str], Any] = None,
    on_width: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_layout.Layout]:
    """Layout specification

    Defines a layout that can be expressed using CSS.  Supports a subset of
    https://developer.mozilla.org/en-US/docs/Web/CSS/Reference

    When a property is also accessible via a shorthand property, we only
    expose the shorthand.

    For example:
    - ``flex-grow``, ``flex-shrink`` and ``flex-basis`` are bound to ``flex``.
    - ``flex-wrap`` and ``flex-direction`` are bound to ``flex-flow``.
    - ``margin-[top/bottom/left/right]`` values are bound to ``margin``, etc.

    :param align_content: The align-content CSS attribute.
    :param align_items: The align-items CSS attribute.
    :param align_self: The align-self CSS attribute.
    :param border: The border CSS attribute.
    :param bottom: The bottom CSS attribute.
    :param display: The display CSS attribute.
    :param flex: The flex CSS attribute.
    :param flex_flow: The flex-flow CSS attribute.
    :param grid_area: The grid-area CSS attribute.
    :param grid_auto_columns: The grid-auto-columns CSS attribute.
    :param grid_auto_flow: The grid-auto-flow CSS attribute.
    :param grid_auto_rows: The grid-auto-rows CSS attribute.
    :param grid_column: The grid-column CSS attribute.
    :param grid_gap: The grid-gap CSS attribute.
    :param grid_row: The grid-row CSS attribute.
    :param grid_template_areas: The grid-template-areas CSS attribute.
    :param grid_template_columns: The grid-template-columns CSS attribute.
    :param grid_template_rows: The grid-template-rows CSS attribute.
    :param height: The height CSS attribute.
    :param justify_content: The justify-content CSS attribute.
    :param justify_items: The justify-items CSS attribute.
    :param left: The left CSS attribute.
    :param margin: The margin CSS attribute.
    :param max_height: The max-height CSS attribute.
    :param max_width: The max-width CSS attribute.
    :param min_height: The min-height CSS attribute.
    :param min_width: The min-width CSS attribute.
    :param object_fit: The object-fit CSS attribute.
    :param object_position: The object-position CSS attribute.
    :param order: The order CSS attribute.
    :param overflow: The overflow CSS attribute.
    :param overflow_x: The overflow-x CSS attribute (deprecated).
    :param overflow_y: The overflow-y CSS attribute (deprecated).
    :param padding: The padding CSS attribute.
    :param right: The right CSS attribute.
    :param top: The top CSS attribute.
    :param visibility: The visibility CSS attribute.
    :param width: The width CSS attribute.
    """
    kwargs: Dict[Any, Any] = without_default(Layout, locals())

    widget_cls = ipywidgets.widgets.widget_layout.Layout
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Output(
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    msg_id: str = "",
    outputs: Sequence[dict] = (),
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_msg_id: typing.Callable[[str], Any] = None,
    on_outputs: typing.Callable[[Sequence[dict]], Any] = None,
) -> Element[ipywidgets.widgets.widget_output.Output]:
    """Widget used as a context manager to display output.

    This widget can capture and display stdout, stderr, and rich output.  To use
    it, create an instance of it and display it.

    You can then use the widget as a context manager: any output produced while in the
    context will be captured and displayed in the widget instead of the standard output
    area.

    You can also use the .capture() method to decorate a function or a method. Any output
    produced by the function will then go to the output widget. This is useful for
    debugging widget callbacks, for example.

    Example::
        import ipywidgets as widgets
        from IPython.display import display
        out = widgets.Output()
        display(out)

        print('prints to output area')

        with out:
            print('prints to output widget')

        @out.capture()
        def func():
            print('prints to output widget')

    :param msg_id: Parent message id of messages to capture
    :param outputs: The output messages synced from the frontend.
    """
    kwargs: Dict[Any, Any] = without_default(Output, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_output.Output
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Password(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    placeholder: str = "\u200b",
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: str = "",
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_placeholder: typing.Callable[[str], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_string.Password]:
    """Single line textbox widget.
    :param continuous_update: Update the value as the user types. If False, update on submission, e.g., pressing Enter or navigating away.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param placeholder: Placeholder text to display when nothing has been typed
    :param style: Styling customizations
    :param value: String value
    """
    kwargs: Dict[Any, Any] = without_default(Password, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_string.Password
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Play(
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    interval: int = 100,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: int = 100,
    min: int = 0,
    show_repeat: bool = True,
    step: int = 1,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: int = 0,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_interval: typing.Callable[[int], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[int], Any] = None,
    on_min: typing.Callable[[int], Any] = None,
    on_show_repeat: typing.Callable[[bool], Any] = None,
    on_step: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[int], Any] = None,
) -> Element[ipywidgets.widgets.widget_int.Play]:
    """Play/repeat buttons to step through values automatically, and optionally loop.

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param interval: The maximum value for the play control.
    :param max: Max value
    :param min: Min value
    :param show_repeat: Show the repeat toggle button in the widget.
    :param step: Increment step
    :param style: Styling customizations
    :param value: Int value
    """
    kwargs: Dict[Any, Any] = without_default(Play, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int.Play
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def RadioButtons(
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    index: int = None,
    label: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    options: Any = (),
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: Any = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_index: typing.Callable[[int], Any] = None,
    on_label: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_options: typing.Callable[[Any], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[Any], Any] = None,
) -> Element[ipywidgets.widgets.widget_selection.RadioButtons]:
    """Group of radio buttons that represent an enumeration.

    Only one radio button can be toggled at any point in time.

    Parameters
    ----------
    options: list
        The options for the dropdown. This can either be a list of values, e.g.
        ``['Galileo', 'Brahe', 'Hubble']`` or ``[0, 1, 2]``, or a list of
        (label, value) pairs, e.g.
        ``[('Galileo', 0), ('Brahe', 1), ('Hubble', 2)]``.

    index: int
        The index of the current selection.

    value: any
        The value of the current selection. When programmatically setting the
        value, a reverse lookup is performed among the options to check that
        the value is valid. The reverse lookup uses the equality operator by
        default, but another predicate may be provided via the ``equals``
        keyword argument. For example, when dealing with numpy arrays, one may
        set ``equals=np.array_equal``.

    label: str
        The label corresponding to the selected value.

    disabled: bool
        Whether to disable user changes.

    description: str
        Label for this input group. This should be a string
        describing the widget.

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param index: Selected index
    :param label: Selected label
    :param options: Iterable of values, (label, value) pairs, or a mapping of {label: value} pairs that the user can select.

        The labels are the strings that will be displayed in the UI, representing the
        actual Python choices, and should be unique.

    :param style: Styling customizations
    :param value: Selected value
    """
    kwargs: Dict[Any, Any] = without_default(RadioButtons, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_selection.RadioButtons
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Select(
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    index: int = None,
    label: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    options: Any = (),
    rows: int = 5,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: Any = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_index: typing.Callable[[int], Any] = None,
    on_label: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_options: typing.Callable[[Any], Any] = None,
    on_rows: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[Any], Any] = None,
) -> Element[ipywidgets.widgets.widget_selection.Select]:
    """
    Listbox that only allows one item to be selected at any given time.

    Parameters
    ----------
    options: list
        The options for the dropdown. This can either be a list of values, e.g.
        ``['Galileo', 'Brahe', 'Hubble']`` or ``[0, 1, 2]``, or a list of
        (label, value) pairs, e.g.
        ``[('Galileo', 0), ('Brahe', 1), ('Hubble', 2)]``.

    index: int
        The index of the current selection.

    value: any
        The value of the current selection. When programmatically setting the
        value, a reverse lookup is performed among the options to check that
        the value is valid. The reverse lookup uses the equality operator by
        default, but another predicate may be provided via the ``equals``
        keyword argument. For example, when dealing with numpy arrays, one may
        set ``equals=np.array_equal``.

    label: str
        The label corresponding to the selected value.

    disabled: bool
        Whether to disable user changes.

    description: str
        Label for this input group. This should be a string
        describing the widget.

    rows: int
        The number of rows to display in the widget.

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param index: Selected index
    :param label: Selected label
    :param options: Iterable of values, (label, value) pairs, or a mapping of {label: value} pairs that the user can select.

        The labels are the strings that will be displayed in the UI, representing the
        actual Python choices, and should be unique.

    :param rows: The number of rows to display.
    :param style: Styling customizations
    :param value: Selected value
    """
    kwargs: Dict[Any, Any] = without_default(Select, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_selection.Select
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def SelectMultiple(
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    index: Sequence[int] = (),
    label: Sequence[str] = (),
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    options: Any = (),
    rows: int = 5,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: Sequence[Any] = (),
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_index: typing.Callable[[Sequence[int]], Any] = None,
    on_label: typing.Callable[[Sequence[str]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_options: typing.Callable[[Any], Any] = None,
    on_rows: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[Sequence[Any]], Any] = None,
) -> Element[ipywidgets.widgets.widget_selection.SelectMultiple]:
    """
    Listbox that allows many items to be selected at any given time.

    The ``value``, ``label`` and ``index`` attributes are all iterables.

    Parameters
    ----------
    options: dict or list
        The options for the dropdown. This can either be a list of values, e.g.
        ``['Galileo', 'Brahe', 'Hubble']`` or ``[0, 1, 2]``, a list of
        (label, value) pairs, e.g.
        ``[('Galileo', 0), ('Brahe', 1), ('Hubble', 2)]``,
        or a dictionary mapping the labels to the values, e.g. ``{'Galileo': 0,
        'Brahe': 1, 'Hubble': 2}``. The labels are the strings that will be
        displayed in the UI, representing the actual Python choices, and should
        be unique. If this is a dictionary, the order in which they are
        displayed is not guaranteed.

    index: iterable of int
        The indices of the options that are selected.

    value: iterable
        The values that are selected. When programmatically setting the
        value, a reverse lookup is performed among the options to check that
        the value is valid. The reverse lookup uses the equality operator by
        default, but another predicate may be provided via the ``equals``
        keyword argument. For example, when dealing with numpy arrays, one may
        set ``equals=np.array_equal``.

    label: iterable of str
        The labels corresponding to the selected value.

    disabled: bool
        Whether to disable user changes.

    description: str
        Label for this input group. This should be a string
        describing the widget.

    rows: int
        The number of rows to display in the widget.

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param index: Selected indices
    :param label: Selected labels
    :param options: Iterable of values, (label, value) pairs, or a mapping of {label: value} pairs that the user can select.

        The labels are the strings that will be displayed in the UI, representing the
        actual Python choices, and should be unique.

    :param rows: The number of rows to display.
    :param style: Styling customizations
    :param value: Selected values
    """
    kwargs: Dict[Any, Any] = without_default(SelectMultiple, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_selection.SelectMultiple
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def SelectionRangeSlider(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    index: tuple = (0, 0),
    label: tuple = (),
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    options: Any = (),
    orientation: str = "horizontal",
    readout: bool = True,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: tuple = (),
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_index: typing.Callable[[tuple], Any] = None,
    on_label: typing.Callable[[tuple], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_options: typing.Callable[[Any], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_readout: typing.Callable[[bool], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[tuple], Any] = None,
) -> Element[ipywidgets.widgets.widget_selection.SelectionRangeSlider]:
    """
    Slider to select multiple contiguous items from a list.

    The index, value, and label attributes contain the start and end of
    the selection range, not all items in the range.

    Parameters
    ----------
    options: dict or list
        The options for the dropdown. This can either be a list of values, e.g.
        ``['Galileo', 'Brahe', 'Hubble']`` or ``[0, 1, 2]``, a list of
        (label, value) pairs, e.g.
        ``[('Galileo', 0), ('Brahe', 1), ('Hubble', 2)]``,
        or a dictionary mapping the labels to the values, e.g. ``{'Galileo': 0,
        'Brahe': 1, 'Hubble': 2}``. The labels are the strings that will be
        displayed in the UI, representing the actual Python choices, and should
        be unique. If this is a dictionary, the order in which they are
        displayed is not guaranteed.

    index: iterable of int
        The indices of the options that are selected.

    value: iterable
        The values that are selected. When programmatically setting the
        value, a reverse lookup is performed among the options to check that
        the value is valid. The reverse lookup uses the equality operator by
        default, but another predicate may be provided via the ``equals``
        keyword argument. For example, when dealing with numpy arrays, one may
        set ``equals=np.array_equal``.

    label: iterable of str
        The labels corresponding to the selected value.

    disabled: bool
        Whether to disable user changes.

    description: str
        Label for this input group. This should be a string
        describing the widget.

    orientation: str
        Either ``'horizontal'`` or ``'vertical'``. Defaults to ``horizontal``.

    readout: bool
        Display the current label next to the slider. Defaults to ``True``.

    continuous_update: bool
        If ``True``, update the value of the widget continuously as the user
        holds the slider. Otherwise, the model is only updated after the
        user has released the slider. Defaults to ``True``.

    :param continuous_update: Update the value of the widget as the user is holding the slider.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param index: Min and max selected indices
    :param label: Min and max selected labels
    :param options: Iterable of values, (label, value) pairs, or a mapping of {label: value} pairs that the user can select.

        The labels are the strings that will be displayed in the UI, representing the
        actual Python choices, and should be unique.

    :param orientation: Vertical or horizontal.
    :param readout: Display the current selected label next to the slider
    :param style: Styling customizations
    :param value: Min and max selected values
    """
    kwargs: Dict[Any, Any] = without_default(SelectionRangeSlider, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_selection.SelectionRangeSlider
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def SelectionSlider(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    index: int = 0,
    label: str = "",
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    options: Any = (),
    orientation: str = "horizontal",
    readout: bool = True,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: Any = None,
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_index: typing.Callable[[int], Any] = None,
    on_label: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_options: typing.Callable[[Any], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_readout: typing.Callable[[bool], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[Any], Any] = None,
) -> Element[ipywidgets.widgets.widget_selection.SelectionSlider]:
    """
    Slider to select a single item from a list or dictionary.

    Parameters
    ----------
    options: list
        The options for the dropdown. This can either be a list of values, e.g.
        ``['Galileo', 'Brahe', 'Hubble']`` or ``[0, 1, 2]``, or a list of
        (label, value) pairs, e.g.
        ``[('Galileo', 0), ('Brahe', 1), ('Hubble', 2)]``.

    index: int
        The index of the current selection.

    value: any
        The value of the current selection. When programmatically setting the
        value, a reverse lookup is performed among the options to check that
        the value is valid. The reverse lookup uses the equality operator by
        default, but another predicate may be provided via the ``equals``
        keyword argument. For example, when dealing with numpy arrays, one may
        set ``equals=np.array_equal``.

    label: str
        The label corresponding to the selected value.

    disabled: bool
        Whether to disable user changes.

    description: str
        Label for this input group. This should be a string
        describing the widget.

    orientation: str
        Either ``'horizontal'`` or ``'vertical'``. Defaults to ``horizontal``.

    readout: bool
        Display the current label next to the slider. Defaults to ``True``.

    continuous_update: bool
        If ``True``, update the value of the widget continuously as the user
        holds the slider. Otherwise, the model is only updated after the
        user has released the slider. Defaults to ``True``.

    :param continuous_update: Update the value of the widget as the user is holding the slider.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param index: Selected index
    :param label: Selected label
    :param options: Iterable of values, (label, value) pairs, or a mapping of {label: value} pairs that the user can select.

        The labels are the strings that will be displayed in the UI, representing the
        actual Python choices, and should be unique.

    :param orientation: Vertical or horizontal.
    :param readout: Display the current selected label next to the slider
    :param style: Styling customizations
    :param value: Selected value
    """
    kwargs: Dict[Any, Any] = without_default(SelectionSlider, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_selection.SelectionSlider
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def SliderStyle(
    description_width: str = "",
    handle_color: str = None,
    on_description_width: typing.Callable[[str], Any] = None,
    on_handle_color: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_int.SliderStyle]:
    """Button style widget.
    :param description_width: Width of the description to the side of the control.
    :param handle_color: Color of the slider handle.
    """
    kwargs: Dict[Any, Any] = without_default(SliderStyle, locals())

    widget_cls = ipywidgets.widgets.widget_int.SliderStyle
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Style() -> Element[ipywidgets.widgets.widget_style.Style]:
    """Style specification"""
    kwargs: Dict[Any, Any] = without_default(Style, locals())

    widget_cls = ipywidgets.widgets.widget_style.Style
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Tab(
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    selected_index: int = 0,
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_selected_index: typing.Callable[[int], Any] = None,
) -> Element[ipywidgets.widgets.widget_selectioncontainer.Tab]:
    """Displays children each on a separate accordion tab.
    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    :param selected_index: The index of the selected page. This is either an integer selecting a particular sub-widget, or None to have no widgets selected.
    """
    kwargs: Dict[Any, Any] = without_default(Tab, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_selectioncontainer.Tab
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Text(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    placeholder: str = "\u200b",
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: str = "",
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_placeholder: typing.Callable[[str], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_string.Text]:
    """Single line textbox widget.
    :param continuous_update: Update the value as the user types. If False, update on submission, e.g., pressing Enter or navigating away.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param placeholder: Placeholder text to display when nothing has been typed
    :param style: Styling customizations
    :param value: String value
    """
    kwargs: Dict[Any, Any] = without_default(Text, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_string.Text
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Textarea(
    continuous_update: bool = True,
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    placeholder: str = "\u200b",
    rows: int = None,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: str = "",
    on_continuous_update: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_placeholder: typing.Callable[[str], Any] = None,
    on_rows: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_string.Textarea]:
    """Multiline text area widget.
    :param continuous_update: Update the value as the user types. If False, update on submission, e.g., pressing Enter or navigating away.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param placeholder: Placeholder text to display when nothing has been typed
    :param rows: The number of rows to display.
    :param style: Styling customizations
    :param value: String value
    """
    kwargs: Dict[Any, Any] = without_default(Textarea, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_string.Textarea
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def ToggleButton(
    button_style: str = "",
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    icon: str = "",
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    tooltip: str = "",
    value: bool = False,
    on_button_style: typing.Callable[[str], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_icon: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_tooltip: typing.Callable[[str], Any] = None,
    on_value: typing.Callable[[bool], Any] = None,
) -> Element[ipywidgets.widgets.widget_bool.ToggleButton]:
    """Displays a boolean `value` in the form of a toggle button.

    Parameters
    ----------
    value : {True,False}
        value of the toggle button: True-pressed, False-unpressed
    description : str
              description displayed next to the button
    tooltip: str
        tooltip caption of the toggle button
    icon: str
        font-awesome icon name

    :param button_style: Use a predefined styling for the button.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes.
    :param icon: Font-awesome icon.
    :param style: Styling customizations
    :param tooltip: Tooltip caption of the toggle button.
    :param value: Bool value
    """
    kwargs: Dict[Any, Any] = without_default(ToggleButton, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_bool.ToggleButton
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def ToggleButtons(
    button_style: str = "",
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    icons: Sequence[str] = (),
    index: int = None,
    label: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    options: Any = (),
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_selection.ToggleButtonsStyle]] = {},
    tooltips: Sequence[str] = (),
    value: Any = None,
    on_button_style: typing.Callable[[str], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_icons: typing.Callable[[Sequence[str]], Any] = None,
    on_index: typing.Callable[[int], Any] = None,
    on_label: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_options: typing.Callable[[Any], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_selection.ToggleButtonsStyle]]], Any] = None,
    on_tooltips: typing.Callable[[Sequence[str]], Any] = None,
    on_value: typing.Callable[[Any], Any] = None,
) -> Element[ipywidgets.widgets.widget_selection.ToggleButtons]:
    """Group of toggle buttons that represent an enumeration.

    Only one toggle button can be toggled at any point in time.

    Parameters
    ----------
    options: list
        The options for the dropdown. This can either be a list of values, e.g.
        ``['Galileo', 'Brahe', 'Hubble']`` or ``[0, 1, 2]``, or a list of
        (label, value) pairs, e.g.
        ``[('Galileo', 0), ('Brahe', 1), ('Hubble', 2)]``.

    index: int
        The index of the current selection.

    value: any
        The value of the current selection. When programmatically setting the
        value, a reverse lookup is performed among the options to check that
        the value is valid. The reverse lookup uses the equality operator by
        default, but another predicate may be provided via the ``equals``
        keyword argument. For example, when dealing with numpy arrays, one may
        set ``equals=np.array_equal``.

    label: str
        The label corresponding to the selected value.

    disabled: bool
        Whether to disable user changes.

    description: str
        Label for this input group. This should be a string
        describing the widget.

    tooltips: list
        Tooltip for each button. If specified, must be the
        same length as `options`.

    icons: list
        Icons to show on the buttons. This must be the name
        of a font-awesome icon. See `http://fontawesome.io/icons/`
        for a list of icons.

    button_style: str
        One of 'primary', 'success', 'info', 'warning' or
        'danger'. Applies a predefined style to every button.

    style: ToggleButtonsStyle
        Style parameters for the buttons.

    :param button_style: Use a predefined styling for the buttons.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes
    :param icons: Icons names for each button (FontAwesome names without the fa- prefix).
    :param index: Selected index
    :param label: Selected label
    :param options: Iterable of values, (label, value) pairs, or a mapping of {label: value} pairs that the user can select.

        The labels are the strings that will be displayed in the UI, representing the
        actual Python choices, and should be unique.

    :param tooltips: Tooltips for each button.
    :param value: Selected value
    """
    kwargs: Dict[Any, Any] = without_default(ToggleButtons, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = ToggleButtonsStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_selection.ToggleButtons
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def ToggleButtonsStyle(
    button_width: str = "",
    description_width: str = "",
    font_weight: str = "",
    on_button_width: typing.Callable[[str], Any] = None,
    on_description_width: typing.Callable[[str], Any] = None,
    on_font_weight: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_selection.ToggleButtonsStyle]:
    """Button style widget.

    Parameters
    ----------
    button_width: str
        The width of each button. This should be a valid CSS
        width, e.g. '10px' or '5em'.

    font_weight: str
        The text font weight of each button, This should be a valid CSS font
        weight unit, for example 'bold' or '600'

    :param button_width: The width of each button.
    :param description_width: Width of the description to the side of the control.
    :param font_weight: Text font weight of each button.
    """
    kwargs: Dict[Any, Any] = without_default(ToggleButtonsStyle, locals())

    widget_cls = ipywidgets.widgets.widget_selection.ToggleButtonsStyle
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def TwoByTwoLayout(
    align_items: str = None,
    bottom_left: Element[ipywidgets.Widget] = None,
    bottom_right: Element[ipywidgets.Widget] = None,
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    grid_gap: str = None,
    height: str = None,
    justify_content: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    merge: bool = True,
    top_left: Element[ipywidgets.Widget] = None,
    top_right: Element[ipywidgets.Widget] = None,
    width: str = None,
    on_align_items: typing.Callable[[str], Any] = None,
    on_bottom_left: typing.Callable[[Element[ipywidgets.Widget]], Any] = None,
    on_bottom_right: typing.Callable[[Element[ipywidgets.Widget]], Any] = None,
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_grid_gap: typing.Callable[[str], Any] = None,
    on_height: typing.Callable[[str], Any] = None,
    on_justify_content: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_merge: typing.Callable[[bool], Any] = None,
    on_top_left: typing.Callable[[Element[ipywidgets.Widget]], Any] = None,
    on_top_right: typing.Callable[[Element[ipywidgets.Widget]], Any] = None,
    on_width: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_templates.TwoByTwoLayout]:
    """Define a layout with 2x2 regular grid.

    Parameters
    ----------

    top_left: instance of Widget
    top_right: instance of Widget
    bottom_left: instance of Widget
    bottom_right: instance of Widget
        widgets to fill the positions in the layout

    merge: bool
        flag to say whether the empty positions should be automatically merged

    grid_gap : str
        CSS attribute used to set the gap between the grid cells

    justify_content : str, in ['flex-start', 'flex-end', 'center', 'space-between', 'space-around']
        CSS attribute used to align widgets vertically

    align_items : str, in ['top', 'bottom', 'center', 'flex-start', 'flex-end', 'baseline', 'stretch']
        CSS attribute used to align widgets horizontally

    width : str
    height : str
        width and height

    Examples
    --------

    >>> from ipywidgets import TwoByTwoLayout, Button
    >>> TwoByTwoLayout(top_left=Button(description="Top left"),
    ...                top_right=Button(description="Top right"),
    ...                bottom_left=Button(description="Bottom left"),
    ...                bottom_right=Button(description="Bottom right"))


    :param align_items: The align-items CSS attribute.
    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    :param grid_gap: The grid-gap CSS attribute.
    :param height: The width CSS attribute.
    :param justify_content: The justify-content CSS attribute.
    :param width: The width CSS attribute.
    """
    kwargs: Dict[Any, Any] = without_default(TwoByTwoLayout, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_templates.TwoByTwoLayout
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def VBox(
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
) -> Element[ipywidgets.widgets.widget_box.VBox]:
    """Displays multiple widgets vertically using the flexible box model.

    Parameters
    ----------
    children: iterable of Widget instances
        list of widgets to display

    box_style: str
        one of 'success', 'info', 'warning' or 'danger', or ''.
        Applies a predefined style to the box. Defaults to '',
        which applies no pre-defined style.

    Examples
    --------
    >>> import ipywidgets as widgets
    >>> title_widget = widgets.HTML('<em>Vertical Box Example</em>')
    >>> slider = widgets.IntSlider()
    >>> widgets.VBox([title_widget, slider])

    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    """
    kwargs: Dict[Any, Any] = without_default(VBox, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_box.VBox
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Valid(
    description: str = "",
    description_tooltip: str = None,
    disabled: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    readout: str = "Invalid",
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: bool = False,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_disabled: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_readout: typing.Callable[[str], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[bool], Any] = None,
) -> Element[ipywidgets.widgets.widget_bool.Valid]:
    """Displays a boolean `value` in the form of a green check (True / valid)
    or a red cross (False / invalid).

    Parameters
    ----------
    value: {True,False}
        value of the Valid widget

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param disabled: Enable or disable user changes.
    :param readout: Message displayed when the value is False
    :param style: Styling customizations
    :param value: Bool value
    """
    kwargs: Dict[Any, Any] = without_default(Valid, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_bool.Valid
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def ValueWidget(value: Any = None, on_value: typing.Callable[[Any], Any] = None) -> Element[ipywidgets.widgets.valuewidget.ValueWidget]:
    """Widget that can be used for the input of an interactive function
    :param value: The value of the widget.
    """
    kwargs: Dict[Any, Any] = without_default(ValueWidget, locals())

    widget_cls = ipywidgets.widgets.valuewidget.ValueWidget
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def Video(
    autoplay: bool = True,
    controls: bool = True,
    format: str = "mp4",
    height: str = "",
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    loop: bool = True,
    value: bytes = b"",
    width: str = "",
    on_autoplay: typing.Callable[[bool], Any] = None,
    on_controls: typing.Callable[[bool], Any] = None,
    on_format: typing.Callable[[str], Any] = None,
    on_height: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_loop: typing.Callable[[bool], Any] = None,
    on_value: typing.Callable[[bytes], Any] = None,
    on_width: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_media.Video]:
    """Displays a video as a widget.

    The `value` of this widget accepts a byte string.  The byte string is the
    raw video data that you want the browser to display.  You can explicitly
    define the format of the byte string using the `format` trait (which
    defaults to "mp4").

    If you pass `"url"` to the `"format"` trait, `value` will be interpreted
    as a URL as bytes encoded in UTF-8.

    :param autoplay: When true, the video starts when it's displayed
    :param controls: Specifies that video controls should be displayed (such as a play/pause button etc)
    :param format: The format of the video.
    :param height: Height of the video in pixels.
    :param loop: When true, the video will start from the beginning after finishing
    :param value: The media data as a byte string.
    :param width: Width of the video in pixels.
    """
    kwargs: Dict[Any, Any] = without_default(Video, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.widget_media.Video
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def interactive(
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
) -> Element[ipywidgets.widgets.interaction.interactive]:
    """
    A VBox container containing a group of interactive widgets tied to a
    function.

    Parameters
    ----------
    __interact_f : function
        The function to which the interactive widgets are tied. The `**kwargs`
        should match the function signature.
    __options : dict
        A dict of options. Currently, the only supported keys are
        ``"manual"`` and ``"manual_name"``.
    **kwargs : various, optional
        An interactive widget is created for each keyword argument that is a
        valid widget abbreviation.

    Note that the first two parameters intentionally start with a double
    underscore to avoid being mixed up with keyword arguments passed by
    ``**kwargs``.

    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    """
    kwargs: Dict[Any, Any] = without_default(interactive, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.interaction.interactive
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def DescriptionStyle(
    description_width: str = "", on_description_width: typing.Callable[[str], Any] = None
) -> Element[ipywidgets.widgets.widget_description.DescriptionStyle]:
    """Description style widget.
    :param description_width: Width of the description to the side of the control.
    """
    kwargs: Dict[Any, Any] = without_default(DescriptionStyle, locals())

    widget_cls = ipywidgets.widgets.widget_description.DescriptionStyle
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def DescriptionWidget(
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
) -> Element[ipywidgets.widgets.widget_description.DescriptionWidget]:
    """Widget that has a description label to the side.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param style: Styling customizations
    """
    kwargs: Dict[Any, Any] = without_default(DescriptionWidget, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_description.DescriptionWidget
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def ProgressStyle(
    bar_color: str = None,
    description_width: str = "",
    on_bar_color: typing.Callable[[str], Any] = None,
    on_description_width: typing.Callable[[str], Any] = None,
) -> Element[ipywidgets.widgets.widget_int.ProgressStyle]:
    """Button style widget.
    :param bar_color: Color of the progress bar.
    :param description_width: Width of the description to the side of the control.
    """
    kwargs: Dict[Any, Any] = without_default(ProgressStyle, locals())

    widget_cls = ipywidgets.widgets.widget_int.ProgressStyle
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def _BoundedInt(
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: int = 100,
    min: int = 0,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: int = 0,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[int], Any] = None,
    on_min: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[int], Any] = None,
) -> Element[ipywidgets.widgets.widget_int._BoundedInt]:
    """Base class for widgets that represent an integer bounded from above and below.

    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param max: Max value
    :param min: Min value
    :param style: Styling customizations
    :param value: Int value
    """
    kwargs: Dict[Any, Any] = without_default(_BoundedInt, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int._BoundedInt
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def _BoundedIntRange(
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    max: int = 100,
    min: int = 0,
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: tuple = (0, 1),
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_max: typing.Callable[[int], Any] = None,
    on_min: typing.Callable[[int], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[tuple], Any] = None,
) -> Element[ipywidgets.widgets.widget_int._BoundedIntRange]:
    """
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param max: Max value
    :param min: Min value
    :param style: Styling customizations
    :param value: Tuple of (lower, upper) bounds
    """
    kwargs: Dict[Any, Any] = without_default(_BoundedIntRange, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int._BoundedIntRange
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def _Int(
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: int = 0,
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[int], Any] = None,
) -> Element[ipywidgets.widgets.widget_int._Int]:
    """Base class for widgets that represent an integer.
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param style: Styling customizations
    :param value: Int value
    """
    kwargs: Dict[Any, Any] = without_default(_Int, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int._Int
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)


###
def _IntRange(
    description: str = "",
    description_tooltip: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    style: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]] = {},
    value: tuple = (0, 1),
    on_description: typing.Callable[[str], Any] = None,
    on_description_tooltip: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_style: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_description.DescriptionStyle]]], Any] = None,
    on_value: typing.Callable[[tuple], Any] = None,
) -> Element[ipywidgets.widgets.widget_int._IntRange]:
    """
    :param description: Description of the control.
    :param description_tooltip: Tooltip for the description (defaults to description).
    :param style: Styling customizations
    :param value: Tuple of (lower, upper) bounds
    """
    kwargs: Dict[Any, Any] = without_default(_IntRange, locals())
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    if isinstance(kwargs.get("style"), dict):
        kwargs["style"] = DescriptionStyle(**kwargs["style"])
    widget_cls = ipywidgets.widgets.widget_int._IntRange
    comp = react.core.ComponentWidget(widget=widget_cls)
    return Element(comp, **kwargs)
