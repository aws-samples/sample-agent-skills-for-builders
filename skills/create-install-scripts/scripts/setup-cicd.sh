#!/bin/bash
set -e

# ============================================================
# CI/CD Setup Script
# Creates S3 bucket and CodeBuild project for deployment
# ============================================================
#
# Usage:
#   1. Copy this script to your project: scripts/cicd/setup-cicd.sh
#   2. Modify PROJECT_PREFIX below to match your project name
#   3. Run: bash scripts/cicd/setup-cicd.sh
#
# Prerequisites:
#   - AWS CLI configured with appropriate permissions
#   - Permissions to create S3 buckets, IAM roles, and CodeBuild projects
# ============================================================

# Configuration - MODIFY THIS for your project
PROJECT_PREFIX="myproject"  # Change this to your project name

# Derived configuration
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="${PROJECT_PREFIX}-cicd-${ACCOUNT_ID}-${REGION}"
PROJECT_NAME="${PROJECT_PREFIX}-deploy"
ROLE_NAME="${PROJECT_PREFIX}-codebuild-role"

echo "========================================"
echo "CI/CD Setup"
echo "========================================"
echo "Region: ${REGION}"
echo "Account: ${ACCOUNT_ID}"
echo "S3 Bucket: ${BUCKET_NAME}"
echo "CodeBuild Project: ${PROJECT_NAME}"
echo "========================================"

# ============================================================
# 1. Create S3 Bucket
# ============================================================
echo ""
echo "[1/3] Creating S3 bucket..."

if aws s3api head-bucket --bucket "${BUCKET_NAME}" 2>/dev/null; then
    echo "Bucket ${BUCKET_NAME} already exists, skipping..."
else
    aws s3api create-bucket \
        --bucket "${BUCKET_NAME}" \
        --region "${REGION}" \
        $([ "${REGION}" != "us-east-1" ] && echo "--create-bucket-configuration LocationConstraint=${REGION}") \
        >/dev/null

    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "${BUCKET_NAME}" \
        --versioning-configuration Status=Enabled

    echo "Bucket created: ${BUCKET_NAME}"
fi

# ============================================================
# 2. Create IAM Role for CodeBuild
# ============================================================
echo ""
echo "[2/3] Creating IAM role..."

TRUST_POLICY=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "codebuild.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
)

if aws iam get-role --role-name "${ROLE_NAME}" >/dev/null 2>&1; then
    echo "Role ${ROLE_NAME} already exists, skipping..."
else
    aws iam create-role \
        --role-name "${ROLE_NAME}" \
        --assume-role-policy-document "${TRUST_POLICY}" \
        --description "IAM role for ${PROJECT_PREFIX} CodeBuild deployment" \
        >/dev/null

    # Attach AdministratorAccess for CDK deployment
    # WARNING: In production, use a more restrictive policy
    aws iam attach-role-policy \
        --role-name "${ROLE_NAME}" \
        --policy-arn "arn:aws:iam::aws:policy/AdministratorAccess"

    echo "Role created: ${ROLE_NAME}"
    echo "Waiting for role to propagate..."
    sleep 10
fi

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

# ============================================================
# 3. Create CodeBuild Project
# ============================================================
echo ""
echo "[3/3] Creating CodeBuild project..."

if aws codebuild batch-get-projects --names "${PROJECT_NAME}" --query 'projects[0].name' --output text 2>/dev/null | grep -qw "${PROJECT_NAME}"; then
    echo "Project ${PROJECT_NAME} already exists, skipping..."
else
    aws codebuild create-project \
        --name "${PROJECT_NAME}" \
        --description "${PROJECT_PREFIX} CDK Deployment" \
        --source "type=S3,location=${BUCKET_NAME}/source/source.zip" \
        --artifacts "type=NO_ARTIFACTS" \
        --environment "type=LINUX_CONTAINER,computeType=BUILD_GENERAL1_MEDIUM,image=aws/codebuild/standard:7.0,privilegedMode=true" \
        --service-role "${ROLE_ARN}" \
        --timeout-in-minutes 60 \
        --logs-config "cloudWatchLogs={status=ENABLED,groupName=/aws/codebuild/${PROJECT_NAME}}" \
        >/dev/null

    echo "Project created: ${PROJECT_NAME}"
fi

# ============================================================
# 4. Output Configuration
# ============================================================
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Add these variables to your CI/CD settings:"
echo ""
echo "  CICD_BUCKET         = ${BUCKET_NAME}"
echo "  CODEBUILD_PROJECT   = ${PROJECT_NAME}"
echo "  AWS_DEFAULT_REGION  = ${REGION}"
echo ""
echo "========================================"

# Output machine-parseable values (for scripted use)
# These lines are prefixed with "OUTPUT:" for easy parsing
echo ""
echo "OUTPUT:BUCKET_NAME=${BUCKET_NAME}"
echo "OUTPUT:PROJECT_NAME=${PROJECT_NAME}"
echo "OUTPUT:REGION=${REGION}"
echo "OUTPUT:ROLE_ARN=${ROLE_ARN}"
