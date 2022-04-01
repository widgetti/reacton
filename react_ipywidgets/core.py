"""Write ipywidgets like React

ReactJS - ipywidgets relation:
 * DOM nodes -- Widget
 * Element -- Element
 * Component -- function

"""

import inspect
import logging  # type: ignore
import sys
import threading
from inspect import isclass
from types import GeneratorType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
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

import ipywidgets as widgets
import rich.traceback

from . import _version

__version__ = _version.__version__
T = TypeVar("T")
U = TypeVar("U")
W = TypeVar("W")  # used for widgets
E = TypeVar("E")  # used for elements

WidgetOrList = Union[widgets.Widget, List[widgets.Widget]]
EffectCleanupCallable = Callable[[], None]
EffectCallable = Callable[[], Optional[EffectCleanupCallable]]
KEY_NAME = "__key__"
logger = logging.getLogger("react")  # type: ignore
DEBUG = 1
TRACEBACK_LOCALS = 1
MIME_WIDGETS = "application/vnd.jupyter.widget-view+json"


widget_render_error_msg = (
    """Cannot show widget. You probably want to rerun the code cell above (<i>Click in the code cell, and press Shift+Enter <kbd>⇧</kbd>+<kbd>↩</kbd></i>)."""
)

mime_bundle_default = {"text/plain": "Cannot show ipywidgets in text", "text/html": widget_render_error_msg}


def element(cls, **kwargs):
    return ComponentWidget(cls)(**kwargs)


widgets.Widget.element = classmethod(element)


class ComponentCreateError(RuntimeError):
    def __init__(self, rich_traceback):
        super().__init__(rich_traceback)
        self.rich_traceback = rich_traceback


class Component:
    def __call__(self, *args, **kwargs) -> Union[widgets.Widget, "Element"]:
        pass


class Element(Generic[W]):
    def __init__(self, component, *args, **kwargs):
        self.component = component
        self.mime_bundle = mime_bundle_default
        self.args = args
        self.kwargs = kwargs
        self.handlers = []
        self._current_context = None
        rc = _get_render_context(required=False)
        if rc:
            self._current_context = rc.context
        if rc and rc.context.container_adders:
            rc.context.container_adders[-1].add(self)
        if DEBUG:
            # since we construct widgets or components from a different code path
            # we want to preserve the original call stack, by manually tracking frames
            try:
                assert False
            except AssertionError:
                self.traceback = sys.exc_info()[2]

            assert self.traceback is not None
            assert self.traceback.tb_frame is not None
            assert self.traceback.tb_frame.f_back is not None
            frame_py = self.traceback.tb_frame.f_back.f_back
            assert frame_py is not None
            filename = inspect.getsourcefile(frame_py) or "<unknown>"
            locals = frame_py.f_locals
            name = "unknown"
            if rc:
                parent_component = rc.context.element.component
                assert isinstance(parent_component, ComponentFunction)
                name = parent_component.f.__name__
            self.frame = rich.traceback.Frame(filename=filename, lineno=frame_py.f_lineno, name=name, locals=locals if TRACEBACK_LOCALS else None)

    def split_kwargs(self, kwargs):
        listeners = {}
        normal_kwargs = {}
        assert isinstance(self.component, ComponentWidget)
        args = self.component.widget.class_trait_names()
        for name, value in kwargs.items():
            if name.startswith("on_") and name not in args:
                listeners[name[3:]] = value
            else:
                normal_kwargs[name] = value
        return normal_kwargs, listeners

    def handle_custom_kwargs(self, widget: widgets.widgets.Widget, kwargs):
        listeners = kwargs
        for name, listener in listeners.items():

            def add_event_handler(name=name, listener=listener):
                def event_handler(change):
                    listener(change.new)

                def cleanup():
                    widget.unobserve(event_handler, name)

                widget.observe(event_handler, name)
                return cleanup

            use_side_effect(add_event_handler)

    def __repr__(self):
        args = ", ".join(f"{key} = {value!r}" for key, value in self.kwargs.items())
        if isinstance(self.component, ComponentFunction):
            name = self.component.f.__name__
            return f"{name}({args})"
        if isinstance(self.component, ComponentWidget):
            name = self.component.widget.__module__ + "." + self.component.widget.__name__
            return f"{name}.element({args})"
        else:
            raise RuntimeError(f"No repr for {type(self)}")

    def on(self, name, callback):
        self.handlers.append((name, callback))
        return self

    def _ipython_display_(self, **kwargs):
        display(self, self.mime_bundle)

    def __enter__(self):
        rc = _get_render_context()
        ca = ContainerAdder[T](self, "children")
        assert rc.context is self._current_context, f"Context change from {self._current_context} -> {rc.context}"
        rc.context.container_adders.append(ca)
        return self

    def __exit__(self, *args, **kwargs):

        rc = _get_render_context()
        assert rc.context is self._current_context, f"Context change from {self._current_context} -> {rc.context}"
        ca = rc.context.container_adders.pop()
        ca.assign()


FuncT = TypeVar("FuncT", bound=Callable[..., Element])


def find_children(el):
    children = set()
    if not isinstance(el.kwargs, dict):
        raise RuntimeError("keyword arguments for {el} should be a dict, not {el.kwargs}")
    for arg in list(el.kwargs.values()) + list(el.args):
        if isinstance(arg, Element):
            children.add(arg)
        elif isinstance(arg, (tuple, list)):
            for child in arg:
                if isinstance(child, Element):
                    children.add(child)
                    children |= find_children(child)
        elif isinstance(arg, dict):
            for child in arg.values():
                if isinstance(child, Element):
                    children.add(child)
                    children |= find_children(child)
    return children


class ContainerAdder(Generic[W]):
    def __init__(self, el: Element[W], prop_name: str):
        self.el = el
        self.prop_name = prop_name
        self.created: List[Element] = []

    def add(self, el):
        self.created.append(el)

    def assign(self):
        children = set()
        for el in self.created:
            children |= find_children(el)
        top_level = [k for k in self.created if k not in children]
        if self.prop_name not in self.el.kwargs:
            self.el.kwargs[self.prop_name] = []
        # generic way to add to a list or tuple
        container_prop_type = type(self.el.kwargs[self.prop_name])
        self.el.kwargs[self.prop_name] = self.el.kwargs[self.prop_name] + container_prop_type(top_level)


class ComponentWidget(Component):
    def __init__(self, widget: Type[widgets.Widget], mime_bundle=mime_bundle_default):
        self.mime_bundle = mime_bundle
        self.widget = widget

    def __repr__(self):
        return f"Component[{self.widget!r}]"

    def __call__(self, *args, **kwargs):
        el: Element = Element(self, *args, **kwargs)
        # TODO: temporary, we cannot change the constructor
        # otherwise we need to generate the wrapper code again for all libraries
        el.mime_bundle = self.mime_bundle
        return el


class ComponentFunction(Component):
    def __init__(self, f: Callable[[], Union[Iterable[Element], Element]], mime_bundle=mime_bundle_default):
        self.mime_bundle = mime_bundle
        self.f = f

    def __call__(self, *args, **kwargs):
        el: Element = Element(self, *args, **kwargs)
        el.mime_bundle = self.mime_bundle
        return el


# it is actually this...
# def component(obj: Union[Type[widgets.Widget], FuncT]) -> Union[ComponentWidget, ComponentFunction[FuncT]]:
# but this gives much better type hints (e.g. argument types checks etc)


@overload
def component(obj: None = None, mime_bundle=...) -> Callable[[FuncT], FuncT]:
    ...


@overload
def component(obj: FuncT, mime_bundle=...) -> FuncT:
    ...


def component(obj: FuncT = None, mime_bundle: Dict[str, Any] = mime_bundle_default):
    def wrapper(obj: FuncT) -> FuncT:
        if isclass(obj) and issubclass(obj, widgets.Widget):
            return cast(FuncT, ComponentWidget(widget=obj, mime_bundle=mime_bundle))
        else:
            return cast(FuncT, ComponentFunction(f=obj, mime_bundle=mime_bundle))

    if obj is not None:
        return wrapper(obj)
    else:
        return wrapper


def force_update():
    rc = _get_render_context()
    rc.force_update()


def get_widget(el: Element):
    """Returns the real underlying widget, can only be used in use_side_effect"""
    rc = _get_render_context()
    if el not in rc._widgets:
        raise KeyError(f"Element {el} not found in all known widgets for the component {rc._widgets}")
    return rc._widgets[el]


def use_state(initial: T, key: str = None, eq: Callable[[Any, Any], bool] = None) -> Tuple[T, Callable[[Union[T, Callable[[T], T]]], T]]:
    """Returns a (value, setter) tuple that is used to manage state in a component.

    This function can only be called from a component function.

    The value rturns the current state (which equals initial at the first render call).
    Or the value that was last

    Subsequent
    """
    global _rc
    if _rc is None:
        raise RuntimeError("No render context")
    return _rc.use_state(initial, key, eq)


def use_side_effect(effect: EffectCallable, dependencies=None):
    global _rc
    if _rc is None:
        raise RuntimeError("No render context")
    return _rc.use_side_effect(effect, dependencies=dependencies)


def use_state_widget(widget: widgets.Widget, prop_name):
    global _rc
    if _rc is None:
        raise RuntimeError("No render context")
    initial_value = getattr(widget, prop_name)
    value, setter = use_state(initial_value)
    if _rc.first_render:

        def handler(change):
            setter(change.new)  # type: ignore

        widget.observe(handler, prop_name)
    return value


def _get_render_context(required=True):
    global _rc
    if _rc is None and required:
        raise RuntimeError("No render context")
    return _rc


def use_reducer(reduce: Callable[[T, U], T], initial_state: T) -> Tuple[T, Callable[[U], None]]:
    state, set_state = use_state(initial_state)

    def dispatch(action):
        new_state = reduce(state, action)
        set_state(new_state)

    return state, dispatch


def use_context(key: str):
    rc = _get_render_context()
    value = None
    context = rc.context
    while value is None and context is not None:
        value = context.user_contexts.get(key)
        context = context.parent
    if value is None:
        raise KeyError(f"No value found in element or parent element under key {key}")
    return value


def use_memo(f, debug_name: str = None, args: Optional[List] = None, kwargs: Optional[Dict] = None):
    if debug_name is None:
        debug_name = f.__name__
    rc = _get_render_context()
    if args is None and kwargs is None:

        def wrapper(*args, **kwargs):
            return rc.use_memo(f, args, kwargs, debug_name)

        return wrapper
    else:
        return rc.use_memo(f, args, kwargs, debug_name)


def use_callback(f, dependencies):
    def wrapper(*ignore):
        return f

    use_memo(wrapper, args=dependencies)


def provide_context(key: str, obj: Any):
    rc = _get_render_context()
    context = rc.context
    context.user_contexts[key] = obj


class ComponentContext:
    def __init__(self, parent=None, element: Element = None) -> None:
        self.parent = parent
        self.element = element
        self.state: Dict = {}
        self.effects: List[Effect] = []
        self.widgets: Dict[str, widgets.Widget] = {}
        self.used_arguments: Dict[str, Set[str]] = {}
        self.state_index = 0
        self.effect_index = 0
        self.memo_index = 0
        self.children: Dict[str, ComponentContext] = {}
        self.result: WidgetOrList = None
        self.user_contexts: Dict[Any, Any] = {}
        self.memo: List[Any] = []
        self.container_adders: List[ContainerAdder] = []
        self.needs_render: bool = False


TEffect = TypeVar("TEffect", bound="Effect")


class Effect:
    def __init__(self, callable: EffectCallable, dependencies: Optional[List[Any]] = None, previous: Optional[TEffect] = None) -> None:
        self.callable = callable
        self.dependencies = dependencies
        self.cleanup: Optional[EffectCleanupCallable] = None
        self.previous = previous
        self._done = False

    def __call__(self):
        if self._done:
            return
        if self.previous:
            if self.previous.cleanup:
                self.previous.cleanup()
                self.previous.cleanup = None  # reset so we don't call it again
        self.cleanup = self.callable()
        self._done = True


class _RenderContext:
    context: Optional[ComponentContext] = None

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
            context.children[name] = ComponentContext(parent=context)
            self.state_set(context.children[name], state)

    def __init__(self, element: Element, container: widgets.Widget = None, children_trait="children", handle_error: bool = True, initial_state=None):
        self.element = element
        self.container = container
        self.children_trait = children_trait
        self.first_render = True
        self.context = ComponentContext()
        self.context_root = self.context
        self.pool: Dict[Type[widgets.Widget], List[widgets.Widget]] = {}
        self.render_count = 0
        self.last_root_widget: widgets.Widget = None
        self._is_rendering = False
        self._state_changed = False
        self._state_changed_reason: Optional[str] = None
        self.thread_lock = threading.RLock()
        self.frames: List[Any] = []
        self.handle_error = handle_error
        if initial_state:
            self.state_set(self.context_root, initial_state)
        self._widgets: Dict[Element, widgets.Widget] = {}

    def use_memo(self, f, args, kwargs, debug_name: str = None):
        assert self.context is not None
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        name = debug_name or "no-name"
        if len(self.context.memo) <= self.context.memo_index:
            self.context.memo_index += 1
            value = f(*args, **kwargs)
            memo = (value, (args, kwargs))
            self.context.memo.append(memo)
            logger.info("Initial memo = %r for index %r (debug-name: %r)", memo, self.context.memo_index - 1, name)
            return value
        else:
            memo = self.context.memo[self.context.memo_index]
            value, dependencies = memo
            if dependencies == (args, kwargs):
                logger.info("Got memo hit = %r for index %r (debug-name: %r)", memo, self.context.memo_index, name)
            else:
                logger.info("Replace memo with = %r for index %r (debug-name: %r)", memo, self.context.memo_index, name)
                value = f(*args, **kwargs)
                memo = (value, (args, kwargs))
                self.context.memo[self.context.memo_index] = memo
            self.context.memo_index += 1
            return value

    def use_state(self, initial, key: str = None, eq: Callable[[Any, Any], bool] = None) -> Tuple[T, Callable[[T], T]]:
        assert self.context is not None
        if key is None:
            key = str(self.context.state_index)
            self.context.state_index += 1
        if key not in self.context.state:
            self.context.state[key] = initial
            logger.info("Initial state = %r for key %r", initial, key)
            return initial, self.make_setter(key, self.context, eq)
        else:
            state = self.context.state[key]
            logger.info("Got state = %r for key %r", state, key)
            return state, self.make_setter(key, self.context, eq)

    def make_setter(self, key, context: ComponentContext, eq: Callable[[Any, Any], bool] = None):
        def set(value):
            if callable(value):
                value = value(context.state[key])
            logger.info("Set state = %r for key %r (previous value was %r)", value, key, context.state[key])

            should_update = not eq(context.state[key], value) if eq is not None else context.state[key] != value

            if should_update:
                context.state[key] = value
                context.needs_render = True
                if self._state_changed is False:
                    self._state_changed = True
                    self._state_changed_reason = f"{key} changed"
                if not self._is_rendering:
                    self.render(self.element, self.container)
                else:
                    logger.info("No render phase triggered, already rendering")

        return set

    def force_update(self):
        if not self._is_rendering:
            self.render(self.element, self.container)

    def use_side_effect(self, effect: EffectCallable, dependencies=None):
        assert self.context is not None
        if len(self.context.effects) <= self.context.effect_index:
            self.context.effect_index += 1
            self.context.effects.append(Effect(effect, dependencies))
            logger.info("Initial effect = %r for index %r (%r)", effect, self.context.effect_index - 1, dependencies)
        else:
            previous_effect = self.context.effects[self.context.effect_index]
            if previous_effect:
                if dependencies is not None and previous_effect.dependencies == dependencies:
                    logger.info("No need to add effect, dependencies are the same (%r)", dependencies)
                    self.context.effect_index += 1
                    return
            logger.info("Got new effect = %r for index %r (%r != %r)", effect, self.context.effect_index, dependencies, previous_effect.dependencies)
            self.context.effects[self.context.effect_index] = Effect(effect, dependencies, previous=previous_effect)
            self.context.effect_index += 1

    def render(self, element: Element, container: widgets.Widget = None):
        global _rc
        with self.thread_lock:
            try:
                _rc = self
                return self._render(element, container)
            except ComponentCreateError as e:
                if self.handle_error:
                    from rich.console import Console

                    console = Console()
                    console.print(e.rich_traceback)
                else:
                    raise e
            finally:
                _rc = None  # type: ignore

    def _render(self, element: Element, container: widgets.Widget = None):
        main_render_phase = not self._is_rendering
        render_count = self.render_count  # make a copy
        logger.info("Render phase: %r %r", self.render_count, "main" if main_render_phase else "(nested)")
        # we will reset this every render loop, since new element are created every render loop
        self._widgets = {}
        self._is_rendering = True
        self._state_changed = False
        self.render_count += 1
        # if we got called recursively, self.context is not the root context
        context_prev = self.context
        self.context = self.context_root
        self.context.element = element
        container = container or self.container
        assert self.context is not None
        try:
            frame = rich.traceback.Frame(filename=__file__, lineno=inspect.getsourcelines(self.update)[1], name="update")
            self.frames.append(frame)
            widget = self.update(element, "children")
            if self.last_root_widget is None:
                self.last_root_widget = widget
            else:
                if container is None:
                    if self.last_root_widget != widget:
                        raise ValueError(
                            "You are not using a container, and the root component returned a new widget,"
                            "make sure your root component always returns the same component type"
                        )
                assert self.context is self.context_root
            is_sequence = isinstance(widget, (list, tuple))
            self._widgets = {}
            if container:
                if is_sequence:
                    container.children = list(widget)
                else:
                    container.children = [widget]
            self.first_render = False
        finally:
            if DEBUG:
                self.frames.pop()
            if main_render_phase:
                # we started the rendering loop, so we keep going
                while self._state_changed:
                    logger.info("Entering nested render phase: %r", self._state_changed_reason)
                    self._render(element, container)
                assert self.context is self.context_root
                self._is_rendering = False
            self.context = context_prev
            logger.info("Done with render phase: %r", render_count)
        if not container:
            return widget

    def update(self, element: Element, key: str) -> widgets.Widget:
        assert self.context is not None
        if not isinstance(element, Element):
            raise TypeError(f"Expected element, not {element}")
        el = element
        if isinstance(el.component, ComponentWidget):
            # leaf widget node
            assert not el.args, "no positional args supported for widgets"
            widget = self.update_widget(el, key)
            return widget
        elif isinstance(el.component, ComponentFunction):
            if el in self._widgets:
                return self._widgets[el]
            if KEY_NAME in el.kwargs:
                key = el.kwargs.pop(KEY_NAME)
            # call the function, and recurse into, until we hit leafs
            if key in self.context.children:
                self.context = self.context.children[key]
                if self.context.element is None:
                    # what about when element changes.. ?
                    self.context.element = el
                else:
                    if self.context.element.component != el.component:
                        # TODO: cleanup old context
                        self.context = ComponentContext(parent=self.context.parent, element=el)
                        self.context.parent.children[key] = self.context
            else:
                self.context = ComponentContext(parent=self.context, element=el)
                self.context.parent.children[key] = self.context
            logger.debug("enter context %r", key)
            render_count = self.render_count
            try:
                self.context.state_index = 0
                self.context.effect_index = 0
                self.context.memo_index = 0
                try:
                    # the call that creates the component
                    if DEBUG:
                        self.frames.append(el.frame)
                    child = el.component.f(*el.args, **el.kwargs)
                except Exception as e:
                    if self.handle_error:
                        # get the real exception
                        assert e.__traceback__ is not None
                        traceback = e.__traceback__
                        if traceback.tb_next:  # we prefer to skip the traceback with el.component.f(..) abiove
                            traceback = traceback.tb_next
                        frame_py = traceback.tb_frame
                        filename = inspect.getsourcefile(frame_py) or "<unkown>"
                        locals = frame_py.f_locals
                        name = el.component.f.__name__
                        frame = rich.traceback.Frame(filename=filename, lineno=frame_py.f_lineno, name=name, locals=locals if TRACEBACK_LOCALS else None)
                        self.frames.append(frame)

                        stack = rich.traceback.Stack(str(type(e)), str(e), frames=self.frames.copy())
                        trace = rich.traceback.Trace(stacks=[stack])
                        tb = rich.traceback.Traceback(trace)
                        raise ComponentCreateError(tb)
                    else:
                        raise
                if isinstance(child, GeneratorType):
                    child = list(child)
                if self.render_count != render_count:
                    raise RuntimeError(
                        "Update detected while rendering component, please don't call set_state in the main "
                        "body of your component as this will cause an infinite loop"
                    )
                is_sequence = isinstance(child, (list, tuple))
                if is_sequence:
                    children = cast(Iterable[Element], child)
                else:
                    children = [cast(Element, child)]
                widgets = []
                for i, child in enumerate(children):
                    key_i = f"{key}-{i}"
                    widget = self.update(child, key_i)
                    widgets.append(widget)
                result = widgets if is_sequence else widgets[0]
                self.context.result = result
                self._widgets[el] = result

                for effect in self.context.effects:
                    effect()

            finally:
                self.context = self.context.parent
                if DEBUG:
                    self.frames.pop()
            assert self.context is not None
            return result
        else:
            raise NotImplementedError

    def update_widget(self, element: Element, key: str) -> widgets.Widget:
        assert self.context is not None
        el = element
        assert isinstance(el.component, ComponentWidget)
        component: ComponentWidget = el.component
        normal_kwargs = {}

        # TODO: we may want to have custom keys
        if KEY_NAME in el.kwargs:
            key = el.kwargs.pop(KEY_NAME)
        logger.debug("update widget for element %r with key %r", el, key)

        current_widget = self.context.widgets.get(key)
        if current_widget is None:
            # we might have already created the widget for this
            current_widget = self._widgets.get(el)
            if current_widget:
                logger.debug("current widget in element cache key=%r: %r", key, current_widget)
                return current_widget
        else:
            logger.debug("current widget in widget cache key=%r: %r", key, current_widget)
        normal_kwargs, custom_kwargs = el.split_kwargs(el.kwargs)
        normal_kwargs = {name: self._possible_create_widget(key, name, value) for name, value in normal_kwargs.items()}
        if type(current_widget) is not component.widget:
            # if not the same, add to pool for reuse
            self.add_to_pool(current_widget)
            current_widget = None
        if current_widget is not None:
            with current_widget.hold_sync():
                for name, value in normal_kwargs.items():
                    self.update_widget_prop(current_widget, name, value)
                # if we previously gave an argument, but now we don't
                # we have to restore the default
                cls = current_widget.__class__
                traits = cls.class_traits()
                dropped_arguments = set(self.context.used_arguments[key]) - set(normal_kwargs)
                for name in dropped_arguments:
                    value = traits[name].default()
                    self.update_widget_prop(current_widget, name, value)
        else:
            widget = component.widget(**normal_kwargs)
            # we only add widgets to the cache where they are originally are created
            # other references have to get the same widget via the element cache
            self.context.widgets[key] = widget
            logger.debug("create new widget for key %r %r", key, widget)
        self.context.used_arguments[key] = set(normal_kwargs)

        if current_widget:
            widget = current_widget

        # make sure we can reused the widget belonging to this element
        # so we don't create it twice
        self._widgets[el] = widget

        el.handle_custom_kwargs(widget, custom_kwargs)

        return widget

    def update_widget_prop(self, widget: widgets.Widget, name, value):
        setattr(widget, name, value)

    def _possible_create_widget(self, key, name, value):
        if isinstance(value, Element):
            value = self.update(value, f"{key}_{name}")
        elif isinstance(value, (list, tuple)):
            was_tuple = isinstance(value, tuple)
            value = [self._possible_create_widget(key, f"{key}_{name}_{i}", k) for i, k in enumerate(value)]
            if was_tuple:
                value = tuple(value)
        elif isinstance(value, dict):
            value = {k: self._possible_create_widget(key, f"{key}`_{name}_{k}", v) for k, v in value.items()}
        return value

    def add_to_pool(self, widget: widgets.Widget):
        self.pool[type(widget)] = widget


_rc = None


def render(element: Element[T], container: widgets.Widget, children_trait="children", handle_error: bool = True, initial_state=None) -> _RenderContext:
    _rc = _RenderContext(element, container, children_trait=children_trait, handle_error=handle_error, initial_state=initial_state)
    _rc.render(element, container)
    return _rc


def render_fixed(element: Element[T], handle_error: bool = True) -> Tuple[T, _RenderContext]:
    _rc = _RenderContext(element, handle_error=handle_error)
    widget = _rc.render(element)
    return widget, _rc


def display(el: Element, mime_bundle: Dict[str, Any] = mime_bundle_default):
    import IPython.display  # type: ignore

    widget = make(el)

    data: Dict[str, Any] = {
        **mime_bundle_default,
        **mime_bundle,
        MIME_WIDGETS: {"version_major": 2, "version_minor": 0, "model_id": widget._model_id},
    }
    IPython.display.display(data, raw=True)
    widget._handle_displayed()


def make(el: Element, handle_error: bool = True):
    hbox = widgets.VBox()
    render(el, hbox, "children", handle_error=handle_error)
    return hbox


def component_interactive(static=None, **kwargs):
    import IPython.display

    static = static or {}

    def make(f):
        c = component(f)
        container = widgets.VBox()
        el0 = c(**{**static, **kwargs})
        _rc = _RenderContext(el0, container, children_trait="children")

        def f_wrap(**kwargs):
            element = c(**{**static, **kwargs})
            _rc.render(element, container)

        control = widgets.interactive(f_wrap, **kwargs)
        control.update()
        result = widgets.VBox([control, container])
        IPython.display.display(result)
        return result

    return make
