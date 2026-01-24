# Digital Ocean Deployment Guide

## Prerequisites

1. **Digital Ocean Droplet**
   - Ubuntu 22.04 LTS (recommended)
   - Minimum: 1GB RAM, 1 vCPU
   - Recommended: 2GB RAM, 2 vCPU for better performance

2. **SSH Access**
   - SSH key configured for your droplet
   - Root or sudo access

3. **Required Credentials**
   - Schiphol API credentials (app_id, app_key)
   - MariaDB server details
   - SSH keys for database access

## Quick Deployment

### Step 1: Connect to Your Droplet

```bash
ssh root@your-droplet-ip
```

### Step 2: Upload Application Files

From your local machine:

```bash
# Create a tarball of the application (excluding unnecessary files)
tar -czf airlines.tar.gz \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='data/raw/*' \
  --exclude='data/processed/*' \
  --exclude='data/reports/*' \
  --exclude='.env' \
  -C c:\Projects Airlines

# Upload to droplet
scp airlines.tar.gz root@your-droplet-ip:/tmp/

# Upload SSH keys
scp c:\Projects\Airlines\id_ed25519 root@your-droplet-ip:/tmp/
scp c:\Projects\Airlines\id_ed25519.pub root@your-droplet-ip:/tmp/
```

### Step 3: Extract and Deploy

On the droplet:

```bash
# Create application directory
mkdir -p /opt/airlines
cd /opt/airlines

# Extract files
tar -xzf /tmp/airlines.tar.gz --strip-components=1

# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Step 4: Configure Environment

```bash
# Edit .env file with your credentials
nano /opt/airlines/.env
```

Add your credentials:

```env
# Schiphol API
SCHIPHOL_APP_ID=your_app_id_here
SCHIPHOL_APP_KEY=your_app_key_here

# MariaDB Connection
MARIA_SERVER=your_server_ip
MARIA_SSH_USER=your_ssh_user
MARIA_SSH_PORT=22
MARIA_ID_ED25519=/opt/airlines/id_ed25519
MARIA_ID_ED25519_PUB=/opt/airlines/id_ed25519.pub
MARIA_ID_ED25519_PASSPHRASE=your_passphrase

# Database
MARIA_DB=flights
MARIA_DB_USER=your_db_user
MARIA_DB_PASSWORD=your_db_password
MARIA_DB_PORT=3306
```

### Step 5: Set Up SSH Keys

```bash
# Move SSH keys to application directory
mv /tmp/id_ed25519 /opt/airlines/
mv /tmp/id_ed25519.pub /opt/airlines/

# Set correct permissions
chown airlines:airlines /opt/airlines/id_ed25519*
chmod 600 /opt/airlines/id_ed25519
chmod 644 /opt/airlines/id_ed25519.pub
```

### Step 6: Test the Application

```bash
# Switch to airlines user
sudo -u airlines bash

# Activate virtual environment
source /opt/airlines/venv/bin/activate

# Test data collection
python main.py collect --days-back 1

# Test full analysis
python main.py analyze --days-back 1
```

## Service Management

### Check Service Status

```bash
# Check timer status
systemctl status airlines-collector.timer

# List all timers
systemctl list-timers

# Check service logs
journalctl -u airlines-collector.service -f
```

### Manual Operations

```bash
# Run collection manually
systemctl start airlines-collector.service

# Stop the timer
systemctl stop airlines-collector.timer

# Restart the timer
systemctl restart airlines-collector.timer

# Disable automatic collection
systemctl disable airlines-collector.timer
```

### View Logs

```bash
# Real-time logs
journalctl -u airlines-collector.service -f

# Last 100 lines
journalctl -u airlines-collector.service -n 100

# Logs from today
journalctl -u airlines-collector.service --since today

# Logs with errors only
journalctl -u airlines-collector.service -p err
```

## Scheduled Collection

The deployment sets up automatic daily data collection at 2:00 AM UTC.

### Modify Schedule

Edit the timer file:

```bash
nano /etc/systemd/system/airlines-collector.timer
```

Change the `OnCalendar` line:

```ini
# Every 6 hours
OnCalendar=*-*-* 00,06,12,18:00:00

# Twice daily (2 AM and 2 PM)
OnCalendar=*-*-* 02,14:00:00

# Every hour
OnCalendar=hourly
```

Reload and restart:

```bash
systemctl daemon-reload
systemctl restart airlines-collector.timer
```

## Accessing Reports

### View Reports Locally

```bash
# List reports
ls -lh /opt/airlines/data/reports/

# View text report
cat /opt/airlines/data/reports/reliability_report_*.txt

# Download reports to your local machine
scp root@your-droplet-ip:/opt/airlines/data/reports/*.png ./reports/
```

### Set Up Web Access (Optional)

If you want to access reports via web browser:

```bash
# Install nginx (if not already installed)
apt-get install nginx

# Create nginx configuration
cat > /etc/nginx/sites-available/airlines << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # or your droplet IP

    location /reports/ {
        alias /opt/airlines/data/reports/;
        autoindex on;
        auth_basic "Airlines Reports";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
EOF

# Create password for web access
apt-get install apache2-utils
htpasswd -c /etc/nginx/.htpasswd admin

# Enable site
ln -s /etc/nginx/sites-available/airlines /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Allow HTTP through firewall
ufw allow 'Nginx HTTP'
```

Access reports at: `http://your-droplet-ip/reports/`

## Monitoring

### Set Up Email Alerts (Optional)

Install and configure postfix for email notifications:

```bash
apt-get install postfix mailutils

# Configure postfix (select "Internet Site")
dpkg-reconfigure postfix
```

Create a monitoring script:

```bash
cat > /opt/airlines/monitor.sh << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet airlines-collector.timer; then
    echo "Airlines collector timer is not running!" | mail -s "Alert: Airlines Service Down" your-email@example.com
fi
EOF

chmod +x /opt/airlines/monitor.sh

# Add to crontab
crontab -e
# Add: */15 * * * * /opt/airlines/monitor.sh
```

### Resource Monitoring

```bash
# Check disk usage
df -h /opt/airlines/data/

# Check memory usage
free -h

# Check CPU usage
top -bn1 | grep "Cpu(s)"

# Monitor application resource usage
systemctl status airlines-collector.service
```

## Maintenance

### Update Application

```bash
cd /opt/airlines

# Backup current version
tar -czf /tmp/airlines-backup-$(date +%Y%m%d).tar.gz .

# Pull latest changes (if using git)
sudo -u airlines git pull

# Or upload new version
# scp airlines.tar.gz root@your-droplet-ip:/tmp/
# tar -xzf /tmp/airlines.tar.gz

# Update dependencies
sudo -u airlines /opt/airlines/venv/bin/pip install -r requirements.txt --upgrade

# Restart service
systemctl restart airlines-collector.timer
```

### Clean Old Data

```bash
# Remove raw data older than 30 days
find /opt/airlines/data/raw/ -name "*.json" -mtime +30 -delete

# Remove old reports
find /opt/airlines/data/reports/ -name "*.png" -mtime +90 -delete
```

### Backup Data

```bash
# Create backup script
cat > /opt/airlines/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/airlines"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/airlines-data-$DATE.tar.gz \
  /opt/airlines/data/processed/ \
  /opt/airlines/data/reports/

# Keep only last 30 days of backups
find $BACKUP_DIR -name "airlines-data-*.tar.gz" -mtime +30 -delete
EOF

chmod +x /opt/airlines/backup.sh

# Add to crontab for daily backup
crontab -e
# Add: 0 3 * * * /opt/airlines/backup.sh
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
systemctl status airlines-collector.service

# Check logs
journalctl -u airlines-collector.service -n 50

# Test manually
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/main.py collect --days-back 1
```

### Database Connection Issues

```bash
# Test SSH connection
sudo -u airlines ssh -i /opt/airlines/id_ed25519 user@database-server

# Test database connection
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/test_mariadb_connection.py
```

### API Issues

```bash
# Test API connectivity
curl -H "app_id: YOUR_APP_ID" -H "app_key: YOUR_APP_KEY" \
  "https://api.schiphol.nl/public-flights/flights?flightDirection=D&scheduleDate=$(date +%Y-%m-%d)"
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Find large files
du -h /opt/airlines/data/ | sort -rh | head -20

# Clean old data
find /opt/airlines/data/raw/ -name "*.json" -mtime +7 -delete
```

## Security Best Practices

1. **Firewall Configuration**

   ```bash
   ufw enable
   ufw allow ssh
   ufw allow 'Nginx HTTP'  # Only if using web access
   ```

2. **Keep System Updated**

   ```bash
   apt-get update && apt-get upgrade -y
   ```

3. **Secure SSH Keys**

   ```bash
   chmod 600 /opt/airlines/id_ed25519
   chmod 600 /opt/airlines/.env
   ```

4. **Regular Backups**
   - Set up automated backups
   - Test restore procedures

5. **Monitor Logs**
   - Regularly check application logs
   - Set up alerts for errors

## Performance Optimization

### For Larger Datasets

Edit `/etc/systemd/system/airlines-collector.service`:

```ini
[Service]
# Increase memory limit if needed
MemoryMax=2G

# Adjust nice level for lower priority
Nice=10
```

### Database Optimization

Consider adding indexes to frequently queried columns in your MariaDB database.

## Support

For issues or questions:

- Check logs: `journalctl -u airlines-collector.service`
- Review configuration: `/opt/airlines/.env`
- Test components individually

---

**Deployment completed!** Your Airlines Flight Tracker is now running on Digital Ocean.
