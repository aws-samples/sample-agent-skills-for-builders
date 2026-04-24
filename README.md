# Sample Skills for Builders

A collection of sample skills demonstrating how to build and publish agent skills for the [skills.sh](https://skills.sh/) ecosystem.

Skills are modular packages that extend AI coding agent capabilities with specialized knowledge, workflows, and tools.

## Installation

Install all skills from this repository:

```bash
npx skills add <your-gitlab-username>/sample-skills-for-builders
```

Install a specific skill:

```bash
npx skills add <your-gitlab-username>/sample-skills-for-builders@hello-world
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [hello-world](skills/hello-world/) | Template skill demonstrating the Agent Skills format |
| [create-install-scripts](skills/create-install-scripts/) | CI/CD installation scripts for AWS CDK projects |
| [cost-estimator](skills/cost-estimator/) | AWS cost estimation with real-time pricing |
| [security-scan](skills/security-scan/) | Security and compliance scanning for CDK |
| [end-to-end-testing](skills/end-to-end-testing/) | Systematic E2E testing workflow |
| [quip-to-gitlab-wiki](skills/quip-to-gitlab-wiki/) | Quip to GitLab Wiki migration |
| [slidingwindow-summarization](skills/slidingwindow-summarization/) | Strands conversation manager pattern |

### hello-world

A template skill demonstrating the correct skill format and structure. Use this as a starting point for creating your own skills.

**Use when:**
- Learning how to create agent skills
- Starting a new skill from a template
- Understanding the SKILL.md format

## Creating Your Own Skills

See [AGENTS.md](./AGENTS.md) for detailed instructions on creating new skills.

### Quick Start

1. Create a new directory under `skills/`:
   ```bash
   mkdir -p skills/my-skill
   ```

2. Create `SKILL.md` with required frontmatter:
   ```markdown
   ---
   name: my-skill
   description: One sentence describing when to use this skill. Include trigger phrases.
   ---

   # My Skill

   {Description and instructions}
   ```

3. Add optional supporting files:
   - `references/` - Additional documentation
   - `scripts/` - Helper automation scripts
   - `metadata.json` - Extended metadata

### Skill Structure

```
skills/
  my-skill/
    SKILL.md              # Required: skill definition with frontmatter
    metadata.json         # Optional: version, author, references
    references/           # Optional: supporting documentation
    scripts/              # Optional: automation scripts
```

## Skill Format

Every skill requires a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: skill-name              # Required: kebab-case identifier
description: When to use...   # Required: trigger phrases for discovery
license: MIT                  # Optional: defaults to repository license
metadata:                     # Optional: extended metadata
  author: your-name
  version: "1.0.0"
---

# Skill Title

## When to Apply
{Conditions that should trigger this skill}

## How It Works
{Step-by-step workflow}

## Usage
{Examples with code blocks}
```

## Contributing

1. Fork this repository
2. Create your skill in the `skills/` directory
3. Follow the format demonstrated in `skills/hello-world/`
4. Submit a merge request

## License

MIT
