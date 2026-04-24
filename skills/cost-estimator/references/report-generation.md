# Report Style Guide

## Excel Generation

Use `generate-pricing-excel.py` to convert the prepared JSON into a styled Excel file.

### Script Usage

```bash
python3 .claude/skills/cost-estimator/scripts/generate-pricing-excel.py \
  --input cost-estimates/.report.json \
  --output cost-estimates/pricing-model-YYYY-MM-DD.xlsx
```

### Input JSON Format

```json
{
  "sheets": [
    {
      "name": "us-east-1",
      "columns": ["Module", "AWS Service", "Required", "Configuration", "Est. Price/Month (USD $)", "Note"],
      "columnWidths": [20, 35, 10, 40, 18, 40],
      "rows": [
        {"values": ["Console", "Amazon ECS Fargate", "Y", "1 vCPU, 2 GB, 2 tasks", 72.10, "API Service"], "module": "Console"},
        {"values": ["", "Amazon RDS", "Y", "db.t4g.medium, Single-AZ", 58.95, ""], "module": "Console"},
        {"values": ["Core", "Amazon ECS Fargate", "Y", "1 vCPU, 2 GB", 36.05, ""], "module": "Core"}
      ],
      "totalRow": {"label": "Total", "value": 639.29},
      "assumptions": [
        "Deployed in us-east-1 region",
        "ECS utilization: 10%, do not assume high usage to avoid auto-scaling cost"
      ]
    },
    {
      "name": "Unit Pricing Reference",
      "columns": ["AWS Service", "Configuration", "Unit Price", "Unit", "Monthly Cost"],
      "columnWidths": [30, 40, 15, 15, 18],
      "rows": [
        {"values": ["Amazon ECS", "1 vCPU", 0.04048, "vCPU-hour", 29.55], "module": ""},
        {"values": ["", "2 GiB memory", 0.00445, "GiB-hour", 6.50], "module": ""}
      ]
    }
  ]
}
```

### Required Content

1. **Pricing Sheet** (one per region): Resource detail table + `totalRow` + `assumptions`
2. **Unit Pricing Reference Sheet**: A separate sheet listing all unit prices used and monthly cost calculations

### Auto-Applied Styles

| Element | Style |
|---------|-------|
| Header row | Gray background (#607D8B) + white text + bold |
| Module coloring | Light blue/green/orange/purple/red/cyan/yellow/lime cycling per module |
| Total row | Dark gray background (#37474F) + white text + bold |
| Price column | Right-aligned, `#,##0.00` format |
| Key Assumptions | Below the Total row, bold title + bulleted list |
| Borders | Thin gray lines |

---

## Markdown Style

The agent directly generates the Markdown file, following this style:

### Structure Template

```markdown
# Pricing Model

## <Region> Pricing

| Module | AWS Service (BOM) | Required | Configuration | Est. Price/Month (<currency>) | Note |
|---|---|---|---|---:|---|
| Console | Amazon ECS Fargate | Y | 1 vCPU, 2 GB, 2 tasks | 72.10 | API Service |
| | Amazon RDS (PostgreSQL) | Y | db.t4g.medium, Single-AZ | 58.95 | |
| Core | Amazon ECS Fargate | Y | 1 vCPU, 2 GB | 36.05 | |
| **Total** | | | | **639.29** | |

**Key Assumptions:**

- Deployed in us-east-1 region
- ECS utilization: 10%
- ...

---

## Unit Pricing Reference

> Avg. hours in a month: **730**

| AWS Service | Configuration | Unit Price | Unit | Monthly Cost |
|---|---|---:|---|---:|
| Amazon ECS | 1 vCPU | 0.04048 | vCPU-hour | 29.55 |
| | 2 GiB memory | 0.00445 | GiB-hour | 6.50 |
| Amazon RDS | db.t4g.medium, Single-AZ | 0.065 | hour | 47.45 |
| ...
```

### Rules

- One `##` section per region
- Price column right-aligned (`---:`)
- Total row in bold
- **Key Assumptions** must follow each pricing table, explaining usage assumptions
- **Unit Pricing Reference** must be at the end, listing all fetched unit prices
- Minimal-cost services represented with `—`
- Module name displayed only on the first row of each module
