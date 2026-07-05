# Session, Connection, and the LLM Extraction Loop

The mechanics of connecting Playwright to AgentCore Browser and driving
extraction with an LLM over fixed tool primitives.

## Connecting Playwright over signed CDP

```python
from bedrock_agentcore.tools.browser_client import browser_session
from playwright.sync_api import sync_playwright

with browser_session(region, **session_kwargs) as client:   # StartBrowserSession
    ws_url, headers = client.generate_ws_headers()           # SigV4-signed
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url, headers=headers)
        page = browser.contexts[0].pages[0]
```

`generate_ws_headers()` SigV4-signs (service `bedrock-agentcore`) the
automation WebSocket URL
(`wss://bedrock-agentcore.<region>.amazonaws.com/browser-streams/<browser_id>/sessions/<session_id>/automation`)
and returns the `Authorization` / `X-Amz-Date` / `X-Amz-Security-Token`
headers Playwright needs.

### Environment pitfalls

- **asyncio × sync Playwright:** calling `sync_playwright()` inside a running
  asyncio loop (FastMCP, FastAPI, any async host) raises greenlet errors.
  Run the entire Playwright + agent block in a dedicated
  `threading.Thread` and join it. A residual, non-fatal
  `greenlet.error: Cannot switch to a different thread` warning at teardown
  is known and harmless.
- **IAM — session APIs:** the caller needs `bedrock-agentcore:StartBrowserSession`,
  `GetBrowserSession`, `StopBrowserSession`, `ConnectBrowserAutomationStream`,
  `UpdateBrowserStream`. **ARN pitfall:** write resource ARNs in *both*
  forms — `...:aws:browser/aws.browser.v1` **and**
  `...:aws:browser-custom/aws.browser.v1`. The service authorizes against
  `browser/` even where documentation shows `browser-custom/`.
- **IAM — model streaming:** agent frameworks (e.g. Strands) call Bedrock via
  ConverseStream by default. Granting only `bedrock:InvokeModel` produces
  AccessDenied on every run; also grant
  `bedrock:InvokeModelWithResponseStream`.
- **SDK versions:** pin `bedrock-agentcore` and boto3 new enough for
  `profileConfiguration` on `start_browser_session`. Never rely on a Lambda
  runtime's bundled boto3 — it predates the `bedrock-agentcore` service
  entirely (`UnknownServiceError`).

## LLM-driven loop over fixed primitives

Architecture: a Strands (or equivalent) agent with a scraping system prompt
and exactly six tools. The model plans; the tools are immutable code.

| Tool | Implementation notes |
|---|---|
| `navigate(url)` | re-runs the SSRF guard on **every** call |
| `scroll_to_bottom()` | scrolling-element + overflow-panel aware (below) |
| `click_load_more()` | locator match + DOM-native click fallback (below) |
| `get_page_text()` | `document.body.innerText`, hard-capped (e.g. 50 k chars) |
| `screenshot()` | JPEG q70, downscaled to ~1024 px wide to control tokens, returned as an image tool-result |
| `extract_by_selector(item_selector, fields)` | fixed JS template (below) |

**Output contract:** instruct the model that its final reply must be exactly
one of: a JSON array of records, `[]`, `LOGIN_NEEDED: <host>`, or
`BLOCKED: <reason>`. Parse defensively; typed sentinels are what downstream
error handling keys on.

**Adaptive budget:** derive the step cap from the requested record count,
e.g. `max_steps = min(40, 14 + ceil(max_records / 10))`, and scale the
session timeout with it (~9–12 s per step in practice). Fixed small budgets
silently under-collect on lazy-loading feeds.

### extract_by_selector: fixed template, parameters as data

The extraction JS is a module-level constant of shape `(arg) => {...}`.
The model's selectors travel as the *argument*:

```python
page.evaluate(_EXTRACT_JS, {"sel": item_selector, "fields": fields})
```

Field specs support: a CSS string, `{"selector", "attr"}`, `{"self": true}`,
`{"self": true, "attr": "href"}`. No string interpolation into code, no
eval — the model cannot inject script. Give the prompt one worked few-shot
(e.g. X/Twitter: items `article[data-testid="tweet"]`, text
`[data-testid="tweetText"]`, time `time[datetime]` attr `datetime`).

### Scrolling on modern layouts

`window.scrollTo(0, document.body.scrollHeight)` is a **no-op on flex-root
layouts** — on YouTube, `body.scrollHeight` is 0 because the scroll root is
`<html>`. Lazy-loaded content then never enters the DOM and the scrape
returns 0 items (easily misdiagnosed as a login wall). Fix:

1. Scroll `document.scrollingElement.scrollHeight` (a strict superset of the
   body value on normal pages — zero regression risk).
2. Additionally scroll every inner overflow panel:
   `clientHeight > 200 && scrollHeight > clientHeight + 80 && overflowY ∈ {auto, scroll}`.
   Comment threads often live in an overlay panel the window never scrolls.
3. Structure loading as *scroll → wait for render → count items*, stopping
   only after 2–3 rounds with no growth — not a fixed number of scrolls.
   Where JS scrolling still proves unreliable, real input events
   (`page.mouse.wheel`) route scrolling the way a human's would; and
   `wait_for_selector` on a known item selector before extracting avoids
   racing the first render.

### click_load_more

Two-stage: try Playwright locators for common button texts first — and note
that hard-coded English texts (`"Load more"`) miss localized UIs. Then a
DOM-native fallback: `page.evaluate` searching by `aria-label` regex (e.g.
`/comment|comments|评论|留言/i`, excluding `/sort/i` to avoid sort menus) and
calling `el.click()` directly — some buttons exist but are not
scroll-into-view reachable, so `locator.click()` times out where a native
`el.click()` works.

### SSRF guard

Validate before *every* navigation, not just at job submission: HTTPS-only,
reject IP-literal hosts, resolve the hostname and reject if **any** resolved
IP is private/link-local/IMDS. The model chooses URLs mid-session; the guard
inside `navigate` is what prevents a pivot to internal endpoints.

## Error taxonomy

Classify failures into stable codes so orchestration can react (retry, park
for login, surface to user):

```
INVALID_CONFIG | URL_NOT_ALLOWED | BROWSER_SESSION_FAILED | BROWSER_TIMEOUT
BROWSER_BLOCKED | BROWSER_PARSE_FAILED | BROWSER_MAX_ITER
LOGIN_NEEDED | LOGIN_WALL_TRANSIENT
```

Mapping: boto `ClientError` → SESSION_FAILED; Playwright timeout → TIMEOUT;
step budget exhausted → MAX_ITER; unparseable model output → PARSE_FAILED
(occasionally transient — retry once before surfacing). Instruct the model to
`screenshot` before ever returning BLOCKED, so "empty page" and "CAPTCHA"
don't collapse into one code.
