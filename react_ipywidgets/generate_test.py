import ipywidgets as widgets
import traitlets
from .generate import generate_component


def test_basic():
    class MyTest(traitlets.HasTraits):
        a = traitlets.traitlets.Int(1)
        b = traitlets.traitlets.Int()

    code = generate_component(MyTest).strip()

    code_expected = '''
def MyTest(
    a: int = 1, b: int = 0, on_a: typing.Callable[[int], Any] = None, on_b: typing.Callable[[int], Any] = None
) -> Element[react_ipywidgets.generate_test.MyTest]:
    """ """

    kwargs: Dict[Any, Any] = dict(a=a, b=b, on_a=on_a, on_b=on_b)
    widget_cls = react_ipywidgets.generate_test.MyTest
    comp = react.core.ComponentWidget(widget=widget_cls)
    return react.core.Element(comp, **kwargs)
    '''
    assert code.strip() == code_expected.strip()


def test_instance_non_widget():
    class NonWidget:
        def __init__(self, *args) -> None:
            pass

    class MyTest(traitlets.HasTraits):
        a = traitlets.traitlets.Instance(NonWidget)

    _ = MyTest()

    code = generate_component(MyTest).strip()

    code_expected = '''
def MyTest(
    a: react_ipywidgets.generate_test.NonWidget = None, on_a: typing.Callable[[react_ipywidgets.generate_test.NonWidget], Any] = None
) -> Element[react_ipywidgets.generate_test.MyTest]:
    """ """

    kwargs: Dict[Any, Any] = dict(a=a, on_a=on_a)
    widget_cls = react_ipywidgets.generate_test.MyTest
    comp = react.core.ComponentWidget(widget=widget_cls)
    return react.core.Element(comp, **kwargs)
'''
    assert code.strip() == code_expected.strip()


def test_instance_widget():
    class SomeWidget(widgets.Widget):
        def __init__(self, *args) -> None:
            pass

    class MyTest(traitlets.HasTraits):
        a = traitlets.traitlets.Instance(SomeWidget)

    code = generate_component(MyTest).strip()

    code_expected = '''
def MyTest(
    a: Element[react_ipywidgets.generate_test.SomeWidget] = None,
    on_a: typing.Callable[[Element[react_ipywidgets.generate_test.SomeWidget]], Any] = None,
) -> Element[react_ipywidgets.generate_test.MyTest]:
    """ """

    kwargs: Dict[Any, Any] = dict(a=a, on_a=on_a)
    widget_cls = react_ipywidgets.generate_test.MyTest
    comp = react.core.ComponentWidget(widget=widget_cls)
    return react.core.Element(comp, **kwargs)'''
    assert code.strip() == code_expected.strip()
