"""The building blocks in reacton._fastcore, compiled (setup_cython.py) or plain Python."""

import copy
import pickle
import sys
import weakref

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
