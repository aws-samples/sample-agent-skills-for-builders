# GitLab Docs Publishing Skill

Publish styled HTML design docs on GitLab Pages and inject per-section 💬
buttons that open pre-filled GitLab Issues — so reviewers can comment in
context without leaving the doc.

## Installation

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill gitlab-docs-publishing
```

## Quick Start

### 1. Add the Pages CI job

Copy [`templates/gitlab-ci-pages.yml`](./templates/gitlab-ci-pages.yml) into
your project's `.gitlab-ci.yml` and replace the `<VERSION>` / `<MAIN_HTML>`
placeholders:

```yaml
pages:
  stage: deploy
  image: alpine:3.20
  script:
    - mkdir -p public/v1.0.0
    - cp docs/v1.0.0/tech-design.html public/v1.0.0/index.html
  artifacts:
    paths:
      - public
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

After merge to main, the doc is served at
`https://<group>.<gitlab-host>/<project>/v1.0.0/`. Self-hosted GitLab may use
a different Pages host — check **Settings → Pages** for the exact URL.

### 2. Inject discuss buttons

```bash
python3 scripts/inject-discuss-buttons.py \
  --html docs/v1.0.0/tech-design.html \
  --doc-url 'https://<group>.<gitlab-host>/<project>/v1.0.0/' \
  --issue-new-url 'https://<gitlab>/<path>/<project>/-/issues/new' \
  --title-prefix '[v1.0.0-tech-design]'
```

Every `<h2>/<h3>/<h4>` gets an `id` (if missing) and a 💬 button; every
mermaid `diagram-frame` gets `id="figure-N-M"`; every `aws-table-wrap` gets
`id="table-N-M"`. The script is idempotent — re-running updates buttons in
place.

### 3. Validate before publishing

```bash
python3 scripts/validate-html.py docs/v1.0.0/tech-design.html
```

Confirms tag balance and that every button anchor has a matching `id` in the
DOM. Exits non-zero if any anchor is broken — wire it into CI if you want.

## Prerequisites

- **Python 3.8+** — standard library only, no pip installs needed.
- **GitLab project with Pages enabled** (default on `gitlab.com`; verify on
  self-hosted).
- **Project Issues enabled** for the per-Issue discussion flow.

## File Structure

```
skills/gitlab-docs-publishing/
├── README.md                        # This file
├── SKILL.md                         # Skill metadata & reference
├── scripts/
│   ├── inject-discuss-buttons.py    # Adds 💬 buttons to HTML
│   └── validate-html.py             # Tag balance + anchor coverage
├── templates/
│   └── gitlab-ci-pages.yml          # Pages CI template
└── references/
    ├── gotchas.md                   # Hard-learned pitfalls
    └── discussion-model.md          # Per-Issue vs. shared-Issue tradeoffs
```

## What Gets Injected

| HTML element | Gets |
|--------------|------|
| `<h2 class="aws-sec-title">` | `id="sec-N"` + 💬 button |
| `<h3 class="aws-sub">` / `<h4 class="aws-subsub">` | `id` derived from heading text + 💬 button |
| `<div class="diagram-frame">` (mermaid figure) | `id="figure-N-M"` + inline 💬 in caption |
| `<div class="aws-table-wrap">` | `id="table-N-M"` + 💬 below the table |

Clicking a 💬 button opens GitLab's new-Issue page with a pre-filled title
(e.g. `[v1.0.0-tech-design] §4.3 Caching Strategy`) and description body
containing the anchor URL back to the exact section.

## Customizing

### Different HTML class names

Pass `--table-wrap-class` if your doc uses a class other than
`aws-table-wrap`:

```bash
python3 scripts/inject-discuss-buttons.py \
  --html my-doc.html \
  --table-wrap-class my-table-wrap \
  ...
```

Heading-class assumptions (`aws-sec-title` / `aws-sub` / `aws-subsub`) are
currently baked into the script — fork and edit the regexes if your doc uses
a different convention.

### Skip appendix sections

```bash
--skip-h2-titles '相关文档' 'Related Documents' 'Appendix'
```

Headings matching these titles won't get 💬 buttons.

### Shared-Issue mode (one Issue for all discussions)

By default each click creates a new Issue. For a single shared Issue, see
[`references/discussion-model.md`](./references/discussion-model.md).

## Troubleshooting

### Pages URL 404 after merge

- **Settings → Pages** to confirm the exact URL for your instance (self-hosted
  GitLab often uses `<project>-<hash>.pages.<host>`).
- Check the `pages:` pipeline ran on the merge commit — if you used
  `rules: changes:` it may have skipped. See
  [`references/gotchas.md`](./references/gotchas.md).

### Clicking a button takes me to the section heading but not the subsection

The injector must add `id`s to `h3`/`h4`, not just `h2`. Run
`scripts/validate-html.py` — it lists any anchor whose `id` is missing.

### Chinese / non-ASCII titles look mangled in the Issue form

Make sure you ran the injector script, which URL-encodes via
`urllib.parse.quote(text, safe='')`. Building the URL yourself with raw
non-ASCII text will break in some browsers.

### Buttons don't appear at all

Confirm your HTML uses the expected classes (`aws-sec-title`, `aws-sub`,
`aws-subsub`, `diagram-frame`, `aws-table-wrap`). Run a dry run to see
counts:

```bash
python3 scripts/inject-discuss-buttons.py --dry-run \
  --html ... --doc-url ... --issue-new-url ...
```

## License

MIT — see the repository [LICENSE](../../LICENSE) file.

## References

- [GitLab Pages documentation](https://docs.gitlab.com/ee/user/project/pages/)
- [GitLab Issues URL parameters](https://docs.gitlab.com/ee/user/project/issues/create_issues.html#using-a-url-with-prefilled-values)
- [Gotchas and common mistakes](./references/gotchas.md)
- [Discussion model tradeoffs](./references/discussion-model.md)
