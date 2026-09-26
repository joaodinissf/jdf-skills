# Leaving and reporting a model

## Layout

Use the repository's existing convention, or `specs/`:

```
specs/
  README.md             index of questions and models
  checks                runnable checks with expected outcomes
  check.sh              copied from this skill's scripts/check.sh
  <Name>/               TLA+ model, configurations and README.md
  lean/<Name>/          Lean project, Audit.lean and README.md
```

Copy [`../scripts/check.sh`](../scripts/check.sh) when these tool checks fit.
List every expected-failure companion in `checks` with the violation it must
produce (`fail:NeverSends`), so a later edit that blinds the model shows up as
a mismatch. A bare `fail` accepts any violation; use it only when the tool does
not name one. Add replay helpers, regression tests or alternative
configurations only when used. Keep runtime caches, TLC state directories and
downloaded tool binaries out of the repository.

## The model's README

Each model's `README.md` records, in this order:

1. **Question and subject.** What the model should answer; the design or the
   implementation (with commit) it describes.
2. **Properties.** Each with its statement, plain-language meaning, source
   label (intent, inferred, proposed) and citation. Written before the first
   check runs; see "Property changes" below.
3. **Correspondence.** One row per model action or variable:

   | Model element | Source | Abstraction |
   |---|---|---|
   | `Claim(w)` | `worker.ts:47` `claim()` after the await | the write is atomic |
   | `status` | `jobs.status` column | two values of five |

   For a design, the source column cites requirement identifiers or design
   choices, never invented files.
4. **Assumptions.** Numbered (A1, A2, …): scheduling, delivery, crashes,
   isolation levels, remote contracts. Findings and simplifications cite them
   by number.
5. **States and transitions** in prose, with omissions stated.
6. **Checks.** The rerun command, bounds or theorem hypotheses, and the
   expected-failure companions with what each shows.
7. **Findings and open questions**, classified as in SKILL.md §5, with
   constructed scenarios distinguished from observed traces and clean checks
   from unfinished work.

## Property changes

Agents that edit their own success criteria stop finding anything. After the
first check has run, any change to a property's statement, a theorem's
hypotheses, a state constraint, a fairness condition or the bounds is a finding
in its own right: add a line under the property giving the old form, the new
form and the reason, and mention it in the report. Legitimate reasons exist —
an inferred property that misread the intent, a bound too large to finish —
and they are reported, not hidden. Changing a property to make a failing check
pass, without such a reason, is not a result.

## Maintenance

Offer an agent-instructions note about maintaining models with the relevant
code or design; add it only if requested. Do not claim the models stay current
without a maintenance step. The source mapping is what a maintainer uses to
find the model elements a code change affects.

## The report

Lead with the answer to the user's question. Then give:

- **Model:** the boundary, key behaviours and assumptions it makes explicit.
- **Evidence:** checked properties or theorems, configurations, bounds or
  hypotheses, reachability, expected-failure and correspondence results,
  property changes, and unfinished checks.
- **Findings:** design decisions, counterexamples, confirmed implementation
  defects, scoped fixes, simplifications and unresolved candidates, clearly
  distinguished.
- **Limits and reuse:** what is excluded, what the evidence does not establish,
  and where to find and rerun the model.

Tell a counterexample as a story in the domain's terms, one line per step, with
the source location of each step: "worker A reads pending; worker B reads
pending; A claims and sends; B claims and sends". Name the step where the
property breaks.
