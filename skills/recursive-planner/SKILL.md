---
name: recursive-planner
description: Plan and carry out work too large to plan in detail up front. Draw a coarse high-level plan, detail only the first step in plan mode, do it, then re-enter plan mode for the next step — revising the high-level plan with what the last step taught — recursively, until the destination is reached. A step too big to plan concretely becomes its own high-level plan with its own detailed first step. Use when the user invokes /recursive-planner.
disable-model-invocation: true
---

# Recursive planner

*Plan the whole route coarsely; plan only the next step in detail.*

A detailed plan for a large job is mostly fiction past its first step. Every
step teaches something — an API behaves differently, a file is shaped
differently, a decision turns out not to matter — and the detail written for
step five was written without it. Planning everything up front either wastes
that detail or, worse, commits to it.

This skill keeps two resolutions at once. The **high-level plan** covers the
whole route and stays coarse. The **step plan** covers only the next step and is
concrete enough to execute. After each step, plan mode is re-entered on purpose:
the high-level plan is revised with what was learned, and only then is the next
step detailed.

## The loop

1. **Name the destination.** One or two lines: what is true when this is done.
   It fixes the scope and the stopping condition. If the user's request does not
   make it clear, ask before planning anything.
2. **Enter plan mode** (call `EnterPlanMode`; if it is a deferred tool, load it
   with `ToolSearch` first). Every planning pass in this skill happens in plan
   mode, so every pass ends in an approval.
3. **Plan, at two resolutions** — in this one plan-mode pass:
   - the **high-level plan**: the remaining route as a short numbered list, each
     step one line, stated as an outcome rather than a set of edits;
   - the **step plan**: the next step only, in full detail — files, commands,
     checks, and how you will know it is done.
4. **Exit plan mode for approval** (`ExitPlanMode`). The user approves, edits,
   or redirects. Do not start the step before approval.
5. **Execute the step.** Only that step. When the pull to carry on into the next
   step appears, that is the signal to stop and re-plan, not to keep going.
6. **Re-enter plan mode** (`EnterPlanMode` again) and go back to step 3, with the
   step just finished marked done and its lessons folded in. Repeat until the
   destination is reached.

Re-entering plan mode is not optional, and it is not a formality for steps that
look obvious. Its value is the revision of the high-level plan, which is easy to
skip exactly when the last step went smoothly.

## Revising the high-level plan

On each re-entry, before detailing the next step, look at the whole remaining
route and ask what the last step changed:

- **A step is no longer needed** — remove it, and say why in one line.
- **A new step appeared** — add it where it belongs.
- **The order changed** — a dependency surfaced, or a risky step should come
  earlier.
- **The destination itself moved** — stop and ask the user. Do not quietly
  redraw it.

Show the changes explicitly, so the user can approve the revision and not only
the next step. If nothing changed, say so in one line.

## Recursion

A step in the high-level plan is a **leaf** when its step plan can be written
concretely in one pass: you know what you will touch and how you will check it.
When you try to detail a step and cannot — it is still a destination, not a
step — it becomes a **sub-plan**: give it its own high-level plan and detail
only its first step, then run the same loop inside it. When the sub-plan reaches
its own destination, pop back up and revise the parent plan.

Whether to recurse is a judgement, not a rule. There is no depth cap; recurse as
deep as the work needs. The user can step in at any approval to flatten a
sub-plan, split a step, or tell you to just do it.

## The plan, shown at each pass

The plan lives in the conversation. Nothing persists it between passes, so each
plan-mode pass restates the whole tree — this is what keeps it intact across
long sessions and context compaction. Use the same shape every time:

```markdown
## Destination

<one or two lines>

## Plan

1. ~~<done step>~~ — <one-line result>
2. <current step>  ← here
   2.1 ~~<done sub-step>~~ — <one-line result>
   2.2 <current sub-step>  ← here
   2.3 <coarse sub-step>
3. <coarse step>
4. <coarse step>

## Changes since last pass

<added, removed, reordered — with one line of why each; or "none">

## Next step: <name>

<the detailed step plan: what changes, in which files, which commands run,
and how you will check it is done>
```

Done steps collapse to one line each: a result, not a log. Coarse steps stay
coarse — do not detail a step until it is next. Detail written early is detail
written before the evidence.

## Stopping

The work is done when the destination is true. On the last pass, check it
against the destination as written in step 1, not against the plan: the plan was
only ever a route there. Report what was done, what changed from the original
high-level plan, and anything deliberately left out.

If the destination turns out to be wrong, unreachable, or not worth reaching,
stop and say so. Finishing the plan is not the goal.

## Traps

- **Detailing ahead.** Writing out steps 2–5 in full during the first pass. The
  whole skill exists to avoid this.
- **Skipping re-entry.** Rolling from one step into the next because it seems
  obvious. The revision of the high-level plan is what gets lost.
- **Running past the step.** Doing part of the next step while executing this
  one, so the next plan describes work already half done.
- **Plan as log.** Done steps that keep their full detail. The tree grows until
  the remaining route is hard to see.
- **Silent scope change.** Adding steps past the destination, or redrawing it,
  without asking.
