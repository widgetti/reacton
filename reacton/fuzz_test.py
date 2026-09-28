# Compare the fast renderer (REACTON_FAST=1) with the default renderer on random component
# trees: the fast renderer skips parts of the tree that did not change, and after every
# (batch of) state change(s) it must give the same widgets and run the same effects, in the
# same order, as the default renderer that walks everything.
import os
import random
import unittest.mock
import zlib
from typing import Any, Callable, Dict, List, Optional

import ipywidgets as widgets
import pytest

import reacton
import reacton as react

from . import core
from . import ipywidgets as w
from .core_test import cleanup_guard  # noqa: F401  (autouse: no leaked widgets or callbacks)


def _random_app(registry, log):
    # component trees that change shape with their state (container type flips, a changing
    # number of children, keys, shuffles, fragments, components whose root is a component,
    # leaves whose root widget changes type, effects that set state, caught exceptions)
    def h(*args):
        # not hash(): the hash of a tuple differs between Python versions, and every version
        # must generate the same trees
        return zlib.crc32(repr(args).encode())

    @react.component
    def Leaf(id):
        value, set_value = react.use_state(0)
        registry[id] = set_value
        if value == 0 and h(id) % 5 == 0:
            # state set during the first render (a second render pass)
            set_value(1)
        kind = h(id, value) % 4
        if kind == 0:
            return w.Label(value=f"leaf {id} {value}")
        if kind == 1:
            return reacton.Fragment(children=[w.Button(description=f"f{id}.{i}") for i in range(value % 3)])
        return w.Button(description=f"leaf {id} {value}")

    @react.component
    def Wrapper(id):
        return Leaf(id * 7 + 1)

    @react.component
    def Thrower(id):
        value, set_value = react.use_state(0)
        registry[id] = set_value
        if value == 7 or (value == 0 and h(id) % 3 == 0):
            # also raises in its first render (in a new subtree)
            raise ValueError(f"boom {id}")
        return w.Button(description=f"thrower {id} {value}")

    @react.component
    def Catcher(id):
        exception, clear = react.use_exception()
        state, set_state = react.use_state(0)

        def set_value(value):
            clear()
            set_state(value)

        registry[id] = set_value
        if exception:
            return w.Label(value=f"caught {exception}")
        return w.HBox(children=[Thrower(id * 3 + 2), Leaf(id * 3 + 1)])

    @react.component
    def Node(id, depth):
        state, set_state = react.use_state(0)
        registry[id] = set_state
        seed = h(id, state)
        rnd = random.Random(seed)

        def effect():
            log.append(("effect", id, state))
            if state % 5 == 4:
                set_state(state + 1)

        react.use_effect(effect, [state])
        children: List[Any] = [w.Label(value=f"node {id} {state}")]
        for i in range(rnd.randint(0, 4)):
            child_id = id * 10 + i
            r = rnd.random()
            if depth < 3 and r < 0.4:
                child = Node(child_id, depth + 1)
            elif r < 0.6:
                child = Wrapper(child_id)
            elif r < 0.7:
                child = Catcher(child_id)
            else:
                child = Leaf(child_id)
            if rnd.random() < 0.3:
                child = child.key(f"k{child_id}")
            children.append(child)
        if rnd.random() < 0.2:
            rnd.shuffle(children)
        if depth == 0:
            # the root keeps its widget type: without a container, reacton does not support a
            # root component whose widget changes
            return w.VBox(children=children)
        if seed % 7 == 0:
            return reacton.Fragment(children=children)
        return (w.VBox if seed % 3 else w.HBox)(children=children)

    return Node


def _widget_signature(widget):
    # a closed widget still has its traits: compare that it is open too
    closed = widget.comm is None
    if isinstance(widget, widgets.Box):
        return (type(widget).__name__, closed, [_widget_signature(child) for child in widget.children])
    return (type(widget).__name__, closed, getattr(widget, "value", None), getattr(widget, "description", None))


def _run_random_updates(fast: bool, seed: int, steps: int, batches: Optional[List] = None):
    registry: Dict[int, Callable] = {}
    log: List[tuple] = []
    Node = _random_app(registry, log)
    record = batches is None
    batches = [] if batches is None else batches
    choices = random.Random(seed)
    results = []
    with unittest.mock.patch.dict(os.environ, {"REACTON_FAST": "1" if fast else "0"}):
        widget, rc = react.render_fixed(Node(1, 0), handle_error=False)
        assert isinstance(rc, core._RenderContextFast) == fast
        for step in range(steps):
            if record:
                ids = sorted(registry)
                batches.append([(choices.choice(ids), choices.randint(0, 9)) for _ in range(choices.choice([1, 1, 1, 2, 3]))])
            batch = batches[step]
            log.clear()
            with rc:
                for id, value in batch:
                    if id in registry:
                        registry[id](value)
            results.append((_widget_signature(rc.last_root_widget), sorted(registry), list(log)))
        rc.close()
    return results, batches


@pytest.mark.parametrize("seed", range(12))
def test_renderers_agree_on_random_updates(seed):
    # the fast renderer skips (and only partially walks) parts of the tree: after every
    # (batch of) state change(s) it must give the same widgets, and run the same effects in
    # the same order, as the default renderer that walks everything
    level = core.logger.level
    core.logger.setLevel(core.logging.CRITICAL)  # the thrower logs tracebacks
    try:
        expected, batches = _run_random_updates(False, seed, 25)
        got, _ = _run_random_updates(True, seed, 25, batches)
    finally:
        core.logger.setLevel(level)
    for step, (a, b) in enumerate(zip(expected, got)):
        assert a == b, f"step {step}, batch {batches[step]}"
