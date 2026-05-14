#!/usr/bin/env python3
"""Inject the doc-comments widget into a published HTML file.

Idempotent: running twice does not duplicate <link>/<script> tags.
Zero deps (stdlib only).

Usage (typical CI):
  python3 scripts/inject-comments.py \
      --html docs/v1.0.0/tech-design.html \
      --out  public/v1.0.0/index.html \
      --assets-dir public/v1.0.0/_assets \
      --assets-url _assets \
      --config-json docs/v1.0.0/comments-issue.json \
      --page-key v1.0.0/tech-design.html
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

INJECTED_META = '<meta name="doc-comments-injected" content="v1">'
SCRIPT_NAME = 'comment-widget.js'
STYLE_NAME = 'comment-widget.css'

# ─── Heading id slugger ────────────────────────────────────────────────────

_slug_strip = re.compile(r'[^\w一-鿿\- ]+', re.UNICODE)
_ws = re.compile(r'\s+')


def slugify(text: str) -> str:
    text = (text or '').strip().lower()
    text = _slug_strip.sub('', text)
    text = _ws.sub('-', text).strip('-')
    return text or 'sec'


# ─── Heading id ensure ─────────────────────────────────────────────────────

HEADING_RE = re.compile(r'<(h[1-6])(\s[^>]*)?>(.*?)</\1>', re.DOTALL | re.IGNORECASE)
ID_ATTR_RE = re.compile(r'\bid\s*=\s*"([^"]*)"', re.IGNORECASE)
TAG_TEXT_RE = re.compile(r'<[^>]+>')


def ensure_heading_ids(html: str) -> str:
    seen: set[str] = set()

    # First pass: collect existing ids so we don't collide.
    for m in re.finditer(r'\bid\s*=\s*"([^"]*)"', html, re.IGNORECASE):
        seen.add(m.group(1))

    def repl(m: re.Match) -> str:
        tag = m.group(1)
        attrs = m.group(2) or ''
        inner = m.group(3)
        if ID_ATTR_RE.search(attrs):
            return m.group(0)
        text = TAG_TEXT_RE.sub('', inner).strip()
        slug = slugify(text)
        cand = slug
        i = 2
        while cand in seen:
            cand = f'{slug}-{i}'
            i += 1
        seen.add(cand)
        new_attrs = (attrs or '') + f' id="{cand}"'
        return f'<{tag}{new_attrs}>{inner}</{tag}>'

    return HEADING_RE.sub(repl, html)


# ─── Figure / table id helpers (best effort, mirrors existing skill style) ─

DIAGRAM_FRAME_RE = re.compile(
    r'<div([^>]*\bclass="[^"]*diagram-frame[^"]*"[^>]*)>',
    re.IGNORECASE,
)
TABLE_WRAP_RE = re.compile(
    r'<div([^>]*\bclass="[^"]*aws-table-wrap[^"]*"[^>]*)>',
    re.IGNORECASE,
)


# ─── Strip stale `<a class="discuss-btn">` markup if present ────────────
# Source HTML produced by older versions of this skill (≤ v1.x) carried
# per-heading 💬 buttons. The v2 selection bubble covers that use case,
# so we strip those legacy anchors from the published artifact (the
# source HTML is left untouched). If your source HTML doesn't have them,
# this is a no-op and safe to keep.

LEGACY_BTN_RE = re.compile(
    r'<a\s+class="discuss-btn"[^>]*>.*?</a>',
    re.DOTALL | re.IGNORECASE,
)
LEGACY_CSS_RULE_RE = re.compile(
    r'\.discuss-btn[^{}]*\{[^{}]*\}',
    re.IGNORECASE,
)


def strip_legacy_discuss_buttons(html: str) -> tuple[str, int]:
    new_html, btn_count = LEGACY_BTN_RE.subn('', html)
    new_html = LEGACY_CSS_RULE_RE.sub('', new_html)
    return new_html, btn_count


def add_sequential_ids(html: str, regex: re.Pattern, prefix: str) -> str:
    counter = {'n': 0}

    def repl(m: re.Match) -> str:
        attrs = m.group(1)
        if ID_ATTR_RE.search(attrs):
            return m.group(0)
        counter['n'] += 1
        return f'<div{attrs} id="{prefix}-{counter["n"]}">'

    return regex.sub(repl, html)


# ─── Injection ─────────────────────────────────────────────────────────────

def already_injected(html: str) -> bool:
    return 'name="doc-comments-injected"' in html


def build_config_snippet(
    *, gitlab_host: str, project_path: str,
    page_key: str, page_url: str,
    title_prefix: str, issue_labels: str,
) -> str:
    payload = {
        'gitlabHost': gitlab_host,
        'projectPath': project_path,
        'pageKey': page_key,
        'pageUrl': page_url,
        'titlePrefix': title_prefix,
        'issueLabels': issue_labels,
    }
    js = json.dumps(payload, ensure_ascii=False)
    return f'<script>window.__DOC_COMMENTS_CONFIG__ = {js};</script>'


def inject_assets(html: str, assets_rel: str, config_snippet: str) -> str:
    if already_injected(html):
        return html

    head_inject = (
        f'  {INJECTED_META}\n'
        f'  <link rel="stylesheet" href="{assets_rel}/{STYLE_NAME}">\n'
    )
    body_inject = (
        f'  {config_snippet}\n'
        f'  <script src="{assets_rel}/{SCRIPT_NAME}" defer></script>\n'
    )

    if '</head>' in html:
        html = html.replace('</head>', head_inject + '</head>', 1)
    else:
        html = head_inject + html  # no <head>; degrade

    if '</body>' in html:
        html = html.replace('</body>', body_inject + '</body>', 1)
    else:
        html = html + body_inject

    return html


# ─── Driver ────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--html', required=True, help='Input HTML file')
    p.add_argument('--out', required=True, help='Output HTML file (e.g. public/v1.0.0/index.html)')
    p.add_argument('--assets-dir', required=True, help='Where comment-widget.{js,css} get copied')
    p.add_argument('--assets-url', default='_assets',
                   help='URL path (relative to the HTML) where the browser fetches assets')
    p.add_argument('--config-json', required=True,
                   help='Path to comments-issue.json (gitlabHost + projectPath + pageUrl)')
    p.add_argument('--page-key', required=True, help='Logical key stored with each comment')
    args = p.parse_args()

    src_path = Path(args.html)
    out_path = Path(args.out)
    assets_dir = Path(args.assets_dir)
    cfg_path = Path(args.config_json)

    if not src_path.is_file():
        print(f'ERROR: html not found: {src_path}', file=sys.stderr)
        return 2
    if not cfg_path.is_file():
        print(f'ERROR: config json not found: {cfg_path}', file=sys.stderr)
        return 2

    cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
    project_path = cfg.get('projectPath')
    page_url = cfg.get('pageUrl')
    if not project_path or not page_url:
        print('ERROR: comments-issue.json missing projectPath or pageUrl', file=sys.stderr)
        return 3

    # 1. Read source
    html = src_path.read_text(encoding='utf-8')

    # 2. Strip stale `<a class="discuss-btn">` markup from earlier tooling.
    html, stripped = strip_legacy_discuss_buttons(html)
    if stripped:
        print(f'OK: stripped {stripped} stale discuss-btn link(s) from source')

    # 3. Augment with ids (so anchors like #sec-4-3 resolve to the right place)
    html = ensure_heading_ids(html)
    html = add_sequential_ids(html, DIAGRAM_FRAME_RE, 'figure')
    html = add_sequential_ids(html, TABLE_WRAP_RE, 'table')

    # 4. Inject (idempotent)
    snippet = build_config_snippet(
        gitlab_host=cfg.get('gitlabHost', 'https://gitlab.aws.dev'),
        project_path=project_path,
        page_key=args.page_key,
        page_url=page_url,
        title_prefix=cfg.get('titlePrefix', '[doc-comment]'),
        issue_labels=cfg.get('issueLabels', 'doc-comments'),
    )
    html = inject_assets(html, args.assets_url, snippet)

    # 5. Write output + copy widget assets
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding='utf-8')

    assets_dir.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).parent
    for name in (SCRIPT_NAME, STYLE_NAME):
        shutil.copy2(here / name, assets_dir / name)

    print(f'OK: wrote {out_path} ({out_path.stat().st_size} bytes)')
    print(f'OK: copied assets to {assets_dir}/')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
