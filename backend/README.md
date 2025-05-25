# Backend API Server

This directory contains the backend API server for the Computer Vision project. The API is deployed on a cost-effective EC2 instance using AWS CDK.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials:
```bash
aws configure
```

3. Deploy the stack:
```bash
cdk deploy
```

## Architecture

The backend is deployed on a t4g.nano EC2 instance (ARM-based) to minimize costs. The instance runs:
- FastAPI application
- Uvicorn server
- All necessary dependencies

## API Documentation

Once deployed, you can access:
- API documentation: http://<instance-ip>/api/docs
- ReDoc documentation: http://<instance-ip>/api/redoc
- OpenAPI specification: http://<instance-ip>/api/openapi.json

## Security

The instance is configured with:
- A security group allowing HTTP traffic
- IAM role with minimal required permissions
- SSM access for management 