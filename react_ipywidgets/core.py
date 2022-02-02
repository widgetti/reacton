"""Write ipywidgets like React

React - ipywidgets relation:
 * DOM nodes -- Widget
 * Element -- Element
 * Component -- function

"""

import logging  # type: ignore
from inspect import isclass
from types import GeneratorType
from typing import Any, Callable, Dict, Generic, Iterable, List, Optional, Tuple, Type, TypeVar, Union, cast

import ipywidgets as widgets  # type: ignore

from . import _version

__version__ = _version.__version__
T = TypeVar("T")
WidgetOrList = Union[widgets.Widget, List[widgets.Widget]]
EffectCleanupCallable = Callable[[], None]
EffectCallable = Callable[[WidgetOrList], Optional[EffectCleanupCallable]]
KEY_NAME = "__key__"
logger = logging.getLogger("ipyreactive")  # type: ignore


def element(cls, **kwargs):
    return ComponentWidget(cls)(**kwargs)


widgets.Widget.element = classmethod(element)


class Component:
    def __call__(self, *args, **kwargs) -> Union[widgets.Widget, "Element"]:
        pass


class Element(Generic[T]):
    def __init__(self, component, *args, **kwargs):
        self.component = component
        self.args = args
        self.kwargs = kwargs
        self.handlers = []

    def __repr__(self):
        return f"{self.component}.element(**{self.kwargs})"

    def on(self, name, callback):
        self.handlers.append((name, callback))
        return self

    def _ipython_display_(self, **kwargs):
        display(self)


class ComponentWidget(Component):
    def __init__(self, widget: Type[widgets.Widget]):
        self.widget = widget

    def __call__(self, *args, **kwargs):
        return Element(self, *args, **kwargs)


class ComponentFunction(Component):
    def __init__(self, f: Callable[[], Union[Iterable[Element], Element]]):
        self.f = f

    def __call__(self, *args, **kwargs):
        return Element(self, *args, **kwargs)


def component(obj: Union[Type[widgets.Widget], Callable]) -> Component:
    if isclass(obj) and issubclass(obj, widgets.Widget):
        return ComponentWidget(widget=obj)
    else:
        return ComponentFunction(f=obj)


def use_state(initial: T) -> Tuple[T, Callable[[T], T]]:
    global _rc
    if _rc is None:
        raise RuntimeError("No render context")
    return _rc.use_state(initial)


def use_side_effect(initial, dependencies=None):
    global _rc
    if _rc is None:
        raise RuntimeError("No render context")
    return _rc.use_side_effect(initial, dependencies=dependencies)


def use_state_widget(widget: widgets.Widget, prop_name):
    global _rc
    if _rc is None:
        raise RuntimeError("No render context")
    initial_value = getattr(widget, prop_name)
    value, setter = use_state(initial_value)
    if _rc.first_render:

        def handler(change):
            setter(change.new)

        widget.observe(handler, prop_name)
    return value


def _get_render_context():
    global _rc
    if _rc is None:
        raise RuntimeError("No render context")
    return _rc


def use_reducer(reduce, initial_state):
    state, set_state = use_state(initial_state)

    def dispatch(action):
        new_state = reduce(state, action)
        set_state(new_state)

    return state, dispatch


def use_context(cls: Type[T]) -> T:
    rc = _get_render_context()
    value: Optional[T] = None
    context = rc.context
    while value is None and context is not None:
        value = context.user_contexts.get(cls)
        context = context.parent
    if value is None:
        raise KeyError(f"No value found in element or parent element under key {cls}")
    return value


def provide_context(obj):
    rc = _get_render_context()
    context = rc.context
    context.user_contexts[type(obj)] = obj


class ElementContext:
    state: List

    def __init__(self, parent=None) -> None:
        self.parent = parent
        self.state = []
        self.effects: List[Effect] = []
        self.widgets: Dict[str, widgets.Widget] = {}
        self.widgets_shared: Dict[Element, widgets.Widget] = {}
        self.state_index = 0
        self.effect_index = 0
        self.children: Dict[str, ElementContext] = {}
        self.result: WidgetOrList = None
        self.user_contexts: Dict[Any, Any] = {}


TEffect = TypeVar("TEffect", bound="Effect")


class Effect:
    def __init__(self, callable: EffectCallable, dependencies: Optional[List[Any]] = None, previous: Optional[TEffect] = None) -> None:
        self.callable = callable
        self.dependencies = dependencies
        self.cleanup: Optional[EffectCleanupCallable] = None
        self.previous = previous
        self._done = False

    def __call__(self, *args):
        if self._done:
            return
        if self.previous:
            if self.previous.cleanup:
                self.previous.cleanup()
                self.previous.cleanup = None  # reset so we don't call it again
        self.cleanup = self.callable(*args)
        self._done = True


class _RenderContext:
    context: Optional[ElementContext] = None

    def __init__(self, element: Element, container: widgets.Widget = None, children_trait="children"):
        self.element = element
        self.container = container
        self.children_trait = children_trait
        self.first_render = True
        self.context = ElementContext()
        self.context_root = self.context
        self.pool: Dict[Type[widgets.Widget], List[widgets.Widget]] = {}
        self.render_count = 0
        self.last_root_widget: widgets.Widget = None
        self._is_rendering = False
        self._state_changed = False

    def use_state(self, initial) -> Tuple[T, Callable[[T], T]]:
        assert self.context is not None
        if len(self.context.state) <= self.context.state_index:
            self.context.state_index += 1
            self.context.state.append(initial)
            logger.info("Initial state = %r for index %r (%r %r)", initial, self.context.state_index - 1, id(self.context), id(self.context.state))
            return initial, self.make_setter(self.context.state_index - 1, self.context)
        else:
            state = self.context.state[self.context.state_index]
            logger.info("Got state = %r for index %r (%r %r)", state, self.context.state_index, id(self.context), id(self.context.state))
            self.context.state_index += 1
            return state, self.make_setter(self.context.state_index - 1, self.context)

    def make_setter(self, index, context):
        def set(value):
            logger.info("Set state = %r for index %r (%r %r)", value, index, id(context), id(context.state))
            if context.state[index] != value:
                context.state[index] = value
                self._state_changed = True
                if not self._is_rendering:
                    self.render(self.element, self.container)

        return set

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
                    return
            logger.info("Got new effect = %r for index %r (%r)", effect, self.context.effect_index, dependencies)
            self.context.effects[self.context.effect_index] = Effect(effect, dependencies, previous=previous_effect)
            self.context.effect_index += 1

    def render(self, element: Element, container: widgets.Widget = None):
        main_render_phase = not self._is_rendering
        self._is_rendering = True
        self._state_changed = False
        self.render_count += 1
        # if we got called recursively, self.context is not the root context
        context_prev = self.context
        self.context = self.context_root
        container = container or self.container
        assert self.context is not None
        try:
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
            self.context.widgets_shared = {}
            if container:
                if is_sequence:
                    container.children = list(widget)
                else:
                    container.children = [widget]
            self.first_render = False
        finally:
            self.context = context_prev
            if main_render_phase:
                # we started the rendering loop, so we keep going
                while self._state_changed:
                    self.render(element, container)
                self._is_rendering = False
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
            if el in self.context.widgets_shared:
                return self.context.widgets_shared[el]
            if KEY_NAME in el.kwargs:
                key = el.kwargs.pop(KEY_NAME)
            # call the function, and recurse into, until we hit leafs
            if key in self.context.children:
                self.context = self.context.children[key]
            else:
                self.context = ElementContext(parent=self.context)
                self.context.parent.children[key] = self.context
            # we will reset this every render loop, since new element are created every render loop
            self.context.widgets_shared = {}
            logger.debug("enter context %r", key)
            render_count = self.render_count
            try:
                self.context.state_index = 0
                self.context.effect_index = 0
                child = el.component.f(*el.args, **el.kwargs)
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

                for effect in self.context.effects:
                    effect(result)

            finally:
                self.context = self.context.parent
            assert self.context is not None
            self.context.widgets_shared[el] = result
            return result
        else:
            raise NotImplementedError

    def update_widget(self, element: Element, key: str) -> widgets.Widget:
        assert self.context is not None
        el = element
        assert isinstance(el.component, ComponentWidget)
        component: ComponentWidget = el.component
        normal_kwargs = {}
        listeners = {}

        # TODO: we may want to have custom keys
        if KEY_NAME in el.kwargs:
            key = el.kwargs.pop(KEY_NAME)
        logger.debug("update widget for element %r with key %r", el, key)

        current_widget = self.context.widgets.get(key)
        if current_widget is None:
            # we might have already created the widget for this
            current_widget = self.context.widgets_shared.get(el)
            if current_widget:
                logger.debug("current widget in element cache key=%r: %r", key, current_widget)
        else:
            logger.debug("current widget in widget cache key=%r: %r", key, current_widget)

        for name, value in el.kwargs.items():
            if name.startswith("on_"):
                listeners[name[3:]] = value
            else:
                normal_kwargs[name] = self._possible_create_widget(key, name, value)
        if current_widget:
            current_widget.unobserve_all()
        if type(current_widget) is not component.widget:
            # if not the same, add to pool for reuse
            self.add_to_pool(current_widget)
            current_widget = None
        if current_widget is not None:
            for name, value in normal_kwargs.items():
                self.update_widget_prop(current_widget, name, value)
        else:
            widget = component.widget(**normal_kwargs)
            # we only add widgets to the cache where they are originally are created
            # other references have to get the same widget via the element cache
            self.context.widgets[key] = widget
            logger.debug("create new widget for key %r %r", key, widget)

        if current_widget:
            widget = current_widget

        # make sure we can reused the widget belonging to this element
        # so we don't create it twice
        self.context.widgets_shared[el] = widget

        for name, listener in listeners.items():
            if listener is not None:

                def handler_wrapper(change, listener=listener):
                    listener(change.new)

                widget.observe(handler_wrapper, name)
        return widget

    def update_widget_prop(self, widget: widgets.Widget, name, value):
        setattr(widget, name, value)

    def _possible_create_widget(self, key, name, value):
        if isinstance(value, Element):
            value = self.update(value, f"{key}_{name}")
        elif isinstance(value, list):
            value = [self._possible_create_widget(key, f"{key}_{name}_{i}", k) for i, k in enumerate(value)]
        elif isinstance(value, dict):
            value = {k: self._possible_create_widget(key, f"{key}`_{name}_{k}", v) for k, v in value.items()}
        return value

    def add_to_pool(self, widget: widgets.Widget):
        self.pool[type(widget)] = widget


_rc: Optional[_RenderContext] = None


def render(element: Element, container: widgets.Widget = None, children_trait="children"):
    global _rc
    _rc = _RenderContext(element, container, children_trait=children_trait)
    widget = _rc.render(element, container)
    if container is None:
        return widget
    else:
        return _rc


def display(el: Element):
    import IPython.display  # type: ignore

    IPython.display.display(make(el))


def make(el: Element):
    hbox = widgets.VBox()
    render(el, hbox, "children")
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
