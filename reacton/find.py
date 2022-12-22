import collections.abc
import time
from typing import Callable, Generic, List, Set, Type, TypeVar, cast

from ipywidgets import Widget

from .core import Element, _RenderContext

W = TypeVar("W")  # used for widgets
X = TypeVar("X")  # used for widgets


def pretty_print(widget: Widget, indent=0, indent_size=2):
    def format_arg(value):
        if isinstance(value, Widget):
            return pretty_print(value, indent + 1, indent_size)
        if isinstance(value, list):
            return "[" + ", ".join(format_arg(v) for v in value) + "]"
        value_repr = repr(value)
        if len(value_repr) > 300:
            value_repr = value_repr[:50] + "..." + value_repr[-50:]
        return value_repr

    def format_kwarg(key, value):
        return f"{' ' * ((indent+1) * indent_size)}{key} = {format_arg(value)}"

    name = type(widget).__name__
    keys = list(widget._repr_keys())
    if hasattr(widget, "_react_meta"):
        keys += ["_react_meta"]
    if "children" in keys:
        keys.remove("children")
        keys = keys + ["children"]
    kwargs = [format_kwarg(key, getattr(widget, key)) for key in keys]
    args_formatted = "".join([f"\n{arg}," for arg in kwargs])
    return f"{name}({args_formatted}\n{' ' * (indent * indent_size)})"


class Finder(collections.abc.Sequence, Generic[W]):
    def __init__(self, widgets: List[W] = [], queries=[], parent=None) -> None:
        # for performance reason, we eagerly evaluate the queries and store the widgets in self.widgets
        # but if we want to wait for a widget to appear, we need to re-evaluate the queries every time
        self.widgets = widgets.copy()
        self.queries = queries.copy()
        self.parent = parent

    def _root(self):
        parent = self
        while parent.parent is not None:
            parent = parent.parent
        return parent

    def _reexecute_find(self):
        finder = self._root()
        for query in self.queries:
            type = query["type"]
            if type == "find":
                cls = query["cls"]
                matches = query["matches"]
                finder = finder.find(cls, **matches)
            elif type == "single":
                finder = finder.single
            elif type == "getitem":
                finder = finder[query["item"]]
            else:
                raise ValueError(f"Unknown query type {type}")

        return finder

    @property
    def widget(self):
        return self.single.widgets[0]

    def assert_empty(self):
        assert len(self.widgets) == 0, f"Expected no widgets, but got: {self.widgets}, current structure:\n{self._current_structure()}"

    def assert_not_empty(self):
        assert len(self.widgets) != 0, f"Expected widgets, but none found, current structure:\n{self._current_structure()}"

    def assert_single(self):
        assert len(self.widgets) == 1, f"Expected a single widget, but got: {self.widgets}"

    def assert_single_wait(self):
        assert len(self.widgets) == 1, f"Expected a single widget, but got: {self.widgets}"

    def matches(self, **matches):
        self.assert_matches(**matches)

    def wait_for(self, state="attached", timeout=1):
        start = time.time()
        finder = self
        while time.time() - start < timeout:
            if state == "attached":
                if len(finder) > 0:
                    return finder
            elif state == "detached":
                if len(finder) == 0:
                    return finder
            else:
                raise ValueError(f"Unknown state {state}, expected 'attached' or 'detached'")
            time.sleep(0.001)
            finder = self._reexecute_find()
        raise TimeoutError(f"Timeout waiting for {self}, current structure:\n{self._current_structure()}")

    def _current_structure(self):
        non_empty = self
        while len(non_empty) == 0:
            non_empty = non_empty.parent
        pp_rendered = "\n".join(pretty_print(widget) for widget in non_empty.widgets)
        return pp_rendered

    def assert_matches(self, **matches):
        widget = self.single.widget
        for name, expected in matches.items():
            if not hasattr(widget, name):
                raise AttributeError(f"Widget {widget} has no attribute {name}")
            value = getattr(widget, name)
            assert value == expected, f"Expected {widget}.{name} == {expected}, got {value}"

    def assert_matches_wait(self, timeout=1, iteration_delay=0.001, **matches):
        start = time.time()
        last_e = None
        while time.time() - start < timeout:
            try:
                self.assert_matches(**matches)
                return
            except AssertionError as e:
                last_e = e
            time.sleep(iteration_delay)

        assert last_e is not None
        raise TimeoutError(f"Timeout, waiting for {matches}") from last_e

    def assert_wait(self, f: Callable[[W], bool], timeout=1, iteration_delay=0.001):
        start = time.time()
        while time.time() - start < timeout:
            result = f(self.widget)
            if result:
                return
            time.sleep(iteration_delay)
        assert f(self.widget)

    @property
    def single(self) -> "Finder[W]":
        if len(self.widgets) != 1:
            raise ValueError(f"Expected 1 match, got {self.widgets}, current structure:\n{self._current_structure()}")
        queries = self.queries + [{"type": "single"}]
        return Finder([self.widgets[0]], queries, parent=self)

    def __len__(self):
        return len(self.widgets)

    def __getitem__(self, item):
        queries = self.queries + [{"type": "getitem", "item": item}]
        return Finder([self.widgets[item]], queries, parent=self)

    def find(self, widget_class: Type[X] = Widget, **matches):
        def test(widget: Widget):
            if isinstance(widget, widget_class):
                for name, expected in matches.items():
                    if not hasattr(widget, name) and name.startswith("meta_"):
                        meta_attr_name = name[5:]
                        if hasattr(widget, "_react_meta") and meta_attr_name in widget._react_meta:  # type: ignore
                            value = widget._react_meta[meta_attr_name]  # type: ignore
                        else:
                            return False
                    elif hasattr(widget, name):
                        value = getattr(widget, name)
                    else:
                        return False
                    if value != expected:
                        return False
                return True
            else:
                return False

        queries = self.queries + [{"type": "find", "cls": widget_class, "matches": matches}]
        return Finder[X](cast(List[X], self._walk(test)), queries, parent=self)

    def _walk(self, f: Callable[[Element], bool]):
        visited: Set[int] = set()
        queue: List[Widget] = list()
        visited = set([id(k) for k in self.widgets])
        queue.extend(self.widgets)

        found: List[Element] = []

        while queue:
            widget = queue.pop(0)
            if f(widget):
                found.append(widget)
            else:
                for name in widget.keys:
                    value = getattr(widget, name)
                    if isinstance(value, Widget):
                        if value not in visited:
                            visited.add(value)
                            queue.append(value)
                    elif isinstance(value, (list, tuple)):
                        for el in value:
                            if isinstance(el, Widget):
                                if id(el) not in visited:
                                    visited.add(id(el))
                                    queue.append(el)
                    elif isinstance(value, dict):
                        for name, el in value.items():
                            if isinstance(el, Widget):
                                if id(el) not in visited:
                                    visited.add(id(el))
                                    queue.append(el)
        return found


def finder(rc: _RenderContext):
    if rc.container is None:
        return Finder[Widget]([rc.last_root_widget])
    else:
        return Finder[Widget](list(rc.container.children))
