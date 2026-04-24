---
name: quip-to-gitlab-wiki
description: Migrate Quip documents to GitLab Wiki with full content preservation. Use when converting Quip docs to wiki, migrating documentation, or setting up GitLab wiki from Quip sources.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# Quip to GitLab Wiki Migration

Migrate Quip documents to GitLab Wiki with full content and media preservation.

## When to Apply

Reference this skill when:
- Migrating Quip documents to GitLab
- Converting documentation to wiki format
- Preserving embedded images and videos
- Setting up GitLab wiki structure

## Workflow

1. **Gather Sources** - Collect Quip URLs and tokens
2. **Convert** - Transform Quip HTML to Markdown
3. **Push** - Upload to GitLab Wiki
4. **Configure** - Set up GitLab MCP for future edits
5. **Structure** - Organize wiki navigation

## Prerequisites

- Quip API token
- GitLab project with wiki enabled
- Python 3.8+ with html2text
- ffmpeg (for video compression)

## Usage

```bash
# Convert Quip document (token from environment)
export QUIP_TOKEN="your_token_here"
python scripts/quip-to-markdown.py <thread_id> <output_dir>

# Push to GitLab wiki
./scripts/push-to-wiki.sh <wiki_git_url> <content_dir> <page_path> <quip_url>
```

## Conversion Features

- HTML to Markdown via html2text
- Embedded image download
- Video compression (MOV→MP4 at 720p)
- Asset organization in `uploads/`

## Wiki Structure

```
wiki/
├── Home.md
├── Section-Name/
│   ├── _index.md
│   └── Page-Name.md
└── uploads/
    ├── image1.png
    └── video1.mp4
```

## Image Path Rules

| Page Location | Image Path |
|--------------|------------|
| Root pages | `uploads/image.png` |
| Section pages | `../uploads/image.png` |
| Nested pages | `../../uploads/image.png` |

## References

- [GitLab MCP Configuration](./references/gitlab-mcp-config.md)
