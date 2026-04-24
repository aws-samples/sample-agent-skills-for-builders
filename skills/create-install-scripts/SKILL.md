---
name: create-install-scripts
description: Generate CI/CD installation scripts for AWS CDK projects. Use when setting up deployment pipelines, creating install.sh scripts, configuring GitLab CI, or setting up AWS CodeBuild for CDK deployments.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# Create Install Scripts

Generate installation scripts, GitLab CI configuration, and CodeBuild deployment setup for AWS CDK projects.

## When to Apply

Reference this skill when:
- Setting up deployment pipelines for CDK projects
- Creating interactive install.sh scripts
- Configuring GitLab CI/CD for AWS deployments
- Setting up AWS CodeBuild for Docker image builds
- Automating CDK deployment workflows

## How It Works

1. Analyze the CDK project structure
2. Generate `install.sh` for interactive local deployments
3. Generate `.gitlab-ci.yml` for GitLab CI/CD
4. Generate `buildspec.yml` for AWS CodeBuild
5. Configure deployment variables and secrets

## Prerequisites

- AWS CDK project initialized
- GitLab repository (for CI/CD)
- AWS credentials configured
- Docker (if using CodeBuild for images)

## Usage

```bash
# Run the setup script
./scripts/setup-cicd.sh

# Or trigger via agent
"Set up CI/CD for my CDK project"
"Create install scripts for deployment"
```

## Generated Files

| File | Purpose |
|------|---------|
| `install.sh` | Interactive installation script |
| `.gitlab-ci.yml` | GitLab CI/CD pipeline |
| `buildspec.yml` | AWS CodeBuild specification |

## References

- [Install Script Guide](./references/install-script-guide.md) - Complete install.sh creation guide
- [GitLab CI Setup](./references/gitlab-ci-setup.md) - GitLab CI/CD configuration
- [CodeBuild Setup](./references/codebuild-setup.md) - AWS CodeBuild setup
- [Common Pitfalls](./references/common-pitfalls.md) - Troubleshooting guide
