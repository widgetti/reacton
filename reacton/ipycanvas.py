import typing
from typing import Any, Dict, Union

import ipycanvas
import ipywidgets

import reacton
from reacton.core import Element

from . import ipywidgets as w
from .utils import implements

if __name__ == "__main__":

    from .generate import generate

    generate(__file__, [ipycanvas])


# generated code:


def _Canvas(
    direction: str = "inherit",
    fill_style: typing.Union[str, Element[ipycanvas.canvas._CanvasGradient], Element[ipycanvas.canvas.Pattern]] = "black",
    filter: str = "none",
    font: str = "12px serif",
    global_alpha: float = 1.0,
    global_composite_operation: str = "source-over",
    height: int = 500,
    image_data: bytes = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    line_cap: str = "butt",
    line_dash_offset: float = 0.0,
    line_join: str = "miter",
    line_width: float = 1.0,
    miter_limit: float = 10.0,
    shadow_blur: float = 0.0,
    shadow_color: str = "rgba(0, 0, 0, 0)",
    shadow_offset_x: float = 0.0,
    shadow_offset_y: float = 0.0,
    stroke_style: typing.Union[str, Element[ipycanvas.canvas._CanvasGradient], Element[ipycanvas.canvas.Pattern]] = "black",
    sync_image_data: bool = False,
    text_align: str = "start",
    text_baseline: str = "alphabetic",
    width: int = 700,
    on_direction: typing.Callable[[str], Any] = None,
    on_fill_style: typing.Callable[[typing.Union[str, Element[ipycanvas.canvas._CanvasGradient], Element[ipycanvas.canvas.Pattern]]], Any] = None,
    on_filter: typing.Callable[[str], Any] = None,
    on_font: typing.Callable[[str], Any] = None,
    on_global_alpha: typing.Callable[[float], Any] = None,
    on_global_composite_operation: typing.Callable[[str], Any] = None,
    on_height: typing.Callable[[int], Any] = None,
    on_image_data: typing.Callable[[bytes], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_line_cap: typing.Callable[[str], Any] = None,
    on_line_dash_offset: typing.Callable[[float], Any] = None,
    on_line_join: typing.Callable[[str], Any] = None,
    on_line_width: typing.Callable[[float], Any] = None,
    on_miter_limit: typing.Callable[[float], Any] = None,
    on_shadow_blur: typing.Callable[[float], Any] = None,
    on_shadow_color: typing.Callable[[str], Any] = None,
    on_shadow_offset_x: typing.Callable[[float], Any] = None,
    on_shadow_offset_y: typing.Callable[[float], Any] = None,
    on_stroke_style: typing.Callable[[typing.Union[str, Element[ipycanvas.canvas._CanvasGradient], Element[ipycanvas.canvas.Pattern]]], Any] = None,
    on_sync_image_data: typing.Callable[[bool], Any] = None,
    on_text_align: typing.Callable[[str], Any] = None,
    on_text_baseline: typing.Callable[[str], Any] = None,
    on_width: typing.Callable[[int], Any] = None,
) -> Element[ipycanvas.canvas.Canvas]:
    """Create a Canvas widget.

    Args:
        width (int): The width (in pixels) of the canvas
        height (int): The height (in pixels) of the canvas


    """
    ...


@implements(_Canvas)
def Canvas(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = ipycanvas.canvas.Canvas
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Canvas


def _MultiCanvas(
    height: int = 500,
    image_data: bytes = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    sync_image_data: bool = False,
    width: int = 700,
    on_height: typing.Callable[[int], Any] = None,
    on_image_data: typing.Callable[[bytes], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_sync_image_data: typing.Callable[[bool], Any] = None,
    on_width: typing.Callable[[int], Any] = None,
) -> Element[ipycanvas.canvas.MultiCanvas]:
    """Create a MultiCanvas widget with n_canvases Canvas widgets.

    Args:
        n_canvases (int): The number of canvases to create
        width (int): The width (in pixels) of the canvases
        height (int): The height (in pixels) of the canvases


    """
    ...


@implements(_MultiCanvas)
def MultiCanvas(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = ipycanvas.canvas.MultiCanvas
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _MultiCanvas


def _MultiRoughCanvas(
    height: int = 500,
    image_data: bytes = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    sync_image_data: bool = False,
    width: int = 700,
    on_height: typing.Callable[[int], Any] = None,
    on_image_data: typing.Callable[[bytes], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_sync_image_data: typing.Callable[[bool], Any] = None,
    on_width: typing.Callable[[int], Any] = None,
) -> Element[ipycanvas.canvas.MultiRoughCanvas]:
    """Create a MultiRoughCanvas widget with n_canvases RoughCanvas widgets.

    Args:
        n_canvases (int): The number of rough canvases to create
        width (int): The width (in pixels) of the canvases
        height (int): The height (in pixels) of the canvases


    """
    ...


@implements(_MultiRoughCanvas)
def MultiRoughCanvas(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = ipycanvas.canvas.MultiRoughCanvas
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _MultiRoughCanvas


def _Path2D(value: str = "", on_value: typing.Callable[[str], Any] = None) -> Element[ipycanvas.canvas.Path2D]:
    """Create a Path2D.

    Args:
        value (str): The path value, e.g. "M10 10 h 80 v 80 h -80 Z"


    """
    ...


@implements(_Path2D)
def Path2D(**kwargs):

    widget_cls = ipycanvas.canvas.Path2D
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Path2D


def _RoughCanvas(
    bowing: float = 1,
    direction: str = "inherit",
    fill_style: typing.Union[str, Element[ipycanvas.canvas._CanvasGradient], Element[ipycanvas.canvas.Pattern]] = "black",
    filter: str = "none",
    font: str = "12px serif",
    global_alpha: float = 1.0,
    global_composite_operation: str = "source-over",
    height: int = 500,
    image_data: bytes = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    line_cap: str = "butt",
    line_dash_offset: float = 0.0,
    line_join: str = "miter",
    line_width: float = 1.0,
    miter_limit: float = 10.0,
    rough_fill_style: str = "hachure",
    roughness: float = 1,
    shadow_blur: float = 0.0,
    shadow_color: str = "rgba(0, 0, 0, 0)",
    shadow_offset_x: float = 0.0,
    shadow_offset_y: float = 0.0,
    stroke_style: typing.Union[str, Element[ipycanvas.canvas._CanvasGradient], Element[ipycanvas.canvas.Pattern]] = "black",
    sync_image_data: bool = False,
    text_align: str = "start",
    text_baseline: str = "alphabetic",
    width: int = 700,
    on_bowing: typing.Callable[[float], Any] = None,
    on_direction: typing.Callable[[str], Any] = None,
    on_fill_style: typing.Callable[[typing.Union[str, Element[ipycanvas.canvas._CanvasGradient], Element[ipycanvas.canvas.Pattern]]], Any] = None,
    on_filter: typing.Callable[[str], Any] = None,
    on_font: typing.Callable[[str], Any] = None,
    on_global_alpha: typing.Callable[[float], Any] = None,
    on_global_composite_operation: typing.Callable[[str], Any] = None,
    on_height: typing.Callable[[int], Any] = None,
    on_image_data: typing.Callable[[bytes], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_line_cap: typing.Callable[[str], Any] = None,
    on_line_dash_offset: typing.Callable[[float], Any] = None,
    on_line_join: typing.Callable[[str], Any] = None,
    on_line_width: typing.Callable[[float], Any] = None,
    on_miter_limit: typing.Callable[[float], Any] = None,
    on_rough_fill_style: typing.Callable[[str], Any] = None,
    on_roughness: typing.Callable[[float], Any] = None,
    on_shadow_blur: typing.Callable[[float], Any] = None,
    on_shadow_color: typing.Callable[[str], Any] = None,
    on_shadow_offset_x: typing.Callable[[float], Any] = None,
    on_shadow_offset_y: typing.Callable[[float], Any] = None,
    on_stroke_style: typing.Callable[[typing.Union[str, Element[ipycanvas.canvas._CanvasGradient], Element[ipycanvas.canvas.Pattern]]], Any] = None,
    on_sync_image_data: typing.Callable[[bool], Any] = None,
    on_text_align: typing.Callable[[str], Any] = None,
    on_text_baseline: typing.Callable[[str], Any] = None,
    on_width: typing.Callable[[int], Any] = None,
) -> Element[ipycanvas.canvas.RoughCanvas]:
    """Create a RoughCanvas widget. It gives a hand-drawn-like style to your drawings.

    Args:
        width (int): The width (in pixels) of the canvas
        height (int): The height (in pixels) of the canvas


    """
    ...


@implements(_RoughCanvas)
def RoughCanvas(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = ipycanvas.canvas.RoughCanvas
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _RoughCanvas
