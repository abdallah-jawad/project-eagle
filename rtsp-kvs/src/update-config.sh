#!/bin/bash

# Get the instance metadata token
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Get the IAM role credentials
PAYLOAD=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/kvsCloudGatewayInstanceRole)

# Set the environment variables
export AWS_ACCESS_KEY_ID=$(echo $PAYLOAD | jq -r .AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo $PAYLOAD | jq -r .SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo $PAYLOAD | jq -r .Token)

# Get latest configuration from AppConfig
aws appconfig get-configuration \
  --application computer-vision \
  --environment production \
  --configuration camera-config \
  --client-id $(curl -s http://169.254.169.254/latest/meta-data/instance-id) \
  --output text > /home/ubuntu/streams-config.json

# Restart the streaming service
sudo systemctl restart stream-rtsp-to-kvs.service 