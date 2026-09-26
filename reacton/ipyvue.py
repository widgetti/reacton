from reacton.core import _fastcore


# The handler object and the hook are in _fastcore (compiled when reacton was built with
# Cython): use_event is called for every button of a page.
_EventHandler = _fastcore._EventHandler
use_event = _fastcore.use_event
