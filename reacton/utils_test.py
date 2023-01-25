import pytest

import reacton.ipywidgets as w

from .utils import equals


class NeverEquals:
    def __eq__(self, other):
        return False


class NonTruty:
    def __bool__(self):
        raise Exception("is not a truthy")


class ArrayLike:
    def __eq__(self, other):
        return NonTruty()


def test_equals():
    assert equals(1, 1)
    assert equals("a", "a")
    assert not equals(1, 2)

    assert not equals(NeverEquals(), NeverEquals())
    never_equals = NeverEquals()
    assert equals(never_equals, never_equals)

    with pytest.raises(Exception):
        assert NonTruty()
    ar1 = ArrayLike()
    ar2 = ArrayLike()
    with pytest.raises(Exception):
        assert ar1 != ar2
    assert not equals(ar1, ar2)

    assert equals(ar1, ar1)

    d1 = {"a": 1, "b": 2}
    d2 = {"a": 1, "b": 2}
    d3 = {"a": 1, "b": 3}
    assert equals(d1, d2)
    assert not equals(d1, d3)

    dar1 = {"a": 1, "b": {"ar": ar1}}
    dar2 = {"a": 1, "b": {"ar": ar1}}
    dar3 = {"a": 1, "b": {"ar": ar2}}
    assert equals(dar1, dar2)
    assert not equals(dar1, dar3)

    def make_function(a):
        def func(x):
            return x**a

        return func

    f1 = make_function(1)
    f2 = make_function(1)
    f3 = make_function(2)
    assert f1 == f1
    assert f1 != f2
    assert equals(f1, f1)
    assert equals(f1, f2)
    assert not equals(f1, f3)

    def make_el(a):
        def on_click():
            pass

        return w.Button(on_click=on_click, label=f"{a}")

    el1 = make_el(1)
    el2 = make_el(1)
    el3 = make_el(2)
    assert el1 == el1
    assert el1 != el2
    assert equals(el1, el1)
    # breakpoint()
    assert equals(el1.kwargs, el2.kwargs)
    assert equals(el1, el2)
    assert not equals(el1, el3)
