# Hospital Analyzer - Docker & AWS Deployment Guide

This guide will walk you through containerizing your Streamlit app and deploying it to AWS, even if you're new to Docker and AWS.

## 🚀 Quick Access

**Your Live Application:** https://hospital-reports.tauspan.com

**Key Management Commands:**
```bash
# Check app status
aws ecs describe-services --cluster hospital-analyzer-cluster --services hospital-analyzer-service --region us-east-1

# View logs
aws logs tail /ecs/hospital-analyzer --follow --region us-east-1

# Stop app (save costs)
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 0 --region us-east-1

# Restart app
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 1 --region us-east-1
```

## Prerequisites

Before starting, you'll need:
- A computer with admin/sudo access
- An internet connection
- A credit card for AWS account setup (AWS has a free tier)

## Part 1: Install Docker

### On macOS:
1. Go to https://www.docker.com/products/docker-desktop/
2. Click "Download for Mac"
3. Open the downloaded `.dmg` file
4. Drag Docker to Applications folder
5. Open Docker from Applications
6. Follow the setup wizard
7. Test installation:
   ```bash
   docker --version
   ```

### On Windows:
1. Go to https://www.docker.com/products/docker-desktop/
2. Click "Download for Windows"
3. Run the installer
4. Restart your computer when prompted
5. Open Docker Desktop
6. Test installation in Command Prompt:
   ```bash
   docker --version
   ```

### On Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```
Log out and back in, then test:
```bash
docker --version
```

## Part 2: Test Your App Locally with Docker

1. Open Terminal/Command Prompt and navigate to your project:
   ```bash
   cd /path/to/hospital-normalized-outcomes
   ```

2. Build your Docker container:
   ```bash
   docker build --platform linux/amd64 -t hospital-analyzer .
   ```
   This creates a container image with your app. The `--platform linux/amd64` flag ensures compatibility with AWS Fargate (required for Apple Silicon Macs).

3. Run the container:
   ```bash
   docker run -p 8501:8501 hospital-analyzer
   ```

4. Open your browser and go to: `http://localhost:8501`
   You should see your Streamlit app running!

5. Stop the container: Press `Ctrl+C` in Terminal

### Alternative: Use Docker Compose (Easier)
```bash
docker-compose up
```
This does steps 2-3 automatically. Stop with `Ctrl+C`.

## Part 3: Set Up AWS Account

1. **Create AWS Account:**
   - Go to https://aws.amazon.com/
   - Click "Create an AWS Account"
   - Enter email, password, account name
   - Provide phone number and credit card
   - Choose "Basic Support (Free)"

2. **Install AWS CLI:**
   
   **On macOS:**
   ```bash
   curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
   sudo installer -pkg AWSCLIV2.pkg -target /
   ```
   
   **On Windows:**
   - Download from: https://awscli.amazonaws.com/AWSCLIV2.msi
   - Run the installer
   
   **On Linux:**
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

3. **Configure AWS CLI:**
   ```bash
   aws configure
   ```
   You'll need:
   - **Access Key ID** and **Secret Access Key**: Get these from AWS Console → IAM → Users → Your User → Security credentials → Create access key
   - **Region**: Use `us-east-1` (recommended)
   - **Output format**: Just press Enter (uses default)

## Part 4: Deploy to AWS

### Step 1: Create Required AWS Resources

1. **Create IAM Role for ECS:**
   ```bash
   aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document '{
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "ecs-tasks.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }'
   ```

2. **Attach policy to role:**
   ```bash
   aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
   ```

3. **Create CloudWatch log group:**
   ```bash
   aws logs create-log-group --log-group-name /ecs/hospital-analyzer --region us-east-1
   ```

4. **Create ECS cluster:**
   ```bash
   aws ecs create-cluster --cluster-name hospital-analyzer-cluster --region us-east-1
   ```

### Step 2: Deploy Your App

1. **Update deployment script variables:**
   Edit `deploy-aws.sh` and change these if needed:
   - `AWS_REGION="us-east-1"` (or your preferred region)
   - Other names can stay as default

2. **Run deployment:**
   ```bash
   ./deploy-aws.sh
   ```
   
   This script will:
   - Build your Docker image
   - Create ECR repository
   - Push image to AWS
   - Register task definition
   - Create/update ECS service

### Step 3: Create Load Balancer & Service

1. **Get your VPC and subnet IDs:**
   ```bash
   aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text
   aws ec2 describe-subnets --query 'Subnets[*].SubnetId' --output text
   ```

2. **Create security group:**
   ```bash
   VPC_ID=$(aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text)
   aws ec2 create-security-group --group-name hospital-analyzer-sg --description "Security group for hospital analyzer" --vpc-id $VPC_ID
   ```

3. **Allow inbound traffic:**
   ```bash
   SG_ID=$(aws ec2 describe-security-groups --group-names hospital-analyzer-sg --query 'SecurityGroups[0].GroupId' --output text)
   aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8501 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
   ```

4. **Create ECS service:**
   ```bash
   SUBNET_IDS=$(aws ec2 describe-subnets --query 'Subnets[*].SubnetId' --output text | tr '\t' ',')
   
   aws ecs create-service \
     --cluster hospital-analyzer-cluster \
     --service-name hospital-analyzer-service \
     --task-definition hospital-analyzer \
     --desired-count 1 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
     --region us-east-1
   ```

### Step 4: Get Your App URL

1. **Find your task's public IP:**
   ```bash
   aws ecs list-tasks --cluster hospital-analyzer-cluster --service hospital-analyzer-service --region us-east-1
   ```

2. **Get task ARN and find IP:**
   ```bash
   TASK_ARN=$(aws ecs list-tasks --cluster hospital-analyzer-cluster --service hospital-analyzer-service --query 'taskArns[0]' --output text --region us-east-1)
   aws ecs describe-tasks --cluster hospital-analyzer-cluster --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text --region us-east-1
   ```

3. **Your app will be available at:** `http://[PUBLIC_IP]:8501`

## Part 5: Managing Your Deployment

### Your Deployment Details
- **Application URL:** https://hospital-reports.tauspan.com
- **Load Balancer URL:** hospital-analyzer-alb-302978426.us-east-1.elb.amazonaws.com
- **AWS Region:** us-east-1
- **ECS Cluster:** hospital-analyzer-cluster
- **ECS Service:** hospital-analyzer-service
- **Load Balancer:** hospital-analyzer-alb
- **ECR Repository:** 157892191819.dkr.ecr.us-east-1.amazonaws.com/hospital-analyzer
- **Route 53 Hosted Zone:** hospital-reports.tauspan.com (Z0636628A3JUA8NHSEJ8)
- **SSL Certificate:** arn:aws:acm:us-east-1:157892191819:certificate/e3badbd5-c83e-4bb3-8a87-da2a1a06b2b1

### Daily Management Commands

#### Check Application Status:
```bash
# Check ECS service health
aws ecs describe-services --cluster hospital-analyzer-cluster --services hospital-analyzer-service --region us-east-1

# Check load balancer target health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:us-east-1:157892191819:targetgroup/hospital-analyzer-targets/235d89c82405da99 --region us-east-1

# Check running tasks
aws ecs list-tasks --cluster hospital-analyzer-cluster --service hospital-analyzer-service --region us-east-1
```

#### View Application Logs:
```bash
# View real-time logs
aws logs tail /ecs/hospital-analyzer --follow --region us-east-1

# View recent logs (last hour)
aws logs tail /ecs/hospital-analyzer --since 1h --region us-east-1

# Search for specific errors
aws logs filter-log-events --log-group-name /ecs/hospital-analyzer --filter-pattern "ERROR" --region us-east-1
```

#### Update Your Application:
1. **Make changes to your code**
2. **Rebuild and push the image:**
   ```bash
   docker build --platform linux/amd64 -t hospital-analyzer .
   docker tag hospital-analyzer:latest 157892191819.dkr.ecr.us-east-1.amazonaws.com/hospital-analyzer:latest
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 157892191819.dkr.ecr.us-east-1.amazonaws.com
   docker push 157892191819.dkr.ecr.us-east-1.amazonaws.com/hospital-analyzer:latest
   ```
3. **Force new deployment:**
   ```bash
   aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --force-new-deployment --region us-east-1
   ```

#### Scale Your Application:
```bash
# Scale up to 2 instances
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 2 --region us-east-1

# Scale down to 1 instance
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 1 --region us-east-1

# Stop the app completely (to save costs)
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 0 --region us-east-1
```

#### Restart Your Application:
```bash
# Restart from stopped state
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 1 --region us-east-1

# Force restart of running app
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --force-new-deployment --region us-east-1
```

### Monitoring and Costs

#### Monitor Costs:

**Expected Monthly Costs:**
- **24/7 Operation:** $35-50/month
- **Business Hours Only:** $15-25/month (60% savings)
- **Weekends Off:** $25-35/month (30% savings)

**Cost Breakdown:**
- **ECS Fargate:** $15-25/month (0.25 vCPU, 0.5GB RAM)
- **Application Load Balancer:** $18/month (fixed cost)
- **Route 53 Hosted Zone:** $0.50/month
- **SSL Certificate:** FREE (AWS Certificate Manager)
- **ECR Storage:** ~$1/month
- **CloudWatch Logs:** ~$1-3/month

**Quick Cost Monitoring:**
```bash
# Run cost monitoring script (included in repository)
./monitor-costs.sh

# View current month's costs
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1

# Service-specific costs
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Elastic Container Service","Amazon Elastic Load Balancing"]}}' \
  --region us-east-1
```

#### Set Up Cost Alerts:

**Billing Alerts (Already Configured):**
- **$50 Monthly Alert:** Email notification when bill exceeds $50
- **Budget Alerts:** 80% and 100% of monthly budget notifications
- **Email:** jcromwell@tauspan.com (confirm SNS subscription)

**Manual Setup for Other Users:**
```bash
# Create SNS topic for billing alerts
aws sns create-topic --name billing-alerts --region us-east-1

# Subscribe email to alerts (replace email)
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT:billing-alerts --protocol email --notification-endpoint your-email@domain.com --region us-east-1

# Create billing alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "AWS-Billing-Alert-50USD" \
  --alarm-description "Alert when AWS bill exceeds $50" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=Currency,Value=USD \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:us-east-1:YOUR_ACCOUNT:billing-alerts \
  --region us-east-1

# Create monthly budget
aws budgets create-budget --account-id YOUR_ACCOUNT_ID --budget '{
  "BudgetName": "Hospital-Analyzer-Monthly-Budget",
  "BudgetLimit": {"Amount": "50", "Unit": "USD"},
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}' --notifications-with-subscribers '[{
  "Notification": {
    "NotificationType": "ACTUAL",
    "ComparisonOperator": "GREATER_THAN",
    "Threshold": 80,
    "ThresholdType": "PERCENTAGE"
  },
  "Subscribers": [{"SubscriptionType": "EMAIL", "Address": "your-email@domain.com"}]
}]' --region us-east-1
```

#### Cost Optimization Strategies:

**Immediate Savings:**
```bash
# Stop during off-hours (saves ~60% of ECS costs)
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 0 --region us-east-1

# Restart when needed
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 1 --region us-east-1
```

**Automated Scheduling:**
Add to your system crontab for automatic start/stop:
```bash
# Stop at 10 PM weekdays (saves ~$1-2/day)
0 22 * * 1-5 aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 0 --region us-east-1

# Start at 8 AM weekdays
0 8 * * 1-5 aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 1 --region us-east-1
```

**Resource Right-Sizing:**
- Current: 256 CPU, 512 MB RAM
- Could reduce to: 256 CPU, 256 MB RAM (saves ~25% on ECS costs)
- Monitor CPU/memory usage before downsizing

#### Additional Cost Tips:
- **Stop when not needed:** Scale to 0 during non-business hours
- **Monitor usage:** Check CloudWatch metrics regularly  
- **Load Balancer:** Fixed cost but necessary for HTTPS and reliability
- **Route 53:** Minimal cost ($0.50/month) for professional domain
- **Delete unused resources:** Remove old task definitions, unused ECR images

#### Performance Monitoring:
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=hospital-analyzer-service Name=ClusterName,Value=hospital-analyzer-cluster \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-east-1
```

### Security Management

#### Update Security Groups (if needed):
```bash
# View current security group rules
aws ec2 describe-security-groups --group-ids sg-0f7fb9dd2eeebb016 --region us-east-1

# Add new IP to access (example)
aws ec2 authorize-security-group-ingress \
  --group-id sg-0f7fb9dd2eeebb016 \
  --protocol tcp \
  --port 8501 \
  --cidr YOUR_IP/32 \
  --region us-east-1
```

#### Rotate Access Keys:
1. Generate new AWS access keys in IAM console
2. Update your local AWS CLI configuration:
   ```bash
   aws configure
   ```
3. Test access, then delete old keys

### Backup and Disaster Recovery

#### Backup Your Container Image:
```bash
# Pull and save current image
docker pull 157892191819.dkr.ecr.us-east-1.amazonaws.com/hospital-analyzer:latest
docker save 157892191819.dkr.ecr.us-east-1.amazonaws.com/hospital-analyzer:latest > hospital-analyzer-backup.tar
```

#### Export Configuration:
```bash
# Export task definition
aws ecs describe-task-definition --task-definition hospital-analyzer --region us-east-1 > task-definition-backup.json

# Export service configuration
aws ecs describe-services --cluster hospital-analyzer-cluster --services hospital-analyzer-service --region us-east-1 > service-backup.json
```

### Delete everything (cleanup):
```bash
# Stop the service first
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 0 --region us-east-1
aws ecs delete-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --force --region us-east-1

# Delete load balancer components
aws elbv2 delete-load-balancer --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:157892191819:loadbalancer/app/hospital-analyzer-alb/c49b354691860a83 --region us-east-1
aws elbv2 delete-target-group --target-group-arn arn:aws:elasticloadbalancing:us-east-1:157892191819:targetgroup/hospital-analyzer-targets/235d89c82405da99 --region us-east-1

# Delete SSL certificate (optional - it's free to keep)
aws acm delete-certificate --certificate-arn arn:aws:acm:us-east-1:157892191819:certificate/e3badbd5-c83e-4bb3-8a87-da2a1a06b2b1 --region us-east-1

# Delete Route 53 hosted zone (optional - small monthly cost)
aws route53 delete-hosted-zone --id Z0636628A3JUA8NHSEJ8 --region us-east-1

# Delete security groups
aws ec2 delete-security-group --group-id sg-0c9ee7ca971705a76 --region us-east-1
aws ec2 delete-security-group --group-id sg-0f7fb9dd2eeebb016 --region us-east-1

# Delete other resources
aws ecs delete-cluster --cluster hospital-analyzer-cluster --region us-east-1
aws ecr delete-repository --repository-name hospital-analyzer --force --region us-east-1
aws logs delete-log-group --log-group-name /ecs/hospital-analyzer --region us-east-1
aws iam delete-role --role-name ecsTaskExecutionRole --region us-east-1

# Remember to remove NS records from GoDaddy manually
```

## Troubleshooting

### Common Issues:

1. **Docker not starting:** Make sure Docker Desktop is running
2. **AWS CLI not found:** Restart terminal after installation
3. **Permission denied:** Run `chmod +x deploy-aws.sh`
4. **ECS task failing:** Check logs with the logs command above
5. **Can't access app:** Make sure security group allows port 8501

### Cost Management:
- ECS Fargate charges ~$0.04/hour for small apps
- Stop your service when not needed
- Use AWS Cost Explorer to monitor spending
- Free tier includes 750 hours/month for new accounts

### Getting Help:
- AWS has extensive documentation at docs.aws.amazon.com
- Docker documentation at docs.docker.com
- Check AWS CloudWatch logs for errors

## Part 6: HTTPS/SSL Configuration (Already Implemented)

Your deployment includes a complete HTTPS setup with:

### Current SSL Configuration:
- **Domain:** hospital-reports.tauspan.com
- **SSL Certificate:** AWS Certificate Manager (auto-renewing)
- **DNS Management:** Route 53 hosted zone
- **HTTP Redirect:** Automatic redirect to HTTPS

### SSL Certificate Management:
```bash
# Check certificate status
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:157892191819:certificate/e3badbd5-c83e-4bb3-8a87-da2a1a06b2b1 \
  --region us-east-1

# List all certificates
aws acm list-certificates --region us-east-1
```

### DNS Management (Route 53):
```bash
# View DNS records
aws route53 list-resource-record-sets \
  --hosted-zone-id Z0636628A3JUA8NHSEJ8 \
  --region us-east-1

# Add additional A records (if needed)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z0636628A3JUA8NHSEJ8 \
  --change-batch file://dns-changes.json \
  --region us-east-1
```

### Load Balancer Listeners:
- **Port 80 (HTTP):** Redirects to HTTPS (301 permanent redirect)
- **Port 443 (HTTPS):** Serves application with SSL certificate

### Adding Additional Domains (Future):
To add more subdomains to the same certificate:
```bash
# Request certificate with multiple domains
aws acm request-certificate \
  --domain-name hospital-reports.tauspan.com \
  --subject-alternative-names additional-subdomain.tauspan.com \
  --validation-method DNS \
  --region us-east-1
```