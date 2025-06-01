# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains a containerized Streamlit web application for analyzing hospital readmission data, deployed on AWS with production-grade infrastructure. The application provides an interactive web interface for selecting hospitals/IDNs, comparing metrics, and generating charts and tables from DRG 329-334 data (major joint replacement procedures) from 2022.

**Live Application**: https://hospital-reports.tauspan.com

## Application Architecture

**Main Application**: `hospital_analyzer_web.py`
- Streamlit-based web interface with Arrow serialization fixes
- Data loading and cleaning functions with pyarrow compatibility
- Interactive hospital/IDN selection
- Chart generation with plotly/matplotlib
- Export functionality
- Production-ready error handling and data type management

**Container Infrastructure**:
- `Dockerfile`: Multi-stage build for AMD64 compatibility
- `docker-compose.yml`: Local development environment
- `requirements_docker.txt`: Container-specific dependencies with pyarrow
- `.dockerignore`: Optimized container builds

**AWS Deployment**:
- ECS Fargate service with Application Load Balancer
- Route 53 DNS management with custom domain
- SSL/TLS certificates via AWS Certificate Manager
- Auto-scaling and health monitoring
- CloudWatch logging integration

**Key Components**:
- Hospital/IDN selection dropdowns
- Comparator group selection (All, Same IDN, Same State)
- Summary statistics generation
- Interactive data tables with Arrow-compatible serialization
- Chart visualization with percentile overlays

## Data Structure

- `Readmission CMI-LOS-DRG 329-334 2022.xlsx`: Dataset with 2,913 hospitals across 678 IDNs
  - Key metrics: Readmission Rate, ALOS (Average Length of Stay), CMI (Case Mix Index)
  - Hospital identifiers: Provider ID, Hospital name, IDN name
  - Geographic data: City/State for regional comparisons
  - Characteristics: Bed counts, discharge volumes, payor mix

## Development Commands

### Local Development
**Installation**: `./install_web.sh` - Sets up virtual environment and dependencies
**Run Application**: `streamlit run hospital_analyzer_web.py` or double-click "Hospital Analyzer Web.command"
**Install Dependencies**: `pip install -r requirements_web.txt`

### Container Development
**Build Container**: `docker build --platform linux/amd64 -t hospital-analyzer .`
**Run Container**: `docker run -p 8501:8501 hospital-analyzer`
**Development Environment**: `docker-compose up`

### Production Deployment
**Deploy to AWS**: See `DEPLOYMENT_GUIDE.md` for complete instructions
**Check Status**: `aws ecs describe-services --cluster hospital-analyzer-cluster --services hospital-analyzer-service --region us-east-1`
**View Logs**: `aws logs tail /ecs/hospital-analyzer --follow --region us-east-1`
**Scale Service**: `aws ecs update-service --cluster hospital-analyzer-cluster --service hospital-analyzer-service --desired-count N --region us-east-1`

## Data Processing Notes

- CMI column requires conversion from object to numeric type
- Missing data is common (ALOS: 1,043 nulls, Readmission Rate: 736 nulls)
- IDN names should be normalized (fill missing with "Independent")
- DRG codes 329-334 are pre-filtered major joint replacement procedures
- **Arrow Compatibility**: All DataFrames use `make_arrow_compatible()` helper function for Streamlit display
- **Data Type Consistency**: Object columns converted to strings, numeric columns validated

## Deployment Architecture

### Production Environment (AWS)
- **ECS Fargate**: Containerized application with auto-scaling
- **Application Load Balancer**: SSL termination and traffic distribution
- **Route 53**: DNS management for custom domain (hospital-reports.tauspan.com)
- **Certificate Manager**: Automatic SSL certificate management and renewal
- **CloudWatch**: Centralized logging and monitoring
- **ECR**: Container image repository

### Local Development
Uses Streamlit for rapid development with Docker containers for production parity. The application supports both local development and cloud deployment workflows.

## Branches

- **main**: Stable version with local development setup
- **containerization**: Docker and AWS deployment infrastructure (current production branch)