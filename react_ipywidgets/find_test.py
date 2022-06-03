import ipywidgets as widgets

import react_ipywidgets as react
import react_ipywidgets.ipywidgets as w


def test_find_by_class():
    @react.component
    def Test():
        with w.VBox() as main:
            with w.HBox():
                w.Button(description="test")
        return main

    box, rc = react.render(Test())
    assert rc._find(widgets.Button).single.widget.description == "test"


def test_find_by_class_and_attr():
    @react.component
    def Test():
        with w.VBox() as main:
            with w.HBox():
                w.Button(description="1")
                with w.VBox():
                    w.Button(description="2")
        return main

    box, rc = react.render(Test())
    assert rc._find(widgets.Button, description="1").single.widget.description == "1"
    assert rc._find(widgets.Button, description="2").single.widget.description == "2"


def test_find_nested():
    @react.component
    def Test():
        with w.VBox() as main:
            with w.VBox():
                w.Button(description="1")
            with w.HBox():
                w.Button(description="2")
        return main

    box, rc = react.render(Test())
    assert rc._find(widgets.HBox).single.find(widgets.Button).single.widget.description == "2"


def test_find_by_class_and_attr_nested():
    @react.component
    def Test():
        with w.VBox() as main:
            with w.HBox(box_style="SUCCESS"):
                w.Button(description="1", disabled=True)
                with w.VBox():
                    w.Button(description="2", disabled=False)
            with w.HBox(box_style="info"):
                w.Button(description="1", disabled=True)
                with w.VBox():
                    w.Button(description="2", disabled=False)
        return main

    box, rc = react.render(Test())
    rc._find(widgets.HBox, box_style="success").find(widgets.Button, description="1").matches(description="1", disabled=True)
    rc._find(widgets.HBox, box_style="info").find(widgets.Button, description="2").matches(description="2", disabled=False)


def test_find_by_meta_widget():
    @react.component
    def Test():
        with w.VBox() as main:
            with w.HBox().meta(name="a"):
                w.Button(description="testb").meta(name="b")
                w.Button(description="testc").meta(name="c")
                w.Button(description="testd")
        return main

    box, rc = react.render(Test())
    rc._find(widgets.Widget, meta_name="a").single
    assert rc._find(widgets.Button, meta_name="b").widget.description == "testb"
    assert rc._find(widgets.Button, meta_not_exist="b").widgets == []


@react.component
def ButtonLevel2(**kwargs):
    return w.Button(**kwargs).meta(level2="2")


@react.component
def ButtonLevel1(**kwargs):
    return ButtonLevel2(**kwargs).meta(level1="1")


def test_find_by_meta_component():
    @react.component
    def Test():
        with w.VBox() as main:
            with w.HBox():
                ButtonLevel1(description="testa").meta(name="a")
                ButtonLevel1(description="testb").meta(name="b")
        return main

    box, rc = react.render(Test())
    assert rc._find(widgets.Button, meta_name="b").widget.description == "testb"
    # make sure the meta dicts get merged
    assert len(rc._find(widgets.Button, meta_level1="1").widgets) == 2
    assert len(rc._find(widgets.Button, meta_level2="2").widgets) == 2


def test_find_count():
    @react.component
    def Test():
        with w.VBox() as main:
            w.Button(description="1")
            w.Button(description="2")
        return main

    box, rc = react.render(Test())
    assert len(rc._find(widgets.Button, description="should-not-be-found")) == 0
    assert len(rc._find(widgets.Button, description="1")) == 1
    assert len(rc._find(widgets.Button)) == 2
