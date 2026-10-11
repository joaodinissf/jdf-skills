# handover

*Leave the next session a map, not a memory.*

Writes a `HANDOVER.md` at the project root so the next session can continue
this one: the goal, what is done (with evidence), what failed and why, the
decisions, the traps, the command that proves the work, and one next step with
a prompt to paste. Every claim is checked against the repository before it is
written; claims that cannot be checked are marked. The file is replaced, not
appended, and stays short.

`/handover resume` reads it back, compares it with what changed since it was
written, and reports the differences before any work starts.

User-invoked only: `/handover [notes]` or `/handover resume`.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s handover
```

## Sources and attribution

The idea and the original section structure come from Zara Zhang's
[`/handover` command](https://x.com/zarazhangrui/status/2020992712825241801)
(February 2026): a "shift-change report" covering what was done, what worked
and what did not, decisions, lessons, next steps and a file map. Her command
text is not public and no licence is stated; this skill was written from the
idea, in new words.

These public skills were read — after a review for prompt injection and unsafe
side effects — for ideas; no text was reused from any of them.

| Skill | Author | Licence | Used for |
|---|---|---|---|
| [claude-code-handoff-skill](https://github.com/ostikwhy-blip/claude-code-handoff-skill) | ostikwhy-blip | MIT | Check claims before writing and mark the rest; a resume mode that reports drift since the recorded commit; sections that are never cut |
| [session-handoff](https://github.com/softaworks/agent-toolkit/tree/main/skills/session-handoff) | softaworks | MIT | A mechanical secret scan of the written file; checking that cited files still exist |
| [claude-code-handover](https://github.com/nrzz/claude-code-handover) | nrzz | MIT | Rewrite instead of append; a size limit; the next step as a prompt to paste, with how to know it is done |
| [create_handoff](https://github.com/humanlayer/humanlayer/blob/main/.claude/commands/create_handoff.md) | humanlayer | Apache-2.0 | A field for the command that verifies the work |
| [claude-handoff](https://github.com/392fyc/claude-handoff) | 392fyc | MIT | One next step, never a menu |

Some of these commit the handover by default, install hooks or edit agent
settings, or run the project's test suite on their own. `handover` does none of
that: it writes one file, never commits it, and runs only read-only git commands.
