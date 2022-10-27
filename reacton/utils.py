import functools
import inspect
from typing import Callable, TypeVar, cast

import ipywidgets as widgets
import typing_extensions

from .core import component

P = typing_extensions.ParamSpec("P")
T = TypeVar("T")


def without_default(func: Callable, kwargs):
    sig = inspect.signature(func)
    {name: param.default for name, param in sig.parameters.items()}
    non_default_kwargs = {name: kwargs[name] for name, param in sig.parameters.items() if kwargs[name] is not param.default}
    return non_default_kwargs


def implements(f: Callable[P, T]):
    def caster(fimpl: Callable) -> Callable[P, T]:
        # wraps gives us the right signature at runtime (such as Jupyter)
        return cast(Callable[P, T], functools.wraps(f)(fimpl))

    return caster


def wrap(mod, globals):
    for cls_name in dir(mod):
        cls = getattr(mod, cls_name)
        if inspect.isclass(cls) and issubclass(cls, widgets.Widget):
            globals[cls_name] = component(cls)


def not_equals(a, b):
    return a != b
    if a is None and b is not None:
        return True
    if a is not None and b is None:
        return True
    if a is b:
        return False

    def numpyish(obj):
        import sys

        if "pandas" in sys.modules:
            import pandas as pd

            if isinstance(obj, pd.Series):
                return True
        if "numpy" in sys.modules:
            import numpy as np

            if isinstance(obj, np.ndarray):
                return True
        return False

    if numpyish(a) or numpyish(b):
        return (a != b).any()
    else:
        return a != b
