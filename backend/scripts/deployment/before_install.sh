#!/bin/bash
# Clean up the destination directory
rm -rf /opt/backend/*

# Install system packages
sudo yum update -y
sudo yum install -y nginx certbot python3-certbot-nginx
sudo systemctl enable nginx
sudo systemctl start nginx 