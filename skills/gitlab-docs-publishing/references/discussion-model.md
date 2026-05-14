# Discussion Model: Per-Issue vs. Shared Issue

Pick one model upfront before publishing the doc — mixing both on the same
doc confuses reviewers.

## Per-discussion Issue (recommended, default)

Each click on the 💬 bubble creates a **new GitLab Issue** with the section
reference in the title and an anchor link in the description.

- **Title:** `[<prefix>] §<heading-text> · "<selection quote>"`
- **Description:** anchor URL back to the section + selection quote + a
  hidden anchor JSON metadata block.
- **Searchable:** Issues are assignable, labelable, and closable per topic.
- **Downside:** an active review can produce dozens of Issues.

This is what `scripts/inject-comments.py` and `scripts/comment-widget.js`
ship with — `comments-issue.json`'s `issueLabels` field tags every Issue
(default: `doc-comments`) so they're easy to filter and triage.

## Shared Issue (simpler)

All clicks jump to one central Issue (e.g. `#1`). The widget would copy the
section reference to the clipboard; the reviewer pastes it as a new comment
on the shared Issue.

- **Pros:** one Issue to watch, fewer notifications.
- **Cons:** threading breaks when many parallel discussions run at once;
  you lose the ability to track/close topics individually. GitLab has no
  URL API to pre-fill a comment on an existing Issue, so the user must
  paste manually.

To switch to this mode, fork `scripts/comment-widget.js` and replace
`buildIssueUrl()` with a function that:

1. Sets `bubble.href = `${gitlabHost}/${projectPath}/-/issues/<shared-iid>#new_note`
2. On click, calls `navigator.clipboard.writeText(buildDescription(anchor))`
   so the reviewer can paste the anchor + quote into the comment box.

## Choosing

| Situation | Pick |
|-----------|------|
| Formal design review, several reviewers, each topic may stay open for days | Per-Issue |
| Informal walkthrough, one short review cycle, minimal bookkeeping desired | Shared Issue |
| Reviewers are external or junior and are likely to forget to file Issues | Shared Issue |
| Each discussion needs an assignee, label, or closes-via-MR tracking | Per-Issue |

When in doubt: start with Per-Issue. Consolidating later is easy; splitting
a shared Issue after the fact is not.
