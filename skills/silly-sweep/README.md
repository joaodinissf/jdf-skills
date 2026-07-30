<h1 align="center">silly-sweep</h1>

<p align="center"><em>Sweep the silly away.</em></p>

---

An agent skill that sweeps a codebase for code that **misleads** — and only that.

Not ugly code. Not slow code. Code that tells a reader something untrue: a comment
describing behaviour that was removed, a guard that cannot detect the thing it
guards against, a test that passes with the implementation deleted. These cost more
than bugs, because a bug is eventually observed and this is believed.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s silly-sweep
```

Then ask your agent to sweep the repo, or invoke it directly:

```
/silly-sweep
```

## What it looks for

Ten categories, ranked by how confidently a reader would be misled:

| | |
|---|---|
| **Reimplemented standard library** | A hand-rolled loop doing what the language ships |
| **Comment contradicts code** | The comment describes what the code used to do |
| **A check that cannot fail** | A guard that passes regardless of the condition it names |
| **A test that does not discriminate** | It passes with the implementation removed |
| **Loudness undone at a boundary** | Returns an error; the caller logs and continues |
| **Nondeterministic selection** | Picking from an unordered collection as if it were stable |
| **Dead weight** | Written but never read, exported with no caller |
| **Drifted duplication** | Copies that no longer agree — the divergence is the finding |
| **Misleading name** | A validator that mutates, a getter that writes |
| **Absurd construct** | A lock guarding nothing, branches that are identical |

Language-agnostic by design. Nothing here names a tool, framework or version, so
it does not rot.

## How it works

It discovers the repo's layout, partitions it into 6–10 areas, and fans out one
read-only agent per area in parallel — then ranks and de-duplicates the findings.

It uses small fast models deliberately. This is pattern-matching over a lot of
text, not deep reasoning, and coverage matters more than depth.

## What it will not do

- Run your build or test suite. It reads.
- Report style preferences. That is your linter's job.
- Pad. An empty result is a valid answer, and the skill says so explicitly.

## Calibration

The skill carries three hard-won rules, each from a real failure:

**Verify claims about external things.** The most dangerous finding is one that
calls correct code broken, because acting on it breaks something that worked. A
sweep once declared a package-manager formula "invalid syntax" and claimed every
build using it would fail — the line was the framework's documented idiom. Any
claim resting on a framework's conventions must be checked against that framework,
or downgraded to a question.

**Budget hard.** A sweep without an explicit tool-call ceiling will grind for hours
and return nothing. Ask for 15 calls and an answer, not exhaustiveness.

**Use long flags.** `rg -r` is `--replace` and `-E` is `--encoding`. A pattern like
`rg -ril foo` silently rewrites every match and looks like a result. A mangled grep
does not fail — it invents a finding.

## Licence

MIT
