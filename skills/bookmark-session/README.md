# bookmark-session

*A pointer to the work, filed where you will see it.*

Saves the current Claude Code session as one Things 3 inbox to-do: the folder,
branch and working-tree state, what is done and pending, one next step, and the
exact `claude --resume` command. It takes the session ID from
`CLAUDE_CODE_SESSION_ID` and never guesses it from transcript files, which
picks the wrong session when several are open.

Needs [Things 3](https://culturedcode.com/things/) and a Things MCP server that
provides `add_todo`.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s bookmark-session
```

## Sources and attribution

Written from scratch. Two public skills were read for ideas; no text was reused.

| Skill | Author | Licence | Used for |
|---|---|---|---|
| [continue-claude-code-work](https://github.com/daymade/claude-code-skills/tree/main/daymade-claude-code/continue-claude-code-work) | daymade | MIT | Stop rather than guess when the session's identity is unclear |
| [session-management](https://github.com/athola/claude-night-market/tree/master/plugins/sanctum/skills/session-management) | athola | MIT | `/rename` and `claude --resume <name>` as the fallback |
