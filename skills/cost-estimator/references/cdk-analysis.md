# Step 2: Scan Resources and Confirm

## Purpose

Automatically scan CDK code and architecture documentation in the project, discover all AWS resource definitions, present them to the user for confirmation, and generate a resource list JSON.

## 2.1 Discover CDK Directories

First, locate the CDK code directories in the project without assuming fixed paths:

```
Search patterns (by priority):
1. glob `**/cdk.json` → find CDK app entry point, infer lib directory from the app field
2. glob `**/lib/**/*.ts` files that import `aws-cdk-lib` or `@aws-cdk`
3. glob `**/infra/**/*.ts` with the same imports
4. glob `**/stack*.ts`, `**/construct*.ts`
```

Record all discovered CDK source file paths for subsequent grep operations.

## 2.2 Resource Scan Checklist

For the discovered CDK files, search for AWS resources using the following patterns. Extract key configuration parameters for each resource type.

### Compute

| Resource | grep Pattern | Fields to Extract |
|----------|-------------|-------------------|
| ECS Fargate | `FargateTaskDefinition`, `FargateService` | cpu, memoryLimitMiB, desiredCount |
| EC2 Instance | `Instance(`, `ec2.Instance` | instanceType |
| Lambda | `Function(`, `lambda.Function` | memorySize, timeout, runtime |
| ECS on EC2 | `Ec2TaskDefinition`, `Ec2Service` | instanceType, desiredCount |

### Database & Storage

| Resource | grep Pattern | Fields to Extract |
|----------|-------------|-------------------|
| RDS | `DatabaseInstance`, `DatabaseCluster` | instanceType, engine, multiAz |
| Aurora | `ServerlessCluster`, `DatabaseCluster` | instanceType, minCapacity, maxCapacity |
| DynamoDB | `Table(`, `dynamodb.Table` | billingMode, GSI count |
| OpenSearch | `opensearch.Domain`, `Domain(` | instanceType, dataNodes, volumeSize |
| ElastiCache | `CfnCacheCluster`, `elasticache` | nodeType, numCacheNodes |
| S3 | `Bucket(` | bucket count |

### Networking

| Resource | grep Pattern | Fields to Extract |
|----------|-------------|-------------------|
| VPC + NAT | `Vpc(`, `natGateways` | natGateways count, maxAzs |
| ALB | `ApplicationLoadBalancer` | internetFacing, associated services |
| NLB | `NetworkLoadBalancer` | same as above |
| API Gateway | `RestApi`, `HttpApi`, `WebSocketApi` | API type |
| CloudFront | `Distribution` | count |

### Messaging & Integration

| Resource | grep Pattern | Fields to Extract |
|----------|-------------|-------------------|
| SQS | `Queue(` | queue count |
| SNS | `Topic(` | topic count |
| EventBridge | `Rule(`, `EventBus` | rule count |
| Step Functions | `StateMachine` | count |

### Security & Management

| Resource | grep Pattern | Fields to Extract |
|----------|-------------|-------------------|
| Secrets Manager | `Secret(`, `secretsmanager` | secret count |
| KMS | `Key(`, `kms.Key` | key count |
| WAF | `WebAcl`, `CfnWebACL` | count |

## 2.3 Architecture Documentation Search

Search project documentation to supplement information that CDK code may miss:

```
Search paths:
- **/doc/**, **/docs/**
- README.md, ARCHITECTURE.md
- **/pricing*, **/cost*
```

Look for in the documentation:
- Existing pricing/cost estimates (as ground truth reference)
- Services managed outside CDK (e.g., manually created EC2 GPU instances, Bedrock usage, SageMaker endpoints, etc.)
- Services mentioned in architecture descriptions but not found in CDK code

## 2.4 Module Assignment

Automatically infer module names from the directory structure, with no fixed mapping:

- Use the directory name as the default module name (e.g., `modules/auth/` → "Auth")
- If all CDK code is in a single directory, group by Stack name
- If unable to infer, label as "Main"

## 2.5 Confirm with User

Format the discovery results as a table and present to the user:

```
=== Discovered AWS Resources (N total) ===

| # | Module | AWS Service | Configuration | Pricing Basis | Source |
|---|--------|-------------|---------------|---------------|--------|
| 1 | ...    | ECS Fargate | 1 vCPU, 2 GB, 2 tasks | hourly | lib/xxx.ts:42 |
| 2 | ...    | RDS PostgreSQL | db.t4g.medium, Single-AZ | hourly | lib/xxx.ts:18 |
| ...

Minimal-cost services (not individually priced): S3(3), DynamoDB(2), SQS(4), SNS(1), Lambda(5)

Please confirm:
1. Are there any missing services to add manually? (e.g., Bedrock, SageMaker, manually created EC2, etc.)
2. Are there any services to exclude?
3. Are the resource configurations correct?
```

**Minimal-cost classification rules**: The following services typically cost < $5/month under normal usage and are grouped as "minimal cost" without individual pricing:
- S3 (storage < 100 GB)
- DynamoDB PAY_PER_REQUEST (low request volume)
- SQS / SNS (low message volume)
- CloudFront (low traffic)
- Lambda (low invocation count)
- Secrets Manager (small number of secrets)
- API Gateway (marked as ~$1 at low request volume)

Users can promote any "minimal cost" service to individual pricing.

## 2.6 Output JSON Schema

After user confirmation, save to `cost-estimates/.current-analysis.json`:

```json
{
  "projectName": "<from package.json or directory name>",
  "analyzedAt": "2026-03-03T10:00:00Z",
  "cdkPaths": [
    "<discovered CDK directories>"
  ],
  "resources": [
    {
      "module": "<inferred module name>",
      "service": "Amazon ECS Fargate",
      "resourceId": "<unique-id>",
      "required": true,
      "configuration": {
        "cpu": 1024,
        "memoryMiB": 2048,
        "desiredCount": 2,
        "display": "1 vCPU, 2 GB memory, 2 tasks"
      },
      "pricingDimensions": {
        "vcpuHours": 1460,
        "gbHours": 2920
      },
      "sourceFile": "lib/ecs-service.ts",
      "note": ""
    }
  ],
  "minimalCostServices": [
    { "service": "Amazon S3", "count": 3, "module": "App" },
    { "service": "Amazon DynamoDB", "count": 2, "module": "App" }
  ]
}
```

### pricingDimensions Calculation Rules

- **ECS Fargate**: `vcpuHours = (cpu/1024) * desiredCount * 730`, `gbHours = (memoryMiB/1024) * desiredCount * 730`
- **RDS / Aurora**: `instanceHours = instanceCount * 730`
- **OpenSearch**: `instanceHours = dataNodes * 730`
- **ALB / NLB**: `lbHours = 730`, `lcuHours = 730` (estimated at 1 LCU)
- **NAT**: `natHours = natGateways * 730`
- **EC2**: `instanceHours = instanceCount * 730`
- **Minimal-cost services**: No pricingDimensions calculated; placed in `minimalCostServices`
