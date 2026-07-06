---
name: agentcore-browser-web-scraping
description: Build production web scraping on Bedrock AgentCore Browser — connect Playwright over signed CDP WebSocket, drive extraction with an LLM agent over fixed tool primitives (navigate, scroll, extract-by-selector, screenshot), reuse login state via Browser Profiles with a DCV live-view login flow, detect login walls without false positives, and route through an external proxy. Use when scraping dynamic or login-gated sites (X/Twitter, Reddit, Instagram, YouTube, forums) with AgentCore Browser, when scraped results come back empty on lazy-loaded pages, when Google SSO fails silently in the cloud browser, or when a target site blocks AWS egress IPs.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# AgentCore Browser Web Scraping

Amazon Bedrock AgentCore Browser gives you a managed cloud Chromium — no
crawler fleet, no resident containers, per-session billing, natural
isolation. This skill captures a production scraping architecture built on
it: an LLM agent decides *what* to do on the page, but only through **fixed
code primitives** it can parameterize, never arbitrary scripts. Login state
lives in Browser Profiles that users populate once through a live-view
session, so credentials never transit the conversation.

```
Collector (Python, worker thread)
  ├─ browser_session(region, profile_configuration=..., proxy_configuration=...)
  │      └─ StartBrowserSession → generate_ws_headers() (SigV4)
  │             └─ playwright chromium.connect_over_cdp(ws_url, headers)
  └─ Strands Agent (LLM) with 6 fixed tools:
        navigate / scroll_to_bottom / click_load_more /
        get_page_text / screenshot / extract_by_selector
```

## When to Apply

Reference this skill when:

- Scraping dynamic, JS-rendered, or lazy-loading pages (social feeds,
  forums, review sites) with AgentCore Browser + Playwright.
- Scraping sites that require login (X/Twitter, Reddit, Instagram) and you
  need reusable login state that never leaves AWS.
- Scrapes return 0 items on pages that clearly have content — usually a
  scroll-container or login-wall misdiagnosis, both covered here.
- Google SSO inside the cloud browser silently fails (third-party cookies).
- The target site blocks AWS egress IPs and you need an external proxy.

**Not for:** general AgentCore Browser service overview or session APIs —
see the `aws-agentic-ai` skill's Browser service docs for that.

## How It Works

### 1. Session, connection, and the LLM-driven extraction loop

Connect Playwright to the managed browser over a SigV4-signed CDP WebSocket,
then let an LLM agent drive a bounded tool loop. Key decisions:

- **LLM decides, code executes.** A hand-written script per site doesn't
  scale across arbitrary DOMs; raw LLM-generated JS is an injection surface.
  The middle path: six fixed tools, the model only supplies parameters.
- **`extract_by_selector`**: a constant JS extraction template evaluated with
  the model's CSS selectors passed as *data* arguments — zero string
  concatenation, zero eval. Preserves item boundaries and attributes that a
  flat `innerText` dump loses.
- **`screenshot`** (downscaled JPEG returned as an image tool-result) lets
  the model *see* the page and distinguish "genuinely empty" from login
  wall / CAPTCHA / cookie banner before declaring failure.
- **Adaptive step budget**: scale the agent's max tool-steps (and the session
  timeout) with the requested record count — lazy feeds yield 10–20 items
  per scroll, so a fixed small budget silently under-collects.
- **Scrolling that actually works**: `document.body.scrollHeight` is 0 on
  flex layouts (YouTube) — scroll `document.scrollingElement` instead, and
  also iterate inner overflow panels; comments often live in an overlay
  that window scrolling never touches.
- **SSRF guard**: HTTPS-only, no IP literals, private ranges and IMDS
  blocked for the hostname *and every resolved IP* — re-validated inside the
  `navigate` tool on every call, so the model can't pivot mid-session.

See [references/session-and-extraction.md](references/session-and-extraction.md)
— includes IAM specifics (the `browser/` vs `browser-custom/` ARN pitfall,
`InvokeModelWithResponseStream`), the asyncio × sync-Playwright worker-thread
requirement, and the error-code taxonomy.

### 2. Login state: Browser Profiles + live-view login

Users log in **once** inside the cloud browser via a DCV live-view page; the
session's cookies/tokens are saved to an AgentCore Browser Profile and reused
by every later scrape (`profile_configuration={"profileIdentifier": ...}`).
Credentials never appear in the conversation or your database.

Flow: mint a one-time URL token → `start_browser_session` with the profile →
presign the `live-view` stream endpoint (SigV4 query auth) → embed the DCV
Web Client → on completion `save_browser_session_profile` **then**
`stop_browser_session` (that order — save requires a live session).

The subtle part is **login-wall detection without false positives**. Hitting
a wall does *not* mean the stored login is dead (a login can stay valid
across days and multiple egress IPs while an overlay still blocks anonymous
views). Use three layers: a pre-flight gate for known login-walled hosts, an
in-scrape sentinel from the model, and an **active probe** that replays the
session's cookies against a login-sensitive endpoint to ask the server
directly — only a definitive INVALID expires the stored profile.

See [references/login-profiles-and-liveview.md](references/login-profiles-and-liveview.md)
— includes profile-name constraints and idempotent creation, DCV embed
gotchas (WebCodecs, absolute `baseUrl`), the Google SSO third-party-cookie
fix via Chromium `enterprisePolicies`, and the parked-task auto-resume
pattern.

### 3. Proxy egress and data normalization

- **External proxy**: sites that score egress-IP reputation block AWS ranges
  wholesale. `start_browser_session` accepts a `proxyConfiguration` with an
  `externalProxy` (server, port, credentials **by Secrets Manager ARN only**
  — never inline). Fall back gracefully to the default egress when
  unconfigured.
- **Timestamp resilience**: if your sink requires non-null timestamps
  (Iceberg/Parquet), a single null can poison an entire batch *silently*.
  Parse ISO → parse relative phrases ("3 hours ago") → fall back to
  collection time tagged `time_confidence="unknown"`. Never drop, never null.
- **Stable message IDs + cross-run dedup**: content-hash IDs with explicit
  field separators, native platform IDs folded in when available; periodic
  scrapes dedup against an already-seen ledger *before* paying for
  enrichment, degrading open on ledger errors.

See [references/proxy-and-data-normalization.md](references/proxy-and-data-normalization.md).

## Usage

Adoption checklist:

1. Pin SDK versions: `bedrock-agentcore` and a boto3 recent enough to know
   `profileConfiguration` / the `bedrock-agentcore` service (Lambda's bundled
   boto3 is too old — bundle your own).
2. Run sync Playwright in a dedicated worker thread if your host framework
   owns an asyncio loop.
3. Grant both `bedrock:InvokeModel` **and** `InvokeModelWithResponseStream`
   to the agent's model, and write Browser session ARNs in both `browser/`
   and `browser-custom/` forms.
4. Constrain the model's final output to a strict contract (JSON array, `[]`,
   or typed sentinels like `LOGIN_NEEDED: <host>` / `BLOCKED: <reason>`) and
   parse defensively.
5. Derive hostnames for profile lookups **server-side from the source URL**,
   never from model output.
6. Apply the same `enterprisePolicies` to login sessions *and* scrape
   sessions — SSO cookies saved under one policy break under another.

## References

- [Session, connection, and LLM extraction loop](references/session-and-extraction.md)
- [Login profiles, live-view login, wall detection](references/login-profiles-and-liveview.md)
- [Proxy egress and data normalization](references/proxy-and-data-normalization.md)
- [Amazon Bedrock AgentCore Browser](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html)
- [AgentCore samples — browser with proxy](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
