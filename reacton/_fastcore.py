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
from typing import Any, Dict, List, Optional  # noqa: F401  (List: in a type comment)

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


# ============================================================================================
# The mount of the fast renderer (reacton.core._RenderContextFast)
#
# A new component (a first render, a new list item, another component type at a key) is
# mounted in one walk: the bodies run as in the render phase, and the widgets of the new
# subtree are made children first. A mounted component (a _MountedContext) keeps its element
# tree positionally: `nodes` holds, in the order the widgets were made (children first), the
# widget of each widget element and the context of each component element. The dicts the
# update paths use (elements, widgets, children, element_to_widget, used_keys,
# resolved_kwargs, ...) are made from that only when they are used (materialize), with the
# same keys as the two phase walk. Reconciliation of the pass runs the effects (finish_mount).
#
# When the pass cannot keep the mounted widgets (a body sets state or raises, a shared
# element, a widget that fails to be made, an explicit key that could match a positional key),
# the mounts of the pass are undone (undo_mounts): the widgets are closed and the contexts
# get the render bookkeeping of the two phase walk, which then takes over.
# ============================================================================================

# what the mount uses from reacton.core (set by _register_core)
_core: Any = None
_ComponentFunction: Any = None
_ComponentWidget: Any = None
_ComponentContext: Any = None
_MountedContext: Any = None
_FragmentWidget: Any = None
_logger: Any = None
# values that cannot hold elements (the child visitors skip them)
_SCALAR_TYPES = frozenset([str, int, float, bool, complex, bytes, type(None)])
# the dicts of a component context that are made from its nodes (see materialize)
_MATERIALIZED = frozenset(["elements", "widgets", "children", "element_to_widget", "used_keys", "resolved_kwargs", "elements_next", "children_next"])
# the slots of reacton.core._MountedContext
_MOUNTED_SLOTS = (
    "nodes",
    "compact_widget",
    "elements",
    "widgets",
    "children",
    "element_to_widget",
    "used_keys",
    "resolved_kwargs",
    "elements_next",
    "children_next",
)
# element classes that use the Element methods to make and remove a widget (see _plain_class)
_plain_classes: dict = {}
_EMPTY: dict = {}


def _register_core(core):
    global _core, _ComponentFunction, _ComponentWidget, _ComponentContext, _MountedContext, _FragmentWidget, _logger
    _core = core
    _ComponentFunction = core.ComponentFunction
    _ComponentWidget = core.ComponentWidget
    _ComponentContext = core.ComponentContext
    _MountedContext = core._MountedContext
    _FragmentWidget = core.FragmentWidget
    _logger = core.logger


def _plain_class(cls):
    # an element class that makes, updates and removes its widget with the Element methods: the
    # mount does that inline (a subclass that overrides one of them gets its own method called)
    plain = _plain_classes.get(cls)
    if plain is None:
        element = _core.Element
        plain = _plain_classes[cls] = (
            cls._create_widget is element._create_widget
            and cls._close_widget is element._close_widget
            and cls._cleanup_callbacks is element._cleanup_callbacks
            and cls._split_kwargs is element._split_kwargs
            and cls._get_widget_args is element._get_widget_args
        )
    return plain


def _trait_names(component):
    # the trait names of the widget class of a ComponentWidget (kept on it)
    names = component.__dict__.get("_reacton_trait_names")
    if names is None:
        names = component._reacton_trait_names = frozenset(component.widget.class_trait_names())
    return names


class _Mount:
    """The walk that mounts one new subtree (see mount_component)."""

    def __init__(self, rc):
        self.rc = rc
        # the widgets made during the mount (to find those made as a side effect, like Layout)
        self.recording = []
        # every context made by a mount in this pass (to undo them), and the tops of the mounts
        self.contexts = rc._mount_contexts
        # the contexts of this mount, children first (effects run in this order)
        self.order = []
        self.failed = False
        # bodies that raised in this mount (then exceptions bubble up, see _mount_component)
        self.raised = 0
        self.shared_next = rc._shared_elements_next
        # context -> the explicit keys in its tree (the duplicate check)
        self.keys = None


def mount_component(rc, el, key, parent_context, order, context):
    """Mount the new component element el at key in parent_context (which renders in two phases).

    context: a context made by state_set (restored state), or None. Returns the root widget,
    or None when this pass cannot keep the mount.
    """
    m = _Mount(rc)
    previous_recording = _core._start_recording_constructed(m.recording)
    try:
        c = _mount_component(m, el, parent_context, context, key)
        c.order_in_parent = order
    finally:
        _core._stop_recording_constructed(previous_recording)
    widget = c.compact_widget
    if widget is not None and not m.failed:
        c.mount_order = m.order
        rc._mount_roots[c] = None
    else:
        # parts of the subtree were mounted, not all: undo at the end of the pass
        rc._mount_failed = True
    return widget


def _new_context(parent):
    c = _MountedContext.__new__(_MountedContext)
    c.parent = parent
    c.nodes = []
    c.compact_widget = None
    return c


def _adopt(precreated, parent):
    # a context made by state_set (restored state) is mounted as a new one with its state; the
    # component elements in its tree look up the pre-made contexts of their keys
    context = _new_context(parent)
    context.state = precreated.state
    context.setters = precreated.setters
    precreated_children = precreated.__dict__.get("children_next")
    if precreated_children:
        context.precreated_children = precreated_children
    return context


def _mount_component(m, el, parent, context, key):
    # key: the key of the top of a mount (in a parent that renders in two phases), else None
    rc = m.rc
    if context is None:
        context = _new_context(parent)
    else:
        context = _adopt(context, parent)
    context.invoke_element = el
    m.contexts.append(context)
    if key is not None:
        # the top of the mount
        context.key_in_parent = key
        parent.children_next[key] = context
        rc._mount_tops.append(context)
    else:
        parent.nodes.append(context)
    manager_classes = _core._component_context_manager_classes
    if manager_classes:
        context.context_managers = [cm(el) for cm in manager_classes]
    adders = rc.container_adders
    if adders:
        del adders[:]
    rc.context = context
    render_count = rc.render_count
    raised = m.raised
    root = None
    try:
        root = _call_body(rc, el, context)
    except BaseException as e:
        _logger.exception("Component %r raised exception %r", el.component, e)
        context.exceptions_self.append(e)
        rc._set_rerender_needed("Exception ocurred during render")
        context.needs_render = True
        m.raised += 1
    if rc.render_count != render_count:
        raise RuntimeError("Recursive render detected, possible a bug in react")
    widget = None
    if root is not None:
        if el._event_handlers:
            _core._add_event_handlers(root, el._event_handlers, context, rc)
        context.root_element = root
        widget = _mount_node(m, root, context, "/" if context.precreated_children else None)
    elif el.is_shared:
        m.shared_next.discard(el)
    rc.context = parent
    if context.precreated_children is not None:
        # pre-made (state_set) children that were not used
        context.precreated_children = None
    user_contexts = context.user_contexts
    if user_contexts is not _EMPTY:
        # (provide() made them)
        context.user_contexts_prev = user_contexts
    if m.raised != raised:
        # exceptions in this subtree: as in _render_component
        if context.exceptions_self or context.exceptions_children and not context.exception_handler:
            parent.exceptions_children.extend(context.exceptions_self)
            parent.exceptions_children.extend(context.exceptions_children)
        if context.exceptions_self or context.exceptions_children:
            rc._mark_dirty(context)
        if parent.exceptions_self or parent.exceptions_children:
            if not rc._rerender_needed:
                rc._set_rerender_needed("Exception ocurred during render")
                parent.needs_render = True
    if widget is not None:
        context.compact_widget = widget
    m.order.append(context)
    return context


def _call_body(rc, el, context):
    # the component function, inside its context managers (solara registers one)
    managers = context.context_managers
    if not managers:
        root = _call_component(rc, el)
        assert root is not None
    elif len(managers) == 1:
        with managers[0]:
            root = _call_component(rc, el)
            assert root is not None
    else:
        import contextlib

        with contextlib.ExitStack() as stack:
            for manager in managers:
                stack.enter_context(manager)
            root = _call_component(rc, el)
            assert root is not None
    return root


def _call_component(rc, el):
    """Run the component function, with an implicit container when it returns None."""
    component = el.component
    default_container = _core._default_container
    if default_container is None:
        component.render_count += 1
        return component.f(*el.args, **el.kwargs)
    # Only a body that returns None needs the implicit container. Building it for every body
    # (an extra element, and collecting the top level elements from all elements the body
    # made) costs more than a typical component body, so first only record the elements the
    # body makes, like the container would.
    adder = rc._body_adder
    created = []  # type: List[Any]
    adder.created = created
    container_adders = rc.container_adders
    container_adders.append(adder)
    try:
        component.render_count += 1
        root_element = component.f(*el.args, **el.kwargs)
    finally:
        container_adders.pop()
        adder.created = _core._NO_ELEMENTS
    if root_element is None:
        with default_container() as container:
            # the container collects the same elements, the same way
            rc.container_adders[-1].created.extend(created)
        if len(container.kwargs["children"]) == 1:
            root_element = container.kwargs["children"][0]
        else:
            root_element = container
    return root_element


def _mount_node(m, el, c, dkey):
    # The mount walk of an element in the tree of the component context c; returns its widget
    # (None when this pass does not make widgets any more). dkey: the positional key of el,
    # only in a context with pre-made children (else None: keys are made when needed).
    if not isinstance(el, ElementBase):
        raise TypeError(f"Expected element, not {el}")
    key = el._key
    if key is not None:
        all_keys = m.keys
        if all_keys is None:
            all_keys = m.keys = {}
        keys = all_keys.get(c)
        if keys is None:
            all_keys[c] = {key}
        elif key in keys:
            raise KeyError(f"Duplicate key {key!r}")
        else:
            keys.add(key)
        if "/" in key:
            # could be the same as a positional key: the two phase walk checks all keys
            m.failed = True
    else:
        key = dkey
    if el.is_shared:
        # rendered once for the whole tree, by the two phase walk
        m.failed = True
        c.has_shared = True
        if el in m.shared_next:
            return None
        m.shared_next.add(el)
    el._render_count += 1  # (also freezes the key, see Element._key_frozen)
    component = el.component
    if type(component) is not _ComponentWidget and not isinstance(component, _ComponentWidget):
        # a component element
        if el.is_shared and (el.args or el.kwargs):
            # the arguments of a shared element belong to the context it is rendered in
            _mount_value(m, el.kwargs, c, key)
            _mount_value(m, el.args, c, key)
        precreated = None
        precreated_children = c.precreated_children
        if precreated_children:
            precreated = precreated_children.pop(key, None)
        child = _mount_component(m, el, c, precreated, None)
        widget = child.compact_widget
        if widget is not None and el._meta:
            widget._react_meta = {**getattr(widget, "_react_meta", {}), **el._meta}
        return widget

    # a widget element: first the elements in its kwargs (children first)
    assert not el.args, "no positional args supported for widgets"
    kwargs = el.kwargs
    resolved = None
    for name, value in kwargs.items():
        t = type(value)
        if t in _SCALAR_TYPES:
            continue
        if t is list:
            new_value = _mount_list(m, value, c, None if key is None else f"{key}{name}/")
        elif isinstance(value, ElementBase):
            new_value = _mount_node(m, value, c, None if key is None else f"{key}{name}/")
        elif t is tuple or t is dict or isinstance(value, (list, tuple, dict)):
            new_value = _mount_value(m, value, c, None if key is None else f"{key}{name}/")
        else:
            continue
        if resolved is None:
            resolved = dict(kwargs)
        resolved[name] = new_value
    rc = m.rc
    if m.failed or rc._rerender_needed:
        # this pass will be undone, do not make more widgets
        return None
    if resolved is None:
        # (no copy: the constructor gets the kwargs unpacked)
        resolved = kwargs
    element_class = type(el)
    plain = _plain_classes.get(element_class)
    if plain is None:
        plain = _plain_class(element_class)
    recording = m.recording
    count = len(recording)
    if plain:
        # Element._create_widget, with the recording of this mount
        listeners = None
        traits = _trait_names(component)
        if not traits.issuperset(resolved):
            for name in list(resolved):
                if name.startswith("on_") and name not in traits:
                    if resolved is kwargs:
                        resolved = dict(kwargs)
                    if listeners is None:
                        listeners = {}
                    listeners[name] = resolved.pop(name)
        try:
            widget = component.widget(**resolved)
        except Exception:
            # let reconciliation make it (and handle the exception) as it always does
            m.failed = True
            return None
        widget_class = type(widget)
        if component.__dict__.get("_reacton_batched") is not widget_class:
            if not getattr(widget_class.hold_trait_notifications, "_reacton_batched", False):
                _core._install_batched_hold(widget_class)
            component._reacton_batched = widget_class
        widget._reacton_rc = rc
        if el._meta:
            widget._react_meta = dict(el._meta)
        if listeners is None:
            c.nodes.append(widget)
        else:
            for name, callback in listeners.items():
                if callback is not None:
                    el._add_widget_event_listener(widget, name, callback)  # type: ignore[attr-defined]
            c.nodes.append((el, widget))
        handlers = el._event_handlers
        if handlers:
            for handler in handlers:
                handler._reacton_attach(widget)
        orphan_ids = None
        if len(recording) > count + 1 or (len(recording) == count + 1 and recording[count] is not widget):
            widgets_dict = _core._get_widgets_dict()
            orphan_ids = {w.model_id for w in recording[count:] if w is not widget and w.comm is not None and w.model_id in widgets_dict}
    else:
        try:
            widget, orphan_ids = el._create_widget(dict(resolved))  # type: ignore[attr-defined]
        except BaseException:
            m.failed = True
            return None
        c.nodes.append((el, widget))
    if orphan_ids:
        widgets_dict = _core._get_widgets_dict()
        for orphan_widget in [widgets_dict[k] for k in orphan_ids]:
            if _core._is_shared_ipyvue_template(orphan_widget):
                orphan_ids.discard(orphan_widget.model_id)
        if orphan_ids:
            rc._orphans.setdefault(widget.model_id, set()).update(orphan_ids)
    return widget


def _mount_list(m, value, c, dkey):
    values = []
    index = 0
    for x in value:
        if isinstance(x, ElementBase):
            w = _mount_node(m, x, c, None if dkey is None else f"{dkey}{index}/")
            if type(w) is _FragmentWidget:
                values.extend(w.children)
            else:
                values.append(w)
        elif type(x) in _SCALAR_TYPES:
            values.append(x)
        else:
            w = _mount_value(m, x, c, None if dkey is None else f"{dkey}{index}/")
            if type(w) is _FragmentWidget:
                values.extend(w.children)
            else:
                values.append(w)
        index += 1
    return values


def _mount_value(m, value, c, dkey):
    # (as core._visit_children_values: lists, tuples and dicts become new plain ones)
    t = type(value)
    if t is list:
        return _mount_list(m, value, c, dkey)
    if t is tuple:
        return tuple(_mount_list(m, value, c, dkey))
    if t is dict:
        return {k: _mount_value(m, v, c, None if dkey is None else f"{dkey}{k}/") for k, v in value.items()}
    if t in _SCALAR_TYPES:
        return value
    if isinstance(value, ElementBase):
        return _mount_node(m, value, c, dkey)
    if isinstance(value, (list, tuple)):
        values = _mount_list(m, value, c, dkey)
        return tuple(values) if isinstance(value, tuple) else values
    if isinstance(value, dict):
        return {k: _mount_value(m, v, c, None if dkey is None else f"{dkey}{k}/") for k, v in value.items()}
    return value


# --------------------------------------------------------------------------------------------
# after the mount: the effects (reconciliation), the dicts (materialize), the undo


def finish_mount(rc, root):
    """Reconciliation of a mounted subtree (rc.context is the parent of root): run the effects,
    children first, and hook the root widget into the parent."""
    parent_context = rc.context
    order = root.mount_order
    raised = False
    try:
        for context in order:
            effects = context.effects
            parent = context.parent
            if effects:
                rc.context = context
                for effect in effects:
                    if effect.next is not None or effect.executed:
                        rc._process_effects(context, parent)
                        break
                    try:
                        effect._cleanup = effect.callable()
                        effect.executed = True
                    except BaseException as e:
                        _logger.exception("Effect %r raised exception %r", effect.callable, e)
                        parent.exceptions_self.append(e)
                        rc._set_rerender_needed("Exception ocurred during effect")
                        rc._mark_dirty(parent)
                        parent.needs_render = True
                        raised = True
            if raised:
                if context.exceptions_self or context.exceptions_children and not context.exception_handler:
                    parent.exceptions_children.extend(context.exceptions_self)
                    parent.exceptions_children.extend(context.exceptions_children)
        widget = root.compact_widget
        el = root.invoke_element
        key = root.key_in_parent
        if el._meta:
            widget._react_meta = {**getattr(widget, "_react_meta", {}), **el._meta}
        parent_context.widgets[key] = widget
        parent_context.element_to_widget[el] = widget
    finally:
        rc.context = parent_context
        root.mount_order = None
        rc._mount_roots.pop(root, None)


def materialize(c):
    """Make the dicts of a mounted context from its nodes (the same keys as the two phase walk).

    For the update paths, get_widget, state_get: the first time they use one of the dicts.
    """
    nodes = c.nodes
    c.nodes = None
    w = _Materialize(c, nodes)
    root = c.root_element
    if root is not None:
        w.node(root, "/")
    c.elements = w.elements
    c.widgets = w.widgets
    c.children = w.children
    c.element_to_widget = w.element_to_widget
    c.used_keys = w.used_keys
    c.resolved_kwargs = w.resolved_kwargs
    c.elements_next = {}
    c.children_next = {}


def partial_element_to_widget(c):
    """element -> widget of a context that is still being mounted: the elements the walk made a
    widget for so far (it goes in the same order). For _find_widget (use_event on an element
    of a parent, whose widget exists already)."""
    w = _Materialize(c, c.nodes, partial=True)
    root = c.root_element
    if root is not None:
        try:
            w.node(root, "/")
        except _StopWalk:
            pass
    return w.element_to_widget


class _StopWalk(Exception):
    pass


class _Materialize:
    def __init__(self, c, nodes, partial=False):
        self.partial = partial
        self.nodes = nodes
        self.index = 0
        self.order = 0
        self.elements = {}
        self.widgets = {}
        self.children = {}
        self.element_to_widget = {}
        self.used_keys = set()
        self.resolved_kwargs = {}

    def node(self, el, default_key):
        key = el._key
        if key is None:
            key = default_key
        self.used_keys.add(key)
        self.elements[key] = el
        component = el.component
        if not isinstance(component, _ComponentWidget):
            if self.partial and (self.index >= len(self.nodes) or self.nodes[self.index].compact_widget is None):
                raise _StopWalk()
            child = self.nodes[self.index]
            self.index += 1
            self.children[key] = child
            child.key_in_parent = key
            child.order_in_parent = self.order
            self.order += 1
            widget = child.compact_widget
            self.widgets[key] = widget
            self.element_to_widget[el] = widget
            return widget
        resolved = None
        start = self.index
        for name, value in el.kwargs.items():
            if type(value) in _SCALAR_TYPES:
                continue
            new_value = self.value(value, f"{key}{name}/")
            if resolved is None:
                resolved = dict(el.kwargs)
            resolved[name] = new_value
        if self.partial and self.index >= len(self.nodes):
            raise _StopWalk()
        node = self.nodes[self.index]
        self.index += 1
        widget = node[1] if type(node) is tuple else node
        self.widgets[key] = widget
        self.element_to_widget[el] = widget
        if self.index - 1 != start:
            # elements in the kwargs (each one took a node): the kwargs the widget was made
            # with, as the update path compares them (see _mount_node: without listeners)
            assert resolved is not None
            traits = _trait_names(component)
            if not traits.issuperset(resolved):
                for name in list(resolved):
                    if name.startswith("on_") and name not in traits:
                        del resolved[name]
            self.resolved_kwargs[key] = resolved
        return widget

    def value(self, value, key):
        t = type(value)
        if t is list or t is tuple or (t is not dict and isinstance(value, (list, tuple))):
            values = []
            index = 0
            for x in value:
                if type(x) in _SCALAR_TYPES:
                    values.append(x)
                else:
                    w = self.node(x, f"{key}{index}/") if isinstance(x, ElementBase) else self.value(x, f"{key}{index}/")
                    if type(w) is _FragmentWidget:
                        values.extend(w.children)
                    else:
                        values.append(w)
                index += 1
            return tuple(values) if isinstance(value, tuple) else values
        if t is dict or isinstance(value, dict):
            return {k: (x if type(x) in _SCALAR_TYPES else self.value(x, f"{key}{k}/")) for k, x in value.items()}
        if isinstance(value, ElementBase):
            return self.node(value, key)
        return value


def undo_mounts(rc):
    """Undo the mounts of a pass that cannot keep them (see the module comment): close their
    widgets, and give their contexts the render bookkeeping of the two phase walk."""
    undo = _Undo(rc)
    for top in rc._mount_tops:
        if top.nodes is not None:
            undo.component(top)
    rc._mount_roots = {}
    rc._mount_tops = []
    rc._mount_contexts = []
    rc._mount_failed = False


class _Undo:
    # the walk of the mount again (depth first, the same order, for the shared elements), with
    # the keys of the two phase walk
    def __init__(self, rc):
        self.rc = rc
        self.widgets_dict = _core._get_widgets_dict()
        self.shared_seen = set()

    def component(self, c):
        nodes = c.nodes
        c.nodes = None
        for node in nodes:
            if not isinstance(node, _ComponentContext):
                _close_widget_node(self.rc, node, self.widgets_dict)
        state = _UndoContext([node for node in nodes if isinstance(node, _ComponentContext)])
        root = c.root_element
        if root is not None:
            self.node(state, root, "/")
        c.elements_next = state.elements_next
        c.children_next = state.children_next
        c.used_keys = state.used_keys
        c.child_order_counter = state.order
        c.root_element_next = root
        c.root_element = None
        c.elements = {}
        c.children = {}
        c.widgets = {}
        c.element_to_widget = {}
        c.resolved_kwargs = {}
        c.compact_widget = None
        c.mount_order = None

    def node(self, state, el, default_key):
        key = el._key
        if key is None:
            key = default_key
        state.used_keys.add(key)
        if el.is_shared:
            if el in self.shared_seen:
                return
            self.shared_seen.add(el)
        state.elements_next[key] = el
        if isinstance(el.component, _ComponentWidget):
            for name, value in el.kwargs.items():
                if type(value) not in _SCALAR_TYPES:
                    self.value(state, value, f"{key}{name}/")
            return
        if el.is_shared and (el.args or el.kwargs):
            self.value(state, el.kwargs, key)
            self.value(state, el.args, key)
        if state.index >= len(state.contexts):
            # (the mount did not get this far)
            return
        child = state.contexts[state.index]
        state.index += 1
        state.children_next[key] = child
        child.key_in_parent = key
        child.order_in_parent = state.order
        state.order += 1
        if child.nodes is not None:
            self.component(child)

    def value(self, state, value, key):
        if isinstance(value, ElementBase):
            self.node(state, value, key)
        elif isinstance(value, (list, tuple)):
            index = 0
            for x in value:
                if type(x) not in _SCALAR_TYPES:
                    self.value(state, x, f"{key}{index}/")
                index += 1
        elif isinstance(value, dict):
            for k, x in value.items():
                if type(x) not in _SCALAR_TYPES:
                    self.value(state, x, f"{key}{k}/")


class _UndoContext:
    def __init__(self, contexts):
        self.contexts = contexts
        self.index = 0
        self.order = 0
        self.elements_next = {}
        self.children_next = {}
        self.used_keys = set()


def _close_widget_node(rc, node, widgets_dict):
    # close the widget of a node (and the widgets it made as a side effect)
    if type(node) is tuple:
        el, widget = node
    else:
        el = None
        widget = node
    orphans = rc._orphans.pop(widget.model_id, None) if rc._orphans else None
    if orphans:
        for orphan in orphans:
            orphan_widget = widgets_dict.get(orphan)
            if orphan_widget:
                _core.close_widget(orphan_widget)
    if el is not None:
        el._cleanup_callbacks(widget)
        el._close_widget(widget)
    else:
        # Element._close_widget, inline
        close = widget.close
        if callable(close):
            close()
        else:
            _core.close_widget(widget)  # logs the warning
        widget.__dict__.pop("_reacton_rc", None)


def remove_mounted(rc, child_context, closing):
    """Remove a mounted component (rc.context is its parent): the same order of effect
    cleanups, handler removals and widget closes as reacton.core's _remove_element (or
    _close_element when closing), from its nodes."""
    context = rc.context
    child_context.exceptions_self = []
    child_context.exceptions_children = []
    rc.context = child_context
    widgets_dict = _core._get_widgets_dict()
    try:
        for effect in child_context.effects:
            if not effect._cleaned_up:
                cleanup = effect._cleanup
                try:
                    if cleanup is not None:
                        cleanup()
                except BaseException as e:
                    _logger.exception("Effect cleanup %r raised exception %r", effect.callable, e)
                    child_context.exceptions_self.append(e)
                    if not closing:
                        rc._set_rerender_needed("Exception ocurred during effect")
                        rc._mark_dirty(child_context)
                effect._cleaned_up = True
        if not closing:
            for handler in child_context.event_handlers:
                try:
                    handler._reacton_detach()
                except BaseException as e:
                    _logger.exception("Removing event handler %r raised exception %r", handler, e)
                    child_context.exceptions_self.append(e)
                    rc._set_rerender_needed("Exception ocurred during effect")
                    rc._mark_dirty(child_context)
        nodes = child_context.nodes
        child_context.nodes = None
        for node in nodes:
            if isinstance(node, _ComponentContext):
                if node.nodes is not None:
                    remove_mounted(rc, node, closing)
                elif closing:
                    # (its dicts were made, e.g. by get_widget): as the two phase walk does
                    rc._close_component_context(node)
                else:
                    rc._remove_component_context(node)
            else:
                _close_widget_node(rc, node, widgets_dict)
    finally:
        rc.context = context
    if child_context.exceptions_self or child_context.exceptions_children and not child_context.exception_handler:
        # child does not handle exceptions, so bubble up
        context.exceptions_children.extend(child_context.exceptions_self)
        context.exceptions_children.extend(child_context.exceptions_children)
