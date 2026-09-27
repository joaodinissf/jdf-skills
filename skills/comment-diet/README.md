# comment-diet

*Keep only what is load-bearing.*

Cuts comments back to the ones that earn their place. A comment is load-bearing
when removing it would let a competent reader make a wrong change; everything
else is decoration, however true. Judges that per comment as its own pass, then
routes what fails — a rejected alternative belongs in the pull request, a reason
for the change belongs in the commit message, neither belongs in the file.

The constraints survive; the argument that produced them does not.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s comment-diet
```
