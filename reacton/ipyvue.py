from typing import Any, Callable, Optional

import ipyvue

import reacton as react
from reacton.core import ComponentWidget, _add_event_handlers, local


class _EventHandler:
    """The handler of one use_event hook, made once (like a stable setter).

    The renderer registers it on the widget of the element when that widget is created or
    updated (Element._event_handlers), and removes it when the component of the hook goes
    away. It calls the latest callback given to use_event.
    """

    __slots__ = ("rc", "context", "callback", "event", "widget", "registered_event", "removed")

    def __init__(self, rc, context, event_and_modifiers: str, callback: Callable[[Any], Any]):
        self.rc = rc
        self.context = context
        self.callback = callback
        self.event = event_and_modifiers
        self.widget: Optional[ipyvue.VueWidget] = None
        self.registered_event: Optional[str] = None
        # the hook is gone: never register again (an element can outlive the hook, e.g. a
        # memoized element of a parent that gets a new widget later)
        self.removed = False

    def __call__(self, *args):
        try:
            self.callback(*args)
        except Exception as e:
            # because widgets don't have a context, but are a child of a component
            # we add it to exceptions_children, not exception_self
            # this allows a component to catch the exception of a direct child
            self.context.exceptions_children.append(e)
            self.rc.force_update()

    def _reacton_attach(self, widget):
        if self.removed:
            return
        event = self.event
        previous = self.widget
        if widget is previous and event == self.registered_event:
            return
        if previous is not None and previous.comm is not None and self.registered_event is not None:
            previous.on_event(self.registered_event, self, remove=True)
        widget.on_event(event, self)
        self.widget = widget
        self.registered_event = event

    def _reacton_detach(self):
        self.removed = True
        widget = self.widget
        self.widget = None
        if widget is None or self.rc._closing:
            # the whole tree is going away: removing the handler would sync
            # the _events trait to the frontend (one message per widget)
            # right before the comm is closed anyway
            return
        if widget.comm is not None:
            widget.on_event(self.registered_event, self, remove=True)


def use_event(el: react.core.Element, event_and_modifiers, callback: Callable[[Any], Any]):
    rc = getattr(local, "rc", None)
    if rc is None:
        raise RuntimeError("No render context")
    context = rc.context
    assert context is not None
    ref = rc.use_ref(None)
    handler = ref.current
    if handler is None:
        handler = ref.current = _EventHandler(rc, context, event_and_modifiers, callback)
        context.event_handlers = (*context.event_handlers, handler)
    else:
        handler.callback = callback
        if event_and_modifiers != handler.event:
            handler.event = event_and_modifiers
            if handler.widget is not None:
                handler._reacton_attach(handler.widget)

    # Put the event name in the widget constructor arguments: the synced _events
    # trait then goes along with the comm open message. The later on_event call
    # only updates _events when the event set differs, so this saves one update
    # message per widget per event. When the element is reused from a previous
    # render (memoized) and the widget already exists, on_event falls back to
    # syncing _events itself.
    if isinstance(el.component, ComponentWidget) and issubclass(el.component.widget, ipyvue.VueWidget):
        events = el.kwargs.get("_events")
        if events is None:
            el.kwargs["_events"] = [event_and_modifiers]
        elif event_and_modifiers not in events:
            # do not mutate the list, it could be shared with a previous element
            el.kwargs["_events"] = [*events, event_and_modifiers]

    handlers = el._event_handlers
    if handler not in handlers:
        if el._key_frozen:
            _add_event_handlers(el, (handler,), context, rc)
        else:
            el._event_handlers = (*handlers, handler)
