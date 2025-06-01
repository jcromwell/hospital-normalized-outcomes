# Hospital Analyzer - Application Update Guide

This guide covers how to update your deployed application on AWS with new features, bug fixes, or data changes.

## 🚀 Quick Update Process

For most updates, you only need one command:

```bash
./deploy-aws.sh
```

**Total Time:** 3-5 minutes from code change to live deployment

## 📋 Step-by-Step Update Process

### Step 1: Make Your Changes Locally

```bash
# Navigate to your project
cd /path/to/hospital-normalized-outcomes

# Make sure you're on the containerization branch
git checkout containerization

# Make your changes (edit files, add features, etc.)
# Example: Edit hospital_analyzer_web.py
```

### Step 2: Test Changes Locally

**Option A: Test with Docker (Recommended)**
```bash
# Build and test container locally
docker build --platform linux/amd64 -t hospital-analyzer .
docker run -p 8501:8501 hospital-analyzer

# Test at http://localhost:8501
```

**Option B: Test with Docker Compose**
```bash
# Quick development testing
docker-compose up

# Test at http://localhost:8501
# Press Ctrl+C to stop
```

**Option C: Test Locally (without Docker)**
```bash
# Traditional local testing
streamlit run hospital_analyzer_web.py

# Test at http://localhost:8501
```

### Step 3: Deploy to AWS

**Automated Deployment (Recommended):**
```bash
# Single command deployment
./deploy-aws.sh
```

**Manual Deployment (if you want control):**
```bash
# 1. Build container for AMD64 (required for AWS)
docker build --platform linux/amd64 -t hospital-analyzer .

# 2. Tag for ECR
docker tag hospital-analyzer:latest 157892191819.dkr.ecr.us-east-1.amazonaws.com/hospital-analyzer:latest

# 3. Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 157892191819.dkr.ecr.us-east-1.amazonaws.com

# 4. Push to ECR
docker push 157892191819.dkr.ecr.us-east-1.amazonaws.com/hospital-analyzer:latest

# 5. Deploy to ECS
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --force-new-deployment --region us-east-1
```

### Step 4: Monitor Deployment

```bash
# Watch deployment progress
aws ecs describe-services --cluster hospital-analyzer-cluster --services hospital-analyzer-service --region us-east-1

# View deployment logs
aws logs tail /ecs/hospital-analyzer --follow --region us-east-1

# Check running tasks
aws ecs list-tasks --cluster hospital-analyzer-cluster --service hospital-analyzer-service --region us-east-1
```

### Step 5: Verify Update

1. **Check the live site:** https://hospital-reports.tauspan.com
2. **Test your changes:** Verify new features work as expected
3. **Monitor for errors:** Check logs for any issues

## 🔄 Deployment Process Details

### What Happens During Deployment:

1. **Container Build** (~30-60 seconds)
   - Docker builds your application with all dependencies
   - Optimized for AWS Fargate (AMD64 platform)

2. **Push to ECR** (~30-60 seconds)
   - Container image uploaded to AWS Elastic Container Registry
   - Tagged with 'latest' for easy reference

3. **ECS Rolling Update** (~2-3 minutes)
   - New container starts alongside the old one
   - Health checks ensure new version is working
   - Load balancer routes traffic to healthy container
   - Old container is terminated automatically

4. **Zero Downtime**
   - Your site stays online during updates
   - Users don't experience interruptions
   - Automatic rollback if health checks fail

### Deployment Status Messages:

```bash
# Deployment in progress
"rolloutState": "IN_PROGRESS"

# Deployment completed successfully
"rolloutState": "COMPLETED" 

# Check running vs desired tasks
"runningCount": 1, "desiredCount": 1
```

## 📝 Common Update Scenarios

### Code Changes (Features, Bug Fixes)

```bash
# 1. Edit your Python files
vim hospital_analyzer_web.py

# 2. Deploy
./deploy-aws.sh

# 3. Test live site
curl -I https://hospital-reports.tauspan.com
```

### Data Updates (New Excel File)

```bash
# 1. Replace data file
cp "New Readmission Data 2025.xlsx" "Readmission CMI-LOS-DRG 329-334 2022.xlsx"

# 2. Deploy (data is included in container)
./deploy-aws.sh

# 3. Verify new data appears in application
```

### Dependency Updates (New Python Packages)

```bash
# 1. Add package to requirements
echo "new-package>=1.0.0" >> requirements_docker.txt

# 2. Update application code to use new package
vim hospital_analyzer_web.py

# 3. Deploy
./deploy-aws.sh
```

### UI/Styling Changes

```bash
# 1. Modify Streamlit components or CSS
vim hospital_analyzer_web.py

# 2. Test locally first
docker run -p 8501:8501 hospital-analyzer

# 3. Deploy
./deploy-aws.sh
```

### Configuration Changes

For infrastructure changes (CPU, memory, environment variables):

```bash
# 1. Edit task definition
vim aws-ecs-task-definition.json

# 2. Register new task definition
aws ecs register-task-definition --cli-input-json file://aws-ecs-task-definition.json --region us-east-1

# 3. Update service to use new task definition
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --task-definition hospital-analyzer --region us-east-1
```

## 🚨 Troubleshooting Updates

### Deployment Fails

```bash
# Check service events for errors
aws ecs describe-services --cluster hospital-analyzer-cluster --services hospital-analyzer-service --query 'services[0].events' --region us-east-1

# Check task failure reasons
aws ecs describe-tasks --cluster hospital-analyzer-cluster --tasks $(aws ecs list-tasks --cluster hospital-analyzer-cluster --service hospital-analyzer-service --query 'taskArns[0]' --output text --region us-east-1) --region us-east-1
```

### Application Not Starting

```bash
# View application logs
aws logs tail /ecs/hospital-analyzer --follow --region us-east-1

# Common issues:
# - Python syntax errors
# - Missing dependencies
# - Data file issues
# - Memory/CPU limits exceeded
```

### Health Check Failures

```bash
# Check target group health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:us-east-1:157892191819:targetgroup/hospital-analyzer-targets/235d89c82405da99 --region us-east-1

# Common causes:
# - Application crash on startup
# - Port 8501 not responding
# - Container taking too long to start
```

## ⏪ Rolling Back Updates

If an update causes issues:

### Quick Rollback

```bash
# Stop problematic deployment
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 0 --region us-east-1

# Start with previous version (ECS keeps previous task definition)
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count 1 --region us-east-1
```

### Rollback to Specific Version

```bash
# List available task definition versions
aws ecs list-task-definitions --family-prefix hospital-analyzer --region us-east-1

# Rollback to specific version (e.g., version 2)
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --task-definition hospital-analyzer:2 --region us-east-1
```

### Emergency: Use Previous Container Image

```bash
# Use previous image from ECR
aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --force-new-deployment --region us-east-1

# Or build from previous git commit
git checkout HEAD~1
./deploy-aws.sh
git checkout containerization
```

## ✅ Update Best Practices

### Before Updating:

1. **Commit your changes:** `git add . && git commit -m "Description of changes"`
2. **Test locally:** Always test with Docker first
3. **Small changes:** Make incremental updates rather than large changes
4. **Backup data:** If changing data files, keep backups

### During Updates:

1. **Monitor deployment:** Watch logs during deployment
2. **Check health:** Verify target group shows healthy
3. **Test immediately:** Check live site after deployment
4. **Document changes:** Update commit messages with what changed

### After Updates:

1. **Verify functionality:** Test all major features
2. **Monitor for 24 hours:** Watch for any delayed issues
3. **Check costs:** Monitor if changes affect resource usage
4. **Update documentation:** Update README or guides if needed

## 📊 Update Monitoring

### Real-Time Monitoring During Updates:

```bash
# Monitor in multiple terminals:

# Terminal 1: Service status
watch -n 10 'aws ecs describe-services --cluster hospital-analyzer-cluster --services hospital-analyzer-service --query "services[0].{Running:runningCount,Desired:desiredCount,Status:status}" --output table --region us-east-1'

# Terminal 2: Application logs  
aws logs tail /ecs/hospital-analyzer --follow --region us-east-1

# Terminal 3: Health checks
watch -n 30 'aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:us-east-1:157892191819:targetgroup/hospital-analyzer-targets/235d89c82405da99 --query "TargetHealthDescriptions[0].TargetHealth.State" --output text --region us-east-1'
```

### Post-Update Verification:

```bash
# Check application response
curl -I https://hospital-reports.tauspan.com

# Verify specific functionality (example)
curl -s https://hospital-reports.tauspan.com | grep -i "hospital analyzer"

# Monitor performance
./monitor-costs.sh
```

## 🔄 Automated Update Workflow (Advanced)

For frequent updates, consider setting up automation:

### Git Hook Deployment:

```bash
# Create post-commit hook
cat << 'EOF' > .git/hooks/post-commit
#!/bin/bash
if [[ $(git branch --show-current) == "containerization" ]]; then
    echo "Deploying to AWS..."
    ./deploy-aws.sh
fi
EOF

chmod +x .git/hooks/post-commit
```

### Scheduled Updates:

```bash
# Cron job for automatic deployments (if code changes)
# Add to crontab: crontab -e
0 2 * * * cd /path/to/hospital-normalized-outcomes && git pull && ./deploy-aws.sh
```

## 📞 Getting Help

If you encounter issues during updates:

1. **Check logs:** `aws logs tail /ecs/hospital-analyzer --follow --region us-east-1`
2. **Review service events:** Service events show deployment status
3. **Test locally:** Reproduce issues in local Docker container
4. **Rollback if needed:** Use rollback procedures above
5. **Check documentation:** Review DEPLOYMENT_GUIDE.md for additional troubleshooting

## 📋 Update Checklist

- [ ] Code changes committed to git
- [ ] Tested locally with Docker
- [ ] Ran `./deploy-aws.sh`
- [ ] Monitored deployment progress
- [ ] Verified live site functionality
- [ ] Checked application logs for errors
- [ ] Updated documentation if needed
- [ ] Monitored costs if infrastructure changed

Your application update process is designed for reliability and ease of use. Most updates can be deployed in under 5 minutes with minimal risk! 🚀