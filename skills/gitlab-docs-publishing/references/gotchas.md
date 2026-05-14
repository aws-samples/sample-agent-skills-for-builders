# Gotchas and Common Mistakes

Hard-learned pitfalls from running this workflow on real GitLab projects.

## GitLab sanitizes HTML in Wiki

Don't try to paste raw HTML into Wiki — `<script>`, `<style>`, and most
`class` attributes get stripped. **Mermaid diagrams won't render and CSS is
lost.** The only places a styled HTML doc renders are:

- Direct browser open from a cloned repo.
- **GitLab Pages** (this skill's approach).
- External hosting (S3/CloudFront/Netlify).

## GitLab blob URLs don't render HTML

`https://<gitlab>/<project>/-/blob/main/docs/foo.html` shows the source code
as plain text. Pages is the only built-in way to render HTML.

## `rules: changes:` drops Pages pipeline on merge commits

```yaml
rules:
  - if: $CI_COMMIT_BRANCH == "main"
    changes: [docs/**/*]   # ← this can skip merge commits!
```

When a feature branch merges to main, the merge commit's diff may not show
"changes" and the pipeline is skipped. **Simplest fix: drop the `changes:`
constraint**, and let Pages rebuild on every push to main. The job is cheap.

## Issue URL prefill supports description + title, NOT comments on existing Issues

GitLab's `/issues/new?issue[title]=X&issue[description]=Y` works as
advertised — but there is **no URL API for pre-filling a comment on an
existing Issue**. If you want all discussion in one Issue, reviewers must
copy/paste the section reference manually. **Per-Issue-per-discussion is
cleaner** and is the default this skill ships with.

## `h3`/`h4` have no id by default

`<h3>` usually just contains the heading text. Anchor links like `#sec-4-3`
**fail silently** (the browser does nothing) if there's no matching `id`. The
injector script adds ids based on heading text — always smoke-test a sample
URL before telling reviewers.

## Mermaid figures need their own id wrapper

The mermaid diagram caption lives inside `<div class="diagram-caption">`. For
`#figure-N` to scroll correctly, the outer `<div class="diagram-frame">`
wrapper needs the `id`. The injector adds these sequentially.

## URL encoding matters for non-ASCII text

Prefilled titles and descriptions must be URL-encoded. The widget uses
`URLSearchParams`, which handles this correctly. If you build the URL
yourself with raw Chinese (or other non-ASCII) text, it will either break
the router or get partially encoded by the browser — unreliable either way.
Use the included builders.

## Title shows section id (`§sec-1`) instead of heading text (`§1.1 背景`)

The widget walks back from the selection through previous siblings to find
the **deepest enclosing heading** and uses its text in the title. If your
DOM nests headings unusually (e.g. headings live inside a section's later
descendant rather than as a preceding sibling of the content), the fallback
is the anchor `id` — which is rarely what you want in the title. Adjust
`findOwningHeading()` in `comment-widget.js` to match your structure.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Anchor only to parent section (`#sec-4`) when reviewer wanted `#sec-4-3` | Make sure the injector adds ids to `h3`/`h4`, not just `h2`. The included script does this. |
| Wrong doc URL (uses blob URL instead of Pages URL) | Re-check **Settings → Pages** and update the `pageUrl` value in `comments-issue.json`. |
| Pipeline doesn't rerun on merge commits | Remove `changes:` from the `rules:` block. |
| Reviewers expect comments to appear "in the page" | They don't — clicking opens GitLab in a new tab. Set expectations in your team announcement; "comment lives as a labelled GitLab Issue, not as inline marginalia". |
| Bubble overlaps something important when reviewer selects near the top of the viewport | The bubble positions itself 40 px above the selection's top edge. If your doc has a fixed top header, increase the offset in `repositionBubble()` or scope the widget to a content container. |
