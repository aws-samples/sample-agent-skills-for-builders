# OAuth Discovery, Fake DCR, and Redirect Rewriting

How to make Amazon Cognito look like a complete OAuth 2.0 / OIDC provider to
MCP clients, without the facade ever issuing a token.

## Design rule: interaction via facade, validation via Cognito

The single most important invariant:

- **Interactive endpoints** (`authorization_endpoint`, `token_endpoint`,
  `registration_endpoint`) point at the **facade** — that's where rewriting
  happens.
- **`issuer` and `jwks_uri`** point at the **real Cognito issuer**
  (`https://cognito-idp.<region>.amazonaws.com/<pool-id>`).

Tokens are therefore always signed and issued by Cognito. The AgentCore
Gateway (or Runtime) JWT authorizer keeps validating against Cognito's JWKS
with zero changes. The facade is a pure man-in-the-middle for the interactive
hops and never holds signing keys.

## Why CloudFront in front of the HTTP API

Some MCP clients (Amazon Quick among them) do **not** support path-prefixed
metadata discovery — the well-known documents must live at the server root.
API Gateway HTTP APIs always have a stage path unless you use the `$default`
stage, and even then the execute-api domain is awkward for OAuth allow-lists.
CloudFront gives a clean root domain. Route everything with a `/{proxy+}`
catch-all and dispatch inside the Lambda on `event.rawPath`. Make sure the
CloudFront origin request policy **forwards the `Authorization` header** (and
disable caching for `/mcp` and the OAuth routes) — the default cache policy
strips it, which presents as every authenticated call failing while curl
against the HTTP API origin works.

CDK wrinkle: the Lambda needs its own public URL as `FACADE_ORIGIN`, which
creates a circular reference (Lambda → Distribution → Lambda). Deploy with a
placeholder env value and back-fill after the Distribution is constructed:

```ts
fn.addEnvironment('FACADE_ORIGIN', `https://${distribution.domainName}`)
```

Same trick for Cognito callback URLs: adding `${facadeUrl}/oauth/callback` to
the user-pool client via props creates a synth cycle; use an L1 override
(`cfnUserClient.addPropertyOverride('CallbackURLs', [...])`) at stack level
instead.

## The three metadata documents

Serve all three, all at root:

| Path | Spec | Notes |
|---|---|---|
| `/.well-known/oauth-protected-resource` | RFC 9728 | `resource` = `{FACADE_ORIGIN}/mcp`, `authorization_servers` = `[FACADE_ORIGIN]` |
| `/.well-known/oauth-authorization-server` | RFC 8414 | facade endpoints + real Cognito `issuer`/`jwks_uri` |
| `/.well-known/openid-configuration` | OIDC Discovery 1.0 | same shape + `subject_types_supported`, `id_token_signing_alg_values_supported: ["RS256"]` |

**Also serve the path-insertion variants.** Clients that connect to
`https://host/mcp` probe `/.well-known/openid-configuration/mcp` (metadata
path with the resource path appended). Register each document under both
forms — six routes total.

**Bootstrap the chain from the 401.** Per RFC 9728, an unauthenticated
request to `/mcp` should get 401 with
`WWW-Authenticate: Bearer resource_metadata="{FACADE_ORIGIN}/.well-known/oauth-protected-resource"`
— that header is how a client that knows nothing about your server finds the
discovery chain at all.

### Case study: the "Fix highlighted fields" failure

Amazon Quick's MCP connector uses RFC 7591 Dynamic Client Registration when
the discovery chain advertises a `registration_endpoint`. If **any** document
in the chain 404s, Quick silently falls back to a manual credentials form
whose *Client secret* field is required — which a public client can never
satisfy. The visible symptom is a validation error ("Fix highlighted
fields"); the root cause is a 404 three requests earlier. Fix the discovery
chain, and DCR + PKCE flows through with no manual input.

## Fake DCR

Cognito has no DCR API, and you don't need one. `POST /register`:

1. Echo the client's requested metadata back.
2. Return the **pre-provisioned public client ID** with HTTP 201.

One shared public client (PKCE, no secret) serves every MCP client. Nothing
is created or stored.

Resist the tempting alternative — a DCR Lambda that really calls
`CreateUserPoolClient` per registration. It works, but now you own client
lifecycle: cleanup of abandoned clients, rate limiting, a growing
`allowedClients` problem on the Gateway authorizer, and (if you generate
secrets) confidential-client handling for clients that expected a public
one. The echo approach has none of that surface.

## Redirect URI rewriting with signed state

Cognito only redirects to pre-registered callback URLs; MCP clients bring
arbitrary ones (`http://localhost:<random>/callback`, hosted-client HTTPS
callbacks). Bridge with a stateless HMAC round-trip:

```
client ── authorize(redirect_uri=R, state=S) ──► facade
facade: state' = sign_hmac({redirect_uri: R, state: S, ts})     # HMAC-SHA256
facade ── authorize(redirect_uri=FACADE/oauth/callback, state=state') ──► Cognito
Cognito ── code + state' ──► facade /oauth/callback
facade: verify state' (max age 600s) → 302 to R?code=...&state=S
client ── token(code, redirect_uri=R) ──► facade /oauth/token
facade: force form.redirect_uri = FACADE/oauth/callback → Cognito /oauth2/token
```

Key points:

- The HMAC key lives in Secrets Manager; the facade holds **no session
  state** (no DynamoDB, no Redis). Signature + max-age is the entire replay
  defense.
- At `/oauth/token` the facade must **overwrite** `redirect_uri` with its own
  callback — Cognito requires it to match what the authorize request used.
- Validate `redirect_uri` against an allow-list (loopback addresses plus your
  known hosted-client domains) **on both the happy path and the error
  branch**. Cognito error redirects otherwise become an open-redirect vector.
- Bare probes of `/oauth/authorize` (no `redirect_uri`) must **not** return
  400. Client wizards probe the authorization URL to check it is alive, and a
  real authorization server answers a bare probe with a 302 to its login
  page. Only hard-reject when a `redirect_uri` is present but not allowed.

## Scope injection

AgentCore Gateway enforces the resource-server scope on **every**
`tools/call` (an MCP Runtime with a JWT authorizer only checks
`allowedClients`). Generic OIDC clients request `openid email profile` and
nothing else, so their tokens lack the custom scope and every call 403s.

Fix at `/oauth/authorize`: union the required resource scope (e.g.
`myapi/invoke`) into the `scope` parameter before forwarding to Cognito.
Pair this with the 403→401 conversion described in
[mcp-session-and-protocol-bridging.md](mcp-session-and-protocol-bridging.md)
so clients holding pre-injection tokens re-authenticate instead of
retry-looping.

## Dual client model

| Client | Type | Flow | Use |
|---|---|---|---|
| user client | public, no secret | authorization code + PKCE, scopes `openid email profile` + resource scope | humans via MCP clients, through the facade |
| machine client | confidential | `client_credentials`, resource scope only, long-lived token | service-to-service and scheduled jobs, **direct to Cognito** `/oauth2/token`, bypassing the facade OAuth layer |

Register **both** client IDs in the Gateway authorizer's `allowedClients`.
