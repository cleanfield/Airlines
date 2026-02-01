
import os
import paramiko
import time

# SSH Configuration
HOSTNAME = '178.128.241.64'
USERNAME = 'flights'
KEY_FILENAME = 'id_ed25519'
SUDO_PASSWORD = 'nog3willy3'

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_path = os.path.abspath(KEY_FILENAME)
    if hasattr(paramiko.Transport, '_preferred_keys'):
        paramiko.Transport._preferred_keys = tuple(k for k in paramiko.Transport._preferred_keys if 'dss' not in k.lower())
    try:
        key = paramiko.Ed25519Key.from_private_key_file(key_path)
    except Exception:
        key = paramiko.RSAKey.from_private_key_file(key_path)
    client.connect(HOSTNAME, username=USERNAME, pkey=key)
    return client

def run_diagnostics(client):
    print("--- DIAGNOSTICS ---")
    
    # 1. Check API response locally on the server
    print("\n[1] Testing API response (curl localhost:5000)...")
    cmd = "curl -s http://127.0.0.1:5000/api/logs/collection?limit=5"
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode())
    print("STDERR:", stderr.read().decode())

    # 2. Check Gunicorn logs for any recent errors
    print("\n[2] Checking recent Gunicorn logs...")
    cmd = f"echo '{SUDO_PASSWORD}' | sudo -S journalctl -u airlines-web -n 50 --no-pager"
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode())

    # 3. Verify Env Var in running process
    print("\n[3] Checking environment variables of running process...")
    # Find pid of gunicorn
    cmd = "pgrep -f gunicorn | head -n 1"
    stdin, stdout, stderr = client.exec_command(cmd)
    pid = stdout.read().decode().strip()
    if pid:
        print(f"PID: {pid}")
        cmd = f"cat /proc/{pid}/environ | tr '\\0' '\\n' | grep SKIP_SSH"
        stdin, stdout, stderr = client.exec_command(cmd)
        print("Env Var:", stdout.read().decode())
    else:
        print("Gunicorn PID not found")

def main():
    try:
        client = get_ssh_client()
        run_diagnostics(client)
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
