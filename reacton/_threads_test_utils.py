"""Shared helpers for the render hand-off tests.

Every test forces its interleaving: a thread is paused at a fixed point with an Event (a
component body, an effect, a widget constructor, one of reacton's own logger.info calls, or one
settrace pause at a source line). Only the stress tests depend on the scheduler.
Calls that can hang on a broken tree run on daemon Worker threads with a timeout, so a failing
test fails instead of hanging the run.
"""

import inspect
import logging
import sys
import threading
import time
import traceback

import pytest

from reacton import core

TIMEOUT = 5.0
SHORT = 1.0  # "did this call block?" (it returns in microseconds when it does not)


class LogHook(logging.Handler):
    """Call a callback at one of reacton's logger.info calls, on a given thread, once.

    handle() is overridden: logging.Handler.handle() takes the handler lock, and a thread
    paused in emit() would then block every other thread's log call.
    """

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.rules = []

    def on(self, thread, prefix, callback):
        self.rules.append([thread, prefix, callback, False])

    def handle(self, record):
        self.emit(record)
        return True

    def emit(self, record):
        msg = record.msg if isinstance(record.msg, str) else str(record.msg)
        for rule in self.rules:
            thread, prefix, callback, fired = rule
            if not fired and threading.current_thread() is thread and msg.startswith(prefix):
                rule[3] = True
                callback()


class EveryTimeHook(logging.Handler):
    """Call callback() at every reacton log record that starts with one of prefixes, on any
    thread except the one named `skip`."""

    def __init__(self, prefixes, callback, skip):
        super().__init__(level=logging.DEBUG)
        self.prefixes, self.callback, self.skip = tuple(prefixes), callback, skip

    def handle(self, record):
        self.emit(record)
        return True

    def emit(self, record):
        msg = record.msg if isinstance(record.msg, str) else str(record.msg)
        if msg.startswith(self.prefixes) and threading.current_thread().name != self.skip:
            self.callback()


def install(handler):
    logger = logging.getLogger("reacton")
    saved = logger.level, logger.propagate
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    def uninstall():
        logger.removeHandler(handler)
        logger.setLevel(saved[0])
        logger.propagate = saved[1]

    return uninstall


@pytest.fixture
def log_hook():
    hook = LogHook()
    uninstall = install(hook)
    yield hook
    uninstall()


@pytest.fixture
def helper_errors():
    """Exceptions raised on other threads (a helper thread renders with handle_error=False)."""
    errors = []
    if hasattr(threading, "excepthook"):
        old = threading.excepthook
        threading.excepthook = lambda args: errors.append(args.exc_value)
        try:
            yield errors
        finally:
            threading.excepthook = old
        return

    old_run = threading.Thread.run

    def run(thread):
        try:
            old_run(thread)
        except BaseException as e:
            errors.append(e)
            raise

    threading.Thread.run = run  # type: ignore[method-assign]
    try:
        yield errors
    finally:
        threading.Thread.run = old_run  # type: ignore[method-assign]


class Worker(threading.Thread):
    def __init__(self, target, name):
        super().__init__(name=name, daemon=True)
        self._target_f = target
        self.error = None
        self.error_tb = ""
        self.result = None

    def run(self):
        try:
            self.result = self._target_f()
        except BaseException as e:  # noqa
            self.error = e
            self.error_tb = traceback.format_exc()


def call_in_thread(f, name, timeout=SHORT):
    """Run f on a new thread; return (finished within timeout, worker)."""
    t = Worker(f, name)
    t.start()
    t.join(timeout)
    return not t.is_alive(), t


def stacks():
    frames = sys._current_frames()
    return "\n".join(f"--- {t.name}\n" + "".join(traceback.format_stack(frames[t.ident])[-6:]) for t in threading.enumerate() if t.ident in frames)


def text(box):
    return box.children[0].description


def wait_until(predicate, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return predicate()


class Injected(Exception):
    pass


def render_loop_function():
    """The function that holds the render loop (RC.render, or _render_locked when present)."""
    RC = core._RenderContext
    return getattr(RC, "_render_locked", None) or RC.render


def source_line(fn, needle, after=None):
    lines, first = inspect.getsourcelines(fn)
    start = 0 if after is None else next(i for i, line in enumerate(lines) if after in line)
    return first + next(i for i, line in enumerate(lines) if i >= start and needle in line)


def pause_at_line(fn, lineno, on_pause, after_line=False):
    """A sys.settrace function that calls on_pause() once, when fn executes line `lineno`
    (after_line=True: at the first line event after `lineno` ran)."""
    code = fn.__code__
    state = {"seen": False, "fired": False}

    def local_trace(frame, event, arg):
        if event == "line" and not state["fired"]:
            if after_line:
                if state["seen"] and frame.f_lineno != lineno:
                    state["fired"] = True
                    on_pause()
                elif frame.f_lineno == lineno:
                    state["seen"] = True
            elif frame.f_lineno == lineno:
                state["fired"] = True
                on_pause()
        return local_trace

    def global_trace(frame, event, arg):
        return local_trace if frame.f_code is code else None

    return global_trace
