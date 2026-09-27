# branch-pruner

*One calm checkout, nothing lost.*

Restores a repository from "branches and worktrees everywhere" to a single calm
checkout. Deletes local branches whose work is already on the default branch —
detecting rebased and cherry-equivalent history, not just true merges, because
`git branch --merged` answers wrongly for a rebase workflow. Removes all extra
worktrees when clean, even for unmerged branches; the refs and commits survive
in the main repository. Anything dirty is a hard stop and a per-item question.

Work that landed needs no branch to survive; uncommitted work git cannot bring
back.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s branch-pruner
```
