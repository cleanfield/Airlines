
import os
import paramiko
import time

# SSH Configuration
HOSTNAME = '178.128.241.64'
USERNAME = 'flights'
KEY_FILENAME = 'id_ed25519'
TARGET_DIR = '/opt/airlines'
SUDO_PASSWORD = 'nog3willy3'

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Load key
    key_path = os.path.abspath(KEY_FILENAME)
    
    # Paramiko workaround 
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

def fix_and_restart(client):
    sftp = client.open_sftp()
    
    # 1. Upload updated web_api.py and mapping
    print("Uploading updated web_api.py and airline_mapping.json...")
    sftp.put('web_api.py', '/home/flights/staging/web_api.py')
    sftp.put('airline_mapping.json', '/home/flights/staging/airline_mapping.json')
    sftp.close()
    
    print("Updating service configuration and restarting...")
    
    # Commands to:
    # 1. Update systemd service to force SKIP_SSH_TUNNEL=true
    # 2. Copy new web_api.py
    # 3. Reload daemon and restart service
    
    service_file = "/etc/systemd/system/airlines-web.service"
    
    # We'll use sed to ensure the environment variable is there
    # It replaces existing or adds if missing (simplified approach: just replace ExecStart line to include it or rely on existing)
    # Actually, simpler: just rewrite the file content essentially or patch it.
    
    # Let's just create a drop-in override or overwrite the file
    service_content = """[Unit]
Description=Airlines Reliability Web Interface
After=network.target

[Service]
Type=notify
User=airlines
Group=airlines
WorkingDirectory=/opt/airlines
Environment="PATH=/opt/airlines/venv/bin"
Environment="SKIP_SSH_TUNNEL=true"
ExecStart=/opt/airlines/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 120 web_api:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # Write service file to a temp local file then upload
    with open('airlines-web.service', 'w', newline='\n') as f:
        f.write(service_content)
        
    client.open_sftp().put('airlines-web.service', '/home/flights/staging/airlines-web.service')
    
    cmds = [
        # Move service file
        f"cp /home/flights/staging/airlines-web.service {service_file}",
        # Move web_api
        f"cp /home/flights/staging/web_api.py {TARGET_DIR}/web_api.py",
        f"chown airlines:airlines {TARGET_DIR}/web_api.py",
        # Move mapping
        f"cp /home/flights/staging/airline_mapping.json {TARGET_DIR}/airline_mapping.json",
        f"chown airlines:airlines {TARGET_DIR}/airline_mapping.json",
        # Reload
        "systemctl daemon-reload",
        "systemctl restart airlines-web"
    ]
    
    full_cmd = " && ".join(cmds)
    final_cmd = f"echo '{SUDO_PASSWORD}' | sudo -S bash -c '{full_cmd}'"
    
    print("Executing system update...")
    stdin, stdout, stderr = client.exec_command(final_cmd)
    
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode())
    err = stderr.read().decode()
    
    if exit_status == 0:
        print("Service updated and restarted successfully!")
        
        # Verify status
        print("Verifying status...")
        stdin, stdout, stderr = client.exec_command(f"echo '{SUDO_PASSWORD}' | sudo -S systemctl status airlines-web")
        print(stdout.read().decode())
        
    else:
        print(f"Failed: {err}")

def main():
    try:
        client = get_ssh_client()
        fix_and_restart(client)
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
