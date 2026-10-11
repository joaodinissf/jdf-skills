---
name: skill-browser
description: Browse and load skills from the user's skill library, which agents do not discover on their own. Use only when the user asks to consult, list, search, browse or use their skills or a named skill from the library; never on your own initiative.
---

# Skill browser

*Skills on request, not by surprise.*

The user keeps their skills in a library that clients do not load on their
own. This skill is the only way in. It lists what is there and loads the one
the user picks. It never picks one for them.

## Where the library is

The `library/` folder next to this file. Each skill is a folder with a
`SKILL.dormant.md` file: a normal skill file, renamed so that no client
discovers it. `manifest.txt` next to this file says where each skill came from.

Resolve the real path of this file first (it is usually reached through a
link), for example with `realpath`, and work from there.

## List or search

When the user asks what is available, or for a skill that does X:

1. Read only the frontmatter (`name`, `description`) of each
   `library/*/SKILL.dormant.md`, for example with
   `head -12 library/*/SKILL.dormant.md`. Do not read whole files to list them.
2. Show a short table: name and a one-line summary. When the user searched,
   show the matches first and say why each matches.
3. Stop. Do not load anything until the user picks a skill.

## Load

When the user names a skill, or picks one from the list:

1. Read `library/<name>/SKILL.dormant.md` in full.
2. Follow it as if the client had loaded it, with these differences:
   - **Paths.** Resolve every relative path in it (`references/`, `scripts/`,
     templates) against `library/<name>/`, not against the working directory.
   - **Restrictions.** If its frontmatter has `allowed-tools`, use only those
     tools while following it. The client does not enforce this for a skill
     loaded by hand, so you must.
   - **Arguments.** Where it uses `$ARGUMENTS`, use what the user said with the
     request.
3. Say in one line which skill you loaded, then do what it says.

If no folder has that name, list the closest names and ask. Never load a skill
the user did not choose, and never load more than one without asking.

## Rules

- **On request only.** Do not mention, suggest or load library skills unless
  the user asks.
- **Read-only.** Do not edit, add or remove anything in the library. It is
  filled by a sync tool; changes there are overwritten.
