"""The building blocks in reacton._fastcore, compiled (setup_cython.py) or plain Python."""

import copy
import pickle
import sys
import weakref
from types import FrameType
from typing import Optional

import ipywidgets as widgets

import reacton
import reacton.core
from reacton import ipywidgets as w
from reacton._fastcore_import import _fastcore


def test_element_is_a_normal_python_object():
    button = w.Button(description="hi")
    assert isinstance(button, reacton.core.Element)
    assert isinstance(button, _fastcore.ElementBase)
    # arbitrary attributes, weak references, generic aliases (used in type hints)
    button.custom = 1
    assert button.custom == 1
    assert weakref.ref(button)() is button
    assert reacton.core.Element[widgets.Button] is not None
    assert reacton.core.ValueElement[widgets.IntSlider, int] is not None
    slider = w.IntSlider(value=1)
    assert isinstance(slider, reacton.core.ValueElement)
    assert slider.value_property == "value"
    # defaults
    element: reacton.core.Element = reacton.core.Element(reacton.core.ComponentWidget(widget=widgets.Button))
    assert element.args == [] and element.kwargs == {}
    assert element._key is None and element._meta == {} and element._event_handlers == ()
    assert not element.is_shared and element._render_count == 0 and not element._key_frozen
    assert element.shared() is element and element.is_shared and element._shared


def test_element_pickle_and_copy():
    element = w.Button(description="hi").key("my-key").meta(name="x")
    element.custom = [1, 2]
    for clone in [pickle.loads(pickle.dumps(element)), copy.copy(element)]:
        assert type(clone) is type(element)
        assert clone.kwargs == {"description": "hi"}
        assert clone._key == "my-key"
        assert clone._meta == {"name": "x"}
        assert clone.custom == [1, 2]
        assert clone.component is element.component
    slider = pickle.loads(pickle.dumps(w.IntSlider(value=3)))
    assert slider.value_property == "value" and slider.kwargs == {"value": 3}


def test_debug_keeps_the_frame_that_made_the_element():
    @reacton.component
    def Child():
        return w.Button()

    assert _fastcore.DEBUG == reacton.core.DEBUG
    reacton.core.DEBUG = True
    try:
        assert _fastcore.DEBUG
        button = w.Button(description="made here")
        child = Child()
    finally:
        reacton.core.DEBUG = False
    assert not _fastcore.DEBUG
    this_function = sys._getframe(0).f_code.co_name
    assert button.traceback.tb_frame.f_code.co_name == this_function
    assert child.traceback.tb_frame.f_code.co_name == this_function


def test_solara_context_manager_and_default_container():
    # solara appends a context manager class to reacton.core._component_context_manager_classes
    # after importing reacton (solara/toestand.py), and assigns reacton.core._default_container
    # (solara/components/__init__.py). The compiled mount reads both as its own globals.
    log = []

    class Manager:
        def __init__(self, el):
            self.name = el.component.name

        def __enter__(self):
            log.append(("enter", self.name))

        def __exit__(self, *args):
            log.append(("exit", self.name))

    @reacton.component
    def MyColumn(children=[]):
        log.append(("column", len(children)))
        return w.VBox(children=children)

    set_value = lambda value: None  # noqa

    @reacton.component
    def Child(name):
        # returns None: the implicit container gets the elements it made
        w.Button(description=f"{name} a")
        w.Button(description=f"{name} b")

    @reacton.component
    def App():
        nonlocal set_value
        value, set_value = reacton.use_state(0)
        return w.HBox(children=[Child(f"child{value}").key(f"child{value}")])

    previous_container = reacton.core._default_container
    reacton.core._component_context_manager_classes.append(Manager)
    reacton.core._default_container = MyColumn
    try:
        assert _fastcore._default_container is MyColumn
        assert Manager in _fastcore._component_context_manager_classes
        hbox, rc = reacton.render_fixed(App(), handle_error=False)
        column = hbox.children[0]
        assert isinstance(column, widgets.VBox)
        assert [button.description for button in column.children] == ["child0 a", "child0 b"]
        assert ("enter", "App") in log and ("exit", "App") in log
        assert ("enter", "Child") in log and ("exit", "Child") in log
        assert ("column", 2) in log
        # a later update mounts a new child: the same container and manager
        log.clear()
        set_value(1)
        column = hbox.children[0]
        assert [button.description for button in column.children] == ["child1 a", "child1 b"]
        assert ("enter", "Child") in log and ("exit", "Child") in log
        assert ("column", 2) in log
        rc.close()
    finally:
        reacton.core._component_context_manager_classes.remove(Manager)
        reacton.core._default_container = previous_container
    assert _fastcore._default_container is previous_container
    assert Manager not in _fastcore._component_context_manager_classes


def test_use_memo_has_a_frame():
    # solara.tasks: task() called inside use_memo does not warn. It checks the 5 frames above
    # the user code that calls task() for a function named use_memo in a reacton module.
    found = []

    def make():
        frame: Optional[FrameType] = sys._getframe(2)  # the frame above the lambda
        for _ in range(5):
            if frame is None:
                break
            if frame.f_code.co_name == "use_memo" and frame.f_globals.get("__name__", "").startswith("reacton."):
                found.append(frame.f_globals["__name__"])
                break
            frame = frame.f_back
        return 1

    @reacton.component
    def Test():
        reacton.use_memo(lambda: make(), [])
        return w.Button()

    box, rc = reacton.render(Test(), handle_error=False)
    rc.close()
    assert len(found) == 1
