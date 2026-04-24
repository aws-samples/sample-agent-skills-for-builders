---
name: security-scan
description: Comprehensive security and compliance scanning for AWS CDK projects. Use when running security audits, checking license compliance, scanning container vulnerabilities, or verifying AWS best practices before deployment.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# Security Scan

Comprehensive AWS CDK project security and compliance scanning with multi-tool analysis.

## When to Apply

Reference this skill when:
- Running security audits on CDK projects
- Checking license compliance
- Scanning container images for vulnerabilities
- Verifying AWS best practices
- Generating security reports for review

## Scan Workflow

**IMPORTANT: All 9 steps are mandatory. Do not skip steps regardless of time constraints.**

1. **Architecture Diagram** - Capture system architecture
2. **CDK Synthesis** - Generate CloudFormation templates
3. **Viperlight Scan** - Code security analysis
4. **License Check** - Dependency license compliance
5. **Trivy Scan** - Container vulnerability scanning
6. **ASH Scan** - AWS Security Hub best practices
7. **Deployment Verification** - Validate deployment readiness
8. **Summary Report** - Generate findings summary
9. **HTML Report** - Create visual report

## Prerequisites

- AWS CDK project
- Viperlight CLI installed
- Trivy CLI installed
- ASH (AWS Security Hub) CLI

## Usage

```bash
# Run security scan
"Run security scan on my CDK project"
"Check this project for vulnerabilities"
"Generate security compliance report"
```

## Output

Results saved to `security-scan-results/{TIMESTAMP}/`:
- Raw scan outputs per tool
- `clean-results/` - Parsed findings
- `security-report.html` - Visual report

## Enforcement Rules

- Execute ALL scan commands (no skipping)
- Fix issues found (don't just comment them)
- Non-interactive execution only
- Continue pipeline on individual step failures

## References

- [Architecture Diagram](./references/architecture-diagram.md)
- [CDK Synthesis](./references/cdk-synthesis.md)
- [Viperlight Scan](./references/viperlight-scan.md)
- [License Check](./references/license-check.md)
- [Trivy Scan](./references/trivy-scan.md)
- [ASH Scan](./references/ash-scan.md)
- [Deployment Verification](./references/deployment-verification.md)
- [Report Generation](./references/report-generation.md)
