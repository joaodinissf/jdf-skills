# OAuth 2.0 / OIDC native-client review checklist

A checklist for reviewing a hand-written OAuth 2.0 / OpenID Connect **client** in a
**native desktop application** (for example an Eclipse plugin) that uses the
authorization code flow with PKCE and a **loopback redirect**.

It is meant to be handed to a code reviewer, human or agent. It covers the client
only: not authorization servers, and not resource servers that validate tokens.

Citations were checked against the RFC texts. MUST / SHOULD in an item reflects
the spec's own strength; "hardening" marks advice that goes beyond the specs.

## How to use it

- Go through every section. For each item, report one of: **pass** (point to the
  code), **fail** (point to the code, give a concrete failure scenario), or
  **n/a** (say why, for example "no OIDC, so no ID token").
- Rank failures by severity:
  - **Critical**: token or code theft, login CSRF, accepting forged tokens.
  - **High**: tokens persisted or logged in plain text, missing validation that
    a spec makes mandatory.
  - **Medium**: robustness (timeouts, error handling, refresh races).
  - **Low**: hygiene and UX.
- Prefer citing the spec section next to each failure.
- A missing **negative test** for a security check is a finding in its own right.

## 1. Authorization request

- [ ] The request opens in the **system browser**, not an embedded web view
  (no SWT `Browser`, JavaFX `WebView` or similar). RFC 8252 §8.12.
- [ ] PKCE with **S256 only**; `plain` is never sent or accepted as a fallback.
  `code_challenge_method=S256` is sent explicitly, because omitting it means
  `plain`. RFC 7636 §4.2, §4.3, §7.2; RFC 8252 §6; RFC 9700 §2.1.1.
- [ ] The code verifier has 43–128 characters from the unreserved set, generated
  with `SecureRandom` (32 random bytes, base64url without padding, is typical).
  RFC 7636 §4.1, §7.1.
- [ ] A fresh `code_verifier` (and `nonce`) is generated for each login attempt
  and stored only with that attempt. Never constant, never reused.
  RFC 9700 §2.1.1; RFC 7636 §4.1.
- [ ] `state` is random, bound to this one login attempt, single use, and checked
  on the callback before anything else happens. Missing or mismatched state
  aborts the flow. RFC 6749 §10.12; RFC 9700 §2.1, §4.7.1; RFC 8252 §8.9.
- [ ] If OIDC is used: a random `nonce` is sent and stored with the attempt.
  OIDC Core §3.1.2.1.
- [ ] No resource owner password grant (MUST NOT, RFC 9700 §2.4). No implicit or
  other response types that return tokens from the authorization endpoint
  (SHOULD NOT, RFC 9700 §2.1.2; NOT RECOMMENDED for native apps, RFC 8252 §8.2).
- [ ] Requested scopes are the minimum the feature needs. RFC 6749 §10.3.
- [ ] If the client talks to more than one resource server, it sends
  `resource` on the authorization and token requests: an absolute URI without a
  fragment (MUST), the base URI of the API. The same value is used for the
  protected resource metadata check (section 3), and `invalid_target` is
  handled. RFC 8707 §2; RFC 9728 §7.4. (MCP clients: check the MCP
  authorization spec, which may require `resource` unconditionally.)
- [ ] The authorization endpoint URL comes from validated configuration or
  discovery (section 3), never from user-editable input without validation.

## 2. Loopback receiver

- [ ] Binds to the loopback IP literal `127.0.0.1` (or `[::1]`), **not** `localhost`
  and **not** `0.0.0.0` / all interfaces. RFC 8252 §7.3, §8.3.
- [ ] Tries both `127.0.0.1` and `[::1]` and uses whichever is available; a
  machine without one IP version can still log in. RFC 8252 §7.3 (SHOULD).
- [ ] Uses an ephemeral port chosen at runtime, and the `redirect_uri` sent
  contains that exact port. RFC 8252 §7.3.
- [ ] The redirect URI in the token request is byte-for-byte identical to the one
  in the authorization request. RFC 6749 §4.1.3.
- [ ] Accepts only the expected path and method; ignores other requests (for
  example `/favicon.ico`) without ending the flow. RFC 8252 §8.10.
- [ ] Callback parameters (`state`, `code`, `iss`, `error`,
  `error_description`) are length-limited and validated before use, and escaped
  wherever they are logged or shown (browser page, IDE dialogs).
  RFC 6749 §10.14.
- [ ] Unknown parameters in the callback are ignored (MUST, RFC 6749 §4.1.2). A
  callback with a repeated `code`, `state` or `iss` is rejected (hardening).
- [ ] Handles `error` / `error_description` in the callback, and user cancellation
  (the browser tab closed: no callback ever arrives).
- [ ] Has a timeout, and shuts down after the first valid callback or on timeout
  or cancellation. The port is not left open. RFC 8252 §8.3.
- [ ] The response page shown in the browser echoes nothing from the request
  (no code, no state, no error text reflected without escaping) and does not
  redirect anywhere based on request input. RFC 9700 §4.11.1.
- [ ] The response page loads no third-party resources or external links, and
  sends `Referrer-Policy: no-referrer`. RFC 9700 §4.2.4.
- [ ] Runs off the UI thread, with cancellation wired to the UI (for example an
  `IProgressMonitor`).
- [ ] **Mix-up defence.** Required when more than one authorization server can
  be configured (RFC 9700 §2.1); a single-AS client is exempt but should be
  ready for it:
  - [ ] The expected issuer is stored with each login attempt.
  - [ ] If the AS supports RFC 9207 (metadata
    `authorization_response_iss_parameter_supported: true`), `iss` is
    **required** in the callback: it is form-decoded and compared with the
    stored issuer by simple string comparison, and a mismatch or a missing `iss`
    aborts the flow. RFC 9207 §2.4.
  - [ ] The `iss` check also runs on error callbacks: an error whose `iss` is
    missing or mismatched is not trusted as coming from the intended AS.
    RFC 9207 §2.4.
  - [ ] Otherwise, each AS gets its own redirect path, and the callback is
    checked to have arrived on the redirect URI stored with the attempt.
    RFC 9700 §4.4.2.2; RFC 8252 §8.10.

## 3. Discovery and configuration

- [ ] Metadata is fetched over HTTPS with normal certificate validation (no
  trust-all `TrustManager` or `HostnameVerifier`). RFC 8414 §6.1, §6.2;
  RFC 9728 §7.3.
- [ ] The metadata URL is derived from the issuer with any trailing `/` removed:
  `/.well-known/oauth-authorization-server` is inserted between host and path
  (RFC 8414 §3.1); `/.well-known/openid-configuration` is appended to the issuer
  (OIDC Discovery §4.1). Tested with an issuer that has a path.
- [ ] The `issuer` in the metadata equals the configured issuer exactly
  (simple string comparison). RFC 8414 §3.3, §4; OIDC Discovery §4.3.
- [ ] If protected resource metadata is used (RFC 9728): the `resource` value
  matches the resource that was asked for (RFC 9728 §3.3), and the listed
  authorization server is one the user or configuration trusts. Following a
  server-supplied pointer to an arbitrary authorization server is a finding
  (reviewer guidance; RFC 9728 §7.6 leaves the trust decision to the client).
- [ ] A failed issuer or `resource` check aborts the login. Nothing from the
  rejected document (endpoints, `jwks_uri`) is used or cached. RFC 8414 §3.3;
  RFC 9728 §3.3; OIDC Discovery §4.3.
- [ ] Configured servers have unique issuer identifiers; two configurations
  cannot share an issuer. RFC 9207 §4.
- [ ] A new `resource_metadata` challenge (in a 401) triggers a re-fetch and
  re-validation of the protected resource metadata, and newly listed
  `authorization_servers` go through the same trust check. RFC 9728 §5.2.
- [ ] Endpoint URLs taken from metadata are HTTPS (loopback excepted for tests).
- [ ] Metadata is cached sensibly and refetched on failure, not on every
  request. RFC 9728 §7.10.
- [ ] Unknown or extra metadata fields are ignored, not treated as errors.
  RFC 9728 §3.2.

## 4. Token request and response

- [ ] Every request that carries a code, token or credential (token, refresh,
  revocation, resource calls) uses HTTPS with certificate and hostname
  validation; connect and read timeouts are set. RFC 6750 §5.2, §5.3;
  RFC 7009 §5.
- [ ] Token and refresh requests are `POST` with an
  `application/x-www-form-urlencoded` UTF-8 body. No secret or token appears in
  a URL. RFC 6749 §3.2, §4.1.3, §6.
- [ ] A public client includes `client_id` in the token request.
  RFC 6749 §3.2.1, §4.1.3.
- [ ] The `code_verifier` is sent (RFC 7636 §4.5); the code is used once and
  then discarded (RFC 6749 §4.1.2).
- [ ] Client authentication, if a secret exists, is encoded correctly: for
  `client_secret_basic`, client ID and secret are form-URL-encoded **before**
  Base64. RFC 6749 §2.3.1. (A native public client usually has no secret; a
  secret embedded in a distributed binary is not a secret. RFC 8252 §8.5.)
- [ ] Error responses are parsed (`error`, `error_description`) for any 4xx,
  not just "status != 200". RFC 6749 §5.2.
- [ ] Unknown parameters in the token response are ignored. RFC 6749 §5.1.
- [ ] The response is checked: `token_type` is `Bearer` (case-insensitive) or
  another type the client actually supports. RFC 6749 §5.1, §7.1.
- [ ] A missing `expires_in` is handled with a sensible default, not a crash or
  "never expires". RFC 6749 §5.1.
- [ ] The granted `scope`, if returned, is compared with what was requested; a
  reduced grant is handled. RFC 6749 §3.3, §5.1.

## 5. ID token (only if OIDC is used)

- [ ] The signature is verified against the provider's JWKS, with an explicit
  algorithm allowlist (reject `none`; never verify an RS/ES-signed token with a
  key used as an HMAC secret). RFC 8725 §3.1, §3.2.
- [ ] Keys come only from the validated issuer's `jwks_uri`. The `jku`, `x5u`
  and embedded `jwk` headers are never used to find a key. OIDC Core §3.1.3.7;
  RFC 8725 §3.8, §3.10.
- [ ] `kid` lookup with key rotation: on an unknown `kid`, refetch the JWKS once
  (rate-limited), then fail. OIDC Core §10.1.1.
- [ ] Claim checks, OIDC Core §3.1.3.7:
  - `iss` equals the issuer;
  - `aud` contains the client ID, and no additional audience the client does
    not trust;
  - if `azp` is present, it equals the client ID;
  - `exp` is in the future (small clock skew allowed);
  - `iat` is sanity-checked if the client defines a window (optional);
  - if a nonce was sent, the `nonce` claim is present and equals the stored
    value.
- [ ] If `max_age` was sent or `auth_time` requested, `auth_time` is present and
  checked, and the client re-authenticates if it is too old.
  OIDC Core §3.1.3.7 (SHOULD).
- [ ] Alternatively, a **documented** decision to rely on TLS for an ID token
  received directly from the token endpoint (allowed by OIDC Core §3.1.3.7),
  with the claim checks still done.
- [ ] If UserInfo is used, its `sub` equals the ID token `sub`; otherwise the
  UserInfo response is discarded. OIDC Core §5.3.2.
- [ ] The user is identified by `(iss, sub)`, never by `email` alone.
  OIDC Core §5.7.

## 6. Token storage

- [ ] Access and refresh tokens are stored only in the platform's secure storage
  (for Eclipse, `ISecurePreferences` with encryption enabled), never in
  ordinary preferences, files, or system properties. RFC 6749 §10.4;
  RFC 6750 §5.3.
- [ ] Check what the secure storage does on each target platform: whether it is
  backed by the OS keychain or a password provider, and what happens when that
  provider is unavailable (it must fail, not silently store in plain text).
- [ ] Tokens never appear in logs, exception messages, error dialogs, `toString()`
  output, or telemetry. Check the exception class and any debug logging.
- [ ] Storage is keyed per account and per issuer, so two configured servers
  cannot read each other's tokens.

## 7. Using tokens

- [ ] Access tokens are sent only in the `Authorization: Bearer` header, one
  method per request, never in a query string. RFC 6750 §2, §2.1;
  RFC 9700 §4.3.2 (MUST NOT in the query).

## 8. Token lifecycle

- [ ] Refresh happens before expiry (with a margin) or on a 401, not both racing.
- [ ] Concurrent refreshes are serialized: one refresh in flight; other callers
  wait for its result.
- [ ] If the server rotates refresh tokens, the new one is persisted
  **before** the old one is discarded; a crash between the two must not lose the
  session. RFC 6749 §6.
- [ ] `invalid_grant` on refresh clears stored tokens and starts a clean
  re-authentication. It does not loop. RFC 6749 §5.2.
- [ ] Disconnect or logout deletes stored tokens and, if the server supports it,
  revokes them. RFC 7009.
- [ ] Revocation, if used: a form-encoded `POST` with `token` (and `client_id`
  for a public client) to the `revocation_endpoint` from validated metadata,
  over HTTPS. On 503 the token is treated as still valid and the call is retried
  later; on `unsupported_token_type` the refresh token is revoked instead. Local
  deletion happens in every case. RFC 7009 §2, §2.1, §2.2.1.
- [ ] Changing the server or client configuration invalidates tokens obtained
  under the old configuration.

## 9. Tests

For each security check above, there is a test that **fails** when the check is
removed. At minimum:

- [ ] State mismatch, missing state, replayed state.
- [ ] Callback with `error`, callback timeout, user cancellation.
- [ ] Callback with repeated `code` / `state`; callback with unknown extra
  parameters (ignored); nothing from the callback reflected unescaped.
- [ ] Mix-up: missing `iss` when the AS advertises support, mismatched `iss`,
  error callback with a mismatched `iss`.
- [ ] Authorization request: `code_challenge_method=S256` present; a different
  verifier, state and nonce on each attempt; `resource` sent where required.
- [ ] Discovery: issuer mismatch, issuer with a path (correct well-known URL),
  rejected metadata not cached or used afterwards.
- [ ] Token request shape: form-encoded `POST`, `client_id` present, nothing
  sensitive in the URL.
- [ ] Token endpoint error response (for example `invalid_grant`,
  `invalid_target`).
- [ ] If OIDC: bad signature, `alg: none`, wrong `aud`, an untrusted extra
  `aud`, `azp` not equal to the client ID, wrong `iss`, expired token, wrong
  `nonce`, missing `nonce` claim when one was sent, unknown `kid`, a `jku`
  header pointing elsewhere (ignored).
- [ ] Resource calls: token only in the `Authorization` header.
- [ ] Refresh: concurrent callers, rotation, `invalid_grant`.
- [ ] Revocation: 503 and `unsupported_token_type` handling; local tokens
  deleted in every case.
- [ ] Nothing secret in logged output (assert on captured logs).

Tests that only cover the happy path are a finding.

## 10. Library question

If more than a few items in sections 1–5 fail, recommend replacing the
hand-written protocol code with a maintained library (for Java, for example the
Nimbus OAuth 2.0 SDK with OpenID Connect extensions) and keeping only the
application glue (receiver, storage, UI, lifecycle). Library or not, sections
2, 6, 7, 8 and 9 stay the application's responsibility.

## References

- [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700): OAuth 2.0 Security Best Current Practice
- [RFC 8252](https://www.rfc-editor.org/rfc/rfc8252): OAuth 2.0 for Native Apps
- [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636): PKCE
- [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749): OAuth 2.0
- [RFC 6750](https://www.rfc-editor.org/rfc/rfc6750): Bearer Token Usage
- [RFC 8414](https://www.rfc-editor.org/rfc/rfc8414): Authorization Server Metadata
- [RFC 9728](https://www.rfc-editor.org/rfc/rfc9728): Protected Resource Metadata
- [RFC 9207](https://www.rfc-editor.org/rfc/rfc9207): Authorization Server Issuer Identification
- [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707): Resource Indicators
- [RFC 7009](https://www.rfc-editor.org/rfc/rfc7009): Token Revocation
- [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725): JWT Best Current Practices
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html), §3.1.3.7 ID Token Validation
- [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html)
