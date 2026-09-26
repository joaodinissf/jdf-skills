# TLA+ reference

For targets where several actors interleave. TLC, the model checker in
`tla2tools.jar`, explores every reachable state of a small instance and prints
a trace to a state that breaks an invariant (a shortest trace with the default
breadth-first search). Bounds apply to the model, not the whole system.

## Contents

- A model to copy
- Configurations: every result with a check that can fail
- Running TLC and reading its output
- Replaying real traces
- Liveness
- When the state space explodes
- PlusCal
- Pitfalls

## A model to copy

This worked example compares two ways for workers to claim one job: a separate
read and unconditional write, and a conditional write that rechecks the status.
It can represent a design alternative or a reproduced implementation fix.
The source locations below are illustrative; replace them with actual source
mappings, or requirement identifiers for a design model. The `Fixed` parameter
belongs to this comparison, not to every model.

```tla
---- MODULE Claim ----
EXTENDS Naturals, FiniteSets

CONSTANTS Workers,  \* a set of model values, e.g. {w1, w2}
          Fixed     \* TRUE models the fixed code, FALSE the code before the fix

VARIABLES status, pc, sends
vars == <<status, pc, sends>>

Init == /\ status = "pending"
        /\ pc = [w \in Workers |-> "idle"]
        /\ sends = 0

\* worker.ts:41 — reads the status, then awaits the lease service
Read(w) == /\ pc[w] = "idle"
           /\ status = "pending"
           /\ pc' = [pc EXCEPT ![w] = "read"]
           /\ UNCHANGED <<status, sends>>

\* worker.ts:47 — writes after the await; the fix makes it compare-and-set
Claim(w) == /\ pc[w] = "read"
            /\ Fixed => status = "pending"
            /\ status' = "claimed"
            /\ pc' = [pc EXCEPT ![w] = "claimed"]
            /\ UNCHANGED sends

\* worker.ts:49 — the fixed write lost the race; the worker gives up
GiveUp(w) == /\ pc[w] = "read"
             /\ Fixed /\ status /= "pending"
             /\ pc' = [pc EXCEPT ![w] = "done"]
             /\ UNCHANGED <<status, sends>>

\* worker.ts:52 — the side effect
Send(w) == /\ pc[w] = "claimed"
           /\ sends' = sends + 1
           /\ pc' = [pc EXCEPT ![w] = "done"]
           /\ UNCHANGED status

\* the job is taken and nobody is between reading and finishing
Terminated == /\ status = "claimed"
              /\ \A w \in Workers : pc[w] \in {"idle", "done"}

Next == \/ \E w \in Workers : Read(w) \/ Claim(w) \/ GiveUp(w) \/ Send(w)
        \/ Terminated /\ UNCHANGED vars   \* a finished system may stutter

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

TypeOK == /\ status \in {"pending", "claimed"}
          /\ pc \in [Workers -> {"idle", "read", "claimed", "done"}]
          /\ sends \in 0..Cardinality(Workers)

AtMostOneSend == sends <= 1                       \* intent: design/jobs.md
EventuallyDone == <>Terminated

\* Reachability, expected to be violated: some worker does send.
NeverSends == sends = 0
====
```

Why the `Terminated` disjunct: without it, a finished system has no next state
and TLC reports a deadlock. Allowing stutter *only* once the system is finished
keeps deadlock checking on, so a genuinely stuck state is still reported.
Prefer this to `CHECK_DEADLOCK FALSE`, which hides stuck states too.

## Configurations: every result with a check that can fail

A passing configuration is evidence only if the same model can fail. Give each
headline result an expected-failure companion, and keep both in `specs/checks`
so a later edit that blinds the model shows up as a mismatch:

| Companion | Shows | Expected result |
|---|---|---|
| Reachability | the states the property talks about occur at all | `fail:<ReachabilityInvariant>` |
| Before/after | the property detects the defect the fix removes | `fail:<Property>` with the fix off |
| Planted weakening | the property detects a plausible defect in a clean system or a design | `fail:<Property>` with one guard weakened |

Use before/after only when there is a real before: a reproduced defect, or two
design alternatives. For a clean implementation or a single design, plant a
weakening in a separate configuration or parameter, and label it planted; it
tests the check, not the system. Every model needs at least the reachability
companion. Name the expected violation (`fail:AtMostOneSend`), not just `fail`:
a companion that fails for another reason does not test what it claims.

For the worked example:

`Claim.cfg` — the fixed code; expected to pass:

```
SPECIFICATION Spec
CONSTANTS
    Workers = {w1, w2}
    Fixed = TRUE
INVARIANT TypeOK
INVARIANT AtMostOneSend
PROPERTY EventuallyDone
```

`ClaimBefore.cfg` — the same with `Fixed = FALSE`; expected
`fail:AtMostOneSend`. `ClaimReach.cfg` — `Fixed = TRUE` with only
`INVARIANT NeverSends`; expected `fail:NeverSends`. If TLC reports
`NeverSends` as holding, the model never reaches the interesting states.

Also run the passing configuration once with `-coverage 1`. Each action is
listed with the `distinct:total` states it produced; an action at `0:0` never
fired, so its guard is contradictory or unreachable at these bounds. A
stuttering disjunct such as `Terminated` legitimately adds no distinct states.

## Running TLC and reading its output

Find an installed `tla2tools.jar` first. `TLA2TOOLS` may be set only in the
user's interactive shell, so an agent's shell can see it unset. Copies usually
live under `~/.local/share/*/` or `~/.local/share/*/*/` (for example
`tlaplus/<version>/`), `~/.cache/`, the TLA+ Toolbox app bundle, a TLA+ editor
extension's `tools/` directory, or a project's own tool directory. A single
`fd -H -I -g tla2tools.jar ~` finds any of them in seconds. If there is none and
the user authorizes an install, a pinned release of `tla2tools.jar` from the
`tlaplus/tlaplus` GitHub releases, placed in `~/.local/share/tla/` (the check
script's default), needs no administrator rights; it needs Java 11 or later.
Homebrew has no TLC formula, only the `tla+-toolbox` IDE cask, whose bundled
jar can lag the current release.

```bash
cd specs/Claim
java -XX:+UseParallelGC -cp "$TLA2TOOLS" tlc2.TLC \
  -workers auto -cleanup -metadir "${TMPDIR:-/tmp}/tlc-Claim" \
  -config Claim.cfg Claim.tla
```

Run from the model's directory so `EXTENDS` finds sibling modules. Read the
output; the exit code varies between releases.

| Output contains | Meaning |
|---|---|
| `No error has been found` | clean at this size |
| `Invariant <Name> is violated` | safety counterexample; the trace follows |
| `Action property <Name> … is violated` | an action property failed |
| `Deadlock reached` | a stuck state; the trace follows |
| `Temporal properties were violated` | liveness counterexample (a lasso: a prefix, then a loop) |
| `Parse Error`, `Semantic error`, anything else | the model is broken — not a finding |

Report the `distinct states found` figure with every result; it is the size of
the evidence.

## Replaying real traces

Use this for observations from an implementation. For a design with no code,
exercise requirement scenarios instead and label them constructed. Neither a
few accepted traces nor hand-written scenarios establish equivalence to an
implementation.

A trace is a list of observed states, one per modelled transition, logged from
a test or a real run. The replay spec walks the model along the trace; if the
model cannot take a step the trace took, TLC stops with `Deadlock reached`, and
the variables `t` and `i` in the error state name the trace and the step.

```tla
---- MODULE ClaimTraces ----
EXTENDS Claim, Sequences, Naturals, TLC
CONSTANTS w1, w2          \* the actor names the traces use; assigned in the cfg

VARIABLES t, i

Traces == <<
  << [status |-> "pending", pc |-> (w1 :> "idle" @@ w2 :> "idle"), sends |-> 0],
     [status |-> "pending", pc |-> (w1 :> "read" @@ w2 :> "idle"), sends |-> 0],
     [status |-> "claimed", pc |-> (w1 :> "claimed" @@ w2 :> "idle"), sends |-> 0] >>
>>

Is(st) == /\ status = st.status /\ pc = st.pc /\ sends = st.sends
Was(st) == /\ status' = st.status /\ pc' = st.pc /\ sends' = st.sends

TraceInit == /\ t \in 1..Len(Traces) /\ i = 1
             /\ Init /\ Is(Traces[t][1])

TraceNext == \/ /\ i < Len(Traces[t])
                /\ Next /\ Was(Traces[t][i + 1])
                /\ i' = i + 1 /\ t' = t
             \/ /\ i = Len(Traces[t])
                /\ UNCHANGED <<status, pc, sends, t, i>>
====
```

`:>` and `@@` build a function from pairs; they come from the `TLC` module.
The trace config:

```
INIT TraceInit
NEXT TraceNext
CONSTANTS
    w1 = w1
    w2 = w2
    Workers = {w1, w2}
    Fixed = TRUE
```

`w1 = w1` makes each name a model value the traces can refer to. Keep deadlock
checking on: it is what reports a trace the model cannot follow.

Pin every variable in every trace state. A variable the trace leaves free lets
TLC choose a branch the code did not take and report a replay that never
happened. For long logs, generate the `Traces` definition from the log with a
small script rather than by hand.

When full states cannot be logged:

- **Partial states.** Constrain only the logged variables. Acceptance then
  means *some* values of the unlogged variables are consistent with the log;
  report it with that weaker wording.
- **Unlogged actions.** Allow at most a stated number of model steps between two
  logged ones, and report the bound. An unbounded gap accepts almost any trace.
- **Several threads or processes.** Order events at the point each takes
  effect: a global sequence number from an atomic counter within one process,
  or logical clocks merged in causal order across processes. Wall-clock
  timestamps from different machines do not give an order.

The reverse direction is also useful: generate behaviours from the model with
`-simulate` and replay them against the implementation as tests.

## Liveness

Safety says nothing bad happens; liveness says something good eventually does.
Liveness usually needs scheduling or environment assumptions to rule out
behaviours that make progress impossible. `WF_vars(A)` says: if `A` stays
enabled, it eventually happens. State which actions the scheduler must serve;
fairness of the whole `Next` does not generally prevent starvation of one actor.
The finite example above only needs some non-stuttering progress to terminate.

Environment assumptions such as eventual delivery can be legitimate contractual
conditions, but must be explicit and justified. Also check what remains true
without them. Do not add fairness to failure actions in an attempt to make
failures stop; model recovery assumptions directly.

A liveness counterexample is a lasso: states that lead into a loop the system
can repeat forever. Explain the loop in the report; it is usually a retry that
never gives up or two actors undoing each other.

## When the state space explodes

In order of preference:

1. Shrink the constants while preserving the behaviour in question. Small
   instances are a starting point, not a completeness guarantee.
2. Define a bound such as `WithinBound == sends <= 2` in the module and use
   `CONSTRAINT WithinBound` in the configuration. This truncates exploration;
   report it and do not infer unbounded safety or progress from that run.
3. Declare actors symmetric (`SYMMETRY Perms` with
   `Perms == Permutations(Workers)`, from the `TLC` module). Not sound with
   liveness properties — use it only for safety runs.
4. Simulate instead of exhausting: `-simulate num=100000 -depth 100`. Report
   it as *N random behaviours, not exhaustive*.

## PlusCal

When each actor is a sequential procedure with many waiting points, PlusCal —
an algorithm language that translates to TLA+ — is often easier to keep
faithful: each label is one atomic step. Match labels to the subject's actual atomicity;
code between two `await`s is atomic only relative to other tasks on that same
cooperative loop, not to external processes or stores. Write the algorithm in a comment block in the `.tla`
file and translate it with:

```bash
java -cp "$TLA2TOOLS" pcal.trans Claim.tla
```

Check the translation into version control with the source; the checks run
against it.

## Pitfalls

- Parenthesise inside action properties: `[][(a) => (b)]_vars`.
- A name assigned in the `.cfg` that the module never declares becomes a model
  value silently — a typo there changes the model instead of failing.
- Declare a `CONSTANT` before any definition uses it.
- Do not pass `-deadlock`; it disables deadlock checking, which the replays and
  the `Terminated` idiom rely on.
- `[f EXCEPT ![k] = v]` for functions and records; forgetting the `'` on a
  variable in an action leaves it unconstrained, and TLC tries every value.
- Keep `-metadir` outside the repository; TLC writes large state files there.
