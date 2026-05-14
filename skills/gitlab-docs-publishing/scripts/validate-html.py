#!/usr/bin/env python3
"""Validate an HTML doc before publishing.

Checks:
  1. Every tag opens and closes cleanly (simple stack-based parser).
  2. Headings have id attributes (so widget-generated anchor URLs scroll
     to the right place after submission).
  3. Counts: sections, headings, mermaid figures, tables.

Run on the source HTML before the inject step:

    python3 validate-html.py docs/v1.0.0/tech-design.html

Or on the published HTML to confirm the inject step ran:

    python3 validate-html.py public/v1.0.0/index.html
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class TagBalance(HTMLParser):
    VOID = {
        "br", "hr", "meta", "link", "img", "input", "area",
        "base", "col", "embed", "source", "track", "wbr",
    }

    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(
                f"expected </{self.stack[-1] if self.stack else '?'}> got </{tag}>"
            )


HEADING_RE = re.compile(r'<(h[1-6])([^>]*)>', re.IGNORECASE)
ID_ATTR_RE = re.compile(r'\bid\s*=\s*"([^"]+)"', re.IGNORECASE)


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-html.py <file.html>", file=sys.stderr)
        sys.exit(1)

    html = Path(sys.argv[1]).read_text(encoding="utf-8")
    print(f"=== {sys.argv[1]} — {len(html):,} bytes ===\n")

    # 1. Tag balance
    bal = TagBalance()
    bal.feed(html)
    if bal.errors:
        print(f"❌ Tag balance: {len(bal.errors)} errors")
        for e in bal.errors[:5]:
            print(f"   - {e}")
    else:
        print("✅ Tag balance: OK")
    if bal.stack:
        print(f"   Unclosed tags at EOF: {bal.stack[-5:]}")

    # 2. Heading id coverage
    headings = HEADING_RE.findall(html)
    headings_without_id = [
        tag for tag, attrs in headings if not ID_ATTR_RE.search(attrs)
    ]
    if headings_without_id:
        print(
            f"⚠ Heading ids: {len(headings_without_id)} of {len(headings)} "
            f"h1..h6 have no id (run inject-comments.py to add them)"
        )
    else:
        print(f"✅ Heading ids: all {len(headings)} h1..h6 have id attributes")

    # 3. Counts
    print()
    print(f"Headings (h1..h6):   {len(headings)}")
    print(f"Mermaid figures:     {html.count('<div class=\"diagram-frame\"')}")
    print(f"Tables (aws-table):  {html.count('<div class=\"aws-table-wrap\"')}")
    print(
        "Widget injected:     "
        + ("yes" if 'doc-comments-injected' in html else "no")
    )

    if bal.errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
