# Digital Ocean Deployment - Quick Reference

## 🚀 Quick Deploy

### From Windows (PowerShell)

```powershell
.\deploy_to_do.ps1 -DropletIP YOUR_DROPLET_IP
```

### From Windows (CMD)

```cmd
deploy_to_do.bat YOUR_DROPLET_IP
```

### Manual Deploy

```bash
# 1. Package application
tar -czf airlines.tar.gz *.py *.sh *.md requirements.txt .env.example data/

# 2. Upload to droplet
scp airlines.tar.gz root@YOUR_DROPLET_IP:/tmp/
scp id_ed25519* root@YOUR_DROPLET_IP:/tmp/

# 3. Deploy on droplet
ssh root@YOUR_DROPLET_IP
cd /opt/airlines
tar -xzf /tmp/airlines.tar.gz
chmod +x deploy.sh
./deploy.sh
```

## ⚙️ Configuration

### Edit Environment File

```bash
ssh root@YOUR_DROPLET_IP
nano /opt/airlines/.env
```

### Required Variables

```env
SCHIPHOL_APP_ID=your_app_id
SCHIPHOL_APP_KEY=your_app_key
MARIA_SERVER=your_db_server
MARIA_SSH_USER=your_ssh_user
MARIA_ID_ED25519=/opt/airlines/id_ed25519
MARIA_ID_ED25519_PASSPHRASE=your_passphrase
MARIA_DB=flights
MARIA_DB_USER=your_db_user
MARIA_DB_PASSWORD=your_db_password
```

## 🧪 Testing

### Test Data Collection

```bash
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/main.py collect --days-back 1
```

### Test Full Analysis

```bash
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/main.py analyze --days-back 1
```

### Test Database Connection

```bash
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/test_mariadb_connection.py
```

## 📊 Service Management

### Check Status

```bash
systemctl status airlines-collector.timer
systemctl status airlines-collector.service
```

### View Logs

```bash
# Real-time logs
journalctl -u airlines-collector.service -f

# Last 50 lines
journalctl -u airlines-collector.service -n 50

# Today's logs
journalctl -u airlines-collector.service --since today
```

### Manual Operations

```bash
# Run now
systemctl start airlines-collector.service

# Stop timer
systemctl stop airlines-collector.timer

# Restart timer
systemctl restart airlines-collector.timer

# Check next run time
systemctl list-timers airlines-collector.timer
```

## 📁 File Locations

| Item | Path |
|------|------|
| Application | `/opt/airlines/` |
| Environment | `/opt/airlines/.env` |
| SSH Keys | `/opt/airlines/id_ed25519*` |
| Raw Data | `/opt/airlines/data/raw/` |
| Processed Data | `/opt/airlines/data/processed/` |
| Reports | `/opt/airlines/data/reports/` |
| Logs | `journalctl -u airlines-collector.service` |
| Service File | `/etc/systemd/system/airlines-collector.service` |
| Timer File | `/etc/systemd/system/airlines-collector.timer` |

## 🔄 Update Application

```bash
# On your local machine
.\deploy_to_do.ps1 -DropletIP YOUR_DROPLET_IP

# On droplet (if using git)
cd /opt/airlines
sudo -u airlines git pull
sudo -u airlines /opt/airlines/venv/bin/pip install -r requirements.txt --upgrade
systemctl restart airlines-collector.timer
```

## 📥 Download Reports

### Single File

```bash
scp root@YOUR_DROPLET_IP:/opt/airlines/data/reports/reliability_report_*.txt ./
```

### All Reports

```bash
scp -r root@YOUR_DROPLET_IP:/opt/airlines/data/reports/ ./reports/
```

### All Processed Data

```bash
scp -r root@YOUR_DROPLET_IP:/opt/airlines/data/processed/ ./processed/
```

## 🌐 Web Access (Optional)

### Setup

```bash
# Install nginx
apt-get install nginx apache2-utils

# Create password
htpasswd -c /etc/nginx/.htpasswd admin

# Configure nginx
nano /etc/nginx/sites-available/airlines
```

Add:

```nginx
server {
    listen 80;
    server_name YOUR_DROPLET_IP;
    
    location /reports/ {
        alias /opt/airlines/data/reports/;
        autoindex on;
        auth_basic "Airlines Reports";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

Enable:

```bash
ln -s /etc/nginx/sites-available/airlines /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
ufw allow 'Nginx HTTP'
```

Access: `http://YOUR_DROPLET_IP/reports/`

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check status
systemctl status airlines-collector.service

# View errors
journalctl -u airlines-collector.service -n 50 --no-pager

# Test manually
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/main.py collect --days-back 1
```

### Database Connection Failed

```bash
# Test SSH to database
sudo -u airlines ssh -i /opt/airlines/id_ed25519 USER@DB_SERVER

# Check .env file
cat /opt/airlines/.env

# Test connection
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/test_mariadb_connection.py
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Check data directory size
du -sh /opt/airlines/data/*

# Clean old data
find /opt/airlines/data/raw/ -name "*.json" -mtime +7 -delete
```

### Permission Issues

```bash
# Fix ownership
chown -R airlines:airlines /opt/airlines

# Fix permissions
chmod 600 /opt/airlines/.env
chmod 600 /opt/airlines/id_ed25519
chmod 644 /opt/airlines/id_ed25519.pub
```

## 📅 Schedule Customization

Edit timer:

```bash
nano /etc/systemd/system/airlines-collector.timer
```

Common schedules:

```ini
# Every 6 hours
OnCalendar=*-*-* 00,06,12,18:00:00

# Twice daily
OnCalendar=*-*-* 02,14:00:00

# Every hour
OnCalendar=hourly

# Daily at 3 AM
OnCalendar=*-*-* 03:00:00
```

Apply changes:

```bash
systemctl daemon-reload
systemctl restart airlines-collector.timer
```

## 🔒 Security Checklist

- [ ] Firewall enabled (`ufw enable`)
- [ ] SSH key authentication only
- [ ] `.env` file permissions set to 600
- [ ] SSH keys permissions set to 600
- [ ] Regular system updates (`apt-get update && apt-get upgrade`)
- [ ] Nginx basic auth configured (if using web access)
- [ ] Non-root user for application (`airlines`)

## 📞 Common Commands

```bash
# Connect to droplet
ssh root@YOUR_DROPLET_IP

# Switch to airlines user
sudo -u airlines bash

# Activate virtual environment
source /opt/airlines/venv/bin/activate

# Run collection
python main.py collect --days-back 7

# Run analysis
python main.py analyze --days-back 7

# View collection log
python check_collection_log.py

# Exit airlines user
exit

# Disconnect from droplet
exit
```

## 📊 Monitoring

### Check Service Health

```bash
# Is timer active?
systemctl is-active airlines-collector.timer

# When is next run?
systemctl list-timers airlines-collector.timer

# Recent runs
journalctl -u airlines-collector.service --since "1 day ago" | grep -i "error\|success"
```

### Resource Usage

```bash
# Disk space
df -h /opt/airlines

# Memory usage
free -h

# Process info
ps aux | grep python
```

---

**For detailed information, see [DEPLOYMENT.md](DEPLOYMENT.md)**
