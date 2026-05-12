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

`https://<gitlab>/<project>/-/blob/main/docs/foo.html` shows the source code as
plain text. Pages is the only built-in way to render HTML.

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
advertised — but there is **no URL API for pre-filling a comment on an existing
Issue**. If you want all discussion in one Issue, reviewers must copy/paste the
section reference manually. **Per-Issue-per-discussion is cleaner** and is the
default this skill ships with.

## `h3`/`h4` have no id by default

`<h3>` usually just contains the heading text. Anchor links like `#sec-4-3`
**fail silently** (the browser does nothing) if there's no matching `id`. The
injector script adds ids based on heading text — always smoke-test a sample URL
before telling reviewers.

## Mermaid figures need their own id wrapper

The mermaid diagram caption lives inside `<div class="diagram-caption">`. For
`#figure-4-2` to scroll correctly, the outer `<div class="diagram-frame">`
wrapper needs the `id`. The injector extracts the figure number from the
caption text (e.g. "Figure 4-2") to build the id.

## URL encoding matters for non-ASCII text

Prefilled titles and descriptions must be URL-encoded with
`urllib.parse.quote(text, safe='')`. A raw Chinese (or other non-ASCII) string
in the URL will either break the router or get partially encoded by the
browser — unreliable either way. The injector already handles this; preserve
this behavior if you fork the script.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Buttons too subtle (gray, low opacity) | Use a vivid accent color (AWS orange, brand color) with white text and a subtle shadow — reviewers need to see them. |
| Anchor only to parent section (`#sec-4`) when user wanted `#sec-4-3` | Make sure the injector adds ids to `h3`/`h4`, not just `h2`. |
| Wrong doc URL (uses blob URL instead of Pages URL) | Re-check **Settings → Pages** and update the `--doc-url` flag. |
| Pipeline doesn't rerun on merge commits | Remove `changes:` from the `rules:` block. |
| Discuss button JS fails silently | Don't use complex JS. A plain `<a href="...issues/new?...">` with `target="_blank"` is robust and needs no JS runtime. |
