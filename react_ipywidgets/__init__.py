"""Write ipywidgets like React

React - ipywidgets relation:
 * DOM nodes -- Widget
 * Element -- Element
 * Component -- function

"""

from . import _version

__version__ = _version.__version__
from .core import (
    component,
    component_interactive,
    display,
    make,
    provide_context,
    render,
    use_context,
    use_reducer,
    use_side_effect,
    use_state,
    use_state_widget,
)

__all__ = [
    "__version__",
    "component",
    "render",
    "make",
    "display",
    "use_state",
    "use_state_widget",
    "use_side_effect",
    "use_reducer",
    "use_context",
    "provide_context",
    "component_interactive",
]
