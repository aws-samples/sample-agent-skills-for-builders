# Create Install Scripts Skill

Automate the generation of deployment infrastructure for AWS CDK projects. This skill creates CI/CD configurations and installation scripts for GitLab CI and AWS CodeBuild environments.

## Quick Start

### Installation

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill create-install-scripts
```

### First Use

```bash
# From your CDK project directory
./scripts/setup-cicd.sh
```

This will generate:
- `install.sh` - Interactive deployment script
- `.gitlab-ci.yml` - GitLab CI/CD pipeline configuration
- `buildspec.yml` - AWS CodeBuild specification

## Usage Examples

### Generate Installation Script
```bash
# Create an interactive install.sh for your CDK project
./scripts/setup-cicd.sh
```

### With Agent
Ask your AI agent directly:
```
"Set up CI/CD for my CDK project"
"Create install scripts for deployment"
"Generate GitLab CI configuration"
```

## File Structure

```
create-install-scripts/
├── SKILL.md                    # Skill definition and metadata
├── README.md                   # This file
├── scripts/
│   └── setup-cicd.sh          # Main setup automation script
└── references/
    ├── install-script-guide.md    # Detailed install.sh creation
    ├── gitlab-ci-setup.md         # GitLab CI/CD configuration
    ├── codebuild-setup.md         # AWS CodeBuild setup
    └── common-pitfalls.md         # Troubleshooting guide
```

## Prerequisites

Before using this skill, ensure you have:

- **AWS CDK Project** - An initialized CDK project (run `cdk init` if needed)
- **AWS Credentials** - Configured in `~/.aws/credentials` or environment variables
- **GitLab Repository** - For CI/CD integration (if using GitLab)
- **Docker** (optional) - Required only if using AWS CodeBuild for Docker image builds
- **Node.js/npm** - For CDK operations

## Generated Files Overview

| File | Purpose | When Generated |
|------|---------|---|
| `install.sh` | Interactive local deployment script with color output and validation | Always |
| `.gitlab-ci.yml` | GitLab CI/CD pipeline for automated deployments | When GitLab integration enabled |
| `buildspec.yml` | AWS CodeBuild specification for container builds | When CodeBuild integration enabled |

## Documentation

For detailed information, refer to:

- **[Install Script Guide](./references/install-script-guide.md)** - Learn how to customize install.sh, handle environment variables, and add pre/post-deployment hooks
- **[GitLab CI Setup](./references/gitlab-ci-setup.md)** - Configure GitLab CI/CD pipelines, secrets, and deployment stages
- **[CodeBuild Setup](./references/codebuild-setup.md)** - Set up AWS CodeBuild for automated container builds and CDK deployments
- **[Common Pitfalls](./references/common-pitfalls.md)** - Troubleshoot common issues and best practices

## Support & Contribution

For issues or questions, check the Common Pitfalls guide first. Contributions are welcome via pull requests.
