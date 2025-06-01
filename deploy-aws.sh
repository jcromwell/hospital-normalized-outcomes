#!/bin/bash

# AWS ECS Deployment Script for Hospital Analyzer
# Make sure to configure AWS CLI and update variables below

# Configuration
AWS_REGION="us-east-1"
ECR_REPO_NAME="hospital-analyzer"
ECS_CLUSTER_NAME="hospital-analyzer-cluster"
ECS_SERVICE_NAME="hospital-analyzer-service"
TASK_DEFINITION_NAME="hospital-analyzer"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build and tag Docker image
echo "Building Docker image..."
docker build -t $ECR_REPO_NAME .

# Create ECR repository if it doesn't exist
echo "Creating ECR repository..."
aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION || true

# Get ECR login token
echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag and push image to ECR
echo "Pushing image to ECR..."
docker tag $ECR_REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Update task definition with new image URI
sed -i.bak "s/YOUR_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" aws-ecs-task-definition.json
sed -i.bak "s|YOUR_ECR_REPO_URI|$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME|g" aws-ecs-task-definition.json

# Register new task definition
echo "Registering task definition..."
aws ecs register-task-definition --cli-input-json file://aws-ecs-task-definition.json --region $AWS_REGION

# Update ECS service
echo "Updating ECS service..."
aws ecs update-service --cluster $ECS_CLUSTER_NAME --service $ECS_SERVICE_NAME --task-definition $TASK_DEFINITION_NAME --region $AWS_REGION

echo "Deployment complete!"
echo "Note: Make sure to create ECS cluster and service if they don't exist."