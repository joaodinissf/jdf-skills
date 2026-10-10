# para-tidy

*Every file where you will look for it; nothing lost on the way.*

Roasts and tidies a personal file tree with the PARA method — Projects, Areas,
Resources, Archive. The roast is read-only: an inventory, a candid list of what
costs you time, and a proposed target structure. The tidy runs only after you
approve, one folder at a time, from a manifest that has passed a dry run: no
overwrites, no permanent deletes (removal means the Trash, per item), an undo
log, and file counts reconciled before and after.

It reads a house-rules file at the root of the tree (`AGENTS.md`) if there is
one, and offers to record the decisions you make so they are made once.

File by the area a thing serves; get every other view from search.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s para-tidy
```

## Sources and attribution

Written from scratch. The method is Tiago Forte's
[PARA](https://fortelabs.com/blog/para/). These public skills were read — after
an adversarial review for prompt injection and unsafe file operations — for
ideas and for the failure modes to avoid; no text was reused from any of them.

| Skill | Author | Licence | Used for |
|---|---|---|---|
| [para-second-brain](https://github.com/robdefeo/agent-skills/tree/main/skills/para-second-brain) | robdefeo | none stated | Ideas only: the three-question filing order, the completion test for projects, most-actionable-wins tie-break |
| [file-organizer](https://github.com/ComposioHQ/awesome-claude-skills/tree/master/file-organizer) | ComposioHQ | none stated | Ideas only: scope one folder at a time, plan before changes |
| [file-organizer](https://github.com/claude-office-skills/skills/tree/main/file-organizer) | claude-office-skills | MIT | Ideas: date-first naming, a shallow-depth limit |
| [knowledge-ops](https://github.com/affaan-m/ecc/tree/main/skills/knowledge-ops) | affaan-m | MIT | Ideas: one canonical home per thing, deduplicate before storing |
| [second-brain-lint](https://github.com/nicholasspisak/second-brain/tree/main/skills/second-brain-lint) | nicholasspisak | none stated | Ideas only: a read-only health check with errors, warnings and info |
| [recipe-organize-drive-folder](https://github.com/googleworkspace/cli/tree/main/skills/recipe-organize-drive-folder) | Google Workspace | Apache-2.0 | The trap that a cloud "move" can orphan a file |

Several of these skills delete duplicates or installers automatically, move
without an overwrite check, start from the whole home folder, or install tools
and write agent configuration as a side effect. `para-tidy` does none of that;
its Traps section says why.
