----------------------------- MODULE render_requests -----------------------------
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
    Requesters,
    Closers,
    NoThread,
    MaxRequests,
    OwnLimit,
    OtherLimit,
    AllowedRequestKinds,
    REQUESTER_HOLDS_USER_LOCK,
    EFFECT_TAKES_USER_LOCK,
    EFFECT_SETS_STATE,
    MUT_BLOCKING_REQUEST,
    MUT_ELEMENT_BEFORE_CLEAR,
    MUT_NO_LOOK_AGAIN,
    MUT_READ_BEFORE_MARK,
    MUT_CLOSE_NO_OWN_CHECK,
    MUT_CLOSE_NO_CLOSING_CHECK,
    MUT_CLOSE_NO_RECHECK,
    MUT_LIMIT_RESET,
    MUT_READ_ERRORS_AFTER_RELEASE,
    EFFECT_CALLS_CLOSE,
    CLEANUP_CALLS_CLOSE,
    CLOSER_HOLDS_USER_LOCK

Threads == Requesters \cup Closers
RequestKinds == {"state", "update", "render", "force"}
VersionBound == (Cardinality(Requesters) * MaxRequests * 4) + MaxRequests + 2
ElemBound == (Cardinality(Requesters) * MaxRequests) + 1

VARIABLES
    pc,
    reqCount,
    reqKind,
    reqHoldsUser,
    checkedRendering,
    markLockOther,
    markNeedsWrite,
    renderFirstCall,
    renderReadRendered,
    renderReadMark,
    renderReadRendering,
    lockOwner,
    lockThread,
    userOwner,
    userDepth,
    closing,
    closed,
    isRendering,
    rerenderNeeded,
    otherThreadMark,
    elementNext,
    element,
    stateVer,
    forceVer,
    lastPassState,
    lastPassForce,
    lastPassElem,
    passAfterClose,
    teardownCount,
    tooMany,
    rendered,
    nestedCount,
    totalNestedCount,
    renderLimit,
    effectCloseRaised,
    effectSetCount,
    loopNeedsRender,
    loopOtherMark,
    cleanupCloseCalled

vars ==
    << pc, reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
       markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
       renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
       closed, isRendering, rerenderNeeded, otherThreadMark, elementNext, element,
       stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
       passAfterClose, teardownCount, tooMany, rendered, nestedCount,
       totalNestedCount, renderLimit, effectCloseRaised, effectSetCount,
       loopNeedsRender, loopOtherMark, cleanupCloseCalled >>

CanUseUser(t) == userOwner = NoThread \/ userOwner = t
ReleaseUserOwner(t) == IF userOwner = t /\ userDepth = 1 THEN NoThread ELSE userOwner
ReleaseUserDepth(t) == IF userOwner = t /\ userDepth = 1 THEN 0 ELSE IF userOwner = t THEN userDepth - 1 ELSE userDepth
DonePc(r, n) == IF n = MaxRequests THEN "done" ELSE "idle"

AllDone ==
    /\ \A r \in Requesters: pc[r] = "done"
    /\ \A c \in Closers: pc[c] = "done"

FinishRequest(r) ==
    /\ pc' = [pc EXCEPT ![r] = DonePc(r, reqCount[r] + 1)]
    /\ reqCount' = [reqCount EXCEPT ![r] = @ + 1]
    /\ userOwner' = IF reqHoldsUser[r] THEN ReleaseUserOwner(r) ELSE userOwner
    /\ userDepth' = IF reqHoldsUser[r] THEN ReleaseUserDepth(r) ELSE userDepth

StartRenderCall(r) ==
    /\ rendered' = [rendered EXCEPT ![r] = TRUE]
    /\ renderFirstCall' = [renderFirstCall EXCEPT ![r] = TRUE]
    /\ renderReadRendered' = [renderReadRendered EXCEPT ![r] = TRUE]
    /\ renderReadMark' = [renderReadMark EXCEPT ![r] = FALSE]
    /\ renderReadRendering' = [renderReadRendering EXCEPT ![r] = FALSE]
    /\ effectSetCount' = [effectSetCount EXCEPT ![r] = 0]
    /\ pc' = [pc EXCEPT ![r] = "render_loop_read_rendered"]

Init ==
    /\ pc = [t \in Threads |-> IF t \in Closers THEN "close_start" ELSE "idle"]
    /\ reqCount = [r \in Requesters |-> 0]
    /\ reqKind = [r \in Requesters |-> "state"]
    /\ reqHoldsUser = [r \in Requesters |-> FALSE]
    /\ checkedRendering = [r \in Requesters |-> FALSE]
    /\ markLockOther = [r \in Requesters |-> FALSE]
    /\ markNeedsWrite = [r \in Requesters |-> FALSE]
    /\ renderFirstCall = [r \in Requesters |-> FALSE]
    /\ renderReadRendered = [r \in Requesters |-> FALSE]
    /\ renderReadMark = [r \in Requesters |-> FALSE]
    /\ renderReadRendering = [r \in Requesters |-> FALSE]
    /\ lockOwner = NoThread
    /\ lockThread = NoThread
    /\ userOwner = NoThread
    /\ userDepth = 0
    /\ closing = FALSE
    /\ closed = FALSE
    /\ isRendering = FALSE
    /\ rerenderNeeded = FALSE
    /\ otherThreadMark = FALSE
    /\ elementNext = 0
    /\ element = 0
    /\ stateVer = 0
    /\ forceVer = 0
    /\ lastPassState = 0
    /\ lastPassForce = 0
    /\ lastPassElem = 0
    /\ passAfterClose = FALSE
    /\ teardownCount = 0
    /\ tooMany = FALSE
    /\ rendered = [r \in Requesters |-> FALSE]
    /\ nestedCount = 0
    /\ totalNestedCount = 0
    /\ renderLimit = OwnLimit
    /\ effectCloseRaised = FALSE
    /\ effectSetCount = [r \in Requesters |-> 0]
    /\ loopNeedsRender = FALSE
    /\ loopOtherMark = FALSE
    /\ cleanupCloseCalled = FALSE

TypeOK ==
    /\ AllowedRequestKinds \subseteq RequestKinds
    /\ pc \in [Threads -> {
        "idle", "done", "req_closing_check", "req_write",
        "req_update_force_closing_check", "req_mark_read_lock_thread",
        "req_mark_write_other", "req_mark_read_rerender",
        "req_mark_write_rerender", "req_check_rendering_before_mark",
        "req_check_rendering", "render_loop_read_rendered",
        "render_loop_read_mark", "render_loop_read_is_rendering",
        "render_loop_decide", "render_entry_write_element",
        "render_entry_read_mark", "render_entry_write_mark",
        "render_entry_try_lock", "pass_start_check",
        "pass_start_clear_mark", "pass_start_clear_other",
        "pass_start_take_elem", "pass_start_set_rendering",
        "pass_render", "loop_read_rerender", "loop_read_other",
        "loop_clear_other", "loop_compare", "stop_rendering",
        "read_errors", "release", "look_again", "close_start",
        "close_closing_check", "close_acquire", "close_recheck",
        "close_teardown", "cleanup_close_closing_check",
        "cleanup_close_acquire", "close_teardown_finish"}]
    /\ reqCount \in [Requesters -> 0..MaxRequests]
    /\ reqKind \in [Requesters -> RequestKinds]
    /\ reqHoldsUser \in [Requesters -> BOOLEAN]
    /\ checkedRendering \in [Requesters -> BOOLEAN]
    /\ markLockOther \in [Requesters -> BOOLEAN]
    /\ markNeedsWrite \in [Requesters -> BOOLEAN]
    /\ renderFirstCall \in [Requesters -> BOOLEAN]
    /\ renderReadRendered \in [Requesters -> BOOLEAN]
    /\ renderReadMark \in [Requesters -> BOOLEAN]
    /\ renderReadRendering \in [Requesters -> BOOLEAN]
    /\ lockOwner \in Threads \cup {NoThread}
    /\ lockThread \in Requesters \cup {NoThread}
    /\ userOwner \in Threads \cup {NoThread}
    /\ userDepth \in 0..2
    /\ closing \in BOOLEAN
    /\ closed \in BOOLEAN
    /\ isRendering \in BOOLEAN
    /\ rerenderNeeded \in BOOLEAN
    /\ otherThreadMark \in BOOLEAN
    /\ elementNext \in 0..ElemBound
    /\ element \in 0..ElemBound
    /\ stateVer \in 0..VersionBound
    /\ forceVer \in 0..VersionBound
    /\ lastPassState \in 0..VersionBound
    /\ lastPassForce \in 0..VersionBound
    /\ lastPassElem \in 0..ElemBound
    /\ passAfterClose \in BOOLEAN
    /\ teardownCount \in 0..(Cardinality(Closers) + 1)
    /\ tooMany \in BOOLEAN
    /\ rendered \in [Requesters -> BOOLEAN]
    /\ nestedCount \in 0..VersionBound
    /\ totalNestedCount \in 0..VersionBound
    /\ renderLimit \in {OwnLimit, OtherLimit}
    /\ effectCloseRaised \in BOOLEAN
    /\ effectSetCount \in [Requesters -> 0..MaxRequests]
    /\ loopNeedsRender \in BOOLEAN
    /\ loopOtherMark \in BOOLEAN
    /\ cleanupCloseCalled \in BOOLEAN

\* D9, set_ / force_update: if self._closing: return.
ReqStart(r) ==
    /\ r \in Requesters
    /\ pc[r] = "idle"
    /\ reqCount[r] < MaxRequests
    /\ \E k \in AllowedRequestKinds:
       \E hold \in {FALSE, TRUE}:
        /\ hold => REQUESTER_HOLDS_USER_LOCK
        /\ ~hold \/ CanUseUser(r)
        /\ reqKind' = [reqKind EXCEPT ![r] = k]
        /\ reqHoldsUser' = [reqHoldsUser EXCEPT ![r] = hold]
        /\ checkedRendering' = [checkedRendering EXCEPT ![r] = FALSE]
        /\ pc' = [pc EXCEPT ![r] =
              IF k \in {"state", "force"} THEN "req_closing_check"
              ELSE IF k = "update" THEN "req_write"
              ELSE "render_loop_read_rendered"]
        /\ userOwner' = IF hold /\ userOwner = NoThread THEN r ELSE userOwner
        /\ userDepth' = IF hold THEN IF userOwner = r THEN userDepth + 1 ELSE IF userOwner = NoThread THEN 1 ELSE userDepth ELSE userDepth
        /\ rendered' = [rendered EXCEPT ![r] = TRUE]
        /\ renderFirstCall' = [renderFirstCall EXCEPT ![r] = TRUE]
        /\ renderReadRendered' = [renderReadRendered EXCEPT ![r] = TRUE]
        /\ renderReadMark' = [renderReadMark EXCEPT ![r] = FALSE]
        /\ renderReadRendering' = [renderReadRendering EXCEPT ![r] = FALSE]
        /\ effectSetCount' = [effectSetCount EXCEPT ![r] = 0]
    /\ UNCHANGED <<reqCount, markLockOther, markNeedsWrite, lockOwner, lockThread,
        closing, closed, isRendering, rerenderNeeded, otherThreadMark, elementNext,
        element, stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
        passAfterClose, teardownCount, tooMany, nestedCount, totalNestedCount,
        renderLimit, effectCloseRaised, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D9, set_: if self._closing: return.
\* D9, force_update: if self._closing: return.
ReqClosingCheck(r) ==
    /\ r \in Requesters
    /\ pc[r] = "req_closing_check"
    /\ IF closing
       THEN FinishRequest(r)
       ELSE
          /\ pc' = [pc EXCEPT ![r] = "req_write"]
          /\ reqCount' = reqCount
          /\ userOwner' = userOwner
          /\ userDepth' = userDepth
    /\ UNCHANGED <<reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D2, set_: context.state[key] = value (a state change).
\* D2, update: self._element_next = element before force_update().
\* D2, force_update() is called after data outside the state changed.
ReqWrite(r) ==
    /\ r \in Requesters
    /\ pc[r] = "req_write"
    /\ stateVer' = IF reqKind[r] = "state" THEN stateVer + 1 ELSE stateVer
    /\ elementNext' = IF reqKind[r] = "update" THEN elementNext + 1 ELSE elementNext
    /\ forceVer' = IF reqKind[r] = "force" THEN forceVer + 1 ELSE forceVer
    /\ pc' = [pc EXCEPT ![r] =
          IF reqKind[r] = "update" THEN "req_update_force_closing_check"
          ELSE IF MUT_READ_BEFORE_MARK THEN "req_check_rendering_before_mark"
          ELSE "req_mark_read_lock_thread"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, otherThreadMark, element,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D9, update: self._element_next is written, then force_update() returns at its closing check.
ReqUpdateForceClosingCheck(r) ==
    /\ r \in Requesters
    /\ pc[r] = "req_update_force_closing_check"
    /\ IF closing
       THEN FinishRequest(r)
       ELSE
          /\ pc' = [pc EXCEPT ![r] = IF MUT_READ_BEFORE_MARK THEN "req_check_rendering_before_mark" ELSE "req_mark_read_lock_thread"]
          /\ reqCount' = reqCount
          /\ userOwner' = userOwner
          /\ userDepth' = userDepth
    /\ UNCHANGED <<reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D2, read-before-mark mutation: _possible_rerender reads _is_rendering too early.
ReqCheckRenderingBeforeMark(r) ==
    /\ r \in Requesters
    /\ pc[r] = "req_check_rendering_before_mark"
    /\ checkedRendering' = [checkedRendering EXCEPT ![r] = isRendering]
    /\ pc' = [pc EXCEPT ![r] = "req_mark_read_lock_thread"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, markLockOther, markNeedsWrite,
        renderFirstCall, renderReadRendered, renderReadMark, renderReadRendering,
        lockOwner, lockThread, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D7, set_: read _lock_thread and decide whether to set _state_set_by_other_thread.
ReqMarkReadLockThread(r) ==
    /\ r \in Requesters
    /\ pc[r] = "req_mark_read_lock_thread"
    /\ markLockOther' = [markLockOther EXCEPT ![r] = reqKind[r] = "state" /\ lockThread # r]
    /\ pc' = [pc EXCEPT ![r] = "req_mark_write_other"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markNeedsWrite,
        renderFirstCall, renderReadRendered, renderReadMark, renderReadRendering,
        lockOwner, lockThread, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D7, set_: self._state_set_by_other_thread = True.
ReqMarkWriteOther(r) ==
    /\ r \in Requesters
    /\ pc[r] = "req_mark_write_other"
    /\ otherThreadMark' = (otherThreadMark \/ markLockOther[r])
    /\ pc' = [pc EXCEPT ![r] = "req_mark_read_rerender"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, elementNext, element, stateVer,
        forceVer, lastPassState, lastPassForce, lastPassElem, passAfterClose,
        teardownCount, tooMany, rendered, nestedCount, totalNestedCount,
        renderLimit, effectCloseRaised, effectSetCount, loopNeedsRender,
        loopOtherMark, cleanupCloseCalled>>

\* D2, set_ / force_update: if self._rerender_needed is False.
ReqMarkReadRerender(r) ==
    /\ r \in Requesters
    /\ pc[r] = "req_mark_read_rerender"
    /\ markNeedsWrite' = [markNeedsWrite EXCEPT ![r] = ~rerenderNeeded]
    /\ pc' = [pc EXCEPT ![r] = "req_mark_write_rerender"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        renderFirstCall, renderReadRendered, renderReadMark, renderReadRendering,
        lockOwner, lockThread, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D2, set_ / force_update: self._rerender_needed = True.
ReqMarkWriteRerender(r) ==
    /\ r \in Requesters
    /\ pc[r] = "req_mark_write_rerender"
    /\ rerenderNeeded' = (rerenderNeeded \/ markNeedsWrite[r])
    /\ LET finishes ==
          MUT_READ_BEFORE_MARK /\ checkedRendering[r]
       IN
       /\ IF finishes
          THEN FinishRequest(r)
          ELSE
             /\ pc' = [pc EXCEPT ![r] = "req_check_rendering"]
             /\ reqCount' = reqCount
             /\ userOwner' = userOwner
             /\ userDepth' = userDepth
    /\ UNCHANGED <<reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, closing, closed, isRendering,
        otherThreadMark, elementNext, element, stateVer, forceVer, lastPassState,
        lastPassForce, lastPassElem, passAfterClose, teardownCount, tooMany,
        rendered, nestedCount, totalNestedCount, renderLimit, effectCloseRaised,
        effectSetCount, loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D3, _possible_rerender / force_update: if not self._is_rendering.
ReqCheckRendering(r) ==
    /\ r \in Requesters
    /\ pc[r] = "req_check_rendering"
    /\ IF isRendering
       THEN
          /\ FinishRequest(r)
          /\ UNCHANGED <<rendered, renderFirstCall, renderReadRendered,
              renderReadMark, renderReadRendering, effectSetCount>>
       ELSE
          /\ StartRenderCall(r)
          /\ reqCount' = reqCount
          /\ userOwner' = userOwner
          /\ userDepth' = userDepth
    /\ UNCHANGED <<reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, lockOwner, lockThread, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, nestedCount, totalNestedCount, renderLimit, effectCloseRaised,
        loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D5, render: read the per-call rendered local.
RenderLoopReadRendered(r) ==
    /\ r \in Requesters
    /\ pc[r] = "render_loop_read_rendered"
    /\ renderReadRendered' = [renderReadRendered EXCEPT ![r] = rendered[r]]
    /\ pc' = [pc EXCEPT ![r] = "render_loop_read_mark"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadMark, renderReadRendering,
        lockOwner, lockThread, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D5, render: read self._rerender_needed.
RenderLoopReadMark(r) ==
    /\ r \in Requesters
    /\ pc[r] = "render_loop_read_mark"
    /\ renderReadMark' = [renderReadMark EXCEPT ![r] = rerenderNeeded]
    /\ pc' = [pc EXCEPT ![r] = "render_loop_read_is_rendering"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadRendering,
        lockOwner, lockThread, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D5, render: read self._is_rendering.
RenderLoopReadIsRendering(r) ==
    /\ r \in Requesters
    /\ pc[r] = "render_loop_read_is_rendering"
    /\ renderReadRendering' = [renderReadRendering EXCEPT ![r] = isRendering]
    /\ pc' = [pc EXCEPT ![r] = "render_loop_decide"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        lockOwner, lockThread, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D5, render: while rendered and self._rerender_needed and not self._is_rendering.
RenderLoopDecide(r) ==
    /\ r \in Requesters
    /\ pc[r] = "render_loop_decide"
    /\ IF renderFirstCall[r] \/
          (renderReadRendered[r] /\ renderReadMark[r] /\ ~renderReadRendering[r] /\ ~MUT_NO_LOOK_AGAIN)
       THEN
          /\ pc' = [pc EXCEPT ![r] = "render_entry_write_element"]
          /\ reqCount' = reqCount
          /\ userOwner' = userOwner
          /\ userDepth' = userDepth
       ELSE
          FinishRequest(r)
    /\ UNCHANGED <<reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D2, _render_once: if element is not None: self._element_next = element.
RenderEntryWriteElement(r) ==
    /\ r \in Requesters
    /\ pc[r] = "render_entry_write_element"
    /\ elementNext' = IF reqKind[r] = "render" /\ renderFirstCall[r] THEN elementNext + 1 ELSE elementNext
    /\ pc' = [pc EXCEPT ![r] = "render_entry_read_mark"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, otherThreadMark, element, stateVer,
        forceVer, lastPassState, lastPassForce, lastPassElem, passAfterClose,
        teardownCount, tooMany, rendered, nestedCount, totalNestedCount,
        renderLimit, effectCloseRaised, effectSetCount, loopNeedsRender,
        loopOtherMark, cleanupCloseCalled>>

\* D2, _render_once: if self._rerender_needed is False.
RenderEntryReadMark(r) ==
    /\ r \in Requesters
    /\ pc[r] = "render_entry_read_mark"
    /\ markNeedsWrite' = [markNeedsWrite EXCEPT ![r] = ~rerenderNeeded]
    /\ pc' = [pc EXCEPT ![r] = "render_entry_write_mark"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        renderFirstCall, renderReadRendered, renderReadMark, renderReadRendering,
        lockOwner, lockThread, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D2, _render_once: self._rerender_needed = True.
RenderEntryWriteMark(r) ==
    /\ r \in Requesters
    /\ pc[r] = "render_entry_write_mark"
    /\ rerenderNeeded' = (rerenderNeeded \/ markNeedsWrite[r])
    /\ pc' = [pc EXCEPT ![r] = "render_entry_try_lock"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, otherThreadMark, elementNext, element, stateVer,
        forceVer, lastPassState, lastPassForce, lastPassElem, passAfterClose,
        teardownCount, tooMany, rendered, nestedCount, totalNestedCount,
        renderLimit, effectCloseRaised, effectSetCount, loopNeedsRender,
        loopOtherMark, cleanupCloseCalled>>

\* D2, _render_once: self.thread_lock.acquire(blocking=False).
RenderEntryTryLock(r) ==
    /\ r \in Requesters
    /\ pc[r] = "render_entry_try_lock"
    /\ IF lockOwner = NoThread
       THEN
          /\ lockOwner' = r
          /\ lockThread' = r
          /\ rendered' = [rendered EXCEPT ![r] = FALSE]
          /\ renderFirstCall' = [renderFirstCall EXCEPT ![r] = FALSE]
          /\ pc' = [pc EXCEPT ![r] = "pass_start_check"]
          /\ nestedCount' = 0
          /\ totalNestedCount' = 0
          /\ renderLimit' = OwnLimit
          /\ reqCount' = reqCount
          /\ userOwner' = userOwner
          /\ userDepth' = userDepth
       ELSE
          /\ ~MUT_BLOCKING_REQUEST
          /\ rendered' = [rendered EXCEPT ![r] = FALSE]
          /\ renderFirstCall' = [renderFirstCall EXCEPT ![r] = FALSE]
          /\ FinishRequest(r)
          /\ lockOwner' = lockOwner
          /\ lockThread' = lockThread
          /\ UNCHANGED <<nestedCount, totalNestedCount, renderLimit>>
    /\ UNCHANGED <<reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderReadRendered, renderReadMark, renderReadRendering,
        closing, closed, isRendering, rerenderNeeded, otherThreadMark,
        elementNext, element, stateVer, forceVer, lastPassState, lastPassForce,
        lastPassElem, passAfterClose, teardownCount, tooMany, effectCloseRaised,
        effectSetCount, loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D9, _render_once: if self._closing or self.context is None.
\* D4, _render_once: self._rerender_needed = False.
\* D7, _render_once: self._state_set_by_other_thread = False.
\* D4, _render_once: self.element = self._element_next.
PassStart(t) ==
    /\ t \in Requesters
    /\ \/ /\ pc[t] = "pass_start_check"
          /\ IF closing \/ closed
             THEN
                /\ pc' = [pc EXCEPT ![t] = "release"]
                /\ rendered' = [rendered EXCEPT ![t] = FALSE]
             ELSE
                /\ pc' = [pc EXCEPT ![t] = IF MUT_ELEMENT_BEFORE_CLEAR THEN "pass_start_take_elem" ELSE "pass_start_clear_mark"]
                /\ rendered' = rendered
          /\ UNCHANGED <<rerenderNeeded, otherThreadMark, element, isRendering>>
       \/ /\ pc[t] = "pass_start_clear_mark"
          /\ rerenderNeeded' = FALSE
          /\ pc' = [pc EXCEPT ![t] =
                IF nestedCount # 0 THEN (IF MUT_ELEMENT_BEFORE_CLEAR THEN "pass_start_set_rendering" ELSE "pass_start_take_elem")
                ELSE "pass_start_clear_other"]
          /\ UNCHANGED <<otherThreadMark, element, isRendering, rendered>>
       \/ /\ pc[t] = "pass_start_clear_other"
          /\ otherThreadMark' = FALSE
          /\ pc' = [pc EXCEPT ![t] = IF MUT_ELEMENT_BEFORE_CLEAR THEN "pass_start_set_rendering" ELSE "pass_start_take_elem"]
          /\ UNCHANGED <<rerenderNeeded, element, isRendering, rendered>>
       \/ /\ pc[t] = "pass_start_take_elem"
          /\ element' = elementNext
          /\ pc' = [pc EXCEPT ![t] = IF MUT_ELEMENT_BEFORE_CLEAR THEN "pass_start_clear_mark" ELSE "pass_start_set_rendering"]
          /\ UNCHANGED <<rerenderNeeded, otherThreadMark, isRendering, rendered>>
       \/ /\ pc[t] = "pass_start_set_rendering"
          /\ isRendering' = TRUE
          /\ rendered' = [rendered EXCEPT ![t] = TRUE]
          /\ pc' = [pc EXCEPT ![t] = "pass_render"]
          /\ UNCHANGED <<rerenderNeeded, otherThreadMark, element>>
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, elementNext, stateVer, forceVer, lastPassState, lastPassForce,
        lastPassElem, passAfterClose, teardownCount, tooMany, nestedCount,
        totalNestedCount, renderLimit, effectCloseRaised, effectSetCount,
        loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D1, _render: one pass reads state and root element.
\* D8, close: close() called during a render raises.
\* D7, set_: a setter on the holder's own thread marks without setting the other-thread mark.
PassRender(t) ==
    /\ t \in Requesters
    /\ pc[t] = "pass_render"
    /\ (EFFECT_TAKES_USER_LOCK => CanUseUser(t))
    /\ ~(EFFECT_CALLS_CLOSE /\ MUT_CLOSE_NO_OWN_CHECK)
    /\ lastPassState' = stateVer
    /\ lastPassForce' = forceVer
    /\ lastPassElem' = element
    /\ passAfterClose' = (passAfterClose \/ closing)
    /\ effectCloseRaised' = (effectCloseRaised \/ EFFECT_CALLS_CLOSE)
    /\ stateVer' = IF EFFECT_SETS_STATE /\ effectSetCount[t] < MaxRequests THEN stateVer + 1 ELSE stateVer
    /\ rerenderNeeded' = IF EFFECT_SETS_STATE /\ effectSetCount[t] < MaxRequests /\ ~rerenderNeeded THEN TRUE ELSE rerenderNeeded
    /\ effectSetCount' = IF EFFECT_SETS_STATE /\ effectSetCount[t] < MaxRequests THEN [effectSetCount EXCEPT ![t] = @ + 1] ELSE effectSetCount
    /\ pc' = [pc EXCEPT ![t] = "loop_read_rerender"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, otherThreadMark, elementNext, element, forceVer,
        teardownCount, tooMany, rendered, nestedCount, totalNestedCount,
        renderLimit, loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D7, _render_once: read _rerender_needed for the loop branch.
LoopReadRerender(t) ==
    /\ t \in Requesters
    /\ pc[t] = "loop_read_rerender"
    /\ loopNeedsRender' = rerenderNeeded
    /\ pc' = [pc EXCEPT ![t] = IF rerenderNeeded THEN "loop_read_other" ELSE "stop_rendering"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, otherThreadMark, elementNext, element,
        stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
        passAfterClose, teardownCount, tooMany, rendered, nestedCount,
        totalNestedCount, renderLimit, effectCloseRaised, effectSetCount,
        loopOtherMark, cleanupCloseCalled>>

\* D7, _render_once: read _state_set_by_other_thread.
LoopReadOther(t) ==
    /\ t \in Requesters
    /\ pc[t] = "loop_read_other"
    /\ loopOtherMark' = otherThreadMark
    /\ pc' = [pc EXCEPT ![t] = "loop_clear_other"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, otherThreadMark, elementNext, element,
        stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
        passAfterClose, teardownCount, tooMany, rendered, nestedCount,
        totalNestedCount, renderLimit, effectCloseRaised, effectSetCount,
        loopNeedsRender, cleanupCloseCalled>>

\* D7, _render_once: clear the other-thread mark and raise the limit only when it was TRUE.
LoopClearOther(t) ==
    /\ t \in Requesters
    /\ pc[t] = "loop_clear_other"
    /\ otherThreadMark' = IF loopOtherMark THEN FALSE ELSE otherThreadMark
    /\ renderLimit' = IF loopOtherMark THEN OtherLimit ELSE renderLimit
    /\ nestedCount' = IF loopOtherMark /\ MUT_LIMIT_RESET THEN 0 ELSE nestedCount
    /\ pc' = [pc EXCEPT ![t] = "loop_compare"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, elementNext, element, stateVer,
        forceVer, lastPassState, lastPassForce, lastPassElem, passAfterClose,
        teardownCount, tooMany, rendered, totalNestedCount, effectCloseRaised,
        effectSetCount, loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D7, _render_once: compare the count after the reads above.
LoopCompare(t) ==
    /\ t \in Requesters
    /\ pc[t] = "loop_compare"
    /\ IF nestedCount > renderLimit
       THEN
          /\ tooMany' = TRUE
          /\ rendered' = [rendered EXCEPT ![t] = FALSE]
          /\ pc' = [pc EXCEPT ![t] = "stop_rendering"]
          /\ nestedCount' = nestedCount
          /\ totalNestedCount' = totalNestedCount
       ELSE
          /\ pc' = [pc EXCEPT ![t] = IF MUT_ELEMENT_BEFORE_CLEAR THEN "pass_start_take_elem" ELSE "pass_start_clear_mark"]
          /\ nestedCount' = nestedCount + 1
          /\ totalNestedCount' = totalNestedCount + 1
          /\ tooMany' = tooMany
          /\ rendered' = rendered
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, otherThreadMark, elementNext, element,
        stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
        passAfterClose, teardownCount, renderLimit, effectCloseRaised,
        effectSetCount, loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D5, _render_once: self._is_rendering = False.
StopRendering(t) ==
    /\ t \in Requesters
    /\ pc[t] = "stop_rendering"
    /\ isRendering' = FALSE
    /\ pc' = [pc EXCEPT ![t] = IF MUT_READ_ERRORS_AFTER_RELEASE THEN "release" ELSE "read_errors"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, rerenderNeeded, otherThreadMark, elementNext, element, stateVer,
        forceVer, lastPassState, lastPassForce, lastPassElem, passAfterClose,
        teardownCount, tooMany, rendered, nestedCount, totalNestedCount,
        renderLimit, effectCloseRaised, effectSetCount, loopNeedsRender,
        loopOtherMark, cleanupCloseCalled>>

\* D1, _render_once: exceptions = self.context.exceptions_children before the outer finally releases the lock.
ReadErrors(t) ==
    /\ t \in Requesters
    /\ pc[t] = "read_errors"
    /\ pc' = [pc EXCEPT ![t] = IF MUT_READ_ERRORS_AFTER_RELEASE THEN "look_again" ELSE "release"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, otherThreadMark, elementNext, element,
        stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
        passAfterClose, teardownCount, tooMany, rendered, nestedCount,
        totalNestedCount, renderLimit, effectCloseRaised, effectSetCount,
        loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D5, _render_once: self.thread_lock.release().
Release(t) ==
    /\ t \in Requesters
    /\ pc[t] = "release"
    /\ lockOwner = t
    /\ lockOwner' = NoThread
    /\ lockThread' = NoThread
    /\ pc' = [pc EXCEPT ![t] = IF MUT_READ_ERRORS_AFTER_RELEASE /\ rendered[t] THEN "read_errors" ELSE "look_again"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D5, render: loop, not recursion.
LookAgain(t) ==
    /\ t \in Requesters
    /\ pc[t] = "look_again"
    /\ renderFirstCall' = [renderFirstCall EXCEPT ![t] = FALSE]
    /\ pc' = [pc EXCEPT ![t] = "render_loop_read_rendered"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderReadRendered, renderReadMark, renderReadRendering,
        lockOwner, lockThread, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D8, close: own render check.
CloseOwnCheck(c) ==
    /\ c \in Closers
    /\ pc[c] = "close_start"
    /\ (CLOSER_HOLDS_USER_LOCK => CanUseUser(c))
    /\ pc' = [pc EXCEPT ![c] = "close_closing_check"]
    /\ userOwner' = IF CLOSER_HOLDS_USER_LOCK /\ userOwner = NoThread THEN c ELSE userOwner
    /\ userDepth' = IF CLOSER_HOLDS_USER_LOCK THEN IF userOwner = c THEN userDepth + 1 ELSE IF userOwner = NoThread THEN 1 ELSE userDepth ELSE userDepth
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D8, close: if self._closing: return.
CloseClosingCheck(c) ==
    /\ c \in Closers
    /\ pc[c] = "close_closing_check"
    /\ IF closing /\ ~MUT_CLOSE_NO_CLOSING_CHECK
       THEN
          /\ pc' = [pc EXCEPT ![c] = "done"]
          /\ userOwner' = ReleaseUserOwner(c)
          /\ userDepth' = ReleaseUserDepth(c)
       ELSE
          /\ pc' = [pc EXCEPT ![c] = "close_acquire"]
          /\ userOwner' = userOwner
          /\ userDepth' = userDepth
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D8, close: with self.thread_lock.
CloseAcquire(c) ==
    /\ c \in Closers
    /\ pc[c] = "close_acquire"
    /\ lockOwner = NoThread
    /\ lockOwner' = c
    /\ lockThread' = NoThread
    /\ pc' = [pc EXCEPT ![c] = "close_recheck"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, userOwner, userDepth, closing, closed, isRendering,
        rerenderNeeded, otherThreadMark, elementNext, element, stateVer, forceVer,
        lastPassState, lastPassForce, lastPassElem, passAfterClose, teardownCount,
        tooMany, rendered, nestedCount, totalNestedCount, renderLimit,
        effectCloseRaised, effectSetCount, loopNeedsRender, loopOtherMark,
        cleanupCloseCalled>>

\* D8, close: if self._closing: return.
\* D8, close: self._closing = True.
CloseRecheck(c) ==
    /\ c \in Closers
    /\ pc[c] = "close_recheck"
    /\ IF closing /\ ~MUT_CLOSE_NO_RECHECK
       THEN
          /\ pc' = [pc EXCEPT ![c] = "done"]
          /\ lockOwner' = NoThread
          /\ lockThread' = NoThread
          /\ userOwner' = ReleaseUserOwner(c)
          /\ userDepth' = ReleaseUserDepth(c)
          /\ closing' = closing
       ELSE
          /\ pc' = [pc EXCEPT ![c] = "close_teardown"]
          /\ lockOwner' = lockOwner
          /\ lockThread' = lockThread
          /\ userOwner' = userOwner
          /\ userDepth' = userDepth
          /\ closing' = TRUE
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, closed, isRendering, rerenderNeeded, otherThreadMark,
        elementNext, element, stateVer, forceVer, lastPassState, lastPassForce,
        lastPassElem, passAfterClose, teardownCount, tooMany, rendered,
        nestedCount, totalNestedCount, renderLimit, effectCloseRaised,
        effectSetCount, loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D8, close: an effect cleanup can call close() during close().
CloseTeardown(c) ==
    /\ c \in Closers
    /\ pc[c] = "close_teardown"
    /\ IF CLEANUP_CALLS_CLOSE /\ ~cleanupCloseCalled
       THEN
          /\ cleanupCloseCalled' = TRUE
          /\ pc' = [pc EXCEPT ![c] = "cleanup_close_closing_check"]
       ELSE
          /\ cleanupCloseCalled' = cleanupCloseCalled
          /\ pc' = [pc EXCEPT ![c] = "close_teardown_finish"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, otherThreadMark, elementNext, element,
        stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
        passAfterClose, teardownCount, tooMany, rendered, nestedCount,
        totalNestedCount, renderLimit, effectCloseRaised, effectSetCount,
        loopNeedsRender, loopOtherMark>>

\* D8, close: nested close() returns at if self._closing.
CleanupCloseClosingCheck(c) ==
    /\ c \in Closers
    /\ pc[c] = "cleanup_close_closing_check"
    /\ IF closing /\ ~MUT_CLOSE_NO_CLOSING_CHECK
       THEN pc' = [pc EXCEPT ![c] = "close_teardown_finish"]
       ELSE pc' = [pc EXCEPT ![c] = "cleanup_close_acquire"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockOwner, lockThread, userOwner, userDepth, closing,
        closed, isRendering, rerenderNeeded, otherThreadMark, elementNext, element,
        stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
        passAfterClose, teardownCount, tooMany, rendered, nestedCount,
        totalNestedCount, renderLimit, effectCloseRaised, effectSetCount,
        loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D8, close: without the closing check, the nested close waits for the lock its own thread holds.
CleanupCloseAcquire(c) ==
    /\ c \in Closers
    /\ pc[c] = "cleanup_close_acquire"
    /\ lockOwner = NoThread
    /\ lockOwner' = c
    /\ pc' = [pc EXCEPT ![c] = "close_recheck"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, lockThread, userOwner, userDepth, closing, closed,
        isRendering, rerenderNeeded, otherThreadMark, elementNext, element,
        stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
        passAfterClose, teardownCount, tooMany, rendered, nestedCount,
        totalNestedCount, renderLimit, effectCloseRaised, effectSetCount,
        loopNeedsRender, loopOtherMark, cleanupCloseCalled>>

\* D8, close: remove tree and clear context.
CloseTeardownFinish(c) ==
    /\ c \in Closers
    /\ pc[c] = "close_teardown_finish"
    /\ teardownCount' = teardownCount + 1
    /\ closed' = TRUE
    /\ element' = 0
    /\ elementNext' = 0
    /\ lockOwner' = NoThread
    /\ lockThread' = NoThread
    /\ userOwner' = ReleaseUserOwner(c)
    /\ userDepth' = ReleaseUserDepth(c)
    /\ pc' = [pc EXCEPT ![c] = "done"]
    /\ UNCHANGED <<reqCount, reqKind, reqHoldsUser, checkedRendering, markLockOther,
        markNeedsWrite, renderFirstCall, renderReadRendered, renderReadMark,
        renderReadRendering, closing, isRendering, rerenderNeeded, otherThreadMark,
        stateVer, forceVer, lastPassState, lastPassForce, lastPassElem,
        passAfterClose, tooMany, rendered, nestedCount, totalNestedCount,
        renderLimit, effectCloseRaised, effectSetCount, loopNeedsRender,
        loopOtherMark, cleanupCloseCalled>>

Next ==
    \/ \E r \in Requesters: ReqStart(r)
    \/ \E r \in Requesters: ReqClosingCheck(r)
    \/ \E r \in Requesters: ReqWrite(r)
    \/ \E r \in Requesters: ReqUpdateForceClosingCheck(r)
    \/ \E r \in Requesters: ReqCheckRenderingBeforeMark(r)
    \/ \E r \in Requesters: ReqMarkReadLockThread(r)
    \/ \E r \in Requesters: ReqMarkWriteOther(r)
    \/ \E r \in Requesters: ReqMarkReadRerender(r)
    \/ \E r \in Requesters: ReqMarkWriteRerender(r)
    \/ \E r \in Requesters: ReqCheckRendering(r)
    \/ \E r \in Requesters: RenderLoopReadRendered(r)
    \/ \E r \in Requesters: RenderLoopReadMark(r)
    \/ \E r \in Requesters: RenderLoopReadIsRendering(r)
    \/ \E r \in Requesters: RenderLoopDecide(r)
    \/ \E r \in Requesters: RenderEntryWriteElement(r)
    \/ \E r \in Requesters: RenderEntryReadMark(r)
    \/ \E r \in Requesters: RenderEntryWriteMark(r)
    \/ \E r \in Requesters: RenderEntryTryLock(r)
    \/ \E r \in Requesters: PassStart(r)
    \/ \E r \in Requesters: PassRender(r)
    \/ \E r \in Requesters: LoopReadRerender(r)
    \/ \E r \in Requesters: LoopReadOther(r)
    \/ \E r \in Requesters: LoopClearOther(r)
    \/ \E r \in Requesters: LoopCompare(r)
    \/ \E r \in Requesters: StopRendering(r)
    \/ \E r \in Requesters: ReadErrors(r)
    \/ \E r \in Requesters: Release(r)
    \/ \E r \in Requesters: LookAgain(r)
    \/ \E c \in Closers: CloseOwnCheck(c)
    \/ \E c \in Closers: CloseClosingCheck(c)
    \/ \E c \in Closers: CloseAcquire(c)
    \/ \E c \in Closers: CloseRecheck(c)
    \/ \E c \in Closers: CloseTeardown(c)
    \/ \E c \in Closers: CleanupCloseClosingCheck(c)
    \/ \E c \in Closers: CleanupCloseAcquire(c)
    \/ \E c \in Closers: CloseTeardownFinish(c)

DoneStutter == AllDone /\ UNCHANGED vars
Spec == Init /\ [][Next \/ DoneStutter]_vars

\* NoDeadlock is TLC's deadlock check (on by default): only DoneStutter may repeat a state.

NoLostRequest ==
    AllDone /\ ~closed /\ ~closing /\ ~tooMany =>
        /\ lastPassState = stateVer
        /\ lastPassForce = forceVer
        /\ lastPassElem = elementNext
        /\ rerenderNeeded = FALSE
        /\ lockOwner = NoThread
        /\ (EFFECT_CALLS_CLOSE => effectCloseRaised)

NoPassAfterClose == ~passAfterClose
BoundedPasses == totalNestedCount <= renderLimit + 1
TeardownOnce == teardownCount <= 1
ErrorsReadUnderLock == \A r \in Requesters: pc[r] = "read_errors" => lockOwner = r /\ ~closing /\ ~closed
NoTooMany == ~tooMany

=============================================================================
