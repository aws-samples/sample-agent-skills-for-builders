/* Game AI QA — In-page Doc Comments (selection → new GitLab Issue)
 *
 * Reviewer selects any text or block element. A floating "💬 添加评论" bubble
 * appears above the selection. Clicking opens a new tab on GitLab's Issue
 * creation page with title + description prefilled — reviewer's Midway/SSO
 * session authenticates them automatically. No CORS/OAuth/PAT involved.
 *
 * Why this shape: AEA + GitLab CORS make any in-browser API call impossible
 * from the Pages origin. Plain navigation works because the browser handles
 * the auth handshake itself.
 *
 * Config injected as window.__DOC_COMMENTS_CONFIG__ before this script.
 */
(function () {
  'use strict';

  // ─── Config ──────────────────────────────────────────────────────────────
  var cfg = window.__DOC_COMMENTS_CONFIG__ || {};
  var required = ['gitlabHost', 'projectPath', 'pageKey', 'pageUrl'];
  var missing = required.filter(function (k) { return !cfg[k]; });
  if (missing.length) {
    showSetupBanner('Doc comments not yet enabled — missing config: ' + missing.join(', '));
    return;
  }
  // Reject anything that isn't an http(s) URL — keeps a `javascript:` host
  // from turning the bubble into an XSS sink if the config is ever tampered
  // with (e.g. via a <script>-context injection in inject-comments.py).
  try {
    var hostUrl = new URL(cfg.gitlabHost);
    if (hostUrl.protocol !== 'https:' && hostUrl.protocol !== 'http:') {
      throw new Error('unsupported scheme: ' + hostUrl.protocol);
    }
  } catch (e) {
    showSetupBanner('Doc comments disabled — invalid gitlabHost: ' + cfg.gitlabHost);
    return;
  }
  var TITLE_PREFIX = cfg.titlePrefix || '[doc-comment]';
  var ISSUE_LABELS = cfg.issueLabels || 'doc-comments';

  // ─── Anchor model ────────────────────────────────────────────────────────
  // Same shape as before so the JSON in the issue body is forward-compatible
  // if we ever add an in-page reader that fetches & re-locates anchors.
  function anchorFromRange(range) {
    if (range.collapsed) return null;
    var exact = range.toString().slice(0, 280);
    if (!exact.trim()) return null;
    var prefix = textBefore(range, 32);
    var suffix = textAfter(range, 32);
    var startEl = range.startContainer.nodeType === 1
      ? range.startContainer
      : range.startContainer.parentElement;
    var heading = findOwningHeading(startEl);
    return {
      type: 'text',
      id: heading && heading.id ? heading.id : null,
      sectionTitle: heading ? cleanHeadingText(heading) : null,
      exact: exact,
      prefix: prefix,
      suffix: suffix,
    };
  }
  // Walk back through previous siblings + their descendants, then up the tree,
  // collecting the deepest (highest-level h-tag number) heading seen so far.
  // Stops as soon as we find a heading that owns the current node.
  function findOwningHeading(el) {
    var node = el;
    while (node && node !== document.body) {
      // 1. Check this node itself if it's a heading
      if (/^H[1-6]$/.test(node.tagName)) return node;
      // 2. Walk back through preceding siblings looking for a heading
      var sib = node.previousElementSibling;
      while (sib) {
        var h = lastHeadingIn(sib);
        if (h) return h;
        sib = sib.previousElementSibling;
      }
      node = node.parentElement;
    }
    return null;
  }
  // Return the LAST heading inside `el` (so a section's last subsection wins
  // over its parent title when selecting text under that subsection).
  function lastHeadingIn(el) {
    if (!el || el.nodeType !== 1) return null;
    if (/^H[1-6]$/.test(el.tagName)) return el;
    var hs = el.querySelectorAll && el.querySelectorAll('h1, h2, h3, h4, h5, h6');
    if (hs && hs.length) return hs[hs.length - 1];
    return null;
  }
  function cleanHeadingText(h) {
    return (h.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80);
  }
  function textBefore(range, n) {
    var s = range.startContainer.textContent || '';
    return s.slice(Math.max(0, range.startOffset - n), range.startOffset);
  }
  function textAfter(range, n) {
    var s = range.endContainer.textContent || '';
    return s.slice(range.endOffset, range.endOffset + n);
  }

  // ─── Title + description for the GitLab Issue ───────────────────────────
  // Format: "[doc-comment] §<section-title> · <selection-quote>"
  // Section title comes from the heading the selection sits under (when available).
  // Falls back to the anchor id, then to the page key. Selection quote is short
  // (first ~30 chars, ellipsised) so the title stays scannable.
  function buildTitle(anchor) {
    var section = anchor.sectionTitle || anchor.id || cfg.pageKey;
    var quote = (anchor.exact || '').replace(/\s+/g, ' ').trim();
    if (quote.length > 30) quote = quote.slice(0, 30) + '…';
    var parts = [TITLE_PREFIX, '§' + section];
    if (quote) parts.push('· "' + quote + '"');
    return parts.join(' ').slice(0, 240);
  }

  function buildDescription(anchor) {
    var anchorUrl = cfg.pageUrl + (anchor.id ? '#' + anchor.id : '');
    var anchorLabel = anchor.sectionTitle || anchor.id || cfg.pageKey;
    var lines = [];
    lines.push('**Anchor**: [§' + anchorLabel + '](' + anchorUrl + ')');
    lines.push('');
    lines.push('**Selection**:');
    lines.push('> ' + (anchor.exact || '').replace(/\n/g, '\n> '));
    lines.push('');
    lines.push('---');
    lines.push('');
    lines.push('<!-- doc-comment-anchor-v1');
    lines.push(JSON.stringify({ anchor: anchor, page: cfg.pageKey }));
    lines.push('-->');
    lines.push('');
    lines.push('Your comment:');
    lines.push('');
    return lines.join('\n');
  }

  function buildIssueUrl(anchor) {
    var base = cfg.gitlabHost + '/' + cfg.projectPath + '/-/issues/new';
    var p = new URLSearchParams();
    p.set('issue[title]', buildTitle(anchor));
    p.set('issue[description]', buildDescription(anchor));
    if (ISSUE_LABELS) p.set('issue[label_names][]', ISSUE_LABELS);
    return base + '?' + p.toString();
  }

  // ─── Bubble UI ───────────────────────────────────────────────────────────
  var bubble;
  function build() {
    bubble = document.createElement('a');
    bubble.id = 'dc-bubble';
    bubble.target = '_blank';
    bubble.rel = 'noopener noreferrer';
    bubble.hidden = true;
    bubble.textContent = '💬 添加评论';
    document.body.appendChild(bubble);

    // Keep selection while clicking the bubble.
    bubble.addEventListener('mousedown', function (e) { e.preventDefault(); });

    document.addEventListener('mouseup', maybeShowBubble);
    document.addEventListener('selectionchange', maybeShowBubble);
    document.addEventListener('scroll', repositionBubble, { passive: true });
    window.addEventListener('resize', repositionBubble);
  }

  var lastRect = null;
  function maybeShowBubble() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || sel.rangeCount === 0) {
      bubble.hidden = true;
      lastRect = null;
      return;
    }
    var range = sel.getRangeAt(0);
    var text = range.toString();
    if (!text || !text.trim()) {
      bubble.hidden = true;
      lastRect = null;
      return;
    }
    if (bubble.contains(range.startContainer)) return;
    var anchor = anchorFromRange(range);
    if (!anchor) {
      bubble.hidden = true;
      return;
    }
    bubble.href = buildIssueUrl(anchor);
    lastRect = range.getBoundingClientRect();
    repositionBubble();
    bubble.hidden = false;
  }

  function repositionBubble() {
    if (!lastRect || bubble.hidden) return;
    var r = lastRect;
    bubble.style.top = (window.scrollY + r.top - 40) + 'px';
    bubble.style.left = (window.scrollX + r.left + r.width / 2 - 64) + 'px';
  }

  // ─── Setup-banner (only when config missing) ────────────────────────────
  function showSetupBanner(msg) {
    var b = document.createElement('div');
    b.id = 'dc-setup-banner';
    b.textContent = msg;
    b.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#ffe9b2;' +
                      'color:#7a4a00;padding:10px 16px;font:13px system-ui;' +
                      'z-index:99999;border-bottom:1px solid #d8a520;';
    if (document.body) document.body.appendChild(b);
    else document.addEventListener('DOMContentLoaded', function () { document.body.appendChild(b); });
  }

  // ─── Public API for testing ─────────────────────────────────────────────
  window.docComments = {
    buildIssueUrl: buildIssueUrl,
    anchorFromRange: anchorFromRange,
  };

  // ─── Boot ───────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
