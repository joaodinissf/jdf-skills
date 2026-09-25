# counterexample

*Let the checker find the bug.*

Point it at code where the order of events matters — a launch that can lose its
response, a claim two workers race for, a fold over an event log, a button that
can offer an action the server will refuse — and it models that part formally,
lets a checker find the ordering that breaks it, and turns the ordering into a
failing test before anyone touches a fix.

It chooses the formalism per target:

- **TLA+** when several actors, retries or crashes interleave. TLC checks every
  interleaving of a small instance and prints the shortest bad one.
- **Lean 4** when one state machine or one pure function must keep a property
  for every input and every length of run.
- **Both** when several actors drive one state machine.

What it leaves behind is a `specs/` directory and a script that reruns every
model, replay and proof, so the evidence outlives the session that produced it.

## Files

| File | Read when |
|---|---|
| [`SKILL.md`](SKILL.md) | always — the procedure |
| [`references/tla.md`](references/tla.md) | modelling a target in TLA+ |
| [`references/lean.md`](references/lean.md) | modelling a target in Lean 4 |
| [`references/bug-shapes.md`](references/bug-shapes.md) | surveying, and choosing a fix |
| [`scripts/check.sh`](scripts/check.sh) | copied into the target repository as `specs/check.sh` |

## Credits

The loop — model the hairiest state machine, find counterexamples, reproduce
them as real bugs, fix — is the one Boris Cherny described after using Claude to
model the Claude Agent SDK in Lean and TLA+. Two MIT-licensed skills published
the day after shaped the details:

- [`todaycha/tla-bug-hunt`](https://github.com/todaycha/tla-bug-hunt): invariants
  come from intent, not from the code under suspicion; prove the model can
  reach its normal outcome before trusting a clean run; no product change
  before a failing test.
- [`yavosh/skills` `formal-verify`](https://github.com/yavosh/skills): atomicity
  rules per runtime, replaying real traces through the model, a before/after
  switch in one model, and a check script that makes the proof rerunnable.
