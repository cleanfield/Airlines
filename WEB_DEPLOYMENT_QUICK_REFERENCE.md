# Web Deployment - Quick Reference

## 🚀 Snelle Installatie

### Automatisch (Aanbevolen)

```bash
# Op je Digital Ocean droplet
cd /opt/airlines
chmod +x deploy_web.sh
sudo ./deploy_web.sh
```

Met domain:

```bash
sudo ./deploy_web.sh your-domain.com
```

## 📦 Wat wordt geïnstalleerd?

| Component | Functie |
|-----------|---------|
| **Nginx** | Web server / Reverse proxy |
| **Gunicorn** | Production WSGI server |
| **Systemd Service** | Auto-start & monitoring |
| **UFW Firewall** | Security |

## ✅ Verificatie

```bash
# Check services
sudo systemctl status airlines-web.service
sudo systemctl status nginx

# Test website
curl http://localhost:5000/api/health

# Check firewall
sudo ufw status
```

## 🌐 Toegang

**Zonder domain:**

```
http://YOUR_DROPLET_IP
```

**Met domain:**

```
http://your-domain.com
```

## 🔒 SSL Instellen (HTTPS)

```bash
# Installeer Certbot
sudo apt-get install certbot python3-certbot-nginx

# Verkrijg SSL certificaat
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

Na SSL:

```
https://your-domain.com  ✅ Veilig!
```

## 🔧 Belangrijke Commando's

### Service Management

```bash
# Restart web service
sudo systemctl restart airlines-web.service

# Stop web service
sudo systemctl stop airlines-web.service

# Start web service
sudo systemctl start airlines-web.service

# Status checken
sudo systemctl status airlines-web.service
```

### Nginx

```bash
# Restart nginx
sudo systemctl restart nginx

# Test configuratie
sudo nginx -t

# Reload configuratie
sudo systemctl reload nginx
```

### Logs

```bash
# Web service logs (real-time)
sudo journalctl -u airlines-web.service -f

# Nginx access logs
sudo tail -f /var/log/nginx/airlines-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/airlines-error.log
```

## 🎯 Domain Configureren

### 1. DNS Instellen

Bij je domain provider:

- **Type**: A Record
- **Host**: @ (of www)
- **Value**: YOUR_DROPLET_IP
- **TTL**: 300

### 2. Nginx Updaten

```bash
sudo nano /etc/nginx/sites-available/airlines
```

Wijzig:

```nginx
server_name your-domain.com www.your-domain.com;
```

### 3. Restart

```bash
sudo systemctl restart nginx
```

### 4. SSL Toevoegen

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🐛 Troubleshooting

### Website niet bereikbaar

```bash
# 1. Check service
sudo systemctl status airlines-web.service

# 2. Check nginx
sudo systemctl status nginx

# 3. Check firewall
sudo ufw status

# 4. Check logs
sudo journalctl -u airlines-web.service -n 50
```

### 502 Bad Gateway

```bash
# Restart web service
sudo systemctl restart airlines-web.service

# Check logs
sudo journalctl -u airlines-web.service -f
```

### Port Already in Use

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 PID
```

## 📊 Performance

### Meer Workers

```bash
sudo nano /etc/systemd/system/airlines-web.service
```

Wijzig:

```ini
ExecStart=/opt/airlines/venv/bin/gunicorn -w 8 -b 127.0.0.1:5000 web_api:app
```

Restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart airlines-web.service
```

### Nginx Caching

Voeg toe aan nginx config:

```nginx
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1d;
    add_header Cache-Control "public, immutable";
}
```

## 🔄 Updates Deployen

```bash
# Pull nieuwe code
cd /opt/airlines
sudo -u airlines git pull

# Restart service
sudo systemctl restart airlines-web.service
```

## 📁 Belangrijke Bestanden

| Bestand | Locatie |
|---------|---------|
| Nginx config | `/etc/nginx/sites-available/airlines` |
| Systemd service | `/etc/systemd/system/airlines-web.service` |
| Access logs | `/var/log/nginx/airlines-access.log` |
| Error logs | `/var/log/nginx/airlines-error.log` |
| App directory | `/opt/airlines` |

## 🛡️ Security Checklist

- [ ] Firewall enabled (`sudo ufw enable`)
- [ ] Only HTTP/HTTPS and SSH open
- [ ] SSL certificate installed
- [ ] Auto-updates configured
- [ ] Fail2ban installed (optional)
- [ ] Rate limiting configured

## 📞 Hulp Nodig?

**Check logs:**

```bash
sudo journalctl -u airlines-web.service -f
sudo tail -f /var/log/nginx/error.log
```

**Test API:**

```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/rankings
```

**Restart alles:**

```bash
sudo systemctl restart airlines-web.service
sudo systemctl restart nginx
```

---

**Voor volledige documentatie:** Zie `WEB_DEPLOYMENT_GUIDE.md`
