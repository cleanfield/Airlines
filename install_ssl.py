
import os
import paramiko
import time
import sys

# SSH Configuration
HOSTNAME = '178.128.241.64'
USERNAME = 'flights'
KEY_FILENAME = 'id_ed25519'
SUDO_PASSWORD = 'nog3willy3'
DOMAIN = 'alstorphius.com'
EMAIL = 'info@alstorphius.com' # Placeholder email

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Load key
    key_path = os.path.abspath(KEY_FILENAME)
    print(f"Loading key from {key_path}")
    
    if hasattr(paramiko.Transport, '_preferred_keys'):
        paramiko.Transport._preferred_keys = tuple(
            k for k in paramiko.Transport._preferred_keys 
            if 'dss' not in k.lower()
        )
        
    try:
        key = paramiko.Ed25519Key.from_private_key_file(key_path)
    except Exception:
        key = paramiko.RSAKey.from_private_key_file(key_path)

    client.connect(HOSTNAME, username=USERNAME, pkey=key)
    return client

def run_sudo_command(client, command, check_output=True):
    """Run a command with sudo"""
    print(f"Executing: {command}")
    full_cmd = f"echo '{SUDO_PASSWORD}' | sudo -S {command}"
    stdin, stdout, stderr = client.exec_command(full_cmd, get_pty=True)
    
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            print(stdout.channel.recv(1024).decode(), end="")
        if stderr.channel.recv_ready():
            print(stderr.channel.recv(1024).decode(), end="")
        time.sleep(0.1)
        
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    
    if exit_status != 0 and check_output:
        print(f"\nCommand failed with status {exit_status}")
        print(f"Error: {err}")
        return False
    
    return True

def install_certbot(client):
    print("\n--- Installing Certbot ---")
    # Update and install dependencies
    if not run_sudo_command(client, "apt-get update"): return False
    if not run_sudo_command(client, "apt-get install -y certbot python3-certbot-nginx"): return False
    return True

def obtain_certificate(client):
    print("\n--- Obtaining SSL Certificate ---")
    # Non-interactive run
    # --nginx: Use the Nginx plugin
    # --agree-tos: Agree to terms
    # --redirect: Force redirect HTTP to HTTPS
    # --no-eff-email: Don't share email with EFF
    # --email: Email for urgent notices
    cmd = f"certbot --nginx --non-interactive --agree-tos --redirect --no-eff-email --email {EMAIL} -d {DOMAIN}"
    return run_sudo_command(client, cmd)

def verify_nginx(client):
    print("\n--- Verifying Nginx Configuration ---")
    return run_sudo_command(client, "nginx -t && systemctl reload nginx")

def main():
    try:
        client = get_ssh_client()
        
        if install_certbot(client):
            if obtain_certificate(client):
                if verify_nginx(client):
                    print("\nSUCCESS: HTTPS enabled for " + DOMAIN)
                else:
                    print("\nWARNING: Certificate obtained but Nginx reload failed")
            else:
                print("\nFAILURE: Could not obtain certificate")
        else:
            print("\nFAILURE: Could not install Certbot")
            
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
