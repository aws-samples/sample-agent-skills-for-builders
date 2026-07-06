# Proxy Egress and Data Normalization

Routing AgentCore Browser through an external proxy, and making scraped
records safe for analytical sinks.

## External proxy (egress IP reputation)

Heavily defended sites (Chinese e-commerce is the canonical case) score
**egress IP reputation** at the first layer: AWS and datacenter ranges are
blocked wholesale — requests get redirected to a risk handler before any
page renders. A real browser defeats fingerprint/signature layers
automatically, but nothing defeats an IP-range block except a clean egress.

`start_browser_session` supports an external proxy:

```python
proxy_configuration = {
    "proxies": [{
        "externalProxy": {
            "server": "<host>",
            "port": <port>,
            "credentials": {"basicAuth": {"secretArn": "<secrets-manager-arn>"}},
        }
    }]
}
```

Implementation guidance:

- **Credentials only by Secrets Manager ARN.** Never inline username/password
  — proxy config tends to get persisted in job configs and echoed into logs.
- Resolve configuration in layers: per-source config first, environment
  default second, none = default AWS egress.
- **Graceful degradation for older SDKs:** if the SDK doesn't accept the
  kwarg (`TypeError`), retry without the proxy and log a warning — a scrape
  from the default egress beats a hard failure.
- Verify the tunnel end-to-end by scraping an IP-echo page — the reported IP
  must be the proxy's.
- Expectations: a clean residential/ISP IP passes IP-reputation layers, but
  free proxies burn out within minutes on defended sites; production use
  needs a paid rotating pool. Content behind login (e.g. review sections
  that don't render anonymously) is a separate problem the proxy does not
  solve — see the login-profiles reference.

## Timestamp resilience

If the sink enforces non-null timestamps (Iceberg, Parquet with a required
field), one null can make an **entire batch** fail to sync while the scrape
job itself reports success — data silently vanishes. Never let a null
through and never drop a record for its timestamp. Three-level fallback:

1. **ISO parse** — normalize `Z` → `+00:00`, assume UTC for naive values.
2. **Relative-phrase parse** — scraped pages say "3 hours ago",
   "yesterday", "just now"; regex-parse into offsets (month ≈ 30 days).
   Let the model return these phrases verbatim rather than forcing it to do
   date math.
3. **Fallback** — stamp the collection time and tag
   `time_confidence="unknown"` so trend analysis can exclude these rows.

## Stable message IDs

Content-addressed ID for records that lack a platform ID:

```
sha256(source \x1f url \x1f author \x1f content \x1f epoch)[:32] + "-" + epoch
```

- Use an explicit field separator (`\x1f`) — plain concatenation lets field
  boundaries shift and two different records collide.
- Normalize the timestamp **before** hashing so `Z` vs `+00:00` doesn't
  produce two IDs for one record.
- Fold native platform IDs (review ID, snowflake) into the hash when
  available — it protects against collisions when timestamp parsing failed
  and epoch is 0 for many records by the same author.

## Cross-run dedup (periodic scrapes)

Scheduled scraping re-fetches the same items every run. Dedup **before**
enrichment (sentiment tagging, embedding) — that's where the money goes:

- Keep an already-seen ledger keyed by message ID (a vector store with
  ID-keyed `get` works well: batch existence checks, written at collect
  time so it's fresher than the analytical table).
- **Degrade open:** on any ledger error, keep the whole batch. Dedup here is
  a cost optimization; correctness belongs to the read layer (e.g.
  `PARTITION BY message_id` dedup at query time).
- Flush collected records even when a later step fails (partial-on-error) —
  a wall hit at item 80 shouldn't discard items 1–79, *unless* the login
  probe says the data is anonymous noise (see login-profiles reference).
