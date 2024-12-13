"""Write ipywidgets like React

ReactJS - ipywidgets relation:
 * DOM nodes -- Widget
 * Element -- Element
 * Component -- function

"""

import contextlib
import copy
import functools
import inspect
import logging
import sys
import threading
import traceback
import weakref
from collections import defaultdict
from dataclasses import dataclass, field
from inspect import isclass
from types import TracebackType
from typing import (
    Any,
    Callable,
    ContextManager,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)
from warnings import warn

import ipywidgets
import ipywidgets as widgets
import traitlets
import typing_extensions
from typing_extensions import Literal, Protocol

import reacton.logging  # noqa: F401  # has sidefx
import reacton.patch_display  # noqa: F401  # has sidefx

from . import _version, patch, utils  # noqa: F401

__version__ = _version.__version__


ipywidget_version_major = int(widgets.__version__.split(".")[0])


# see solara/server/patch.py for similar code
def _widgets_dict_getter() -> Callable[[], Dict[str, widgets.Widget]]:
    if ipywidget_version_major < 8:

        def get():
            return ipywidgets.widget.Widget.widgets

    else:
        if hasattr(ipywidgets.widgets.widget, "_instances"):  # since 8.0.3

            def get():
                return ipywidgets.widgets.widget._instances

        elif hasattr(ipywidgets.widget.Widget, "_instances"):

            def get():
                return ipywidgets.widget.Widget._instances

        else:
            raise RuntimeError("Could not find _instances on ipywidgets version %r" % ipywidgets.__version__)
    return get


_get_widgets_dict = _widgets_dict_getter()

_last_rc = None  # used for testing
local = threading.local()
T = TypeVar("T")
U = TypeVar("U")
W = TypeVar("W")  # used for widgets
V = TypeVar("V")  # used for value type of widget
V2 = TypeVar("V2")  # used for value type of widget
E = TypeVar("E")  # used for elements
P = typing_extensions.ParamSpec("P")

WidgetOrList = Union[widgets.Widget, List[widgets.Widget]]
EffectCleanupCallable = Callable[[], None]
EffectCallable = Callable[[], Optional[EffectCleanupCallable]]
ROOT_KEY = "ROOT::"
logger = logging.getLogger("reacton")  # type: ignore

# this will show friendly stack traces
DEBUG = 0
# if True, will show the original stacktrace as cause
TRACEBACK_ORIGINAL = True
MIME_WIDGETS = "application/vnd.jupyter.widget-view+json"


widget_render_error_msg = (
    """Cannot show widget. You probably want to rerun the code cell above (<i>Click in the code cell, and press Shift+Enter <kbd>⇧</kbd>+<kbd>↩</kbd></i>)."""
)

mime_bundle_default = {"text/plain": "Cannot show ipywidgets in text", "text/html": widget_render_error_msg}


def element(cls, **kwargs):
    return ComponentWidget(cls)(**kwargs)


def are_events_supressed():
    return getattr(local, "events_supressed", False)


@contextlib.contextmanager
def suppress_events():
    """Suppress events while updating a widget"""
    local.events_supressed = True
    try:
        yield
    finally:
        local.events_supressed = False


widgets.Widget.element = classmethod(element)


def close_widget(widget: widgets.Widget):
    # this happens for v.Chip, which has a close trait
    if callable(widget.close):
        widget.close()
    else:
        logger.warning("Widget %r does not have a close method, possibly a close trait was added", widget)


def _event_handler_exception_wrapper(f):
    """Wrap an event handler to catch exceptions and put them in a reacton context.

    This allows a component to catch the exception of a direct child"""
    rc = get_render_context()
    context = rc.context
    assert context is not None

    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            assert context is not None
            # because widgets don't have a context, but are a child of a component
            # we add it to exceptions_children, not exception_self
            # this allows a component to catch the exception of a direct child
            context.exceptions_children.append(e)
            rc.force_update()

    return wrapper


def join_key(parent_key, key):
    return f"{parent_key}{key}"


def pp(o):
    import prettyprinter

    prettyprinter.install_extras()

    prettyprinter.pprint(o, width=200)


def same_component(c1, c2):
    # return (c1.f.__name__ == c2.f.__name__) and (c1.f.__module__ == c2.f.__module__)
    return c1 == c2


def _with_tracebacks(e, tracebacks):
    # copy it, and we need with_traceback for unknown reasons not to cause
    # an infinite loop
    e_original = e
    e = copy.copy(e).with_traceback(e.__traceback__)
    tb_next = None

    # last item is the top of the stack
    for tb in tracebacks:
        # make a copy, so we do not mutate the original traceback
        tb = TracebackType(tb_next=tb_next, tb_frame=tb.tb_frame, tb_lasti=tb.tb_lasti, tb_lineno=tb.tb_lineno)
        tb_next = tb

    if TRACEBACK_ORIGINAL:
        e = e.with_traceback(tb_next)
        e_original.__cause__ = e
        return e_original
    else:
        e = e.with_traceback(tb_next)
        return e


class ComponentCreateError(RuntimeError):
    def __init__(self, rich_traceback):
        super().__init__(rich_traceback)
        self.rich_traceback = rich_traceback


class Component:
    name: str

    def __call__(self, *args, **kwargs) -> Union[widgets.Widget, "Element"]:
        pass


class Element(Generic[W]):
    child_prop_name = "children"
    # to make every unique on_value callback to a unique wrapper
    # so that we can remove the listeners
    _callback_wrappers: Dict[Tuple[str, str, Callable], Callable] = {}
    create_lock: ContextManager = threading.Lock()
    _shared = False

    def __init__(self, component, args=None, kwargs=None):
        self.component = component
        self.mime_bundle = mime_bundle_default
        self._key: Optional[str] = None
        self.args = args or []
        self.kwargs = kwargs or {}
        self.handlers = []
        self._meta = {}
        # for debugging/testing only
        self._render_count = 0
        self._key_frozen: bool = False

        rc = _get_render_context(required=False)
        if rc is not None and rc.container_adders:
            rc.container_adders[-1].add(self)
        if DEBUG:
            # since we construct widgets or components from a different code path
            # we want to preserve the original call stack, by manually tracking frames
            try:
                assert False
            except AssertionError:
                self.traceback = cast(TracebackType, sys.exc_info()[2])

            assert self.traceback is not None
            assert self.traceback.tb_frame is not None
            assert self.traceback.tb_frame.f_back is not None
            frame_py = self.traceback.tb_frame.f_back.f_back
            assert frame_py is not None
            self.traceback = TracebackType(tb_frame=frame_py, tb_lasti=self.traceback.tb_lasti, tb_lineno=frame_py.f_lineno, tb_next=None)

    def _arguments_changed(self, other: "Element"):
        if len(self.args) != len(other.args):
            return True
        if len(self.kwargs) != len(other.kwargs):
            return True
        for k, v in self.kwargs.items():
            if k not in other.kwargs:
                return True
            if not utils.equals(v, other.kwargs[k]):
                return True
        for a, b in zip(self.args, other.args):
            if not utils.equals(a, b):
                return True
        return False

    def key(self, value: str):
        """Returns the same element with a custom key set.

        This can help render performance. See documentation for details.
        """
        if self._key_frozen:
            raise RuntimeError("Element keys should not be mutated after rendering")
        self._key = value
        return self

    def meta(self, **kwargs):
        """Add metadata to the created widget.

        This can be used to find a widget for testing.
        """
        self._meta = {**self._meta, **kwargs}
        return self

    @property
    def is_shared(self):
        return self._shared

    def shared(self):
        self._shared = True
        return self

    def __repr__(self):
        def format_arg(value):
            value_repr = repr(value)
            if len(value_repr) > 50:
                value_repr = value_repr[:10] + "..." + value_repr[-10:]
            return value_repr

        args = [format_arg(value) for value in self.args]

        def format_kwarg(key, value):
            if key == "children":
                if isinstance(value, (list, tuple)) and len(value) > 0:
                    contains_elements = any(isinstance(child, Element) for child in value)
                    if contains_elements:
                        return "children = ..."
            return f"{key} = {format_arg(value)}"

        kwargs = [format_kwarg(key, value) for key, value in self.kwargs.items()]
        args_formatted = ", ".join(args + kwargs)
        if isinstance(self.component, ComponentFunction):
            name = self.component.f.__name__
            return f"{name}({args_formatted})"
        if isinstance(self.component, ComponentWidget):
            modulename = self.component.widget.__module__
            # lets shorten e.g. ipyvuetify.generated.Label.Label to ipyvuetify.Label
            shorten = "ipywidgets ipyvuetify ipyvue".split()
            for prefix in shorten:
                if modulename.startswith(prefix):
                    modulename = prefix
                    # don't replace ipyvuetify with ipyvue
                    break
            name = modulename + "." + self.component.widget.__name__
            return f"{name}({args_formatted})"
        else:
            raise RuntimeError(f"No repr for {type(self)}")

    def on(self, name, callback):
        self.handlers.append((name, callback))
        return self

    def _ipython_display_(self, **kwargs):
        display(self, self.mime_bundle)

    def __enter__(self):
        rc = _get_render_context()
        ca = ContainerAdder[W](self, "children")
        assert rc.context is not None
        rc.container_adders.append(ca)
        return self

    def __exit__(self, *args, **kwargs):
        rc = _get_render_context()
        assert rc.context is not None
        ca = rc.container_adders.pop()
        collected = ca.collect()
        self.add_children(collected)

    def add_children(self, children):
        if self.child_prop_name not in self.kwargs:
            self.kwargs[self.child_prop_name] = []
        # generic way to add to a list or tuple
        container_prop_type = type(self.kwargs[self.child_prop_name])
        self.kwargs[self.child_prop_name] = self.kwargs[self.child_prop_name] + container_prop_type(children)

    def _get_widget_args(self):
        return self.component.widget.class_trait_names()

    def _split_kwargs(self, kwargs):
        # split into normal kwargs and events
        listeners = {}
        normal_kwargs = {}
        assert isinstance(self.component, ComponentWidget)
        args = self._get_widget_args()
        for name, value in kwargs.items():
            if name.startswith("on_") and name not in args:
                listeners[name] = value
            else:
                normal_kwargs[name] = value
        return normal_kwargs, listeners

    def _close_widget(self, widget: widgets.Widget):
        close_widget(widget)
        try:
            delattr(widget, "hold_trait_notifications")
        except AttributeError:
            raise

    def _create_widget(self, kwargs):
        # we can't use our own kwarg, since that contains elements, not widgets
        kwargs, listeners = self._split_kwargs(kwargs)
        assert isinstance(self.component, ComponentWidget)
        # Because we look before and after, we need a lock.
        # A different implementation might avoid this.
        with self.create_lock:
            rc = get_render_context(required=True)
            before = set(_get_widgets_dict())
            try:
                widget = self.component.widget(**kwargs)
                hold_trait_notifications = widget.hold_trait_notifications

                @contextlib.contextmanager
                def hold_trait_notifications_extra(*args, **kwargs):
                    with rc, hold_trait_notifications(*args, **kwargs):
                        yield

                widget.hold_trait_notifications = hold_trait_notifications_extra

                if self._meta:
                    widget._react_meta = dict(self._meta)
            except Exception as e:
                raise RuntimeError(f"Could not create widget {self.component.widget} with {kwargs}") from e
            for name, callback in listeners.items():
                if callback is not None:
                    self._add_widget_event_listener(widget, name, callback)
            after = set(_get_widgets_dict())
        orphans = (after - before) - {widget.model_id}
        return widget, orphans

    def _update_widget(self, widget: widgets.Widget, el_prev: "Element", kwargs):
        assert isinstance(self.component, ComponentWidget)
        assert isinstance(el_prev.component, ComponentWidget)
        assert same_component(self.component, el_prev.component)
        # used_kwargs, _ = el_prev.split_kwargs(el_prev.kwargs)
        args = self.component.widget.class_trait_names()
        with widget.hold_sync(), suppress_events():
            # update values
            for name, value in kwargs.items():
                if name.startswith("on_") and name not in args:
                    self._update_widget_event_listener(widget, name, value, el_prev.kwargs.get(name))
                else:
                    self._update_widget_prop(widget, name, value)

            # if we previously gave an argument, but now we don't
            # we have to restore the default values, and remove listeners
            cls = widget.__class__
            traits = cls.class_traits()

            dropped_arguments = set(el_prev.kwargs) - set(self.kwargs)
            for name in dropped_arguments:
                if name.startswith("on_") and name not in args:
                    self._remove_widget_event_listener(widget, name, el_prev.kwargs[name])
                else:
                    value = traits[name].default()
                    self._update_widget_prop(widget, name, value)

    def _update_widget_prop(self, widget, name, value):
        setattr(widget, name, value)

    def _update_widget_event_listener(self, widget: widgets.Widget, name: str, callback: Optional[Callable], callback_prev: Optional[Callable]):
        # it's an event listener
        if callback != callback_prev and callback_prev is not None:
            self._remove_widget_event_listener(widget, name, callback_prev)
        if callback is not None and callback != callback_prev:
            self._add_widget_event_listener(widget, name, callback)

    def _add_widget_event_listener(self, widget: widgets.Widget, name: str, callback: Callable):
        target_name = name[3:]
        callback_exception_safe = _event_handler_exception_wrapper(callback)

        def on_change(change):
            if are_events_supressed():
                return
            logger.info("event %r on %r with %r", name, widget, change)
            callback_exception_safe(change["new"])

        key = (widget.model_id, name, callback)
        self._callback_wrappers[key] = on_change
        widget.observe(on_change, target_name)

    def _remove_widget_event_listener(self, widget: widgets.Widget, name: str, callback: Callable):
        target_name = name[3:]
        key = (widget.model_id, name, callback)
        on_change = self._callback_wrappers[key]
        del self._callback_wrappers[key]
        try:
            widget.unobserve(on_change, target_name)
        except ValueError:
            logger.error("Could not remove event listener %r from %r", name, widget)

    def _cleanup_callbacks(self, widget: widgets.Widget):
        args = self._get_widget_args()
        for name, value in self.kwargs.items():
            if name.startswith("on_") and name not in args and value is not None:
                self._remove_widget_event_listener(widget, name, value)


class Value(Generic[V], Protocol):
    def get(self) -> V: ...

    def set(self, value: V): ...


class ValueElement(Generic[W, V], Element[W]):
    def __init__(self, value_property, component, args=None, kwargs=None):
        self.value_property = value_property
        super().__init__(component, args, kwargs)

    # TODO: we want to enable something like this, but requires a good hash function
    # for the key
    # def use_value(self, *default) -> V:
    #     assert self.value_property in self.kwargs
    #     default_value = self.kwargs[self.value_property]
    #     # if not default:
    #     # else:
    #     #     default_value = default[0]
    #     #     if "kwargs" in self.kwargs:
    #     #         default_value = self.kwargs["value"]
    #     value, set_value = use_state(default_value)
    #     self.kwargs[self.value_property] = value
    #     self.kwargs[f"on_{self.value_property}"] = lambda x: set_value(x)
    #     return value

    def connect(self, value: Value[V]):
        """Will automatically set up a connection between the value and the widget.

        The object passed should have a get and set method. The get method
        set the current value, while the set method will be called when the
        `on_value` event is triggered.

        The get method could also be used to automically set up listeners.
        """
        self.kwargs[self.value_property] = value.get()
        self.kwargs[f"on_{self.value_property}"] = lambda x: value.set(x)
        return self


FuncT = TypeVar("FuncT", bound=Callable[..., Element])


def find_elements(value: Union[Element, List, Tuple, Dict]) -> Set[Element]:
    if isinstance(value, Element):
        el = value
        elements = {el}
        if not isinstance(el.kwargs, dict):
            raise RuntimeError("keyword arguments for {el} should be a dict, not {el.kwargs}")
        elements |= find_elements(el.args)
        elements |= find_elements(el.kwargs)
        return elements
    elif isinstance(value, (tuple, list)):
        elements = set()
        for child in value:
            if isinstance(child, (Element, tuple, list, dict)):
                elements |= find_elements(child)
        return elements
    elif isinstance(value, dict):
        elements = set()
        for child in value.values():
            if isinstance(child, (Element, tuple, list, dict)):
                elements |= find_elements(child)
        return elements


class ContainerAdder(Generic[W]):
    def __init__(self, el: Element[W], prop_name: str):
        self.el = el
        self.prop_name = prop_name
        self.created: List[Element] = []

    def add(self, el):
        self.created.append(el)

    def collect(self):
        children = set()
        for el in self.created:
            children |= find_elements(el) - {el}
        top_level = [k for k in self.created if k not in children]
        return top_level


class ComponentWidget(Component):
    def __init__(self, widget: Type[widgets.Widget], mime_bundle=mime_bundle_default):
        self.mime_bundle = mime_bundle
        self.widget = widget
        self.name = widget.__name__

    def __eq__(self, rhs):
        if self is rhs:
            return True
        if not isinstance(rhs, ComponentWidget):
            return False
        return self.widget == rhs.widget

    def __repr__(self):
        return f"Component[{self.widget!r}]"

    def __call__(self, *args, **kwargs):
        el: Element = Element(self, args=args, kwargs=kwargs)
        # TODO: temporary, we cannot change the constructor
        # otherwise we need to generate the wrapper code again for all libraries
        el.mime_bundle = self.mime_bundle
        return el


class ComponentFunction(Component):
    def __init__(self, f: Callable[[], Element], mime_bundle=mime_bundle_default, value_name=None):
        self.f = f
        self.name = self.f.__name__
        self.mime_bundle = mime_bundle
        self.value_name = value_name
        self.render_count = 0  # used for debugging, not thread safe, so count can be off
        functools.update_wrapper(self, f)

    def widget(self, **kwargs):
        _ensure_colab_fixes()
        return self.widget_class()(**kwargs)

    def widget_class(self):
        parameters = inspect.signature(self.f).parameters
        args = list(parameters.keys())
        listeners = set()
        normal_kwargs = set()
        for name in args:
            if name.startswith("on_"):
                listeners.add(name)
            else:
                normal_kwargs.add(name)
        component = self

        class Container(widgets.VBox, widgets.ValueWidget):
            description = traitlets.Unicode()

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._children = []
                traits = {}

                for name in normal_kwargs:
                    if name != "children":  # children is a special trait we keep
                        if name in normal_kwargs:
                            trait = traitlets.Any(default_value=parameters[name].default)
                        else:
                            trait = traitlets.Any()
                        traits[name] = trait
                Container.add_traits(self, **traits)
                for name, value in kwargs.items():
                    if name in normal_kwargs:
                        setattr(self, name, value)
                for name in normal_kwargs:
                    self.observe(self._rerender, name)
                el = self._create_el()
                self.rc = _RenderContext(el, self)
                self.rc.render(el, self)

            def _create_el(self):
                kwargs = {}
                for name in normal_kwargs:
                    if name != "children":
                        kwargs[name] = getattr(self, name)
                for name in listeners:
                    propname = name[3:]

                    def closure(propname=propname):
                        def setter(value):
                            setattr(self, propname, value)

                        return setter

                    kwargs[name] = closure()
                logger.info("calling component with kwargs: %r", kwargs)
                return component(**kwargs)

            def _rerender(self, change):
                el = self._create_el()
                self.rc.update(el)

        return Container

    def __eq__(self, rhs):
        if self is rhs:
            return True
        if not isinstance(rhs, ComponentFunction):
            return False
        return self.f == rhs.f

    def __repr__(self):
        return f"react.component({self.f.__module__}.{self.f.__name__})"

    def __call__(self, *args, **kwargs):
        if self.value_name is not None:
            el: Element = ValueElement(self.value_name, self, args=args, kwargs=kwargs)
        else:
            el = Element(self, args=args, kwargs=kwargs)
        el.mime_bundle = self.mime_bundle
        return el


@overload
def component(obj: None = None, mime_bundle=...) -> Callable[[FuncT], FuncT]: ...


@overload
def component(obj: FuncT, mime_bundle=...) -> FuncT: ...


@overload
def component(obj: Callable[P, None], mime_bundle=...) -> Callable[P, Element]: ...


# it is actually this...
# def component(obj: Union[Type[widgets.Widget], FuncT]) -> Union[ComponentWidget, ComponentFunction[FuncT]]:
# but casting to FuncT gives much better type hints (e.g. argument types checks etc)


def component(obj: Union[Callable[P, None], FuncT] = None, mime_bundle: Dict[str, Any] = mime_bundle_default):
    def wrapper(obj: Union[Callable[P, None], FuncT]) -> FuncT:
        if isclass(obj) and issubclass(obj, widgets.Widget):
            return cast(FuncT, ComponentWidget(widget=obj, mime_bundle=mime_bundle))
        else:
            return cast(FuncT, ComponentFunction(f=cast(FuncT, obj), mime_bundle=mime_bundle))

    if obj is not None:
        return wrapper(obj)
    else:
        return wrapper


@overload
def value_component(
    value_type: None, value_name="value", mime_bundle: Dict[str, Any] = mime_bundle_default
) -> Callable[[Callable[P, ValueElement[W, V]]], Callable[P, ValueElement[W, V]]]: ...


@overload
def value_component(
    value_type: Type[V], value_name="value", mime_bundle: Dict[str, Any] = mime_bundle_default
) -> Callable[[Callable[P, Element[W]]], Callable[P, ValueElement[W, V]]]: ...


def value_component(value_type: Union[Type[V], None], value_name="value", mime_bundle: Dict[str, Any] = mime_bundle_default):
    """Creates a custom component that returns a ValueElement.

    A ValueElement is a special element that can be used to connect to a Value, and be used to automatically
    wire up the value and on_value events.
    """

    def wrapper(obj: Callable[P, Union[Element[W], ValueElement[W, V2]]]) -> Callable[P, ValueElement[W, V]]:
        if isclass(obj) and issubclass(obj, widgets.Widget):
            return cast(Callable[P, ValueElement[T, V]], ComponentWidget(widget=obj, mime_bundle=mime_bundle))
        else:
            return cast(Callable[P, ValueElement[T, V]], ComponentFunction(f=obj, mime_bundle=mime_bundle, value_name=value_name))

    return wrapper


def force_update():
    rc = _get_render_context()
    rc.force_update()


def get_widget(el: Element):
    """Returns the real underlying widget, can only be used in use_effect.

    Note that if the same element it used twice in a component, the widget corresponding to the last
    element will be returned.
    """
    rc = get_render_context()
    # breadth first search
    contexts = [rc.context]
    while contexts:
        context = contexts.pop()
        if context is None:
            raise RuntimeError("get_widget() can only be used in use_effect")
        contexts.extend(context.children.values())
        if el.is_shared:
            if el not in rc._shared_widgets:
                return rc._shared_widgets[el]
        else:
            if el in context.element_to_widget:
                return context.element_to_widget[el]
    if id(el) in rc._old_element_ids:
        raise KeyError(f"Element {el} was found to be in a previous render, you may have used a stale element")
    raise KeyError(f"Element {el} not found in all known widgets")  # for the component {context.widgets}")


def use_state(initial: T, key: str = None, eq: Callable[[Any, Any], bool] = None) -> Tuple[T, Callable[[Union[T, Callable[[T], T]]], None]]:
    """Returns a `(value, setter)` tuple that is used to manage state in a component.

    This function can only be called from a component function.

    The value returns the current state (which equals `initial` at the first render call). Or the value that was last set using the setter.

    Note that the setter function can be used in two ways.

    Directly setting the value:

    ```python
    @reacton.component
    def ButtonClick():
        clicks, set_clicks = reacton.use_state(0)
        def my_click_handler():
            set_clicks(clicks+1)
        button = w.Button(description=f"Clicked {clicks} times",
                        on_click=my_click_handler)
        return button
    ```

    Updating the value based on the previous/current value.

    ```python
    @reacton.component
    def ButtonClick():
        clicks, set_clicks = reacton.use_state(0)
        def my_click_handler():
            set_clicks(lambda prev: prev+1)
        button = w.Button(description=f"Clicked {clicks} times",
                        on_click=my_click_handler)
        return button
    ```

    The last one avoid issues with stale data, which means you have a reference to the value of an old render pass (not present in this simple example).

    """
    rc = _get_render_context()
    return rc.use_state(initial, key, eq)


def use_effect(effect: EffectCallable, dependencies=None):
    rc = _get_render_context()
    return rc.use_effect(effect, dependencies=dependencies)


def use_side_effect(effect: EffectCallable, dependencies=None):
    warn("use_side_effect is deprecated, please use use_effect", DeprecationWarning, stacklevel=2)
    return use_effect(effect=effect, dependencies=dependencies)


def use_state_widget(widget: widgets.Widget, prop_name, key=None):
    rc = _get_render_context()
    initial_value = getattr(widget, prop_name)
    value, setter = use_state(initial_value, key=key)
    if rc.first_render:

        def handler(change):
            setter(change.new)  # type: ignore

        widget.observe(handler, prop_name)
    return value


@overload
def get_render_context(required: Literal[True] = ...) -> "_RenderContext": ...


@overload
def get_render_context(required: Literal[False] = ...) -> Optional["_RenderContext"]: ...


def get_render_context(required=True):
    rc = getattr(local, "rc", None)
    if rc is None and required:
        raise RuntimeError("No render context")
    return rc


# previous name
_get_render_context = get_render_context


def use_reducer(reduce: Callable[[T, U], T], initial_state: T) -> Tuple[T, Callable[[U], None]]:
    state, set_state = use_state(initial_state)

    def dispatch(action):
        def state_updater(state):
            return reduce(state, action)

        set_state(state_updater)

    return state, dispatch


def use_memo(f: Callable[[], T], dependencies=None, debug_name: str = None) -> T:
    if debug_name is None:
        debug_name = f.__name__
    rc = _get_render_context()
    if dependencies is None:
        dependencies = inspect.getclosurevars(f).nonlocals
        dependencies = {k: v for k, v in dependencies.items() if not k.startswith("__")}
        return rc.use_memo(f, dependencies, debug_name)
    else:
        return rc.use_memo(f, dependencies, debug_name)


def use_callback(f, dependencies):
    def wrapper(*ignore):
        return f

    use_memo(wrapper, dependencies)


def use_exception() -> Tuple[Optional[BaseException], Callable[[], None]]:
    rc = _get_render_context(required=True)
    assert rc.context is not None
    # we keep track of the exception in the state because we want to explicitly
    # clear it.
    exception, set_exception = use_state(cast(Optional[BaseException], None))
    rc.context.exception_handler = True
    if rc.context.exceptions_children:
        # if we found an exception in one of our children, we want to return this
        # exception, until clear is called.
        e = rc.context.exceptions_children[0]
        # reset the exceptions that we found
        rc.context.exceptions_children = []
        set_exception(e)
        exception = e

    def clear():
        set_exception(None)

    logger.info("use_exception: %r", exception)
    return exception, clear


class Ref(Generic[T]):
    def __init__(self, initial_value: T):
        self.current = initial_value


def use_ref(initial_value: T) -> Ref[T]:
    def make_ref():
        return Ref(initial_value)

    ref = use_memo(make_ref, [])
    return ref


class UserContext(Generic[T]):
    def __init__(self, _default_value: T, name: Optional[str]) -> None:
        self._default_value: T = _default_value
        self.name = name

    def provide(self, obj: T):
        rc = _get_render_context()
        context = rc.context
        assert context is not None
        prev = context.user_contexts_prev.get(self, self._default_value)
        context.user_contexts[self] = obj
        if not utils.equals(prev, obj):
            for listener in context.context_listeners.get(self, []):
                listener()

    def get(self):
        """Convenience method to get the context value, same as get_context"""
        return get_context(self)

    def use(self):
        """Convenience method to use the context value, same as use_context"""
        return use_context(self)

    def __repr__(self):
        return f"UserContext({self._default_value}, name={self.name})"


def create_context(default_value: T, name: str = None) -> UserContext[T]:
    return UserContext[T](default_value, name)


# this does not work with well mypy, UserContext[T] and obj:T
# so for type hints it is better to use user_context.provide
def provide_context(user_context: UserContext[T], obj: T):
    user_context.provide(obj)


def get_context(user_context: UserContext[T]) -> T:
    """Similar to use_context, but does not trigger a re-render if the context changes."""
    rc = _get_render_context()
    value = None
    assert rc.context is not None
    context = rc.context.parent
    # we need to walk up the context tree to find the nearest
    # ancestor that has the context we are looking for.
    while value is None and context is not None:
        if user_context in context.user_contexts:
            value = context.user_contexts.get(user_context)
            break
        else:
            context = context.parent

    if context is None:
        # we did not find the context, so we return the default value
        return user_context._default_value
    else:
        return cast(T, value)


def use_context(user_context: UserContext[T]) -> T:
    counter, set_counter = use_state(0)

    def force_update():
        set_counter(lambda x: x + 1)

    rc = _get_render_context()
    value = None
    assert rc.context is not None
    context = rc.context.parent
    # we need to walk up the context tree to find the nearest
    # ancestor that has the context we are looking for.
    while value is None and context is not None:
        if user_context in context.user_contexts:
            value = context.user_contexts.get(user_context)
            break
        else:
            context = context.parent

    # we need to register a listener on the context so that we can
    # force an update when the context value changes (using provides).
    def connect():
        if context is not None:
            context.context_listeners[user_context].add(force_update)

            def cleanup():
                assert context is not None
                context.context_listeners[user_context].remove(force_update)

            return cleanup

    use_effect(connect, dependencies=[context])
    if context is None:
        # we did not find the context, so we return the default value
        return user_context._default_value
    else:
        return cast(T, value)


"""
# naming:

# this is a component
@react.component
def Child(children=[])
    # this is the render function
    return w.VBox(children=children)  # it returns the root element

# this is also a component
@react.component
def App():
    # element1 will go into elements_next on render
    # and move to elements during reconciliation
    element1 = w.Button(description="Hi")
    element = Child(children=[element1])
    return element

invoke_element = App()
"""


@dataclass
class ComponentContext:
    parent: Optional["ComponentContext"] = field(default=None, repr=False)

    # this is the element in the parent context
    invoke_element: Optional[Element] = None

    # the root element for this component
    root_element_next: Optional[Element] = None
    root_element: Optional[Element] = None
    # all elements, including the root element
    elements_next: Dict[str, Element] = field(default_factory=dict)
    # from previous reconciliation phase
    elements: Dict[str, Element] = field(default_factory=dict)
    # contexts for child elements which are a component
    # (every function component should be in children and elements, but not widget component)
    children_next: Dict[str, "ComponentContext"] = field(default_factory=dict)
    # from previous reconciliation phase, so we can reuse hooks
    children: Dict[str, "ComponentContext"] = field(default_factory=dict)

    # widgets correponding to the elements (non-shared widgets)
    widgets: Dict[str, "widgets.Widget"] = field(default_factory=dict)

    # used for get_widget to find the widget corresponding to an element
    element_to_widget: Dict[Element, "ipywidgets.Widget"] = field(default_factory=dict)

    # hooks data
    state: Dict = field(default_factory=dict)
    state_metadata: Dict = field(default_factory=dict)
    state_index = 0
    effects: List["Effect"] = field(default_factory=list)
    effect_index = 0
    memo: List[Any] = field(default_factory=list)
    memo_index = 0
    # for provide/use_context
    user_contexts: Dict["UserContext", Any] = field(default_factory=dict)
    user_contexts_prev: Dict["UserContext", Any] = field(default_factory=dict)
    context_listeners: Dict["UserContext", Set[Callable]] = field(default_factory=lambda: defaultdict(set))

    # to track key collisions, and remove unused elements
    used_keys: Set[str] = field(default_factory=set)
    # if a child component's state if changed, it needs a rerender
    needs_render: bool = True

    # elements created in this context go there
    owns: Set[Element] = field(default_factory=set)

    # the exception that were raised in this component
    exceptions_self: List[BaseException] = field(default_factory=list)
    # all exceptions that occurred during render, reconcolliate or use effect
    # that bubbled up (children with exception_handler = False)
    exceptions_children: List[BaseException] = field(default_factory=list)
    # flag if this component will handle an exception of it's children
    # NOTE: we can never handle an exception in our own render function,
    # it will always bubble up to the parent component.
    exception_handler: bool = False

    context_managers: List[ContextManager] = field(default_factory=list)


TEffect = TypeVar("TEffect", bound="Effect")


@dataclass
class RerenderReason:
    reason: str
    prev_value: Any = None
    next_value: Any = None
    created_stack: List[str] = field(default_factory=list)
    trigger_stack: List[str] = field(default_factory=list)


class Effect:
    def __init__(self, callable: EffectCallable, dependencies: Optional[List[Any]] = None, next: Optional["Effect"] = None) -> None:
        self.callable = callable
        self.dependencies = dependencies
        self._cleanup: Optional[EffectCleanupCallable] = None
        self.next = next
        self.executed = False
        self._cleaned_up = False

    def cleanup(self):
        if self._cleaned_up:
            raise RuntimeError("Already cleaned up!")
        if self._cleanup is not None:
            self._cleanup()
        self._cleaned_up = True

    def __call__(self):
        if self.executed:
            return
        self._cleanup = self.callable()
        self.executed = True


class _RenderContext:
    context: Optional[ComponentContext] = None

    def __init__(self, element: Element, container: widgets.Widget = None, children_trait="children", handle_error: bool = True, initial_state=None):
        self.element = element
        self.container = container
        self.children_next_trait = children_trait
        self.first_render = True
        self.container_adders: List[ContainerAdder] = []
        self.context = ComponentContext()
        self.context_root = self.context
        self.render_count = 0
        self._lock_thread = cast(Optional[threading.Thread], None)
        self.last_root_widget: widgets.Widget = None
        self._is_rendering = False
        self._rerender_needed = False
        self._rerender_needed_reasons: List[RerenderReason] = []
        self.thread_lock = threading.Lock()
        self._closing = False
        self.tracebacks: List[TracebackType] = []
        self.handle_error = handle_error
        self.reconsolidating = False
        self._batch_counter = utils.ThreadSafeCounter()
        if initial_state:
            self.state_set(self.context_root, initial_state)

        # element that are shared outlive the ComponentContext, so we
        # store them in the RenderContext
        self._shared_widgets: Dict[Element, widgets.Widget] = {}

        # each render phase, we track which (shared) elements we proccessed
        # so we don't render them twice (only 1 widget per element)
        self._shared_elements_next: Set[Element] = set()

        # once reconcilidated, shared elements move here.
        self._shared_elements: Set[Element] = set()

        # widgets created as side effect (like Layout and Style)
        # key is the widget model id (because some widgets are not hashable, like plotly)
        # We keep track of this to make sure we clean up all widgets.
        self._orphans: Dict[str, Set[str]] = {}
        # for detecting stale elements used get_widget
        self._old_element_ids: Set[int] = set()

    def __enter__(self):
        counter = self._batch_counter.increment()
        if counter == 1:
            logger.info("entering batch render")

    def __exit__(self, exc_type, exc_value, traceback):
        counter = self._batch_counter.decrement()
        if counter == 0:
            logger.info("finishing batch render (%s)", "needs rerender" if self._rerender_needed else "no rerender needed")
            if self._rerender_needed:
                self._possible_rerender()

    def find(self, cls: Type[W] = ipywidgets.Widget, **matches):
        from .find import finder

        return finder(self).find(cls, **matches)

    _find = find  # for backward compatibility

    def close(self):
        with self.thread_lock:
            self._closing = True
            logger.info("Removing elements...")
            self._remove_element(self.element, default_key="/", parent_key=ROOT_KEY)
            logger.info("Removing elements done.")
            assert self.context is self.context_root
        if self.container:
            self.container.close()
            if isinstance(self.container, widgets.DOMWidget) and self.container.layout is not None:
                self.container.layout.close()
        if self._shared_elements:
            raise RuntimeError(f"Element not cleaned up: {self._shared_elements}")
        if self._orphans:
            orphan_widgets = set([_get_widgets_dict()[k] for k in self._orphans])
            raise RuntimeError(f"Orphan widgets not cleaned up for widgets: {orphan_widgets}")
        exceptions = [*self.context.exceptions_children, *self.context_root.exceptions_self]
        if exceptions:
            raise exceptions[0]

    def state_get(self, context: Optional[ComponentContext] = None):
        if context is None:
            context = self.context_root
        data = {}
        data["state"] = context.state
        if context.children:
            children_state = data["children"] = {}
            for name, context in context.children.items():
                children_state[name] = self.state_get(context)
        return data

    def state_set(self, context: ComponentContext, state):
        context.state = state.get("state", {})
        for name, state in state.get("children", {}).items():
            context.children_next[name] = ComponentContext(parent=context)
            self.state_set(context.children_next[name], state)

    def use_memo(self, f, dependencies, debug_name: str = None, use_nonlocals=False):
        assert self.context is not None
        name = debug_name or "no-name"
        if len(self.context.memo) <= self.context.memo_index:
            value = f()
            memo = (value, dependencies)
            self.context.memo.append(memo)
            self.context.memo_index += 1
            logger.debug("Initial memo = %r for index %r (debug-name: %r)", memo, self.context.memo_index - 1, name)
            return value
        else:
            memo = self.context.memo[self.context.memo_index]
            value, dependencies_previous = memo
            if utils.equals(dependencies_previous, dependencies):
                logger.debug("Got memo hit = %r for index %r (debug-name: %r)", memo, self.context.memo_index, name)
            else:
                logger.debug("Replace memo with = %r for index %r (debug-name: %r)", memo, self.context.memo_index, name)
                value = f()
                memo = (value, dependencies)
                self.context.memo[self.context.memo_index] = memo
            self.context.memo_index += 1
            return value

    def use_state(self, initial, key: str = None, eq: Callable[[Any, Any], bool] = None) -> Tuple[T, Callable[[Union[T, Callable[[T], T]]], None]]:
        assert self.context is not None
        if key is None:
            key = str(self.context.state_index)
            self.context.state_index += 1
        if key not in self.context.state:
            self.context.state[key] = initial
            if isinstance(initial, (list, dict, set)):
                self.context.state_metadata[key] = len(initial)
            elif utils.isinstance_lazy(initial, "pandas.DataFrame"):
                self.context.state_metadata[key] = utils.dataframe_fingerprint(initial)
            logger.debug("Initial state = %r for key %r (%r)", initial, key, id(self.context))
            return initial, self.make_setter(key, self.context, eq)
        else:
            state = self.context.state[key]
            logger.debug("Got state = %r for key %r (%r)", state, key, id(self.context))
            return state, self.make_setter(key, self.context, eq)

    def make_setter(self, key, context: ComponentContext, eq: Callable[[Any, Any], bool] = None):
        if DEBUG:
            created_stack = traceback.format_stack()

        # if we do not use a weakref, the memory test fails
        # I am not sure exactly why, but this will at least make
        # it easier for Python to garbage collect, since it will
        # avoid circular references

        def set_(value):
            if callable(value):
                value = value(context.state[key])
            logger.info("Set state = %r for key %r (previous value was %r) (%r)", value, key, context.state[key], id(self.context))

            should_update = False
            new_metadata = None
            if eq is None:
                if context.state[key] is value and isinstance(value, (list, dict, set)):
                    new_metadata = len(value)
                    if context.state_metadata[key] != new_metadata:
                        warn(
                            "You are setting the state with the same object, this will usually not trigger a rerender. "
                            f"The length of {value} changed compared to the previous time it was set. Are you mutating an existing state object? "
                            "A common mistake is appending to a list, mutating a dict or set, etc.",
                            UserWarning,
                            stacklevel=2,
                        )
                        should_update = True
                if context.state[key] is value and utils.isinstance_lazy(value, "pandas.DataFrame"):
                    new_metadata = utils.dataframe_fingerprint(value)
                    if context.state_metadata[key] != new_metadata:
                        warn(
                            "You are setting the state with the dataframe, this will usually not trigger a rerender. "
                            "We noticed the ids of the dataframe series are changed. Are you mutating an dataframe? "
                            "Consider making a copy of the dataframe.",
                            UserWarning,
                            stacklevel=2,
                        )
                        should_update = True
            equals = eq or utils.equals
            should_update = not equals(context.state[key], value) or should_update

            # if a cleanup during close trigger a state update in a different component, we want to ignore that
            # otherwise we get a deadlock
            if self._closing:
                should_update = False

            if should_update:
                prev_value = context.state[key]
                context.state[key] = value
                if context.state[key] is value and isinstance(value, (list, dict, set)) and new_metadata is None:
                    new_metadata = len(value)
                if context.state[key] is value and utils.isinstance_lazy(value, "pandas.DataFrame") and new_metadata is None:
                    new_metadata = utils.dataframe_fingerprint(value)
                context.state_metadata[key] = new_metadata
                # TODO: enable
                context.needs_render = True
                if self._rerender_needed is False:
                    if DEBUG:
                        trigger_stack = traceback.format_stack()

                        self._rerender_needed_reasons.append(
                            RerenderReason(
                                reason=f"state changed with key {key}",
                                prev_value=prev_value,
                                next_value=value,
                                created_stack=created_stack,
                                trigger_stack=trigger_stack,
                            )
                        )
                    else:
                        self._rerender_needed_reasons.append(RerenderReason(reason=f"state changed with key {key}", prev_value=prev_value, next_value=value))
                    self._rerender_needed = True
                self._possible_rerender()

        return set_

    def force_update(self):
        if not self._is_rendering:
            self.render(self.element, self.container)

    def use_effect(self, effect: EffectCallable, dependencies=None):
        assert self.context is not None
        if len(self.context.effects) <= self.context.effect_index:
            self.context.effect_index += 1
            self.context.effects.append(Effect(effect, dependencies))
            logger.debug("Initial effect = %r for index %r (%r)", effect, self.context.effect_index - 1, dependencies)
        else:
            previous_effect = self.context.effects[self.context.effect_index]
            # we always set it, even replacing it when we didn't execute it
            # in the consolidation phase we decide what to do (e.g. skip it)
            logger.debug("Setting next effect = %r for index %r (%r)", effect, self.context.effect_index, dependencies)
            if previous_effect.executed:
                # line up...
                previous_effect.next = Effect(effect, dependencies)
            else:
                # replace
                self.context.effects[self.context.effect_index] = Effect(effect, dependencies)
            self.context.effect_index += 1

    def update(self, element: Element):
        if self._is_rendering:
            self.element = element
            self._rerender_needed_reasons.append(RerenderReason(reason="root element changed"))
            self._rerender_needed = True
        else:
            self.render(element, self.container)

    def _possible_rerender(self):
        if not self._is_rendering and self._batch_counter.current() == 0:
            self.render(self.element, self.container)
        else:
            logger.info("No render phase triggered, already rendering")

    def render(self, element: Element, container: widgets.Widget = None):
        # render + consolidate
        widget = None
        if container is None:
            container = self.container
        was_locked = False
        if self.thread_lock.locked():
            if self._lock_thread == threading.current_thread():
                raise RuntimeError("Recursive render detected (avoided deadlock), current thread: %r" % threading.current_thread())
            logger.info(
                "Render phase still in progress, waiting for mutex to release (locked obtained by %r, we are in thread %r)",
                self._lock_thread,
                threading.current_thread(),
            )
            was_locked = True
        with self.thread_lock:
            self._lock_thread = threading.current_thread()
            if was_locked:
                logger.info("Mutex released, continuing render phase")
            prev_rc = getattr(local, "rc", None)
            try:
                local.rc = self
                self.element = element
                del element
                main_render_phase = not self._is_rendering
                render_count = self.render_count  # make a copy
                self._rerender_needed = False
                logger.info("Render phase: %r %r of %r", self.render_count, "main" if main_render_phase else "(nested)", self.element)
                self.render_count += 1
                self._is_rendering = True
                # if we got called recursively, self.context is not the root context
                context_prev = self.context
                self.context = self.context_root
                self.context.exception_handler = False
                self.context.exceptions_children = []
                self.context.exceptions_self = []
                self.context.root_element_next = self.element
                assert self.context is not None

                try:
                    self._shared_elements_next = set()
                    self._render(self.element, "/", parent_key=ROOT_KEY)
                    self.first_render = False
                except BaseException:
                    self._is_rendering = False
                    raise

                if main_render_phase:
                    stable = False
                    render_counts = 0
                    while not stable and not self.context_root.exceptions_children:
                        # we started the rendering loop (main_render_phase is True), so we keep going
                        # but if an exception bubbled up, we should stop
                        while self._rerender_needed and not self.context_root.exceptions_children:
                            if render_counts > 50:

                                def format(reason: RerenderReason):
                                    f = f"Reason: {reason.reason}\nValue changed from {reason.prev_value} to {reason.next_value}\n"
                                    if reason.created_stack:
                                        f += f"Created at: {''.join(reason.created_stack)}\n"
                                    if reason.trigger_stack:
                                        f += f"Triggered at: {''.join(reason.trigger_stack)}\n"
                                    return f

                                self._rerender_needed_reasons[-1]
                                msg = f"Too many renders triggered, your render loop does not stop\nLast reason: {format(self._rerender_needed_reasons[-1])}\n"
                                if len(self._rerender_needed_reasons) >= 2:
                                    msg += f"Previous reasons: {format(self._rerender_needed_reasons[-2])}\n"
                                raise RuntimeError(msg)
                            logger.info("Entering nested render phase: %r", self._rerender_needed_reasons[-1])
                            self._rerender_needed = False
                            self._shared_elements_next = set()
                            self.context.exception_handler = False
                            self.context.exceptions_children = []
                            self.context.exceptions_self = []

                            self._render(self.element, "/", parent_key=ROOT_KEY)
                            logger.info("Render done: %r %r", self._rerender_needed, self._rerender_needed_reasons[-1])
                            assert self.context is self.context_root
                            render_counts += 1
                        logger.debug("Render phase resulted in (next) elements:")
                        for el in self._shared_elements_next:
                            logger.debug("\t%r %x", el, id(el))

                        logger.debug("Current elements:")
                        for el in self._shared_elements:
                            logger.debug("\t %r %x", el, id(el))
                        if self.context_root.exceptions_children:
                            # an exception bubbled up render
                            break

                        logger.info("Render reconsolidate...")
                        self.reconsolidating = True
                        try:
                            widget = self._reconsolidate(self.element, default_key="/", parent_key=ROOT_KEY)
                        finally:
                            self.reconsolidating = False
                        logger.info("Render reconsolidate done")
                        self.context.root_element = self.context.root_element_next
                        self.context.root_element_next = None

                        if self._shared_elements_next:
                            raise RuntimeError(f"Element not reconsolidated: {self._shared_elements_next}")
                        logger.debug("Reconsolidate phase resulted in elements:")
                        for el in self._shared_elements:
                            logger.debug("\t%r %x", el, id(el))
                        # RESET
                        assert self.context is self.context_root
                        if self.element.is_shared:
                            assert widget in self._shared_widgets.values()
                        else:
                            assert widget in self.context_root.widgets.values()
                        if self.last_root_widget is None:
                            self.last_root_widget = widget
                        else:
                            if container is None:
                                if self.last_root_widget != widget:
                                    raise ValueError(
                                        "You are not using a container, and the root component returned a new widget,"
                                        "make sure your root component always returns the same component type"
                                    )
                        if container:
                            if widget is None:
                                # Exception occurred, and we cannot render the widget
                                container.children = []
                            else:
                                container.children = [widget]

                        if self.context_root.exceptions_children or self.context_root.exceptions_self:
                            # an exception bubbled up during reconsolidate
                            break

                        if self._rerender_needed:
                            logger.info("Need rerender after reconsolidation: %r", self._rerender_needed_reasons[-1])
                            stable = False
                        else:
                            stable = True

                    self._is_rendering = False
                self.context = context_prev
                logger.info("Done with render phase: %r", render_count)
            except Exception as e:
                if DEBUG:
                    # construct a fake traceback (showing how the elements were constructed)
                    if not self.tracebacks:
                        raise
                    e = _with_tracebacks(e, self.tracebacks)
                    raise e
                else:
                    raise

            finally:
                local.rc = prev_rc  # type: ignore
                self._is_rendering = False
                assert self.context is self.context_root

        exceptions = [*self.context.exceptions_children, *self.context_root.exceptions_self]
        if exceptions:
            exc = exceptions[0]
            if DEBUG:
                exc = _with_tracebacks(exc, self.tracebacks)

            if self.handle_error:
                logger.info("Exception occurred, rendering error message")
                if exc.__traceback__ is None:
                    value = "Exception occurred, but no traceback available"
                else:
                    error = "".join(traceback.format_exception(None, exc, exc.__traceback__))
                    import html

                    value = html.escape(error)
                from . import ipywidgets as w

                return self.render(w.HTML(value="<pre>" + value + "</pre>", layout=w.Layout(overflow="auto")), self.container)
            else:
                raise exc
        return widget

    def _render(self, element: Element, default_key: str, parent_key: str):
        if not isinstance(element, Element):
            raise TypeError(f"Expected element, not {element}")
        # for tracking stale data/elements when using get_widget
        self._old_element_ids.add(id(element))
        context = self.context
        assert context is not None

        if default_key == "/":
            # if this is the root element, reset
            context.used_keys.clear()
            default_key = "/"

        el = element
        # if we did not define a custom key, use the default key
        key = el._key
        if key is None:
            key = default_key
        el._key_frozen = True

        logger.debug("Render: (%s,%s)  - %r", parent_key, key, element)

        if key in context.used_keys:
            if DEBUG:
                self.tracebacks.append(el.traceback)
            raise KeyError(f"Duplicate key {key!r}")
        context.used_keys.add(key)
        # if a shared element is used in multiple places, we only render it once
        if el.is_shared:
            if el in self._shared_elements_next:
                # we already rendered it
                logger.debug("Render: Already rendered")
                return
            else:
                self._shared_elements_next.add(el)
        el_prev = context.elements_next.get(key)
        if el_prev is None:
            el_prev = context.elements.get(key)
        context.elements_next[key] = el
        # used for testing
        el._render_count += 1

        if isinstance(el.component, ComponentWidget):
            assert not el.args, "no positional args supported for widgets"
            # if at this place we had a componentfunction, remove it
            if key in context.children_next:
                del context.children_next[key]

        if el.args or el.kwargs:
            # do this conditionally to make logs cleaner
            logger.debug("Render: arguments... (children of %s,%s)", parent_key, key)
            # only when we landed at a widget leaf, or a shared element, we need to render the children
            if isinstance(el.component, ComponentWidget) or el.is_shared:
                self._visit_children(el, key, parent_key, self._render)
            assert self.context is context
            logger.debug("Render: arguments done (children of %s,%s)", parent_key, key)

        if isinstance(el.component, ComponentFunction):
            # call the function, and recurse into, until we hit leafs
            # find a context from previous reconsolidation phase, or otherwise the previous render run
            context_previous = context.children_next.get(key)

            if context_previous is None:
                context_previous = context.children.get(key)
            parent_context = context
            del context
            if context_previous is not None:
                # We could reuse the same context
                if context_previous.root_element is None and context_previous.root_element_next is None:
                    # this happens when we already created a context (with state) using state_set()
                    context = context_previous
                    context.context_managers = [cm(el) for cm in _component_context_manager_classes]
                    logger.debug("Render: Previous element was None, so we reuse the ComponentContext")
                else:
                    # except when the type has changed
                    assert context_previous.invoke_element is not None
                    if not same_component(context_previous.invoke_element.component, el.component):
                        logger.debug("Render: Not the same component, we just copy the children and elements of the ComponentContext")
                        # The old context is cleaned up in the reconciliation phase
                        context = ComponentContext(parent=parent_context, context_managers=[cm(el) for cm in _component_context_manager_classes])
                        el_prev = None  # we dont want to compare the old element
                    else:
                        logger.debug("Render: Same component: %r", el.component)
                        context = context_previous
                        context.parent = parent_context
                        # TODO: only render dirty components
                        # if not context_previous.needs_render:
                        #     # nothing changed
                        #     logger.info("skipping rendering of %s", key)
                        #     return
            else:
                logger.debug("Render: New ComponentContext")
                context = ComponentContext(parent=parent_context, context_managers=[cm(el) for cm in _component_context_manager_classes])
                el_prev = None  # we dont want to compare the old element
            context.invoke_element = el
            assert context.parent is not None
            self.container_adders = []
            logger.debug("Render: Enter context %r and excuting component function %r", key, el.component.f)
            self.context = context
            render_count = self.render_count
            needs_render = context.needs_render
            if not needs_render:
                if el_prev is not None and context_previous is context:
                    assert not isinstance(el_prev.component, ComponentWidget)
                    needs_render = el._arguments_changed(el_prev)
                if context.exceptions_children:
                    # we have exceptions, so we need to render
                    needs_render = True
            if not needs_render:
                assert el_prev is not None
            try:
                # this is reset in use_exception
                # context.exceptions_children = []
                # TODO: why do the tests pass if we comment the next line out
                context.exceptions_self = []
                if needs_render:
                    context.state_index = 0
                    context.effect_index = 0
                    context.memo_index = 0
                    context.user_contexts = {}
                    context.exception_handler = False
                    # we reset if before calling the component
                    # which might set it to true again
                    context.needs_render = False
                    # Now, we actually execute the render function, and get
                    # back the root element
                    root_element: Optional[Element] = None
                    try:
                        with contextlib.ExitStack() as stack:
                            for cm in context.context_managers:
                                stack.enter_context(cm)
                            if _default_container is not None:
                                with _default_container() as container:
                                    el.component.render_count += 1
                                    root_element = el.component.f(*el.args, **el.kwargs)
                                if root_element is None:
                                    if len(container.kwargs["children"]) == 1:
                                        root_element = container.kwargs["children"][0]
                                    else:
                                        root_element = container
                            else:
                                el.component.render_count += 1
                                root_element = el.component.f(*el.args, **el.kwargs)
                            assert root_element is not None
                    except BaseException as e:
                        if DEBUG:
                            # we might be interested in the traceback inside the call...
                            if len(self.tracebacks) == 0:
                                assert e.__traceback__ is not None
                                traceback = cast(TracebackType, e.__traceback__)
                                if traceback.tb_next:  # is there an error inside the call
                                    self.tracebacks.append(traceback.tb_next)
                            self.tracebacks.append(el.traceback)
                        logger.exception("Component %r raised exception %r", el.component, e)
                        context.exceptions_self.append(e)
                        self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during render"))
                        self._rerender_needed = True
                        context.needs_render = True

                    if root_element is None and not context.exceptions_self:
                        raise ValueError(f"Component {el.component} returned None")
                else:
                    root_element = context.root_element_next or context.root_element

                if self.render_count != render_count:
                    raise RuntimeError("Recursive render detected, possible a bug in react")
                if root_element is not None:
                    logger.debug("root element: %r %x", root_element, id(root_element))
                    new_parent_key = join_key(parent_key, key)
                    self._render(root_element, "/", parent_key=new_parent_key)  # depth first
                    context.root_element_next = root_element
                else:
                    if el.is_shared:
                        # TODO: why do the tests pass if we comment the next line out
                        self._shared_elements_next.remove(el)
                try:
                    # if we had an exception, we allow for LESS hooks calls, since the render body might not be executed completely
                    if not ((context.effect_index == len(context.effects)) or (context.exceptions_self and context.effect_index <= len(context.effects))):
                        raise RuntimeError(
                            f"Previously render had {len(context.effects)} effects, this run {context.effect_index} "
                            f"(in element/component: {el}/{el.component}). "
                            "Are you using conditional hooks?"
                        )
                    if not ((context.memo_index == len(context.memo)) or (context.exceptions_self and context.memo_index <= len(context.memo))):
                        raise RuntimeError(
                            f"Previously render had {len(context.memo)} calls to use_memo, this run {context.memo_index} "
                            f"(in element/component: {el}/{el.component}). "
                            "Are you using conditional hooks?"
                        )
                except RuntimeError as e:
                    logger.exception("Exception in hook count check")
                    context.exceptions_self.append(e)
                    self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during render (hook count check)"))
                    self._rerender_needed = True
                    context.needs_render = True
                # only expose to parent when no error occurs
                context.parent.children_next[key] = context
                # drop all children from the previous render run (this render phase)
                context.children_next = {k: v for k, v in context.children_next.items() if k in context.used_keys}
                # same for elements
                context.elements_next = {k: v for k, v in context.elements_next.items() if k in context.used_keys}
                context.user_contexts_prev = context.user_contexts
            finally:
                assert context.parent is parent_context
                self.context = context.parent
                if context.exceptions_self or context.exceptions_children and not context.exception_handler:
                    # child does not handle exceptions, so bubble up
                    self.context.exceptions_children.extend(context.exceptions_self)
                    self.context.exceptions_children.extend(context.exceptions_children)
                if self.context.exceptions_self or self.context.exceptions_children:
                    if not self._rerender_needed:
                        # this happens when an exception was added from an event handler
                        # this means no exception was raised during the render phase
                        # but we still need to rerender, until someone catches the exception
                        self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during render"))
                        self._rerender_needed = True
                        self.context.needs_render = True

            assert context is not None

    def _reconsolidate(self, el: Element, default_key: str, parent_key: str):
        # we don't use default_key, but we want the same signature for the visitor pattern
        kwargs = el.kwargs.copy()
        key = el._key
        if key is None:
            key = default_key
        assert key is not None
        logger.debug("Reconsolidate: (%s,%s) %r", parent_key, key, el)
        context = self.context
        assert context is not None

        el_prev = context.elements.get(key)

        already_reconsolidated = el in self._shared_elements
        if already_reconsolidated and el is not self.element and el.is_shared:
            logger.debug("Reconsolidate: Using existing widget (prev = %r)", el_prev)
            # keeping this for debugging
            # logger.debug("Current:")
            # for el_ in self._shared_elements:
            #     logger.debug("\t%r", el_)
            # logger.debug("Next:")
            # for el_ in self._shared_elements_next:
            #     logger.debug("\t%r", el_)
            # import pdb
            # pdb.set_trace()

            return self._shared_widgets[el]

        try:
            if isinstance(el.component, ComponentFunction):
                if el_prev and isinstance(el_prev.component, ComponentWidget):
                    self._remove_element(el_prev, default_key=key, parent_key=parent_key)
                new_parent_key = join_key(parent_key, key)
                try:
                    # TODO: test suite passes when this block if commented out
                    if el.is_shared and (el.args or el.kwargs):
                        # do this conditionally to make logs cleaner
                        logger.debug("Reconsolidate: arguments... (children of %s,%s)", parent_key, key)
                        self._visit_children(el, key, parent_key, self._reconsolidate)
                        assert self.context is context
                        logger.debug("Reconsolidate: arguments done (children of %s,%s)", parent_key, key)

                    child_context_prev = context.children.get(key)
                    child_context = context.children_next[key]
                    if child_context_prev is not None and child_context_prev is not child_context:
                        assert el_prev is not None, "prev child is not None, but element is"
                        # this happens when the component type changes
                        # this is not always true, it could be that there are two renders phases before this happened
                        # where the first updated the invoke_element, and the second changed the component
                        # assert child_context_prev.invoke_element is el_prev
                        self._remove_element(el_prev, default_key=key, parent_key=parent_key)

                    logger.debug("Reconsolidate: enter context %r", new_parent_key)
                    self.context = child_context
                    assert child_context.root_element_next
                    elements_now = dict(child_context.elements_next)
                    elements = dict(child_context.elements)

                    widget = self._reconsolidate(child_context.root_element_next, "/", new_parent_key)
                    child_context.root_element = child_context.root_element_next
                    child_context.root_element_next = None
                    # merge the component root level meta dict with the component meta dict
                    # for instance if we do
                    # SomeComonent().meta(name="a") we want that name="a" to appear on the widget
                    if el._meta or getattr(widget, "_react_meta", {}):
                        widget._react_meta = {**getattr(widget, "_react_meta", {}), **el._meta}

                    if el.is_shared:
                        self._shared_widgets[el] = widget
                    else:
                        context.widgets[key] = widget
                    removed = set(elements) - set(elements_now)
                    if removed:
                        logger.info("elements to be removed: %r", removed)
                    if removed:
                        for key_remove in removed:
                            el_remove = elements[key_remove]
                            self._remove_element(el_remove, key_remove, parent_key)
                    for effect_index, effect in enumerate(child_context.effects):
                        if effect.next:
                            # if we have a next, it means that effect itself is executed
                            # TODO: custom equals
                            if effect.next.dependencies is not None and utils.equals(effect.dependencies, effect.next.dependencies):
                                logger.debug("No need to add effect, dependencies are the same (%r %r)", effect.callable, effect.dependencies)
                                # not needed, just remove the reference
                                effect.next = None
                            else:
                                # dependencies changed, cleanup and execute next
                                if not effect._cleaned_up:
                                    try:
                                        effect.cleanup()
                                    except BaseException as e:
                                        context.exceptions_self.append(e)
                                        self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during effect"))
                                        self._rerender_needed = True
                                        context.needs_render = True
                                effect = child_context.effects[effect_index] = effect.next
                                try:
                                    if child_context.exceptions_self or child_context.exceptions_children:
                                        # we had an exception, so we skip the effect (not the cleanup)
                                        continue
                                    effect()
                                except BaseException as e:
                                    context.exceptions_self.append(e)
                                    self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during effect"))
                                    self._rerender_needed = True
                                    context.needs_render = True
                        else:
                            try:
                                if child_context.exceptions_self or child_context.exceptions_children:
                                    # we had an exception, so we skip the effect (not the cleanup)
                                    continue
                                effect()
                            except BaseException as e:
                                context.exceptions_self.append(e)
                                self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during effect"))
                                self._rerender_needed = True
                                context.needs_render = True

                    if child_context.children_next:
                        # if we had two render phases, we can have old context left over
                        # TODO: we could see if we can remove this, and use used_keys instead
                        child_context.children_next.clear()
                    if child_context.elements_next:
                        # we can still have elements that are not used as a 'widget' in this context
                        # but we can still pass them down as an element.
                        unreferenced = []
                        for child_key, child_el in list(child_context.elements_next.items()):
                            if child_el not in self._shared_elements:
                                unreferenced.append(child_el)
                            else:
                                child_context.elements[child_key] = child_context.elements_next.pop(child_key)
                        if unreferenced:
                            raise RuntimeError(f"Unused elements and unreferenced elements {unreferenced}")
                    if child_context.exceptions_self or child_context.exceptions_children and not child_context.exception_handler:
                        # child does not handle exceptions, so bubble up
                        context.exceptions_children.extend(child_context.exceptions_self)
                        context.exceptions_children.extend(child_context.exceptions_children)
                finally:
                    # restore context
                    self.context = context
                    logger.debug("Reconsolidate: leaving context %r", new_parent_key)
                context.children[key] = context.children_next.pop(key)

            else:
                assert isinstance(el.component, ComponentWidget)
                if el.args:
                    raise TypeError("Widget element only take keyword arguments")

                def reconsolidate_children():
                    logger.debug("Reconsolidate: arguments... (children of %s,%s)", parent_key, key)
                    assert key is not None  # make mypy happy
                    new_kwargs = self._visit_children_values(kwargs, key, parent_key, self._reconsolidate)
                    assert self.context is context
                    logger.debug("Reconsolidate: arguments done (children of %s,%s)", parent_key, key)
                    return new_kwargs

                orphan_ids = set()
                widget_previous = None
                if el_prev is not None:
                    if el_prev.is_shared:
                        # TODO: where to remove this?
                        widget_previous = self._shared_widgets[el_prev]
                    else:
                        # TODO: where to remove this?
                        widget_previous = context.widgets[key]
                if widget_previous is None:
                    # initial create
                    kwargs = reconsolidate_children()
                    if el.is_shared and el in self._shared_widgets:
                        raise RuntimeError(f"Element ({el}) was already in self._shared_widgets")
                    else:
                        logger.info("Creating new widget: %r %r", el, key)
                        widget = None
                        if not context.exceptions_children:
                            try:
                                widget, orphan_ids = el._create_widget(kwargs)
                            except BaseException as e:
                                context.exceptions_self.append(e)
                                self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during reconciliation (creating widget)"))
                                self._rerender_needed = True
                        if el.is_shared:
                            self._shared_widgets[el] = widget
                        else:
                            context.widgets[key] = widget
                elif el_prev is not None and el_prev.component == el.component:
                    logger.debug("Updating widget: %r  → %r %r", el_prev, el, key)
                    assert el_prev is not None
                    # TODO: remove event listeners while doing so
                    # assign to _widgets[el] first, before errors can occur
                    kwargs = reconsolidate_children()
                    if not context.exceptions_children:
                        try:
                            el._update_widget(widget_previous, el_prev, kwargs)
                        except BaseException as e:
                            context.exceptions_self.append(e)
                            self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during reconciliation (updating widget)"))
                            self._rerender_needed = True
                    if el.is_shared:
                        self._shared_widgets[el] = widget_previous
                    else:
                        context.widgets[key] = widget_previous
                else:
                    assert el_prev is not None, "widget_previous is not None, but el_prev is"
                    logger.debug("Replacing widget: %r → %r %r", el_prev, el, key)
                    self._remove_element(el_prev, key, parent_key=parent_key)
                    kwargs = reconsolidate_children()
                    widget = None
                    if not context.exceptions_children:
                        try:
                            widget, orphan_ids = el._create_widget(kwargs)
                        except BaseException as e:
                            context.exceptions_self.append(e)
                            self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during reconciliation (updating widget)"))
                            self._rerender_needed = True
                    if el.is_shared:
                        self._shared_widgets[el] = widget
                    else:
                        context.widgets[key] = widget
                # widgets are not always hashable, so store the model_id
                orphan_widgets = set([_get_widgets_dict()[k] for k in orphan_ids])
                if orphan_ids:
                    for orphan_widget in orphan_widgets:
                        # these are shared widgets
                        if orphan_widget.__class__.__name__ == "Template" and orphan_widget.__class__.__module__ == "ipyvue.Template":
                            orphan_ids -= {orphan_widget.model_id}
                    if el.is_shared:
                        widget = self._shared_widgets[el]
                    else:
                        widget = context.widgets[key]
                    if widget.model_id not in self._orphans:
                        self._orphans[widget.model_id] = set()
                    self._orphans[widget.model_id].update(orphan_ids)

            if el.is_shared:
                widget = self._shared_widgets[el]
            else:
                widget = context.widgets[key]
            # used in get_widget
            if el_prev in context.element_to_widget:
                del context.element_to_widget[el_prev]
            context.element_to_widget[el] = widget
            return widget
        except Exception as e:
            if DEBUG:
                # we don't care about the traceback of the root element
                if self.element is not el:
                    # we might be interested in the traceback inside the call...
                    if len(self.tracebacks) == 0:
                        assert e.__traceback__ is not None
                        traceback = cast(TracebackType, e.__traceback__)
                        if traceback.tb_next:  # is there an error inside the call
                            self.tracebacks.append(traceback.tb_next)
                    self.tracebacks.append(el.traceback)
            raise
        finally:
            # this marks the work as 'done'
            # move from _elemens_next to _elements
            context.elements[key] = context.elements_next.pop(key)

            if el_prev in self._shared_elements:
                self._shared_elements.remove(el_prev)

            if el.is_shared:
                assert el not in self._shared_elements
                self._shared_elements.add(el)

            if el.is_shared:
                assert el in self._shared_elements_next
                if el in self._shared_elements_next:
                    self._shared_elements_next.remove(el)
            assert self.context is not None

            # Remove unused element.
            # It is a bit odd that we do this for each element type, so this get executed
            # multiple times for each context. But if we only do this for a ComponentFunction element
            # we have to do this separately for the root element as well.
            # NOTE: keep this sorted for reproducation reasons
            extra = list(sorted(set(self.context.elements.keys()) - self.context.used_keys))
            if extra:
                for key in list(extra):
                    if key in self.context.elements:
                        self._remove_element(self.context.elements[key], key, parent_key=parent_key)

            # keeping this for debugging
            # logger.debug("Current:")
            # for el_ in self._shared_elements:
            #     logger.debug("\t%r", el_)
            # logger.debug("Next:")
            # for el_ in self._shared_elements_next:
            #     logger.debug("\t%r", el_)

    def _remove_element(self, el: Element, default_key: str, parent_key):
        key = el._key
        if key is None:
            key = default_key
        assert key is not None
        assert self.context is not None
        context = self.context
        logger.debug("Remove: (%s, %s) %r", parent_key, key, el)

        if el.is_shared:
            if el not in self._shared_elements:
                return
            assert el in self._shared_elements
            self._shared_elements.remove(el)

        if key not in context.elements:
            # for instance if we first remove a root element, which also removes all its children,
            # and we then remove some child element again, it is already removed.
            return

        if isinstance(el.component, ComponentFunction):
            if el.is_shared:
                self._visit_children(el, key, parent_key, self._remove_element)
            try:
                self.context = child_context = context.children[key]
                # we are removing the element, so we want to handle the
                # exceptions any more, only if the cleanup fails
                child_context.exceptions_self = []
                child_context.exceptions_children = []

                for effect_index, effect in enumerate(self.context.effects):
                    try:
                        if not effect._cleaned_up:
                            effect.cleanup()
                    except BaseException as e:
                        child_context.exceptions_self.append(e)
                        self._rerender_needed_reasons.append(RerenderReason(reason="Exception ocurred during effect"))
                        self._rerender_needed = True
                assert self.context.root_element is not None
                new_parent_key = join_key(parent_key, key)
                self._remove_element(self.context.root_element, "/", parent_key=new_parent_key)
            finally:
                try:
                    assert not child_context.elements, f"left over elements {child_context.elements}"
                    assert not child_context.element_to_widget, f"left over element_to_widget {child_context.element_to_widget}"
                    assert not child_context.widgets, f"left over widgets {child_context.widgets}"
                    assert not child_context.children, f"left over children {child_context.children}"
                    assert not child_context.owns, f"left over owns {child_context.owns}"
                    # TODO: this is not the case when an exception occurs
                    # assert not child_context.children_next, f"left over children {child_context.children_next}"
                except Exception as e:
                    child_context.exceptions_self.append(e)

                # restore context
                self.context = context
            if child_context.exceptions_self or child_context.exceptions_children and not child_context.exception_handler:
                # child does not handle exceptions, so bubble up
                context.exceptions_children.extend(child_context.exceptions_self)
                context.exceptions_children.extend(child_context.exceptions_children)
            del context.children[key]
        else:
            self._visit_children(el, key, parent_key, self._remove_element)
            if el.is_shared:
                widget = self._shared_widgets[el]
            else:
                widget = context.widgets[key]
            if widget is not None:
                assert widget.comm is not None
                assert widget.model_id in _get_widgets_dict()

                for orphan in self._orphans.get(widget.model_id, set()):
                    orphan_widget = _get_widgets_dict().get(orphan)
                    if orphan_widget:
                        close_widget(orphan_widget)
                if widget.model_id in self._orphans:
                    del self._orphans[widget.model_id]
                el._cleanup_callbacks(widget)
                el._close_widget(widget)
        if el.is_shared:
            del self._shared_widgets[el]
        else:
            del context.widgets[key]
        # elements can be removed multiple times, since they can be added multiple times
        # (even non-shared element can)
        if el in context.element_to_widget:
            del context.element_to_widget[el]
        del context.elements[key]

    def _visit_children(self, el: Element, default_key: str, parent_key: str, f: Callable):
        assert self.context is not None
        key = el._key
        if key is None:
            key = default_key
        assert key is not None
        self._visit_children_values(el.kwargs, key, parent_key, f)
        self._visit_children_values(el.args, key, parent_key, f)

    def _visit_children_values(self, value: Any, key: str, parent_key: str, f: Callable):
        if isinstance(value, Element):
            return f(value, key, parent_key)
        elif isinstance(value, (list, tuple)):
            was_tuple = isinstance(value, tuple)
            values = []
            for index, v in enumerate(value):
                new_value = self._visit_children_values(v, f"{key}{index}/", parent_key, f)
                if isinstance(new_value, FragmentWidget):
                    values.extend(new_value.children)
                else:
                    values.append(new_value)
            if was_tuple:
                return tuple(values)
            return values
        elif isinstance(value, dict):
            return {k: self._visit_children_values(v, f"{key}{k}/", parent_key, f) for k, v in value.items()}
        else:
            return value


@overload
def render(
    element: Element[T], container: None = None, children_trait="children", handle_error: bool = True, initial_state=None
) -> Tuple[widgets.HBox, _RenderContext]: ...


@overload
def render(
    element: Element[T], container: None = None, children_trait="children", handle_error: bool = True, initial_state=None
) -> Tuple[widgets.Widget, _RenderContext]: ...


def render(element: Element[T], container: widgets.Widget = None, children_trait="children", handle_error: bool = True, initial_state=None):
    container = container or widgets.VBox()
    _rc = _RenderContext(element, container, children_trait=children_trait, handle_error=handle_error, initial_state=initial_state)
    _rc.render(element, _rc.container)
    local.last_rc = weakref.ref(_rc)
    return container, _rc


def render_fixed(element: Element[T], handle_error: bool = True) -> Tuple[T, _RenderContext]:
    _rc = _RenderContext(element, handle_error=handle_error)
    widget = _rc.render(element)
    local.last_rc = weakref.ref(_rc)
    return widget, _rc


_colab_enabled_custom_widget_manager = False


def _ensure_colab_fixes():
    if utils.environment() == "colab":
        if "ipyvuetify" in sys.modules:
            import IPython.display  # type: ignore

            # we probably want to use ipyvuetify
            # so we need to enable the custom widget manager
            global _colab_enabled_custom_widget_manager
            if not _colab_enabled_custom_widget_manager:
                from google.colab import output

                output.enable_custom_widget_manager()
                _colab_enabled_custom_widget_manager = True
            import ipyvue

            IPython.display.display(ipyvue.Html(tag="span", style_="display: none"))


def display(el: Element, mime_bundle: Dict[str, Any] = mime_bundle_default):
    import IPython.display  # type: ignore

    _ensure_colab_fixes()

    box = widgets.VBox(_view_count=0)
    el = _wrap(el, jupyter_decorator_components)
    widget, rc = render(el, container=box)
    displayed = False

    def check_view_count(change):
        nonlocal displayed
        if not displayed and change.new > 0:
            displayed = True
        if displayed and change.new == 0:
            rc.close()
            box.layout.close()
            box.close()

    box.observe(check_view_count, "_view_count")

    data: Dict[str, Any] = {
        **mime_bundle_default,
        **mime_bundle,
        MIME_WIDGETS: {"version_major": 2, "version_minor": 0, "model_id": widget._model_id},
    }
    IPython.display.display(data, raw=True)
    if ipywidget_version_major < 8:
        widget._handle_displayed()


# list of decorators that wrap an element when displayed
# in a jupyter environment, like notebook, or lab via _ipython_display_
jupyter_decorator_components: List[Callable[..., Element]] = []


def _wrap(el: Element, decorators: List[FuncT]) -> Element:
    for c in jupyter_decorator_components:
        el = c(children=[el])
    return el


def make(el: Element, handle_error: bool = True):
    hbox = widgets.VBox(_view_count=0)
    _, rc = render(el, hbox, "children", handle_error=handle_error)
    return hbox


def component_interactive(static=None, **kwargs):
    import IPython.display

    static = static or {}

    def make(f):
        global _last_interactive_vbox
        c = component(f)
        el0 = c(**{**static, **kwargs})
        container, rc = render(el0)

        def f_wrap(**kwargs):
            element = c(**{**static, **kwargs})
            rc.render(element)

        control = widgets.interactive(f_wrap, **kwargs)
        control.update()
        result = widgets.VBox([control, container])
        _last_interactive_vbox = result
        IPython.display.display(result)
        return result

    return make


def __getattr__(name):
    if name == "_last_rc":
        last_rc_ref = getattr(local, "last_rc", None)
        return last_rc_ref() if last_rc_ref else None
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


class FragmentWidget(widgets.VBox):
    def __init__(self, children, **kwargs):
        super().__init__(children=children, **kwargs)


@component
def Fragment(children: List[Element]):
    return FragmentWidget.element(children=children)


_last_interactive_vbox = None
_default_container: Optional[Callable[..., Element]] = Fragment
# not a public api yet, used in solara for now only.
# lifecycle of context objects are linked to the lifecycle of the component
_component_context_manager_classes: List[Any] = []
