#!/bin/bash
# Deployment script for Airlines web fix
# Run with: bash deploy_to_droplet.sh

DROPLET_IP="178.128.241.64"
SSH_USER="root"
PASSWORD="nog3willy3"

echo "========================================="
echo "Deploying Destination Filter Fix"
echo "========================================="
echo ""
echo "Server: $DROPLET_IP"
echo "User: $SSH_USER"
echo ""

# Use sshpass if available, otherwise manual
if command -v sshpass &> /dev/null; then
    echo "Using sshpass for authentication..."
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SSH_USER@$DROPLET_IP << 'ENDSSH'
        echo "Step 1: Navigating to application directory..."
        cd /opt/airlines || exit 1
        
        echo "Step 2: Pulling latest changes from GitHub..."
        git pull origin main
        
        echo "Step 3: Restarting web service..."
        systemctl restart airlines-web.service
        
        echo "Step 4: Checking service status..."
        systemctl status airlines-web.service --no-pager -l
        
        echo ""
        echo "Deployment complete!"
ENDSSH
else
    echo "Please enter password when prompted: $PASSWORD"
    echo ""
    ssh -o StrictHostKeyChecking=no $SSH_USER@$DROPLET_IP << 'ENDSSH'
        echo "Step 1: Navigating to application directory..."
        cd /opt/airlines || exit 1
        
        echo "Step 2: Pulling latest changes from GitHub..."
        git pull origin main
        
        echo "Step 3: Restarting web service..."
        systemctl restart airlines-web.service
        
        echo "Step 4: Checking service status..."
        systemctl status airlines-web.service --no-pager -l
        
        echo ""
        echo "Deployment complete!"
ENDSSH
fi

echo ""
echo "========================================="
echo "Testing Instructions"
echo "========================================="
echo ""
echo "Visit: https://alstorphius.com"
echo ""
echo "1. Select 'Vertrek' (Departures)"
echo "2. Choose Continent, Country, Airport"
echo "3. Verify filtering works"
echo ""
