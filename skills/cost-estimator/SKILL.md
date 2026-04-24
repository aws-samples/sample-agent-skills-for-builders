---
name: cost-estimator
description: Estimate AWS costs for CDK projects using real-time pricing data. Use when calculating infrastructure costs, generating pricing reports, or analyzing CDK resource costs before deployment.
license: MIT
metadata:
  author: sample-skills-for-builders
  version: "1.0.0"
---

# Cost Estimator

AWS cost estimation tool for CDK projects with real-time pricing from AWS Price List Bulk API.

## When to Apply

Reference this skill when:
- Estimating AWS infrastructure costs
- Analyzing CDK project resource costs
- Generating pricing reports (Excel/Markdown)
- Comparing costs across AWS regions
- Calculating Bedrock model costs

## How It Works

1. **Confirm Region** - Select target AWS region(s)
2. **Scan Resources** - Analyze CDK code for AWS resources
3. **Fetch Pricing** - Get real-time prices from AWS Bulk API
4. **Generate Reports** - Create Excel and Markdown reports

## Prerequisites

- AWS CDK project with synthesizable stacks
- Python 3.8+ with pandas, openpyxl
- AWS credentials (for pricing API access)

## Usage

```bash
# Fetch AWS pricing data
python scripts/fetch-aws-pricing.py --region us-east-1

# Generate Excel report
python scripts/generate-pricing-excel.py --input resources.json --output costs.xlsx
```

## Output Files

Reports are saved to `cost-estimates/`:
- `cost-estimate-{region}.xlsx` - Detailed Excel report
- `cost-estimate-{region}.md` - Markdown summary

## Supported Regions

- All standard AWS regions
- China regions (cn-north-1, cn-northwest-1) with CNY pricing

## References

- [CDK Analysis](./references/cdk-analysis.md) - Resource scanning guide
- [Pricing API](./references/pricing-api.md) - AWS Bulk API usage
- [Report Generation](./references/report-generation.md) - Report creation
- [Bedrock Pricing](./references/bedrock-pricing.md) - AI model pricing
