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
| [`references/lean.md`](references/lean.md) | modelling, searching and proving properties in Lean |
| [`references/modelling-targets.md`](references/modelling-targets.md) | surveying a codebase, choosing a boundary or recognizing a failure class |
| [`references/simplifying.md`](references/simplifying.md) | removing code a checked property shows to be redundant |
| [`references/output.md`](references/output.md) | laying out the model, its README and the report |
| [`scripts/check.sh`](scripts/check.sh) | copied into the target repository to rerun formal checks |
| [`scripts/find-tools.sh`](scripts/find-tools.sh) | finding an installed Java, TLC jar and Lean toolchain; writes nothing |

## Related

[opum-ai/proof-skills](https://github.com/opum-ai/proof-skills) (MIT) packages
the same model, counterexample, reproduce and fix loop as four Claude Code
skills with more automation: a library of checked TLA+ and Lean patterns,
install scripts, a TLC wrapper that turns traces into code-mapped tables, a
drift checker for model-to-code pointers, CI templates, and a generated HTML
report. Reach for it when you want that tooling. This skill is smaller,
depends on neither it nor its scripts, and differs in stance: it treats
understanding and specifying a system as complete outcomes, labels where each
property came from, and words results as bounded checks or proofs about a model
rather than as verification of the code.

## Credits

The implementation-focused origin is Boris Cherny's
[account of modelling the Claude Agent SDK in Lean and TLA+](https://www.linkedin.com/posts/bcherny_i-used-opus-55-to-formally-verify-the-claude-activity-7508309724598263808-TVJY)
to discover bugs and races. The design-modelling workflow extends that use case.
Two MIT-licensed skills shaped the original procedures:

- [`todaycha/tla-bug-hunt`](https://github.com/todaycha/tla-bug-hunt): derive
  properties from intent, check reachability, and reproduce defects before fixes.
- [`yavosh/skills` `formal-verify`](https://github.com/yavosh/skills): runtime
  atomicity, trace replay, before/after comparisons and rerunnable checks.

Several procedures were adapted, in new words and code, from ideas in
[opum-ai/proof-skills](https://github.com/opum-ai/proof-skills) (MIT, v0.1.1):
searching a Lean model's small instances for counterexamples before proving,
recording properties before the first check and reporting later changes,
pairing results with expected-failure configurations, the failure-class
catalogue, simplifying code from checked properties, surveying a codebase
before modelling several boundaries, and extending trace replay to partial logs.
No text or code was copied.

The revision follows
[Anthropic's Skill Creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator):
explain the reasoning, keep tool details in references, and compare realistic
outputs against the previous skill before refining the instructions.
