#!/bin/bash
set -e

# Clean up the destination directory
rm -rf /opt/backend/*

# Wait for CodeDeploy to copy the new files
sleep 5

# Install Python dependencies
pip3 install -r /opt/backend/requirements.txt 