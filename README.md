# Sample Agent Skills for Builders

A curated collection of ready-to-use agent skills covering AWS development, security scanning, testing, and AI coding workflows. Skills are self-contained capability packs that extend AI coding agents (Claude Code, Cursor, Copilot, etc.) with specialized knowledge, reference material, and automation scripts — drop a skill directory into your agent's skills folder and it's live.

This repository also serves as a reference for builders authoring their own skills.

## Installation

Install skills from this repository using [`skills.sh`](https://skills.sh/) via `npx`.

Install all skills from the repository:

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders
```

Install a specific skill by name:

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill security-scan
```

Once this repository is registered on [skills.sh](https://skills.sh/), you will also be able to
browse all skills at `skills.sh/aws-samples/sample-agent-skills-for-builders`.

## Available Skills

| Skill | Description |
|-------|-------------|
| [create-install-scripts](skills/create-install-scripts/) | CI/CD installation scripts for AWS CDK projects |
| [cost-estimator](skills/cost-estimator/) | AWS cost estimation with real-time pricing |
| [security-scan](skills/security-scan/) | Security and compliance scanning for CDK |
| [end-to-end-testing](skills/end-to-end-testing/) | Systematic E2E testing workflow |
| [quip-to-gitlab-wiki](skills/quip-to-gitlab-wiki/) | Quip to GitLab Wiki migration |
| [strands-context-manager](skills/strands-context-manager/) | Strands conversation manager pattern |
| [aws-mcp-setup](skills/aws-mcp-setup/) | AWS Documentation MCP configuration |
| [aws-cdk-development](skills/aws-cdk-development/) | CDK best practices with AWS CDK MCP |
| [aws-cost-operations](skills/aws-cost-operations/) | Cost estimation and operational excellence |
| [aws-agentic-ai](skills/aws-agentic-ai/) | Bedrock AgentCore AI agent deployment |

The last four skills are adapted from [zxkane/aws-skills](https://github.com/zxkane/aws-skills)
(MIT License, © 2025 Mengxin Zhu). See each skill's `LICENSE.upstream` file and the
[NOTICE](./NOTICE) file for attribution.

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

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on how to
contribute a new skill or improve an existing one.

Short version:

1. Fork this repository
2. Create your skill in the `skills/` directory (see any existing skill as a reference)
3. Follow the format documented in [AGENTS.md](./AGENTS.md)
4. Submit a pull request

## Security

See [CONTRIBUTING](./CONTRIBUTING.md#security-issue-notifications) for information about reporting
security issues.

## Code of Conduct

This project has adopted the [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct).
See [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) for details.

## License

This library is licensed under the Apache-2.0 License. See the [LICENSE](./LICENSE) file.
