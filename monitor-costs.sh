#!/bin/bash

# Hospital Analyzer Cost Monitoring Script
echo "=== Hospital Analyzer AWS Cost Monitor ==="
echo "Date: $(date)"
echo

# Get current month costs
echo "📊 Current Month Costs:"
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1 \
  --output table

echo
echo "🔍 ECS Service Status:"
aws ecs describe-services \
  --cluster hospital-analyzer-cluster \
  --services hospital-analyzer-service \
  --query 'services[0].{RunningTasks:runningCount,DesiredTasks:desiredCount,Status:status}' \
  --output table \
  --region us-east-1

echo
echo "📈 Current Month Breakdown:"
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Elastic Container Service","Amazon Elastic Load Balancing","Amazon Route 53","Amazon EC2 Container Registry (ECR)","Amazon CloudWatch"]}}' \
  --region us-east-1 \
  --output table

echo
echo "💡 Cost Optimization Tips:"
echo "- Stop ECS service during off-hours to save ~60% on compute costs"
echo "- Current setup: ~\$35-50/month for 24/7 operation"
echo "- With scheduled downtime: ~\$15-25/month"
echo
echo "Commands to manage costs:"
echo "Stop service: aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 0 --region us-east-1"
echo "Start service: aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 1 --region us-east-1"