#!/bin/bash
set -e

# Install Python dependencies
pip3 uninstall -y -r /opt/backend/requirements.txt
pip3 install -r /opt/backend/requirements.txt 