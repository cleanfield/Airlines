import os
import paramiko
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

# Configuration
DROPLET_IP = os.getenv('OCEAN_IP')
DROPLET_PASSWORD = os.getenv('OCEAN_PASSWORD')
REMOTE_CONFIG_PATH = "/etc/nginx/sites-available/airlines"

def update_nginx_config():
    if not DROPLET_IP or not DROPLET_PASSWORD:
        print("Error: OCEAN_IP or OCEAN_PASSWORD not found in .env file.")
        return

    print("Loading environment variables...")
    print(f"Connecting to root@{DROPLET_IP}...")

    try:
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(DROPLET_IP, username='root', password=DROPLET_PASSWORD)
        print("Connected successfully.")

        # 1. Read current config
        print(f"Reading current config from {REMOTE_CONFIG_PATH}...")
        stdin, stdout, stderr = client.exec_command(f"cat {REMOTE_CONFIG_PATH}")
        config_content = stdout.read().decode()
        
        if not config_content:
            print("Error: Could not read nginx config file.")
            print(stderr.read().decode())
            return

        # 2. Modify content using regex
        # Default fallback if regex fails
        new_content = config_content
        
        # Regex to find 'server_name' followed by anything until a semicolon
        pattern = r"server_name\s+[^;]+;"
        replacement = "server_name flightscore.nl www.flightscore.nl;"
        
        new_content = re.sub(pattern, replacement, config_content)

        if new_content == config_content:
             print("Warning: Content did not change. Maybe regex didn't match?")
             print(f"Current content snippet: {config_content[:200]}") # Print start of file for debug
        else:
             print("Configuration updated locally.")

        # 3. Write back to file using SFTP
        print("Uploading new configuration...")
        sftp = client.open_sftp()
        with sftp.open(REMOTE_CONFIG_PATH, 'w') as f:
            f.write(new_content)
        sftp.close()

        # 4. Test and Reload
        print("Testing Nginx configuration...")
        stdin, stdout, stderr = client.exec_command("nginx -t")
        test_output = stdout.read().decode() + stderr.read().decode()
        print(test_output)

        if "successful" in test_output:
            print("Reloading Nginx...")
            client.exec_command("systemctl reload nginx")
            print("Nginx reloaded.")
            print("\nSUCCESS: Droplet is now listening on flightscore.nl and www.flightscore.nl")
        else:
            print("ERROR: Nginx configuration test failed. Reverting not implemented, please check manually.")

        client.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_nginx_config()
