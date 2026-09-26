---
name: system-model
description: Model a system's behaviour in TLA+ or Lean, make its assumptions explicit, and check its properties. Use for understanding or comparing stateful designs, specifying workflows or protocols before implementation, checking existing state machines and pure functions, and discovering concurrency, retry, recovery or data-flow defects without needing a suspected bug. Leaves a runnable model and evidence with stated limits; reproduces implementation defects and fixes them when requested. Not for architecture diagrams alone or behaviour a direct unit test already settles.
---

# System model

*Make the behaviour explicit. Let the checks test the assumptions.*

A model records which states a system can occupy, which changes are allowed,
and what must remain true. Writing it exposes missing decisions; checking it
can expose behaviours nobody anticipated. The model is useful even when no
property fails.

Model the smallest part that answers the user's question. An existing
implementation and a proposed design are both valid subjects, but they support
different claims. A design counterexample can justify changing a proposal; it
does not prove that deployed code has a bug. A proof covers the formal model
under its assumptions, not everything about the real system.

## Establish the question

Identify the subject and intended outcome from the request:

| Request | Deliverable and stopping point |
|---|---|
| Understand or specify a system | An explained, runnable model, assumptions, representative behaviours and open questions |
| Check properties or compare designs | The model plus checked properties, counterexamples or proofs, and implications for each alternative |
| Find implementation bugs | The checks plus attempted reproduction of candidate defects; distinguish confirmed bugs from unresolved findings |
| Fix defects | The above plus scoped fixes and regression evidence |

These are outcomes of one workflow, not separate mandatory passes. Run basic
model sanity checks even for an understanding task; pursue deeper checking only
as far as the question warrants. A modelling or review request does not itself
authorize product changes. Do not require a suspected bug to begin.

With a supplied target, stay within it. Without one, survey intent and behaviour,
then select a small, consequential boundary and explain the choice. Start with
one model; add another only when it answers a distinct question. Use
[`references/modelling-targets.md`](references/modelling-targets.md) to identify
useful boundaries and failure cases, not as a quota of bugs to find. If a direct
test or explanation settles the question, say so rather than manufacturing a
formal-methods project.

Ask when an unresolved requirement would materially change the conclusion.
Otherwise record the assumption and proceed. When two plausible interpretations
matter, check both and explain their consequences instead of silently choosing
one. Tool installation and consequential external changes remain subject to the
user's authorization and the environment's permissions.

## 1. Describe the system and its contract

Read requirements, design notes, API contracts, tests and relevant code. Keep
what the system is required to do separate from what it currently does.

Before formal syntax, record:

- **Boundary and question:** the workflow, protocol, function or decision under
  study, and which question the model should answer.
- **State and actors:** who can act, what each knows, what persists, and what
  crosses a process, storage or network boundary.
- **Transitions:** initial conditions, permitted actions, guards, outcomes,
  and the atomicity of each action.
- **Environment and assumptions:** scheduling, delivery, crashes, recovery,
  time, external services and any dependencies deliberately omitted.
- **Properties:** the obligations to check, in plain language first.

Label each property's source: **intent** (a requirement or user statement),
**inferred** (suggested by existing behaviour), or **proposed** (a design choice
not yet agreed). Cite the source. An inferred or proposed property that fails
may reveal a decision to make rather than a defect to fix.

Distinguish state invariants such as "at most one owner", other safety
properties such as "every acknowledgement follows a durable write", and
liveness properties such as "every accepted request eventually completes".
State the environment and scheduling assumptions needed for progress. Do not
assume eventual success merely to make a liveness check pass.

## 2. Choose the formalism

| Question | Usually start with | Why |
|---|---|---|
| Interleavings, retries, crashes, deadlock or eventual progress | TLA+ with TLC | Explores reachable behaviours of a finite instance and returns violating traces |
| A state invariant over arbitrary runs, or a pure function's property | Lean 4 | Checks a proof of the stated theorem, including its hypotheses |
| Both kinds of question | One first; both only if needed | Separate bounded exploration from the distinct theorem being proved |

This is a starting point, not a limit on either language. Prefer the tool that
can answer the actual question with the least additional machinery. Record the
choice and read only the relevant reference:
[`references/tla.md`](references/tla.md) or
[`references/lean.md`](references/lean.md).

TLC can produce a counterexample automatically. An unsuccessful Lean proof
attempt is inconclusive: it might reflect a false claim, a weak induction
hypothesis, or a proof the agent has not found. To refute a property in Lean,
construct a witness and prove that it violates the property.

## 3. Build a faithful abstraction

For an **existing implementation**, map model actions to source files and
symbols, adding line locations where useful. Preserve the branches, ordering
and failure paths relevant to the properties. Explain how concrete data maps
to abstract state and which details are omitted. Transcribing every line is
unnecessary; omitting a relevant guard or inventing atomicity changes the answer.

For a **proposed design**, map actions to requirements or explicit design
choices. Missing implementation files are expected. Record underspecified
behaviour and keep alternatives separate. Do not invent code citations or
present design scenarios as observed implementation traces.

For a **comparison**, use the same properties, environment assumptions and
bounds for each alternative where possible. State differences that prevent a
like-for-like conclusion. If both a design and its implementation are modelled,
make the abstraction mapping explicit; neither automatically validates the other.

In every case:

- **Choose atomic steps deliberately.** On one cooperative event loop, code
  between suspension points can be indivisible relative to tasks on that loop;
  external stores and other processes can still act. On threads, consider locks
  and atomic operations. Across a network, separate the remote action from the
  response: the reply can be lost after the action succeeded. Treat database
  atomicity and isolation as separate questions.
- **Model the relevant environment.** Include crashes, recovery, timeouts or
  lost responses when they affect the question. Use time events or bounded
  logical time when exact clocks are unnecessary.
- **Expose assumptions.** Use parameters or explicit hypotheses, then vary the
  ones the conclusion depends on. Do not encode the desired result as a guard
  unless the actual design or implementation enforces it.
- **Start with a small finite instance for exploration.** Two actors and one
  or two items often reveal useful behaviours. They are a starting point, not
  a guarantee that larger instances behave alike. Record any state constraints.

## 4. Validate the model before trusting its results

A model can pass because it never reaches the behaviour under discussion.
Check normal outcomes and important failure or recovery states. In TLC, a
separate reachability check can assert that a desired state is never reached
and expect a violation. In Lean, prove that a concrete event sequence reaches
it. Keep these expected failures separate from the system's obligations.

Where existing code can run, replay observed traces through the model or compare
function outputs on shared inputs. Trace acceptance is evidence of correspondence,
not a proof of equivalence. A rejected trace needs investigation: the model,
instrumentation, mapping or implementation may disagree with the stated design.
Report what was observed and how much was checked; do not silently filter out
inconvenient traces.

For an unimplemented design, exercise scenarios drawn from the requirements and
label them **constructed**, not observed. Check that the model permits required
behaviour and that at least one meaningful bad behaviour would be detected—for
example, by deliberately weakening a guard in a separate sanity configuration.
A planted failure checks the test setup; it is not a discovered design defect.

Review the abstraction against its sources and its omissions. When independent
review is available and authorized, give the reviewer the sources, model and
check results without the author's justification. This is especially useful for
atomicity and model/code correspondence. State any validation left undone.

## 5. Check and interpret

Run the selected tool and retain the command, toolchain, configuration and
result. For TLC, report the bounds, explored states, properties and whether the
search completed; simulation or a timed-out run is not exhaustive. For Lean,
check theorem statements, hypotheses and their axioms. No `sorry` or
`native_decide` in the accepted proof artifact; the reference explains the trust
boundary and the supplied script checks it.

Classify each finding before changing anything:

| Finding | Action |
|---|---|
| Model or mapping error | Correct it against the evidence and rerun |
| Ambiguous requirement or failed inferred/proposed property | Explain the behaviour and the decision needed; do not label it an agreed defect |
| Design defect | Show the trace or witness against the stated requirement; propose or model a revised design within scope |
| Candidate implementation bug | Map the behaviour back to the code and attempt deterministic reproduction |
| No violation / proved property | Keep the model and state exactly what was checked or proved |

An assumption-sensitive result is useful: say which assumption changes the
conclusion. Do not strengthen the environment or weaken the obligation simply
to obtain a pass. After handling a violation, rerun the applicable checks; the
first failure may have hidden others.

## 6. Reproduce and fix when applicable

A candidate becomes a **confirmed implementation bug** when a deterministic test
or executable reproducer exercises the real code and fails for the stated reason.
Drive the trace's order explicitly with held promises, latches, controlled store
failures or a remote fake that acts and loses its reply. Avoid timing sleeps.

A test that passes does not settle the finding. Check whether the schedule and
observations actually exercise the counterexample and whether the model omitted
a real guard. Keep unresolved candidates with the missing evidence; retract a
finding only when there is a reason. A valid design defect does not need a
nonexistent implementation test.

Fix only within the requested scope. For an authorized implementation fix,
make the smallest change that restores the property, demonstrate the reproducer
failing before and passing after, and rerun the model, correspondence checks and
relevant repository tests. A before/after switch or separate configurations can
preserve both behaviours. Do not add an artificial "before" defect to a clean
system just to satisfy the example layout.

## 7. Leave a model others can use

Use the repository's existing convention, or `specs/`:

```
specs/
  README.md             index of questions and models
  checks                runnable checks with expected outcomes
  check.sh              copied from this skill's scripts/check.sh
  <Name>/               TLA+ model, configurations and explanation
  lean/<Name>/          Lean project, Audit.lean and explanation
```

Copy [`scripts/check.sh`](scripts/check.sh) when these tool checks fit. A row
expecting `fail` succeeds only on a genuine tool-reported violation, not a parse
error; inspect the named violation as well to ensure it is the intended check.
Add replay helpers, regression tests or alternative configurations only when
used. Keep runtime caches and downloaded tool binaries out of the repository.

Each model's explanation records its question, design or implementation subject,
states and transitions, property sources, assumptions and omissions, source
mapping, exact rerun instructions, validation evidence, findings and open
questions. Include checked bounds or theorem hypotheses. Distinguish constructed
scenarios from observed traces and clean checks from unfinished work.

Offer an agent-instructions note about maintaining models with the relevant
code or design; add it only if requested. Do not claim the models stay current
without a maintenance step.

## 8. Report what was learned

Lead with the answer to the user's question. Then give:

- **Model:** the boundary, key behaviours and assumptions it makes explicit.
- **Evidence:** checked properties or theorems, configurations, bounds or
  hypotheses, reachability and correspondence results, and unfinished checks.
- **Findings:** design decisions, counterexamples, confirmed implementation
  defects, scoped fixes and unresolved candidates, clearly distinguished.
- **Limits and reuse:** what is excluded, what the evidence does not establish,
  and where to find and rerun the model.

Use *no counterexample in the checked finite instance* for exhaustive TLC runs,
*proved for this model under these hypotheses* for Lean, and *not checked* for
unfinished work. Avoid *verified* on its own. A useful model with no defect is
a complete result.

## Tools

TLC needs Java and `tla2tools.jar`; the check script reads `JAVA` and
`TLA2TOOLS`. Lean uses `lean` and `lake`, commonly managed by `elan`.

Check existing installations before proposing a download. On macOS, the system
Java launcher may fail while a package-managed JDK works; inspect the active
path and known package/version-manager locations. Look for an existing TLC jar
in configured or project tool directories. For Lean, list installed toolchains
with `elan toolchain list` and prefer an existing one, even if no default is set.

If a required tool is unavailable, explain the gap and follow the user's
installation authorization. A model can still be drafted and reviewed, but
label it unexecuted until the check has actually run.
