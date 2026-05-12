---
name: gitlab-docs-publishing
description: Publish HTML/Markdown design documents on GitLab with reviewer comments. Use when you need GitLab Pages auto-deploy, Issue-based discussion buttons with URL prefill, precise anchors for every heading/figure/table, and per-discussion Issue-creation links for any GitLab project hosting shareable, commentable technical design docs.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# GitLab Docs Publishing

Publish styled HTML design docs on GitLab so the team can read them in a browser
and file per-section feedback as Issues — with zero external services.

Standalone HTML design docs are great for reading but miss two things GitLab
does not provide out of the box: a public URL (GitLab renders `.html` blobs as
source code, not as a page) and an in-context comment thread tied to each
section, figure, or table. This skill bolts both on using only free GitLab
features:

- **GitLab Pages** auto-publishes HTML on every merge to main → public URL like
  `https://<group>.<gitlab-host>/<project>/`.
- **Per-section 💬 buttons** create pre-filled Issues with title, anchor link,
  and description template — reviewers click, write feedback, submit.

Works on `gitlab.com`, self-hosted GitLab, and internal GitLab instances.

## When to Apply

Reference this skill when:

- Publishing a technical design doc (HTML or Markdown) for team review.
- Teammates complain they have to `git clone` to see the styled HTML version.
- Meeting feedback gets lost because there's no place to write it against
  specific sections.
- You want reviewers to file Issues per topic instead of one giant email thread.
- An HTML visual doc has been generated from source Markdown (a common output
  of design-doc workflows) and now needs a distribution channel.

**Not for:**

- Documents that belong in GitLab Wiki (Wiki renders Markdown natively and has
  built-in comments).
- Single-reviewer review — use MR line comments instead.
- External/public audiences who do not have GitLab accounts.

## How It Works

1. **Enable Pages** — Add `.gitlab-ci.yml` with a `pages` job that copies your
   HTML under `public/` on every push to main. Template:
   [`templates/gitlab-ci-pages.yml`](./templates/gitlab-ci-pages.yml).
2. **Inject discuss buttons** — Run `scripts/inject-discuss-buttons.py` on the
   generated HTML. Every `<h2>/<h3>/<h4>` gets an `id` (if missing) and a 💬
   button; every mermaid `diagram-frame` gets `id="figure-N-M"`; every
   `aws-table-wrap` gets `id="table-N-M"`.
3. **Validate** — Run `scripts/validate-html.py` to confirm tag balance and
   that every button anchor has a matching `id`.
4. **Merge and share** — Push to main, wait for the Pages pipeline, then share
   the Pages URL. Reviewers click 💬 buttons to file per-section Issues.

## Usage

### 1. Add the Pages CI job

Copy [`templates/gitlab-ci-pages.yml`](./templates/gitlab-ci-pages.yml) into
your project's `.gitlab-ci.yml` and replace `<VERSION>` / `<MAIN_HTML>`:

```yaml
pages:
  stage: deploy
  image: alpine:3.20
  script:
    - mkdir -p public/v1.0.0
    - cp docs/v1.0.0/tech-design.html public/v1.0.0/index.html
    - cp docs/v1.0.0/*.md public/v1.0.0/ 2>/dev/null || true
  artifacts:
    paths:
      - public
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

After merge, the doc is served at `https://<group>.<gitlab-host>/<project>/v1.0.0/`.
Self-hosted GitLab instances may use a different Pages host — check
**Settings → Pages** in the project for the exact URL.

### 2. Inject discuss buttons

```bash
python3 scripts/inject-discuss-buttons.py \
  --html docs/v1.0.0/tech-design.html \
  --doc-url 'https://<group>.<gitlab-host>/<project>/v1.0.0/' \
  --issue-new-url 'https://<gitlab>/<path>/<project>/-/issues/new' \
  --title-prefix '[v1.0.0-tech-design]'
```

The script is idempotent — re-running it updates buttons in place rather than
duplicating them.

### 3. Validate before publishing

```bash
python3 scripts/validate-html.py docs/v1.0.0/tech-design.html
```

Confirms tag balance and that every button anchor (`#sec-4-3`, `#figure-4-2`,
`#table-4-1`) has a matching `id` in the DOM.

### Deployment checklist

- [ ] HTML generated; tag balance and anchors validated.
- [ ] `.gitlab-ci.yml` includes the `pages` job.
- [ ] Injector ran; 💬 buttons visible next to every heading, figure, and table.
- [ ] Clicking a sample 💬 button opens the GitLab new-Issue page with the
  correct title and body.
- [ ] After merge to main, the Pages URL serves the doc.
- [ ] Anchor round-trip works: click a 💬 button, open the resulting Issue,
  follow the link in the description → lands on the right section.

## References

- [Gotchas and common mistakes](./references/gotchas.md) — hard-learned
  pitfalls: Wiki HTML sanitization, `rules: changes:` dropping merge commits,
  anchor coverage on `h3`/`h4`, URL encoding.
- [Discussion model: per-Issue vs. shared Issue](./references/discussion-model.md)
  — tradeoffs and how to switch modes.
- [GitLab Pages documentation](https://docs.gitlab.com/ee/user/project/pages/)
- [GitLab Issues URL parameters](https://docs.gitlab.com/ee/user/project/issues/create_issues.html#using-a-url-with-prefilled-values)
