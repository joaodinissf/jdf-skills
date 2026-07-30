---
name: perennial-docs
description: Rewrite documentation that reads as a record of the work that produced it — examples taken from the last thing touched, warnings about obstacles hit once, ordering that follows how the work happened. Use when writing standing documentation (READMEs, contributor guides, agent instruction files, runbooks, style guides), or when a reader says a document reads like a diary, is too tied to recent work, or will not age well.
---

# Perennial docs

Standing documentation is read by people who were not there. A document is
perennial when nothing in it depends on knowing what happened the week it was
written.

The instinct behind the failure is a good one: something has just been learned,
and it gets written down while it is vivid. What lands on the page is the
episode. What was needed was the rule.

**Write the destination, not the path.**

## Why this survives review

A session diary is usually *accurate the day it is written*. That is what makes
it hard to catch — nothing in it is false, so nothing objects. It decays from
both ends: readers without the context cannot use it, and the context it assumes
stops being true.

General patterns last. Episodes rot.

## Signals

Each of these is mechanical enough to catch by reading.

**The example is the last thing worked on.** The file just edited becomes the
illustration. Ask whether a stranger would have picked it.

**A warning about something that happened once.** An obstacle hit during the
work becomes a caution in the docs. One occurrence is not a pattern.

**Ordering follows how the work went.** The path taken this time leads, and the
path most readers take is further down.

**Temporal words.** *now, currently, recently, still, new, no longer, as of,
these days, going forward.* Each one is a claim that requires re-checking.

**Version-specific defects.** A named tool's bug, a workaround for a broken
release. True this month, misleading after the fix.

**Rationale longer than the rule.** Paragraphs of why, one line of what.

**Self-reference.** The document uses itself, or its own project, as the
example — a sign the writer reached for what was in front of them.

**Prose that argues.** *We found that… It turns out… Note that we had to…* The
reader does not need convincing, only telling.

## The rewrites

1. **State the rule, not the story.** Everything a reader must *do* survives.
   Everything explaining how it came to be goes.

2. **Common case first.** Check this deliberately — the case just worked through
   will feel like the common one, and usually is not.

3. **Cut the incident.** If it happened once, it is not documentation. If it
   recurs, describe the recurring condition, not the occasion.

4. **Describe how it works, not what went wrong with it.** Mechanism outlives
   symptom, and reads as instruction instead of grievance.

5. **Name tools; keep rules independent of them.** Name what to run, but phrase
   the rule so it survives the tool being replaced.

6. **Delete temporal words.** State what is true, unqualified. If it is only
   true for now, it does not belong in standing documentation.

7. **At most one clause of rationale.** Enough that the rule is not arbitrary.

## What this is not

Specificity is not the failure — contingency is. Over-correcting produces vague
documentation, which is worse than a dated example.

Keep all of this:

- **Concrete commands, paths, flags, names.** Precision is the point.
- **Rules particular to this project.** Project docs *should* say what this
  project does; that is not a diary, it is the subject.
- **A worked example a newcomer would actually hit.** Choose it for the reader,
  not because it was nearest.
- **Recorded decisions with reasoning,** where the reasoning still constrains
  what people may do. A decision log is a legitimate genre — just not a
  substitute for the instruction.

The question is never *is this specific?* It is *does this require knowing what
happened?*

## Two tests

**The newcomer test.** Read it as someone joining in a year with no history.
Which sentences would they have to ask about? Those are the diary.

**The decay test.** Which sentences become false in a year with nobody editing
them? Those rot. Rewrite them as conditions rather than states — what makes
something true, not that it currently is.

A sentence failing either test gets rewritten or cut. Cutting is usually right;
a document that says less and stays true beats one that says more and drifts.

## Correcting an existing draft

Rewrite; do not annotate. A note saying a passage is too specific leaves the
passage there.

Work in this order — earlier steps often delete the material later ones would
have fixed:

1. Cut incidents and one-off warnings.
2. Reorder to common case first.
3. Replace borrowed examples with chosen ones.
4. Strip temporal words.
5. Compress rationale.

Then read the result cold. A perennial document is usually shorter than the
diary it replaces, and states more.
