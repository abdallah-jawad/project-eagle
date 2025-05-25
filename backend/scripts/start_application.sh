#!/bin/bash
set -e

# Kill any existing uvicorn process
pkill -f uvicorn || true

# Start the FastAPI application
cd /opt/backend
nohup uvicorn main:app --host 0.0.0.0 --port 80 >> /var/log/fastapi.log 2>&1 & 