# Gateway Pagination, Tool Name Prefix, Schema Limits, Lambda Target

AgentCore Gateway-specific constraints and the adapter code shapes that make
them invisible to MCP clients.

## tools/list pagination — aggregate server-side

**Problem.** Gateway paginates `tools/list`: at most 30 tools per page plus a
`nextCursor`. Cursor-following is optional in the MCP spec and many clients
(Amazon Quick, among others) only read the first page. Tool #31 onward
**silently disappears** — no error, the tools just aren't there.

**Fix.** Intercept `method == "tools/list"` in the facade's `/mcp` proxy and
walk the cursor chain server-side:

```python
all_tools, cursor = [], None
for _ in range(20):                      # hard cap: 20 pages x 30 = 600 tools
    params = {} if cursor is None else {"cursor": cursor}
    status, raw = gateway_post(page_request(params), fwd_headers)
    raw = strip_tool_name_prefix(raw)    # see next section
    result = parse_result(raw)
    all_tools.extend(result.get("tools") or [])
    cursor = result.get("nextCursor")
    if not cursor:
        break
return tools_list_envelope(request_id, all_tools)   # single page, no nextCursor
```

Edge cases that matter in production:

- **Don't leak `nextCursor`** in the merged response — clients must see one
  complete page.
- A non-JSON page mid-walk (e.g. an upstream 401/403 error body): return the
  pages already collected if any, otherwise pass the first-page error
  through verbatim.
- If the client requested SSE, the aggregated result goes through the same
  JSON→SSE re-wrap as any other response.
- Bound the loop. A runaway cursor should fail loudly, not spin.

## Tool name prefix (`{target}___{tool}`)

Gateway exposes every tool as `{targetName}___{toolName}` (triple-underscore
separator). To keep clients and internal callers on bare names:

- **Inbound** (`tools/list` responses): strip the prefix from
  `result.tools[].name` — in both plain-JSON and SSE `data:` line bodies.
- **Outbound** (`tools/call` requests): add the prefix to `params.name`.
  Make it idempotent (don't double-prefix an already-prefixed name).
- Drive it from an env var (e.g. `TOOL_NAME_PREFIX=mytarget___`); empty value
  = no-op, which doubles as the Runtime-mode/rollback switch.
- **In the Lambda target**, the tool name arrives via
  `context.client_context.custom['bedrockAgentCoreToolName']` in prefixed
  form; split on `___` and take the tail.

**Gotcha (two-layer regression).** Any code path that calls the Gateway
*directly* — bypassing the facade proxy (e.g. an internal auto-resume flow) —
misses the rewrite and gets `-32602 "Unknown tool"` for bare names. It must
add the prefix itself. In the same direct path, a second bug hid behind the
first: Gateway validates `tools/call` arguments against the tool schema and
**rejects `null` for typed optional parameters** (FastMCP treated `None` as
"omitted"), and its error body isn't JSON — crashing naive response parsing.
Drop `None`-valued arguments before calling:

```python
call_args = {k: v for k, v in args.items() if v is not None}
```

## Input schema whitelist

`create_gateway_target` validates every tool's `inputSchema` and accepts
**only** these keys:

```python
_ALLOWED_SCHEMA_KEYS = {"type", "properties", "required", "items", "description"}
```

Pydantic/FastMCP-generated JSON Schema includes `title`, `default`,
`additionalProperties`, and `anyOf` (from `Optional[X]`) — all rejected with
`ParamValidationError`. Sanitize recursively:

1. Drop every key outside the whitelist.
2. **Flatten `anyOf`/`oneOf`**: merge the first non-null branch's concrete
   `type` upward. Semantics survive because optionality is already encoded in
   `required`.
3. Nodes with `properties` but no `type` get `type: "object"`.

## Lambda target: reuse live tool registrations

If your tools are registered via `@mcp.tool` decorators inside a registration
function (closures — not importable module-level functions), don't hand-write
a `TOOL_HANDLERS` dict for the Gateway target. Reuse the exact registration
path:

- On cold start, build a `FastMCP("...", stateless_http=True)` instance and
  run the same `register_all(mcp)` the Runtime used.
- Dispatch through the tool manager (`mcp._tool_manager`) — its async
  `call_tool` returns the tool's raw dict, unlike the public
  `FastMCP.call_tool` which wraps results in `TextContent`.
- **Gateway contract:** return the tool's result dict directly (no
  `{statusCode, body}` envelope). Return `{"error": ...}` dicts for unknown
  tools / exceptions.
- Use a container-image Lambda if dependencies exceed the 250 MB zip limit,
  with the build context set so shared runtime modules can be `COPY`-ed in.

### Generating the Gateway tool payload

Export the tool schema **from the live FastMCP registration** (then sanitize
per the whitelist) into a `payload.json` used as the target's
`toolSchema.inlinePayload`. Then treat this as law:

> **Regenerate `payload.json` on every tool-surface change** (adding/removing
> a tool, changing a signature). The Gateway broadcasts whatever payload it
> was registered with — a stale payload means clients see old tools and old
> schemas while your Lambda has already moved on.

Related: some MCP clients (Amazon Quick among them) **cache the tool list per
connection** — after any tool-surface change, reconnect the client before
concluding a tool is missing. When debugging "tool not visible", check in
this order: payload regenerated? → facade aggregation working? → client
reconnected?

### Custom Resource lifecycle gotchas

Registering the Gateway + target from a CloudFormation Custom Resource:

- `create_gateway` (`protocolType: MCP`, `authorizerType: CUSTOM_JWT` with
  `discoveryUrl` + `allowedClients`) → poll until `AVAILABLE` → then
  `create_gateway_target` (`credentialProviderType: GATEWAY_IAM_ROLE`).
- **Deletes must wait.** After `delete_gateway_target` / `delete_gateway`,
  poll until the resource actually 404s — a recreate while the old one is
  `DELETING` fails.
- Make creates idempotent (clean up a same-name gateway first).
- On delete, swallow **only** `ResourceNotFound`; re-raise every other
  `ClientError`, otherwise failures leak orphaned resources.

## Facade upstream dual-mode (rollback path)

Keep the facade able to front either backend: require **exactly one** of
`GATEWAY_URL` or `UPSTREAM_RUNTIME_ARN` (Runtime mode URL-encodes the ARN
into the invocations URL). Fail fast at startup if both or neither is set.
Combined with the empty-`TOOL_NAME_PREFIX` no-op, this gives a clean rollback
from Gateway to Runtime without a facade code change.
