#!/bin/bash

# Install Python dependencies
pip3 install -r /opt/backend/requirements.txt

# Copy Nginx configuration
sudo cp /opt/backend/scripts/nginx/api.neelo.vision.conf /etc/nginx/conf.d/

# Copy systemd service file
sudo cp /opt/backend/scripts/systemd/backend.service /etc/systemd/system/

# Get SSL certificate
sudo certbot --nginx -d api.neelo.vision --non-interactive --agree-tos --email abdallah-jawad@hotmail.com

# Set up automatic renewal
echo "0 0 * * * root /usr/bin/certbot renew --quiet && systemctl reload nginx" | sudo tee /etc/cron.d/certbot-renew

# Reload systemd and start services
sudo systemctl daemon-reload
sudo systemctl enable backend
sudo systemctl start backend
sudo systemctl reload nginx 