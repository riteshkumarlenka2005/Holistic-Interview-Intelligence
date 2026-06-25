# AWS Deployment Guide

## Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Docker installed
- Terraform installed

## Infrastructure Components
- EKS for container orchestration
- RDS PostgreSQL for database
- S3 for media storage
- CloudFront for CDN
- Route53 for DNS

## Deployment Steps

### 1. Setup Infrastructure
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 2. Configure EKS
```bash
aws eks update-kubeconfig --name interview-pro-cluster
```

### 3. Deploy Services
```bash
kubectl apply -f infrastructure/kubernetes/
```

### 4. Configure Domain
Update Route53 with your domain settings.

## Monitoring
- CloudWatch for logs
- X-Ray for tracing
- SNS for alerts
