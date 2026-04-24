---
name: hello-world
description: A template skill demonstrating the correct Agent Skills format. Use when learning to create skills, starting from a template, or understanding the SKILL.md structure.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# Hello World Skill

This is a template skill demonstrating the standard Agent Skills format. Use this as a starting point for creating your own skills.

## When to Apply

Reference this skill when:
- Learning how to create agent skills
- Starting a new skill from a template
- Understanding the SKILL.md format and frontmatter
- Demonstrating skill structure to others

## Skill Format Overview

Every skill requires:

1. **YAML Frontmatter** - Metadata between `---` markers at the top
2. **name** - Unique identifier in kebab-case
3. **description** - One sentence with trigger phrases for discovery

Optional frontmatter fields:
- `license` - Defaults to repository license
- `metadata` - Object with author, version, tags

## Directory Structure

```
skills/
  hello-world/
    SKILL.md              # This file (required)
    references/           # Supporting documentation (optional)
      examples.md
    scripts/              # Automation scripts (optional)
    metadata.json         # Extended metadata (optional)
```

## Best Practices

### Write Effective Descriptions

The `description` field determines when agents activate this skill. Include:
- What the skill does
- Trigger phrases users might say
- Keywords for search discovery

**Good:** "Deploy applications to Vercel. Use when user says 'deploy my app', 'push to production', or 'create preview'."

**Bad:** "Deployment skill."

### Keep SKILL.md Focused

- Under 500 lines for the main file
- Put detailed documentation in `references/`
- Use progressive disclosure - link to details, don't inline everything

### Use Code Examples

Show, don't just tell:

```bash
# Example command
npx skills add owner/repo@skill-name
```

## References

See [examples.md](./references/examples.md) for additional skill examples and patterns.
