# Using WSL Ubuntu for MariaDB Connection

This guide explains how to use WSL (Windows Subsystem for Linux) Ubuntu instead of Windows for connecting to MariaDB.

## Why Use WSL Ubuntu?

✅ **Better SSH support** - Native SSH client and libraries  
✅ **No DSSKey issues** - Linux handles SSH keys more reliably  
✅ **Faster performance** - Native Linux tools are optimized  
✅ **Better compatibility** - Most Python packages are designed for Linux  
✅ **Easier debugging** - Better error messages and logging  

## Prerequisites

### 1. Install WSL Ubuntu

If you don't have WSL installed:

```powershell
# In PowerShell (as Administrator)
wsl --install -d Ubuntu
```

Or install from Microsoft Store:

- Open Microsoft Store
- Search for "Ubuntu"
- Install "Ubuntu" or "Ubuntu 22.04 LTS"

### 2. Verify WSL Installation

```powershell
# Check WSL version
wsl --list --verbose

# Should show Ubuntu running WSL 2
```

## Setup Steps

### Step 1: Access Your Project in WSL

```bash
# Open WSL Ubuntu terminal
wsl

# Navigate to your Windows project folder
cd /mnt/c/Projects/Airlines

# Verify you're in the right place
ls -la
```

### Step 2: Install Python and Dependencies

```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Verify installation
python3 --version
pip3 --version
```

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

### Step 4: Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Or install individually
pip install pymysql sshtunnel paramiko cryptography pandas python-dotenv
```

### Step 5: Copy SSH Keys

Your SSH keys need to be accessible in WSL with proper permissions:

```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh

# Copy SSH key from Windows to WSL
cp /mnt/c/Projects/Airlines/id_ed25519 ~/.ssh/
cp /mnt/c/Projects/Airlines/id_ed25519.pub ~/.ssh/

# Set correct permissions (IMPORTANT!)
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# Verify permissions
ls -la ~/.ssh/
```

### Step 6: Update .env File for WSL

Create a WSL-specific `.env` file or update the existing one:

```bash
# Edit .env file
nano .env
```

Update the SSH key path to use the Linux path:

```env
# Schiphol API Credentials
SCHIPHOL_APP_ID=8a1d0f4c
SCHIPHOL_APP_KEY=288f3b5bf862f61e73aaea3ca936612e

# SSH Connection
MARIA_SERVER=<server_ip>
MARIA_SSH_USER=flights
MARIA_ID_ED25519=/home/YOUR_USERNAME/.ssh/id_ed25519
MARIA_ID_ED25519_PUB=/home/YOUR_USERNAME/.ssh/id_ed25519.pub

# Database Connection
MARIA_DB=flights
MARIA_DB_USER=flights
MARIA_DB_PASSWORD=<password>
```

**Note:** Replace `YOUR_USERNAME` with your actual WSL username (run `whoami` to find it)

Or use environment variable:

```env
MARIA_ID_ED25519=$HOME/.ssh/id_ed25519
MARIA_ID_ED25519_PUB=$HOME/.ssh/id_ed25519.pub
```

### Step 7: Test SSH Connection

Before testing the database, verify SSH works:

```bash
# Test SSH connection
ssh -i ~/.ssh/id_ed25519 <ssh_user>@<server_ip>

# If successful, you should connect to the server
# Type 'exit' to disconnect
```

If you get "Host key verification failed":

```bash
# Add server to known hosts
ssh-keyscan <server_ip> >> ~/.ssh/known_hosts
```

### Step 8: Test Database Connection

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Test the connection
python3 database.py
```

Expected output:

```
=== Database Connection Test ===

Establishing SSH tunnel to <server_ip>...
Loading SSH key from: /home/username/.ssh/id_ed25519
✓ Loaded Ed25519 key
SSH tunnel established on local port XXXXX
Connecting to MariaDB database 'flights'...
Database connection established successfully!

Creating tables...
Database tables created/verified successfully

Database test completed successfully!
```

## Using the Database in WSL

### Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run Python scripts
python3 database.py
python3 test_mariadb_connection.py
python3 mariadb_connection_example.py

# Run your main application
python3 main.py analyze --days-back 7
```

### Interactive Python

```bash
# Start Python interactive shell
python3

# In Python:
>>> from database import DatabaseManager
>>> with DatabaseManager() as db:
...     with db.connection.cursor() as cursor:
...         cursor.execute("SELECT COUNT(*) as count FROM flights")
...         print(cursor.fetchone())
...
```

## File Access Between Windows and WSL

### Access Windows Files from WSL

```bash
# Windows C: drive
cd /mnt/c/

# Your project
cd /mnt/c/Projects/Airlines

# Edit files with nano
nano database.py

# Or use VS Code
code .
```

### Access WSL Files from Windows

In Windows File Explorer, navigate to:

```
\\wsl$\Ubuntu\home\YOUR_USERNAME\
```

Or from command line:

```powershell
explorer.exe \\wsl$\Ubuntu\home\YOUR_USERNAME\
```

## VS Code Integration

### Install VS Code WSL Extension

1. Open VS Code
2. Install "WSL" extension by Microsoft
3. Click the green icon in bottom-left corner
4. Select "Connect to WSL"
5. Open your project folder

### Open Project in WSL

```bash
# From WSL terminal in your project directory
code .
```

This opens VS Code connected to WSL, giving you:

- Linux terminal in VS Code
- Python running in WSL
- Full IntelliSense support
- Integrated debugging

## Advantages of WSL for This Project

### 1. Better SSH Handling

```bash
# No DSSKey warnings
# Native SSH agent support
# Better key management
```

### 2. Native Linux Tools

```bash
# Use standard Linux commands
grep, sed, awk, etc.

# Better shell scripting
bash scripts work natively
```

### 3. Performance

```bash
# Faster I/O for many operations
# Better process management
# Native networking stack
```

## Common WSL Commands

### Managing WSL

```powershell
# From Windows PowerShell:

# List all WSL distributions
wsl --list --verbose

# Start WSL
wsl

# Shutdown WSL
wsl --shutdown

# Restart specific distribution
wsl --terminate Ubuntu
```

### File Operations

```bash
# Copy from Windows to WSL
cp /mnt/c/source/file.txt ~/destination/

# Copy from WSL to Windows
cp ~/source/file.txt /mnt/c/destination/

# Create symbolic link
ln -s /mnt/c/Projects/Airlines ~/airlines
```

## Troubleshooting WSL

### Issue: "Cannot connect to SSH server"

```bash
# Check network connectivity
ping <server_ip>

# Test SSH directly
ssh -v -i ~/.ssh/id_ed25519 <ssh_user>@<server_ip>

# Check SSH key permissions
ls -la ~/.ssh/id_ed25519
# Should show: -rw------- (600)
```

### Issue: "Permission denied (publickey)"

```bash
# Fix key permissions
chmod 600 ~/.ssh/id_ed25519

# Verify key is correct
ssh-keygen -l -f ~/.ssh/id_ed25519

# Test with verbose output
ssh -vvv -i ~/.ssh/id_ed25519 <ssh_user>@<server_ip>
```

### Issue: "Module not found"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
which python3
# Should show: /home/username/venv/bin/python3
```

### Issue: "Bad interpreter"

If you get "bad interpreter" errors:

```bash
# Convert line endings from Windows to Unix
sudo apt install dos2unix
dos2unix *.py
```

## Performance Tips

### 1. Work in WSL File System

For better performance, copy your project to WSL:

```bash
# Copy project to WSL home directory
cp -r /mnt/c/Projects/Airlines ~/Airlines

# Work from there
cd ~/Airlines
```

### 2. Use WSL 2

```powershell
# Ensure you're using WSL 2
wsl --set-version Ubuntu 2
```

### 3. Allocate More Resources

Create/edit `.wslconfig` in Windows:

```powershell
# In Windows, create: C:\Users\YOUR_USERNAME\.wslconfig
notepad $env:USERPROFILE\.wslconfig
```

Add:

```ini
[wsl2]
memory=4GB
processors=2
```

## Quick Start Script for WSL

Create a startup script:

```bash
# Create script
nano ~/start_airlines.sh
```

Add:

```bash
#!/bin/bash

# Navigate to project
cd /mnt/c/Projects/Airlines

# Activate virtual environment
source venv/bin/activate

# Show status
echo "✓ Airlines project ready!"
echo "  Python: $(python3 --version)"
echo "  Location: $(pwd)"
echo ""
echo "Available commands:"
echo "  python3 database.py - Test database connection"
echo "  python3 main.py analyze - Run analysis"
echo "  python3 test_mariadb_connection.py - Run tests"
```

Make it executable:

```bash
chmod +x ~/start_airlines.sh
```

Use it:

```bash
# Run the script
~/start_airlines.sh
```

## Comparison: Windows vs WSL

| Feature | Windows | WSL Ubuntu |
|---------|---------|------------|
| SSH Support | Via libraries | Native |
| Performance | Good | Better |
| Compatibility | Some issues | Excellent |
| Setup | Easier | Requires setup |
| Tools | Limited | Full Linux |
| DSSKey Issues | Yes | No |

## Recommendation

**Use WSL Ubuntu for:**

- Development and testing
- Running database operations
- SSH-heavy tasks
- Better debugging

**Use Windows for:**

- Quick edits
- File management
- GUI applications

## Next Steps

1. **Install WSL Ubuntu** if not already installed
2. **Set up virtual environment** in WSL
3. **Copy SSH keys** with correct permissions
4. **Update .env** with Linux paths
5. **Test connection** with `python3 database.py`
6. **Run your application** in WSL

## Additional Resources

- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [VS Code WSL Guide](https://code.visualstudio.com/docs/remote/wsl)
- [Python in WSL](https://docs.microsoft.com/en-us/windows/python/web-frameworks)

---

**WSL Ubuntu provides a better environment for Python development and SSH operations!** 🐧🚀
