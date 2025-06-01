# Hospital Analyzer - Docker & AWS Deployment Guide

This guide will walk you through containerizing your Streamlit app and deploying it to AWS, even if you're new to Docker and AWS.

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
- **Application URL:** http://hospital-analyzer-alb-302978426.us-east-1.elb.amazonaws.com
- **AWS Region:** us-east-1
- **ECS Cluster:** hospital-analyzer-cluster
- **ECS Service:** hospital-analyzer-service
- **Load Balancer:** hospital-analyzer-alb
- **ECR Repository:** 157892191819.dkr.ecr.us-east-1.amazonaws.com/hospital-analyzer

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
```bash
# View current month's costs for ECS
aws ce get-cost-and-usage \
  --time-period Start=2025-06-01,End=2025-06-30 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1
```

#### Cost Optimization Tips:
- **Stop when not needed:** Scale to 0 during non-business hours
- **Use smaller instance sizes:** Current setup uses 256 CPU / 512 MB memory
- **Monitor usage:** Check CloudWatch metrics regularly
- **Set billing alerts:** Configure AWS billing alerts for cost control

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

# Delete security groups
aws ec2 delete-security-group --group-id sg-0c9ee7ca971705a76 --region us-east-1
aws ec2 delete-security-group --group-id sg-0f7fb9dd2eeebb016 --region us-east-1

# Delete other resources
aws ecs delete-cluster --cluster hospital-analyzer-cluster --region us-east-1
aws ecr delete-repository --repository-name hospital-analyzer --force --region us-east-1
aws logs delete-log-group --log-group-name /ecs/hospital-analyzer --region us-east-1
aws iam delete-role --role-name ecsTaskExecutionRole --region us-east-1
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

## Part 6: Adding HTTPS/SSL (Optional)

### Prerequisites for HTTPS:
- A custom domain name (e.g., myapp.example.com)
- Access to DNS settings for the domain

### Step 1: Request SSL Certificate
```bash
# Request certificate for your domain
aws acm request-certificate \
  --domain-name yourdomain.com \
  --validation-method DNS \
  --region us-east-1

# Note the certificate ARN from the output
```

### Step 2: Validate Certificate
1. Go to AWS Certificate Manager in the console
2. Find your certificate and click "Create record in Route 53" (if using Route 53)
3. Or manually add the CNAME record to your DNS provider
4. Wait for validation to complete (can take 5-30 minutes)

### Step 3: Add HTTPS Listener to Load Balancer
```bash
# Replace CERT_ARN with your certificate ARN
CERT_ARN="arn:aws:acm:us-east-1:YOUR_ACCOUNT:certificate/YOUR_CERT_ID"
ALB_ARN="arn:aws:elasticloadbalancing:us-east-1:157892191819:loadbalancer/app/hospital-analyzer-alb/c49b354691860a83"
TARGET_GROUP_ARN="arn:aws:elasticloadbalancing:us-east-1:157892191819:targetgroup/hospital-analyzer-targets/235d89c82405da99"

aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN \
  --region us-east-1
```

### Step 4: Redirect HTTP to HTTPS (Optional)
```bash
# Get the HTTP listener ARN
HTTP_LISTENER_ARN=$(aws elbv2 describe-listeners --load-balancer-arn $ALB_ARN --query 'Listeners[?Port==`80`].ListenerArn' --output text --region us-east-1)

# Modify HTTP listener to redirect to HTTPS
aws elbv2 modify-listener \
  --listener-arn $HTTP_LISTENER_ARN \
  --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}' \
  --region us-east-1
```

### Step 5: Update DNS
Point your domain's A record to the load balancer:
- **Target:** hospital-analyzer-alb-302978426.us-east-1.elb.amazonaws.com
- **Type:** CNAME or A (with alias if using Route 53)

After completing these steps, your app will be available at:
- **HTTPS:** https://yourdomain.com
- **HTTP:** Redirects to HTTPS