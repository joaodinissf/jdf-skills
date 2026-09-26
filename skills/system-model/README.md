# system-model

*Make the behaviour explicit. Let the checks test the assumptions.*

Point it at a workflow, protocol, state machine or pure function, implemented or
proposed. It builds a small formal model, explains the states and transitions,
makes assumptions explicit, and checks the properties that answer your question.
You do not need to suspect a bug. Understanding the system and retaining a
runnable model are useful outcomes even when no property fails.

It usually starts with **TLA+** for interleavings and progress, or **Lean 4** for
proofs about state transitions and functions. The question decides; using both
is worthwhile only when they answer distinct questions.

A design counterexample identifies a problem with the proposal under its stated
requirements. A candidate implementation bug needs a deterministic reproduction
before it is called confirmed. Fixes are made when requested. Results always
state their assumptions and limits: checked finite instances, proved model
properties, or work still unexecuted.

## Use

- “Model this retry workflow and explain what happens after a lost response.”
- “Compare these two lease designs before we implement either.”
- “Check this event fold for ordering bugs; reproduce anything you find.”
- “Find and fix races in this worker's claim protocol.”

The result lives in `specs/` (or the repository's established equivalent), with
source mappings, properties, scenarios or traces, check results and rerun
instructions. Implementation fixes add regression tests; a design-only model
does not invent an implementation to satisfy that step.

## Files

| File | Read when |
|---|---|
| [`SKILL.md`](SKILL.md) | always — scope, workflow and evidence rules |
| [`references/tla.md`](references/tla.md) | modelling and checking a target in TLA+ |
| [`references/lean.md`](references/lean.md) | modelling and proving properties in Lean |
| [`references/modelling-targets.md`](references/modelling-targets.md) | choosing a boundary or investigating a failure |
| [`scripts/check.sh`](scripts/check.sh) | copied into the target repository to rerun formal checks |

## Credits

The implementation-focused origin is Boris Cherny's
[account of modelling the Claude Agent SDK in Lean and TLA+](https://www.linkedin.com/posts/bcherny_i-used-opus-55-to-formally-verify-the-claude-activity-7508309724598263808-TVJY)
to discover bugs and races. The design-modelling workflow extends that use case.
Two MIT-licensed skills shaped the original procedures:

- [`todaycha/tla-bug-hunt`](https://github.com/todaycha/tla-bug-hunt): derive
  properties from intent, check reachability, and reproduce defects before fixes.
- [`yavosh/skills` `formal-verify`](https://github.com/yavosh/skills): runtime
  atomicity, trace replay, before/after comparisons and rerunnable checks.

The revision follows
[Anthropic's Skill Creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator):
explain the reasoning, keep tool details in references, and compare realistic
outputs against the previous skill before refining the instructions.
