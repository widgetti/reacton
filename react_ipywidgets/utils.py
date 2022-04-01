import inspect
from typing import Callable

import ipywidgets as widgets

from .core import component


def without_default(func: Callable, kwargs):
    sig = inspect.signature(func)
    {name: param.default for name, param in sig.parameters.items()}
    non_default_kwargs = {name: kwargs[name] for name, param in sig.parameters.items() if kwargs[name] is not param.default}
    return non_default_kwargs


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
