import datetime
import typing
from typing import Any, Dict, Union

import bqplot
import ipywidgets
import numpy as np
from numpy import ndarray

import reacton
from reacton.core import ContainerAdder, Element, _get_render_context

from . import ipywidgets as w
from .ipywidgets import Layout
from .utils import implements


class FigureElement(Element[bqplot.Figure]):
    def __enter__(self):
        rc = _get_render_context()
        ca = ContainerAdder[bqplot.Figure](self, "marks")
        assert rc.context is self._current_context, f"Context change from {self._current_context} -> {rc.context}"
        rc.container_adders.append(ca)
        return self


if __name__ == "__main__":

    from . import generate

    class CodeGen(generate.CodeGen):
        element_classes = {bqplot.Figure: FigureElement}
        ignore_props = "domain_class".split() + generate.CodeGen.ignore_props

        def get_extra_argument(self, cls):
            return {ipywidgets.Button: [("on_click", None, typing.Callable[[], Any])]}.get(cls, [])

    current_module = __import__(__name__)

    CodeGen([bqplot]).generate(__file__)


# generated code:


def _Albers(
    allow_padding: bool = True,
    center: tuple = (0, 60),
    parallels: tuple = (29.5, 45.5),
    precision: float = 0.1,
    reverse: bool = False,
    rotate: tuple = (96, 0),
    scale_factor: float = 250,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_center: typing.Callable[[tuple], Any] = None,
    on_parallels: typing.Callable[[tuple], Any] = None,
    on_precision: typing.Callable[[float], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_rotate: typing.Callable[[tuple], Any] = None,
    on_scale_factor: typing.Callable[[float], Any] = None,
) -> Element[bqplot.scales.Albers]:
    """A geographical scale which is an alias for a conic equal area projection.

    The Albers projection is a conic equal area map. It does not preserve scale
    or shape, though it is recommended for chloropleths since it preserves the
    relative areas of geographic features. Default values are US-centric.

    Attributes
    ----------
    scale_factor: float (default: 250)
        Specifies the scale value for the projection
    rotate: tuple (default: (96, 0))
        Degree of rotation in each axis.
    parallels: tuple (default: (29.5, 45.5))
        Sets the two parallels for the conic projection.
    center: tuple (default: (0, 60))
        Specifies the longitude and latitude where the map is centered.
    precision: float (default: 0.1)
        Specifies the threshold for the projections adaptive resampling to the
        specified value in pixels.
    rtype: (Number, Number) (class-level attribute)
        This attribute should not be modified. The range type of a geo
        scale is a tuple.
    dtype: type (class-level attribute)
        the associated data type / domain type


    """
    ...


@implements(_Albers)
def Albers(**kwargs):

    widget_cls = bqplot.scales.Albers
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Albers


def _AlbersUSA(
    allow_padding: bool = True,
    reverse: bool = False,
    scale_factor: float = 1200,
    translate: tuple = (600, 490),
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_scale_factor: typing.Callable[[float], Any] = None,
    on_translate: typing.Callable[[tuple], Any] = None,
) -> Element[bqplot.scales.AlbersUSA]:
    """A composite projection of four Albers projections meant specifically for
    the United States.

    Attributes
    ----------
    scale_factor: float (default: 1200)
        Specifies the scale value for the projection
    translate: tuple (default: (600, 490))
    rtype: (Number, Number) (class-level attribute)
        This attribute should not be modified. The range type of a geo
        scale is a tuple.
    dtype: type (class-level attribute)
        the associated data type / domain type


    """
    ...


@implements(_AlbersUSA)
def AlbersUSA(**kwargs):

    widget_cls = bqplot.scales.AlbersUSA
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _AlbersUSA


def _Axis(
    color: str = None,
    grid_color: str = None,
    grid_lines: str = "solid",
    label: str = "",
    label_color: str = None,
    label_location: str = "middle",
    label_offset: str = None,
    num_ticks: int = None,
    offset: dict = {},
    orientation: str = "horizontal",
    scale: Element[bqplot.scales.Scale] = None,
    side: str = None,
    tick_format: str = None,
    tick_rotate: int = 0,
    tick_style: dict = {},
    tick_values: ndarray = None,
    visible: bool = True,
    on_color: typing.Callable[[str], Any] = None,
    on_grid_color: typing.Callable[[str], Any] = None,
    on_grid_lines: typing.Callable[[str], Any] = None,
    on_label: typing.Callable[[str], Any] = None,
    on_label_color: typing.Callable[[str], Any] = None,
    on_label_location: typing.Callable[[str], Any] = None,
    on_label_offset: typing.Callable[[str], Any] = None,
    on_num_ticks: typing.Callable[[int], Any] = None,
    on_offset: typing.Callable[[dict], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_scale: typing.Callable[[Element[bqplot.scales.Scale]], Any] = None,
    on_side: typing.Callable[[str], Any] = None,
    on_tick_format: typing.Callable[[str], Any] = None,
    on_tick_rotate: typing.Callable[[int], Any] = None,
    on_tick_style: typing.Callable[[dict], Any] = None,
    on_tick_values: typing.Callable[[ndarray], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.axes.Axis]:
    """A line axis.

    A line axis is the visual representation of a numerical or date scale.

    Attributes
    ----------
    icon: string (class-level attribute)
        The font-awesome icon name for this object.
    axis_types: dict (class-level attribute)
        A registry of existing axis types.
    orientation: {'horizontal', 'vertical'}
        The orientation of the axis, either vertical or horizontal
    side: {'bottom', 'top', 'left', 'right'} or None (default: None)
        The side of the axis, either bottom, top, left or right.
    label: string (default: '')
        The axis label
    tick_format: string or None (default: '')
        The tick format for the axis, for dates use d3 string formatting.
    scale: Scale
        The scale represented by the axis
    num_ticks: int or None (default: None)
        If tick_values is None, number of ticks
    tick_values: numpy.ndarray or None (default: None)
        Tick values for the axis
    offset: dict (default: {})
        Contains a scale and a value {'scale': scale or None,
        'value': value of the offset}
        If offset['scale'] is None, the corresponding figure scale is used
        instead.
    label_location: {'middle', 'start', 'end'}
        The location of the label along the axis, one of 'start', 'end' or
        'middle'
    label_color: Color or None (default: None)
        The color of the axis label
    grid_lines: {'none', 'solid', 'dashed'}
        The display of the grid lines
    grid_color: Color or None (default: None)
        The color of the grid lines
    color: Color or None (default: None)
        The color of the line
    label_offset: string or None (default: None)
        Label displacement from the axis line. Units allowed are 'em', 'px'
        and 'ex'. Positive values are away from the figure and negative
        values are towards the figure with respect to the axis line.
    visible: bool (default: True)
        A visibility toggle for the axis
    tick_style: Dict (default: {})
        Dictionary containing the CSS-style of the text for the ticks.
        For example: font-size of the text can be changed by passing
        `{'font-size': 14}`
    tick_rotate: int (default: 0)
        Degrees to rotate tick labels by.


    """
    ...


@implements(_Axis)
def Axis(**kwargs):

    widget_cls = bqplot.axes.Axis
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Axis


def _Bars(
    align: str = "center",
    apply_clip: bool = True,
    base: float = 0.0,
    color: ndarray = None,
    color_mode: str = "auto",
    colors: list = ["steelblue"],
    display_legend: bool = False,
    enable_hover: bool = True,
    fill: bool = True,
    interactions: dict = {"hover": "tooltip"},
    label_display: bool = False,
    label_display_format: str = ".2f",
    label_display_horizontal_offset: float = 0.0,
    label_display_vertical_offset: float = 0.0,
    label_font_style: dict = {},
    labels: list = [],
    opacities: list = [],
    opacity_mode: str = "auto",
    orientation: str = "vertical",
    padding: float = 0.05,
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "color": {"dimension": "color"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    stroke: str = None,
    stroke_width: float = 1.0,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    type: str = "stacked",
    unselected_style: dict = {},
    visible: bool = True,
    x: ndarray = np.array([]),
    y: ndarray = np.array([]),
    on_align: typing.Callable[[str], Any] = None,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_base: typing.Callable[[float], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_color_mode: typing.Callable[[str], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_fill: typing.Callable[[bool], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_label_display: typing.Callable[[bool], Any] = None,
    on_label_display_format: typing.Callable[[str], Any] = None,
    on_label_display_horizontal_offset: typing.Callable[[float], Any] = None,
    on_label_display_vertical_offset: typing.Callable[[float], Any] = None,
    on_label_font_style: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_opacities: typing.Callable[[list], Any] = None,
    on_opacity_mode: typing.Callable[[str], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_padding: typing.Callable[[float], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_stroke: typing.Callable[[str], Any] = None,
    on_stroke_width: typing.Callable[[float], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_type: typing.Callable[[str], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot.marks.Bars]:
    """Bar mark.

    In the case of the Bars mark, scales for 'x' and 'y'  MUST be provided.
    The scales of other data attributes are optional. In the case where another
    data attribute than 'x' or 'y' is provided but the corresponding scale is
    missing, the data attribute is ignored.

    Attributes
    ----------
    icon: string (class-level attribute)
        font-awesome icon for that mark
    name: string (class-level attribute)
        user-friendly name of the mark
    color_mode: {'auto', 'group', 'element', 'no_group'}
        Specify how default colors are applied to bars.
        The 'group' mode means colors are assigned per group. If the list
        of colors is shorter than the number of groups, colors are reused.
        The 'element' mode means colors are assigned per group element. If the list
        of colors is shorter than the number of bars in a group, colors are reused.
        The 'no_group' mode means colors are assigned per bar, discarding the fact
        that there are groups or stacks. If the list of colors is shorter than the
        total number of bars, colors are reused.
    opacity_mode: {'auto', 'group', 'element', 'no_group'}
        Same as the `color_mode` attribute, but for the opacity.
    type: {'stacked', 'grouped'}
        whether 2-dimensional bar charts should appear grouped or stacked.
    colors: list of colors (default: ['steelblue'])
        list of colors for the bars.
    orientation: {'horizontal', 'vertical'}
        Specifies whether the bar chart is drawn horizontally or vertically.
        If a horizontal bar chart is drawn, the x data is drawn vertically.
    padding: float (default: 0.05)
        Attribute to control the spacing between the bars value is specified
        as a percentage of the width of the bar
    fill: Bool (default: True)
        Whether to fill the bars or not
    stroke: Color or None (default: None)
        Stroke color for the bars
    stroke_width: Float (default: 0.)
        Stroke width of the bars
    opacities: list of floats (default: [])
        Opacities for the bars. Defaults to 1 when the list is too
        short, or the element of the list is set to None.
    base: float (default: 0.0)
        reference value from which the bars are drawn. defaults to 0.0
    align: {'center', 'left', 'right'}
        alignment of bars with respect to the tick value
    label_display: bool (default: False)
        whether or not to display bar data labels
    label_display_format: string (default: .2f)
        format for displaying values.
    label_font_style: dict
        CSS style for the text of each cell
    label_display_vertical_offset: float
        vertical offset value for the label display
    label_display_horizontal_offset: float
        horizontal offset value for the label display

    Data Attributes

    x: numpy.ndarray (default: [])
        abscissas of the data points (1d array)
    y: numpy.ndarray (default: [])
        ordinates of the values for the data points
    color: numpy.ndarray or None (default: None)
        color of the data points (1d array). Defaults to default_color when not
        provided or when a value is NaN

    Notes
    -----
    The fields which can be passed to the default tooltip are:
        All the data attributes
        index: index of the bar being hovered on
        sub_index: if data is two dimensional, this is the minor index


    """
    ...


@implements(_Bars)
def Bars(**kwargs):

    widget_cls = bqplot.marks.Bars
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Bars


def _BaseAxis() -> Element[bqplot.axes.BaseAxis]:
    """ """
    ...


@implements(_BaseAxis)
def BaseAxis(**kwargs):

    widget_cls = bqplot.axes.BaseAxis
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _BaseAxis


def _Bins(
    align: str = "center",
    apply_clip: bool = True,
    base: float = 0.0,
    bins: typing.Union[int, list, str] = 10,
    color: ndarray = None,
    color_mode: str = "auto",
    colors: list = ["steelblue"],
    density: bool = False,
    display_legend: bool = False,
    enable_hover: bool = True,
    fill: bool = True,
    interactions: dict = {"hover": "tooltip"},
    label_display: bool = False,
    label_display_format: str = ".2f",
    label_display_horizontal_offset: float = 0.0,
    label_display_vertical_offset: float = 0.0,
    label_font_style: dict = {},
    labels: list = [],
    max: float = None,
    min: float = None,
    opacities: list = [],
    opacity_mode: str = "auto",
    orientation: str = "vertical",
    padding: float = 0.05,
    preserve_domain: dict = {},
    sample: ndarray = np.array([]),
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "color": {"dimension": "color"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    stroke: str = None,
    stroke_width: float = 1.0,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    type: str = "stacked",
    unselected_style: dict = {},
    visible: bool = True,
    x: ndarray = np.array([]),
    y: ndarray = np.array([]),
    on_align: typing.Callable[[str], Any] = None,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_base: typing.Callable[[float], Any] = None,
    on_bins: typing.Callable[[typing.Union[int, list, str]], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_color_mode: typing.Callable[[str], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_density: typing.Callable[[bool], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_fill: typing.Callable[[bool], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_label_display: typing.Callable[[bool], Any] = None,
    on_label_display_format: typing.Callable[[str], Any] = None,
    on_label_display_horizontal_offset: typing.Callable[[float], Any] = None,
    on_label_display_vertical_offset: typing.Callable[[float], Any] = None,
    on_label_font_style: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_opacities: typing.Callable[[list], Any] = None,
    on_opacity_mode: typing.Callable[[str], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_padding: typing.Callable[[float], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_sample: typing.Callable[[ndarray], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_stroke: typing.Callable[[str], Any] = None,
    on_stroke_width: typing.Callable[[float], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_type: typing.Callable[[str], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot.marks.Bins]:
    """Backend histogram mark.

    A `Bars` instance that bins sample data.

    It is very similar in purpose to the `Hist` mark, the difference being that
    the binning is done in the backend (python), which avoids large amounts of
    data being shipped back and forth to the frontend. It should therefore be
    preferred for large data.
    The binning method is the numpy `histogram` method.

    The following  documentation is in part taken from the numpy documentation.

    Attributes
    ----------
    icon: string (class-level attribute)
        font-awesome icon for that mark
    name: string (class-level attribute)
        user-friendly name of the mark
    bins: nonnegative int (default: 10)
          or {'auto', 'fd', 'doane', 'scott', 'rice', 'sturges', 'sqrt'}
        If `bins` is an int, it defines the number of equal-width
        bins in the given range (10, by default).
        If `bins` is a string (method name), `histogram` will use
        the method chosen to calculate the optimal bin width and
        consequently the number of bins (see `Notes` for more detail on
        the estimators) from the data that falls within the requested
        range.
    density : bool (default: `False`)
        If `False`, the height of each bin is the number of samples in it.
        If `True`, the height of each bin is the value of the
        probability *density* function at the bin, normalized such that
        the *integral* over the range is 1. Note that the sum of the
        histogram values will not be equal to 1 unless bins of unity
        width are chosen; it is not a probability *mass* function.
    min : float (default: None)
        The lower range of the bins.  If not provided, lower range
        is simply `x.min()`.
    max : float (default: None)
        The upper range of the bins.  If not provided, lower range
        is simply `x.max()`.
    Data Attributes
    sample: numpy.ndarray (default: [])
        sample of which the histogram must be computed.
    Notes
    -----
    The fields which can be passed to the default tooltip are:
        All the `Bars` data attributes (`x`, `y`, `color`)
        index: index of the bin


    """
    ...


@implements(_Bins)
def Bins(**kwargs):

    widget_cls = bqplot.marks.Bins
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Bins


def _Boxplot(
    apply_clip: bool = True,
    auto_detect_outliers: bool = True,
    box_fill_color: str = "steelblue",
    box_width: int = None,
    display_legend: bool = False,
    enable_hover: bool = True,
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    opacities: list = [],
    outlier_fill_color: str = "gray",
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {"x": {"orientation": "horizontal", "dimension": "x"}, "y": {"orientation": "vertical", "dimension": "y"}},
    selected: ndarray = None,
    selected_style: dict = {},
    stroke: str = None,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    x: ndarray = np.array([]),
    y: ndarray = np.array([[]]),
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_auto_detect_outliers: typing.Callable[[bool], Any] = None,
    on_box_fill_color: typing.Callable[[str], Any] = None,
    on_box_width: typing.Callable[[int], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_opacities: typing.Callable[[list], Any] = None,
    on_outlier_fill_color: typing.Callable[[str], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_stroke: typing.Callable[[str], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot.marks.Boxplot]:
    """Boxplot marks.

    Attributes
    ----------
    stroke: Color or None
        stroke color of the marker
    color: Color
        fill color of the box
    opacities: list of floats (default: [])
        Opacities for the markers of the boxplot. Defaults to 1 when the
        list is too short, or the element of the list is set to None.
    outlier-color: color
        color for the outlier
    box_width: int (default: None)
        width of the box in pixels. The minimum value is 5.
        If set to None, box_with is auto calculated
    auto_detect_outliers: bool (default: True)
        Flag to toggle outlier auto-detection

    Data Attributes

    x: numpy.ndarray (default: [])
        abscissas of the data points (1d array)
    y: numpy.ndarray (default: [[]])
        Sample data points (2d array)


    """
    ...


@implements(_Boxplot)
def Boxplot(**kwargs):

    widget_cls = bqplot.marks.Boxplot
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Boxplot


def _ColorAxis(
    color: str = None,
    grid_color: str = None,
    grid_lines: str = "solid",
    label: str = "",
    label_color: str = None,
    label_location: str = "middle",
    label_offset: str = None,
    num_ticks: int = None,
    offset: dict = {},
    orientation: str = "horizontal",
    scale: Element[bqplot.scales.ColorScale] = None,
    side: str = "bottom",
    tick_format: str = None,
    tick_rotate: int = 0,
    tick_style: dict = {},
    tick_values: ndarray = None,
    visible: bool = True,
    on_color: typing.Callable[[str], Any] = None,
    on_grid_color: typing.Callable[[str], Any] = None,
    on_grid_lines: typing.Callable[[str], Any] = None,
    on_label: typing.Callable[[str], Any] = None,
    on_label_color: typing.Callable[[str], Any] = None,
    on_label_location: typing.Callable[[str], Any] = None,
    on_label_offset: typing.Callable[[str], Any] = None,
    on_num_ticks: typing.Callable[[int], Any] = None,
    on_offset: typing.Callable[[dict], Any] = None,
    on_orientation: typing.Callable[[str], Any] = None,
    on_scale: typing.Callable[[Element[bqplot.scales.ColorScale]], Any] = None,
    on_side: typing.Callable[[str], Any] = None,
    on_tick_format: typing.Callable[[str], Any] = None,
    on_tick_rotate: typing.Callable[[int], Any] = None,
    on_tick_style: typing.Callable[[dict], Any] = None,
    on_tick_values: typing.Callable[[ndarray], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.axes.ColorAxis]:
    """A colorbar axis.

    A color axis is the visual representation of a color scale.

    Attributes
    ----------
    scale: ColorScale
        The scale represented by the axis


    """
    ...


@implements(_ColorAxis)
def ColorAxis(**kwargs):

    widget_cls = bqplot.axes.ColorAxis
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _ColorAxis


def _ColorScale(
    allow_padding: bool = True,
    colors: list = [],
    extrapolation: str = "constant",
    max: float = None,
    mid: float = None,
    min: float = None,
    reverse: bool = False,
    scale_type: str = "linear",
    scheme: str = "RdYlGn",
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_extrapolation: typing.Callable[[str], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_mid: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_scale_type: typing.Callable[[str], Any] = None,
    on_scheme: typing.Callable[[str], Any] = None,
) -> Element[bqplot.scales.ColorScale]:
    """A color scale.

    A mapping from numbers to colors. The relation is affine by part.

    Attributes
    ----------
    scale_type: {'linear'}
        scale type
    colors: list of colors (default: [])
        list of colors
    min: float or None (default: None)
        if not None, min is the minimal value of the domain
    max: float or None (default: None)
        if not None, max is the maximal value of the domain
    mid: float or None (default: None)
        if not None, mid is the value corresponding to the mid color.
    scheme: string (default: 'RdYlGn')
        Colorbrewer color scheme of the color scale.
    extrapolation: {'constant', 'linear'} (default: 'constant')
        How to extrapolate values outside the [min, max] domain.
    rtype: string (class-level attribute)
        The range type of a color scale is 'Color'. This should not be modified.
    dtype: type (class-level attribute)
        the associated data type / domain type


    """
    ...


@implements(_ColorScale)
def ColorScale(**kwargs):

    widget_cls = bqplot.scales.ColorScale
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _ColorScale


def _DOMWidget(
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
) -> Element[ipywidgets.widgets.domwidget.DOMWidget]:
    """Widget that can be inserted into the DOM"""
    ...


@implements(_DOMWidget)
def DOMWidget(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = Layout(**kwargs["layout"])
    widget_cls = ipywidgets.widgets.domwidget.DOMWidget
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _DOMWidget


def _DateColorScale(
    allow_padding: bool = True,
    colors: list = [],
    extrapolation: str = "constant",
    max: datetime.datetime = None,
    mid: datetime.datetime = None,
    min: datetime.datetime = None,
    reverse: bool = False,
    scale_type: str = "linear",
    scheme: str = "RdYlGn",
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_extrapolation: typing.Callable[[str], Any] = None,
    on_max: typing.Callable[[datetime.datetime], Any] = None,
    on_mid: typing.Callable[[datetime.datetime], Any] = None,
    on_min: typing.Callable[[datetime.datetime], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_scale_type: typing.Callable[[str], Any] = None,
    on_scheme: typing.Callable[[str], Any] = None,
) -> Element[bqplot.scales.DateColorScale]:
    """A date color scale.

    A mapping from dates to a numerical domain.

    Attributes
    ----------
    min: Date or None (default: None)
        if not None, min is the minimal value of the domain
    max: Date or None (default: None)
        if not None, max is the maximal value of the domain
    mid: Date or None (default: None)
        if not None, mid is the value corresponding to the mid color.
    rtype: string (class-level attribute)
        This attribute should not be modified by the user.
        The range type of a color scale is 'Color'.
    dtype: type (class-level attribute)
        the associated data type / domain type


    """
    ...


@implements(_DateColorScale)
def DateColorScale(**kwargs):

    widget_cls = bqplot.scales.DateColorScale
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _DateColorScale


def _DateScale(
    allow_padding: bool = True,
    max: datetime.datetime = None,
    min: datetime.datetime = None,
    reverse: bool = False,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_max: typing.Callable[[datetime.datetime], Any] = None,
    on_min: typing.Callable[[datetime.datetime], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.scales.DateScale]:
    """A date scale, with customizable formatting.

    An affine mapping from dates to a numerical range.

    Attributes
    ----------
    min: Date or None (default: None)
        if not None, min is the minimal value of the domain
    max: Date (default: None)
        if not None, max is the maximal value of the domain
    domain_class: type (default: Date)
         traitlet type used to validate values in of the domain of the scale.
    rtype: string (class-level attribute)
        This attribute should not be modified by the user.
        The range type of a linear scale is numerical.
    dtype: type (class-level attribute)
        the associated data type / domain type


    """
    ...


@implements(_DateScale)
def DateScale(**kwargs):

    widget_cls = bqplot.scales.DateScale
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _DateScale


def _EquiRectangular(
    allow_padding: bool = True,
    center: tuple = (0, 60),
    reverse: bool = False,
    scale_factor: float = 145.0,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_center: typing.Callable[[tuple], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_scale_factor: typing.Callable[[float], Any] = None,
) -> Element[bqplot.scales.EquiRectangular]:
    """An elementary projection that uses the identity function.

    The projection is neither equal-area nor conformal.

    Attributes
    ----------
    scale_factor: float (default: 145)
       Specifies the scale value for the projection
    center: tuple (default: (0, 60))
        Specifies the longitude and latitude where the map is centered.


    """
    ...


@implements(_EquiRectangular)
def EquiRectangular(**kwargs):

    widget_cls = bqplot.scales.EquiRectangular
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _EquiRectangular


def _Figure(
    animation_duration: int = 0,
    axes: list = [],
    background_style: dict = {},
    fig_margin: dict = {"top": 60, "bottom": 60, "left": 60, "right": 60},
    interaction: Element[bqplot.interacts.Interaction] = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    legend_location: str = "top-right",
    legend_style: dict = {},
    legend_text: dict = {},
    marks: list = [],
    max_aspect_ratio: float = 100,
    min_aspect_ratio: float = 0.01,
    padding_x: float = 0.0,
    padding_y: float = 0.025,
    pixel_ratio: float = None,
    scale_x: Element[bqplot.scales.Scale] = None,
    scale_y: Element[bqplot.scales.Scale] = None,
    theme: str = "classic",
    title: str = "",
    title_style: dict = {},
    on_animation_duration: typing.Callable[[int], Any] = None,
    on_axes: typing.Callable[[list], Any] = None,
    on_background_style: typing.Callable[[dict], Any] = None,
    on_fig_margin: typing.Callable[[dict], Any] = None,
    on_interaction: typing.Callable[[Element[bqplot.interacts.Interaction]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_legend_location: typing.Callable[[str], Any] = None,
    on_legend_style: typing.Callable[[dict], Any] = None,
    on_legend_text: typing.Callable[[dict], Any] = None,
    on_marks: typing.Callable[[list], Any] = None,
    on_max_aspect_ratio: typing.Callable[[float], Any] = None,
    on_min_aspect_ratio: typing.Callable[[float], Any] = None,
    on_padding_x: typing.Callable[[float], Any] = None,
    on_padding_y: typing.Callable[[float], Any] = None,
    on_pixel_ratio: typing.Callable[[float], Any] = None,
    on_scale_x: typing.Callable[[Element[bqplot.scales.Scale]], Any] = None,
    on_scale_y: typing.Callable[[Element[bqplot.scales.Scale]], Any] = None,
    on_theme: typing.Callable[[str], Any] = None,
    on_title: typing.Callable[[str], Any] = None,
    on_title_style: typing.Callable[[dict], Any] = None,
) -> Element[bqplot.figure.Figure]:
    """Main canvas for drawing a chart.

    The Figure object holds the list of Marks and Axes. It also holds an
    optional Interaction object that is responsible for figure-level mouse
    interactions, the "interaction layer".

    Besides, the Figure object has two reference scales, for positioning items
    in an absolute fashion in the figure canvas.

    Attributes
    ----------
    title: string (default: '')
        title of the figure
    axes: List of Axes (default: [])
        list containing the instances of the axes for the figure
    marks: List of Marks (default: [])
        list containing the marks which are to be appended to the figure
    interaction: Interaction or None (default: None)
        optional interaction layer for the figure
    scale_x: Scale
        Scale representing the x values of the figure
    scale_y: Scale
        Scale representing the y values of the figure
    padding_x: Float (default: 0.0)
        Padding to be applied in the horizontal direction of the figure
        around the data points, proportion of the horizontal length
    padding_y: Float (default: 0.025)
        Padding to be applied in the vertical direction of the figure
        around the data points, proportion of the vertical length
    legend_location: {'top-right', 'top', 'top-left', 'left',
        'bottom-left', 'bottom', 'bottom-right', 'right'}
        location of the legend relative to the center of the figure
    background_style: Dict (default: {})
        CSS style to be applied to the background of the figure
    legend_style: Dict (default: {})
        CSS style to be applied to the SVG legend e.g, {'fill': 'white'}
    legend_text: Dict (default: {})
        CSS style to be applied to the legend text e.g., {'font-size': 20}
    title_style: Dict (default: {})
        CSS style to be applied to the title of the figure
    animation_duration: nonnegative int (default: 0)
        Duration of transition on change of data attributes, in milliseconds.
    pixel_ratio:
        Pixel ratio of the WebGL canvas (2 on retina screens). Set to 1 for better performance,
        but less crisp edges. If set to None it will use the browser's window.devicePixelRatio.

    Layout Attributes

    fig_margin: dict (default: {top=60, bottom=60, left=60, right=60})
        Dictionary containing the top, bottom, left and right margins. The user
        is responsible for making sure that the width and height are greater
        than the sum of the margins.
    min_aspect_ratio: float
         minimum width / height ratio of the figure
    max_aspect_ratio: float
         maximum width / height ratio of the figure

    Methods
    -------

    save_png:
       Saves the figure as a PNG file
    save_svg:
       Saves the figure as an SVG file

    Note
    ----

    The aspect ratios stand for width / height ratios.

     - If the available space is within bounds in terms of min and max aspect
       ratio, we use the entire available space.
     - If the available space is too oblong horizontally, we use the client
       height and the width that corresponds max_aspect_ratio (maximize width
       under the constraints).
     - If the available space is too oblong vertically, we use the client width
       and the height that corresponds to min_aspect_ratio (maximize height
       under the constraint).
       This corresponds to maximizing the area under the constraints.

    Default min and max aspect ratio are both equal to 16 / 9.


    """
    ...


@implements(_Figure)
def Figure(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = bqplot.figure.Figure
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return FigureElement(comp, kwargs=kwargs)


del _Figure


def _FlexLine(
    apply_clip: bool = True,
    color: ndarray = None,
    colors: list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
    display_legend: bool = False,
    enable_hover: bool = True,
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "color": {"dimension": "color"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    stroke_width: float = 1.5,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    width: ndarray = None,
    x: ndarray = np.array([]),
    y: ndarray = np.array([]),
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
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
    on_width: typing.Callable[[ndarray], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot.marks.FlexLine]:
    """Flexible Lines mark.

    In the case of the FlexLines mark, scales for 'x' and 'y' MUST be provided.
    Scales for the color and width data attributes are optional. In the case
    where another data attribute than 'x' or 'y' is provided but the
    corresponding scale is missing, the data attribute is ignored.

    Attributes
    ----------
    name: string (class-level attributes)
        user-friendly name of the mark
    colors: list of colors (default: CATEGORY10)
        List of colors for the Lines
    stroke_width: float (default: 1.5)
        Default stroke width of the Lines

    Data Attributes

    x: numpy.ndarray (default: [])
        abscissas of the data points (1d array)
    y: numpy.ndarray (default: [])
        ordinates of the data points (1d array)
    color: numpy.ndarray or None (default: None)
        Array controlling the color of the data points
    width: numpy.ndarray or None (default: None)
        Array controlling the widths of the Lines.


    """
    ...


@implements(_FlexLine)
def FlexLine(**kwargs):

    widget_cls = bqplot.marks.FlexLine
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _FlexLine


def _GeoScale(
    allow_padding: bool = True,
    reverse: bool = False,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.scales.GeoScale]:
    """The base projection scale class for Map marks.

    The GeoScale represents a mapping between topographic data and a
    2d visual representation.


    """
    ...


@implements(_GeoScale)
def GeoScale(**kwargs):

    widget_cls = bqplot.scales.GeoScale
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _GeoScale


def _Gnomonic(
    allow_padding: bool = True,
    center: tuple = (0, 60),
    clip_angle: float = 89.999,
    precision: float = 0.1,
    reverse: bool = False,
    scale_factor: float = 145.0,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_center: typing.Callable[[tuple], Any] = None,
    on_clip_angle: typing.Callable[[float], Any] = None,
    on_precision: typing.Callable[[float], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_scale_factor: typing.Callable[[float], Any] = None,
) -> Element[bqplot.scales.Gnomonic]:
    """A perspective projection which displays great circles as straight lines.

    The projection is neither equal-area nor conformal.

    Attributes
    ----------
    scale_factor: float (default: 145)
       Specifies the scale value for the projection
    center: tuple (default: (0, 60))
        Specifies the longitude and latitude where the map is centered.
    precision: float (default: 0.1)
        Specifies the threshold for the projections adaptive resampling to the
        specified value in pixels.
    clip_angle: float (default: 89.999)
        Specifies the clipping circle radius to the specified angle in degrees.


    """
    ...


@implements(_Gnomonic)
def Gnomonic(**kwargs):

    widget_cls = bqplot.scales.Gnomonic
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Gnomonic


def _Graph(
    apply_clip: bool = True,
    charge: int = -600,
    color: ndarray = None,
    colors: list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
    directed: bool = True,
    display_legend: bool = False,
    enable_hover: bool = True,
    highlight_links: bool = True,
    hovered_point: int = None,
    hovered_style: dict = {},
    interactions: dict = {"hover": "tooltip", "click": "select"},
    labels: list = [],
    link_color: ndarray = np.array([]),
    link_data: list = [],
    link_distance: float = 100,
    link_matrix: ndarray = np.array([]),
    link_type: str = "arc",
    node_data: list = [],
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "color": {"dimension": "color"},
        "link_color": {"dimension": "link_color"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    static: bool = False,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unhovered_style: dict = {},
    unselected_style: dict = {},
    visible: bool = True,
    x: ndarray = np.array([]),
    y: ndarray = np.array([]),
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_charge: typing.Callable[[int], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_directed: typing.Callable[[bool], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_highlight_links: typing.Callable[[bool], Any] = None,
    on_hovered_point: typing.Callable[[int], Any] = None,
    on_hovered_style: typing.Callable[[dict], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_link_color: typing.Callable[[ndarray], Any] = None,
    on_link_data: typing.Callable[[list], Any] = None,
    on_link_distance: typing.Callable[[float], Any] = None,
    on_link_matrix: typing.Callable[[ndarray], Any] = None,
    on_link_type: typing.Callable[[str], Any] = None,
    on_node_data: typing.Callable[[list], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_static: typing.Callable[[bool], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unhovered_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot.marks.Graph]:
    """Graph with nodes and links.

    Attributes
    ----------
    node_data: List
        list of node attributes for the graph
    link_matrix: numpy.ndarray of shape(len(nodes), len(nodes))
        link data passed as 2d matrix
    link_data: List
        list of link attributes for the graph
    charge: int (default: -600)
        charge of force layout. Will be ignored when x and y data attributes
        are set
    static: bool (default: False)
        whether the graph is static or not
    link_distance: float (default: 100)
        link distance in pixels between nodes. Will be ignored when x and y
        data attributes are set
    link_type: {'arc', 'line', 'slant_line'} (default: 'arc')
        Enum representing link type
    directed: bool (default: True)
        directed or undirected graph
    highlight_links: bool (default: True)
        highlights incoming and outgoing links when hovered on a node
    colors: list (default: CATEGORY10)
        list of node colors

    Data Attributes

    x: numpy.ndarray (default: [])
        abscissas of the node data points (1d array)
    y: numpy.ndarray (default: [])
        ordinates of the node data points (1d array)
    color: numpy.ndarray or None (default: None)
        color of the node data points (1d array).
    link_color: numpy.ndarray of shape(len(nodes), len(nodes))
        link data passed as 2d matrix


    """
    ...


@implements(_Graph)
def Graph(**kwargs):

    widget_cls = bqplot.marks.Graph
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Graph


def _GridHeatMap(
    anchor_style: dict = {},
    apply_clip: bool = True,
    color: ndarray = None,
    column: ndarray = None,
    column_align: str = "start",
    display_format: str = None,
    display_legend: bool = False,
    enable_hover: bool = True,
    font_style: dict = {},
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    null_color: str = "black",
    opacity: float = 1.0,
    preserve_domain: dict = {},
    row: ndarray = None,
    row_align: str = "start",
    scales: dict = {},
    scales_metadata: dict = {
        "row": {"orientation": "vertical", "dimension": "y"},
        "column": {"orientation": "horizontal", "dimension": "x"},
        "color": {"dimension": "color"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    stroke: str = "black",
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    on_anchor_style: typing.Callable[[dict], Any] = None,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_column: typing.Callable[[ndarray], Any] = None,
    on_column_align: typing.Callable[[str], Any] = None,
    on_display_format: typing.Callable[[str], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_font_style: typing.Callable[[dict], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_null_color: typing.Callable[[str], Any] = None,
    on_opacity: typing.Callable[[float], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_row: typing.Callable[[ndarray], Any] = None,
    on_row_align: typing.Callable[[str], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_stroke: typing.Callable[[str], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.marks.GridHeatMap]:
    """GridHeatMap mark.

    Alignment: The tiles can be aligned so that the data matches either the
    start, the end or the midpoints of the tiles. This is controlled by the
    align attribute.

    Suppose the data passed is a m-by-n matrix. If the scale for the rows is
    Ordinal, then alignment is by default the mid points. For a non-ordinal
    scale, the data cannot be aligned to the mid points of the rectangles.

    If it is not ordinal, then two cases arise. If the number of rows passed
    is m, then align attribute can be used. If the number of rows passed
    is m+1, then the data are the boundaries of the m rectangles.

    If rows and columns are not passed, and scales for them are also
    not passed, then ordinal scales are generated for the rows and columns.

    Attributes
    ----------
    row_align: Enum(['start', 'end'])
        This is only valid if the number of entries in `row` exactly match the
        number of rows in `color` and the `row_scale` is not `OrdinalScale`.
        `start` aligns the row values passed to be aligned with the start
        of the tiles and `end` aligns the row values to the end of the tiles.
    column_align: Enum(['start', end'])
        This is only valid if the number of entries in `column` exactly
        match the number of columns in `color` and the `column_scale` is
        not `OrdinalScale`. `start` aligns the column values passed to
        be aligned with the start of the tiles and `end` aligns the
        column values to the end of the tiles.
    anchor_style: dict (default: {})
        Controls the style for the element which serves as the anchor during
        selection.
    display_format: string (default: None)
        format for displaying values. If None, then values are not displayed
    font_style: dict
        CSS style for the text of each cell

    Data Attributes

    color: numpy.ndarray or None (default: None)
        color of the data points (2d array). The number of elements in
        this array correspond to the number of cells created in the heatmap.
    row: numpy.ndarray or None (default: None)
        labels for the rows of the `color` array passed. The length of
        this can be no more than 1 away from the number of rows in `color`.
        This is a scaled attribute and can be used to affect the height of the
        cells as the entries of `row` can indicate the start or the end points
        of the cells. Refer to the property `row_align`.
        If this property is None, then a uniformly spaced grid is generated in
        the row direction.
    column: numpy.ndarray or None (default: None)
        labels for the columns of the `color` array passed. The length of
        this can be no more than 1 away from the number of columns in `color`
        This is a scaled attribute and can be used to affect the width of the
        cells as the entries of `column` can indicate the start or the
        end points of the cells. Refer to the property `column_align`.
        If this property is None, then a uniformly spaced grid is generated in
        the column direction.


    """
    ...


@implements(_GridHeatMap)
def GridHeatMap(**kwargs):

    widget_cls = bqplot.marks.GridHeatMap
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _GridHeatMap


def _HeatMap(
    apply_clip: bool = True,
    color: ndarray = None,
    display_legend: bool = False,
    enable_hover: bool = True,
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    null_color: str = "black",
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "color": {"dimension": "color"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    x: ndarray = None,
    y: ndarray = None,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_null_color: typing.Callable[[str], Any] = None,
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
) -> Element[bqplot.marks.HeatMap]:
    """HeatMap mark.


    Attributes
    ----------

    Data Attributes

    color: numpy.ndarray or None (default: None)
        color of the data points (2d array).
    x: numpy.ndarray or None (default: None)
        labels for the columns of the `color` array passed. The length of
        this has to be the number of columns in `color`.
        This is a scaled attribute.
    y: numpy.ndarray or None (default: None)
        labels for the rows of the `color` array passed. The length of this has
        to be the number of rows in `color`.
        This is a scaled attribute.


    """
    ...


@implements(_HeatMap)
def HeatMap(**kwargs):

    widget_cls = bqplot.marks.HeatMap
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _HeatMap


def _Hist(
    apply_clip: bool = True,
    bins: int = 10,
    colors: list = ["steelblue"],
    count: ndarray = np.array([]),
    display_legend: bool = False,
    enable_hover: bool = True,
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    midpoints: list = [],
    normalized: bool = False,
    opacities: list = [],
    preserve_domain: dict = {},
    sample: ndarray = np.array([]),
    scales: dict = {},
    scales_metadata: dict = {"sample": {"orientation": "horizontal", "dimension": "x"}, "count": {"orientation": "vertical", "dimension": "y"}},
    selected: ndarray = None,
    selected_style: dict = {},
    stroke: str = None,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_bins: typing.Callable[[int], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_count: typing.Callable[[ndarray], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_midpoints: typing.Callable[[list], Any] = None,
    on_normalized: typing.Callable[[bool], Any] = None,
    on_opacities: typing.Callable[[list], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_sample: typing.Callable[[ndarray], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_stroke: typing.Callable[[str], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.marks.Hist]:
    """Histogram mark.

    In the case of the Hist mark, scales for 'sample' and 'count' MUST be
    provided.

    Attributes
    ----------
    icon: string (class-level attribute)
        font-awesome icon for that mark
    name: string (class-level attribute)
        user-friendly name of the mark
    bins: nonnegative int (default: 10)
        number of bins in the histogram
    normalized: bool (default: False)
        Boolean attribute to return normalized values which
        sum to 1 or direct counts for the `count` attribute. The scale of
        `count` attribute is determined by the value of this flag.
    colors: list of colors (default: ['steelblue'])
        List of colors of the Histogram. If the list is shorter than the number
        of bins, the colors are reused.
    stroke: Color or None (default: None)
        Stroke color of the histogram
    opacities: list of floats (default: [])
        Opacity for the bins of the histogram. Defaults to 1 when the list
        is too short, or the element of the list is set to None.
    midpoints: list (default: [])
        midpoints of the bins of the histogram. It is a read-only attribute.

    Data Attributes

    sample: numpy.ndarray (default: [])
        sample of which the histogram must be computed.
    count: numpy.ndarray (read-only)
        number of sample points per bin. It is a read-only attribute.

    Notes
    -----
    The fields which can be passed to the default tooltip are:
        midpoint: mid-point of the bin related to the rectangle hovered on
        count: number of elements in the bin hovered on
        bin_start: start point of the bin
        bin-end: end point of the bin
        index: index of the bin


    """
    ...


@implements(_Hist)
def Hist(**kwargs):

    widget_cls = bqplot.marks.Hist
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Hist


def _Image(
    apply_clip: bool = True,
    display_legend: bool = False,
    enable_hover: bool = True,
    image: Element[ipywidgets.widgets.widget_media.Image] = None,
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    pixelated: bool = True,
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
    x: ndarray = np.array([0, 1]),
    y: ndarray = np.array([0, 1]),
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_image: typing.Callable[[Element[ipywidgets.widgets.widget_media.Image]], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_pixelated: typing.Callable[[bool], Any] = None,
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
) -> Element[bqplot.marks.Image]:
    """Image mark, based on the ipywidgets image

    If no scales are passed, uses the parent Figure scales.

    Attributes
    ----------
    image: Instance of ipywidgets.Image
        Image to be displayed

    Data Attributes

    x: tuple (default: (0, 1))
        abscissas of the left and right-hand side of the image
        in the format (x0, x1)
    y: tuple (default: (0, 1))
        ordinates of the bottom and top side of the image
        in the format (y0, y1)


    """
    ...


@implements(_Image)
def Image(**kwargs):

    widget_cls = bqplot.marks.Image
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Image


def _Interaction() -> Element[bqplot.interacts.Interaction]:
    """The base interaction class.

    An interaction is a mouse interaction layer for a figure that requires the
    capture of all mouse events on the plot area. A consequence is that one can
    allow only one interaction at any time on a figure.

    An interaction can be associated with features such as selection or
    manual change of specific mark. Although, they differ from the so called
    'mark interactions' in that they do not rely on knowing whether a specific
    element of the mark are hovered by the mouse.

    Attributes
    ----------
    types: dict (class-level attribute) representing interaction types
        A registry of existing interaction types.


    """
    ...


@implements(_Interaction)
def Interaction(**kwargs):

    widget_cls = bqplot.interacts.Interaction
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Interaction


def _Label(
    align: str = "start",
    apply_clip: bool = True,
    color: ndarray = None,
    colors: list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
    default_size: float = 16.0,
    display_legend: bool = False,
    drag_size: float = 1.0,
    enable_delete: bool = False,
    enable_hover: bool = True,
    enable_move: bool = False,
    font_unit: str = "px",
    font_weight: str = "bold",
    hovered_point: int = None,
    hovered_style: dict = {},
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    opacities: ndarray = np.array([1.0]),
    opacity: ndarray = None,
    preserve_domain: dict = {},
    restrict_x: bool = False,
    restrict_y: bool = False,
    rotate_angle: float = 0.0,
    rotation: ndarray = None,
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "color": {"dimension": "color"},
        "size": {"dimension": "size"},
        "opacity": {"dimension": "opacity"},
        "rotation": {"dimension": "rotation"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    size: ndarray = None,
    text: ndarray = None,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unhovered_style: dict = {},
    unselected_style: dict = {},
    update_on_move: bool = False,
    visible: bool = True,
    x: ndarray = np.array([]),
    x_offset: int = 0,
    y: ndarray = np.array([]),
    y_offset: int = 0,
    on_align: typing.Callable[[str], Any] = None,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_default_size: typing.Callable[[float], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_drag_size: typing.Callable[[float], Any] = None,
    on_enable_delete: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_enable_move: typing.Callable[[bool], Any] = None,
    on_font_unit: typing.Callable[[str], Any] = None,
    on_font_weight: typing.Callable[[str], Any] = None,
    on_hovered_point: typing.Callable[[int], Any] = None,
    on_hovered_style: typing.Callable[[dict], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_opacities: typing.Callable[[ndarray], Any] = None,
    on_opacity: typing.Callable[[ndarray], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_restrict_x: typing.Callable[[bool], Any] = None,
    on_restrict_y: typing.Callable[[bool], Any] = None,
    on_rotate_angle: typing.Callable[[float], Any] = None,
    on_rotation: typing.Callable[[ndarray], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_size: typing.Callable[[ndarray], Any] = None,
    on_text: typing.Callable[[ndarray], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unhovered_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_update_on_move: typing.Callable[[bool], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_x_offset: typing.Callable[[int], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
    on_y_offset: typing.Callable[[int], Any] = None,
) -> Element[bqplot.marks.Label]:
    """Label mark.

    Attributes
    ----------
    x_offset: int (default: 0)
        horizontal offset in pixels from the stated x location
    y_offset: int (default: 0)
        vertical offset in pixels from the stated y location
    text: string (default: '')
        text to be displayed
    default_size: string (default: '14px')
        font size in px, em or ex
    font_weight: {'bold', 'normal', 'bolder'}
        font weight of the caption
    drag_size: nonnegative float (default: 1.)
        Ratio of the size of the dragged label font size to the default
        label font size.
    align: {'start', 'middle', 'end'}
        alignment of the text with respect to the provided location
        enable_move: Bool (default: False)
        Enable the label to be moved by dragging. Refer to restrict_x,
        restrict_y for more options.
    restrict_x: bool (default: False)
        Restricts movement of the label to only along the x axis. This is valid
        only when enable_move is set to True. If both restrict_x and restrict_y
        are set to True, the label cannot be moved.
    restrict_y: bool (default: False)
        Restricts movement of the label to only along the y axis. This is valid
        only when enable_move is set to True. If both restrict_x and restrict_y
        are set to True, the label cannot be moved.

    Data Attributes

    x: numpy.ndarray (default: [])
        horizontal position of the labels, in data coordinates or in
        figure coordinates
    y: numpy.ndarray (default: [])
        vertical position of the labels, in data coordinates or in
        figure coordinates
    color: numpy.ndarray or None (default: None)
        label colors
    size: numpy.ndarray or None (default: None)
        label sizes
    rotation: numpy.ndarray or None (default: None)
        label rotations
    opacity: numpy.ndarray or None (default: None)
        label opacities



    """
    ...


@implements(_Label)
def Label(**kwargs):

    widget_cls = bqplot.marks.Label
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Label


def _LinearScale(
    allow_padding: bool = True,
    max: float = None,
    mid_range: float = 0.8,
    min: float = None,
    min_range: float = 0.6,
    reverse: bool = False,
    stabilized: bool = False,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_mid_range: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_min_range: typing.Callable[[float], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_stabilized: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.scales.LinearScale]:
    """A linear scale.

    An affine mapping from a numerical domain to a numerical range.

    Attributes
    ----------
    min: float or None (default: None)
        if not None, min is the minimal value of the domain
    max: float or None (default: None)
        if not None, max is the maximal value of the domain
    rtype: string (class-level attribute)
        This attribute should not be modified. The range type of a linear
        scale is numerical.
    dtype: type (class-level attribute)
        the associated data type / domain type
    precedence: int (class-level attribute, default_value=2)
        attribute used to determine which scale takes precedence in cases when
        two or more scales have the same rtype and dtype.
        default_value is 2 because for the same range and domain types,
        LinearScale should take precedence.
    stabilized: bool (default: False)
        if set to False, the domain of the scale is tied to the data range
        if set to True, the domain of the scale is updated only when
        the data range is beyond certain thresholds, given by the attributes
        mid_range and min_range.
    mid_range: float (default: 0.8)
        Proportion of the range that is spanned initially.
        Used only if stabilized is True.
    min_range: float (default: 0.6)
        Minimum proportion of the range that should be spanned by the data.
        If the data span falls beneath that level, the scale is reset.
        min_range must be <= mid_range.
        Used only if stabilized is True.


    """
    ...


@implements(_LinearScale)
def LinearScale(**kwargs):

    widget_cls = bqplot.scales.LinearScale
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _LinearScale


def _Lines(
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
) -> Element[bqplot.marks.Lines]:
    """Lines mark.

    In the case of the Lines mark, scales for 'x' and 'y' MUST be provided.

    Attributes
    ----------
    icon: string (class-level attribute)
        Font-awesome icon for the respective mark
    name: string (class-level attribute)
        User-friendly name of the mark
    colors: list of colors (default: CATEGORY10)
        List of colors of the Lines. If the list is shorter than the number
        of lines, the colors are reused.
    close_path: bool (default: False)
        Whether to close the paths or not.
    fill: {'none', 'bottom', 'top', 'inside', 'between'}
        Fill in the area defined by the curves
    fill_colors: list of colors (default: [])
        Fill colors for the areas. Defaults to stroke-colors when no
        color provided
    opacities: list of floats (default: [])
        Opacity for the  lines and patches. Defaults to 1 when the list is too
        short, or the element of the list is set to None.
    fill_opacities: list of floats (default: [])
        Opacity for the areas. Defaults to 1 when the list is too
        short, or the element of the list is set to None.
    stroke_width: float (default: 2)
        Stroke width of the Lines
    labels_visibility: {'none', 'label'}
        Visibility of the curve labels
    curves_subset: list of integers or None (default: [])
        If set to None, all the lines are displayed. Otherwise, only the items
        in the list will have full opacity, while others will be faded.
    line_style: {'solid', 'dashed', 'dotted', 'dash_dotted'}
        Line style.
    interpolation: {'linear', 'basis', 'cardinal', 'monotone'}
        Interpolation scheme used for interpolation between the data points
        provided. Please refer to the svg interpolate documentation for details
        about the different interpolation schemes.
    marker: {'circle', 'cross', 'diamond', 'square', 'triangle-down', 'triangle-up', 'arrow', 'rectangle', 'ellipse'}
        Marker shape
    marker_size: nonnegative int (default: 64)
        Default marker size in pixels

    Data Attributes

    x: numpy.ndarray (default: [])
        abscissas of the data points (1d or 2d array)
    y: numpy.ndarray (default: [])
        ordinates of the data points (1d or 2d array)
    color: numpy.ndarray (default: None)
        colors of the different lines based on data. If it is [], then the
        colors from the colors attribute are used. Each line has a single color
        and if the size of colors is less than the number of lines, the
        remaining lines are given the default colors.

    Notes
    -----
    The fields which can be passed to the default tooltip are:
        name: label of the line
        index: index of the line being hovered on
        color: data attribute for the color of the line
    The following are the events which can trigger interactions:
        click: left click of the mouse
        hover: mouse-over an element
    The following are the interactions which can be linked to the above events:
        tooltip: display tooltip


    """
    ...


@implements(_Lines)
def Lines(**kwargs):

    widget_cls = bqplot.marks.Lines
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Lines


def _LogScale(
    allow_padding: bool = True,
    max: float = None,
    min: float = None,
    reverse: bool = False,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.scales.LogScale]:
    """A log scale.

    A logarithmic mapping from a numerical domain to a numerical range.

    Attributes
    ----------
    min: float or None (default: None)
        if not None, min is the minimal value of the domain
    max: float or None (default: None)
        if not None, max is the maximal value of the domain
    rtype: string (class-level attribute)
        This attribute should not be modified by the user.
        The range type of a linear scale is numerical.
    dtype: type (class-level attribute)
        the associated data type / domain type


    """
    ...


@implements(_LogScale)
def LogScale(**kwargs):

    widget_cls = bqplot.scales.LogScale
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _LogScale


def _Map(
    apply_clip: bool = True,
    color: dict = {},
    colors: dict = {},
    display_legend: bool = False,
    enable_hover: bool = True,
    hover_highlight: bool = True,
    hovered_styles: dict = {"hovered_fill": "Orange", "hovered_stroke": None, "hovered_stroke_width": 2.0},
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    map_data: dict = bqplot.Map.map_data.default,
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {"color": {"dimension": "color"}, "projection": {"dimension": "geo"}},
    selected: ndarray = None,
    selected_style: dict = {},
    selected_styles: dict = {"selected_fill": "Red", "selected_stroke": None, "selected_stroke_width": 2.0},
    stroke_color: str = None,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[dict], Any] = None,
    on_colors: typing.Callable[[dict], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_hover_highlight: typing.Callable[[bool], Any] = None,
    on_hovered_styles: typing.Callable[[dict], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_map_data: typing.Callable[[dict], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_selected_styles: typing.Callable[[dict], Any] = None,
    on_stroke_color: typing.Callable[[str], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.marks.Map]:
    """Map mark.

    Attributes
    ----------
    colors: Dict (default: {})
        default colors for items of the map when no color data is passed.
        The dictionary should be indexed by the id of the element and have
        the corresponding colors as values. The key `default_color`
        controls the items for which no color is specified.
    selected_styles: Dict (default: {'selected_fill': 'Red',
    'selected_stroke': None, 'selected_stroke_width': 2.0})
        Dictionary containing the styles for selected subunits
    hovered_styles: Dict (default: {'hovered_fill': 'Orange',
    'hovered_stroke': None, 'hovered_stroke_width': 2.0})
        Dictionary containing the styles for hovered subunits
    hover_highlight: bool (default: True)
        boolean to control if the map should be aware of which country is being
        hovered on.
    map_data: dict (default: topo_load("map_data/WorldMap.json"))
        a topojson-formatted dictionary with the objects to map under the key
        'subunits'.

    Data Attributes

    color: Dict or None (default: None)
        dictionary containing the data associated with every country for the
        color scale


    """
    ...


@implements(_Map)
def Map(**kwargs):

    widget_cls = bqplot.marks.Map
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Map


def _Mark(
    apply_clip: bool = True,
    display_legend: bool = False,
    enable_hover: bool = True,
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {},
    selected: ndarray = None,
    selected_style: dict = {},
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
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
) -> Element[bqplot.marks.Mark]:
    """The base mark class.

    Traitlet mark attributes may be decorated with metadata.

    **Data Attribute Decoration**

    Data attributes are decorated with the following values:

    scaled: bool
        Indicates whether the considered attribute is a data attribute which
        must be associated with a scale in order to be taken into account.
    rtype: string
        Range type of the associated scale.
    atype: string
        Key in bqplot's axis registry of the recommended axis type to represent
        this scale. When not specified, the default is 'bqplot.Axis'.

    Attributes
    ----------
    display_name: string
        Holds a user-friendly name for the trait attribute.
    mark_types: dict (class-level attribute)
        A registry of existing mark types.
    scales: Dict of scales (default: {})
        A dictionary of scales holding scales for each data attribute.
        - If a mark holds a scaled attribute named 'x', the scales dictionary
        must have a corresponding scale for the key 'x'.
        - The scale's range type should be equal to the scaled attribute's
        range type (rtype).
    scales_metadata: Dict (default: {})
        A dictionary of dictionaries holding metadata on the way scales are
        used by the mark. For example, a linear scale may be used to count
        pixels horizontally or vertically. The content of this dictionary
        may change dynamically. It is an instance-level attribute.
    preserve_domain: dict (default: {})
        Indicates if this mark affects the domain(s) of the specified scale(s).
        The keys of this dictionary are the same as the ones of the "scales"
        attribute, and values are boolean. If a key is missing, it is
        considered as False.
    display_legend: bool (default: False)
        Display toggle for the mark legend in the general figure legend
    labels: list of unicode strings (default: [])
        Labels of the items of the mark. This attribute has different meanings
        depending on the type of mark.
    apply_clip: bool (default: True)
        Indicates whether the items that are beyond the limits of the chart
        should be clipped.
    visible: bool (default: True)
        Visibility toggle for the mark.
    selected_style: dict (default: {})
        CSS style to be applied to selected items in the mark.
    unselected_style: dict (default: {})
        CSS style to be applied to items that are not selected in the mark,
        when a selection exists.
    selected: list of integers or None (default: None)
        Indices of the selected items in the mark.
    tooltip: DOMWidget or None (default: None)
        Widget to be displayed as tooltip when elements of the scatter are
        hovered on
    tooltip_style: Dictionary (default: {'opacity': 0.9})
        Styles to be applied to the tooltip widget
    enable_hover: Bool (default: True)
        Boolean attribute to control the hover interaction for the scatter. If
        this is false, the on_hover custom mssg is not sent back to the python
        side
    interactions: Dictionary (default: {'hover': 'tooltip'})
        Dictionary listing the different interactions for each mark. The key is
        the event which triggers the interaction and the value is the kind of
        interactions. Keys and values can only take strings from separate enums
        for each mark.
    tooltip_location : {'mouse', 'center'} (default: 'mouse')
        Enum specifying the location of the tooltip. 'mouse' places the tooltip
        at the location of the mouse when the tooltip is activated and 'center'
        places the tooltip at the center of the figure. If tooltip is linked to
        a click event, 'mouse' places the tooltip at the location of the click
        that triggered the tooltip to be visible.


    """
    ...


@implements(_Mark)
def Mark(**kwargs):

    widget_cls = bqplot.marks.Mark
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Mark


def _Mercator(
    allow_padding: bool = True,
    center: tuple = (0, 60),
    reverse: bool = False,
    rotate: tuple = (0, 0),
    scale_factor: float = 190,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_center: typing.Callable[[tuple], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_rotate: typing.Callable[[tuple], Any] = None,
    on_scale_factor: typing.Callable[[float], Any] = None,
) -> Element[bqplot.scales.Mercator]:
    """A geographical projection scale commonly used for world maps.

    The Mercator projection is a cylindrical map projection which ensures that
    any course of constant bearing is a straight line.

    Attributes
    ----------
    scale_factor: float (default: 190)
        Specifies the scale value for the projection
    center: tuple (default: (0, 60))
        Specifies the longitude and latitude where the map is centered.
    rotate: tuple (default: (0, 0))
        Degree of rotation in each axis.
    rtype: (Number, Number) (class-level attribute)
        This attribute should not be modified. The range type of a geo
        scale is a tuple.
    dtype: type (class-level attribute)
        the associated data type / domain type


    """
    ...


@implements(_Mercator)
def Mercator(**kwargs):

    widget_cls = bqplot.scales.Mercator
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Mercator


def _OHLC(
    apply_clip: bool = True,
    colors: list = ["green", "red"],
    display_legend: bool = False,
    enable_hover: bool = True,
    format: str = "ohlc",
    interactions: dict = {"hover": "tooltip"},
    labels: list = [],
    marker: str = "candle",
    opacities: list = [],
    preserve_domain: dict = {},
    scales: dict = {},
    scales_metadata: dict = {"x": {"orientation": "horizontal", "dimension": "x"}, "y": {"orientation": "vertical", "dimension": "y"}},
    selected: ndarray = None,
    selected_style: dict = {},
    stroke: str = None,
    stroke_width: float = 1.0,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    visible: bool = True,
    x: ndarray = np.array([]),
    y: ndarray = np.array([[]]),
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_format: typing.Callable[[str], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_marker: typing.Callable[[str], Any] = None,
    on_opacities: typing.Callable[[list], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_stroke: typing.Callable[[str], Any] = None,
    on_stroke_width: typing.Callable[[float], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot.marks.OHLC]:
    """Open/High/Low/Close marks.

    Attributes
    ----------
    icon: string (class-level attribute)
        font-awesome icon for that mark
    name: string (class-level attribute)
        user-friendly name of the mark
    marker: {'candle', 'bar'}
        marker type
    stroke: color (default: None)
        stroke color of the marker
    stroke_width: float (default: 1.0)
        stroke width of the marker
    colors: List of colors (default: ['limegreen', 'red'])
        fill colors for the markers (up/down)
    opacities: list of floats (default: [])
        Opacities for the markers of the OHLC mark. Defaults to 1 when
        the list is too short, or the element of the list is set to None.
    format: string (default: 'ohlc')
        description of y data being passed
        supports all permutations of the strings 'ohlc', 'oc', and 'hl'

    Data Attributes

    x: numpy.ndarray
        abscissas of the data points (1d array)
    y: numpy.ndarrays
        Open/High/Low/Close ordinates of the data points (2d array)

    Notes
    -----
    The fields which can be passed to the default tooltip are:
        x: the x value associated with the bar/candle
        open: open value for the bar/candle
        high: high value for the bar/candle
        low: low value for the bar/candle
        close: close value for the bar/candle
        index: index of the bar/candle being hovered on


    """
    ...


@implements(_OHLC)
def OHLC(**kwargs):

    widget_cls = bqplot.marks.OHLC
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _OHLC


def _OrdinalColorScale(
    allow_padding: bool = True,
    colors: list = [],
    domain: list = [],
    extrapolation: str = "constant",
    max: float = None,
    mid: float = None,
    min: float = None,
    reverse: bool = False,
    scale_type: str = "linear",
    scheme: str = "RdYlGn",
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_domain: typing.Callable[[list], Any] = None,
    on_extrapolation: typing.Callable[[str], Any] = None,
    on_max: typing.Callable[[float], Any] = None,
    on_mid: typing.Callable[[float], Any] = None,
    on_min: typing.Callable[[float], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_scale_type: typing.Callable[[str], Any] = None,
    on_scheme: typing.Callable[[str], Any] = None,
) -> Element[bqplot.scales.OrdinalColorScale]:
    """An ordinal color scale.

    A mapping from a discrete set of values to colors.

    Attributes
    ----------
    domain: list (default: [])
        The discrete values mapped by the ordinal scales.
    rtype: string (class-level attribute)
        This attribute should not be modified by the user.
        The range type of a color scale is 'color'.
    dtype: type (class-level attribute)
        the associated data type / domain type


    """
    ...


@implements(_OrdinalColorScale)
def OrdinalColorScale(**kwargs):

    widget_cls = bqplot.scales.OrdinalColorScale
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _OrdinalColorScale


def _OrdinalScale(
    allow_padding: bool = True,
    domain: list = [],
    reverse: bool = False,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_domain: typing.Callable[[list], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.scales.OrdinalScale]:
    """An ordinal scale.

    A mapping from a discrete set of values to a numerical range.

    Attributes
    ----------
    domain: list (default: [])
        The discrete values mapped by the ordinal scale
    rtype: string (class-level attribute)
        This attribute should not be modified by the user.
        The range type of a linear scale is numerical.
    dtype: type (class-level attribute)
        the associated data type / domain type


    """
    ...


@implements(_OrdinalScale)
def OrdinalScale(**kwargs):

    widget_cls = bqplot.scales.OrdinalScale
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _OrdinalScale


def _Orthographic(
    allow_padding: bool = True,
    center: tuple = (0, 60),
    clip_angle: float = 90.0,
    precision: float = 0.1,
    reverse: bool = False,
    rotate: tuple = (0, 0),
    scale_factor: float = 145.0,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_center: typing.Callable[[tuple], Any] = None,
    on_clip_angle: typing.Callable[[float], Any] = None,
    on_precision: typing.Callable[[float], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_rotate: typing.Callable[[tuple], Any] = None,
    on_scale_factor: typing.Callable[[float], Any] = None,
) -> Element[bqplot.scales.Orthographic]:
    """A perspective projection that depicts a hemisphere as it appears from
    outer space.

    The projection is neither equal-area nor conformal.

    Attributes
    ----------
    scale_factor: float (default: 145)
       Specifies the scale value for the projection
    center: tuple (default: (0, 60))
        Specifies the longitude and latitude where the map is centered.
    rotate: tuple (default: (96, 0))
        Degree of rotation in each axis.
    clip_angle: float (default: 90.)
        Specifies the clipping circle radius to the specified angle in degrees.
    precision: float (default: 0.1)
        Specifies the threshold for the projections adaptive resampling to the
        specified value in pixels.


    """
    ...


@implements(_Orthographic)
def Orthographic(**kwargs):

    widget_cls = bqplot.scales.Orthographic
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Orthographic


def _PanZoom(
    allow_pan: bool = True,
    allow_zoom: bool = True,
    scales: dict = {},
    on_allow_pan: typing.Callable[[bool], Any] = None,
    on_allow_zoom: typing.Callable[[bool], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
) -> Element[bqplot.interacts.PanZoom]:
    """An interaction to pan and zoom wrt scales.

    Attributes
    ----------
    allow_pan: bool (default: True)
        Toggle the ability to pan.
    allow_zoom: bool (default: True)
        Toggle the ability to zoom.
    scales: Dictionary of lists of Scales (default: {})
        Dictionary with keys such as 'x' and 'y' and values being the scales in
        the corresponding direction (dimensions) which should be panned or
        zoomed.


    """
    ...


@implements(_PanZoom)
def PanZoom(**kwargs):

    widget_cls = bqplot.interacts.PanZoom
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _PanZoom


def _Pie(
    apply_clip: bool = True,
    color: ndarray = None,
    colors: list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
    display_labels: str = "inside",
    display_legend: bool = False,
    display_values: bool = False,
    enable_hover: bool = True,
    end_angle: float = 360.0,
    font_size: str = "12px",
    font_weight: str = "normal",
    inner_radius: float = 0.1,
    interactions: dict = {"hover": "tooltip"},
    label_color: str = None,
    labels: list = [],
    opacities: list = [],
    preserve_domain: dict = {},
    radius: float = 180.0,
    scales: dict = {},
    scales_metadata: dict = {"color": {"dimension": "color"}},
    selected: ndarray = None,
    selected_style: dict = {},
    sizes: ndarray = np.array([]),
    sort: bool = False,
    start_angle: float = 0.0,
    stroke: str = None,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unselected_style: dict = {},
    values_format: str = ".1f",
    visible: bool = True,
    x: typing.Union[float, datetime.datetime, str] = 0.5,
    y: typing.Union[float, datetime.datetime, str] = 0.5,
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_display_labels: typing.Callable[[str], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_display_values: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_end_angle: typing.Callable[[float], Any] = None,
    on_font_size: typing.Callable[[str], Any] = None,
    on_font_weight: typing.Callable[[str], Any] = None,
    on_inner_radius: typing.Callable[[float], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_label_color: typing.Callable[[str], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_opacities: typing.Callable[[list], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_radius: typing.Callable[[float], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_sizes: typing.Callable[[ndarray], Any] = None,
    on_sort: typing.Callable[[bool], Any] = None,
    on_start_angle: typing.Callable[[float], Any] = None,
    on_stroke: typing.Callable[[str], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_values_format: typing.Callable[[str], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[typing.Union[float, datetime.datetime, str]], Any] = None,
    on_y: typing.Callable[[typing.Union[float, datetime.datetime, str]], Any] = None,
) -> Element[bqplot.marks.Pie]:
    """Piechart mark.

    Attributes
    ----------
    colors: list of colors (default: CATEGORY10)
        list of colors for the slices.
    stroke: color (default: 'white')
        stroke color for the marker
    opacities: list of floats (default: [])
        Opacities for the slices of the Pie mark. Defaults to 1 when the list
        is too short, or the element of the list is set to None.
    sort: bool (default: False)
        sort the pie slices by descending sizes
    x: Float (default: 0.5) or Date
        horizontal position of the pie center, in data coordinates or in figure
        coordinates
    y: Float (default: 0.5)
        vertical y position of the pie center, in data coordinates or in figure
        coordinates
    radius: Float
        radius of the pie, in pixels
    inner_radius: Float
        inner radius of the pie, in pixels
    start_angle: Float (default: 0.0)
        start angle of the pie (from top), in degrees
    end_angle: Float (default: 360.0)
        end angle of the pie (from top), in degrees
    display_labels: {'none', 'inside', 'outside'} (default: 'inside')
        label display options
    display_values: bool (default: False)
        if True show values along with labels
    values_format: string (default: '.2f')
        format for displaying values
    label_color: Color or None (default: None)
        color of the labels
    font_size: string (default: '14px')
        label font size in px, em or ex
    font_weight: {'bold', 'normal', 'bolder'} (default: 'normal')
        label font weight

    Data Attributes

    sizes: numpy.ndarray (default: [])
        proportions of the pie slices
    color: numpy.ndarray or None (default: None)
        color of the data points. Defaults to colors when not provided.

    Notes
    -----
    The fields which can be passed to the default tooltip are:
        : the x value associated with the bar/candle
        open: open value for the bar/candle
        high: high value for the bar/candle
        low: low value for the bar/candle
        close: close value for the bar/candle
        index: index of the bar/candle being hovered on


    """
    ...


@implements(_Pie)
def Pie(**kwargs):

    widget_cls = bqplot.marks.Pie
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Pie


def _Scale(
    allow_padding: bool = True,
    reverse: bool = False,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.scales.Scale]:
    """The base scale class.

    Scale objects represent a mapping between data (the domain) and a visual
    quantity (The range).

    Attributes
    ----------
    scale_types: dict (class-level attribute)
        A registry of existing scale types.
    domain_class: type (default: Float)
        traitlet type used to validate values in of the domain of the scale.
    reverse: bool (default: False)
        whether the scale should be reversed.
    allow_padding: bool (default: True)
        indicates whether figures are allowed to add data padding to this scale
        or not.
    precedence: int (class-level attribute)
        attribute used to determine which scale takes precedence in cases when
        two or more scales have the same rtype and dtype.


    """
    ...


@implements(_Scale)
def Scale(**kwargs):

    widget_cls = bqplot.scales.Scale
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Scale


def _Scatter(
    apply_clip: bool = True,
    color: ndarray = None,
    colors: list = ["steelblue"],
    default_size: int = 64,
    default_skew: float = 0.5,
    display_legend: bool = False,
    display_names: bool = True,
    drag_color: str = None,
    drag_size: float = 5.0,
    enable_delete: bool = False,
    enable_hover: bool = True,
    enable_move: bool = False,
    fill: bool = True,
    hovered_point: int = None,
    hovered_style: dict = {},
    interactions: dict = {"hover": "tooltip"},
    label_display_horizontal_offset: float = 0.0,
    label_display_vertical_offset: float = 0.0,
    labels: list = [],
    marker: str = "circle",
    names: ndarray = None,
    names_unique: bool = True,
    opacities: ndarray = np.array([1.0]),
    opacity: ndarray = None,
    preserve_domain: dict = {},
    restrict_x: bool = False,
    restrict_y: bool = False,
    rotation: ndarray = None,
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "color": {"dimension": "color"},
        "size": {"dimension": "size"},
        "opacity": {"dimension": "opacity"},
        "rotation": {"dimension": "rotation"},
        "skew": {"dimension": "skew"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    size: ndarray = None,
    skew: ndarray = None,
    stroke: str = None,
    stroke_width: float = 1.5,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unhovered_style: dict = {},
    unselected_style: dict = {},
    update_on_move: bool = False,
    visible: bool = True,
    x: ndarray = np.array([]),
    y: ndarray = np.array([]),
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_default_size: typing.Callable[[int], Any] = None,
    on_default_skew: typing.Callable[[float], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_display_names: typing.Callable[[bool], Any] = None,
    on_drag_color: typing.Callable[[str], Any] = None,
    on_drag_size: typing.Callable[[float], Any] = None,
    on_enable_delete: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_enable_move: typing.Callable[[bool], Any] = None,
    on_fill: typing.Callable[[bool], Any] = None,
    on_hovered_point: typing.Callable[[int], Any] = None,
    on_hovered_style: typing.Callable[[dict], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_label_display_horizontal_offset: typing.Callable[[float], Any] = None,
    on_label_display_vertical_offset: typing.Callable[[float], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_marker: typing.Callable[[str], Any] = None,
    on_names: typing.Callable[[ndarray], Any] = None,
    on_names_unique: typing.Callable[[bool], Any] = None,
    on_opacities: typing.Callable[[ndarray], Any] = None,
    on_opacity: typing.Callable[[ndarray], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_restrict_x: typing.Callable[[bool], Any] = None,
    on_restrict_y: typing.Callable[[bool], Any] = None,
    on_rotation: typing.Callable[[ndarray], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_size: typing.Callable[[ndarray], Any] = None,
    on_skew: typing.Callable[[ndarray], Any] = None,
    on_stroke: typing.Callable[[str], Any] = None,
    on_stroke_width: typing.Callable[[float], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unhovered_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_update_on_move: typing.Callable[[bool], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot.marks.Scatter]:
    """Scatter mark.

    In the case of the Scatter mark, scales for 'x' and 'y' MUST be provided.
    The scales of other data attributes are optional. In the case where another
    data attribute than 'x' or 'y' is provided but the corresponding scale is
    missing, the data attribute is ignored.

    Attributes
    ----------
    icon: string (class-level attribute)
        Font-awesome icon for that mark
    name: string (class-level attribute)
        User-friendly name of the mark
    marker: {'circle', 'cross', 'diamond', 'square', 'triangle-down', 'triangle-up', 'arrow', 'rectangle', 'ellipse'}
        Marker shape
    colors: list of colors (default: ['steelblue'])
        List of colors of the markers. If the list is shorter than the number
        of points, the colors are reused.
    default_colors: Deprecated
        Same as `colors`, deprecated as of version 0.8.4
    fill: Bool (default: True)
        Whether to fill the markers or not
    stroke: Color or None (default: None)
        Stroke color of the marker
    stroke_width: Float (default: 1.5)
        Stroke width of the marker
    opacities: list of floats (default: [1.0])
        Default opacities of the markers. If the list is shorter than
        the number
        of points, the opacities are reused.
    default_skew: float (default: 0.5)
        Default skew of the marker.
        This number is validated to be between 0 and 1.
    default_size: nonnegative int (default: 64)
        Default marker size in pixel.
        If size data is provided with a scale, default_size stands for the
        maximal marker size (i.e. the maximum value for the 'size' scale range)
    drag_size: nonnegative float (default: 5.)
        Ratio of the size of the dragged scatter size to the default
        scatter size.
    names: numpy.ndarray (default: None)
        Labels for the points of the chart
    display_names: bool (default: True)
        Controls whether names are displayed for points in the scatter
    label_display_horizontal_offset: float (default: None)
        Adds an offset, in pixels, to the horizontal positioning of the 'names'
        label above each data point
    label_display_vertical_offset: float (default: None)
        Adds an offset, in pixels, to the vertical positioning of the 'names'
        label above each data point
    enable_move: bool (default: False)
        Controls whether points can be moved by dragging. Refer to restrict_x,
        restrict_y for more options.
    restrict_x: bool (default: False)
        Restricts movement of the point to only along the x axis. This is valid
        only when enable_move is set to True. If both restrict_x and restrict_y
        are set to True, the point cannot be moved.
    restrict_y: bool (default: False)
        Restricts movement of the point to only along the y axis. This is valid
        only when enable_move is set to True. If both restrict_x and restrict_y
        are set to True, the point cannot be moved.


    Data Attributes

    x: numpy.ndarray (default: [])
        abscissas of the data points (1d array)
    y: numpy.ndarray (default: [])
        ordinates of the data points (1d array)
    color: numpy.ndarray or None (default: None)
        color of the data points (1d array). Defaults to default_color when not
        provided or when a value is NaN
    opacity: numpy.ndarray or None (default: None)
        opacity of the data points (1d array). Defaults to default_opacity when
        not provided or when a value is NaN
    size: numpy.ndarray or None (default: None)
        size of the data points. Defaults to default_size when not provided or
        when a value is NaN
    skew: numpy.ndarray or None (default: None)
        skewness of the markers representing the data points. Defaults to
        default_skew when not provided or when a value is NaN
    rotation: numpy.ndarray or None (default: None)
        orientation of the markers representing the data points.
        The rotation scale's range is [0, 180]
        Defaults to 0 when not provided or when a value is NaN.

    Notes
    -----
    The fields which can be passed to the default tooltip are:
        All the data attributes
        index: index of the marker being hovered on
    The following are the events which can trigger interactions:
        click: left click of the mouse
        hover: mouse-over an element
    The following are the interactions which can be linked to the above events:
        tooltip: display tooltip
        add: add new points to the scatter (can only linked to click)


    """
    ...


@implements(_Scatter)
def Scatter(**kwargs):

    widget_cls = bqplot.marks.Scatter
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Scatter


def _ScatterGL(
    apply_clip: bool = True,
    color: ndarray = None,
    colors: list = ["steelblue"],
    default_size: int = 64,
    default_skew: float = 0.5,
    display_legend: bool = False,
    display_names: bool = True,
    drag_color: str = None,
    drag_size: float = 5.0,
    enable_delete: bool = False,
    enable_hover: bool = True,
    enable_move: bool = False,
    fill: bool = True,
    hovered_point: int = None,
    hovered_style: dict = {},
    interactions: dict = {"hover": "tooltip"},
    label_display_horizontal_offset: float = 0.0,
    label_display_vertical_offset: float = 0.0,
    labels: list = [],
    marker: str = "circle",
    names: ndarray = None,
    names_unique: bool = True,
    opacities: ndarray = np.array([1.0]),
    opacity: ndarray = None,
    preserve_domain: dict = {},
    restrict_x: bool = False,
    restrict_y: bool = False,
    rotation: ndarray = None,
    scales: dict = {},
    scales_metadata: dict = {
        "x": {"orientation": "horizontal", "dimension": "x"},
        "y": {"orientation": "vertical", "dimension": "y"},
        "color": {"dimension": "color"},
        "size": {"dimension": "size"},
        "opacity": {"dimension": "opacity"},
        "rotation": {"dimension": "rotation"},
        "skew": {"dimension": "skew"},
    },
    selected: ndarray = None,
    selected_style: dict = {},
    size: ndarray = None,
    skew: ndarray = None,
    stroke: str = None,
    stroke_width: float = 1.5,
    tooltip: Element[ipywidgets.widgets.domwidget.DOMWidget] = None,
    tooltip_location: str = "mouse",
    tooltip_style: dict = {"opacity": 0.9},
    unhovered_style: dict = {},
    unselected_style: dict = {},
    update_on_move: bool = False,
    visible: bool = True,
    x: ndarray = np.array([]),
    y: ndarray = np.array([]),
    on_apply_clip: typing.Callable[[bool], Any] = None,
    on_color: typing.Callable[[ndarray], Any] = None,
    on_colors: typing.Callable[[list], Any] = None,
    on_default_size: typing.Callable[[int], Any] = None,
    on_default_skew: typing.Callable[[float], Any] = None,
    on_display_legend: typing.Callable[[bool], Any] = None,
    on_display_names: typing.Callable[[bool], Any] = None,
    on_drag_color: typing.Callable[[str], Any] = None,
    on_drag_size: typing.Callable[[float], Any] = None,
    on_enable_delete: typing.Callable[[bool], Any] = None,
    on_enable_hover: typing.Callable[[bool], Any] = None,
    on_enable_move: typing.Callable[[bool], Any] = None,
    on_fill: typing.Callable[[bool], Any] = None,
    on_hovered_point: typing.Callable[[int], Any] = None,
    on_hovered_style: typing.Callable[[dict], Any] = None,
    on_interactions: typing.Callable[[dict], Any] = None,
    on_label_display_horizontal_offset: typing.Callable[[float], Any] = None,
    on_label_display_vertical_offset: typing.Callable[[float], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_marker: typing.Callable[[str], Any] = None,
    on_names: typing.Callable[[ndarray], Any] = None,
    on_names_unique: typing.Callable[[bool], Any] = None,
    on_opacities: typing.Callable[[ndarray], Any] = None,
    on_opacity: typing.Callable[[ndarray], Any] = None,
    on_preserve_domain: typing.Callable[[dict], Any] = None,
    on_restrict_x: typing.Callable[[bool], Any] = None,
    on_restrict_y: typing.Callable[[bool], Any] = None,
    on_rotation: typing.Callable[[ndarray], Any] = None,
    on_scales: typing.Callable[[dict], Any] = None,
    on_scales_metadata: typing.Callable[[dict], Any] = None,
    on_selected: typing.Callable[[ndarray], Any] = None,
    on_selected_style: typing.Callable[[dict], Any] = None,
    on_size: typing.Callable[[ndarray], Any] = None,
    on_skew: typing.Callable[[ndarray], Any] = None,
    on_stroke: typing.Callable[[str], Any] = None,
    on_stroke_width: typing.Callable[[float], Any] = None,
    on_tooltip: typing.Callable[[Element[ipywidgets.widgets.domwidget.DOMWidget]], Any] = None,
    on_tooltip_location: typing.Callable[[str], Any] = None,
    on_tooltip_style: typing.Callable[[dict], Any] = None,
    on_unhovered_style: typing.Callable[[dict], Any] = None,
    on_unselected_style: typing.Callable[[dict], Any] = None,
    on_update_on_move: typing.Callable[[bool], Any] = None,
    on_visible: typing.Callable[[bool], Any] = None,
    on_x: typing.Callable[[ndarray], Any] = None,
    on_y: typing.Callable[[ndarray], Any] = None,
) -> Element[bqplot.marks.ScatterGL]:
    """ """
    ...


@implements(_ScatterGL)
def ScatterGL(**kwargs):

    widget_cls = bqplot.marks.ScatterGL
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _ScatterGL


def _Stereographic(
    allow_padding: bool = True,
    center: tuple = (0, 60),
    clip_angle: float = 179.9999,
    precision: float = 0.1,
    reverse: bool = False,
    rotate: tuple = (96, 0),
    scale_factor: float = 145.0,
    on_allow_padding: typing.Callable[[bool], Any] = None,
    on_center: typing.Callable[[tuple], Any] = None,
    on_clip_angle: typing.Callable[[float], Any] = None,
    on_precision: typing.Callable[[float], Any] = None,
    on_reverse: typing.Callable[[bool], Any] = None,
    on_rotate: typing.Callable[[tuple], Any] = None,
    on_scale_factor: typing.Callable[[float], Any] = None,
) -> Element[bqplot.scales.Stereographic]:
    """A perspective projection that uses a bijective and smooth map at every
    point except the projection point.

    The projection is not an equal-area projection but it is conformal.

    Attributes
    ----------
    scale_factor: float (default: 250)
        Specifies the scale value for the projection
    rotate: tuple (default: (96, 0))
        Degree of rotation in each axis.
    center: tuple (default: (0, 60))
        Specifies the longitude and latitude where the map is centered.
    precision: float (default: 0.1)
        Specifies the threshold for the projections adaptive resampling to the
        specified value in pixels.
    clip_angle: float (default: 90.)
        Specifies the clipping circle radius to the specified angle in degrees.


    """
    ...


@implements(_Stereographic)
def Stereographic(**kwargs):

    widget_cls = bqplot.scales.Stereographic
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Stereographic


def _Toolbar(
    figure: Element[bqplot.figure.Figure] = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    on_figure: typing.Callable[[Element[bqplot.figure.Figure]], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
) -> Element[bqplot.toolbar.Toolbar]:
    """Default toolbar for bqplot figures.

    The default toolbar provides three buttons:

    - A *Panzoom* toggle button which enables panning and zooming the figure.
    - A *Save* button to save the figure as a png image.
    - A *Reset* button, which resets the figure position to its original
      state.

    When the *Panzoom* button is toggled to True for the first time, a new
    instance of ``PanZoom`` widget is created.
    The created ``PanZoom`` widget uses the scales of all the marks that are on
    the figure at this point.
    When the *PanZoom* widget is toggled to False, the figure retrieves its
    previous interaction.
    When the *Reset* button is pressed, the ``PanZoom`` widget is deleted and
    the figure scales reset to their initial state. We are back to the case
    where the PanZoom widget has never been set.

    If new marks are added to the figure after the panzoom button is toggled,
    and these use new scales, those scales will not be panned or zoomed,
    unless the reset button is clicked.

    Attributes
    ----------
    figure: instance of Figure
        The figure to which the toolbar will apply.


    """
    ...


@implements(_Toolbar)
def Toolbar(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = bqplot.toolbar.Toolbar
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Toolbar


def _Tooltip(
    fields: list = [],
    formats: list = [],
    labels: list = [],
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    show_labels: bool = True,
    on_fields: typing.Callable[[list], Any] = None,
    on_formats: typing.Callable[[list], Any] = None,
    on_labels: typing.Callable[[list], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_show_labels: typing.Callable[[bool], Any] = None,
) -> Element[bqplot.default_tooltip.Tooltip]:
    """Default tooltip widget for marks.

    Attributes
    ----------
    fields: list (default: [])
        list of names of fields to be displayed in the tooltip
        All the attributes  of the mark are accessible in the tooltip
    formats: list (default: [])
        list of formats to be applied to each of the fields.
        if no format is specified for a field, the value is displayed as it is
    labels: list (default: [])
        list of labels to be displayed in the table instead of the fields. If
        the length of labels is less than the length of fields, then the field
        names are displayed for those fields for which label is missing.
    show_labels: bool (default: True)
        Boolean attribute to enable and disable display of the
        label /field name
        as the first column along with the value


    """
    ...


@implements(_Tooltip)
def Tooltip(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = bqplot.default_tooltip.Tooltip
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _Tooltip
