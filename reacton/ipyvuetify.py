# for backward compatibility
from .ipyvue import use_event  # noqa: F401

try:
    from ipyvuetify.components import *  # noqa: F401, F403
except ModuleNotFoundError:
    from reacton.deprecated.ipyvuetify import *  # noqa: F401, F403
