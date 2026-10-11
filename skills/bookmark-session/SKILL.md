---
name: bookmark-session
description: Save a pointer to the current Claude Code session as a Things 3 inbox to-do, so the user can find and resume it later. The to-do holds the folder, branch, state, next step and the exact resume command. Use when the user asks to bookmark, park, stash or save the session for later, or invokes /bookmark-session.
argument-hint: "[focus or note]"
allowed-tools:
  - Bash
  - mcp__things__add_todo
---

# Bookmark session

*A pointer to the work, filed where you will see it.*

Creates one Things 3 inbox to-do that points back to this session: where it
ran, what state it left, the next step, and the command that reopens it. It is
a pointer, not an archive. For a full write-up in the repository, use
`handover`.

Needs the Things 3 app and a Things MCP server that provides `add_todo`.

## 1. Collect the state

Run only these commands, and skip those that do not apply:

- `pwd`
- `git rev-parse --show-toplevel`, `git branch --show-current`
- `git log --oneline -3`, `git status --short`
- `printenv CLAUDE_CODE_SESSION_ID`

The session ID is what `claude --resume <id>` needs. Use it only from
`CLAUDE_CODE_SESSION_ID`, or from a transcript path this conversation already
shows (for example in a compaction summary). If neither gives one, leave it
out and tell the user that `/rename <name>` followed by `claude --resume
<name>` is the fallback. **Never guess** the ID, for example from the newest
transcript file: with several sessions open, the newest one is often another
session.

## 2. Summarise from the conversation

Work from the conversation; do not re-read files to be thorough:

- what this session was doing, in one to three sentences;
- what is done, concretely: commits, files, PRs;
- what is pending or blocked;
- the one next step: a command, a file to edit, a PR to open.

If the session covered two unrelated pieces of work, ask which one to bookmark,
or whether to create two to-dos.

## 3. Create the to-do

Call `mcp__things__add_todo` without a `when` value, so the to-do lands in the
Inbox. (`when: "anytime"` would file it under Anytime instead.)

Title: `[CLAUDE] <verb> <thing>`, under about 80 characters. For example:
`[CLAUDE] Resume: open PR for the bedrock pricing fix`.

Notes, in this shape; omit lines and sections that do not apply:

```
Resume: cd <folder> && claude --resume <session id>
Folder: <absolute path>
Repo: <repo root> · Branch: <branch>
Last commit: <short sha> <subject>
Working tree: <clean | summary>

Context:
<one to three sentences>

Done:
- <item>

Pending:
- <item, or "none">

Next step:
<one concrete action>

Links:
- <issue, PR or doc URLs from this session>
```

If the user gave a note with the command, work it into Context and Next step
instead of pasting it at the end.

## 4. Confirm

One line: `Bookmarked in Things: <title>`.

## Rules

- **The folder is required.** Without an absolute path, the to-do cannot be
  resumed.
- **No secrets** in the title or notes: no tokens, keys, `.env` contents or URLs
  that carry credentials. Write `[redacted]` if the context needs it.
- **Be specific.** "Continue refactoring" cannot be resumed; "open a draft PR
  for branch `fix/foo`" can.
