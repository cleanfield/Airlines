from dotenv import load_dotenv
import os
import paramiko

# Load environment variables from .env file
load_dotenv()

ssh_key_path = os.getenv('MARIA_ID_ED25519', '').strip('"')
print(f"SSH Key Path: {ssh_key_path}")
print(f"File exists: {os.path.exists(ssh_key_path)}")

if os.path.exists(ssh_key_path):
    try:
        key = paramiko.Ed25519Key.from_private_key_file(ssh_key_path)
        print("✓ Successfully loaded Ed25519 key")
    except Exception as e:
        print(f"✗ Failed to load key: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
else:
    print("SSH key file not found!")
