# Security Scan Skill

A comprehensive security and compliance scanning solution for AWS CDK projects, providing multi-tool analysis including code security, license compliance, container vulnerability scanning, and aggregated SAST/IaC/secret analysis.

## Installation

```bash
npx skills add https://github.com/aws-samples/sample-agent-skills-for-builders --skill security-scan
```

## Quick Start

Trigger the skill with natural language prompts:

```bash
# Security audits
"Run security scan on my CDK project"
"Check this project for vulnerabilities"

# Compliance checks
"Generate security compliance report"
"Verify license compliance for all dependencies"

# Aggregated SAST/IaC/secret scanning
"Run ASH aggregated security scan"
```

## Prerequisites

Before using this skill, ensure you have the following installed:

- **AWS CDK** - AWS Cloud Development Kit for infrastructure as code
- **Viperlight** - Code security scanner
  ```bash
  npm install -g viperlight
  ```
- **Trivy** - Container vulnerability scanner
  ```bash
  brew install trivy  # macOS
  # or
  apt-get install trivy  # Linux
  ```
- **ASH (Automated Security Helper)** - Aggregated security scanner from AWS Labs ([awslabs/automated-security-helper](https://github.com/awslabs/automated-security-helper)) that bundles bandit, checkov, semgrep, grype, and other tools. Requires Python 3.10+, Docker (running), and `uv`. See [references/ash-scan.md](./references/ash-scan.md) for the pinned install command.

## What the Skill Does

The security-scan skill executes a 9-step comprehensive security workflow:

1. **Architecture Diagram** - Visualizes your system architecture
2. **CDK Synthesis** - Generates CloudFormation templates
3. **Viperlight Scan** - Detects code security issues
4. **License Check** - Verifies dependency license compliance
5. **Trivy Scan** - Scans container images for vulnerabilities
6. **ASH Scan** - Runs Automated Security Helper (aggregates SAST, IaC, and secret scanners)
7. **Deployment Verification** - Validates deployment readiness
8. **Summary Report** - Creates a findings summary
9. **HTML Report** - Generates a visual HTML report

All 9 steps execute sequentially. The workflow continues even if individual steps encounter failures.

## Output Structure

Security scan results are saved to `security-scan-results/{TIMESTAMP}/` with the following structure:

```
security-scan-results/2024-01-15-14-30-45/
├── viperlight-output.json
├── license-report.json
├── trivy-report.json
├── ash-report.json
├── deployment-check.json
├── clean-results/
│   ├── vulnerabilities.json
│   ├── license-issues.json
│   └── best-practices-violations.json
├── architecture-diagram.png
└── security-report.html
```

Open `security-report.html` in your browser to view a visual summary of all findings.

## Usage Examples

### Basic Security Scan

```
User: "Run a complete security scan on my CDK project"
```

The skill will execute all 9 scanning steps and generate reports.

### License Compliance Check

```
User: "Check if all dependencies have compliant licenses"
```

Focuses on license scanning and generates a compliance report.

### Vulnerability Assessment

```
User: "Scan container images for vulnerabilities before deployment"
```

Runs Trivy container scanning and generates vulnerability findings.

## File Structure

```
skills/security-scan/
├── SKILL.md                    # Skill definition and trigger rules
├── README.md                   # This file
├── references/
│   ├── architecture-diagram.md
│   ├── cdk-synthesis.md
│   ├── viperlight-scan.md
│   ├── license-check.md
│   ├── trivy-scan.md
│   ├── ash-scan.md
│   ├── deployment-verification.md
│   └── report-generation.md
└── scripts/
    └── [automation scripts, if present]
```

Consult the reference files for detailed information on each scanning tool and step.

## Key Features

- **Multi-tool analysis** - Combines industry-standard security tools
- **Comprehensive reports** - HTML visual reports with findings
- **License compliance** - Ensures all dependencies meet licensing requirements
- **Container security** - Scans images for known vulnerabilities
- **Aggregated security scanning** - ASH consolidates findings from multiple SAST/IaC/secret scanners
- **Non-blocking failures** - Pipeline continues even if individual scans fail

## Interpreting Results

Check the generated `security-report.html` for a visual overview of:
- **High priority vulnerabilities** - Require immediate attention
- **License violations** - Dependencies with non-compliant licenses
- **SAST / IaC / secret findings** - From ASH-aggregated scanners (bandit, checkov, semgrep, grype, etc.)
- **Deployment blockers** - Issues preventing safe deployment

Review the JSON reports in `clean-results/` for programmatic access to findings.

## Next Steps

1. Install all prerequisites (see Prerequisites section)
2. Navigate to your AWS CDK project
3. Trigger the skill with a natural language prompt
4. Review the generated security report
5. Address any high-priority findings
6. Re-run the scan to verify fixes

## Support

For detailed tool-specific documentation, see the `references/` directory included with this skill.
