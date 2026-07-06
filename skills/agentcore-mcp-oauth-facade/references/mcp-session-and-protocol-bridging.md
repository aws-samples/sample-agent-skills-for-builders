# MCP Session Handling and Protocol Bridging

The session-id mechanics and the protocol differences a facade must bridge
between strict MCP clients and AgentCore Gateway / Runtime.

## Two session identifiers, two owners

| Header | Owner | Purpose | Constraint |
|---|---|---|---|
| `X-Amzn-Bedrock-AgentCore-Runtime-Session-Id` | AgentCore platform | routes the request to a microVM/container | **length ≥ 33 chars** (a bare 32-hex UUID is rejected) |
| `Mcp-Session-Id` | MCP protocol | protocol session continuity between client and server | issued by the MCP server on `initialize` |

Generic MCP clients know nothing about the AgentCore header. The facade
injects it:

```python
_AGENTCORE_SESSION_ID_HEADER = "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id"

def _ensure_agentcore_session_id(src_headers):
    # pass through a client-supplied value if it is long enough,
    # otherwise mint one; "facade-" + 32 hex = 39 chars, clears the 33 floor
    return f"facade-{uuid.uuid4().hex}"
```

Minting a **fresh routing key per request is safe** — it only picks a
container; protocol continuity lives entirely in `Mcp-Session-Id`. But it has
two consequences you must handle (session poison, stateless servers — below).
And every code path that calls the upstream directly, outside the main proxy
handler, must mint its own ≥33-char id too.

## Session poison: suppress the routing-key echo

AgentCore Runtime echoes the injected routing key back as an
`mcp-session-id` **response** header on responses that carry no real MCP
session — typically the 202 for `notifications/initialized`.

Spec-compliant clients (`mcp-remote` and everything built on it) adopt any
new `Mcp-Session-Id` they see in a response. So the client silently switches
from the real session id it got from `initialize` to your routing key, and
every subsequent `tools/call` hits a session the server never issued → 404.

Surgical fix — filter only the exact echo when relaying response headers:

```python
if header_name.lower() == "mcp-session-id" and value == injected_routing_key:
    continue  # suppress; a real session id can never equal the routing key
```

Real session ids still pass through untouched.

## Stateless servers: two separate problems

**1. FastMCP-on-Runtime must be `stateless_http=True`.** Default FastMCP is
stateful: session state lives in one container's memory, keyed by
`Mcp-Session-Id`. With a fresh routing key per request, AgentCore may land
each request on any (possibly recycled) microVM, which doesn't know the
client's session → intermittent 404 "no valid session" that "heals" when
traffic converges on a single warm instance. `FastMCP(..., stateless_http=True)`
makes every request self-contained.

**2. Gateway never returns an `Mcp-Session-Id` — synthesize one.** AgentCore
Gateway is stateless and omits the header entirely, but strict clients
require one from `initialize` and echo it on every later request; without it
they stall at the handshake. The facade returns a synthesized stable id
(`facade-mcp-<uuid>`), or echoes back whatever the client already sent. The
Gateway ignores the header, so it never becomes upstream state.

## The full bridging table (Gateway vs. a complete MCP server)

Migrating tools from an MCP Runtime (full FastMCP) to AgentCore Gateway
surfaced six behavioral differences. **None of them reproduce with curl** —
curl doesn't demand session ids, doesn't request SSE, brings its own scopes,
and never paginates. Test with a real strict MCP client.

| # | Gateway behavior | Facade bridge |
|---|---|---|
| 1 | stateless, never returns `Mcp-Session-Id` | synthesize a stable `facade-mcp-<uuid>` |
| 2 | always answers `application/json`, ignores `Accept: text/event-stream` | re-wrap 2xx JSON bodies as a single SSE `message` event when the client asked for SSE |
| 3 | enforces resource scope per `tools/call` → 403 | inject scope at authorize; convert 403 `insufficient_scope` → 401 + RFC 9728 `WWW-Authenticate` challenge (otherwise clients loop retry→403 forever instead of re-authenticating) |
| 4 | `GET /mcp` (server→client SSE channel) → 405; `mcp-remote` retries in a loop | facade answers the GET itself: 200 `text/event-stream` with an empty stream (a single SSE comment line) |
| 5 | `tools/list` paginated, 30 tools/page + `nextCursor` | server-side aggregation — see [gateway-pagination-and-limits.md](gateway-pagination-and-limits.md) |
| 6 | tool names prefixed `{target}___{tool}` | strip inbound / add outbound — see same reference |

## Injecting server instructions into `initialize`

A facade is also the right place to inject onboarding text into the
`initialize` response's `result.instructions` (a standard MCP field), giving
every client server-side usage guidance with zero client-side installation.
Rules learned in production:

- Only patch when `result.protocolVersion` is present (it's really an
  initialize response) and the upstream didn't set its own instructions.
- Patch **before** any JSON→SSE re-wrapping — the SSE bridge treats the body
  as opaque bytes.
- Every inbound rewrite function must handle **both** plain JSON bodies and
  SSE `data:` lines; MCP streamable-http traffic contains both.
