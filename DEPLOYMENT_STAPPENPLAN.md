# 🚀 DEPLOYMENT STAPPENPLAN - Start Hier

## Wat je nodig hebt

1. ✅ Digital Ocean droplet (Ubuntu 22.04)
2. ✅ SSH toegang tot je droplet
3. ✅ Droplet IP-adres
4. ✅ Je credentials (.env bestand)

## 📋 Deployment Checklist

### STAP 1: Verkrijg je Droplet IP-adres

1. Ga naar <https://cloud.digitalocean.com/>
2. Klik op je droplet
3. Kopieer het IP-adres (bijvoorbeeld: 164.92.123.45)

**Mijn droplet IP:** _________________ (noteer hier)

---

### STAP 2: Test SSH Verbinding

Open PowerShell en test de verbinding:

```powershell
ssh root@YOUR_DROPLET_IP
```

Als dit werkt, type `exit` om terug te gaan.

**Status:** ☐ SSH werkt

---

### STAP 3: Upload Applicatie

**Optie A: Automatisch (Aanbevolen)**

```powershell
# In c:\Projects\Airlines
.\deploy_to_do.ps1 -DropletIP YOUR_DROPLET_IP
```

**Optie B: Handmatig**

```powershell
# 1. Maak tarball
tar -czf airlines.tar.gz --exclude='.git' --exclude='venv' --exclude='__pycache__' *

# 2. Upload
scp airlines.tar.gz root@YOUR_DROPLET_IP:/tmp/
scp id_ed25519 root@YOUR_DROPLET_IP:/tmp/
scp id_ed25519.pub root@YOUR_DROPLET_IP:/tmp/

# 3. Connect en extract
ssh root@YOUR_DROPLET_IP
mkdir -p /opt/airlines
cd /opt/airlines
tar -xzf /tmp/airlines.tar.gz
```

**Status:** ☐ Bestanden geüpload

---

### STAP 4: Run Deployment Script

Op je droplet (via SSH):

```bash
cd /opt/airlines
chmod +x deploy.sh
sudo ./deploy.sh
```

Dit installeert:

- Python dependencies
- Data directories
- Systemd service voor data collectie

**Status:** ☐ Basis deployment compleet

---

### STAP 5: Configureer Environment

```bash
sudo nano /opt/airlines/.env
```

Vul in:

```env
# Schiphol API
SCHIPHOL_APP_ID=your_app_id_here
SCHIPHOL_APP_KEY=your_app_key_here

# MariaDB
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

Opslaan: `Ctrl+X`, dan `Y`, dan `Enter`

**Status:** ☐ Environment geconfigureerd

---

### STAP 6: Configureer SSH Keys

```bash
# Verplaats SSH keys
mv /tmp/id_ed25519 /opt/airlines/
mv /tmp/id_ed25519.pub /opt/airlines/

# Set permissions
chown airlines:airlines /opt/airlines/id_ed25519*
chmod 600 /opt/airlines/id_ed25519
chmod 644 /opt/airlines/id_ed25519.pub
```

**Status:** ☐ SSH keys geconfigureerd

---

### STAP 7: Test de Applicatie

```bash
# Test data collectie
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/main.py collect --days-back 1

# Test database connectie
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/test_mariadb_connection.py
```

**Status:** ☐ Applicatie werkt

---

### STAP 8: Deploy Web Interface (Publiek Toegankelijk)

```bash
cd /opt/airlines
chmod +x deploy_web.sh
sudo ./deploy_web.sh
```

Dit installeert:

- Nginx web server
- Gunicorn WSGI server
- Systemd service voor web interface
- Firewall configuratie

**Status:** ☐ Web interface deployed

---

### STAP 9: Verificatie

```bash
# Check services
sudo systemctl status airlines-web.service
sudo systemctl status nginx

# Test API
curl http://localhost:5000/api/health
```

**Status:** ☐ Services draaien

---

### STAP 10: Test in Browser

Open je browser en ga naar:

```
http://YOUR_DROPLET_IP
```

Je zou nu de Airlines Betrouwbaarheid website moeten zien! 🎉

**Status:** ☐ Website werkt

---

## 🔒 OPTIONEEL: SSL/HTTPS Toevoegen

Als je een domain naam hebt:

### 1. DNS Configureren

Bij je domain provider (Namecheap, GoDaddy, etc.):

- Type: A Record
- Host: @ (of subdomain zoals 'airlines')
- Value: YOUR_DROPLET_IP
- TTL: 300

Wacht 5-10 minuten voor DNS propagatie.

### 2. SSL Certificaat Installeren

```bash
# Installeer Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Verkrijg SSL certificaat
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### 3. Test HTTPS

```
https://your-domain.com
```

**Status:** ☐ SSL geconfigureerd

---

## 📊 Service Management

### Data Collectie Service

```bash
# Status
sudo systemctl status airlines-collector.timer

# Logs
sudo journalctl -u airlines-collector.service -f

# Manual run
sudo systemctl start airlines-collector.service
```

### Web Interface Service

```bash
# Status
sudo systemctl status airlines-web.service

# Restart
sudo systemctl restart airlines-web.service

# Logs
sudo journalctl -u airlines-web.service -f
```

### Nginx

```bash
# Status
sudo systemctl status nginx

# Restart
sudo systemctl restart nginx

# Logs
sudo tail -f /var/log/nginx/airlines-access.log
```

---

## 🐛 Troubleshooting

### Website niet bereikbaar?

```bash
# 1. Check firewall
sudo ufw status

# 2. Check services
sudo systemctl status airlines-web.service
sudo systemctl status nginx

# 3. Check logs
sudo journalctl -u airlines-web.service -n 50
sudo tail -f /var/log/nginx/error.log
```

### Database connectie problemen?

```bash
# Test SSH naar database
sudo -u airlines ssh -i /opt/airlines/id_ed25519 USER@DB_SERVER

# Test database connectie
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/test_mariadb_connection.py
```

### 502 Bad Gateway?

```bash
# Restart web service
sudo systemctl restart airlines-web.service

# Check logs
sudo journalctl -u airlines-web.service -f
```

---

## ✅ Deployment Compleet

Als alle stappen zijn afgerond:

**Je website is nu live op:**

- HTTP: `http://YOUR_DROPLET_IP`
- HTTPS: `https://your-domain.com` (als SSL is ingesteld)

**Features:**

- ✅ Real-time airline rankings
- ✅ Auto-refresh elke 5 minuten
- ✅ Responsive design (mobiel, tablet, desktop)
- ✅ Interactieve filters
- ✅ Live statistieken
- ✅ Automatische data collectie (dagelijks om 2:00 AM)

---

## 📞 Hulp Nodig?

**Check documentatie:**

- `WEB_DEPLOYMENT_GUIDE.md` - Complete guide
- `WEB_DEPLOYMENT_QUICK_REFERENCE.md` - Snelle referentie
- `DEPLOYMENT.md` - Algemene deployment guide

**Belangrijke commando's:**

```bash
# Alles herstarten
sudo systemctl restart airlines-web.service
sudo systemctl restart airlines-collector.timer
sudo systemctl restart nginx

# Alle logs bekijken
sudo journalctl -u airlines-web.service -f
sudo journalctl -u airlines-collector.service -f
sudo tail -f /var/log/nginx/error.log
```

---

## 🎉 Gefeliciteerd

Je Airlines Betrouwbaarheid Tracker is nu live en publiek toegankelijk!

**Deel je website:**

- Stuur het IP-adres naar vrienden/collega's
- Voeg toe aan je portfolio
- Gebruik voor travel planning

**Volgende stappen:**

- Monitor de logs regelmatig
- Check data collectie status
- Voeg SSL toe voor productie gebruik
- Overweeg een custom domain naam

---

**Deployment datum:** _________________

**Droplet IP:** _________________

**Domain (optioneel):** _________________

**Status:** ☐ Volledig operationeel
