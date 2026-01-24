# Web Deployment Guide - Digital Ocean

## 🌐 Website Publiek Toegankelijk Maken

Deze guide laat zien hoe je de Airlines Betrouwbaarheid website publiek toegankelijk maakt op je Digital Ocean droplet.

## 📋 Wat wordt geïnstalleerd?

### 1. **Nginx** - Web Server

- Reverse proxy voor je Flask applicatie
- Handelt alle HTTP requests af
- SSL/HTTPS ondersteuning
- Static file serving
- Load balancing

### 2. **Gunicorn** - WSGI Server

- Production-ready Python web server
- Meerdere workers voor betere performance
- Automatische restart bij crashes
- Process management

### 3. **Systemd Service**

- Automatisch starten bij boot
- Process monitoring
- Automatic restart bij failures
- Logging

### 4. **Firewall (UFW)**

- Beveiligt je server
- Alleen HTTP/HTTPS en SSH toegestaan

## 🚀 Snelle Installatie

### Optie 1: Automatische Deployment

```bash
# Op je droplet
cd /opt/airlines
chmod +x deploy_web.sh
sudo ./deploy_web.sh
```

Met custom domain:

```bash
sudo ./deploy_web.sh your-domain.com
```

### Optie 2: Handmatige Installatie

Volg de stappen hieronder voor meer controle.

## 📝 Stap-voor-Stap Installatie

### Stap 1: Installeer Nginx

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

### Stap 2: Installeer Gunicorn

```bash
cd /opt/airlines
sudo -u airlines /opt/airlines/venv/bin/pip install gunicorn
```

### Stap 3: Maak Systemd Service

```bash
sudo nano /etc/systemd/system/airlines-web.service
```

Voeg toe:

```ini
[Unit]
Description=Airlines Reliability Web Interface
After=network.target

[Service]
Type=notify
User=airlines
Group=airlines
WorkingDirectory=/opt/airlines
Environment="PATH=/opt/airlines/venv/bin"
ExecStart=/opt/airlines/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 120 web_api:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Stap 4: Configureer Nginx

```bash
sudo nano /etc/nginx/sites-available/airlines
```

Voeg toe:

```nginx
server {
    listen 80;
    server_name your-droplet-ip;  # Of je domain naam

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

Enable de site:

```bash
sudo ln -s /etc/nginx/sites-available/airlines /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Verwijder default site
sudo nginx -t  # Test configuratie
```

### Stap 5: Configureer Firewall

```bash
sudo ufw enable
sudo ufw allow 'Nginx Full'
sudo ufw allow 'OpenSSH'
sudo ufw status
```

### Stap 6: Start Services

```bash
# Start web service
sudo systemctl daemon-reload
sudo systemctl enable airlines-web.service
sudo systemctl start airlines-web.service

# Restart nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status airlines-web.service
sudo systemctl status nginx
```

## ✅ Verificatie

### Test de Website

1. **Lokaal op de server:**

   ```bash
   curl http://localhost:5000
   curl http://localhost:5000/api/health
   ```

2. **Vanaf je computer:**
   - Open browser
   - Ga naar: `http://YOUR_DROPLET_IP`
   - Je zou de Airlines ranking pagina moeten zien!

### Check Logs

```bash
# Web service logs
sudo journalctl -u airlines-web.service -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

## 🔒 SSL/HTTPS Instellen (Aanbevolen)

### Met Let's Encrypt (Gratis SSL)

```bash
# Installeer Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Verkrijg SSL certificaat
sudo certbot --nginx -d your-domain.com

# Auto-renewal is automatisch geconfigureerd
sudo certbot renew --dry-run
```

Na SSL setup is je site toegankelijk via:

- ✅ `https://your-domain.com` (veilig)
- ❌ `http://your-domain.com` (redirect naar HTTPS)

## 🎯 Domain Naam Configureren

### Als je een domain hebt

1. **Bij je domain provider (bijv. Namecheap, GoDaddy):**
   - Ga naar DNS settings
   - Voeg een A record toe:
     - Type: `A`
     - Host: `@` (of `www`)
     - Value: `YOUR_DROPLET_IP`
     - TTL: `300` (5 minuten)

2. **Update Nginx configuratie:**

   ```bash
   sudo nano /etc/nginx/sites-available/airlines
   ```

   Wijzig `server_name`:

   ```nginx
   server_name your-domain.com www.your-domain.com;
   ```

3. **Restart Nginx:**

   ```bash
   sudo systemctl restart nginx
   ```

4. **Installeer SSL:**

   ```bash
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

## 🔧 Service Management

### Belangrijke Commando's

```bash
# Status checken
sudo systemctl status airlines-web.service

# Service herstarten
sudo systemctl restart airlines-web.service

# Service stoppen
sudo systemctl stop airlines-web.service

# Service starten
sudo systemctl start airlines-web.service

# Logs bekijken (real-time)
sudo journalctl -u airlines-web.service -f

# Nginx herstarten
sudo systemctl restart nginx

# Nginx configuratie testen
sudo nginx -t
```

## 📊 Performance Optimalisatie

### Gunicorn Workers Aanpassen

Voor betere performance, pas aantal workers aan:

```bash
sudo nano /etc/systemd/system/airlines-web.service
```

Wijzig:

```ini
ExecStart=/opt/airlines/venv/bin/gunicorn -w 8 -b 127.0.0.1:5000 web_api:app
```

Formule: `workers = (2 x CPU cores) + 1`

Herstart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart airlines-web.service
```

### Nginx Caching

Voeg toe aan nginx config:

```nginx
# Cache voor static files
location ~* \.(css|js|jpg|png|gif|ico|svg)$ {
    expires 1d;
    add_header Cache-Control "public, immutable";
}
```

## 🛡️ Security Best Practices

### 1. Firewall

```bash
# Alleen essentiële poorten open
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Fail2Ban (Bescherming tegen brute force)

```bash
sudo apt-get install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Automatische Updates

```bash
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 4. Rate Limiting in Nginx

Voeg toe aan nginx config:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20;
    proxy_pass http://127.0.0.1:5000;
}
```

## 📈 Monitoring

### Check Website Uptime

```bash
# Simpele health check
curl http://localhost:5000/api/health

# Met output
curl -s http://localhost:5000/api/health | python3 -m json.tool
```

### Monitoring Script

Maak `/opt/airlines/monitor_web.sh`:

```bash
#!/bin/bash
if ! curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "Website is down! Restarting..."
    systemctl restart airlines-web.service
    echo "Website down at $(date)" | mail -s "Airlines Website Alert" your-email@example.com
fi
```

Voeg toe aan crontab:

```bash
crontab -e
# Voeg toe:
*/5 * * * * /opt/airlines/monitor_web.sh
```

## 🔄 Updates Deployen

### Code Updates

```bash
# Op je lokale machine
git push

# Op de droplet
cd /opt/airlines
sudo -u airlines git pull
sudo systemctl restart airlines-web.service
```

### Dependency Updates

```bash
cd /opt/airlines
sudo -u airlines /opt/airlines/venv/bin/pip install -r requirements.txt --upgrade
sudo systemctl restart airlines-web.service
```

## 🐛 Troubleshooting

### Website niet bereikbaar

1. **Check service status:**

   ```bash
   sudo systemctl status airlines-web.service
   ```

2. **Check nginx status:**

   ```bash
   sudo systemctl status nginx
   ```

3. **Check firewall:**

   ```bash
   sudo ufw status
   ```

4. **Check logs:**

   ```bash
   sudo journalctl -u airlines-web.service -n 50
   sudo tail -f /var/log/nginx/error.log
   ```

### 502 Bad Gateway

Dit betekent dat Nginx draait maar de Flask app niet:

```bash
# Check of Flask app draait
sudo systemctl status airlines-web.service

# Herstart de service
sudo systemctl restart airlines-web.service
```

### 500 Internal Server Error

Check de applicatie logs:

```bash
sudo journalctl -u airlines-web.service -n 100
```

### Database Connection Errors

```bash
# Test database connectie
sudo -u airlines /opt/airlines/venv/bin/python /opt/airlines/test_mariadb_connection.py
```

## 📱 Mobile Testing

Test je website op mobiel:

1. Open browser op je telefoon
2. Ga naar `http://YOUR_DROPLET_IP`
3. De responsive design zou perfect moeten werken!

## 🎉 Klaar

Je website is nu publiek toegankelijk!

**Toegang via:**

- HTTP: `http://YOUR_DROPLET_IP`
- HTTPS: `https://your-domain.com` (na SSL setup)

**API Endpoints:**

- Rankings: `http://YOUR_DROPLET_IP/api/rankings`
- Stats: `http://YOUR_DROPLET_IP/api/stats`
- Health: `http://YOUR_DROPLET_IP/api/health`

---

**Hulp nodig?** Check de logs met `sudo journalctl -u airlines-web.service -f`
