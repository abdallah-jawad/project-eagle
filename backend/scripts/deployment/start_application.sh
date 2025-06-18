#!/bin/bash
set -e

# Ensure Nginx is running
sudo systemctl start nginx
sudo systemctl status nginx

# Start the backend service
sudo systemctl start backend
sudo systemctl status backend

# Check if services are running
if ! sudo systemctl is-active --quiet nginx; then
    echo "Nginx failed to start"
    exit 1
fi

if ! sudo systemctl is-active --quiet backend; then
    echo "Backend service failed to start"
    exit 1
fi

echo "All services started successfully" 