#!/bin/bash
# Clean up the destination directory
rm -rf /opt/backend/*

# Install system packages
sudo systemctl enable nginx
sudo systemctl start nginx 