# AWS Price List Bulk API Reference

## Overview

The AWS Price List Bulk API is a public endpoint that requires no authentication. It is used to query On-Demand unit prices for any AWS service.

## Script Usage

```bash
# Basic usage: query pricing for a given offerCode in a given region
python3 .claude/skills/cost-estimator/scripts/fetch-aws-pricing.py <region> \
  --offer-code <CODE> [--filter KEY=VALUE ...] \
  [--cache-dir DIR] [--output FILE]
```

### Examples

```bash
# ECS Fargate (returns both vCPU and Memory usagetype results)
python3 fetch-aws-pricing.py us-east-1 --offer-code AmazonECS --filter usagetype=Fargate

# RDS specific instance type
python3 fetch-aws-pricing.py us-east-1 --offer-code AmazonRDS \
  --filter instanceType=db.t4g.medium --filter databaseEngine=PostgreSQL

# ALB
python3 fetch-aws-pricing.py us-east-1 --offer-code AWSELB --filter usagetype=LoadBalancer

# NAT Gateway (under the AmazonEC2 offerCode)
python3 fetch-aws-pricing.py us-east-1 --offer-code AmazonEC2 --filter usagetype=NatGateway

# OpenSearch
python3 fetch-aws-pricing.py us-east-1 --offer-code AmazonES --filter instanceType=r7g.large

# EC2 GPU instance
python3 fetch-aws-pricing.py cn-northwest-1 --offer-code AmazonEC2 \
  --filter instanceType=g5.12xlarge --filter operatingSystem=Linux
```

### Output

Returns JSON where each result contains `price`, `currency`, `unit`, `description`, and key `attributes`.

### Parameter Reference

- `--filter KEY=VALUE` — Performs substring matching on product attributes. Can be repeated. Common keys: `usagetype`, `instanceType`, `databaseEngine`, `operatingSystem`, `deploymentOption`
- `--cache-dir` — Enables 24-hour file caching to avoid re-downloading large files
- `--output` — Writes to a file; if not specified, outputs to stdout

## Common offerCodes

| offerCode | Included Services |
|-----------|-------------------|
| AmazonECS | ECS Fargate, ECS on EC2 |
| AmazonRDS | RDS (all engines) |
| AmazonES | OpenSearch Service |
| AWSELB | ALB, NLB, CLB |
| AmazonEC2 | EC2 instances, NAT Gateway, EBS |
| AmazonElastiCache | ElastiCache |
| AmazonRedshift | Redshift |
| AmazonSageMaker | SageMaker |
| AmazonDynamoDB | DynamoDB |

## Endpoints

| Region Type | Base URL |
|-------------|----------|
| Global regions | `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/` |
| China regions | `https://pricing.cn-northwest-1.amazonaws.com.cn/offers/v1.0/cn/` |

The script automatically selects the endpoint based on the region prefix (`cn-`).

## Bedrock Pricing

Bedrock uses a different service code (`AmazonBedrockService`) and many newer models are not yet in the API. The script handles this automatically:

```bash
# Query Bedrock — auto-uses Query API + fallback for missing models
python3 fetch-aws-pricing.py us-east-1 --offer-code Bedrock \
  --filter "model=Claude Sonnet 4.6"

# Filter by provider
python3 fetch-aws-pricing.py us-east-1 --offer-code Bedrock \
  --filter "provider=Anthropic"
```

**How it works:**
1. Queries `AmazonBedrockService` via boto3 Query API (paginated)
2. For models not found in API, loads fallback prices from `scripts/bedrock-fallback-prices.json`
3. API results take priority — fallback only fills gaps

**Fallback file maintenance:** Update `scripts/bedrock-fallback-prices.json` when new models are released. Once AWS adds them to the Pricing API, the fallback entries are automatically ignored.

## Monthly Cost Calculation Reference

- Average hours per month: **730**
- ECS Fargate: `(vCPU count × vCPU unit price + GB count × GB unit price) × task count × 730`
- RDS / OpenSearch / EC2: `instance unit price × instance count × 730`
- ALB: `ALB fixed fee × 730` (LCU estimated at 1)
- NAT: `NAT unit price × gateway count × 730`
