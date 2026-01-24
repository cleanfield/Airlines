#!/bin/bash
# Web Interface Deployment Script for Digital Ocean
# Makes the Airlines Reliability website publicly accessible

set -e

echo "========================================="
echo "Airlines Web Interface - Public Deployment"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

APP_DIR="/opt/airlines"
APP_USER="airlines"
DOMAIN="${1:-_}"  # Use provided domain or default to IP

echo "Step 1: Installing web server dependencies..."
apt-get update
apt-get install -y nginx gunicorn python3-pip

echo ""
echo "Step 2: Installing Python web dependencies..."
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install gunicorn flask flask-cors

echo ""
echo "Step 3: Creating Gunicorn systemd service..."
cat > /etc/systemd/system/airlines-web.service << EOF
[Unit]
Description=Airlines Reliability Web Interface
After=network.target

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 120 web_api:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "Step 4: Configuring Nginx..."
cat > /etc/nginx/sites-available/airlines << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Root location - serve web interface
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        
        # CORS headers (if needed)
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type" always;
    }

    # Static files caching
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://127.0.0.1:5000;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;

    # Access and error logs
    access_log /var/log/nginx/airlines-access.log;
    error_log /var/log/nginx/airlines-error.log;
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/airlines /etc/nginx/sites-enabled/

# Remove default site if exists
rm -f /etc/nginx/sites-enabled/default

echo ""
echo "Step 5: Testing Nginx configuration..."
nginx -t

echo ""
echo "Step 6: Configuring firewall..."
ufw --force enable
ufw allow 'Nginx Full'
ufw allow 'OpenSSH'

echo ""
echo "Step 7: Starting services..."
systemctl daemon-reload
systemctl enable airlines-web.service
systemctl start airlines-web.service
systemctl restart nginx

echo ""
echo "Step 8: Checking service status..."
systemctl status airlines-web.service --no-pager -l

echo ""
echo "========================================="
echo "Web Interface Deployment Complete!"
echo "========================================="
echo ""
echo "Your website is now publicly accessible at:"
if [ "$DOMAIN" = "_" ]; then
    IP=$(hostname -I | awk '{print $1}')
    echo "  http://$IP"
else
    echo "  http://$DOMAIN"
fi
echo ""
echo "Service Management:"
echo "  systemctl status airlines-web.service"
echo "  systemctl restart airlines-web.service"
echo "  systemctl stop airlines-web.service"
echo ""
echo "Logs:"
echo "  journalctl -u airlines-web.service -f"
echo "  tail -f /var/log/nginx/airlines-access.log"
echo "  tail -f /var/log/nginx/airlines-error.log"
echo ""
echo "Next steps:"
echo "1. Test the website in your browser"
echo "2. (Optional) Set up SSL with Let's Encrypt:"
echo "   sudo apt-get install certbot python3-certbot-nginx"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
