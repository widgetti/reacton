# for backward compatibility
from .ipyvue import use_event  # noqa: F401

try:
    from ipyvuetify.components import *  # type: ignore  # noqa: F401, F403
except ModuleNotFoundError:
    from reacton.deprecated.ipyvuetify import *  # type: ignore  # noqa: F401, F403
