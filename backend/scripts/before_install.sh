#!/bin/bash
set -e
pip3 uninstall -y -r requirements.txt

# Clean up the destination directory
rm -rf /opt/backend/*