# Skill Examples

This document provides additional examples of skill patterns and structures.

## Minimal Skill

The simplest valid skill has only the required frontmatter:

```markdown
---
name: minimal-skill
description: Does one specific thing when triggered.
---

# Minimal Skill

Instructions for the agent.
```

## Skill with References

For skills that need detailed documentation:

```markdown
---
name: documented-skill
description: Complex skill with extensive documentation.
---

# Documented Skill

Brief overview here.

## Quick Reference

Key points inline.

## Detailed Guide

See [full-guide.md](./references/full-guide.md) for comprehensive documentation.
```

## Skill with Scripts

For skills that automate tasks:

```markdown
---
name: automation-skill
description: Automates deployment tasks.
---

# Automation Skill

## Usage

Run the deployment script:

\`\`\`bash
bash /path/to/skill/scripts/deploy.sh [args]
\`\`\`
```

With `scripts/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "Starting deployment..." >&2
# Deployment logic here
echo '{"status": "success", "url": "https://example.com"}'
```

## Skill with Metadata

Extended metadata for search and versioning:

```json
{
  "version": "2.1.0",
  "author": "Your Name",
  "organization": "Your Org",
  "date": "April 2026",
  "abstract": "Detailed description for search engines and skill discovery.",
  "tags": ["deployment", "automation", "devops"],
  "references": [
    "https://docs.example.com"
  ]
}
```
