---
name: jdf-keepalive
description: Keep 1Password's SSH agent able to sign git commits while the user is away from the Mac. Run it from the session that will make the signed commits, before the user leaves, while they can still approve a 1Password prompt. Use when the user says they are stepping away, leaving or going to sleep while work continues, or invokes /jdf-keepalive. Only for SSH commit signing; never for reading 1Password items.
---

# jdf-keepalive

*Keep commit signing working after the user walks away.*

Commits are signed with an SSH key held by 1Password. Two things block that
when the user is away:

- **Idle auto-lock.** 1Password locks after a period without keyboard, mouse
  or trackpad input. Signing does not count as input.
- **Per-app approval.** The SSH agent asks the user to approve each app once
  per unlock. An app signing for the first time since the last unlock waits on
  a prompt nobody can answer.

`jdf-keepalive start` handles both. It signs a dummy message with git's
signing key, which unlocks 1Password if needed and approves the key for *this*
session's app. It then posts a zero-distance synthetic mouse move every 15
minutes, so the idle lock never fires. A controlled test confirmed it: with
nudges, signing still worked after 74 minutes without input; without them,
1Password locked.

## When to run it

**Before the user leaves**, from the session that will make the signed
commits. The approval belongs to the app that asks for it, and the first
signature may need the user's Touch ID. Nudges only keep an unlock alive; they
cannot create one. Once the screen or 1Password has locked, nothing can be done
until the user is back.

## How

```sh
TOOL=~/Git/jdf/jdf-suite/packages/jdf-keepalive/jdf-keepalive
$TOOL start [duration=4h] [interval=15m]   # check, sign once, then nudge in the background
$TOOL status                               # loop, idle time, screen, display, permission
$TOOL stop
```

1. Tell the user a 1Password prompt may appear, and ask them to approve it.
   Tell them **not** to tick "Approve for all applications": approving only
   this app is the narrower grant.
2. Run `start` with a duration that covers the task, with some margin. The
   tool caps it at 8h.
3. If it aborts, relay its message and stop. Do not retry until the user says
   they are ready. The messages mean:
   - *no Accessibility permission* — macOS has not allowed the program running
     the tool to post input. The user grants it in System Settings → Privacy &
     Security. For Claude Code the program is the versioned `claude` binary,
     so the grant is likely lost after each Claude Code update.
   - *the screen is locked* — too late; the user has to unlock the Mac.
   - *1Password did not sign within 90 s* — locked or awaiting approval, with
     nobody there to approve.
4. If another loop is already running, `start` still signs (approving this
   app) and leaves that loop alone. That is the expected result.
5. When the task ends and nothing else needs signing, run `stop`.

## Limits

- Never read, list or change 1Password items, never call `op`, and never read
  1Password's own files. The tool needs only the SSH signature.
- "Lock when device locks or sleeps" still applies. If the display sleeps or
  the screen locks, 1Password locks anyway. Nudges every 15 minutes are
  shorter than a typical display-sleep timer; that they prevent display sleep
  has not been tested.
- Synthetic input keeps the whole Mac looking active, not only 1Password.
  Tell the user so on the first run in a session.
