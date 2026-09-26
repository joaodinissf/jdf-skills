# Useful modelling boundaries

Start with the question the model should answer. These boundaries are useful
for both proposed designs and existing systems. The failure cases suggest
behaviours to include; they are not claims that a defect must exist. Use the fix
shapes only after a property and its violation are established.

## Failure classes at a glance

| Class | Typical shape | Section |
|---|---|---|
| Check-then-act, lost update | read, decide, write back without rechecking | Durable state machines; Threads |
| Async interleaving | a fact checked before an `await` and used after it | Single-threaded async |
| Retries and idempotency | a redelivered request or a retry repeats an effect | Two systems that must agree; Processes |
| Leases and fencing | a paused holder acts after its lease was reclaimed | Durable state machines |
| Deadlock and lost wakeup | opposite lock orders; a notify nobody is waiting for | Threads |
| Data-flow loss, duplication or stall | the last partial batch never flushed | Pipelines and streams |
| Illegal state transition | `paid → cancelled` from a read-decide-write handler | Durable state machines |
| Dependency scheduling | a task dispatched before its dependencies finish | Schedulers and dependency graphs |
| Divergent views | two folds, two tabs or an index disagreeing with the source | Event logs; User interfaces |

## Surveying a codebase

For a broad request such as "find bugs in this codebase", the model is not the
first step. Survey the code for shared mutable state and the places it is
changed: locks, `async` functions, threads and channels, queues, caches,
retries, timers, transactions, status columns, webhook and message handlers,
schedulers. Rank candidate boundaries by consequence (money, data loss, stuck
work) and by how much interleaving or partial failure they admit. Propose the
top few, each with a one-line risk, and let the user choose; if told to
proceed, take the highest-ranked.

Model each chosen boundary independently, with its own directory, properties
and checks. Separate boundaries can be modelled in parallel, for example by
subagents, when the environment and the user allow it; merge their findings
only after each has been classified. Report the boundaries surveyed but not
modelled, so silence is not read as a clean result.

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
  nothing enforcing it. Model expiry as an action that can happen at any
  moment, including while the holder is paused; the classic failure is a stale
  holder committing after another claimed the work.
- A transition decided from a status read earlier (`if status == pending:
  … status = cancelled`) while another handler moves the same record.
- A claim or conditional update whose atomicity depends on the isolation level.
  Under read committed, `UPDATE … WHERE id = (SELECT … LIMIT 1)` can let two
  workers take the same row; model the statements separately or state the
  isolation assumption.
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
- A lost wakeup: a notify sent before the waiter waits, or a wait not
  re-checking its condition in a loop after waking.
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

## Pipelines and streams

Is every item delivered exactly once, in order where order matters, and does
the pipeline always drain?

A producer, a bounded queue or channel, batching or windowing stages, a sink.

- The last partial batch never flushed at end of stream. This violates no
  safety property — nothing wrong is ever emitted — so only a liveness property
  such as "every accepted item is eventually delivered" catches it. Pair each
  "nothing bad" property with a "something good eventually".
- Items lost or duplicated where a stage retries, fans out or restarts.
- Unbounded buffering where backpressure was assumed.
- A consumer that stops on one poison item and stalls everything behind it.

Useful properties: the output is a prefix of the input (safety), the output
eventually equals the input (liveness), the output is a permutation of the
input (after fan-out and fan-in).

## Schedulers and dependency graphs

Does each task run only after its dependencies, exactly once, and does the
schedule always finish?

Build systems, workflow engines, job DAGs, garbage collectors' mark phases.

- Readiness computed from dependencies *started* rather than *finished*.
- A task run twice after a worker failure and retry.
- A scheduler stuck because a failed task's dependants wait forever.
- A cycle check racing an edge insertion.

Check every small graph in one run: let the initial state choose any edge set on
three or four nodes, restricted to acyclic ones where the property needs it,
instead of hand-picking a graph. For a property of all graphs, prove it in Lean;
the safety of dependency-respecting dispatch typically needs no acyclicity,
while progress does.

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
| a fencing token checked by the store on every write | a stale lease holder cannot commit |
| wait in a loop on the condition, notify under the same lock | no lost wakeup |
| flush on end of stream and on shutdown | no lost tail |
| readiness from finished dependencies only | no premature dispatch |
