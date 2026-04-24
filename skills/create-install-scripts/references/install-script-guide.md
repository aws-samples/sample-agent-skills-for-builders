# Create Install Script

Create an interactive installation script for CDK projects supporting both local and CodeBuild deployment.

## Script Structure

```bash
#!/bin/bash

# 1. Deployment method selection
echo "Deployment Method"
echo "  1. Local deployment (requires Node.js, pnpm, Docker)"
echo "  2. AWS CodeBuild deployment (no local tools required)"

# 2. Check for previous configuration
if [ -f "$deploy_script" ]; then
    # Ask to reuse
fi

# 3. Interactive configuration collection
#    - Stack name
#    - Auth method (Cognito/OIDC)
#    - Domain and certificate
#    - Storage configuration

# 4. Execute deployment
if [ "$useCodeBuild" == "true" ]; then
    # CodeBuild deployment
else
    # Local deployment
fi
```

## Key Configuration Options

### Authentication Methods

```bash
# Cognito mode
authMethod="cognito"
adminEmail="admin@example.com"
additionalIdp=""  # Optional external IdP

# OIDC mode
authMethod="oidc"
oidcProvider="https://cognito-idp.region.amazonaws.com/pool_id"
oidcClientId="client_id"
```

### Self-Signed Certificate Generation

```bash
if [ -z "$customDomain" ]; then
    cert_dir=$(mktemp -d)
    cert_domain="project-selfsigned.local"

    # Generate private key
    openssl genrsa -out "$cert_dir/private.key" 2048 2>/dev/null

    # Generate CSR
    openssl req -new -key "$cert_dir/private.key" -out "$cert_dir/cert.csr" \
        -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=$cert_domain" 2>/dev/null

    # Generate self-signed certificate
    openssl x509 -req -days 365 -in "$cert_dir/cert.csr" \
        -signkey "$cert_dir/private.key" -out "$cert_dir/certificate.crt" 2>/dev/null

    # Upload to ACM
    acmCertificateArn=$(aws acm import-certificate \
        --certificate fileb://"$cert_dir/certificate.crt" \
        --private-key fileb://"$cert_dir/private.key" \
        --query 'CertificateArn' \
        --output text)

    rm -rf "$cert_dir"
fi
```

### Storage Configuration

```bash
# Serverless options (recommended)
useNeptuneServerless="true"
useOpenSearchServerless="true"
useRdsServerless="true"
```

## Local Deployment Script Format

Generated `default_deploy.sh` should be a standalone executable script:

```bash
#!/bin/bash
# Bootstrap CDK (idempotent)
pnpm -C packages/cdk exec cdk bootstrap \
  -c stackName=PROJECT \
  -c authMethod=cognito \
  -c adminEmail=admin@example.com \
  ...

# Deploy
pnpm cdk:deploy PROJECT \
  -c stackName=PROJECT \
  -c authMethod=cognito \
  -c adminEmail=admin@example.com \
  ... \
  --require-approval never
```

## .gitignore Configuration

```gitignore
# Deployment configs (contain sensitive info)
default_deploy*.sh
default_codebuild_deploy.sh

# Certificate files
*.key
*.crt
*.csr
```

## Dependency Checks

Check for required dependencies at script start:

```bash
# Check AWS CLI version
aws_version=$(aws --version 2>&1)
if [[ "$aws_version" == *"aws-cli/1"* ]]; then
    echo "Warning: AWS CLI v1 detected. v2 is recommended for log streaming."
fi

# Check openssl (required for self-signed certs)
if ! command -v openssl &> /dev/null; then
    echo "Error: openssl is required for certificate generation"
    exit 1
fi
```
