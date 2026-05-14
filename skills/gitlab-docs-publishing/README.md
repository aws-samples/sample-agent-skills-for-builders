# GitLab Docs Publishing Skill

Publish styled HTML design docs on GitLab Pages and let reviewers file
**pre-filled GitLab Issues** for in-context discussion — by selecting any
text in the doc and clicking a small floating 💬 bubble. No OAuth, no PAT,
no in-browser API calls.

## Installation

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill gitlab-docs-publishing
```

## Quick Start

### 1. Add the Pages CI job

Copy [`templates/gitlab-ci-pages.yml`](./templates/gitlab-ci-pages.yml) into
your project's `.gitlab-ci.yml` and replace the `<VERSION>` / `<MAIN_HTML>`
placeholders. The template already runs `inject-comments.py` against the
config from Step 2.

After merge to main, the doc is served at your project's Pages URL — check
**Settings → Pages** for the exact host.

### 2. Configure the per-page Issue settings

Commit a small per-page config:

```json
// docs/v1.0.0/comments-issue.json
{
  "gitlabHost": "https://gitlab.example.com",
  "projectPath": "group/subgroup/project",
  "pageUrl": "https://<pages-url>/v1.0.0/",
  "titlePrefix": "[v1.0.0-tech-design]",
  "issueLabels": "doc-comments"
}
```

The CI template's `pages` job already invokes the injector with this config.
To run it locally for a smoke test:

```bash
python3 scripts/inject-comments.py \
  --html docs/v1.0.0/tech-design.html \
  --out  public/v1.0.0/index.html \
  --assets-dir public/v1.0.0/_assets \
  --assets-url _assets \
  --config-json docs/v1.0.0/comments-issue.json \
  --page-key v1.0.0/tech-design.html
```

The injector:

- Adds `id`s to every `<h1>`–`<h6>` (slug from heading text) and to
  `<div class="diagram-frame">` (`figure-N`) and `<div class="aws-table-wrap">`
  (`table-N`).
- Injects a `<link>` and a deferred `<script>` referencing the bundled widget.
- Copies `comment-widget.{js,css}` into `--assets-dir`.
- Is idempotent — running twice doesn't double up.

### 3. Validate before publishing

```bash
python3 scripts/validate-html.py docs/v1.0.0/tech-design.html
```

Confirms tag balance and anchor IDs.

## Reviewer experience

- The published doc renders normally — no extra buttons anywhere.
- The reviewer selects any text → a small orange **"💬 添加评论"** bubble
  appears above the selection.
- Click → new tab opens GitLab's *New Issue* page with:
  - **Title:** `[<prefix>] §<heading-text> · "<first 30 chars of selection>…"`
  - **Description:** anchor link back to the section + selection quote + a
    hidden `<!-- doc-comment-anchor-v1 ... -->` JSON block for any future
    tooling that wants to re-locate the selection.
  - **Label:** `doc-comments` (configurable).
- GitLab authenticates the reviewer with their existing browser session.
- Reviewer types under "Your comment:" and submits.

## Prerequisites

- **Python 3.8+** — standard library only.
- **GitLab project with Pages enabled** (default on `gitlab.com`; verify on
  self-hosted).
- **Project Issues enabled** so reviewers can file new issues.

## File Structure

```
skills/gitlab-docs-publishing/
├── README.md
├── SKILL.md
├── scripts/
│   ├── inject-comments.py      # Injects widget + ids into HTML
│   ├── comment-widget.js       # Selection-bubble widget (~7 KB)
│   ├── comment-widget.css      # Bubble styles (~1 KB)
│   └── validate-html.py        # Tag balance + anchor coverage
├── templates/
│   └── gitlab-ci-pages.yml     # Pages CI template
└── references/
    ├── gotchas.md              # Hard-learned pitfalls
    └── discussion-model.md     # Per-Issue vs. shared-Issue tradeoffs
```

## Customizing

### Title format

Default: `[<titlePrefix>] §<heading-text> · "<first 30 chars>…"`. The widget
walks back from the selection to find the deepest enclosing heading and uses
its text. Edit `buildTitle()` in `scripts/comment-widget.js` if you want a
different shape.

### Different figure / table classes

The injector looks for `<div class="diagram-frame">` and
`<div class="aws-table-wrap">` to add `figure-N` / `table-N` ids. If your
doc uses different classes, edit `DIAGRAM_FRAME_RE` / `TABLE_WRAP_RE` in
`scripts/inject-comments.py`.

### Shared-Issue mode

By default each click creates a new Issue. To route all clicks into one
shared Issue instead, see
[`references/discussion-model.md`](./references/discussion-model.md).

## Troubleshooting

### Pages URL 404 after merge

- Check **Settings → Pages** for the exact URL — self-hosted and
  proxy-fronted GitLab often serve at `<project>-<hash>.pages.<host>` rather
  than at `<group>.<gitlab-host>`.
- Confirm the `pages:` pipeline ran on the merge commit; if you used
  `rules: changes:`, it may have skipped. See
  [`references/gotchas.md`](./references/gotchas.md).

### Bubble doesn't appear when I select text

- Open the browser console; look for `Doc comments not yet enabled —
  missing config: …` — means `comments-issue.json` is incomplete.
- Confirm the widget loaded:
  `document.querySelector('script[src*="comment-widget"]')` should return
  the tag. If null, the inject step didn't run.
- Check that `_assets/comment-widget.js` returns `200` from the network tab.

### Title shows section id like `sec-1` instead of heading text

The widget walks back through siblings to find the deepest enclosing
heading. If your DOM nests headings unusually (e.g. headings live inside a
sibling of the content rather than as a preceding sibling), the fallback is
the anchor id. Adjust `findOwningHeading()` in `scripts/comment-widget.js`
to match your structure.

### Clicking opens GitLab but the section doesn't scroll into view

- Confirm `id`s are present on `h3`/`h4` (run `scripts/validate-html.py`).
- The `pageUrl` in `comments-issue.json` must end with `/` and match the
  actual Pages URL for this document.

### Chinese / non-ASCII titles look mangled in the Issue form

`URLSearchParams` (used by the widget) and `urllib.parse.quote` (used by
the validator) handle this correctly. If you see mangled text, you likely
constructed the URL by hand somewhere — keep using the included builders.

## License

MIT — see the repository [LICENSE](../../LICENSE) file.

## References

- [GitLab Pages documentation](https://docs.gitlab.com/ee/user/project/pages/)
- [GitLab Issues URL parameters](https://docs.gitlab.com/ee/user/project/issues/create_issues.html#using-a-url-with-prefilled-values)
- [Gotchas and common mistakes](./references/gotchas.md)
- [Discussion model tradeoffs](./references/discussion-model.md)
