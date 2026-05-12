#!/usr/bin/env python3
"""
Inject 💬 discuss buttons into an HTML design document.

Every <h2>/<h3>/<h4>, every <div class="diagram-frame"> (mermaid figure),
and every <div class="aws-table-wrap"> (or configurable table-wrap class)
gets:
  1. An `id` attribute (if missing)
  2. A clickable 💬 button that opens GitLab's new-Issue page pre-filled
     with the section reference and anchor URL.

Usage:
    python3 inject-discuss-buttons.py \\
        --html docs/v1.0.0/tech-design.html \\
        --doc-url 'https://mygroup.gitlab.example.com/myproject/v1.0.0/' \\
        --issue-new-url 'https://gitlab.example.com/mygroup/myproject/-/issues/new' \\
        --title-prefix '[v1.0.0-tech-design]'

Assumptions about the HTML structure (based on common patterns generated
by Claude for AWS-docs-style outputs):
  - Sections use <section class="aws-sec" id="sec-N">
  - Headings use <h2 class="aws-sec-title">, <h3 class="aws-sub">,
    <h4 class="aws-subsub">
  - Mermaid figures wrapped in <div class="diagram-frame"> with a
    <span class="figure-num">Figure N-M</span> in the caption
  - Tables wrapped in <div class="aws-table-wrap">

If your document uses different class names, customize via the
--heading-classes and --table-wrap-class flags.
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote


def slugify(text: str, max_len: int = 30) -> str:
    s = re.sub(r"[^\w一-鿿-]+", "-", text)
    s = re.sub(r"-+", "-", s).strip("-").lower()
    return s[:max_len] or "sec"


def make_issue_url(base_url: str, title: str, desc: str) -> str:
    return (
        f"{base_url}"
        f"?issue[title]={quote(title, safe='')}"
        f"&issue[description]={quote(desc, safe='')}"
    )


def process(html: str, args) -> tuple[str, dict]:
    stats = {"headings": 0, "figures": 0, "tables": 0}

    # -------- Remove previously injected buttons (idempotent) --------
    html = re.sub(r"<a class=\"discuss-btn\"[^>]*>.*?</a>", "", html, flags=re.DOTALL)
    html = re.sub(r"<button class=\"discuss-btn\"[^>]*>.*?</button>", "", html, flags=re.DOTALL)
    html = re.sub(r"<a class=\"discuss-inline\"[^>]*>.*?</a>", "", html, flags=re.DOTALL)
    html = re.sub(r"\s*<div class=\"discuss-caption\">\s*</div>", "", html)

    # -------- Track top-level section positions --------
    section_pattern = re.compile(r'<section class="aws-sec" id="(sec-[^"]+)">')
    section_markers = [(m.start(), m.group(1)) for m in section_pattern.finditer(html)]

    def section_for(pos: int) -> str:
        current = section_markers[0][1] if section_markers else "sec-1"
        for start, sid in section_markers:
            if start <= pos:
                current = sid
            else:
                break
        return current

    # Map h2 index → number (skip the "相关文档"/"Related" appendix)
    h2_positions = [
        (m.start(), m.group(1))
        for m in re.finditer(r'<h2 class="aws-sec-title">([^<]+)</h2>', html)
    ]
    skip_h2_titles = set(args.skip_h2_titles or ["相关文档", "Related Documents"])
    h2_to_num = {}
    idx = 0
    for start, text in h2_positions:
        if text in skip_h2_titles:
            continue
        idx += 1
        h2_to_num[start] = idx

    def h2_num_for(pos: int) -> int | None:
        last = None
        for start, _ in h2_positions:
            if start < pos and start in h2_to_num:
                last = h2_to_num[start]
            elif start >= pos:
                break
        return last

    # -------- Pass 1: Add id to h3/h4 (if missing) --------
    used_ids = {sid for _, sid in section_markers}
    h34_pattern = re.compile(r'<(h[34]) class="aws-(sub|subsub)"(?: id="([^"]+)")?>([^<]+)</\1>')

    def replace_h34(m):
        tag = m.group(1)
        cls = m.group(2)
        existing_id = m.group(3)
        text = m.group(4)
        if existing_id:
            return m.group(0)
        # Prefer numeric prefix ("1.1", "3.1.2") for stable ids
        num_match = re.match(r"^(\d+(?:\.\d+)*)", text)
        if num_match:
            id_base = "sec-" + num_match.group(1).replace(".", "-")
        else:
            parent = h2_num_for(m.start()) or 0
            id_base = f"sec-{parent}-{slugify(text)}"
        final = id_base
        k = 2
        while final in used_ids:
            final = f"{id_base}-{k}"
            k += 1
        used_ids.add(final)
        return f'<{tag} class="aws-{cls}" id="{final}">{text}</{tag}>'

    html = h34_pattern.sub(replace_h34, html)

    # -------- Pass 2: Add id to figure frames --------
    fig_pattern = re.compile(
        r'(<div class="diagram-frame">)(.*?<span class="figure-num">)(Figure[^<]+)(</span>.*?</div>\s*</div>)',
        re.DOTALL,
    )

    def replace_fig(m):
        # Derive id from "Figure 4-2"
        nums = re.findall(r"\d+", m.group(3))
        fig_id = "figure-" + "-".join(nums)
        return f'<div class="diagram-frame" id="{fig_id}">{m.group(2)}{m.group(3)}{m.group(4)}'

    html = fig_pattern.sub(replace_fig, html)

    # -------- Pass 3: Add id to table wrappers --------
    sec_tbl_counter = {}
    table_open = re.compile(rf'<div class="{args.table_wrap_class}">')

    def replace_tbl(m):
        pos = m.start()
        sn = h2_num_for(pos) or 0
        sec_tbl_counter.setdefault(sn, 0)
        sec_tbl_counter[sn] += 1
        tbl_id = f"table-{sn}-{sec_tbl_counter[sn]}"
        return f'<div class="{args.table_wrap_class}" id="{tbl_id}">'

    html = table_open.sub(replace_tbl, html)

    # -------- Pass 4: Inject discuss buttons on all headings --------
    heading_pattern = re.compile(
        r'<(h[234]) class="aws-(sec-title|sub|subsub)"(?: id="([^"]+)")?>([^<]+)</\1>'
    )

    def make_heading_btn(ref, anchor):
        title = f"{args.title_prefix} {ref}".strip()
        desc = (
            f"## 讨论范围\n"
            f"**章节**：{ref}\n"
            f"**文档**：{args.doc_url}#{anchor}\n\n"
            f"---\n\n"
            f"<!-- 在此处写你的讨论内容 -->\n"
        )
        url = make_issue_url(args.issue_new_url, title, desc)
        return (
            f'<a class="discuss-btn" href="{url}" target="_blank" rel="noopener" '
            f'title="为本节创建讨论 Issue（自动带入章节与文档链接）">'
            f'<span class="icon">💬</span>讨论</a>'
        )

    new_parts = []
    last = 0
    h2_seen = 0
    in_appendix = False
    for m in heading_pattern.finditer(html):
        tag = m.group(1)
        cls = m.group(2)
        hid = m.group(3)
        text = m.group(4)
        new_parts.append(html[last : m.end()])
        if cls == "sec-title":
            h2_seen += 1
            if text in skip_h2_titles:
                in_appendix = True
            else:
                in_appendix = False
                ref = f"§{h2_seen} {text}"
                anchor = f"sec-{h2_seen}"
                new_parts.append(make_heading_btn(ref, anchor))
                stats["headings"] += 1
        else:
            if not in_appendix:
                if re.match(r"^\d", text):
                    ref = f"§{text}"
                else:
                    ref = f"§{h2_seen} · {text}"
                anchor = hid or f"sec-{h2_seen}"
                new_parts.append(make_heading_btn(ref, anchor))
                stats["headings"] += 1
        last = m.end()
    new_parts.append(html[last:])
    html = "".join(new_parts)

    # -------- Pass 5: Inject discuss buttons on figures --------
    def make_inline_btn(ref, anchor, kind):
        title = f"{args.title_prefix} {ref}".strip()
        desc = (
            f"## 讨论范围\n"
            f"**{kind}**：{ref}\n"
            f"**文档**：{args.doc_url}#{anchor}\n\n"
            f"---\n\n"
            f"<!-- 在此处写你的讨论内容 -->\n"
        )
        url = make_issue_url(args.issue_new_url, title, desc)
        return (
            f'<a class="discuss-inline" href="{url}" target="_blank" rel="noopener" '
            f'title="针对此{kind}创建讨论 Issue"><span class="icon">💬</span>讨论</a>'
        )

    cap_pattern = re.compile(
        r'<div class="diagram-caption">\s*<span class="figure-num">([^<]+)</span>([^<]+)</div>'
    )

    def replace_caption(m):
        fig_num = m.group(1).strip()
        title_text = m.group(2).strip()
        ref = f"{fig_num} {title_text}"
        nums = re.findall(r"\d+", fig_num)
        anchor = "figure-" + "-".join(nums)
        btn = make_inline_btn(ref, anchor, "图")
        stats["figures"] += 1
        return f'<div class="diagram-caption"><span class="figure-num">{fig_num}</span>{title_text} {btn}</div>'

    html = cap_pattern.sub(replace_caption, html)

    # -------- Pass 6: Inject discuss buttons on tables --------
    tbl_pattern = re.compile(
        rf'(<div class="{args.table_wrap_class}" id="(table-[\d-]+)">\s*<table[^>]*>.*?</table>\s*</div>)',
        re.DOTALL,
    )

    tbl_context_cache = []

    def make_tbl_btn(m):
        whole = m.group(1)
        tbl_id = m.group(2)
        # Derive ref from nearby preceding heading
        pos = m.start()
        head_text = None
        head_has_num = False
        for hm in re.finditer(
            r'<h([234]) class="aws-(sec-title|sub|subsub)"(?: id="[^"]+")?>([^<]+)</h\1>',
            html[:pos],
        ):
            head_text = hm.group(3)
            head_has_num = bool(re.match(r"^\d", head_text))
        # Derive section number
        sn = 0
        for start, num in h2_to_num.items():
            if start < pos:
                sn = num
        # Table index from id
        tbl_idx = tbl_id.rsplit("-", 1)[-1]
        if head_text and head_has_num:
            ref = f"§{head_text} · 表 {tbl_idx}"
        elif head_text:
            ref = f"§{sn} · {head_text} · 表 {tbl_idx}"
        else:
            ref = f"§{sn} · 表 {tbl_idx}"
        btn = make_inline_btn(ref, tbl_id, "表")
        stats["tables"] += 1
        return f'{whole}\n<div class="discuss-caption">{btn}</div>'

    html = tbl_pattern.sub(make_tbl_btn, html)

    # -------- Inject CSS if missing --------
    if ".discuss-btn {" not in html:
        css = """
/* discuss buttons */
.discuss-btn, .discuss-inline {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 12px;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  background: #ff9900;
  border: 1px solid #ec7211;
  border-radius: 10px;
  text-decoration: none;
  vertical-align: middle;
  transition: all 120ms;
  cursor: pointer;
  line-height: 1;
  box-shadow: 0 1px 2px rgba(236,114,17,0.25);
}
.discuss-btn:hover, .discuss-inline:hover {
  background: #ec7211;
  box-shadow: 0 2px 6px rgba(236,114,17,0.4);
  transform: translateY(-1px);
}
.discuss-caption {
  text-align: right;
  margin: -10px 0 18px;
  padding-right: 4px;
}
.discuss-caption .discuss-inline { margin-left: 0; }
"""
        html = html.replace("</style>", css + "\n</style>", 1)

    return html, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--html", required=True, help="Path to the HTML file to modify in-place")
    parser.add_argument("--doc-url", required=True, help="Public Pages URL of the doc (no trailing hash)")
    parser.add_argument("--issue-new-url", required=True, help="GitLab new-issue URL for this project")
    parser.add_argument("--title-prefix", default="", help="Prefix for Issue titles, e.g. '[v1.0.0-tech-design]'")
    parser.add_argument("--table-wrap-class", default="aws-table-wrap", help="CSS class of the table wrapper div")
    parser.add_argument("--skip-h2-titles", nargs="*", help="H2 titles to skip injecting on (e.g. appendices)")
    parser.add_argument("--dry-run", action="store_true", help="Print stats but don't write the file")
    args = parser.parse_args()

    path = Path(args.html)
    original = path.read_text()
    new_html, stats = process(original, args)

    if args.dry_run:
        print(f"[dry-run] Would inject: {stats}")
        return

    path.write_text(new_html)
    print(
        f"Done. Injected {stats['headings']} heading buttons, "
        f"{stats['figures']} figure buttons, {stats['tables']} table buttons. "
        f"Total: {sum(stats.values())}."
    )


if __name__ == "__main__":
    main()
