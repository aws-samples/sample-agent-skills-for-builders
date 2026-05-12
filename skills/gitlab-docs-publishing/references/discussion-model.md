# Discussion Model: Per-Issue vs. Shared Issue

Pick one model upfront before publishing the doc — mixing both on the same
doc confuses reviewers.

## Per-discussion Issue (recommended, default)

Each click on a 💬 button creates a **new GitLab Issue** with the section
reference in the title and an anchor link in the description.

- **Title:** `[doc-tag] §4.3 section name`
- **Description:** contains an anchor URL back to the section.
- **Searchable:** Issues are assignable, labelable, and closable per topic.
- **Downside:** an active review can produce dozens of Issues.

This is the default model the included `inject-discuss-buttons.py` script
produces.

## Shared Issue (simpler)

All 💬 clicks jump to one central Issue (e.g. `#1`). The button copies the
section reference to the clipboard; the reviewer pastes it as a new comment on
the shared Issue.

- **Pros:** one Issue to watch, fewer notifications.
- **Cons:** threading breaks when many parallel discussions run at once; you
  lose the ability to track/close topics individually.

To switch to this mode, edit the URL template at the top of
`scripts/inject-discuss-buttons.py` to point at a single existing Issue
instead of `/issues/new`. You'll also need to change the button copy from
"create Issue" to "copy reference and comment on #N".

## Choosing

| Situation | Pick |
|-----------|------|
| Formal design review, several reviewers, each topic may stay open for days | Per-Issue |
| Informal walkthrough, one short review cycle, minimal bookkeeping desired | Shared Issue |
| Reviewers are external or junior and are likely to forget to file Issues | Shared Issue |
| Each discussion needs an assignee, label, or closes-via-MR tracking | Per-Issue |

When in doubt: start with Per-Issue. Consolidating later is easy; splitting a
shared Issue after the fact is not.
