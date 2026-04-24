# CLAUDE.md

Instructions for Claude Code when working with this repository.

## Project Overview

This is a sample skills repository demonstrating the Agent Skills format for the skills.sh ecosystem. Use this as a reference when helping users create new skills.

## Key Commands

```bash
# Validate skill frontmatter
grep -A5 '^---' skills/*/SKILL.md

# List all skills
ls -la skills/

# Check skill structure
find skills -type f -name "*.md"
```

## Creating Skills

When asked to create a new skill:

1. Create directory: `skills/{skill-name}/`
2. Create `SKILL.md` with frontmatter (name and description required)
3. Add `references/` directory if detailed documentation needed
4. Add `scripts/` directory if automation needed

## SKILL.md Template

```markdown
---
name: {skill-name}
description: {Trigger phrase description}
---

# {Title}

## When to Apply
{Bullet list of conditions}

## How It Works
{Numbered steps}

## Usage
{Code examples}
```

## Conventions

- Skill names: `kebab-case`
- Directory names match skill names
- SKILL.md is always uppercase
- Frontmatter is YAML between `---` markers
- Description should include trigger phrases for discovery

## Testing

After creating a skill, verify:
- [ ] Frontmatter parses as valid YAML
- [ ] `name` field matches directory name
- [ ] `description` is a clear, single sentence
- [ ] All file references resolve correctly
