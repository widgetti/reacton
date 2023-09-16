import sys
from typing import Any, Callable, Generic, TypeVar

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets as Qt

import reacton
from reacton.core import ComponentFunction, ComponentWidget

W = TypeVar("W")  # used for widgets
T = TypeVar("T")  # used for widgets


def snake_to_setter(name):
    parts = name.split("_")
    name = "".join([k.title() for k in parts])
    return f"set{name}"


def snake_to_camel(name):
    parts = name.split("_")
    name = parts[0] + "".join([k.title() for k in parts[1:]])
    return name


class Element(Generic[T], reacton.core.Element[T]):
    def add_children(self, children):
        if len(children) == 1 and isinstance(children[0].component, ComponentFunction) and children[0].component.name.endswith("Layout"):
            self.kwargs["layout"] = children[0]
        elif isinstance(self.component, ComponentWidget) and self.component.widget == Qt.QMainWindow:
            self.kwargs["central_widget"] = children[0]
        else:
            import pdb

            pdb.set_trace()

    def _create_widget(self, kwargs):
        kwargs, listeners = self._split_kwargs(kwargs)
        assert isinstance(self.component, ComponentWidget)
        widget = self.component.widget()
        for name, value in kwargs.items():
            self._update_widget_prop(widget, name, value)
        for name, callback in listeners.items():
            self._add_widget_event_listener(widget, name, callback)
        return widget, []

    def _get_widget_args(self):
        return []

    def _update_widget_prop(self, widget, name, value):
        name = snake_to_setter(name)
        try:
            method = getattr(widget, name)
            method(value)
        except AttributeError:
            # setChildren gets treated differently
            # in layouts
            if name != "setChildren":
                raise

    def _update_widget(self, widget: Qt.QWidget, el_prev: "Element[Any]", kwargs):
        args: Any = []
        for name, value in kwargs.items():
            if name.startswith("on_") and name not in args:
                self._update_widget_event_listener(widget, name, value, el_prev.kwargs.get(name))
            else:
                self._update_widget_prop(widget, name, value)

    def _add_widget_event_listener(self, widget: Qt.QWidget, name: str, callback: Callable):
        target_name = snake_to_camel(name[3:])

        signal = getattr(widget, target_name)
        signal.connect(callback)

    def _remove_widget_event_listener(self, widget: Qt.QWidget, name: str, callback: Callable):
        target_name = snake_to_camel(name[3:])
        signal = getattr(widget, target_name)
        signal.disconnect(callback)


def QPushButton(text="Push button", **kwargs):
    comp = reacton.core.ComponentWidget(widget=Qt.QPushButton)
    kwargs = {**locals(), **kwargs}
    del kwargs["comp"]
    del kwargs["kwargs"]
    return Element(comp, **kwargs)


def QMainWindow(window_title="React-Qt", **kwargs):
    comp = reacton.core.ComponentWidget(widget=Qt.QMainWindow)
    kwargs = {**locals(), **kwargs}
    del kwargs["comp"]
    del kwargs["kwargs"]
    return Element(comp, kwargs=kwargs)


def QWidget(**kwargs):
    comp = reacton.core.ComponentWidget(widget=Qt.QWidget)
    kwargs = {**locals(), **kwargs}
    del kwargs["comp"]
    del kwargs["kwargs"]
    return Element(comp, **kwargs)


def QLabel(**kwargs):
    comp = reacton.core.ComponentWidget(widget=Qt.QLabel)
    kwargs = {**locals(), **kwargs}
    del kwargs["comp"]
    del kwargs["kwargs"]
    return Element(comp, kwargs=kwargs)


def QLineEdit(**kwargs):
    comp = reacton.core.ComponentWidget(widget=Qt.QLineEdit)
    kwargs = {**locals(), **kwargs}
    del kwargs["comp"]
    del kwargs["kwargs"]
    return Element(comp, kwargs=kwargs)


def QVBoxLayoutRaw(children=[], **kwargs):
    comp = reacton.core.ComponentWidget(widget=Qt.QVBoxLayout)
    kwargs = {"children": children, **kwargs}

    def add_children():
        widgets = [reacton.get_widget(child) for child in children]
        layout_widget: Qt.QLayout = reacton.get_widget(layout)
        for i in range(layout_widget.count()):
            widget = layout_widget.itemAt(0).widget()
            layout_widget.removeWidget(widget)
        for widget in widgets:
            layout_widget.addWidget(widget)
        print(layout_widget, widgets)

    reacton.use_effect(add_children, children)
    # del kwargs["comp"]
    # del kwargs["kwargs"]
    layout = Element(comp, kwargs=kwargs)
    return layout


def QSlider(**kwargs):
    comp = reacton.core.ComponentWidget(widget=Qt.QSlider)
    kwargs = {**locals(), **kwargs}
    del kwargs["comp"]
    del kwargs["kwargs"]
    return Element(comp, kwargs=kwargs)


@reacton.component
def QVBoxLayout(**kwargs):
    layout = QVBoxLayoutRaw(**kwargs)

    return layout


@reacton.component
def ClickApp():
    clicked, set_clicked = reacton.use_state(0)
    toomuch = clicked > 3
    button = QPushButton(text=f"Clicked {clicked} times", on_clicked=lambda: set_clicked(clicked + 1), enabled=not toomuch)
    return QMainWindow(window_title="Stop" if toomuch else "First React-Qt app", central_widget=button)


@reacton.component
def App():
    text, set_text = reacton.use_state("text")
    value, set_value = reacton.use_state(4)
    with QMainWindow(window_title="First React-Qt app") as main:
        with QWidget():
            with QVBoxLayout():
                QSlider(orientation=QtCore.Qt.Horizontal, minimum=1, maximum=10, value=value, on_value_changed=set_value)
                QLabel(text=f"Value = {value}", font=QtGui.QFont("monospace", value + 10))
                QLineEdit(on_text_changed=set_text)
                QLabel(text=text)
    return main


@reacton.component
def SliderDemo():
    size, set_size = reacton.use_state(20)
    with QWidget(window_title="Slider demo with React-Qt") as main:
        with QVBoxLayout():
            QLabel(text="Hello", font=QtGui.QFont("Arial", size), alignment=QtCore.Qt.AlignCenter)
            QSlider(orientation=QtCore.Qt.Horizontal, minimum=10, maximum=30, tick_position=Qt.QSlider.TicksBelow, tick_interval=5, on_value_changed=set_size)
    return main


app = Qt.QApplication(sys.argv)
widget, rc = reacton.core.render_fixed(App(), handle_error=False)
widget.show()
app.exec()
