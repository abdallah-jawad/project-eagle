#!/bin/bash
set -e
pip uninstall -y -r requirements.txt

# Clean up the destination directory
rm -rf /opt/backend/*