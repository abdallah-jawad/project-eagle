#!/bin/bash
set -e

# Clean up the destination directory
rm -rf /opt/backend/*

# Install Python dependencies
pip3 install -r /opt/backend/requirements.txt 