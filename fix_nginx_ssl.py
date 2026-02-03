
import os
import paramiko
import time

# SSH Configuration
HOSTNAME = '178.128.241.64'
USERNAME = 'flights'
KEY_FILENAME = 'id_ed25519'
SUDO_PASSWORD = 'nog3willy3'
DOMAIN = 'alstorphius.com'

NGINX_CONFIG = """server {
    listen 80;
    server_name alstorphius.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Root location - serve web interface
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # CORS headers
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
"""

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_path = os.path.abspath(KEY_FILENAME)
    try:
        key = paramiko.Ed25519Key.from_private_key_file(key_path)
    except Exception:
        key = paramiko.RSAKey.from_private_key_file(key_path)
    client.connect(HOSTNAME, username=USERNAME, pkey=key)
    return client

def run_sudo_command(client, command):
    print(f"Executing: {command}")
    full_cmd = f"echo '{SUDO_PASSWORD}' | sudo -S {command}"
    stdin, stdout, stderr = client.exec_command(full_cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if exit_status != 0:
        print(f"Failed: {err}")
        return False
    return True

def fix_nginx_and_enable_ssl(client):
    print("Updating Nginx config...")
    
    # Write config to a temp file then move it
    sftp = client.open_sftp()
    with sftp.file('nginx_temp', 'w') as f:
        f.write(NGINX_CONFIG)
    sftp.close()
    
    if not run_sudo_command(client, "mv nginx_temp /etc/nginx/sites-available/airlines"): return False
    if not run_sudo_command(client, "ln -sf /etc/nginx/sites-available/airlines /etc/nginx/sites-enabled/"): return False
    if not run_sudo_command(client, "nginx -t"): return False
    if not run_sudo_command(client, "systemctl reload nginx"): return False
    
    print("Re-running Certbot installer...")
    # Since cert is already there (from previous step success), we just need to install it
    # certbot install --cert-name alstorphius.com --nginx
    # But running the full command again is also safe, it will maintain the cert and just reinstall
    cmd = f"certbot --nginx --non-interactive --agree-tos --redirect --no-eff-email -d {DOMAIN} --reinstall"
    return run_sudo_command(client, cmd)

def main():
    try:
        client = get_ssh_client()
        fix_nginx_and_enable_ssl(client)
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
