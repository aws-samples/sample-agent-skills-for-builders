# Setup CodeBuild

Configure AWS CodeBuild for CDK deployment.

## setup-cicd.sh Script

Copy `scripts/setup-cicd.sh` to your project and modify `PROJECT_NAME`:

```bash
#!/bin/bash
set -e

# Configuration - modify these as needed
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="PROJECT-cicd-${ACCOUNT_ID}-${REGION}"  # Change PROJECT
PROJECT_NAME="PROJECT-deploy"                        # Change PROJECT
ROLE_NAME="PROJECT-codebuild-role"                   # Change PROJECT
```

## buildspec.yml Template

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      nodejs: 20
      python: 3.12
    commands:
      - echo "Installing pnpm..."
      - npm install -g pnpm
      - corepack enable

  pre_build:
    commands:
      - echo "Installing dependencies..."
      - pnpm install --frozen-lockfile
      - echo "Installing Python dependencies..."
      - cd packages/service && pip install -e . && cd ../..

  build:
    commands:
      - echo "Ensuring CDK is bootstrapped..."
      - |
        pnpm -C packages/cdk exec cdk bootstrap \
          -c stackName=${STACK_NAME:-PROJECT} \
          -c authMethod=${AUTH_METHOD:-cognito} \
          -c adminEmail=${ADMIN_EMAIL:-} \
          -c customDomain=${CUSTOM_DOMAIN:-} \
          -c acmCertificateArn=${ACM_CERTIFICATE_ARN:-} \
          -c oidcProvider=${OIDC_PROVIDER:-} \
          -c oidcClientId=${OIDC_CLIENT_ID:-}
      - echo "Deploying stack..."
      - |
        pnpm -C packages/cdk exec cdk deploy ${STACK_NAME:-PROJECT} \
          --require-approval never \
          -c stackName=${STACK_NAME:-PROJECT} \
          -c authMethod=${AUTH_METHOD:-cognito} \
          -c adminEmail=${ADMIN_EMAIL:-} \
          -c customDomain=${CUSTOM_DOMAIN:-} \
          -c acmCertificateArn=${ACM_CERTIFICATE_ARN:-} \
          -c oidcProvider=${OIDC_PROVIDER:-} \
          -c oidcClientId=${OIDC_CLIENT_ID:-}

  post_build:
    commands:
      - echo "Deployment completed at $(date)"
      - |
        if [ $CODEBUILD_BUILD_SUCCEEDING -eq 1 ]; then
          echo "SUCCESS: Deployed successfully"
        else
          echo "FAILED: Deployment failed"
        fi

cache:
  paths:
    - node_modules/**/*
    - packages/*/node_modules/**/*
    - /root/.cache/pip/**/*
```

## CodeBuild Project Configuration

The `setup-cicd.sh` script creates:

### 1. S3 Bucket
- Name: `{project}-cicd-{account}-{region}`
- Versioning enabled
- Used for source code uploads

### 2. IAM Role
- Name: `{project}-codebuild-role`
- Trust policy for CodeBuild service
- **WARNING**: Uses `AdministratorAccess` - restrict for production

### 3. CodeBuild Project
- Name: `{project}-deploy`
- Source: S3 bucket
- Environment: `aws/codebuild/standard:7.0` with privileged mode
- Timeout: 60 minutes
- CloudWatch Logs enabled

## Machine-Parseable Output

The script outputs values for programmatic use:

```bash
echo "OUTPUT:BUCKET_NAME=${BUCKET_NAME}"
echo "OUTPUT:PROJECT_NAME=${PROJECT_NAME}"
echo "OUTPUT:REGION=${REGION}"
echo "OUTPUT:ROLE_ARN=${ROLE_ARN}"
```

Parse in install.sh:

```bash
setup_output=$(bash scripts/cicd/setup-cicd.sh 2>&1)
CICD_BUCKET=$(echo "$setup_output" | grep "^OUTPUT:BUCKET_NAME=" | cut -d'=' -f2)
CODEBUILD_PROJECT=$(echo "$setup_output" | grep "^OUTPUT:PROJECT_NAME=" | cut -d'=' -f2)
```

## Triggering CodeBuild from install.sh

```bash
BUILD_INFO=$(aws codebuild start-build \
    --project-name "${CODEBUILD_PROJECT}" \
    --environment-variables-override \
        "name=STACK_NAME,value=${stackName}" \
        "name=AUTH_METHOD,value=${authMethod}" \
        "name=ADMIN_EMAIL,value=${adminEmail}" \
        ...)

BUILD_ID=$(echo "$BUILD_INFO" | jq -r '.build.id')
```

## Log Streaming

Wait for log stream to be created, then stream:

```bash
LOG_GROUP="/aws/codebuild/${CODEBUILD_PROJECT}"
LOG_STREAM=$(echo "$BUILD_ID" | cut -d':' -f2)

# Wait for log stream
for i in $(seq 1 30); do
    STREAM_EXISTS=$(aws logs describe-log-streams \
        --log-group-name "$LOG_GROUP" \
        --log-stream-name-prefix "$LOG_STREAM" \
        --query 'logStreams[0].logStreamName' \
        --output text 2>/dev/null || echo "None")

    if [ "$STREAM_EXISTS" != "None" ] && [ -n "$STREAM_EXISTS" ]; then
        break
    fi
    sleep 10
done

# Stream logs (AWS CLI v2 required)
aws logs tail "$LOG_GROUP" \
    --log-stream-names "$LOG_STREAM" \
    --follow \
    --format short
```
