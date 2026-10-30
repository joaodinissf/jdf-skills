# OAuth 2.0 authorization server and resource server review checklist

A checklist for reviewing an OAuth 2.0 **authorization server** (AS) and the
**resource server** (RS) that accepts its tokens. It is independent of stack and
language. It is the server-side companion to the native-client checklist.

It is meant to be handed to a code reviewer, human or agent. It does not cover how
the AS authenticates the end user (passwords, MFA, upstream identity providers),
except where that touches the OAuth flow.

Citations were checked against the RFC texts. MUST / SHOULD in an item reflects
the spec's own strength; "hardening" or "local policy" marks advice that goes
beyond the specs. Items on the Client ID Metadata Document draft were checked
against draft -02, and MCP items against the MCP 2025-11-25 authorization spec;
recheck them if your deployment follows a later revision.

## How to use it

- **Write the profile first**, in two or three lines: client types (public,
  confidential), how clients register (static, dynamic registration, client ID
  metadata documents), token format (JWT or opaque), and where the RS gets its
  answers (JWT validation, introspection, a shared database). Use it to mark
  whole blocks n/a up front, for example "public clients only, no DCR, opaque
  tokens" rules out most of §6 client authentication, the JWT block in §7, the
  DCR block in §2 and the secret and key storage items in §13.
- Go through every section. For each item, report one of: **pass** (point to the
  code), **fail** (point to the code, give a concrete failure scenario), or
  **n/a** (say why, for example "no dynamic registration").
- Rank failures by severity:
  - **Critical**: code or token issued to the wrong client or redirect URI, code
    or refresh token replay, open redirect from the authorization endpoint, the
    RS accepting forged, expired or foreign-audience tokens.
  - **High**: secrets, codes or tokens stored or logged in plain text; a
    validation that a spec makes mandatory is missing; consent can be bypassed.
  - **Medium**: robustness and abuse resistance (rate limits, cleanup, error
    handling, races).
  - **Low**: hygiene, metadata completeness, UX.
- Prefer citing the spec section next to each failure.
- A missing **negative test** for a security check is a finding in its own right.

## 1. Authorization endpoint and consent

- [ ] The authorization, token, revocation, introspection and registration
  endpoints are TLS-only (registration: TLS 1.2 or later). The authorization
  endpoint supports `GET`. RFC 6749 §3.1, §3.2; RFC 7009 §2; RFC 7662 §4;
  RFC 7591 §3, §5.
- [ ] Response types that issue access tokens from the authorization endpoint
  (`token`, and hybrid types containing `token`) are disabled.
  RFC 9700 §2.1.2. Accepting only `code` is local hardening; the BCP permits
  `code id_token`.
- [ ] A repeated parameter gives `invalid_request`, and an unknown
  `response_type` gives `unsupported_response_type`, once client and redirect
  URI are validated (before that: show an error, do not redirect). Repeated
  `resource` parameters are legal (RFC 8707 §2) and exempt.
  RFC 6749 §3.1, §3.1.1, §4.1.2.1.
- [ ] Unknown request parameters are ignored, not treated as errors; parameters
  sent with an empty value are treated as absent. RFC 6749 §3.1, §3.2.
- [ ] The client and redirect URI are validated **before** anything else. If
  either is missing or invalid, the AS shows an error to the user and does
  **not** redirect. RFC 6749 §4.1.2.1; RFC 9700 §4.11.2.
- [ ] For clients whose redirect URIs the AS does not vouch for (dynamic
  registration, client ID metadata documents), the user is authenticated before
  any redirect, including error and consent-denied redirects, and the AS
  redirects automatically only to redirect URIs it trusts; otherwise it informs
  the user. This closes open redirects via an attacker-registered client plus
  an invalid scope or a denial. RFC 9700 §4.11.2 (MUST authenticate first;
  SHOULD for trusted URIs). The section is written about attacker-registered
  clients; error redirects to admin-registered clients before login follow
  RFC 6749 §4.1.2.1 and are not a finding on their own, but say which clients
  the AS treats as trusted.
- [ ] Errors after that point go back to the validated redirect URI with `error`,
  `state` and `iss` (section 8), **unless** the redirect URI is not trusted (for
  example a client registered dynamically or through a client ID metadata
  document): then the next item applies, and the AS may show the error itself
  instead of redirecting. RFC 6749 §4.1.2.1; RFC 9700 §4.11.2.
- [ ] Redirects after a login or consent `POST` use 303, never 307.
  RFC 9700 §4.12.
- [ ] The authorization endpoint sends no CORS headers (the token, metadata,
  JWKS and registration endpoints may). RFC 9700 §2.6.
- [ ] `state`, `redirect_uri`, client name and error text are validated and
  escaped wherever they are rendered or logged (no XSS, no log injection).
  RFC 6749 §10.14.
- [ ] Login, consent and error pages load no third-party scripts, images or
  links, and set a Referrer-Policy that keeps the URL from third parties.
  RFC 9700 §4.2.4 gives `no-referrer` as an example. On pages with forms whose
  CSRF check relies on the `Origin` header, prefer `same-origin`: under
  `no-referrer`, browsers send `Origin: null` on a form `POST` (Fetch
  standard), and the check fails or has to accept `null`.
- [ ] The consent page shows the client's identity and the requested scopes and
  resources. Dynamically registered or unverified clients are marked as such;
  their self-asserted name, logo and URIs are not presented as verified, and
  `logo_uri`, `client_uri`, `tos_uri` and `policy_uri` are checked for host and
  scheme match with `redirect_uris`. RFC 7591 §5; RFC 6749 §10.2;
  RFC 8707 §2.1.
- [ ] For clients identified by a client ID metadata document, the consent page
  shows the `client_id` hostname, not only the self-asserted name and logo.
  CIMD draft -02 §8.5. When the redirect URI's host differs from the
  `client_id` host, the consent page shows the redirect host too (hardening).
- [ ] Consent is recorded per user, per client, and per scope and resource set.
  A new scope or resource asks again. Consent is never skipped for a client just
  because another client with the same name or upstream identity was approved.
- [ ] If the AS is itself a proxy to an upstream identity provider using one
  static upstream client ID, it still asks for consent per downstream client
  (confused-deputy defence).
- [ ] Consent and login forms are protected against CSRF and against framing
  (`frame-ancestors` / `X-Frame-Options`). RFC 6749 §10.12, §10.13;
  RFC 9700 §4.16.
- [ ] A pending consent request is bound to the browser session that started
  it: approving it from another session, or after the user changed, fails
  (hardening; a CSRF token alone does not ensure this).
- [ ] `state` is returned unchanged. The AS does not interpret it.
  RFC 6749 §4.1.2.

## 2. Client registration

- [ ] Every client has a type (confidential or public), and the type decides the
  client authentication it may use. A public client is never issued or asked for
  a secret (per-installation credentials from dynamic registration are the
  exception). RFC 6749 §2.1, §10.1; RFC 8252 §8.4, §8.5.
- [ ] `client_id` is generated by the server (or namespaced) and cannot collide
  with user `sub` values; otherwise the RS has another way to tell user tokens
  from client-credentials tokens. RFC 9700 §4.15.1; RFC 9068 §5.
- [ ] Redirect URIs are registered in full. No wildcards, no prefix patterns.
  RFC 9700 §2.1.
- [ ] Registered redirect URIs are checked at registration:
  - `http` only for native loopback redirects (MUST, RFC 9700 §2.6). Rejecting
    `http://localhost` is stricter than RFC 8252 (NOT RECOMMENDED there).
  - Custom schemes in reverse-domain form (SHOULD); at minimum, schemes without
    a `.` are rejected. RFC 8252 §8.4.
  - No fragments (MUST). RFC 6749 §3.1.2.
  - `https` for web clients (SHOULD). RFC 6749 §3.1.2.1.
- [ ] **Dynamic registration** (RFC 7591), if offered:
  - [ ] The endpoint is either protected by an initial access token, or open on
    purpose with the risk documented. RFC 7591 §3.
  - [ ] Client metadata is validated, not stored as given: redirect URIs as
    above, `grant_types` and `response_types` consistent with each other,
    `token_endpoint_auth_method` allowed for the client type, URIs well formed.
    RFC 7591 §2, §2.1, §5.
  - [ ] Unknown registration metadata is dropped, not stored or echoed.
    RFC 7591 §2.
  - [ ] Values the AS does not support are rejected or replaced, and the
    response says what was actually registered. RFC 7591 §3.2.1.
  - [ ] Software statements, if accepted, are signature-checked against a trusted
    key. RFC 7591 §2.3, §5.
  - [ ] Each `client_id` gets its own secret (ideally per instance). Generated
    secrets are high-entropy and have an expiry policy
    (`client_secret_expires_at`). RFC 7591 §3.2.1.
  - [ ] Registrations are rate-limited and unused ones expire (section 13).
- [ ] **Client ID metadata documents** (draft-ietf-oauth-client-id-metadata-document-02;
  a URL-shaped `client_id` fetched by the AS, used by MCP), if supported:
  - [ ] The `client_id` URL is `https`, has a path, has no userinfo, fragment or
    dot segments (a query is discouraged), and is compared by simple string
    comparison. §3.
  - [ ] Neither the document URL nor any URL inside it (`jwks_uri`,
    `logo_uri`, ...) is fetched if it resolves to a special-use address
    (RFC 6890); the loopback exception is for development only, never in
    production. Only known URI schemes are fetched or parsed. §8.6.
  - [ ] Fetches are rate-limited per `client_id` (and per source), since
    errors are never cached (below) and each authorization request can
    otherwise trigger a fresh fetch (hardening; §5 suggests periodic re-fetch,
    not one per request).
  - [ ] HTTP redirects are **not followed at all**. §5.
  - [ ] At most about 5 KB is read. §8.7.
  - [ ] A 200 response is required, and the document's `client_id` equals the
    URL. §4.
  - [ ] Documents declaring shared-secret auth methods (`client_secret_post`,
    `client_secret_basic`, `client_secret_jwt`, ...) or a `client_secret` are
    rejected. Private key material in the document is rejected. §4.1.
  - [ ] The document's `redirect_uris` are the only allowed redirect URIs,
    matched exactly by simple string comparison. §4.2. The draft is silent on
    the loopback port: it invokes RFC 9700, whose §4.1.3 requires variable
    ports for native apps' localhost redirects (RFC 8252 §7.3). State which the
    AS does; an AS that allows the port to vary must match everything else
    exactly.
  - [ ] Cache headers are respected; errors and invalid documents are never
    cached. §5.2.

## 3. Redirect URI matching

- [ ] The redirect URI in the request is compared with the registered ones by
  **exact string match**. RFC 9700 §2.1, §4.1.3.
- [ ] The only exception is the port of a loopback redirect for native clients:
  any port is allowed, everything else matches exactly. RFC 8252 §7.3, §8.4;
  RFC 9700 §2.1.
- [ ] If the client registered more than one redirect URI, the request must
  include `redirect_uri`. RFC 6749 §3.1.2.3.
- [ ] At the token endpoint, if `redirect_uri` was in the authorization request,
  it is required and must be identical. RFC 6749 §4.1.3.

## 4. PKCE

- [ ] PKCE is **required** for public clients, and preferably for all clients.
  A request without `code_challenge` is rejected where it is required.
  RFC 9700 §2.1.1; RFC 7636 §4.4.1; RFC 8252 §6, §8.1.
- [ ] Only `S256` is accepted, and `plain` is rejected with `invalid_request`.
  This is hardening: RFC 9700 §2.1.1 tells clients to use S256 (see also
  RFC 7636 §4.2, §4.4.1).
- [ ] `code_challenge` is 43–128 unreserved characters (RFC 7636 §4.2); for
  S256 that means exactly 43 base64url characters.
- [ ] PKCE errors at the authorization endpoint (missing required challenge,
  unsupported method) use `error=invalid_request`. RFC 7636 §4.4.1.
- [ ] The challenge is stored with the code and checked at the token endpoint.
  A mismatch fails with `invalid_grant`. RFC 7636 §4.4, §4.6. Stateless codes
  that embed the challenge encrypt it. RFC 7636 §4.4.
- [ ] **Downgrade defence:** if the authorization request had no
  `code_challenge`, a token request that sends a `code_verifier` is rejected.
  If it had one, a token request without `code_verifier` is rejected.
  RFC 9700 §2.1.1, §4.8.2 (stricter than RFC 7636 §5).
- [ ] `code_challenge_methods_supported` is published in metadata.
  RFC 8414 §2; RFC 9700 §2.1.1.

## 5. Authorization code issuance and single use

- [ ] Codes are random with at least 128 bits of entropy and cannot be guessed
  or derived from other values. RFC 6749 §10.10.
- [ ] Codes are short-lived (a few minutes; at most 10 minutes). RFC 6749 §4.1.2.
- [ ] A code is bound to: client ID, redirect URI, user, scopes, resource(s) and
  PKCE challenge, and each binding is checked at the token endpoint.
  RFC 6749 §4.1.3. With OIDC, the `nonce` from the authorization request is
  stored with the code and copied unchanged into the ID token; it is not
  checked at the token endpoint. OIDC Core §2, §3.1.3.6.
- [ ] A code is redeemed **at most once**, atomically, even under concurrent
  requests (check-and-mark in one transaction or with a compare-and-set).
- [ ] A second redemption attempt fails (MUST) and, where possible, revokes the
  tokens already issued from that code (SHOULD). RFC 6749 §4.1.2, §10.5;
  RFC 9700 §4.2.4.

## 6. Token endpoint and client authentication

- [ ] Only HTTPS and `POST` with form-encoded parameters. RFC 6749 §3.2.
- [ ] Confidential clients must authenticate. Only the methods registered for
  that client are accepted. RFC 6749 §2.3, §3.2.1. Prefer `private_key_jwt` or
  mTLS over shared secrets. RFC 9700 §2.5.
- [ ] `client_secret_basic`: the ID and secret are form-URL-decoded after
  Base64 decoding. RFC 6749 §2.3.1.
- [ ] Secrets are compared in constant time.
- [ ] `private_key_jwt` / `client_secret_jwt`, if supported (OIDC Core §9;
  RFC 7523 §3):
  - `iss` and `sub` equal the `client_id`;
  - `aud` identifies the AS (OIDC: the token endpoint URL SHOULD be used), and
    other audiences are rejected;
  - `exp` is present and enforced (a short maximum lifetime is local policy);
  - the signature is verified with the client's registered key against an
    algorithm allowlist;
  - `jti` is required and single-use (OIDC Core §9; optional under plain
    RFC 7523);
  - failures return `invalid_client` (`invalid_grant` for grant assertions).
- [ ] A public client is identified by `client_id`, and the code must have been
  issued to that same client. RFC 6749 §4.1.3.
- [ ] Error responses use the standard codes (`invalid_request`,
  `invalid_client`, `invalid_grant`, `unauthorized_client`,
  `unsupported_grant_type`, `invalid_scope`) with no internal detail. A failed
  client authentication returns 401 with `WWW-Authenticate` when the client used
  HTTP authentication. RFC 6749 §5.2.
- [ ] Token responses carry `Cache-Control: no-store` **and**
  `Pragma: no-cache` (MUST); error responses should too. RFC 6749 §5.1.
- [ ] The response includes `scope` whenever it differs from the request. A
  request without a scope gets a documented default or fails with
  `invalid_scope`. RFC 6749 §3.3, §5.1.
- [ ] Each client may use only the grant types it registered (else
  `unauthorized_client`). RFC 6749 §5.2. Under RFC 7591 §2 an omitted
  `grant_types` means `authorization_code` only, and `refresh_token` is a
  separate grant type, so: either the AS registers `refresh_token` explicitly
  and says so in the registration response (RFC 7591 §3.2.1), or it does not
  issue refresh tokens to that client. Check how the client ID metadata
  document draft treats an omitted `grant_types`.

## 7. Access tokens and validation (resource server)

- [ ] The token format is a deliberate choice: self-contained (for example a JWT
  per RFC 9068) or opaque with introspection (RFC 7662). The trade-off on
  revocation latency is documented.
- [ ] Opaque access and refresh tokens come from a CSPRNG with at least 128 bits
  (160 preferred); self-contained tokens are integrity-protected.
  RFC 6749 §10.10; RFC 6750 §5.2.
- [ ] Access tokens have an enforced expiry (one hour or less recommended), and
  `expires_in` is returned. RFC 6750 §5.2, §5.3; RFC 6749 §5.1.
- [ ] **JWT access tokens:**
  - [ ] Signed, never with `none` (MUST). Asymmetric signing is RECOMMENDED; an
    HMAC algorithm needs a deliberate decision. RS256 is among the supported
    algorithms. The RS validates against an explicit allowlist and rejects
    algorithm confusion. RFC 9068 §2.1, §4; RFC 8725 §3.1, §3.2.
  - [ ] Issued tokens contain `iss`, `exp`, `aud`, `sub`, `client_id`, `iat`
    and `jti` (REQUIRED). RS rejection of tokens missing any of them is
    hardening. RFC 9068 §2.2.
  - [ ] Explicit typing: `typ` is `at+jwt`, and the RS rejects other JWTs (such
    as ID tokens) offered as access tokens. RFC 9068 §2.1, §4; RFC 8725 §3.11,
    §3.12.
  - [ ] The RS checks `iss` (exact match), that `aud` **contains** its own
    identifier, `exp` (small leeway), and `nbf` if present (RFC 7519 §4.1.5).
    RFC 9068 §4.
  - [ ] The RS takes keys only from the issuer's `jwks_uri` and ignores `jku`,
    `x5u` and `jwk` headers; `kid` is only a sanitised lookup key. Keys are
    rotated with overlap, and the RS refetches on an unknown `kid`
    (rate-limited). Every validation failure returns 401 `invalid_token`.
    RFC 9068 §4; RFC 8725 §3.8, §3.10; OIDC Core §10.1.1.
- [ ] **Opaque tokens and introspection:**
  - [ ] The endpoint requires authentication of the caller, and only resource
    servers specifically authorized for introspection may call it. TLS only;
    `GET` may be refused. RFC 7662 §2, §4.
  - [ ] `active: true` is returned only after all applicable checks (`exp`,
    `nbf`, revocation, signature, audience matching the calling RS); every
    invalid, expired or revoked token gets `active: false` without saying why.
    RFC 7662 §2.2, §4.
  - [ ] `username` and `sub` are returned only to resource servers that need
    them (consider per-RS opaque identifiers). RFC 7662 §5.
  - [ ] The RS caches introspection results no longer than `exp` and within an
    agreed revocation-latency budget. RFC 7662 §4.
- [ ] The RS accepts tokens only in the `Authorization` header (hardening).
  RFC 6750 §2.1 requires header support; query support is optional (§2.3, MAY;
  discouraged in §5.3). RFC 9700 §4.3.2 forbids clients from sending tokens in
  the query, and RS rejection closes that channel.
- [ ] RS error responses, RFC 6750 §3, §3.1:
  - no token: 401 with `WWW-Authenticate: Bearer` and **no** `error` attribute;
  - invalid token: 401 with `error="invalid_token"`;
  - insufficient scope: 403 with `error="insufficient_scope"`;
  - malformed request: 400 `invalid_request`.

  The statuses are SHOULD; the header and the Bearer scheme are MUST. The
  challenge is well formed: each auth-param at most once, values within the
  allowed character set.
- [ ] The RS lets clients find its protected resource metadata. RFC 9728
  makes the `resource_metadata` parameter in the 401 a MAY (§5, §5.1). MCP
  2025-11-25 requires **one of**: `resource_metadata` in the 401, or the
  metadata at the RFC 9728 well-known URI (MCP clients must support both).
- [ ] MCP: a runtime 403 `insufficient_scope` SHOULD carry `scope` (the scopes
  the request needs) and `resource_metadata` in the `WWW-Authenticate` header.
  MCP 2025-11-25, Authorization, "Runtime Insufficient Scope Errors".
- [ ] Scope and resource checks happen per endpoint, not once at login.
  RFC 6749 §7; RFC 9700 §2.3.
- [ ] On every request the RS also checks the user's **current** state, not only
  the token: a disabled account, a removed membership or a lowered role takes
  effect before the token expires (hardening; with JWTs, through a short
  lifetime or a per-request lookup).
- [ ] If a stateful protocol runs on top (for example MCP sessions), each
  session ID is bound to the authenticated user and client, and a request whose
  token belongs to someone else is rejected even with a valid session ID
  (hardening; check the protocol's own spec).
- [ ] **No token passthrough:** the RS never forwards the access token it
  received to another service. If it calls downstream APIs, it gets its own
  token (for example via token exchange, RFC 8693, which is the mechanism, not
  the source of the rule).
- [ ] **Sender-constrained tokens:** DPoP (RFC 9449) or mTLS (RFC 8705) is
  supported, or the decision not to support it is documented.
  RFC 9700 §2.2.1 (SHOULD).
  - [ ] DPoP: the AS and the RS run every RFC 9449 §4.3 check (a single DPoP
    header, `typ=dpop+jwt`, an asymmetric non-`none` alg, no private key in
    `jwk`, `htm`/`htu` match, nonce if issued, `iat` freshness window), and the
    RS also checks `ath` and the key binding. `jti` tracking is optional.
    RFC 9449 §4.3, §7.1, §11.1.
  - [ ] DPoP: a DPoP-bound access token presented with the Bearer scheme is
    rejected. RFC 9449 §7.2.
  - [ ] mTLS: the RS compares the TLS client certificate thumbprint with
    `cnf` `x5t#S256` on every request; a mismatch gives 401 `invalid_token`.
    RFC 8705 §3.

## 8. Issuer identification (RFC 9207)

- [ ] Every authorization response, success or error, includes `iss` equal to
  the AS issuer identifier (an `https` URL without query or fragment).
  RFC 9207 §2.
- [ ] `authorization_response_iss_parameter_supported: true` is in metadata.
  RFC 9207 §2.3, §3.

## 9. Audience and resource binding (RFC 8707)

- [ ] The `resource` parameter is accepted at the authorization and token
  endpoints. Each value is an absolute URI without a fragment. RFC 8707 §2.
- [ ] Unknown or disallowed resources are rejected with `invalid_target`.
  RFC 8707 §2.
- [ ] Issued access tokens are audience-restricted to the requested resource(s)
  (`aud` in a JWT, or the audience in introspection). RFC 9700 §2.3;
  RFC 9068 §3; RFC 9728 §7.4.
- [ ] A request without `resource` still gets a default, non-empty `aud`.
  Scopes that map to different default resources are rejected with
  `invalid_scope`; ambiguous tokens are never issued. RFC 9068 §3.
- [ ] Each resource has its own `aud` identifier. No shared or wildcard `aud`
  across resource servers. RFC 9068 §5.
- [ ] Resources requested at the token endpoint are a subset of those granted at
  authorization time. RFC 8707 §2.2.
- [ ] If the AS serves several resources, a token for one is rejected by the
  others (test this, section 15). RFC 8707 §3.

## 10. Refresh tokens

Here a **grant** is one user's authorization of one client, from one
authorization code redemption onwards: the refresh tokens that descend from
that code by rotation, and the access tokens issued from them. Two
installations of the same client, or two logins, are two grants. Say in the
review if the implementation draws the line elsewhere.

- [ ] Refresh tokens are issued only where needed, and are bound to the client
  they were issued to. Using one from another client fails. RFC 6749 §6, §10.4.
- [ ] Requested scopes **and resources** on refresh can only narrow the original
  grant. RFC 6749 §6; RFC 9700 §4.14.2.
- [ ] For public clients, refresh tokens are either sender-constrained or
  **rotated** on every use. RFC 9700 §2.2.2. With DPoP, a public client's
  refresh token is bound to the proof key and the binding is checked on refresh
  (RFC 9449 §5; mTLS: RFC 8705 §4, SHOULD).
- [ ] With rotation, reuse of a rotated-out refresh token is detected and the
  grant's active refresh token is revoked (RFC 9700 §4.14.2). Also revoking the
  outstanding access tokens of that grant is recommended hardening
  (compare RFC 7009 §2.1).
- [ ] Rotation is atomic under concurrent refresh requests. Decide and document
  how a benign retry is told apart from replay (for example a short grace window
  for the same client), because clients race, and test it: two concurrent
  refreshes with the **same** token give exactly the documented outcome.
- [ ] Refresh tokens have an absolute lifetime and, ideally, an idle timeout, and
  they end when the user revokes the grant or the user account is disabled.
  RFC 9700 §4.14.2.

## 11. Revocation

- [ ] If a revocation endpoint is offered (RFC 7009 does not require one), it is
  published in metadata as `revocation_endpoint`. RFC 8414 §2.
- [ ] It authenticates confidential clients, and only lets a client revoke its
  own tokens (refusing with an error is also valid). RFC 7009 §2.1.
- [ ] It returns 200 for unknown or already-invalid tokens, so it does not leak
  which tokens exist. RFC 7009 §2.2.
- [ ] A wrong or invalid `token_type_hint` causes neither a failure nor a missed
  revocation (the AS searches all token types). Unsupported types return
  `unsupported_token_type`. RFC 7009 §2.1, §2.2, §2.2.1.
- [ ] If the AS supports access token revocation, revoking a refresh token also
  invalidates the access tokens of the same grant (SHOULD); otherwise the
  residual window is documented. RFC 7009 §2.1, §5.
- [ ] Invalidation takes effect immediately at the AS, and the delay until
  revoked access tokens stop working at the RS (JWT lifetime, caches) is
  minimized, known and acceptable. RFC 7009 §2.1.
- [ ] Users can see and revoke the grants they gave to each client.

## 12. Metadata (RFC 8414 and RFC 9728)

- [ ] AS metadata is served at the well-known URL derived from the issuer,
  including the path-insertion rule for issuers with a path. RFC 8414 §3, §3.1.
- [ ] `issuer` in the document equals the issuer identifier exactly, and equals
  `iss` in tokens and authorization responses. RFC 8414 §3.3; RFC 9207 §2.3;
  OIDC Discovery §3, §4.3; RFC 9068 §4.
- [ ] If both `/.well-known/oauth-authorization-server` and
  `/.well-known/openid-configuration` exist, `issuer`, `jwks_uri` and the
  endpoints are identical in both. RFC 9068 §4.
- [ ] Metadata is complete and true: endpoints, `grant_types_supported`
  (publish it explicitly: when omitted it defaults to authorization code plus
  implicit), `response_types_supported`, `code_challenge_methods_supported`,
  `token_endpoint_auth_methods_supported`, `registration_endpoint` if dynamic
  registration exists, `revocation_endpoint`, `introspection_endpoint`,
  `jwks_uri`. Nothing advertised that is not implemented. RFC 8414 §2.
- [ ] Protected resource metadata is served at the RS well-known URL. Its
  `resource` equals the resource identifier the client used, and
  `authorization_servers` lists only the AS(s) that actually issue tokens for it.
  RFC 9728 §3, §3.3.
- [ ] Both documents are HTTPS only and safe to cache.

## 13. Storage, expiry and cleanup

- [ ] Client secrets are stored hashed (or encrypted if the method needs the
  plain value, such as `client_secret_jwt`). RFC 6819 §5.1.4.1.3
  (Informational; a recommendation).
- [ ] Authorization codes and refresh tokens are stored as hashes, so a database
  read does not give usable credentials. Opaque access tokens are stored the
  same way. RFC 6819 §5.1.4.1.3 (recommendation).
- [ ] Signing keys are in a key store or KMS, not in source or plain config.
- [ ] Expired codes, tokens, consents and unused dynamic registrations are
  purged on a schedule. Revocation records are kept until the revoked token
  would have expired anyway.
- [ ] Cleanup does not race with redemption (a code being redeemed is not deleted
  halfway).

## 14. Deployment, rate limiting, abuse and logging

- [ ] Behind a TLS-terminating proxy, client-supplied `X-Forwarded-*` and
  client-certificate headers are stripped or overwritten, and the
  proxy-to-application hop is protected. RFC 6750 §5.2; RFC 9700 §4.13.
- [ ] Rate limits on the authorization, token, registration, introspection and
  revocation endpoints, per client and per source. RFC 6749 §2.3.1;
  RFC 7009 §5; RFC 7662 §4; RFC 6819 §5.1.4.2.
- [ ] Repeated failures (bad client secrets, bad PKCE verifiers, replayed codes,
  refresh token reuse) are counted and can raise alerts or lock out a client.
- [ ] Request sizes and parameter lengths are limited.
- [ ] Codes, access tokens, refresh tokens, client secrets, PKCE verifiers and
  assertions never appear in logs, error messages, URLs of redirects to
  third parties, or telemetry. Check the HTTP access log for query strings.
  RFC 9700 §4.9.3.
- [ ] Security events are logged for audit without secrets: client
  registration, consent granted or revoked, token issuance, refresh reuse
  detected, revocation. Check that the **production** log level and
  configuration actually emit them; reading the logging calls is not enough.
- [ ] Error pages and responses do not include stack traces or internal details.

## 15. Tests

For each security check above, there is a test that **fails** when the check is
removed. At minimum:

- [ ] Authorization request with an unregistered or slightly different redirect
  URI: no redirect happens. Loopback with a different port: allowed.
- [ ] Unknown client, `response_type=token`, duplicate parameters: rejected.
  Repeated `resource`: accepted.
- [ ] Error and denial paths: no redirect before the user is authenticated;
  303 after `POST`; no CORS headers on the authorization endpoint.
- [ ] PKCE: missing challenge where required, `plain`, wrong verifier, verifier
  without challenge (downgrade), challenge without verifier.
- [ ] Code: reused (fails; tokens from the first use are revoked where
  supported), expired, used by another client, used with another redirect URI,
  concurrent double redemption.
- [ ] Client authentication: wrong secret, wrong method for the client, replayed
  `jti` (OIDC Core §9), wrong `aud` in the assertion.
- [ ] Token responses carry `Cache-Control: no-store` and `Pragma: no-cache`.
- [ ] Refresh: rotation, reuse detection revokes the active refresh token, scope
  or resource widening rejected, refresh by another client rejected, two
  concurrent refreshes with the same token, refresh for a client that did not
  register `refresh_token`.
- [ ] Consent: approval from another browser session fails.
- [ ] RS: a token for a since-disabled user or lowered role is refused; a
  session ID used with another user's token is refused.
- [ ] Revocation: revoked refresh and access tokens stop working; revoking
  another client's token has no effect; unknown token returns 200; wrong
  `token_type_hint` still revokes.
- [ ] RS: no token (401, no `error`), expired token, `aud` that omits this RS,
  wrong `iss`, bad signature, `alg: none`, `typ` other than `at+jwt` (for
  example an ID token), `jku` header pointing elsewhere, token in query string,
  missing scope (403).
- [ ] DPoP / mTLS, if used: missing or invalid proof, a DPoP-bound token sent as
  Bearer, wrong certificate.
- [ ] Introspection: unauthorized caller rejected; revoked token `active: false`.
- [ ] Resource binding: token for resource A rejected by resource B;
  `invalid_target` for an unknown resource.
- [ ] Dynamic registration: invalid redirect URIs, inconsistent grant types,
  public client asking for a secret-based method, unknown metadata dropped.
- [ ] Client ID metadata documents, if supported: redirect not followed,
  oversized document, private address, `client_id` mismatch, shared-secret auth
  method declared.
- [ ] Every authorization response, including errors, carries `iss`.
- [ ] Nothing secret in logged output (assert on captured logs).

Tests that only cover the happy path are a finding.

## 16. Library question

An authorization server is much more work to get right than a client. If more
than a few items in sections 1–11 fail, recommend replacing the hand-written
protocol code with a maintained, preferably OpenID-certified, implementation
(an embedded library or a separate server) and keeping only the application
parts: user authentication, consent UI, scope and resource policy, and storage
integration. Library or not, sections 1 (consent), 7 (resource server checks),
13, 14 and 15 stay the application's responsibility.

## References

- [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749): OAuth 2.0
- [RFC 6750](https://www.rfc-editor.org/rfc/rfc6750): Bearer Token Usage
- [RFC 6819](https://www.rfc-editor.org/rfc/rfc6819): OAuth 2.0 Threat Model and Security Considerations (Informational)
- [RFC 7009](https://www.rfc-editor.org/rfc/rfc7009): Token Revocation
- [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519): JSON Web Token
- [RFC 7523](https://www.rfc-editor.org/rfc/rfc7523): JWT Profile for Client Authentication
- [RFC 7591](https://www.rfc-editor.org/rfc/rfc7591): Dynamic Client Registration
- [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636): PKCE
- [RFC 7662](https://www.rfc-editor.org/rfc/rfc7662): Token Introspection
- [RFC 8252](https://www.rfc-editor.org/rfc/rfc8252): OAuth 2.0 for Native Apps
- [RFC 8414](https://www.rfc-editor.org/rfc/rfc8414): Authorization Server Metadata
- [RFC 8693](https://www.rfc-editor.org/rfc/rfc8693): Token Exchange
- [RFC 8705](https://www.rfc-editor.org/rfc/rfc8705): Mutual-TLS Client Authentication and Certificate-Bound Tokens
- [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707): Resource Indicators
- [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725): JWT Best Current Practices
- [RFC 9068](https://www.rfc-editor.org/rfc/rfc9068): JWT Profile for Access Tokens
- [RFC 9207](https://www.rfc-editor.org/rfc/rfc9207): Authorization Server Issuer Identification
- [RFC 9449](https://www.rfc-editor.org/rfc/rfc9449): DPoP
- [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700): OAuth 2.0 Security Best Current Practice
- [RFC 9728](https://www.rfc-editor.org/rfc/rfc9728): Protected Resource Metadata
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [MCP Authorization, 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [OAuth Client ID Metadata Document, draft -02](https://datatracker.ietf.org/doc/draft-ietf-oauth-client-id-metadata-document/) (IETF draft; pin the revision)
