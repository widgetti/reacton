"""The hot building blocks of reacton, written for Cython's pure Python mode.

This module is plain Python and works as it is (PyPy, no compiler, development). When it is
compiled (``python setup_cython.py build_ext --inplace``, see ``_fastcore.pxd``), the same
source becomes a C extension: elements become extension types with typed fields, and the
code that makes and walks them runs without the interpreter. Rules for this file:

- all typing lives in ``_fastcore.pxd``: the .py must not pay for it when it is not compiled
  (``cython.cast``/``cython.declare``/decorators are real calls in plain Python);
- class defaults that are typed fields when compiled go in an ``if not cython.compiled:``
  block of the class body (it runs once, at import), the compiled defaults in ``__cinit__``
  (never called when not compiled);
- no closures inside functions that the .pxd declares ``cpdef``.

reacton.core builds the public classes on top of these (``Element`` is a Python subclass of
``ElementBase``), so everything that user code sees stays a normal Python class.
"""

import sys
import threading
from types import TracebackType
from typing import Any, Dict, Optional

try:
    import cython
except ImportError:  # plain Python without Cython installed
    # (through globals(): a plain assignment would redeclare the name for the compiler)
    globals()["cython"] = type("cython", (), {"compiled": False})


from . import utils

# the render context of the thread that renders (local.rc), see reacton.core
local = threading.local()
# set together with reacton.core.DEBUG: keep the stack where every element was made
DEBUG = 0

widget_render_error_msg = (
    """Cannot show widget. You probably want to rerun the code cell above (<i>Click in the code cell, and press Shift+Enter <kbd>⇧</kbd>+<kbd>↩</kbd></i>)."""
)
mime_bundle_default: Dict[str, Any] = {"text/plain": "Cannot show ipywidgets in text", "text/html": widget_render_error_msg}
# the default meta of an element (never changed in place: meta() makes a new dict)
_NO_META: dict = {}
# reacton.core's Element and ValueElement (see _register)
_Element: Any = None
_ValueElement: Any = None


def _register(element_class, value_element_class):
    global _Element, _ValueElement
    _Element = element_class
    _ValueElement = value_element_class


def find_elements(value):
    if isinstance(value, ElementBase):
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
            if isinstance(child, (ElementBase, tuple, list, dict)):
                elements |= find_elements(child)
        return elements
    elif isinstance(value, dict):
        elements = set()
        for child in value.values():
            if isinstance(child, (ElementBase, tuple, list, dict)):
                elements |= find_elements(child)
        return elements


class ContainerAdder:
    """Collects the elements made inside a ``with element:`` block (and a component body).

    Every new element is added to the innermost one on ``rc.container_adders``: to ``created``
    for this class, through ``add()`` for any other kind of adder.
    """

    def __init__(self, el, prop_name):
        self.el = el
        self.prop_name = prop_name
        self.created = []

    def __class_getitem__(cls, item):
        # (ContainerAdder[W](...), it used to be a typing.Generic)
        return cls

    def add(self, el):
        self.created.append(el)

    def collect(self):
        children = set()
        for el in self.created:
            children |= find_elements(el) - {el}
        top_level = [k for k in self.created if k not in children]
        return top_level


class ElementBase:
    """The data of an element (reacton.core.Element adds the rest)."""

    if not cython.compiled:
        # (compiled: typed fields, see _fastcore.pxd, with the defaults set in __cinit__)
        component: Any
        args: Any
        kwargs: Dict[str, Any]
        # a plain attribute (not a property): it is read for every element in every walk
        is_shared: bool = False
        # Defaults as class attributes: every component body makes elements, most of them
        # never change these. (_meta is never changed in place, meta() makes a new dict.)
        mime_bundle: Dict[str, Any] = mime_bundle_default
        _key: Optional[str] = None
        _meta: Dict[str, Any] = _NO_META
        # how often the element was rendered (also for testing), see _key_frozen
        _render_count: int = 0
        # facts about the kwargs of a widget element, learned when its widget is created or
        # updated (None: not known), so a close of the whole tree can skip work
        _on_kwargs: Optional[bool] = None  # a kwarg starts with on_ (maybe an event listener)
        _leaf: Optional[bool] = None  # no elements in the kwargs
        # handlers (of reacton.ipyvue.use_event) to register on the widget of this element
        # when it is created or updated: objects with _reacton_attach(widget)
        _event_handlers: tuple = ()
        # (only in DEBUG mode: where the element was made)
        traceback: TracebackType

    def __cinit__(self):
        # (compiled only: the defaults of the typed fields)
        self.mime_bundle = mime_bundle_default
        self._meta = _NO_META
        self._event_handlers = ()

    def __init__(self, component, args=None, kwargs=None):
        self.component = component
        self.args = args or []
        self.kwargs = kwargs or {}
        # the elements made in a `with container:` block (or a component body) go there
        rc = getattr(local, "rc", None)
        if rc is not None:
            container_adders = rc.container_adders
            if container_adders:
                adder = container_adders[-1]
                if type(adder) is ContainerAdder:
                    adder.created.append(self)
                else:
                    adder.add(self)
        if DEBUG:
            _keep_traceback(self)

    @property
    def _key_frozen(self):
        # rendered at least once. The renderers used to set a flag next to every
        # _render_count += 1, one attribute write per element render.
        return self._render_count > 0

    def key(self, value):
        """Returns the same element with a custom key set.

        This can help render performance. See documentation for details.
        """
        if self._render_count:
            raise RuntimeError("Element keys should not be mutated after rendering")
        self._key = value
        return self

    def meta(self, **kwargs):
        """Add metadata to the created widget.

        This can be used to find a widget for testing.
        """
        self._meta = {**self._meta, **kwargs}
        return self

    # the old name of is_shared
    @property
    def _shared(self):
        return self.is_shared

    @_shared.setter
    def _shared(self, value):
        self.is_shared = value

    def shared(self):
        self.is_shared = True
        return self

    def _arguments_changed(self, other):
        # called for every child of a component that renders again: the same objects
        # (small ints, interned strings, the same callbacks) need no utils.equals call
        args = self.args
        other_args = other.args
        kwargs = self.kwargs
        other_kwargs = other.kwargs
        if args:
            if len(args) != len(other_args):
                return True
        elif other_args:
            return True
        if kwargs:
            if len(kwargs) != len(other_kwargs):
                return True
            for k, v in kwargs.items():
                if k not in other_kwargs:
                    return True
                other_v = other_kwargs[k]
                if v is not other_v and not utils.equals(v, other_v):
                    return True
        elif other_kwargs:
            return True
        if args:
            for a, b in zip(args, other_args):
                if a is not b and not utils.equals(a, b):
                    return True
        return False

    def __reduce__(self):
        # (explicit, the same in both modes: a compiled element has no automatic pickling)
        return (_rebuild_element, (type(self), _element_state(self)))


class ValueElementBase(ElementBase):
    """An element for a widget with a value (reacton.core.ValueElement adds the rest)."""

    if not cython.compiled:
        value_property: str

    def __init__(self, value_property, component, args=None, kwargs=None):
        self.value_property = value_property
        # ElementBase.__init__, inline
        self.component = component
        self.args = args or []
        self.kwargs = kwargs or {}
        rc = getattr(local, "rc", None)
        if rc is not None:
            container_adders = rc.container_adders
            if container_adders:
                adder = container_adders[-1]
                if type(adder) is ContainerAdder:
                    adder.created.append(self)
                else:
                    adder.add(self)
        if DEBUG:
            _keep_traceback(self)


_ELEMENT_FIELDS = (
    "component",
    "args",
    "kwargs",
    "is_shared",
    "mime_bundle",
    "_key",
    "_meta",
    "_render_count",
    "_on_kwargs",
    "_leaf",
    "_event_handlers",
    "value_property",
)
_MISSING = object()


def _element_state(el):
    state = {}
    for name in _ELEMENT_FIELDS:
        value = getattr(el, name, _MISSING)
        if value is not _MISSING:
            state[name] = value
    state.update(el.__dict__)
    return state


def _rebuild_element(cls, state):
    el = cls.__new__(cls)
    for name, value in state.items():
        setattr(el, name, value)
    return el


def _keep_traceback(el, depth=-1):
    # DEBUG: keep the frame of the code that made the element (the caller of the factory), to
    # show where an element came from when rendering it fails. Compiled functions have no
    # frame of their own, so the frame of that code is closer to the top of the stack.
    # (depth -1: called from ElementBase.__init__, which is called by a factory)
    if depth == -1:
        depth = 1 if cython.compiled else 3
    frame = sys._getframe(depth)
    el.traceback = TracebackType(tb_next=None, tb_frame=frame, tb_lasti=frame.f_lasti, tb_lineno=frame.f_lineno)


def component_call(self, *args, **kwargs):
    # ComponentFunction.__call__: make the element of a component
    if self.value_name is not None:
        el = _ValueElement(self.value_name, self, args, kwargs)
    else:
        el = _Element(self, args, kwargs)
    if self.mime_bundle is not mime_bundle_default:
        el.mime_bundle = self.mime_bundle
    if DEBUG:
        # the code that called the component (see _keep_traceback)
        _keep_traceback(el, 0 if cython.compiled else 2)
    return el
