---
name: security-checklists
description: Review security-sensitive code against a spec-checked checklist, item by item, reporting pass, fail or n/a with a pointer to the code and a severity for every failure. Covers OAuth 2.0 / OpenID Connect native clients (PKCE, loopback redirect, discovery, ID tokens, token storage) and OAuth 2.0 authorization and resource servers (registration, redirect matching, PKCE, codes, client authentication, token validation, refresh, revocation, metadata). Use when asked to review, audit or check an OAuth or OIDC implementation, or to hand a reviewer a checklist for one.
---

# Security checklists

*Check every item, cite the spec, prove it with a test.*

Hand-written security code fails in the details a happy-path test never
reaches. Each checklist here lists those details, with the spec section that
makes each one a requirement. The citations were checked against the RFC texts,
so MUST, SHOULD and "hardening" in an item mean what they say.

## Pick the checklist

| Code under review | Checklist |
|---|---|
| A native or desktop OAuth / OIDC client: authorization code, PKCE, loopback redirect | [references/oauth-native-client.md](references/oauth-native-client.md) |
| An OAuth authorization server, or a resource server that accepts its tokens | [references/oauth-server.md](references/oauth-server.md) |

If the code does both (for example an MCP server that is its own authorization
server and also calls other APIs), use both. If no checklist fits, say so; do
not stretch one to cover a different role.

Read the chosen checklist in full before looking at the code.

## Review

1. Find the code for each section first: the files and classes that implement
   it. A section with no code is a finding or an n/a, never a silent skip.
2. Go through every item. Report one of:
   - **pass**: point to the code that does it;
   - **fail**: point to the code, give a concrete failure scenario, cite the
     spec section from the item;
   - **n/a**: say why (for example "no OIDC, so no ID token").
3. Check the tests section the same way. For each security check that passes,
   find the test that would fail if the check were removed. A missing negative
   test is a finding in its own right.
4. Rank failures with the severity scale at the top of the checklist.

Report failures first, most severe first, then the n/a items with their
reasons, then a one-line count of passes. Do not list every pass unless asked.

## Rules

- **The spec's strength, not yours.** Do not report a SHOULD as a MUST, or
  local hardening as a spec violation. Say which it is.
- **Read the code, not the names.** A method called `validateIssuer` that only
  checks for null is a fail.
- **No fixes unless asked.** The output is the review. Propose a fix per
  failure in one or two lines; change code only when the user asks.
