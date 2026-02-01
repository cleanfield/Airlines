#!/bin/bash
# Deployment script for Airlines Flight Tracker on Digital Ocean
# Run this script on your Digital Ocean droplet

set -e  # Exit on error

echo "========================================="
echo "Airlines Flight Tracker - Deployment"
echo "========================================="
echo ""

# Configuration
APP_DIR="/opt/airlines"
APP_USER="airlines"
SERVICE_NAME="airlines-collector"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "Step 1: Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git nginx

echo ""
echo "Step 2: Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$APP_DIR" -m "$APP_USER"
    echo "User $APP_USER created"
else
    echo "User $APP_USER already exists"
fi

echo ""
echo "Step 3: Setting up application directory..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    echo "Updating existing repository..."
    sudo -u "$APP_USER" git pull
else
    echo "Cloning repository..."
    # You'll need to replace this with your actual repository URL
    # For now, we'll copy files manually
    echo "Note: Copy your application files to $APP_DIR"
fi

echo ""
echo "Step 4: Setting up Python virtual environment..."
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"

echo ""
echo "Step 5: Installing Python dependencies..."
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo ""
echo "Step 6: Creating data directories..."
sudo -u "$APP_USER" mkdir -p "$APP_DIR/data/raw"
sudo -u "$APP_USER" mkdir -p "$APP_DIR/data/processed"
sudo -u "$APP_USER" mkdir -p "$APP_DIR/data/reports"

echo ""
echo "Step 7: Setting up environment file..."
if [ ! -f "$APP_DIR/.env" ]; then
    echo "Creating .env file from example..."
    sudo -u "$APP_USER" cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit $APP_DIR/.env with your actual credentials!"
    echo ""
else
    echo ".env file already exists"
fi

echo ""
echo "Step 8: Setting up systemd service..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Airlines Flight Data Collector
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/main.py analyze --days-back 1
Restart=on-failure
RestartSec=300

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "Step 9: Setting up systemd timer for daily collection..."
cat > /etc/systemd/system/${SERVICE_NAME}.timer << EOF
[Unit]
Description=Daily Airlines Flight Data Collection
Requires=${SERVICE_NAME}.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

echo ""
echo "Step 9b: Configuring SSH keys..."
if [ -f "/tmp/id_ed25519" ]; then
    echo "Installing SSH keys..."
    mv /tmp/id_ed25519 "$APP_DIR/"
    if [ -f "/tmp/id_ed25519.pub" ]; then
        mv /tmp/id_ed25519.pub "$APP_DIR/"
    fi
    chown "$APP_USER:$APP_USER" "$APP_DIR/id_ed25519"*
    chmod 600 "$APP_DIR/id_ed25519"
    
    # Update .env to use the Linux path for the key
    if [ -f "$APP_DIR/.env" ]; then
        sed -i 's|MARIA_ID_ED25519=.*|MARIA_ID_ED25519="/opt/airlines/id_ed25519"|g' "$APP_DIR/.env"
        # Also ensure strict mode is off if it causes issues, or adjust other paths if needed
        echo "Updated .env with correct SSH key path"
    fi
fi

echo ""
echo "Step 10: Enabling and starting services..."
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}.timer
systemctl start ${SERVICE_NAME}.timer

echo ""
echo "Step 11: Setting correct permissions..."
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod 600 "$APP_DIR/.env"

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your credentials:"
echo "   sudo nano $APP_DIR/.env"
echo ""
echo "2. Copy your SSH keys to $APP_DIR/"
echo "   - id_ed25519"
echo "   - id_ed25519.pub"
echo ""
echo "3. Test the application:"
echo "   sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/main.py collect --days-back 1"
echo ""
echo "4. Check service status:"
echo "   systemctl status ${SERVICE_NAME}.timer"
echo "   systemctl list-timers ${SERVICE_NAME}.timer"
echo ""
echo "5. View logs:"
echo "   journalctl -u ${SERVICE_NAME}.service -f"
echo ""
echo "6. Manual run:"
echo "   systemctl start ${SERVICE_NAME}.service"
echo ""
echo "========================================="
echo "Optional: Deploy Web Interface"
echo "========================================="
echo ""
echo "To make the website publicly accessible:"
echo "   chmod +x $APP_DIR/deploy_web.sh"
echo "   sudo $APP_DIR/deploy_web.sh"
echo ""
echo "Or with a custom domain:"
echo "   sudo $APP_DIR/deploy_web.sh your-domain.com"
echo ""

