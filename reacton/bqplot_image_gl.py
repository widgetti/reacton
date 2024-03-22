import typing
from typing import Any, Dict, Union

import bqplot_image_gl
import ipywidgets
import numpy as np
from numpy import ndarray

import reacton
from reacton.core import ContainerAdder, Element, _get_render_context

from .utils import implements


class FigureElement(Element[bqplot_image_gl.ImageGL]):
    def __enter__(self):
        rc = _get_render_context()
        ca = ContainerAdder[bqplot_image_gl.ImageGL](self, "marks")
        rc.container_adders.append(ca)
        return self


if __name__ == "__main__":

    import reacton.generate as generate

    class CodeGen(generate.CodeGen):
        element_classes = {bqplot_image_gl.ImageGL: FigureElement}
        ignore_props = "domain_class".split() + generate.CodeGen.ignore_props

    current_module = __import__(__name__)

    CodeGen([bqplot_image_gl]).generate(__file__)

# generated code:


def _Contour(
    apply_clip: bool = True,
    color: typing.Union[str, list] = None,
    contour_lines: list = [],
    display_legend: bool = False,
    enable_hover: bool = True,
    image: Element[bqplot_image_gl.imagegl.ImageGL] = None,
    interactions: dict = {"hover": "tooltip"},
    label: typing.Union[str, list] = None,
    label_steps: int = 40,
    labels: list = [],
    level: typing.Union[float, list] = 0.0,
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {"x": {"orientation": "horizontal", "dimension": "x"}, "y": {"orientation": "vertical", "dimension": "y"}},
    selected: ndarray = None,
    selected_style: dict = {},
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[typing.Union[str, list]], Any] = None,
    on_contour_lines: typing.Callable[[list], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_image: typing.Callable[[Element[bqplot_image_gl.imagegl.ImageGL]], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_label: typing.Callable[[typing.Union[str, list]], Any] = None,
    on_label_steps: typing.Callable[[int], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_level: typing.Callable[[typing.Union[float, list]], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
) -> Element[bqplot_image_gl.imagegl.Contour]:
    """ """
    ...


@implements(_Contour)
def Contour(**kwargs):

    widget_cls = bqplot_image_gl.imagegl.Contour
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Contour


def _ImageGL(
    apply_clip: bool = True,
    display_legend: bool = False,
    enable_hover: bool = True,
    image: ndarray = np.array(0),
    interactions: dict = {"hover": "tooltip"},
    interpolation: str = "nearest",
    labels: list = [],
    opacity: float = 1.0,
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "image": {"dimension": "color"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    x: ndarray = np.array([0, 1]),
    y: ndarray = np.array([0, 1]),
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_image: typing.Callable[[ndarray], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_interpolation: typing.Callable[[str], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_opacity: typing.Callable[[float], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot_image_gl.imagegl.ImageGL]:
    """An example widget."""
    ...


@implements(_ImageGL)
def ImageGL(**kwargs):

    widget_cls = bqplot_image_gl.imagegl.ImageGL
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return FigureElement(comp, kwargs=kwargs)


del _ImageGL


def _LinesGL(
    apply_clip: bool = True,
    close_path: bool = False,
    color: ndarray = None,
    colors: list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
    curves_subset: list = [],
    display_legend: bool = False,
    enable_hover: bool = True,
    fill: str = "none",
    fill_colors: list = [],
    fill_opacities: list = [],
    interactions: dict = {"hover": "tooltip"},
    interpolation: str = "linear",
    labels: list = [],
    labels_visibility: str = "none",
    line_style: str = "solid",
    marker: str = None,
    marker_size: int = 64,
    opacities: list = [],
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "color": {"dimension": "color"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    stroke_width: float = 2.0,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    x: ndarray = np.array([]),
    y: ndarray = np.array([]),
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_close_path: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_curves_subset: typing.Callable[[list], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_fill: typing.Callable[[str], Any] = None,
    on_fill_colors: typing.Callable[[list], Any] = None,
    on_fill_opacities: typing.Callable[[list], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_interpolation: typing.Callable[[str], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_labels_visibility: typing.Callable[[str], Any] = None,
    on_line_style: typing.Callable[[str], Any] = None,
    on_marker: typing.Callable[[str], Any] = None,
    on_marker_size: typing.Callable[[int], Any] = None,
    on_opacities: typing.Callable[[list], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_stroke_width: typing.Callable[[float], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot_image_gl.linesgl.LinesGL]:
    """An example widget."""
    ...


@implements(_LinesGL)
def LinesGL(**kwargs):

    widget_cls = bqplot_image_gl.linesgl.LinesGL
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _LinesGL
