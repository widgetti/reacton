# Reacton render benchmarks & the opt-in fast reconciler

This directory holds the performance harness for a faster reimplementation of
the renderer (the tree-walking downstream of `render()`), plus its design notes.

The fast renderer is **opt-in and off by default.** The default `_RenderContext`
is the original, unchanged implementation; the rewrite lives in a
`_RenderContextFast(_RenderContext)` subclass that overrides only the
tree-walking methods. Set `REACTON_FAST=1` to select it. CI runs the full test
suite against both (a `reacton-fast: ["0", "1"]` matrix dimension), so the two
stay behavior-identical.

## Running the benchmarks

```bash
# default renderer, then the fast one:
python benchmarks/bench.py --label baseline
REACTON_FAST=1 python benchmarks/bench.py --label fast
python benchmarks/compare.py baseline fast
```

`bench.py` writes `benchmarks/results/<label>.json`. `--scenario <name>` runs a
subset; `--profile` also writes a cProfile `.prof` per scenario. Scenarios cover
initial render (wide/deep), single-leaf update, root update, memoized-subtree
skip, keyed list reorder, burst updates, full `force_update`, and teardown — so
a change can be checked against both the headline case (one leaf updating in a
large tree) and the no-op/​full-walk cases.

Use the cheapest widgets possible in scenarios (bare `Button`/`Label`): real
ipywidget construction cost can dominate and mask reconciler cost, so confirm
with a profile that you are measuring tree-walking, not traitlets.

## What the fast renderer changes

Goal: an update should cost work proportional to what actually changed, not a
full tree walk. With the default renderer, a single-leaf state change, a
memoized-subtree "skip", and a full `force_update` all cost the same (~14ms on a
300-row tree), and stale-element removal is accidentally quadratic. The fast
renderer (`_RenderContextFast`, `REACTON_FAST=1`) addresses both:

- **Dirty-subtree skipping.** State setters mark `needs_render_descendant` up
  the parent chain, so a render pass only descends into subtrees that can
  contain work. A component subtree whose element is identical to the previous
  render (`el is el_prev`), is fully reconciled, and has no dirty/excepted
  contexts is skipped in *both* phases and keeps its previous widgets
  (`clean_subtree`).
- **Forced full walks** (`force_update()`, `update()`, the first render) set
  `rc._walk_all`, disabling skipping for that pass — faithful to the old
  behavior.
- **Stale-element removal** runs once per component context (and once for the
  root context in `render()`) instead of an O(elements) set-difference per
  element.
- **Widget updates** are skipped when an identical element reconciles to
  identical child widget objects (`_values_identical`), avoiding pointless
  traitlets assignments.
- **Side-effect ("orphan") widgets** (Layout/Style created during construction)
  are tracked via ipywidgets' `on_widget_constructed` hook instead of diffing
  the global widgets dict per creation — the old diff was O(live widgets) per
  widget, so it degraded as an app grew.

## Renderer contract

What both renderers must preserve (derived from `core.py` + the test suite).
The fast renderer overrides only `_render`, `_reconsolidate`, `_remove_element`,
`_visit_children`, `_visit_children_values`; everything else (Element widget
create/update/close, hooks storage, `ComponentContext`, exception plumbing, the
render loop) is shared with the default renderer.

**Phases** (inside one `rc.render()` call, under `thread_lock`, with `local.rc` set):

1. *Render phase*: execute component functions depth-first, build
   `elements_next`/`children_next`. Repeat while `_rerender_needed` (max 50,
   then `RuntimeError`) and no exception has bubbled up.
2. *Reconsolidate phase*: create/update/close widgets, run effects, move
   `*_next` → current. Loop back to phase 1 if state was set during reconcile
   (e.g. in an effect). `render()` returns the root widget.

**Keys.** `el._key` or a positional default. A context's root key is `"/"`.
Children of an element with key `K`: list → `f"{K}{i}/"`, dict → `f"{K}{k}/"`.
Component child contexts live in `context.children[key]`. A duplicate key in one
context raises `KeyError`. `el._key_frozen` is set once an element is rendered.

**Render phase, per element:**
- `el._render_count += 1` (a shared element is visited once; a non-shared one
  per use — see `test_render_count_element`).
- Element arguments (args/kwargs) are walked only for `ComponentWidget`
  elements or shared elements; a `ComponentFunction` element does not walk its
  arguments.
- `ComponentFunction`: reuse the `ComponentContext` when
  `same_component(invoke_element.component, el.component)`, or when a context
  exists with no `root_element` (pre-created by `state_set`). A different
  component → fresh context, old one removed during reconcile.
- `needs_render` = `context.needs_render` (set by setters/force) OR
  `el._arguments_changed(el_prev)` OR `context.exceptions_children`. If false,
  the body is *not* executed (component `render_count` stays put), the previous
  `root_element` is reused, but it is still walked.
- Body execution resets `state_index`/`effect_index`/`memo_index`,
  `user_contexts={}`, `exception_handler=False`, `needs_render=False` before the
  call; wraps in `context_managers` (the solara `ContextManager` hook) and the
  `_default_container` handling (implicit containers via
  `ContainerAdder`/`el.__enter__`).
- Body exceptions → `context.exceptions_self`, set `_rerender_needed`; a
  hook-count mismatch is itself an error (fewer calls only allowed if an
  exception interrupted the body); a component returning `None` → `ValueError`.
- After: `parent.children_next[key] = context`; prune `children_next`/
  `elements_next` to `used_keys`; `user_contexts_prev = user_contexts`.
  Exceptions bubble to `parent.exceptions_children` unless `exception_handler`
  (set by `use_exception` during the body).

**Reconsolidate phase, per element** (depth-first over the element tree,
entering child contexts):
- *Widget element*: visit children → new kwargs (Elements replaced by widgets;
  `FragmentWidget` children flattened into lists); then create / update-in-place
  (same component) / replace (remove old first). Created via `el._create_widget`
  (orphan side-effect widgets tracked into `rc._orphans[widget.model_id]`);
  updated via `el._update_widget` (dropped kwargs restored to trait defaults,
  listeners removed) under `hold_sync` + `suppress_events`.
- *Component element*: recurse into the child context root, then process
  effects: an `effect.next` with equal deps drops `next`; otherwise clean up the
  old effect and run the next; never-executed effects run now; all are skipped
  (cleanups still run) if the context has exceptions.
- `el.meta` / root-widget meta merge → `widget._react_meta`.
- Bookkeeping: `elements_next[key]` → `elements[key]`; `children_next[key]` →
  `children[key]`; shared elements move `_shared_elements_next` →
  `_shared_elements` with the widget in `rc._shared_widgets` (one widget per rc);
  non-shared widget in `context.widgets[key]`; `context.element_to_widget[el]`
  set (used by `get_widget`).
- Stale keys (old elements whose key is not in `used_keys`) → `_remove_element`,
  in sorted order for reproducibility.
- After reconciling a context, `elements_next` must be empty (shared leftovers
  are moved), else `RuntimeError`. `root_element = root_element_next`;
  `root_element_next = None` (asserted by `test_internals`).

**Removal.**
- *Component element*: clean up all effects, recurse into `root_element`, assert
  the context is fully empty, `del parent.children[key]`; cleanup exceptions
  bubble (`close()` raises the first).
- *Widget element*: recurse children first, close orphans,
  `el._cleanup_callbacks(widget)`, `el._close_widget(widget)`. Shared widgets are
  removed only on the last reference.
- Removing an already-removed key is a no-op (`test_remove_element_twice`).

`close()`: `_remove_element(root)`, container closed (+layout), asserts
`_shared_elements`/`_orphans` empty, raises any pending exception.

**Other pinned behavior:** `rc.render_count` increments per `render()` call;
root widget type change without a container → `ValueError`; container gets
`.children = [widget]` (`[]` on error). `handle_error=True` renders an HTML
traceback widget instead of raising. Batching: `with rc:` defers re-render, and
`hold_trait_notifications` is wrapped so frontend-triggered trait updates batch
into a single render. Setters use `eq`/`utils.equals`, warn on mutated
list/dict/DataFrame state, are ignored while `_closing`, and trigger a render
unless already rendering or batching. `use_context`/`provide` walk parent
contexts; `provide` notifies listeners only when the value changed.

## Deliberate behavior deltas (not observable by the test suite)

- Stale elements are now closed *after* the parent widget gets its new children
  assigned (the old code closed them mid-walk, so a closed widget could briefly
  remain in a container's `children`).
- Per-element debug logging in the hot paths was dropped.

## Known issues worth revisiting (found during the rewrite, not fixed here)

- **Effect/cleanup exceptions** are recorded on the *parent* context's
  `exceptions_self`, while render exceptions go to the component's own context.
  So an effect exception is caught by `use_exception` one level higher than a
  render exception would be. Behavior preserved from the old code; looks
  unintentional.
- **pandas 3.0**: setting state to an equal DataFrame triggers a re-render and
  leaks widgets (`test_set_state_with_dataframe`). The reacton equality logic
  likely needs a pandas-3 fix; the test environment pins `pandas<3` for now.
- `ComponentContext.owns` is dead — never written, only asserted empty in
  `_remove_element`.

## Where initial-render time goes

After the rewrite, initial render is dominated by ipywidget *construction*, not
reconciler tree-walking — most of it is traitlets default materialization and
`get_state` during `Widget.open()`. Reacton-side reconciliation of a large tree
is now a small fraction of that. Future initial-render wins are mostly in
ipywidgets/traitlets, not here.
