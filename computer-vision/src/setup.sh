#!/bin/bash
# Setup script for Computer Vision application

set -e

# Create application directory
APP_DIR="/home/ec2-user/computer-vision"
mkdir -p $APP_DIR

# Copy application files
cp -r /tmp/computer-vision/* $APP_DIR/

# Set permissions
chown -R ec2-user:ec2-user $APP_DIR
chmod -R 755 $APP_DIR

# Install Python dependencies
pip3 install --user logging

# Install systemd service
cp $APP_DIR/computer_vision.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable computer-vision.service
systemctl start computer-vision.service

echo "Computer Vision application installed and started successfully!" 