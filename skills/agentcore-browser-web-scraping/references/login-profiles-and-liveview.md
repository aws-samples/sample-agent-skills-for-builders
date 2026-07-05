# Login Profiles, Live-View Login, and Wall Detection

Reusable login state for scraping login-gated sites, with credentials that
never leave AWS.

## Why profiles + live-view

Login-walled sites (X/Twitter shows ~2 items anonymously) need
authenticated sessions. Asking users to export cookies is unsafe and
fragile. Instead: the user logs in **once** with a dedicated scraping
account, inside the cloud browser, watched through a DCV live-view page.
The session is saved to an **AgentCore Browser Profile**; every later scrape
starts Chromium with that profile already logged in:

```python
browser_session(region, profile_configuration={"profileIdentifier": profile_id})
```

Cookies and tokens stay inside AWS — they never transit the chat, logs, or
your database.

## Profile creation and reuse

- **Naming constraint:** `[a-zA-Z][a-zA-Z0-9_]{0,47}` — no dots or hyphens.
  Sanitize host-derived names (`browser_login-x.com` →
  `myapp_browser_login_x_com`).
- **Idempotency:** derive the profile name deterministically from the target
  host; on `ConflictException` from `create_browser_profile`, look the
  existing profile up via `list_browser_profiles` (paginated) and reuse it.
- **IAM:** `CreateBrowserProfile` / `ListBrowserProfiles` do not support
  resource-level scoping — grant them on `Resource: "*"` in a separate
  statement.
- **Key consistency:** every component that maps host → profile must
  normalize identically (lowercase, strip `www.`). Two normalizers = two
  different profile records = login that "doesn't stick".
- Derive the host **server-side from the source URL**, never from model
  output — models report `twitter.com` when the page is `x.com`, add ports,
  or name CDN domains, and the profile key never matches again.

## Live-view login flow

```
1. Mint one-time token (DB row, TTL 1800s) → return {facade}/browser-login?t=<token>
2. GET page handler:
     validate token → lazily create profile if missing
     → start_browser_session(browserIdentifier="aws.browser.v1",
         sessionTimeoutSeconds=1800, viewPort=1280x720,
         profileConfiguration=..., enterprisePolicies=...)
     → persist session_id on the token row
     → presign live-view URL → render DCV page
3. User logs into the target site inside the streamed browser
4. POST (user clicks "done"):
     save_browser_session_profile(profileId, browserId, sessionId)
     → stop_browser_session → mark credential READY → auto-resume parked work
```

Hard-won details:

- **Presigning:** SigV4 *query* auth (`expires=300`) on
  `https://bedrock-agentcore.<region>.amazonaws.com/browser-streams/<browser_id>/sessions/<session_id>/live-view`.
  The 300 s is the **DCV WebSocket handshake window, not viewing time** —
  once connected, the stream lives until the session times out, so no
  refresh route is needed. The URL is a stream endpoint; a plain browser GET
  returns 501 — it only works through the DCV client.
- **DCV embed:** vendor the DCV Web Client UMD bundle and serve it from the
  same Lambda (guard against path traversal). Two gotchas: pass
  `enableWebCodecs: true` (default WebGL decoding black-screens for users
  with hardware acceleration off), and `baseUrl` must be an **absolute**
  URL (`location.origin + "/browser-login"`) — a relative path gets
  re-resolved inside DCV's blob worker and every asset 404s, which presents
  as video-works-but-keyboard/mouse-dead.
- **Save before stop.** `save_browser_session_profile` requires a *live*
  session; it snapshots the whole profile (overwrite, not merge).
- **Token TTL:** 600 s is too short — login + 2FA regularly exceeds 10
  minutes and the final "done" POST fails with an expired token. Use 1800 s,
  matching the session timeout.
- **Lazily create the profile in the GET handler** if it doesn't exist yet:
  the first anonymous scrape that hits a wall parks *before* any profile
  exists, and without lazy creation the user's login has nowhere to be saved
  (the POST 409s and the login is lost).

## Google SSO: third-party cookies

Cloud Chromium blocks third-party cookies by default → "Sign in with
Google" opens, authenticates, and then **fails silently** — only visitor
cookies land, the site still shows the logged-out state.

Fix with Chromium **enterprise policies** delivered from S3:

```json
{ "BlockThirdPartyCookies": false,
  "DefaultCookiesSetting": 1,
  "CookiesAllowedForUrls": ["[*.]google.com", "[*.]x.com", "..."] }
```

passed as `enterprisePolicies=[{"type": "RECOMMENDED", "location": {"s3":
{"bucket": ..., "prefix": ...}}}]` to `start_browser_session`.

**Apply the same policies to login sessions AND scrape sessions** — SSO
state saved under relaxed cookies breaks when replayed under default
policy. Scrape sessions only need it when a profile is attached. Consider
hardening additions: `SyncDisabled: true`, `BrowserSignin: 0` — otherwise a
personal Google account can sync private history/bookmarks *into* the
scraping profile.

If SSO still fails after the cookie fix, the remaining failure modes are on
Google's side: automation fingerprinting ("this browser may not be secure" /
`disallowed_useragent`) and the SSO popup opening as a separate window
target. Both are mitigated by the live-view design itself — a human drives a
real rendered browser — but keep the viewport reasonably large (≥1280×720)
so the popup isn't off-screen, and if Google balks at the target site's SSO
button, log in at `accounts.google.com` directly first, then return and
click "Sign in with Google". Use a dedicated scraping account either way;
scraping logged-in areas may violate the target site's ToS, and account
bans are the operational risk to plan for.

## Login-wall detection without false positives

Core insight from production: **hitting a wall ≠ the stored login is
dead.** A saved login stayed valid across 57 hours and four different AWS
egress IPs while anonymous views still hit overlays. Naively expiring the
profile on every wall forces users to re-login constantly. Three layers:

1. **Pre-flight gate** (before any browser session): if the source is
   flagged `login_required` or the host is in a known login-walled list
   (`x.com`, `twitter.com`, `reddit.com`, `instagram.com` — keep such lists
   minimal; YouTube comments are anonymously scrapable and force-gating them
   blocks scrapes that would succeed): profile READY → attach and proceed;
   otherwise return a login URL immediately, no wasted session.
2. **In-scrape sentinel:** the model replies `LOGIN_NEEDED: <host>`.
   Downgrade the sentinel when data is present — real posts + login overlay
   coexist, and data wins. Add a prose fallback (regex for login-wall
   phrasing near "required/blocked" in the model's explanation) to rescue
   runs where the model ignored the sentinel format.
3. **Active probe (the decider):** capture `context.cookies()` before the
   session closes; on a wall, replay them against a login-*sensitive*
   endpoint and ask the server:
   - status-based probes (e.g. Reddit `/api/me.json`): 200 = VALID,
     401/403 = INVALID;
   - redirect-based probes: follow **zero** redirects and match the
     `Location` target (some sites 302 between two logged-in URLs); use an
     HTTP request context, not page rendering, to bypass front-end JS;
   - missing key cookie (`auth_token` / `sessionid` / `SID`) = INVALID
     locally, no network needed;
   - **degrade open**: any probe error → UNKNOWN; never expire a login on
     uncertainty.

Verdict routing: VALID → `LOGIN_WALL_TRANSIENT` (keep collected data, do
not park, do not expire); INVALID/UNKNOWN/no-profile → `LOGIN_NEEDED`
(discard the handful of pre-wall noise records, park the task).

## Parking and auto-resume

When a scrape parks on `LOGIN_NEEDED`:

- Flag the source `login_required=true` so the pre-flight gate catches the
  next attempt (if config spans multiple tables, resolve each explicitly — a
  silent no-op write here re-runs anonymous scrapes in a loop).
- Flip the stored credential READY → EXPIRED **only on probe verdict
  INVALID** (record when and why, for passive monitoring).
- Mint the login token with a `resume_action` (e.g. `resume_task <id>`); the
  login-completion POST then automatically resumes the parked task —
  guarded by compare-and-set on task status so a zombie worker can't revive
  a finished task.
- Resume paths must **re-look-up the profile by host** from the credential
  store — a resumed task may predate the profile binding and would
  otherwise re-run anonymous, hit the wall, and park again forever.
