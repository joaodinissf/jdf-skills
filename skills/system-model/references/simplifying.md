# Simplifying code from checked properties

A checked model says what is always true of the modelled system. Code written
without that knowledge often defends against states that cannot occur: a guard
that never fails, a lock that no other party takes, a flag that duplicates other
state. This reference covers removing such code, and only on evidence.

Start from a model that has already been validated: its reachability and
expected-failure checks behave as recorded, and its properties are fixed and
sourced. Without that, nothing justifies a deletion.

## Candidates

| Candidate | Signal in the model | Evidence to produce |
|---|---|---|
| A guard implied by an invariant | removing the guard's conjunct from the action changes nothing reachable | the invariant implies the guard wherever the action is otherwise enabled |
| A lock or transaction that protects nothing | the other parties never take it, or every property holds without it | a recheck of every property with it removed |
| A dead branch or unreachable state | TLC coverage shows the action never fires; the Lean search never reaches it | unreachability, plus a companion showing it *is* reached when the upstream guard is weakened |
| A retry, timeout or recovery path that never triggers | its trigger cannot arise under the modelled failures | a recheck of safety **and** progress without it; retries usually exist for progress |
| A redundant flag | an invariant shows it always equals a function of other state | the invariant, then a recheck with the flag derived |

The companion for a dead branch matters: without it, the branch may look dead
only because the model cannot reach anything nearby.

## Strength of the justification

From cheapest to strongest; state which one was used.

1. **Recheck.** Apply the simplification to the model and rerun every property
   and every expected-failure companion at the same or larger bounds. Holds only
   for the checked instance.
2. **Implied guard.** Check `Enabled_without_guard => Guard` as an invariant in
   TLC, or prove it from the inductive invariant in Lean.
3. **Same reachable states.** In Lean, prove that the model with and without the
   guard reach exactly the same states: one direction because the guarded step
   is a special case, the other by induction using the implied-guard lemma. Every
   state property then carries over.
4. **Refinement.** Show that every behaviour of the simplified model is a
   behaviour of the current one, with a mapping that reconstructs removed
   variables (in TLA+, `INSTANCE … WITH` checked as a property). This carries over
   safety, not progress; recheck liveness separately.

A bounded result does not justify a deletion that could matter only at larger
sizes. Either argue why the bound covers it, prove it in Lean, or recheck at
larger bounds.

## Assumptions decide the change

List the assumptions the justification relies on, then choose:

- **Remove** when every assumption is enforced by something the team controls: a
  type, a database constraint, a single-writer design.
- **Downgrade to an assertion, metric or log** when the proof holds but an
  assumption is only a convention. The next person to break it gets a signal.
- **Keep** when the code sits on a trust boundary (network or user input, disk,
  another team's service, a mixed-version deployment), or when an unmodelled
  caller may rely on it. Search for every other acquirer of a lock and every
  other writer of a field before calling them absent. Internal invariants never
  justify removing validation of external input.

## Applying it

A simplification is a code change: make it only when the user asked for one.
Apply one at a time; two individually safe deletions can be jointly unsafe. For
each, change the code and the model together, update the source mapping, rerun
the model checks and the repository's tests, and record the property that
justified it. Report rejected candidates with the reason, such as "the lock
looks redundant but also protects the nightly job, which is not modelled".
