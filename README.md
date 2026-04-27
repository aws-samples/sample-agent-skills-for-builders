# Sample Agent Skills for Builders

> A curated, open collection of agent skills that extend AI coding agents (Claude Code, Cursor, Copilot, …) with production-ready AWS, CDK, and engineering workflows.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Format: skills.sh](https://img.shields.io/badge/format-skills.sh-informational)](https://skills.sh/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

Skills are self-contained capability packs. An agent loads only the skill name and one-line description at startup and pulls the full instructions, references, and scripts on demand — so you can ship dozens of capabilities without eating the context window.

This repository is both:

- **a ready-to-use library** — install any skill with a single `npx` command; and
- **a reference implementation** — copy the format when authoring your own.

---

## Contents

- [Install](#install)
- [Available Skills](#available-skills)
- [Author a Skill](#author-a-skill)
- [Contributing](#contributing)
- [License](#license)

## Install

Skills are installed with [`skills.sh`](https://skills.sh/) via `npx`.

```bash
# install every skill in this repo
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders

# or install just one
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill security-scan
```

Once this repository is registered on [skills.sh](https://skills.sh/), you will also be able to browse it at `skills.sh/aws-samples/sample-agent-skills-for-builders`.

## Available Skills

### AWS foundation

| Skill | What it does |
|-------|--------------|
| [aws-mcp-setup](skills/aws-mcp-setup/) | Configure the AWS MCP servers (full server + documentation-only) so agents can query AWS docs and invoke AWS APIs. Prerequisite for the other `aws-*` skills. |

### CDK development

| Skill | What it does |
|-------|--------------|
| [aws-cdk-development](skills/aws-cdk-development/) | CDK expert for TypeScript/Python — app structure, construct patterns, stack composition, and deployment workflows, with MCP-assisted validation. |
| [create-install-scripts](skills/create-install-scripts/) | Generate interactive `install.sh`, GitLab CI pipelines, and CodeBuild setup for CDK projects. |
| [cost-estimator](skills/cost-estimator/) | Estimate CDK infrastructure cost before deploy using real-time AWS Price List data. Produces Markdown and Excel reports. |
| [security-scan](skills/security-scan/) | Aggregated SAST / IaC / secrets / license / container scanning for CDK projects via the Automated Security Helper (ASH). |

### AWS operations & AI

| Skill | What it does |
|-------|--------------|
| [aws-cost-operations](skills/aws-cost-operations/) | Analyze AWS bills, set CloudWatch alarms, query logs, audit CloudTrail, and tighten operational excellence. |
| [aws-agentic-ai](skills/aws-agentic-ai/) | Deploy and manage agents on Bedrock AgentCore — Gateway, Runtime, Memory, Identity, Code Interpreter, Browser, Observability, Registry, and Evaluations. |

### Engineering workflows

| Skill | What it does |
|-------|--------------|
| [end-to-end-testing](skills/end-to-end-testing/) | Systematic E2E testing workflow with evidence capture (screenshots, logs) and report generation. |
| [quip-to-gitlab-wiki](skills/quip-to-gitlab-wiki/) | Migrate Quip documents to GitLab Wiki with full text and media preservation. |
| [strands-context-manager](skills/strands-context-manager/) | Sliding-window + summarization pattern for managing long conversations in Strands Agents. |

## Author a Skill

The full spec lives in [AGENTS.md](./AGENTS.md). The 60-second version:

```bash
mkdir -p skills/my-skill
```

```markdown
---
name: my-skill
description: One sentence describing when to activate. Include the exact trigger phrases a user might say.
---

# My Skill

## When to Apply
- …

## How It Works
1. …

## Usage
…
```

Optional supporting files:

```
skills/my-skill/
  SKILL.md         # required
  metadata.json    # optional: version, author, tags
  references/      # optional: long-form docs, loaded on demand
  scripts/         # optional: automation invoked by the agent
```

Rules of thumb:

- **Kebab-case** directory names that match the `name` field in frontmatter.
- **Keep `SKILL.md` under ~500 lines** — push long content into `references/` so it only loads when the agent decides to use it.
- **Write the `description` as trigger phrases** — it is the only text an agent sees at startup when deciding whether to pull the skill.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the PR workflow and [AGENTS.md](./AGENTS.md) for the skill spec.

To report a security issue, please use the [AWS vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/) rather than opening a public issue.

This project adopts the [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct); see [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

## License

Apache-2.0. See [LICENSE](./LICENSE).
