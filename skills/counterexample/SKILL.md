---
name: counterexample
description: Find the bugs tests miss in state machines, concurrency and data flow by modelling the risky part of a codebase formally — TLA+ when several actors, retries or crashes interleave, Lean 4 when one state machine or pure function must keep an invariant for every input — then letting the model checker or prover produce a counterexample, reproducing it as a failing test in the real code, fixing it, and leaving a proof anyone can rerun. Chooses the formalism per target. Use whenever the user asks to formally verify, model-check or prove code, to "throw TLA+ or Lean at" something, or to hunt race conditions, lost updates, stuck states, double execution, retry and idempotency bugs, or to check that a workflow, protocol, lease, queue, reconciler or UI flow can never reach a bad state — even when no formalism is named.
---

# Counterexample

*Let the checker find the bug.*

A test checks the orderings someone thought of. A model checker checks every
ordering, at a small size, and hands back the one nobody thought of as a
numbered list of steps. That list is what this skill produces: a suspected bug
concrete enough to become a failing test.

This is bug finding first and proof second, and the difference must survive
into every sentence of the report. A model check that finds nothing says *no
counterexample with two workers and one job*, not *correct*. A Lean proof proves
the model; it covers the code only as far as the model matches the code. Say
which one you have.

## When it earns its cost

It pays where the bug needs an unlucky order:

- state written by more than one actor — requests, workers, replicas, a user
  and a background job;
- a lifecycle with many exits — retry, timeout, cancel, crash, restart,
  reconcile, abandon;
- two systems that must agree — a database and a queue, an event log and a
  workflow engine, a local record and a remote API;
- promises of *at most once*, *exactly once*, *eventually*, *never both*;
- a pure function with a crisp property that a few examples cannot cover.

It does not pay for rendering, formatting, plain CRUD, or anything a direct
unit test already pins. If the survey finds nothing that fits, report that. An
empty survey is a valid result; a skill that must find something will invent
something.

## The loop

| Stage | Ends with |
|---|---|
| 1. Survey | ranked targets |
| 2. Choose the tool | TLA+, Lean, or both, per target, with the reason |
| 3. Write the invariants | each one sourced: *intent* or *inferred* |
| 4. Model the real code | a model that cites `file:line` for every step |
| 5. Prove the model can fail | reachability shown, real traces accepted |
| 6. Check | a clean run or a counterexample |
| 7. Triage | modelling mistake, question, or candidate |
| 8. Reproduce | a failing test in the real code — or the finding is dropped |
| 9. Fix | the smallest change, the model rerun with the fix switched on |
| 10. Leave the proof | `specs/` with a check script anyone can run |
| 11. Report | bugs, evidence, limits |

Stages 5 and 8 are the ones that make the rest worth anything. A model nobody
has shown to be *capable* of failing proves nothing when it passes; a
counterexample nobody has reproduced is a guess.

## Working without supervision

The skill is meant to be pointed at something and left to run.

- **With a target** (a file, a module, a flow, a bug hypothesis): work that
  target only.
- **Without one**: survey, show the ranking in one table, then work the top
  targets (at most five). Say which ones you skipped and why.

Stop and ask only where the answer changes risk or scope:

- a tool is missing (installing one is a download onto the user's machine);
- an invariant can only be inferred from the code and a counterexample depends
  on it (stage 7);
- the change needed is not small, or touches shared or production state.

Everything else — which target first when two rank alike, how big to make the
model, how to phrase a test — decide, say what you decided, and continue.

With more than one target, give each its own subagent for stages 3–8. Hand it
the target's files, its actors and the relevant reference file; it writes only
under `specs/` and in test files. You own version control and the report.

## 1. Survey

Read intent before code: design notes, ADRs, API contracts, issue text, and the
tests' names. Invariants come from intent (stage 3), and a survey that starts
from the code tends to model what the code does rather than what it must do.

Then look for the shapes in [`references/bug-shapes.md`](references/bug-shapes.md):
durable status fields, claims and leases, retries and idempotency keys,
reconcilers, event logs folded into state, a check before an `await` and an act
after it, two stores written without one transaction, a lock or queue that is
only local to one process.

For each candidate record:

| Target | Actors | Shared state | The bad outcome, in one sentence | Where intent is written | Size |
|---|---|---|---|---|---|

Rank by the cost of the bad outcome times how many orderings reach it — not by
how complicated the code looks. Small and reachable beats large and exotic.

## 2. Choose the tool, per target

| The target is… | TLA+ | Lean 4 |
|---|---|---|
| several actors, retries, crashes or replicas interleaving | **yes** — TLC explores every interleaving | awkward |
| one actor's state machine that must hold for any length of run | only up to a bound | **yes** — induction over every event sequence |
| a pure function with a property (encode/decode, a sanitiser, a decision table) | a poor fit | **yes** |
| "eventually reaches a terminal state", "never stuck" | **yes**, with fairness | through a decreasing measure |
| wanted quickly | **cheaper** — model, config, run | dearer — proofs need lemmas |

Default: TLA+ for anything with more than one actor; Lean for single-actor step
invariants and pure functions; both when several actors drive one state machine
— TLA+ for the interleavings at a small size, Lean for the step invariant at
every size. Write the choice and its reason into the model's README. Neither is
the house style; the target decides.

Details: [`references/tla.md`](references/tla.md), [`references/lean.md`](references/lean.md).

## 3. Write the invariants — with their source

An invariant says what must never happen (*safety*: at most one execution per
launch) or what must eventually happen (*liveness*: every accepted request ends
in a terminal state). Write each as one plain sentence before writing it as a
formula; if the sentence is hard to write, the formula will be wrong.

Label each one:

- **intent** — stated in a design note, contract, issue, test name, or by the
  user;
- **inferred** — read off the code because nothing else states it.

The label matters because a model built from the code inherits the code's
mistakes. If the code implements the wrong rule, a model that takes its rule
from the code will agree with it and pass. And a counterexample to an inferred
invariant may be behaviour someone intended. So prefer intent; when only
inference is available, continue with the inferred invariant but carry the
label into triage. If several invariants are inferred and the user is present,
ask about them once, as one batch, and keep modelling while you wait.

Invariants that recur: at most one of something; no lost update; a terminal
state is absorbing; every accepted request ends terminal; two stores agree once
activity stops; a retry never repeats a side effect; a refusal leaves nothing
half-done; a newer fact is never overwritten by an older one.

## 4. Model the real code

- **Model the code, not the design.** If the code has a flag, a copy-pasted
  branch or a workaround, so does the model. Put the `file:line` each action or
  event models in a comment beside it. A model of the intended design finds
  bugs in the design document.
- **Atomicity decides everything.** One model step is one indivisible unit of
  the real runtime:
  - on a single-threaded event loop (JavaScript, TypeScript, Python asyncio),
    the code between two `await`s;
  - on threads, one lock-held section or one atomic operation;
  - in a database, one statement, or one transaction;
  - across a network, the request and the response are separate steps, and the
    response can be lost *after* the other side acted.

  A *read, then act* is two steps unless a lock, a transaction or a
  compare-and-set joins them. Most real bugs live in that gap.
- **The environment is nondeterministic.** Crashes and restart recovery, lost
  responses, timeouts firing, a second replica, a deadline passing — each is an
  action the checker may take at any moment. Model time as events, not clocks.
- **Assumptions are parameters**, not facts: a constant in TLA+, a hypothesis
  in Lean. Then the model can show what breaks when one fails.
- **Start small.** Two actors, one or two items, counters bounded at two or
  three. Ordering bugs almost always show at size two. Grow after a clean run.
- **Add a switch once a fix is known** (`Fixed` in TLA+, `fixed : Bool` in
  Lean), so one model shows the old code failing and the new code passing.

## 5. Prove the model can fail

Skip this and a clean result means nothing — a model with a wrong guard can
simply never reach the interesting states.

- **Reachability.** Show the model reaches the normal good outcome: add a
  temporary invariant claiming it cannot ("no run ever completes") and confirm
  the checker violates it. In Lean, prove a concrete event list reaches it.
- **Conformance.** Show the model accepts real behaviour. Log each modelled
  transition from the existing tests (or a cheap real run), turn the logs into
  traces of model states, and replay them through the model — the reference
  files show how. Every trace must be accepted; a rejected trace means a
  missing action, a wrong guard or wrong atomicity. If 100% is out of reach,
  report *N of M accepted* and call the results provisional. For a pure
  function, conformance is a differential test: run the real implementation
  and the Lean definition over the same inputs and compare.
- **Independent review.** Give a fresh subagent the source, the model and the
  replay results — not your reasoning — and ask it to check each action against
  its `file:line`, to find code paths the model lacks and model paths the code
  cannot take, and to confirm each theorem proves what its name claims.

## 6. Check

Run TLC or build the Lean project as the reference files describe. Read TLC's
output, not its exit code. In Lean, no `sorry` and no `native_decide`; an audit
file prints the axioms each main theorem depends on.

## 7. Triage every counterexample

TLC stops at the first violation. After handling one, run again — the next may
have been hiding behind it.

- **Modelling mistake** — the trace needs something the code cannot do.
  Constrain the model, tell the user in one line, rerun.
- **Question** — the trace breaks an *inferred* invariant. Present the trace
  and ask whether the behaviour is intended. Do not fix it.
- **Candidate** — map every step to `file:line` and write the interleaving as a
  numbered list in plain language. Go to stage 8.

## 8. Reproduce — the promotion rule

Only a counterexample that reproduces as a failing test in the real code is a
bug. Everything else stays a parked note in the model's README.

Make the test deterministic; it drives the trace's order itself:

- fakes that block until the test releases them — a held promise `resolve`, a
  latch, a channel — released in trace order;
- a store wrapper that fails exactly one call;
- a fake remote that commits and then loses the response;
- internal steps called directly when the public path cannot be paced.

No sleeps. Run it on the current code: it must fail, and for the reason the
trace gives. If it passes, the model was too pessimistic — find the guard the
model omitted, refine the model, and drop the finding.

## 9. Fix

Fix confirmed bugs unless the user asked for findings only. Follow the
repository's own rules for branches, commits and pull requests over anything
here, one bug per commit.

- Make the smallest change that restores the invariant, in the surrounding
  code's style. Common shapes are in [`references/bug-shapes.md`](references/bug-shapes.md).
- Turn the model's switch on, and rerun the model, the replays, the full test
  suite and the linter.
- Prove the regression test: it fails on the parent of the fix and passes on
  the fix.

## 10. Leave the proof

```
specs/
  README.md             index: one line per model
  checks                one line per check; run by check.sh
  check.sh              copied from this skill's scripts/
  <Name>/               a TLA+ model: <Name>.tla, <Name>.cfg,
                        <Name>Before.cfg, <Name>Traces.tla, README.md
  lean/<Name>/          a Lean project: the model, Audit.lean, README.md
```

Copy [`scripts/check.sh`](scripts/check.sh) to `specs/check.sh`. It runs every
line of `specs/checks` and fails when any result differs from its expectation —
including an expected *fail*, which passes only on a genuine violation, never on
a parse error.

Each model's README states: what it covers (files and functions), the
invariants with their source, the assumptions, the sizes checked and states
explored, the replay result, the counterexamples found and the tests that
reproduce them, and what it does not prove.

Offer — do not add without a yes — one line for the repository's agent
instructions: *`specs/` holds formal models; when changing code a model cites,
update the model and run `specs/check.sh`.*

## 11. Report

Three parts, in this order:

1. **Bugs** — each as its numbered interleaving, the test that reproduces it,
   and the commit that fixes it.
2. **Evidence** — one row per model: tool, checks, sizes, states explored,
   replay *N of M*, result.
3. **Limits** — assumptions, bounds, inferred invariants still unconfirmed,
   parts of the code modelled out, questions from stage 7.

Use the words that match the evidence: *no counterexample up to size N* for a
model check, *proved for the model* for Lean, *not modelled* for the rest. Never
*verified* on its own.

## Tools

- **TLA+:** a Java runtime (11 or later) and `tla2tools.jar` from the
  [tlaplus releases](https://github.com/tlaplus/tlaplus/releases). The script
  reads the jar's path from `TLA2TOOLS`.
- **Lean 4:** `elan`, which installs `lean` and `lake`.

Look before concluding a tool is missing — both are often installed where the
obvious command cannot see them:

- **Java.** On macOS, `/usr/bin/java` is a placeholder that reports no runtime
  even when several are installed, because package managers keep their JDKs off
  the `PATH`. Look in `/usr/libexec/java_home -V`, the package manager's own
  directories (Homebrew's `opt/openjdk*`), and version managers (`mise`,
  `sdkman`, `asdf`). Point `JAVA` at the one you pick.
- **`tla2tools.jar`.** Search the machine for an existing copy before
  downloading one; point `TLA2TOOLS` at it.
- **Lean.** With no default toolchain, `lean --version` fails although a
  project that pins an installed toolchain builds fine. List them with
  `elan toolchain list` and pin one in `lean-toolchain`.

If something is really missing, name it and give the install command, then wait
for a yes: each is a download onto the user's machine. Never commit the jar; keep TLC's
working directory out of the repository.
