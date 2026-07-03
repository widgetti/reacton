"""Benchmark harness for the reacton renderer/reconciler.

Run with the project venv:

    .venv/bin/python benchmarks/bench.py --label baseline
    .venv/bin/python benchmarks/bench.py --label after --scenario leaf_update
    .venv/bin/python benchmarks/compare.py baseline after

Results are written to benchmarks/results/<label>.json. Use --profile to
additionally write a cProfile .prof file per scenario.
"""

import argparse
import cProfile
import gc
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

import reacton as react
import reacton.core
import reacton.ipywidgets as w

# the current implementation renders recursively; keep deep trees from
# hitting the interpreter limit so we measure speed, not stack depth
sys.setrecursionlimit(100_000)

RESULTS_DIR = Path(__file__).parent / "results"

SCENARIOS = {}


def scenario(cls):
    SCENARIOS[cls.name] = cls
    return cls


class Scenario:
    inner = 1  # operations per timed run(); reported times are per operation

    def setup(self):  # once per scenario
        pass

    def setup_iteration(self):  # before each timed run, untimed
        pass

    def run(self):  # the timed part
        raise NotImplementedError

    def cleanup_iteration(self):  # after each timed run, untimed
        pass

    def teardown(self):  # once per scenario
        pass


@react.component
def Row(i):
    return w.HBox(children=[w.Button(description=f"button-{i}"), w.Label(value=f"label-{i}")])


@react.component
def WideApp(n):
    return w.VBox(children=[Row(i) for i in range(n)])


@react.component
def Nest(depth):
    if depth == 0:
        return w.Button(description="leaf")
    return w.VBox(children=[Nest(depth - 1)])


# handles to reach use_state setters from outside the component
_handle: dict = {}


@react.component
def StatefulLeaf():
    value, set_value = react.use_state(0)
    _handle["set"] = set_value
    return w.Button(description=f"leaf-{value}")


@react.component
def AppWithStatefulLeaf(n):
    rows = [Row(i) for i in range(n)]
    rows.append(StatefulLeaf())
    return w.VBox(children=rows)


@react.component
def RootCounterApp(n):
    value, set_value = react.use_state(0)
    _handle["set"] = set_value
    rows = [Row(i) for i in range(n)]
    return w.VBox(children=[w.Label(value=f"count: {value}"), *rows])


@react.component
def MemoApp(n):
    value, set_value = react.use_state(0)
    _handle["set"] = set_value
    rows = react.use_memo(lambda: [Row(i) for i in range(n)], [n])
    return w.VBox(children=[w.Label(value=f"count: {value}"), w.VBox(children=rows)])


@react.component
def ReorderApp(n):
    order, set_order = react.use_state(list(range(n)))
    _handle["set"] = set_order
    rows = [Row(i).key(f"row-{i}") for i in order]
    return w.VBox(children=rows)


@react.component
def BurstApp(n):
    value, set_value = react.use_state(0)
    _handle["set"] = set_value
    rows = [Row(i) for i in range(n)]
    return w.VBox(children=[w.IntSlider(value=value), *rows])


@scenario
class InitialRenderWide(Scenario):
    """Initial render of a wide tree: N component rows, ~3N widgets."""

    name = "initial_render_wide"
    N = 300

    def run(self):
        self.widget, self.rc = react.render(WideApp(self.N))

    def cleanup_iteration(self):
        self.rc.close()


@scenario
class InitialRenderDeep(Scenario):
    """Initial render of a deeply nested tree (component per level)."""

    name = "initial_render_deep"
    DEPTH = 100

    def run(self):
        self.widget, self.rc = react.render(Nest(self.DEPTH))

    def cleanup_iteration(self):
        self.rc.close()


@scenario
class LeafUpdate(Scenario):
    """State change in a single leaf component of a large tree."""

    name = "leaf_update"
    N = 300
    inner = 10

    def setup(self):
        self.widget, self.rc = react.render(AppWithStatefulLeaf(self.N))
        self.set = _handle["set"]
        self.counter = 0

    def run(self):
        for _ in range(self.inner):
            self.counter += 1
            self.set(self.counter)

    def teardown(self):
        self.rc.close()


@scenario
class RootUpdate(Scenario):
    """State change at the root: children re-render but reconcile to no widget changes."""

    name = "root_update"
    N = 300
    inner = 5

    def setup(self):
        self.widget, self.rc = react.render(RootCounterApp(self.N))
        self.set = _handle["set"]
        self.counter = 0

    def run(self):
        for _ in range(self.inner):
            self.counter += 1
            self.set(self.counter)

    def teardown(self):
        self.rc.close()


@scenario
class MemoSubtreeSkip(Scenario):
    """Root state change where the heavy subtree is memoized (identical elements)."""

    name = "memo_subtree_skip"
    N = 300
    inner = 10

    def setup(self):
        self.widget, self.rc = react.render(MemoApp(self.N))
        self.set = _handle["set"]
        self.counter = 0

    def run(self):
        for _ in range(self.inner):
            self.counter += 1
            self.set(self.counter)

    def teardown(self):
        self.rc.close()


@scenario
class ListReorder(Scenario):
    """Keyed children list reversed on every update."""

    name = "list_reorder"
    N = 300
    inner = 2

    def setup(self):
        self.widget, self.rc = react.render(ReorderApp(self.N))
        self.set = _handle["set"]
        self.order = list(range(self.N))

    def run(self):
        for _ in range(self.inner):
            self.order = self.order[::-1]
            self.set(self.order)

    def teardown(self):
        self.rc.close()


@scenario
class BurstUpdates(Scenario):
    """Many small sequential updates in a modest tree: per-update fixed overhead."""

    name = "burst_updates"
    N = 20
    inner = 50

    def setup(self):
        self.widget, self.rc = react.render(BurstApp(self.N))
        self.set = _handle["set"]
        self.counter = 0

    def run(self):
        for _ in range(self.inner):
            self.counter += 1
            self.set(self.counter)

    def teardown(self):
        self.rc.close()


@scenario
class ForceUpdateWide(Scenario):
    """rc.force_update() on a large unchanged tree: full re-render + reconcile no-op."""

    name = "force_update_wide"
    N = 300
    inner = 3

    def setup(self):
        self.widget, self.rc = react.render(WideApp(self.N))

    def run(self):
        for _ in range(self.inner):
            self.rc.force_update()

    def teardown(self):
        self.rc.close()


@scenario
class TeardownWide(Scenario):
    """Closing a large tree."""

    name = "teardown_wide"
    N = 300

    def setup_iteration(self):
        self.widget, self.rc = react.render(WideApp(self.N))

    def run(self):
        self.rc.close()


def run_scenario(cls, repeats, warmup=1):
    s = cls()
    s.setup()
    times = []
    for i in range(warmup + repeats):
        s.setup_iteration()
        gc.collect()
        gc.disable()
        t0 = time.perf_counter()
        s.run()
        t1 = time.perf_counter()
        gc.enable()
        s.cleanup_iteration()
        if i >= warmup:
            times.append((t1 - t0) / cls.inner)
    s.teardown()
    return times


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, help="name for the results file")
    parser.add_argument("--scenario", action="append", help="run only these scenarios (repeatable)")
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--profile", action="store_true", help="also write cProfile output per scenario")
    args = parser.parse_args()

    names = args.scenario or list(SCENARIOS)
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"{args.label}.json"
    results = {}
    if out_path.exists():
        results = json.loads(out_path.read_text()).get("results", {})

    git_rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()

    for name in names:
        cls = SCENARIOS[name]
        widgets_before = len(reacton.core._get_widgets_dict())
        if args.profile:
            prof = cProfile.Profile()
            prof.enable()
        times = run_scenario(cls, args.repeats)
        if args.profile:
            prof.disable()
            prof_path = RESULTS_DIR / f"{args.label}-{name}.prof"
            prof.dump_stats(prof_path)
        widgets_after = len(reacton.core._get_widgets_dict())
        if widgets_after > widgets_before:
            print(f"  WARNING: {name} leaked {widgets_after - widgets_before} widgets")
        results[name] = {
            "inner": cls.inner,
            "repeats": args.repeats,
            "times": times,
            "min": min(times),
            "median": statistics.median(times),
            "mean": statistics.mean(times),
        }
        print(f"{name:25s} min={min(times) * 1000:8.3f}ms median={statistics.median(times) * 1000:8.3f}ms")

    out_path.write_text(
        json.dumps(
            {
                "meta": {"git_rev": git_rev, "python": sys.version.split()[0], "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
                "results": results,
            },
            indent=2,
        )
    )
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
