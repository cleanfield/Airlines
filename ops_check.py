
import os
import paramiko
import hashlib
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv('MARIA_SERVER', '178.128.241.64')
USER = os.getenv('MARIA_SSH_USER', 'flights')
KEY_PATH = 'id_ed25519'
PASSWORD = os.getenv('MARIA_SSH_PASSWORD') 

def check_status():
    if not PASSWORD:
        print("Error: MARIA_SSH_PASSWORD not set (inject it via env var)")
        return

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"Connecting to {SERVER} as {USER}...")
    
    connected = False
    
    # Try key first (with passphrase)
    if not connected and os.path.exists(KEY_PATH):
        try:
            key = paramiko.Ed25519Key.from_private_key_file(KEY_PATH, password=PASSWORD)
            client.connect(SERVER, username=USER, pkey=key)
            connected = True
        except Exception:
            pass

    # Try password
    if not connected:
        try:
            client.connect(SERVER, username=USER, password=PASSWORD)
            connected = True
        except Exception as e:
            print(f"Auth failed: {e}")
            return

    try:
        print("\n--- SERVICE STATUS ---")
        for svc in ['nginx', 'airlines-web']:
            stdin, stdout, stderr = client.exec_command(f"systemctl is-active {svc}")
            print(f"{svc}: {stdout.read().decode().strip()}")

        print("\n--- FIREWALL ---")
        stdin, stdout, stderr = client.exec_command(f"echo '{PASSWORD}' | sudo -S ufw status")
        out = stdout.read().decode()
        # Filter out password echo if present
        for line in out.splitlines():
            if PASSWORD not in line:
                print(line)

        print("\n--- CODE VERIFICATION ---")
        stdin, stdout, stderr = client.exec_command("md5sum /opt/airlines/web_api.py")
        remote_out = stdout.read().decode().strip()
        remote_md5 = remote_out.split()[0] if remote_out else "N/A"
        
        with open('web_api.py', 'rb') as f:
            local_md5 = hashlib.md5(f.read()).hexdigest()
            
        print(f"Local MD5:  {local_md5}")
        print(f"Remote MD5: {remote_md5}")
        
        if local_md5 != remote_md5:
            print(">> MISMATCH! Deployment needed.")
        else:
            print(">> Code matches.")
            
    finally:
        client.close()

if __name__ == "__main__":
    check_status()
