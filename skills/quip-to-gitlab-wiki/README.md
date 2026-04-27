# Quip to GitLab Wiki Migration Skill

Effortlessly migrate Quip documents to GitLab Wiki while preserving all content, images, and videos.

## Installation

Copy this skill directory into your agent's skills folder (e.g., `~/.claude/skills/` for Claude Code):

```bash
cp -r skills/quip-to-gitlab-wiki ~/.claude/skills/
```

## Quick Start

### 1. Set Up Your API Token

```bash
export QUIP_TOKEN="your_quip_api_token_here"
```

### 2. Convert a Quip Document

```bash
python scripts/quip-to-markdown.py <quip_thread_id> ./output
```

**Example:**
```bash
python scripts/quip-to-markdown.py ABC123XYZ ./migration
```

The script outputs:
- `content.md` - Your Quip document as Markdown
- `uploads/` - Downloaded images and compressed videos
- JSON summary with conversion details

### 3. Push to GitLab Wiki

```bash
./scripts/push-to-wiki.sh <wiki_git_url> ./migration my-page "https://quip.com/threadid"
```

**Example:**
```bash
./scripts/push-to-wiki.sh https://gitlab.com/mygroup/myproject.wiki.git ./migration setup-guide "https://quip.com/ABC123XYZ"
```

## Prerequisites

- **Quip API Token** - Generate from [Quip Developer Settings](https://quip.com/dev/token)
- **GitLab Project** - Must have wiki feature enabled
- **Python 3.8+** - With `html2text` library
- **System Tools** - `ffmpeg` (for video compression), `curl`, `git`

### Install Dependencies

```bash
# Python packages
pip install html2text

# System packages (macOS)
brew install ffmpeg

# System packages (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

## File Structure

```
skills/quip-to-gitlab-wiki/
├── README.md                          # This file
├── SKILL.md                          # Skill metadata & reference
├── scripts/
│   ├── quip-to-markdown.py          # Main conversion script
│   └── push-to-wiki.sh              # GitLab wiki uploader
└── references/
    └── gitlab-mcp-config.md         # GitLab MCP integration guide
```

## What Gets Converted

| Quip Content | Conversion |
|-------------|-----------|
| Text & Formatting | Markdown syntax |
| Images | Downloaded to `uploads/` |
| Videos (MOV, MP4) | Compressed to 720p MP4 |
| Links | Preserved with relative paths |
| Tables | Markdown table format |
| Code Blocks | Markdown code fences |

## Output Example

After conversion, your wiki directory looks like:

```
migration/
├── content.md
└── uploads/
    ├── img_ABC123_0.png           # Images from Quip
    ├── img_ABC123_1.mp4           # Compressed videos
    └── img_ABC123_2.png
```

Images in your Markdown are automatically linked:
```markdown
![Document Image](uploads/img_ABC123_0.png)
```

## Advanced Usage

### Batch Migration

```bash
for thread_id in ABC123 XYZ789 DEF456; do
  python scripts/quip-to-markdown.py $thread_id ./batch/$thread_id
done
```

### Custom Wiki Structure

After converting, organize pages:

```bash
# Create structured wiki layout
mkdir -p wiki/Team-Docs/Onboarding
mv ./migration/content.md wiki/Team-Docs/Onboarding/Getting-Started.md
mv ./migration/uploads/* wiki/uploads/
```

### Relative Image Paths

The skill automatically handles relative paths:
- Root pages: `uploads/image.png`
- Section pages: `../uploads/image.png`
- Nested pages: `../../uploads/image.png`

## Troubleshooting

### QUIP_TOKEN not set
```
ERROR: QUIP_TOKEN environment variable is not set.
Export it: export QUIP_TOKEN='your_token_here'
```
Make sure the token is exported before running the script.

### Invalid thread ID
Thread IDs must be alphanumeric. Check your Quip URL: `https://quip.com/THREADID`

### Video compression fails
Ensure ffmpeg is installed and in your PATH:
```bash
ffmpeg -version
```

### GitLab wiki push issues
- Verify wiki is enabled in your GitLab project settings
- Check Git credentials: `git config credential.helper`
- Test access: `git clone <wiki_git_url>`

## Integration with Claude Code

Once pushed to GitLab, use the [GitLab MCP](./references/gitlab-mcp-config.md) to:
- Create and update wiki pages from Claude Code
- Link issues to wiki documentation
- Manage wiki structure programmatically

## License

MIT - See project LICENSE file

## References

- [Quip API Documentation](https://quip.com/api/documentation)
- [GitLab Wiki Documentation](https://docs.gitlab.com/ee/user/project/wiki/)
- [GitLab MCP Configuration](./references/gitlab-mcp-config.md)
