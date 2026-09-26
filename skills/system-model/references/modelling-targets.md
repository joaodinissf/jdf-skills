# Useful modelling boundaries

Start with the question the model should answer. These boundaries are useful
for both proposed designs and existing systems. The failure cases suggest
behaviours to include; they are not claims that a defect must exist. Use the fix
shapes only after a property and its violation are established.

## Durable state machines

Which transitions are legal, who owns a claim, and what permits recovery?

A status column, a claim, a lease, a `locked_until`, a `next_attempt`, a
sweeper, a reaper, a reconciler.

- An unguarded write (`UPDATE … WHERE id = ?`) beside a guarded claim.
- *List, then act*: a loop that writes from a snapshot another actor has since
  changed.
- A side effect performed before the status write that retires it — a crash in
  between repeats the side effect on restart.
- A lease whose correctness depends on timing (`work time < lease time`) with
  nothing enforcing it.
- An error ignored on a status write, so the state and the world disagree.
- A fan-out saved one row per statement instead of in one transaction.

## Two systems that must agree

What does each side know after a partial failure, and how is agreement restored?

A database and a queue, an event log and a workflow engine, a local record and a
remote API. Each side may be locally correct while their interaction violates the contract.

- **The lost response.** The remote acted, the reply never arrived, and the
  caller records a failure — then retries or lets someone start again. Model the
  response as a separate, losable step.
- **A retry with a new identity.** An idempotency key regenerated per attempt,
  or scoped so a legitimate fresh attempt reuses an old one.
- **A crash between write A and write B**, with no outbox and no reconcile to
  finish the job.
- **Reconcile racing a fresh action** — the reconciler reads, a new attempt
  starts, the reconciler writes its stale conclusion.
- **A search index treated as the source of truth**: a secondary index that can
  lag, lose data or be rebuilt, consulted for decisions the primary store should
  make.

Fixes: persist intent before calling out; resolve uncertainty by asking the
remote (reconcile with the same key) rather than guessing; one idempotency key
per logical attempt; an outbox or a reconciler for the second write.

## Event logs folded into state

Which facts determine state, and what changes under duplication or reordering?

- *Latest* decided by arrival order where it should be by version or sequence.
- A duplicate event applied twice by a fold that is not idempotent.
- A later event that should supersede an earlier one but is not consulted
  (*launch-authorized* read without the *launch-failed* after it).
- Two folds of the same log — server and client — that disagree.
- Sequence or epoch numbers reused after a restart.

## Single-threaded async (JavaScript, TypeScript, Python)

Which facts can change across suspension points or in another process?

- State checked before an `await` and acted on after it.
- A queue, map or lock that serialises work *within one process*, relied on as
  if it covered every replica.
- A promise never awaited: its error and its ordering are both lost.
- Cancel or abort paths that skip the transition to a terminal state.
- Retry loops whose guards reset each other, so the loop never ends.
- Async generators: `return()` before the first `next()`, or a consumer that
  breaks out mid-flush.

## Threads (Go, Java, .NET and kin)

Which operations are atomic, and what ordering prevents interference or deadlock?

- Check-then-act across a lock release; read under a read lock, write under the
  write lock without checking again.
- Check-then-act on a concurrent map (`containsKey` then `put`) where an atomic
  `compute`, `putIfAbsent` or `LoadOrStore` exists.
- Two locks taken in different orders; a callback or channel send while holding
  a lock.
- Close or release not in a `finally`/`defer`; a channel closed twice.
- Sync-over-async (`.Result`, `.Wait()`) and fire-and-forget tasks.
- An atomic load followed by an atomic store where a compare-and-swap is needed.

## Processes talking to each other

Which messages establish durable facts, and which assumptions permit progress?

- An acknowledgement sent before the thing acknowledged is durable.
- At-least-once delivery into a handler that is not idempotent.
- Liveness signals (heartbeats) mistaken for correctness signals, or a missing
  heartbeat treated as proof of failure.
- A fail-closed path with no way out: a claim that stays pending forever after
  one lost write.

## User interfaces

Which user and server events may interleave, and which actions should remain available?

A UI is a state machine too, driven by the user and by the server at once.

- A button's mode derived from a local flag that a server event should have
  cleared — the page offers an action the server will refuse.
- An optimistic update never reconciled with the server's answer.
- A poll that overwrites a newer local change with an older server snapshot.
- Two tabs, or a tab and a background job, acting on the same record.

## Fix shapes

These are hypotheses to check, not automatic repairs. For example, retiring a
record before an external side effect can prevent duplicates but lose the effect
on a crash; a durable intent plus idempotency and recovery may be needed to
satisfy both safety and progress.

| Shape | Restores |
|---|---|
| compare-and-set on the status the writer read | no lost update, at most one claimant |
| one transaction for the whole change | no half-done state |
| durable intent, stable idempotency identity and recovery | retry without losing or duplicating the external effect, under the stated remote contract |
| the same idempotency key on every retry of one attempt | at most one remote execution |
| reconcile by asking the remote, never by assuming | agreement after a lost response |
| one lock order; no callback under a lock | no deadlock |
| version or sequence comparison instead of arrival order | a newer fact is never overwritten |
| an explicit escape from every pending state | nothing stuck forever |
