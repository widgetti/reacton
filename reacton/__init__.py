"""Write ipywidgets like React

React - ipywidgets relation:
 * DOM nodes -- Widget
 * Element -- Element
 * Component -- function

"""

from . import _version

__version__ = _version.__version__
from .core import (
    Fragment,
    component,
    component_interactive,
    create_context,
    display,
    get_context,
    get_widget,
    make,
    provide_context,
    render,
    render_fixed,
    use_context,
    use_effect,
    use_exception,
    use_memo,
    use_reducer,
    use_ref,
    use_side_effect,
    use_state,
    use_state_widget,
    value_component,
)

__all__ = [
    "Fragment",
    "__version__",
    "component",
    "value_component",
    "render",
    "render_fixed",
    "make",
    "display",
    "get_widget",
    "get_context",
    "use_context",
    "create_context",
    "use_exception",
    "use_memo",
    "use_ref",
    "use_state",
    "use_state_widget",
    "use_effect",
    "use_side_effect",
    "use_reducer",
    "provide_context",
    "component_interactive",
]
