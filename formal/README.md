# Render requests and the render lock: decisions and their model

Reacton renders from many threads: a state change renders on the thread that makes it, and a
background thread can change state while another thread renders. This file lists the decisions
that keep that free of deadlocks and lost updates. Each decision names the code that implements
it, the test that shows it, and the part of the TLA+ model (`render_requests.tla`) that checks it.
When you change one of these places in `reacton/core.py`, update the decision, the model and the
test together, and run `formal/check.sh`.

## Words

- **render lock**: `_RenderContext.thread_lock`. Whoever holds it may change the tree.
- **holder**: the thread that holds the render lock.
- **request**: a state change (the setter of `use_state`), `update(el)`, `render(el)`,
  `force_update()`, or the end of a batch (`with rc:`). A request asks for a render.
- **pass**: one run over the components (`_render`), in the render loop of `_render_once`.
- **mark**: `_rerender_needed`, "a render is needed". `_element_next`: the last requested root element.

## Decisions

| | Decision | Why | Code (`reacton/core.py`) | Test (`reacton/threads_test.py` unless noted) | Model |
|---|---|---|---|---|---|
| D1 | The render lock is the only lock that guards the tree. It is held by a render (`_render_once`) or by `close()`. A render reads what it needs from the tree (the errors of its pass) before it releases the lock. Nothing else in reacton blocks, except the batch counter's lock, which is held around `+= 1` only. | One lock and no other waits: a deadlock needs a circle of waits. After the release, `close()` on another thread can tear the tree down. | `thread_lock`, `_render_once` (`exceptions = ...` before the `finally`), `utils.ThreadSafeCounter` | `test_close_right_after_a_render_released_the_render_lock` | `lockOwner`, `ReadErrors`, `ErrorsReadUnderLock` |
| D2 | A request never waits for the render lock. It marks itself first (`_element_next` when it brings an element, then `_rerender_needed`), and only then looks at `_is_rendering` or *tries* the lock. When another thread holds it, the request is left to that thread. | A requester can hold a lock (its own, a solara store lock) that the render needs: waiting would deadlock. Marking first is what D5 needs. | `set_`, `force_update` (`update` calls it), `_render_once` (the mark, `acquire(blocking=False)`), `_possible_rerender`, `render` | `test_render_request_while_holding_a_user_lock_does_not_deadlock[set_state, update, render, force_update]`, `test_force_update_after_the_last_look_is_rendered` | `ReqWrite`, `ReqMarkReadRerender`, `ReqMarkWriteRerender`, `RenderEntryTryLock`, `NoDeadlock` |
| D3 | A state change, `update()` or `force_update()` during a running render (`_is_rendering`) only marks, it does not try the lock: the running render loop sees the mark. (An explicit `render(el)` tries the lock anyway; that does not wait either.) | The loop re-renders before it commits, so the change is not rendered twice. | `set_` → `_possible_rerender`, `force_update` | `test_state_change_during_a_render_only_marks` | `ReqCheckRendering` |
| D4 | At the start of each pass the holder first clears `_rerender_needed`, and then takes `_element_next` into `self.element`. | A request writes the element before the mark. So either this pass uses the new element, or the mark stays set and there is one more pass. | `_render_once`: the render start and the inner loop | `test_element_request_right_after_a_pass_took_the_element_is_rendered` | `PassStart`, `NoLostRequest` |
| D5 | After the holder released the render lock, it looks at `_rerender_needed` again, and renders again when it is set (unless a render runs, or a batch is open). `render()` does this in a loop, not by recursion. | A request writes the mark, then reads `_is_rendering` or tries the lock. The holder releases the lock, then reads the mark. One of the two always sees the other, so a request is never lost. | `render` (the `while` loop around `_render_once`) | `test_state_change_from_another_thread_after_the_last_check_is_rendered`, `test_many_changes_after_the_last_look_in_a_row_do_not_recurse` | `Release`, `RenderLoopReadMark`, `RenderLoopDecide`, `LookAgain`, `NoLostRequest` |
| D6 | While a batch (`with rc:`) is open, a state change only marks. The end of the batch renders when the mark is set. | Many changes, one render. | `__enter__`, `__exit__`, `_possible_rerender` | `core_test.py::test_batch_update`, `core_test.py::test_batch_update_from_render` | not modeled |
| D7 | The render loop of one `_render_once` stops with "Too many renders" after about 50 passes of its own. Once another thread changed state during a pass, the limit is about 100 passes, once. The other-thread mark (`_state_set_by_other_thread`) is cleared when a render starts. The holder raises, not the thread that changed state. | A component that sets state on every render must fail. A progress update from another thread is not such a loop, but a thread that changes state during every pass must not keep the holder busy forever: its caller would not return, and `close()` waits. | `_render_once` (`render_limit`), `set_` (`_state_set_by_other_thread`) | `test_state_changes_from_another_thread_are_not_a_render_loop`, `test_render_loop_for_another_thread_is_bounded`, `test_own_render_loop_stops_after_about_50_passes` | `LoopReadRerender`, `LoopReadOther`, `LoopClearOther`, `LoopCompare`, `EFFECT_SETS_STATE`, `BoundedPasses`, `budget.cfg` |
| D8 | `close()` is the only code that waits for the render lock: it must not tear the tree down during a render. Called from its own render it raises. On a closing or closed render context it returns. After it got the lock, it checks again. | Waiting in its own render would wait for itself. A second `close()` (or one from an effect cleanup during `close()`) must not wait or tear down twice. | `close` | `test_close_from_its_own_render_raises_instead_of_hanging`, `test_close_during_or_after_close_returns`, `test_two_close_calls_at_the_same_time_tear_down_once` | `CloseOwnCheck`, `CloseClosingCheck`, `CloseAcquire`, `CloseRecheck`, `CloseTeardown`, `CleanupCloseClosingCheck`, `TeardownOnce` |
| D9 | Once closing, a request does nothing: the setter and `force_update()` return at once, and a render that gets the lock returns without a pass. | The tree is (being) torn down. | `set_` (`_closing`), `force_update`, `_render_once` (`self._closing`) | `test_close_during_or_after_close_returns`, `test_render_on_a_closed_render_context_leaves_nothing_behind` | `ReqClosingCheck`, `ReqUpdateForceClosingCheck`, `PassStart`, `NoPassAfterClose` |
| D10 | The render lock is taken inside the `try`, in one statement with the assignment `locked = ...acquire(blocking=False)`. | An exception right after it (an interrupt, a cancel from a trace function, like solara's `cancel_guard`) must still release the lock: a leaked render lock stops every later render. | `_render_once` (`locked = ...`, the `finally`) | `test_exception_right_after_the_render_lock_is_taken_does_not_leak_it` | not modeled |
| D11 | `_lock_thread` is the holder while a render holds the lock, and is cleared where the lock is released, on every way out. A render or `close()` from inside its own render raises ("Recursive render detected", "close() called during a render"). | Both would wait for, or leave the render to, themselves. A stale `_lock_thread` makes those checks fire for a thread that merely rendered last. | `_render_once` (`_lock_thread`, the outer `finally`), `close` | `test_render_from_its_own_render_raises`, `test_close_from_its_own_render_raises_instead_of_hanging`, `test_render_on_a_closed_render_context_leaves_nothing_behind` | not modeled (the model's `lockThread` only serves D7) |
| D12 | Constructing a widget takes no lock. Each thread records the widgets it constructs in a thread-local list. | A global lock around widget construction blocked every kernel behind one slow client. | `_ConstructionRecording`, `_record_constructed_widget`, `_create_widget` | `core_test.py::test_widget_construction_does_not_block_other_threads`, `core_test.py::test_widget_created_by_another_thread_is_not_an_orphan` | not modeled |
| D13 | `close()` and the cleanup of an aborted pass visit each component context once. | After a render that failed, a context can be in both `children` and `children_next`; a visit per path is `2**depth` visits, a hang while the render lock is held. | `close` (`collect`), `_discard_aborted_pass` | `core_test.py::test_close_after_a_failed_render_of_a_deep_tree_is_fast` | not modeled |

## Known limits

These follow from the decisions above, or are older behavior that the decisions do not cover.

- **L1**: `close()` by a thread that holds a lock which the running render needs deadlocks,
  because `close()` waits for the render (D8). Solara's teardown releases `context.lock` before it
  closes. The model shows this deadlock when the closer holds the user lock (`closer_holds_user_lock.cfg`).
- **L2**: a request that wins the render lock renders on its own thread. If that thread holds a
  *non-reentrant* lock that a component or an effect also takes, it waits for itself. (A reentrant
  lock, like the model's user lock, is fine.)
- **L3**: when the holder's render raises (`handle_error=False`) or is interrupted, a request that
  was left to it is not rendered until the next request. An interrupt right after a pass start
  cleared the mark also clears that request's mark. With `handle_error=True`, the error message
  replaces a root element that another thread requested during that render.
- **L4**: exceptions raised *inside* reacton's own code by an interrupt or a trace function (solara's
  `cancel_guard` before it stopped raising in library frames) can leave it stuck: on the line that
  releases the render lock (the lock leaks), in a batch's `__enter__` after the count went up (no
  render until the count is fixed), or during `close()`'s teardown (`_closing` is already set, so
  `close()` is not retried and the tree is not freed). D10 only covers the step right after the acquire.
- **L5**: D7 limits the passes of one `_render_once`. The loop in `render()` (D5) starts a new
  count; a thread whose change lands right after every last look can keep it going.
  A thread that changes state during every pass for more than about 100 passes gets "Too many renders".
- **L6**: D4 and D5 rely on Python running attribute reads and writes in program order. The GIL
  gives that.
- **L7**: an explicit `rc.render(el, container)` that finds the render lock taken returns the
  container at once, before its element is on screen (D2); the holder renders it into its own
  container.
- **L8**: a functional setter (`set_x(lambda x: x + 1)`) is not atomic across threads: two threads can
  read the same old value. Use your own lock around it (a setter never waits for the render lock, D2).
  A functional setter that runs while `close()` tears down can raise a `KeyError`.
- **L9**: `force_update()` sets `_walk_all`; a pass that ends right after clears it, so the next pass
  may skip subtrees in which no state changed. The event handlers that route an exception mark
  the path to it (`_mark_needs_render_ancestors`) for this reason.

## The model

`render_requests.tla` models the render lock, the marks, requesting threads that hold a (reentrant) user lock while they request, a render pass whose effect takes that user lock or sets state on the holder's own thread, and closing threads.
A request is one of: a state change, `update(el)`, an explicit `render(el)` (no `_is_rendering` check), or `force_update()` after data outside the state changed.
The model records `forceVer` to check that a pass ran after the last forced update.
It does not model which subtrees that pass re-walks (L9).
Each action carries the decision it models in a comment, and names the function and the statement.
Checked properties:

- `NoDeadlock`: TLC's deadlock check (on by default); the only state without a next step is the end,
  where every thread is done (`DoneStutter`).
- `NoLostRequest`: at the end, the last pass saw the last state change, the last forced update and
  the last requested element, the mark is clear and the lock is free, unless the render context was
  closed or a loop stopped with "Too many renders".
- `NoPassAfterClose`: no pass starts once `close()` marked the render context as closing.
- `BoundedPasses`: a render does at most its limit of passes, plus one.
- `TeardownOnce`: `close()` tears down at most once.
- `ErrorsReadUnderLock`: `_render_once` reads the collected child errors before it releases the render lock, while the render context is still live.

`render_requests.cfg` keeps the closer, so it checks close/request interleavings.
`no_closer.cfg` removes the closer, so `NoLostRequest` reaches non-closed end states.
`budget.cfg` turns on the own-thread setter during a pass, so "Too many renders" is reachable and allowed.
`budget_reachable.cfg` adds `NoTooMany`, which must fail and proves that path is checked.

Every check also runs on a broken copy of the model: one mutation constant per `*.cfg` in
`mutations/`, and each must fail with the expected error. That shows the checks can fail.

| Mutation | Breaks | Fails with |
|---|---|---|
| `blocking_request` | D2: a request waits for the render lock | deadlock |
| `read_before_mark` | D2: a request looks at `_is_rendering` before it marks (`update()` and `force_update()` did this until #77) | `NoLostRequest` |
| `element_before_clear` | D4 | `NoLostRequest` |
| `no_look_again` | D5 | `NoLostRequest` |
| `limit_reset` | D7: another thread's change starts the count again (before #76) | `BoundedPasses` |
| `close_no_own_check` | D8: `close()` from its own render waits for itself | deadlock |
| `close_no_closing_check` | D8: a cleanup's nested `close()` during `close()` waits for the lock its own thread holds | deadlock |
| `close_no_recheck` | D8 | `TeardownOnce` |
| `read_errors_after_release` | D1: a render reads child errors after releasing the render lock | `ErrorsReadUnderLock` |

`closer_holds_user_lock.cfg` is limit L1, and must fail with a deadlock.
`cleanup_calls_close.cfg` checks the passing D8 case where a cleanup calls `close()` during `close()`.

## Run it

```bash
formal/check.sh
```

It needs Java 11 or newer, and downloads `tla2tools.jar` (1.7.4, the latest stable release; the sha256 is pinned) to `~/.cache/tla/` the first
time. CI runs it (`.github/workflows/formal.yaml`) when `reacton/core.py` or `formal/` changes.
