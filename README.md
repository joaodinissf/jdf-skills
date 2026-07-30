# jdf-skills

Agent skills for keeping a codebase honest.

Each one goes after writing that costs a reader more than it gives: code that
says something untrue, documentation that only made sense the week it was
written, comments that repay nobody for re-reading them.

## Install

```sh
npx skills add joaodinissf/jdf-skills --all      # everything
npx skills add joaodinissf/jdf-skills --list     # see what's here
npx skills add joaodinissf/jdf-skills -s <name>  # just one
```

## Skills

### [`silly-sweep`](skills/silly-sweep) — sweep the silly away

Finds code that **misleads**: a comment describing behaviour that was removed, a
guard that cannot detect what it guards against, a test that passes with the
implementation deleted. Ten categories, ranked by how confidently a reader would
be misled. Fans out read-only agents by area and returns ranked findings.

Not ugly code, not slow code — only code that tells a reader something untrue.

### [`perennial-docs`](skills/perennial-docs) — write the destination, not the path

Finds documentation written as a record of the work that produced it: examples
taken from the last thing touched, warnings about obstacles hit once, ordering
that follows how the work happened. Such a document is usually accurate the day
it is written, which is why it survives review, and useless a year later.

General patterns last. Episodes rot.

### [`comment-diet`](skills/comment-diet) — keep only what is load-bearing

Cuts comments back to the ones that earn their place. A comment is load-bearing
when removing it would let a competent reader make a wrong change; everything
else is decoration, however true. Judges that per comment as its own pass, then
routes what fails — a rejected alternative belongs in the pull request, a reason
for the change belongs in the commit message, neither belongs in the file.

The constraints survive; the argument that produced them does not.

## Design notes

All three are language- and framework-agnostic on purpose. Nothing in any of
them names a version, a toolchain or a vendor, so none needs revisiting when
those change.

They are also written to fail quietly rather than loudly: an empty result is a
valid answer, and each says so explicitly. A skill that must find something will
invent something.

## Licence

MIT
