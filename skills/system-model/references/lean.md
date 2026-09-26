# Lean 4 reference

For one actor's state machine that must keep an invariant for every length of
run, and for pure functions with a crisp property. Where TLC checks every state
of a small instance, Lean checks the proposition actually stated. A theorem
quantified over all runs can be unbounded, but finite types or hypotheses may
still restrict it. A failed proof attempt alone is not a counterexample.

## Contents

- Project layout
- A model to copy
- The counterexample, before the fix
- The invariant, after the fix
- Replaying real traces
- Pure functions
- The audit
- Pitfalls

## Project layout

One Lake project per target, core Lean only — add Mathlib only when a proof
needs it, because it costs minutes of build time and gigabytes of disk.

```bash
cd specs/lean
lake new Launch lib        # the library template; the model goes in the file it creates
cd Launch && lake build
```

Pin the toolchain the project was proved with in `lean-toolchain`; proofs can
break between Lean releases. Prefer one already installed (`elan toolchain
list`), written exactly as listed, e.g. `leanprover/lean4:v4.35.0-rc2`.

## A model to copy

A launch that can lose the remote system's response. Before the fix, a lost
response was recorded as a failure, so a fresh launch could start the work a
second time; the fix records it as *unknown* and resolves it by reconciling.

- **State** is a structure; **events** are an inductive type with one
  constructor per code path; **step** is a partial function, `none` meaning the
  event is not enabled in that state.
- Each constructor maps to the code or requirement it models. The source
  locations below are placeholders for this worked example, not real citations.
- `fixed` compares two behaviours here. A single-design or clean-system model
  does not need a synthetic broken variant.

```lean
namespace Launch

inductive Phase where
  | idle | authorized | unknown | launched | failed
  deriving DecidableEq, Repr

structure State where
  phase : Phase
  executions : Nat          -- how many times the remote actually started the work
  deriving DecidableEq, Repr

inductive Event where
  | authorize   -- launch.ts:40
  | startOk     -- launch.ts:55
  | startLost   -- launch.ts:61  the remote started it; the response was lost
  | reject      -- launch.ts:66  the remote refused; nothing started
  | reconcile   -- launch.ts:80
  deriving DecidableEq, Repr

def init : State := { phase := .idle, executions := 0 }

def step (fixed : Bool) (s : State) : Event → Option State
  | .authorize =>
      if s.phase = .idle ∨ s.phase = .failed then some { s with phase := .authorized } else none
  | .startOk =>
      if s.phase = .authorized then some { phase := .launched, executions := s.executions + 1 }
      else none
  | .startLost =>
      if s.phase = .authorized then
        some { phase := if fixed then .unknown else .failed, executions := s.executions + 1 }
      else none
  | .reject =>
      if s.phase = .authorized then some { s with phase := .failed } else none
  | .reconcile =>
      if s.phase = .unknown then some { s with phase := .launched } else none

def run (fixed : Bool) : State → List Event → Option State
  | s, [] => some s
  | s, e :: es =>
      match step fixed s e with
      | some s' => run fixed s' es
      | none => none
```

## The counterexample, before the fix

The Lean form of a TLC trace: a concrete event list, and a proof that it
reaches the bad state. For an implementation finding, attempt the same four events in the real code.
For a design, this is evidence against its stated property; no implementation
is required to demonstrate that design behaviour.

```lean
/-- Before the fix: a lost response, then a fresh launch, starts the work twice. -/
theorem before_double_start :
    (run false init [.authorize, .startLost, .authorize, .startOk]).map (·.executions)
      = some 2 := by
  decide
```

Prove reachability the same way: a theorem that some event list
reaches `.launched`. If no such list exists, the model is wrong.

## The invariant, after the fix

The claim — *the work starts at most once* — is not itself preserved by every
step, so strengthen it until it is: tie `executions` to the phase.

```lean
def Inv (s : State) : Prop :=
  match s.phase with
  | .unknown | .launched => s.executions = 1
  | _ => s.executions = 0

theorem inv_init : Inv init := rfl

theorem inv_step {s s' : State} {e : Event}
    (h : Inv s) (hs : step true s e = some s') : Inv s' := by
  obtain ⟨phase, n⟩ := s
  cases e <;> cases phase <;> simp [step] at hs <;> subst hs <;> simp_all [Inv]

theorem inv_run : ∀ (es : List Event) (s s' : State),
    Inv s → run true s es = some s' → Inv s'
  | [], s, s', h, hr => by
      simp [run] at hr
      subst hr
      exact h
  | e :: es, s, s', h, hr => by
      cases hs : step true s e with
      | none => simp [run, hs] at hr
      | some s₁ =>
          simp [run, hs] at hr
          exact inv_run es s₁ s' (inv_step h hs) hr

/-- After the fix: every run from the start keeps the work to at most one start. -/
theorem at_most_one_execution (es : List Event) (s : State)
    (hr : run true init es = some s) : s.executions ≤ 1 := by
  have h := inv_run es init s inv_init hr
  unfold Inv at h
  split at h <;> omega
```

The shape generalises: `Inv` with `inv_init` and `inv_step`, lifted to runs by
induction, then the headline property as a corollary. If `inv_step` will not close, inspect the obligation: the invariant may need
strengthening, the model or property may be wrong, or the proof may simply be
unfinished. Strengthening the induction hypothesis must still follow from the
initial state and be preserved by every permitted step.

Further proofs may be useful when the question calls for them:

- **Agreement** — on every step where the old code kept the invariant, the
  fixed step gives the same result. It shows the fix changed nothing else.
- **Termination** — for a loop that must stop, a measure that every step
  decreases (retries left, turns left).

## Replaying real traces

Replay implementation observations only when code exists. For proposed designs,
prove selected requirement scenarios reachable and label them constructed.
The example below illustrates the encoding; use actual recorded states before
claiming observed correspondence.

```lean
def replay (fixed : Bool) : State → List (Event × State) → Bool
  | _, [] => true
  | s, (e, observed) :: rest =>
      match step fixed s e with
      | some s' => s' == observed && replay fixed s' rest
      | none => false

/-- The happy path, as logged by launch.test.ts. -/
example : replay true init
    [(.authorize, ⟨.authorized, 0⟩), (.startOk, ⟨.launched, 1⟩)] = true := by
  decide
```

Generate one `example` per logged trace with a small script. Every one must
build.

## Pure functions

For a function such as a sanitiser or a routing decision, write the Lean
definition that preserves the relevant semantics, documenting any abstraction
from the implementation, then state the property
for every input (`∀ s, Valid (sanitize s)`). Two cautions:

- Proofs over `String` in core Lean are laborious; modelling the input as
  `List Char` usually makes them tractable.
- The proof covers the Lean definition. One correspondence check is a differential test: run
  the real implementation and `#eval` the Lean one over the same inputs —
  including the edge cases the proof relied on — and compare. Agreement on
  these inputs is evidence, not a proof that the transcription is equivalent.
  For a proposed function with no implementation, report this check as not
  applicable; validate its stated requirements instead.

## The audit

`Audit.lean` in the project root imports the model and prints the axioms of
every headline theorem:

```lean
import Launch

#print axioms Launch.at_most_one_execution
#print axioms Launch.before_double_start
```

```bash
lake build && lake env lean Audit.lean
```

Acceptable: *does not depend on any axioms*, or only `propext`, `Quot.sound`
and `Classical.choice`. `sorryAx` means an unfinished proof; `Lean.ofReduceBool`
means `native_decide`, which trusts the compiler rather than the kernel. The
check script rejects both.

## Pitfalls

- `decide` fails with *failed to reduce* when a definition uses well-founded
  recursion or opaque functions; keep models structurally recursive, or try
  `rfl`. Never reach for `native_decide`.
- `deriving DecidableEq` on every state and event type, or `decide` and `==`
  have nothing to work with.
- A proof that goes through with `simp_all` today may break on the next
  toolchain; the pinned `lean-toolchain` is part of the proof.
- A theorem's name is a claim. Reviewers read names; make each one say exactly
  what the statement proves.
