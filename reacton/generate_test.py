import ipywidgets as widgets
import traitlets

from .generate import CodeGen


def test_basic():
    class MyTest(traitlets.HasTraits):
        a = traitlets.traitlets.Int(1)
        b = traitlets.traitlets.Int()

    gen = CodeGen[widgets.Widget]([])
    code = gen.generate_component(MyTest).strip()

    code_expected = '''
def _MyTest(
    a: int = 1, b: int = 0, on_a: typing.Callable[[int], Any] = None, on_b: typing.Callable[[int], Any] = None
) -> Element[reacton.generate_test.MyTest]:
    """ """
    ...


@implements(_MyTest)
def MyTest(**kwargs):

    widget_cls = reacton.generate_test.MyTest
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _MyTest
'''
    assert code.strip() == code_expected.strip()


def test_value():
    class MyTest(traitlets.HasTraits):
        a = traitlets.traitlets.Int(1)
        value = traitlets.traitlets.Int()

    gen = CodeGen[widgets.Widget]([])
    code = gen.generate_component(MyTest).strip()

    code_expected = '''
def _MyTest(
    a: int = 1, value: int = 0, on_a: typing.Callable[[int], Any] = None, on_value: typing.Callable[[int], Any] = None
) -> ValueElement[reacton.generate_test.MyTest, int]:
    """ """
    ...


@implements(_MyTest)
def MyTest(**kwargs):

    widget_cls = reacton.generate_test.MyTest
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return ValueElement("value", comp, kwargs=kwargs)


del _MyTest
'''
    assert code.strip() == code_expected.strip()


def test_instance_non_widget():
    class NonWidget:
        def __init__(self, *args) -> None:
            pass

    class MyTest(traitlets.HasTraits):
        a = traitlets.traitlets.Instance(NonWidget)

    _ = MyTest()

    gen = CodeGen[widgets.Widget]([])
    code = gen.generate_component(MyTest).strip()

    code_expected = '''
def _MyTest(
    a: reacton.generate_test.NonWidget = None, on_a: typing.Callable[[reacton.generate_test.NonWidget], Any] = None
) -> Element[reacton.generate_test.MyTest]:
    """ """
    ...


@implements(_MyTest)
def MyTest(**kwargs):

    widget_cls = reacton.generate_test.MyTest
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _MyTest'''
    assert code.strip() == code_expected.strip()


def test_instance_widget():
    class SomeWidget(widgets.Widget):
        def __init__(self, *args) -> None:
            pass

    class MyTest(traitlets.HasTraits):
        a = traitlets.traitlets.Instance(SomeWidget)

    gen = CodeGen[widgets.Widget]([])
    code = gen.generate_component(MyTest).strip()

    code_expected = '''
def _MyTest(
    a: Element[reacton.generate_test.SomeWidget] = None, on_a: typing.Callable[[Element[reacton.generate_test.SomeWidget]], Any] = None
) -> Element[reacton.generate_test.MyTest]:
    """ """
    ...


@implements(_MyTest)
def MyTest(**kwargs):

    widget_cls = reacton.generate_test.MyTest
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _MyTest
'''
    assert code.strip() == code_expected.strip()


def test_skip_defaults():
    from .ipywidgets import Accordion, Button

    el = Accordion()
    assert el.kwargs == {}

    button = Button()
    assert button.kwargs == {}
