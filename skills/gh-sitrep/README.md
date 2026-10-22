# gh-sitrep

*A few numbers you can keep an eye on, and the short list behind them.*

Reports everything on GitHub that waits on you:
- **Pull requests:** reviews requested of you; pull requests you opened and
  haven't landed, split into your own repositories and other people's; bot pull
  requests (Dependabot, Renovate) in repositories you own.
- **Issues:** assigned to you, mentioning you, or untriaged in your
  repositories.
- **Security alerts:** Dependabot, code scanning and secret scanning, counted
  by severity.
- **Other:** default branches whose CI is red, deployments waiting for
  approval, pending invitations and the notifications you're participating in.

The report gives a headline count per bucket, a breakdown by repository and the
short list that needs a decision. It ends with a bookmarkable search link for
each bucket, so you can check again without the tool.

It is read-only. It suggests what to close, rebase, triage or land, and does
none of it.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s gh-sitrep
```
