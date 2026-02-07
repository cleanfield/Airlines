import os
import paramiko
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configuration
DROPLET_IP = os.getenv('OCEAN_IP')
DROPLET_PASSWORD = os.getenv('OCEAN_PASSWORD')

def setup_ssl():
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

        # 1. Install Certbot
        print("Step 1: Installing Certbot and Nginx plugin...")
        stdin, stdout, stderr = client.exec_command("apt-get update && apt-get install -y certbot python3-certbot-nginx")
        
        # Stream output
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end='')
            if stderr.channel.recv_ready():
                print(stderr.channel.recv(1024).decode(), end='')
            time.sleep(0.1)
        
        if stdout.channel.recv_exit_status() != 0:
            print("\nError installing Certbot.")
            return

        print("\nCertbot installed.")

        # 2. Run Certbot
        print("Step 2: Requesting SSL certificates for flightscore.nl and www.flightscore.nl...")
        # using --register-unsafely-without-email to avoid prompt blocking. 
        # In a real scenario, we'd ask for an email.
        certbox_cmd = "certbot --nginx -d flightscore.nl -d www.flightscore.nl --non-interactive --agree-tos --register-unsafely-without-email --redirect"
        
        stdin, stdout, stderr = client.exec_command(certbox_cmd)
        
        # Stream output
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end='')
            if stderr.channel.recv_ready():
                print(stderr.channel.recv(1024).decode(), end='')
            time.sleep(0.1)

        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("\n\nSUCCESS: SSL Certificates installed and Nginx configured!")
            print("Your site should now be accessible via https://flightscore.nl")
        else:
            print(f"\n\nERROR: Certbot failed with exit code {exit_status}.")
        
        client.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    setup_ssl()
