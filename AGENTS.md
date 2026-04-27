# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Cursor, Copilot, etc.) when working with code in this repository.

## Repository Overview

A collection of sample skills for AI coding agents. Skills are packaged instructions and scripts that extend agent capabilities. This repository follows the Agent Skills format (a `SKILL.md` file with YAML frontmatter, optionally accompanied by `references/` and `scripts/`).

## Creating a New Skill

### Directory Structure

```
skills/
  {skill-name}/           # kebab-case directory name
    SKILL.md              # Required: skill definition with frontmatter
    metadata.json         # Optional: extended metadata
    references/           # Optional: supporting documentation
    scripts/              # Optional: executable scripts
```

### Naming Conventions

- **Skill directory**: `kebab-case` (e.g., `my-awesome-skill`, `code-reviewer`)
- **SKILL.md**: Always uppercase, always this exact filename
- **Scripts**: `kebab-case.sh` (e.g., `deploy.sh`, `validate.sh`)

### SKILL.md Format

Every skill MUST have a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: {skill-name}
description: {One sentence describing when to use this skill. Include trigger phrases like "Deploy my app", "Review this code", etc.}
license: MIT
metadata:
  author: {author-name}
  version: "1.0.0"
---

# {Skill Title}

{Brief description of what the skill does.}

## When to Apply

Reference this skill when:
- {Condition 1}
- {Condition 2}
- {Condition 3}

## How It Works

1. {Step 1}
2. {Step 2}
3. {Step 3}

## Usage

{Show examples with code blocks}

## References

- {Link to documentation}
- {Link to related resources}
```

### Required Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier in kebab-case |
| `description` | Yes | One sentence with trigger phrases for discovery |
| `license` | No | Defaults to repository license (MIT) |
| `metadata` | No | Extended metadata object |

### Best Practices for Context Efficiency

Skills are loaded on-demand. Only the skill name and description are loaded at startup. The full SKILL.md loads into context only when the agent decides the skill is relevant.

To minimize context usage:

- **Keep SKILL.md under 500 lines** - put detailed reference material in separate files
- **Write specific descriptions** - helps the agent know exactly when to activate
- **Use progressive disclosure** - reference supporting files that get read only when needed
- **Prefer scripts over inline code** - script execution doesn't consume context

### Adding References

For skills that need detailed documentation:

1. Create a `references/` directory in your skill folder
2. Add markdown files with detailed documentation
3. Reference them from SKILL.md:

```markdown
## References

See [detailed-guide.md](./references/detailed-guide.md) for comprehensive examples.
```

### Adding Scripts

For skills that automate tasks:

1. Create a `scripts/` directory in your skill folder
2. Add bash scripts with proper shebang and error handling:

```bash
#!/bin/bash
set -e

# Your script logic here
echo "Status message" >&2
echo '{"result": "success"}'
```

### metadata.json Format

Optional extended metadata:

```json
{
  "version": "1.0.0",
  "author": "Your Name",
  "organization": "Your Org",
  "date": "April 2026",
  "abstract": "Detailed description for search indexing",
  "references": [
    "https://example.com/docs"
  ],
  "tags": ["category1", "category2"]
}
```

## Validating Skills

Before committing, verify your skill:

1. **Frontmatter is valid YAML**
2. **Name matches directory name**
3. **Description is a single, clear sentence**
4. **All referenced files exist**

## Testing Skills

To test a skill locally:

1. Copy the skill to your agent's skills directory
2. Start a new agent session
3. Trigger the skill with phrases from the description
4. Verify the skill activates and provides correct guidance
