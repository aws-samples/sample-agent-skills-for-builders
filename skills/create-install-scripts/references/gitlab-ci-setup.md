# Setup GitLab CI

Configure GitLab CI/CD pipeline for CDK deployment via CodeBuild.

## .gitlab-ci.yml Template

```yaml
default:
  image: public.ecr.aws/sam/build-python3.12:latest-x86_64
  tags:
    - arch:amd64
    - size:large

variables:
  GIT_SUBMODULE_STRATEGY: recursive
  GIT_SUBMODULE_DEPTH: 1
  GIT_SUBMODULE_FORCE_HTTPS: true

stages:
  - deploy

deploy:
  stage: deploy
  environment: $CI_COMMIT_BRANCH
  variables:
    AWS_CREDS_TARGET_ROLE: $AWS_CREDS_TARGET_ROLE
    AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION
    AWS_CONFIG_FILE: $CI_BUILDS_DIR/.awscredentialvendor/config
    AWS_SHARED_CREDENTIALS_FILE: $CI_BUILDS_DIR/.awscredentialvendor/credentials
  script:
    # Install dependencies
    - |
      if command -v dnf &>/dev/null; then
        dnf install -y zip jq -q
      elif command -v yum &>/dev/null; then
        yum install -y zip jq -q
      elif command -v apt-get &>/dev/null; then
        apt-get update && apt-get install -y zip jq
      fi

    # 1. Package source code
    - echo "Packaging source code..."
    - |
      zip -r source.zip . \
        -x ".git/*" \
        -x "node_modules/*" \
        -x "*/node_modules/*" \
        -x "cdk.out/*" \
        -x "*/cdk.out/*" \
        -x "*.pyc" \
        -x "*/__pycache__/*" \
        -x ".venv/*" \
        -x "*/.venv/*" \
        -x ".next/*" \
        -x "*/.next/*" \
        -x "sessions/*" \
        -x "test-data/*" \
        -x "*.zip"
    - echo "Package size:" && ls -lh source.zip

    # 2. Upload to S3
    - echo "Uploading to S3..."
    - aws s3 cp source.zip s3://${CICD_BUCKET}/source/source.zip

    # 3. Trigger CodeBuild
    - |
      echo "Starting CodeBuild..."
      BUILD_INFO=$(aws codebuild start-build \
        --project-name ${CODEBUILD_PROJECT} \
        --environment-variables-override \
          name=DEPLOY_ENV,value=${CI_COMMIT_BRANCH} \
          name=AUTH_METHOD,value=${AUTH_METHOD:-cognito} \
          name=ADMIN_EMAIL,value=${ADMIN_EMAIL:-} \
          name=CUSTOM_DOMAIN,value=${CUSTOM_DOMAIN:-} \
          name=ACM_CERTIFICATE_ARN,value=${ACM_CERTIFICATE_ARN:-} \
          name=OIDC_PROVIDER,value=${OIDC_PROVIDER:-} \
          name=OIDC_CLIENT_ID,value=${OIDC_CLIENT_ID:-})

      BUILD_ID=$(echo $BUILD_INFO | jq -r '.build.id')
      echo "CodeBuild started: $BUILD_ID"

    # 4. Wait for log stream
    - |
      LOG_GROUP="/aws/codebuild/${CODEBUILD_PROJECT}"
      LOG_STREAM=$(echo $BUILD_ID | cut -d':' -f2)

      for i in $(seq 1 30); do
        STREAM_EXISTS=$(aws logs describe-log-streams \
          --log-group-name "$LOG_GROUP" \
          --log-stream-name-prefix "$LOG_STREAM" \
          --query 'logStreams[0].logStreamName' \
          --output text 2>/dev/null || echo "None")

        if [ "$STREAM_EXISTS" != "None" ] && [ -n "$STREAM_EXISTS" ]; then
          echo "Log stream ready!"
          break
        fi
        echo "Waiting for logs... ($i/30)"
        sleep 10
      done

    # 5. Stream logs
    - |
      # Monitor build status in background
      (
        while true; do
          STATUS=$(aws codebuild batch-get-builds --ids $BUILD_ID \
            --query 'builds[0].buildStatus' --output text 2>/dev/null)
          if [ "$STATUS" != "IN_PROGRESS" ]; then
            echo "$STATUS" > /tmp/build_status
            break
          fi
          sleep 10
        done
      ) &
      MONITOR_PID=$!

      # Stream logs (AWS CLI v2)
      aws logs tail "$LOG_GROUP" \
        --log-stream-names "$LOG_STREAM" \
        --follow \
        --format short &
      LOGS_PID=$!

      # Wait for build completion
      while [ ! -f /tmp/build_status ]; do
        sleep 5
      done

      sleep 5
      kill $LOGS_PID 2>/dev/null || true
      kill $MONITOR_PID 2>/dev/null || true

      FINAL_STATUS=$(cat /tmp/build_status)
      if [ "$FINAL_STATUS" = "SUCCEEDED" ]; then
        exit 0
      else
        exit 1
      fi
  only:
    - develop
    - stage
    - main
```

## Required GitLab CI/CD Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `CICD_BUCKET` | S3 bucket for source code | Yes |
| `CODEBUILD_PROJECT` | CodeBuild project name | Yes |
| `AWS_DEFAULT_REGION` | AWS region | Yes |
| `AUTH_METHOD` | `cognito` or `oidc` | Yes |
| `ADMIN_EMAIL` | Admin email (for Cognito) | If Cognito |
| `CUSTOM_DOMAIN` | Custom domain | No |
| `ACM_CERTIFICATE_ARN` | ACM certificate ARN | Yes |
| `OIDC_PROVIDER` | OIDC issuer URL | If OIDC |
| `OIDC_CLIENT_ID` | OIDC client ID | If OIDC |

## Notes

- The SAM build image includes AWS CLI v2 and Python
- `zip` and `jq` need to be installed at runtime
- Log streaming requires AWS CLI v2 (`aws logs tail --follow`)
