# Cost Estimator Skill

Analyze and estimate AWS infrastructure costs for CDK projects using real-time pricing data from AWS.

## Quick Start

### Installation

Copy this skill directory into your agent's skills folder (e.g., `~/.claude/skills/` for Claude Code):

```bash
cp -r skills/cost-estimator ~/.claude/skills/
```

### Basic Usage

```bash
# Estimate costs for your CDK project in a specific region
python scripts/fetch-aws-pricing.py --region us-east-1

# Generate an Excel report with detailed cost breakdown
python scripts/generate-pricing-excel.py --input resources.json --output costs.xlsx
```

## Prerequisites

Before using this skill, ensure you have:

- **Python 3.8+** installed
- **AWS CDK project** with synthesizable stacks
- **Python packages**: `pandas`, `openpyxl`
- **AWS credentials** configured (for AWS Pricing API access)
- **Valid AWS regions** (standard regions or China regions: cn-north-1, cn-northwest-1)

## File Structure

```
cost-estimator/
├── README.md                      # This file
├── SKILL.md                       # Skill definition and metadata
├── scripts/
│   ├── fetch-aws-pricing.py       # Fetch real-time pricing from AWS
│   ├── generate-pricing-excel.py  # Create detailed Excel reports
│   └── bedrock-fallback-prices.json  # AI model pricing fallback data
├── references/
│   ├── cdk-analysis.md            # Guide to scanning CDK resources
│   ├── pricing-api.md             # AWS Bulk API usage details
│   ├── report-generation.md       # Report creation methodology
│   └── bedrock-pricing.md         # Bedrock model pricing guide
```

## Common Tasks

### Estimate costs for a single region

```bash
python scripts/fetch-aws-pricing.py --region us-west-2
```

Output files will be saved to `cost-estimates/` directory:
- `cost-estimate-us-west-2.xlsx` - Detailed spreadsheet with formulas
- `cost-estimate-us-west-2.md` - Markdown summary for documentation

### Generate costs for multiple regions

Run the pricing script for each region:

```bash
for region in us-east-1 us-west-2 eu-west-1; do
  python scripts/fetch-aws-pricing.py --region $region
done
```

### Calculate Bedrock model costs

The skill includes Bedrock model pricing data. Reference `references/bedrock-pricing.md` for supported models and pricing structures.

## Output Files

Generated reports are saved to the `cost-estimates/` directory:

| File | Purpose |
|------|---------|
| `cost-estimate-{region}.xlsx` | Comprehensive cost breakdown with per-resource costs |
| `cost-estimate-{region}.md` | Summary report for sharing and documentation |

## Supported AWS Regions

- **Standard Regions**: us-east-1, us-west-1, us-west-2, eu-west-1, eu-central-1, ap-southeast-1, ap-northeast-1, and all other public AWS regions
- **China Regions**: cn-north-1, cn-northwest-1 (with pricing in CNY)

## References

For detailed documentation:

- **[CDK Analysis](./references/cdk-analysis.md)** - Learn how the skill scans and identifies AWS resources in your CDK code
- **[Pricing API](./references/pricing-api.md)** - Understand AWS Bulk API integration and pricing data sources
- **[Report Generation](./references/report-generation.md)** - Details on Excel and Markdown report creation
- **[Bedrock Pricing](./references/bedrock-pricing.md)** - AI model pricing including Claude, Titan, and Llama

## Troubleshooting

### AWS Credentials Not Found
Ensure your AWS credentials are configured:
```bash
aws configure
# or set AWS_PROFILE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
```

### Python Dependencies Missing
Install required packages:
```bash
pip install pandas openpyxl
```

### No Resources Found
Verify your CDK project can be synthesized:
```bash
cdk synth
```

## License

MIT
