import threading
import time

import ipywidgets as widgets
import pytest

import reacton as react
import reacton.ipywidgets as w


def test_find_by_class():
    @react.component
    def Test():
        with w.VBox() as main:
            with w.HBox():
                w.Button(description="test")
        return main

    box, rc = react.render(Test())
    assert rc.find(widgets.Button).single.widget.description == "test"


def test_find_non_existing_attr():
    el = w.Button(description="test")
    box, rc = react.render(el, handle_error=False)
    rc.find(widgets.Button, doesnotexist="test").assert_empty()


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
    assert rc.find(widgets.Button, description="1").single.widget.description == "1"
    assert rc.find(widgets.Button, description="2").single.widget.description == "2"


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
    assert rc.find(widgets.HBox).single.find(widgets.Button).single.widget.description == "2"


def test_assert_matches_wait():
    @react.component
    def Test():
        with w.VBox() as main:
            with w.VBox():
                w.Button(description="1")
        return main

    box, rc = react.render(Test())
    rc.find(widgets.Button).assert_matches_wait(description="1")
    with pytest.raises(TimeoutError):
        rc.find(widgets.Button).assert_matches_wait(description="3", timeout=0.1)


def test_assert_wait():
    @react.component
    def Test():
        with w.VBox() as main:
            with w.VBox():
                w.Button(description="1")
        return main

    box, rc = react.render(Test())
    rc.find(widgets.Button).assert_wait(lambda x: x.description == "1")
    with pytest.raises(AssertionError):
        rc.find(widgets.Button).assert_wait(lambda x: x.description == "xx", timeout=0.1)


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
    rc.find(widgets.HBox, box_style="success").find(widgets.Button, description="1").matches(description="1", disabled=True)
    rc.find(widgets.HBox, box_style="info").find(widgets.Button, description="2").matches(description="2", disabled=False)


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
    rc.find(widgets.Widget, meta_name="a").single
    assert rc.find(widgets.Button, meta_name="b").widget.description == "testb"
    assert rc.find(widgets.Button, meta_not_exist="b").widgets == []


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
    assert rc.find(widgets.Button, meta_name="b").widget.description == "testb"
    # make sure the meta dicts get merged
    assert len(rc.find(widgets.Button, meta_level1="1").widgets) == 2
    assert len(rc.find(widgets.Button, meta_level2="2").widgets) == 2


def test_find_count():
    @react.component
    def Test():
        with w.VBox() as main:
            w.Button(description="1")
            w.Button(description="2")
        return main

    box, rc = react.render(Test())
    assert len(rc.find(widgets.Button, description="should-not-be-found")) == 0
    assert len(rc.find(widgets.Button, description="1")) == 1
    assert len(rc.find(widgets.Button)) == 2


def test_wait_for():
    set_state = None

    @react.component
    def Test():
        nonlocal set_state
        state, set_state = react.use_state(0)
        with w.VBox() as main:
            w.Button(description="1")
            w.Button(description="2")
            if state == 1:
                w.Button(description="3")
        return main

    box, rc = react.render(Test(), handle_error=False)
    assert set_state is not None

    def run():
        assert set_state is not None
        time.sleep(0.3)
        set_state(1)

    threading.Thread(target=run).start()
    assert len(rc.find(widgets.Button, description="should-not-be-found")) == 0
    assert len(rc.find(widgets.Button, description="1")) == 1
    assert len(rc.find(widgets.Button)) == 2
    finder = rc.find(widgets.Button, description="3")
    assert len(finder) == 0
    finder = finder.wait_for()
    assert finder.widget.description == "3"
