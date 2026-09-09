#!/usr/bin/env bash
# ==============================================================================
# JARVIS Sentinel - AWS Bedrock AgentCore Deployment Script
# Deploys the multi-agent container to Amazon ECR, creates the Lambda runtime,
# and configures the Amazon Bedrock Agent with Action Groups.
# ==============================================================================

set -e

REGION="${AWS_DEFAULT_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="jarvis-sentinel-agentcore"
IMAGE_TAG="latest"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}"
LAMBDA_FUNCTION_NAME="JARVIS-Sentinel-AgentCore-Runtime"
AGENT_NAME="JARVIS-Sentinel-SOC"

echo "=== 1. Logging into Amazon ECR ==="
aws ecr get-login-password --region "${REGION}" | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

echo "=== 2. Creating ECR Repository if missing ==="
aws ecr describe-repositories --repository-names "${ECR_REPO}" --region "${REGION}" || \
aws ecr create-repository --repository-name "${ECR_REPO}" --region "${REGION}"

echo "=== 3. Building and Tagging Docker Container ==="
docker build -t "${ECR_REPO}:${IMAGE_TAG}" -f bedrock_agentcore/Dockerfile .
docker tag "${ECR_REPO}:${IMAGE_TAG}" "${ECR_URI}"

echo "=== 4. Pushing Image to Amazon ECR ==="
docker push "${ECR_URI}"

echo "=== 5. Deploying / Updating AWS Lambda Container Function ==="
ROLE_ARN=$(aws iam get-role --role-name "JARVIS-Sentinel-LambdaExecutionRole" --query "Role.Arn" --output text 2>/dev/null || echo "")

if [ -z "${ROLE_ARN}" ]; then
  echo "Notice: Creating default IAM execution role for Lambda..."
  ROLE_ARN=$(aws iam create-role --role-name "JARVIS-Sentinel-LambdaExecutionRole" \
    --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":["lambda.amazonaws.com","bedrock.amazonaws.com"]},"Action":"sts:AssumeRole"}]}' \
    --query "Role.Arn" --output text)
  aws iam attach-role-policy --role-name "JARVIS-Sentinel-LambdaExecutionRole" \
    --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  sleep 10
fi

# Create or update Lambda function
aws lambda get-function --function-name "${LAMBDA_FUNCTION_NAME}" --region "${REGION}" >/dev/null 2>&1 && \
aws lambda update-function-code --function-name "${LAMBDA_FUNCTION_NAME}" --image-uri "${ECR_URI}" --region "${REGION}" || \
aws lambda create-function --function-name "${LAMBDA_FUNCTION_NAME}" \
  --package-type Image \
  --code ImageUri="${ECR_URI}" \
  --role "${ROLE_ARN}" \
  --timeout 300 \
  --memory-size 1024 \
  --region "${REGION}"

echo "=== 6. Bedrock AgentCore Deployment Succeeded ==="
echo "Lambda Function ARN: arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${LAMBDA_FUNCTION_NAME}"
echo "Ready to attach to Bedrock Agent using action_group_schema.yaml"
