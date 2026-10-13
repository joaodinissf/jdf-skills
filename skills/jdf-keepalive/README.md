# jdf-keepalive

*Keep commit signing working after you walk away.*

Keeps 1Password's SSH agent able to sign git commits while agents work and you
are away. Run from the agent's own session before you leave: it signs once
(unlocking 1Password and approving the key for that app, with your Touch ID if
needed), then posts a harmless zero-distance mouse move every 15 minutes so
1Password's idle auto-lock never fires. It never reads 1Password items or
files.

In a controlled test, signing still worked after 74 minutes with no input and
nudges running; without nudges, 1Password locked on schedule.

Needs the [`jdf-keepalive`](https://github.com/joaodinissf/jdf-suite/tree/main/packages/jdf-keepalive)
tool from jdf-suite, macOS, 1Password's SSH agent for commit signing, and
Accessibility permission for the program that runs it.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s jdf-keepalive
```
