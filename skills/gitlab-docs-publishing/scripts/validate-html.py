#!/usr/bin/env python3
"""
Validate an HTML doc for balanced tags and discussable-anchor coverage.

Checks:
  1. Every tag opens and closes cleanly (simple stack-based parser)
  2. Every discuss-button href anchor (#xxx) has a matching id in the DOM
  3. Count of buttons, anchors, mermaid figures, tables

Usage:
    python3 validate-html.py docs/v1.0.0/tech-design.html
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote


class TagBalance(HTMLParser):
    VOID = {"br", "hr", "meta", "link", "img", "input", "area", "base", "col", "embed", "source", "track", "wbr"}

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
            self.errors.append(f"expected </{self.stack[-1] if self.stack else '?'}> got </{tag}>")


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-html.py <file.html>", file=sys.stderr)
        sys.exit(1)

    html = Path(sys.argv[1]).read_text()

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

    # 2. Anchor coverage
    ids = set(re.findall(r' id="([^"]+)"', html))
    button_anchors = set()
    for m in re.finditer(r'href="[^"]*issue\[description\]=([^"&]+)', html):
        desc = unquote(m.group(1))
        for am in re.finditer(r"#([a-zA-Z0-9_-]+)", desc):
            button_anchors.add(am.group(1))
    missing = button_anchors - ids
    if missing:
        print(f"❌ Anchor coverage: {len(missing)} button anchors have no matching id")
        for a in sorted(missing)[:10]:
            print(f"   - #{a}")
    else:
        print(f"✅ Anchor coverage: all {len(button_anchors)} referenced anchors exist")

    # 3. Counts
    print()
    print(f"Sections (h2): {len(re.findall(r'<section class=.aws-sec.', html))}")
    print(f"Headings (h2/h3/h4): {sum(1 for _ in re.finditer(r'<h[234] class=.aws-', html))}")
    print(f"Mermaid figures: {html.count('<div class=\"diagram-frame\"')}")
    print(f"Tables: {html.count('<div class=\"aws-table-wrap\"')}")
    print(f"Discuss buttons: {html.count('class=\"discuss-btn\"') + html.count('class=\"discuss-inline\"')}")
    print(f"Prefilled issue URLs: {len(re.findall(r'issues/new\\?issue%5Btitle%5D=', html))}")

    if bal.errors or missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
