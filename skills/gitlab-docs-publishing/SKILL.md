---
name: gitlab-docs-publishing
description: Publish HTML/Markdown design documents on GitLab Pages with selection-driven discussion. Reviewers select any text in the published doc; a floating 💬 bubble opens a prefilled GitLab Issue (title + anchor link + selection quote + label) in a new tab. GitLab handles auth via the user's existing session — no OAuth, no PAT, no API calls. Works on gitlab.com, self-hosted, and proxy-fronted GitLab.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "2.0.0"
---

# GitLab Docs Publishing

Publish styled HTML design docs on GitLab Pages and let reviewers file
in-context feedback by **selecting any text** and clicking a floating 💬
bubble — which opens a pre-filled GitLab Issue in a new tab. Zero external
services, zero in-page API calls.

Standalone HTML design docs are great for reading but miss two things GitLab
does not provide out of the box: a public URL (GitLab renders `.html` blobs
as source code, not as a page) and an in-context comment thread tied to the
exact piece of prose a reviewer wants to discuss. This skill bolts both on
using only free GitLab features:

- **GitLab Pages** auto-publishes HTML on every merge to main.
- **Selection-driven 💬 bubble** — a small JS widget watches text selection.
  On click, it navigates the browser to GitLab's "New issue" page with title
  + description + label prefilled. GitLab authenticates the user with their
  existing session cookie.

## When to Apply

- Publishing a technical design doc (HTML or Markdown) for team review.
- Teammates complain they have to `git clone` to see the styled HTML version.
- Meeting feedback gets lost because there's no place to write it against
  specific sentences.
- An HTML visual doc has been generated from source Markdown and now needs
  a distribution channel with feedback affordances.

**Not for:**

- Documents that belong in GitLab Wiki (Wiki renders Markdown natively and
  has built-in comments).
- Single-reviewer review — use MR line comments instead.
- External/public audiences who do not have GitLab accounts.

## How It Works

```
docs/<v>/foo.html
   │
   │ inject-comments.py:
   │   1. Strip any pre-existing in-page widgets
   │   2. Add ids to headings/figures/tables
   │   3. Inject <link>+<script> for the selection-bubble widget
   │   4. Copy comment-widget.{js,css} into <assets-dir>
   ↓
public/<v>/index.html  ──▶  GitLab Pages CI publishes public/
                              ↓
                     Reviewer opens published URL
                     Selects any text → 💬 bubble appears
                     Clicks → new tab on GitLab issues/new
                     with title + description + label prefilled
                     GitLab uses existing session cookie
                     Reviewer types → submits → labelled Issue created
```

## Usage

### Step 1 — Add the Pages CI job

Copy [`templates/gitlab-ci-pages.yml`](./templates/gitlab-ci-pages.yml) into
your project's `.gitlab-ci.yml` and replace `<VERSION>` / `<MAIN_HTML>`.
The template already runs the inject step (Step 2 explains its config).
After merge to main, the doc is served at the project's Pages URL — check
**Settings → Pages** for the exact host.

### Step 2 — Configure the per-page Issue settings

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

The CI template invokes the injector with this config. The injector:

- Adds `id` attributes to every `<h1>`–`<h6>` (slug from heading text),
  `<div class="diagram-frame">` (`figure-N`), and `<div class="aws-table-wrap">`
  (`table-N`) so anchor URLs resolve.
- Injects `<link rel="stylesheet">` and `<script defer>` referencing the
  bundled widget assets.
- Copies `comment-widget.{js,css}` into `--assets-dir`.
- Is idempotent — re-running on the same HTML doesn't double up.

### Step 3 — Validate before publishing

```bash
python3 scripts/validate-html.py docs/v1.0.0/tech-design.html
```

Confirms tag balance and that anchor IDs are present.

### What the reviewer sees

- The published doc renders normally — no extra buttons or chrome anywhere.
- Selecting any text shows a small orange "💬 添加评论" / "💬 Add comment"
  bubble above the selection.
- Clicking opens a new tab on GitLab's New Issue page. Title is
  `[<prefix>] §<heading-text> · "<first 30 chars of selection>…"`.
  Description contains an anchor link (back to the section) plus the
  selection quote, plus a hidden anchor JSON block for forward-compat tooling.
- The reviewer types their comment under "Your comment:" and submits.

### Deployment Checklist

- [ ] HTML generated; tag balance and anchors validated.
- [ ] `.gitlab-ci.yml` includes the `pages` job and the inject step.
- [ ] `comments-issue.json` is committed and has the right `gitlabHost`,
      `projectPath`, and `pageUrl`.
- [ ] Selecting text on the published page shows the bubble.
- [ ] Clicking the bubble opens GitLab's New Issue page with prefilled
      title, description, and label.
- [ ] After submitting, the resulting Issue has a working anchor link in
      its description that scrolls back to the right section.

## References

- [Gotchas and common mistakes](./references/gotchas.md)
- [Discussion model: per-Issue vs. shared Issue](./references/discussion-model.md)
- [GitLab Pages documentation](https://docs.gitlab.com/ee/user/project/pages/)
- [GitLab Issues URL parameters](https://docs.gitlab.com/ee/user/project/issues/create_issues.html#using-a-url-with-prefilled-values)
