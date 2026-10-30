# security-checklists

*Check every item, cite the spec, prove it with a test.*

Reviews security-sensitive code against a checklist whose citations were
checked against the RFC texts. Every item gets pass, fail or n/a, every failure
gets a pointer to the code, a concrete scenario and a severity, and every
security check needs a test that fails without it.

Checklists:

- **OAuth 2.0 / OIDC native client**: system browser, PKCE, loopback receiver,
  mix-up defence, discovery, token requests, ID token validation, secure
  storage, refresh and revocation.
- **OAuth 2.0 authorization and resource server**: consent, client
  registration (including dynamic registration and client ID metadata
  documents), redirect URI matching, PKCE, single-use codes, client
  authentication, access token validation, DPoP and mTLS, audience binding,
  refresh rotation, revocation, metadata, storage and logging.

## Install

```sh
npx skills add joaodinissf/jdf-skills -s security-checklists
```
