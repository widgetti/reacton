"""Import reacton._fastcore: compiled when it was built with Cython, else the plain Python.

REACTON_CYTHON=0 in the environment forces the plain Python version, also when a compiled
module is there (to test both, or to debug).
"""

import importlib.util
import os
import sys


def _load():
    if os.environ.get("REACTON_CYTHON", "1") == "0":
        name = __package__ + "._fastcore"
        existing = sys.modules.get(name)
        if existing is not None:
            return existing
        path = os.path.join(os.path.dirname(__file__), "_fastcore.py")
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    from . import _fastcore as module

    return module


_fastcore = _load()
compiled: bool = not _fastcore.__file__.endswith(".py")
