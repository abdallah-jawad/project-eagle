#!/bin/bash
# Setup script for Computer Vision application

set -e

# Application directory is already set up
APP_DIR="/home/ec2-user/computer-vision"

# Set permissions
chown -R ec2-user:ec2-user $APP_DIR
chmod -R 755 $APP_DIR

# Install Python dependencies
pip3 install --user -r $APP_DIR/requirements.txt

# Install systemd service
sudo cp $APP_DIR/computer_vision.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable computer-vision.service
sudo systemctl start computer-vision.service

echo "Computer Vision application installed and started successfully!" 