#!/usr/bin/env python3
"""
AWS Price List Bulk API query tool.

All queries use the public Bulk API — no AWS credentials needed.
For Bedrock models not yet in the API, falls back to bedrock-fallback-prices.json.

Usage:
    python3 fetch-aws-pricing.py <region> --offer-code CODE [--filter KEY=VALUE ...]
        [--cache-dir DIR] [--output FILE]

Examples:
    # Fargate prices
    python3 fetch-aws-pricing.py us-east-1 --offer-code AmazonECS \
        --filter usagetype=Fargate

    # RDS db.t4g.medium
    python3 fetch-aws-pricing.py cn-northwest-1 --offer-code AmazonRDS \
        --filter instanceType=db.t4g.medium --filter databaseEngine=PostgreSQL

    # NAT Gateway (under AmazonEC2)
    python3 fetch-aws-pricing.py us-east-1 --offer-code AmazonEC2 \
        --filter usagetype=NatGateway

    # Bedrock — tries AmazonBedrockService then AmazonBedrock, plus fallback
    python3 fetch-aws-pricing.py us-east-1 --offer-code Bedrock \
        --filter "model=Claude Sonnet 4.6"

Uses only Python stdlib (urllib). No boto3 or AWS CLI dependency.
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

GLOBAL_BASE = "https://pricing.us-east-1.amazonaws.com"
CN_BASE = "https://pricing.cn-northwest-1.amazonaws.com.cn"
CACHE_TTL = 86400  # 24 hours

# Bedrock offer codes to try via Bulk API (in order of preference)
BEDROCK_SERVICE_CODES = ["AmazonBedrockService", "AmazonBedrock"]

# Path to fallback prices JSON (relative to this script)
BEDROCK_FALLBACK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bedrock-fallback-prices.json")

# Attributes to keep in output
KEEP_ATTRS = (
    # infra
    "servicecode", "usagetype", "operation", "regionCode",
    "instanceType", "instanceFamily",
    "databaseEngine", "deploymentOption",
    "operatingSystem", "cpuArchitecture",
    "tenancy", "storage", "networkPerformance",
    "vcpu", "memory",
    # bedrock
    "model", "provider", "inferenceType", "featuretype",
)


def is_cn(region: str) -> bool:
    return region.startswith("cn-")


def base_url(region: str) -> tuple[str, str]:
    host = CN_BASE if is_cn(region) else GLOBAL_BASE
    path = "/offers/v1.0/cn" if is_cn(region) else "/offers/v1.0/aws"
    return host, host + path


def cache_key(cache_dir: str, url: str) -> str:
    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    return os.path.join(cache_dir, f"{h}.json")


def fetch_json(url: str, cache_dir: str | None = None) -> dict:
    if cache_dir:
        cp = cache_key(cache_dir, url)
        if os.path.exists(cp) and (time.time() - os.path.getmtime(cp)) < CACHE_TTL:
            with open(cp) as f:
                return json.load(f)

    print(f"  Fetching {url[:120]}...", file=sys.stderr)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"  Error: {e}", file=sys.stderr)
        return {}

    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_key(cache_dir, url), "w") as f:
            json.dump(data, f)
    return data


def resolve_region_url(host, api_base, offer_code, region, cache_dir):
    index_url = f"{api_base}/{offer_code}/current/region_index.json"
    index = fetch_json(index_url, cache_dir)
    if not index:
        return None
    region_info = index.get("regions", {}).get(region)
    if not region_info:
        print(f"  Region {region} not in {offer_code}", file=sys.stderr)
        return None
    ver_url = region_info.get("currentVersionUrl", "")
    return (host + ver_url) if ver_url.startswith("/") else ver_url


def extract_on_demand_price(terms: dict, sku: str) -> dict:
    for _k, offer in terms.get(sku, {}).items():
        for _dk, dim in offer.get("priceDimensions", {}).items():
            per_unit = dim.get("pricePerUnit", {})
            for currency, val in per_unit.items():
                try:
                    p = float(val)
                    if p > 0:
                        return {"price": p, "currency": currency, "unit": dim.get("unit", ""),
                                "description": dim.get("description", "")}
                except ValueError:
                    pass
    return {}


def match_filters(attrs: dict, filters: list[tuple[str, str]]) -> bool:
    for key, val in filters:
        attr_val = attrs.get(key, "")
        if val.lower() not in attr_val.lower():
            return False
    return True


# ---------- Bulk API query ----------

def query_bulk(region, offer_code, filters, cache_dir):
    host, api_base = base_url(region)
    region_url = resolve_region_url(host, api_base, offer_code, region, cache_dir)
    if not region_url:
        return []

    data = fetch_json(region_url, cache_dir)
    if not data:
        return []

    products = data.get("products", {})
    terms = data.get("terms", {}).get("OnDemand", {})
    results = []

    for sku, product in products.items():
        attrs = product.get("attributes", {})
        if not match_filters(attrs, filters):
            continue

        price_info = extract_on_demand_price(terms, sku)
        if not price_info:
            continue

        results.append({
            "sku": sku,
            "productFamily": product.get("productFamily", attrs.get("productFamily", "")),
            "attributes": {k: v for k, v in attrs.items() if k in KEEP_ATTRS},
            **price_info,
        })

    return results


# ---------- Bedrock fallback from local JSON ----------

def query_bedrock_fallback(region, filters):
    """Load hardcoded Bedrock prices from bedrock-fallback-prices.json."""
    if not os.path.exists(BEDROCK_FALLBACK_PATH):
        print(f"  Fallback file not found: {BEDROCK_FALLBACK_PATH}", file=sys.stderr)
        return []

    with open(BEDROCK_FALLBACK_PATH) as f:
        data = json.load(f)

    entries = data.get(region, data.get("us-east-1", []))
    results = []
    for entry in entries:
        attrs = {
            "model": entry.get("model", ""),
            "provider": entry.get("provider", ""),
            "inferenceType": entry.get("inferenceType", ""),
        }
        if not match_filters(attrs, filters):
            continue
        results.append({
            "sku": "fallback",
            "productFamily": "Amazon Bedrock (fallback)",
            "attributes": attrs,
            "price": entry["price"],
            "currency": "USD",
            "unit": entry.get("unit", "1K tokens"),
            "description": f"Fallback: {entry['model']} {entry['inferenceType']} @ ${entry['price']}/{entry.get('unit','1K tokens')}",
        })
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Query AWS Price List Bulk API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("region", help="AWS region (e.g. us-east-1, cn-northwest-1)")
    parser.add_argument("--offer-code", required=True,
                        help="Service offer code. Use 'Bedrock' as shortcut for AmazonBedrockService + fallback.")
    parser.add_argument("--filter", action="append", default=[],
                        help="Filter as KEY=VALUE (substring match). Repeatable.")
    parser.add_argument("--cache-dir", default=None, help="Cache dir (24h TTL)")
    parser.add_argument("--output", default=None, help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    filters = []
    for f in args.filter:
        if "=" not in f:
            print(f"Invalid filter (need KEY=VALUE): {f}", file=sys.stderr)
            sys.exit(1)
        k, v = f.split("=", 1)
        filters.append((k, v))

    offer_code = args.offer_code

    # Bedrock shortcut: Bulk API + fallback for missing models
    if offer_code.lower() in ("bedrock", "amazonbedrock", "amazonbedrockservice"):
        api_results = []
        for svc in BEDROCK_SERVICE_CODES:
            api_results = query_bulk(args.region, svc, filters, args.cache_dir)
            if api_results:
                offer_code = svc
                break
        if not api_results:
            offer_code = "AmazonBedrockService"

        # Fill gaps from fallback for models not in API
        api_models = {r["attributes"].get("model", "") for r in api_results}
        fallback_results = query_bedrock_fallback(args.region, filters)
        merged = list(api_results)
        fallback_count = 0
        for fb in fallback_results:
            if fb["attributes"].get("model", "") not in api_models:
                merged.append(fb)
                fallback_count += 1
        if fallback_count:
            print(f"  Added {fallback_count} entries from fallback (models not in API)", file=sys.stderr)
        results = merged
    else:
        results = query_bulk(args.region, offer_code, filters, args.cache_dir)

    output = {
        "region": args.region,
        "offerCode": offer_code,
        "filters": {k: v for k, v in filters},
        "resultCount": len(results),
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }

    text = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            f.write(text)
        print(f"Wrote {len(results)} results to {args.output}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
