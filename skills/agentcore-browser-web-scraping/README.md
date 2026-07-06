# AgentCore Browser Web Scraping Skill

Production patterns for web scraping on Bedrock AgentCore Browser: Playwright
over signed CDP, an LLM agent driving fixed extraction primitives
(selector-based extraction, adaptive scrolling, screenshots), reusable login
state via Browser Profiles with DCV live-view login, login-wall detection
with active probes, external proxy egress, and scrape-data normalization
(timestamps, stable IDs, dedup).

## Installation

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill agentcore-browser-web-scraping
```

See [SKILL.md](./SKILL.md) for the architecture and adoption checklist. The
`references/` directory contains deep dives on session/extraction mechanics,
login profiles + live-view, and proxy/data normalization.
