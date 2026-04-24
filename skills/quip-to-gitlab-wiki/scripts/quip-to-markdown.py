#!/usr/bin/env python3
"""
Convert a Quip document to Markdown with images/videos downloaded.

Usage:
    QUIP_TOKEN="xxx" python3 quip_to_markdown.py <quip_thread_id> <output_dir>

Token is read from QUIP_TOKEN environment variable (not command line args).
"""
import json, os, re, subprocess, sys

def get_token():
    """Read token from environment variable only."""
    token = os.environ.get("QUIP_TOKEN")
    if not token:
        print("ERROR: QUIP_TOKEN environment variable is not set.", file=sys.stderr)
        print("Export it: export QUIP_TOKEN='your_token_here'", file=sys.stderr)
        sys.exit(1)
    return token

def sanitize_path(base_dir, filename):
    """Prevent path traversal by ensuring output stays within base_dir."""
    abs_base = os.path.realpath(base_dir)
    abs_target = os.path.realpath(os.path.join(base_dir, filename))
    if not abs_target.startswith(abs_base + os.sep) and abs_target != abs_base:
        raise ValueError(f"Path traversal detected: {filename}")
    return abs_target

def fetch_thread(thread_id, token, base_url="https://platform.quip-amazon.com"):
    """Fetch Quip thread via API with SSL verification."""
    import urllib.request, ssl
    # Validate thread_id: alphanumeric only
    if not re.match(r'^[A-Za-z0-9]+$', thread_id):
        raise ValueError(f"Invalid thread ID: {thread_id}")
    url = f"{base_url}/1/threads/{thread_id}"
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        return json.loads(resp.read().decode())

def download_blob(blob_id, blob_name, token, output_path):
    """Download blob using curl with token via stdin to avoid ps leakage."""
    # Validate blob_id and blob_name
    if not re.match(r'^[A-Za-z0-9_-]+$', blob_id):
        return False
    clean_name = re.sub(r'[^A-Za-z0-9._-]', '', blob_name)
    url = f"https://quip-amazon.com/blob/{blob_id}/{clean_name}"
    # Use --config stdin to pass header, avoiding token in process list
    config = f'header = "Authorization: Bearer {token}"'
    proc = subprocess.run(
        ["curl", "-s", "-L", "--config", "-", url, "-o", output_path],
        input=config, capture_output=True, text=True, timeout=60
    )
    return os.path.exists(output_path) and os.path.getsize(output_path) > 100

def detect_file_type(path):
    return subprocess.run(["file", "-b", path], capture_output=True, text=True).stdout.strip()

def compress_video(input_path, output_path):
    r = subprocess.run(
        ["ffmpeg", "-i", input_path, "-vf", "scale=1280:720",
         "-c:v", "libx264", "-crf", "28", "-preset", "fast", "-an",
         output_path, "-y"],
        capture_output=True, timeout=300
    )
    return r.returncode == 0 and os.path.exists(output_path)

def html_to_markdown(html):
    import html2text
    html = re.sub(r'<control[^>]*>', '', html)
    html = re.sub(r'</control>', '', html)
    h = html2text.HTML2Text()
    h.body_width = 0; h.unicode_snob = True; h.protect_links = True
    md = h.handle(html)
    md = re.sub(r'\{#temp:C:[^}]+\}', '', md)
    md = re.sub(r'\n{4,}', '\n\n\n', md)
    return md

def convert(thread_id, token, output_dir):
    # Validate output_dir
    output_dir = os.path.realpath(output_dir)
    uploads_dir = os.path.join(output_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    data = fetch_thread(thread_id, token)
    title = data["thread"]["title"]; html = data["html"]
    print(f"Title: {title} ({len(html)} chars HTML)")

    blobs = re.findall(r'/blob/([^/\s"\'<>]+)/([^/\s"\'<>]+)', html)
    asset_map = {}
    for i, (blob_id, blob_name) in enumerate(blobs):
        clean_name = blob_name.rstrip("'\"")
        fname = f"img_{thread_id[:6]}_{i}.png"
        fpath = sanitize_path(uploads_dir, fname)
        if download_blob(blob_id, clean_name, token, fpath):
            ftype = detect_file_type(fpath)
            if "QuickTime" in ftype or "ISO Media" in ftype:
                mp4 = fname.replace(".png", ".mp4")
                mp4_path = sanitize_path(uploads_dir, mp4)
                if compress_video(fpath, mp4_path):
                    os.remove(fpath); fname = mp4
                asset_map[f"/blob/{blob_id}/{clean_name}"] = f"uploads/{fname}"
                fsize = os.path.getsize(os.path.join(uploads_dir, fname))
                print(f"  Video {i}: {fname} ({fsize//1024}KB)")
            else:
                asset_map[f"/blob/{blob_id}/{clean_name}"] = f"uploads/{fname}"
                print(f"  Image {i}: {fname} ({os.path.getsize(fpath)//1024}KB)")

    md = html_to_markdown(html)
    for old, new in asset_map.items(): md = md.replace(old, new)
    md_path = os.path.join(output_dir, "content.md")
    with open(md_path, "w") as f:
        f.write(md)
    print(f"Output: {md_path} ({len(md)} chars, {len(asset_map)} assets)")
    return {"title": title, "thread_id": thread_id, "md_path": md_path, "assets": list(asset_map.values())}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: QUIP_TOKEN=xxx {sys.argv[0]} <thread_id> <output_dir>")
        sys.exit(1)
    token = get_token()
    print(json.dumps(convert(sys.argv[1], token, sys.argv[2]), indent=2))
