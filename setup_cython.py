"""Optional: compile reacton's hot modules with Cython (pure Python mode).

    pip install "cython>=3.1,<3.2" setuptools
    python setup_cython.py build_ext --inplace

reacton does not need this: the same modules run as plain Python (pip install -e . works
without Cython). With the compiled modules next to the .py files, they are imported instead.
REACTON_CYTHON=0 forces the plain Python modules (reacton/_fastcore_import.py). Remove the
compiled modules with: python setup_cython.py clean_inplace
"""

import glob
import os
import sys

from Cython.Build import cythonize
from setuptools import Distribution, Extension
from setuptools.command.build_ext import build_ext

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = ["reacton._fastcore"]


def clean_inplace():
    for module in MODULES:
        base = module.replace(".", "/")
        for path in glob.glob(base + ".*.so") + glob.glob(base + ".*.pyd") + [base + ".c", base + ".html"]:
            if os.path.exists(path):
                os.remove(path)
                print("removed", path)


def build_inplace():
    extensions = [Extension(module, [module.replace(".", "/") + ".py"]) for module in MODULES]
    ext_modules = cythonize(
        extensions,
        compiler_directives={
            "language_level": 3,
            # compiled functions behave like Python functions (methods bind, inspect.signature)
            "binding": True,
        },
        annotate=os.environ.get("REACTON_CYTHON_ANNOTATE") == "1",
    )
    # (a Distribution of its own: setuptools.setup() would read reacton's hatch pyproject.toml)
    dist = Distribution({"name": "reacton-cython-build", "ext_modules": ext_modules})
    command = build_ext(dist)
    command.inplace = True
    command.ensure_finalized()
    command.run()


if __name__ == "__main__":
    os.chdir(HERE)
    args = sys.argv[1:]
    if args == ["clean_inplace"]:
        clean_inplace()
    elif args in (["build_ext", "--inplace"], []):
        build_inplace()
    else:
        sys.exit("usage: python setup_cython.py [build_ext --inplace | clean_inplace]")
