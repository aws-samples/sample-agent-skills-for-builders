# Common Pitfalls

Common issues and solutions when creating CDK install scripts.

## 1. CDK Bootstrap Requires Context Parameters

If CDK app validates context parameters during initialization, `cdk bootstrap` also needs them.

**Symptom:**
```
Error: adminEmail is required when using Cognito authentication
```

**Wrong:**
```bash
pnpm -C packages/cdk exec cdk bootstrap
```

**Correct:**
```bash
pnpm -C packages/cdk exec cdk bootstrap \
  -c stackName=${STACK_NAME} \
  -c authMethod=${AUTH_METHOD} \
  -c adminEmail=${ADMIN_EMAIL} \
  ...
```

**Note:** `cdk bootstrap` is idempotent - safe to run every time before deploy.

## 2. Running CDK in Monorepos

Cannot use `npx cdk` directly in monorepos.

**Wrong:**
```bash
npx cdk deploy
cd packages/cdk && npx cdk deploy
```

**Correct:**
```bash
pnpm -C packages/cdk exec cdk deploy
# Or use script defined in root package.json
pnpm cdk:deploy
```

## 3. AWS CLI v1 vs v2

`aws logs tail --follow` is **AWS CLI v2 only**.

**Symptom:**
```
aws: error: argument operation: Invalid choice
```

**Solution:**
```bash
# Remove v1 if installed via pip
pip uninstall awscli

# Install v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
unzip /tmp/awscliv2.zip -d /tmp
sudo /tmp/aws/install --update

# Verify
aws --version  # Should show aws-cli/2.x.x
```

## 4. ZIP Exclusion Patterns for Monorepos

Root-level patterns don't match subdirectories.

**Wrong - only matches root level:**
```bash
zip -r source.zip . \
  -x ".venv/*" \
  -x "cdk.out/*" \
  -x ".next/*"
```

**Correct - matches all levels:**
```bash
zip -r source.zip . \
  -x ".venv/*" \
  -x "*/.venv/*" \
  -x "cdk.out/*" \
  -x "*/cdk.out/*" \
  -x ".next/*" \
  -x "*/.next/*" \
  -x "node_modules/*" \
  -x "*/node_modules/*" \
  -x "sessions/*" \
  -x "test-data/*" \
  -x "*.zip"
```

## 5. Multi-line Scripts with eval

Cannot use `eval $(cat script.sh)` for multi-line scripts.

**Wrong:**
```bash
eval $(cat $deploy_script)
```

**Correct:**
```bash
bash "$deploy_script"
```

## 6. CodeBuild Log Stream Timing

Log stream isn't immediately available when build starts.

**Solution - wait with retry:**
```bash
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
```

## 7. Parsing JSON with grep vs jq

Using grep for JSON parsing is fragile.

**Fragile:**
```bash
BUILD_ID=$(echo "$BUILD_INFO" | grep -o '"id": "[^"]*"' | head -1 | cut -d'"' -f4)
```

**Robust:**
```bash
BUILD_ID=$(echo "$BUILD_INFO" | jq -r '.build.id')
```

## 8. Self-Signed Certificate Dependencies

Generating self-signed certificates requires `openssl`.

**Check dependency:**
```bash
if ! command -v openssl &> /dev/null; then
    echo "Error: openssl is required for certificate generation"
    exit 1
fi
```

## 9. setup-cicd.sh Output Parsing

Need machine-readable output format for scripting.

**In setup-cicd.sh:**
```bash
# Human-readable output first
echo "Setup Complete!"
echo "  Bucket: ${BUCKET_NAME}"

# Machine-readable output at end (with prefix)
echo "OUTPUT:BUCKET_NAME=${BUCKET_NAME}"
echo "OUTPUT:PROJECT_NAME=${PROJECT_NAME}"
```

**In install.sh:**
```bash
setup_output=$(bash scripts/cicd/setup-cicd.sh 2>&1)

# Hide machine-readable lines from user
echo "$setup_output" | grep -v "^OUTPUT:"

# Parse values
CICD_BUCKET=$(echo "$setup_output" | grep "^OUTPUT:BUCKET_NAME=" | cut -d'=' -f2)
```

## 10. Sensitive Files in Git

Deployment configs contain account IDs, ARNs, and emails.

**Required .gitignore entries:**
```gitignore
# Deployment configs
default_deploy*.sh
default_codebuild_deploy.sh

# Certificate files
*.key
*.crt
*.csr
```

## 11. CDK Bootstrap Not Found Error

**Symptom:**
```
SSM parameter /cdk-bootstrap/hnb659fds/version not found
```

**Cause:** CDK hasn't been bootstrapped in the target account/region.

**Solution:** Always run bootstrap before deploy (it's idempotent):
```bash
pnpm -C packages/cdk exec cdk bootstrap -c ...
pnpm -C packages/cdk exec cdk deploy -c ...
```

## 12. Wrong Parameter Passing Method

CDK supports two ways to pass parameters - using the wrong one will fail silently or with confusing errors.

### Context Parameters (`-c`)

For apps using `node.tryGetContext()`:

```typescript
// CDK code
const stackName = this.node.tryGetContext('stackName');
```

```bash
# Command line
cdk deploy -c stackName=MyStack -c adminEmail=admin@example.com
```

### CloudFormation Parameters (`--parameters`)

For stacks using `CfnParameter`:

```typescript
// CDK code
new CfnParameter(this, 'VpcId', { type: 'String' });
```

```bash
# Command line
cdk deploy --parameters vpcId="vpc-12345"
```

**Always inspect the CDK code first** to determine which method is used:
- Search for `tryGetContext` → use `-c`
- Search for `CfnParameter` → use `--parameters`
