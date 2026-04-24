# Amazon Bedrock Model Pricing Reference

> Last updated: 2026-03-03. Source: https://aws.amazon.com/bedrock/pricing/

Bedrock models are NOT available in the Bulk Price List API. Use the hardcoded prices below when estimating Bedrock costs.

## Anthropic Claude Models (On-Demand)

| Model | Input ($/1M tokens) | Output ($/1M tokens) | Batch Input | Batch Output | Cache Write (5m) | Cache Write (1h) | Cache Read |
|---|---:|---:|---:|---:|---:|---:|---:|
| Claude Sonnet 4.6 | $3.00 | $15.00 | $1.50 | $7.50 | $3.75 | $6.00 | $0.30 |
| Claude Sonnet 4.6 — Long Context | $6.00 | $22.50 | $3.00 | $11.25 | $7.50 | $12.00 | $0.60 |
| Claude Opus 4.6 | $5.00 | $25.00 | $2.50 | $12.50 | $6.25 | $10.00 | $0.50 |
| Claude Opus 4.6 — Long Context | $10.00 | $37.50 | $5.00 | $18.75 | $12.50 | $20.00 | $1.00 |
| Claude Opus 4.5 | $5.00 | $25.00 | $2.50 | $12.50 | $6.25 | $10.00 | $0.50 |
| Claude Haiku 4.5 | $1.00 | $5.00 | $0.50 | $2.50 | $1.25 | $2.00 | $0.10 |
| Claude Sonnet 4.5 | $3.00 | $15.00 | $1.50 | $7.50 | $3.75 | $6.00 | $0.30 |
| Claude Sonnet 4.5 — Long Context | $6.00 | $22.50 | $3.00 | $11.25 | $7.50 | $12.00 | $0.60 |
| Claude Sonnet 4 | $3.00 | $15.00 | $1.50 | $7.50 | $3.75 | N/A | $0.30 |
| Claude Sonnet 4 — Long Context | $6.00 | $22.50 | $3.00 | $11.25 | $7.50 | N/A | $0.60 |

**Long Context** pricing applies when input exceeds 200K tokens (1M context window beta).

## Amazon Embedding Models

| Model | Input ($/1M tokens) |
|---|---:|
| Titan Text Embeddings V2 | $0.02 |
| Titan Multimodal Embeddings G1 | $0.80 (image), $0.02 (text) |

## Amazon Nova Models

| Model | Input ($/1M tokens) | Output ($/1M tokens) |
|---|---:|---:|
| Nova Micro | $0.035 | $0.14 |
| Nova Lite | $0.06 | $0.24 |
| Nova Pro | $0.80 | $3.20 |

## OpenSearch Serverless (AOSS)

Not in Bulk API. Published pricing:

| Component | Price | Unit |
|---|---:|---|
| Indexing OCU | $0.24 | OCU-hour |
| Search & Query OCU | $0.24 | OCU-hour |

Minimum: **2 OCU for indexing + 2 OCU for search = 4 OCU total**.

## Neptune Serverless

Available via Bulk API (`AmazonNeptune`, filter `usagetype=Serverless`), but listed here for reference:

| Component | Price | Unit |
|---|---:|---|
| NCU | $0.1608 | NCU-hour |

## Usage Notes

- Default to **on-demand** pricing unless the user specifies batch or caching.
- For GraphRAG / RAG workloads, remember to account for **document parsing token usage** (entity extraction, relationship extraction, summarization) — typically 5-10x amplification of raw document token count.
- For agent workloads, estimate token usage per interaction and multiply by expected daily/monthly volume.
