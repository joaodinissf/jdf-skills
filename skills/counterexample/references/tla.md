# TLA+ reference

For targets where several actors interleave. TLC, the model checker in
`tla2tools.jar`, explores every reachable state of a small instance and prints
the shortest path to any state that breaks an invariant.

## Contents

- A model to copy
- Configurations: after, before, sanity
- Running TLC and reading its output
- Replaying real traces
- Liveness
- When the state space explodes
- PlusCal
- Pitfalls

## A model to copy

Two workers claim one job. The code reads the status, awaits something, then
writes; the fix makes the write conditional on the status it read.

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
EventuallyDone == <>(\A w \in Workers : pc[w] /= "read" /\ pc[w] /= "claimed")
====
```

Why the `Terminated` disjunct: without it, a finished system has no next state
and TLC reports a deadlock. Allowing stutter *only* once the system is finished
keeps deadlock checking on, so a genuinely stuck state is still reported.
Prefer this to `CHECK_DEADLOCK FALSE`, which hides stuck states too.

## Configurations: after, before, sanity

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

`ClaimBefore.cfg` — the same with `Fixed = FALSE`; expected to fail on
`AtMostOneSend`. Keep it: it proves the model can see the bug the fix removes.

The reachability check from stage 5 is a temporary invariant that must be
violated, for example `NeverSends == sends = 0` added to a scratch config. If
TLC reports it as holding, the model never reaches the interesting states.

## Running TLC and reading its output

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

## Liveness

Safety says nothing bad happens; liveness says something good eventually does.
Liveness needs fairness, or TLC will find the trivial counterexample where the
system simply stops. `WF_vars(A)` says: if `A` stays enabled, it eventually
happens. Put fairness only on actions the real system is obliged to take —
a retry loop, a reconciler — never on the environment (crashes, lost
responses), or the model assumes the failures politely stop.

A liveness counterexample is a lasso: states that lead into a loop the system
can repeat forever. Explain the loop in the report; it is usually a retry that
never gives up or two actors undoing each other.

## When the state space explodes

In order of preference:

1. Shrink the constants. Two actors and one item find most bugs.
2. Bound counters with a `CONSTRAINT` (`CONSTRAINT sends <= 2`).
3. Declare actors symmetric (`SYMMETRY Perms` with
   `Perms == Permutations(Workers)`, from the `TLC` module). Not sound with
   liveness properties — use it only for safety runs.
4. Simulate instead of exhausting: `-simulate num=100000 -depth 100`. Report
   it as *N random behaviours, not exhaustive*.

## PlusCal

When each actor is a sequential procedure with many waiting points, PlusCal —
an algorithm language that translates to TLA+ — is often easier to keep
faithful: each label is one atomic step, which maps directly onto "the code
between two `await`s". Write the algorithm in a comment block in the `.tla`
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
