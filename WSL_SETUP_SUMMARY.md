# WSL Ubuntu Setup - Summary

## ✅ What's Been Created

I've created a complete WSL Ubuntu setup for your MariaDB connection! Here's everything you need.

## 📁 New Files Created

1. **`WSL_UBUNTU_SETUP.md`** - Complete WSL setup guide
   - Why use WSL
   - Step-by-step installation
   - Configuration instructions
   - Troubleshooting

2. **`wsl_setup.sh`** - Automated setup script
   - Installs all dependencies
   - Configures environment
   - Sets up SSH keys
   - Tests connections

3. **`WSL_QUICK_REFERENCE.md`** - Quick command reference
   - Daily usage commands
   - Common operations
   - Troubleshooting tips
   - Pro tips

## 🚀 Quick Start Guide

### Option 1: Automated Setup (Recommended)

```bash
# 1. Open WSL Ubuntu
wsl

# 2. Navigate to project
cd /mnt/c/Projects/Airlines

# 3. Make setup script executable
chmod +x wsl_setup.sh

# 4. Run setup script
./wsl_setup.sh
```

The script will:

- ✅ Update system packages
- ✅ Install Python 3 and pip
- ✅ Create virtual environment
- ✅ Install all Python dependencies
- ✅ Copy and configure SSH keys
- ✅ Update .env file for WSL
- ✅ Test SSH connection
- ✅ Test database connection

### Option 2: Manual Setup

```bash
# 1. Open WSL
wsl

# 2. Go to project
cd /mnt/c/Projects/Airlines

# 3. Install Python
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# 4. Create virtual environment
python3 -m venv venv

# 5. Activate virtual environment
source venv/bin/activate

# 6. Install dependencies
pip install -r requirements.txt

# 7. Set up SSH keys
mkdir -p ~/.ssh
cp id_ed25519 ~/.ssh/
chmod 600 ~/.ssh/id_ed25519

# 8. Update .env file
nano .env
# Change SSH key path to: $HOME/.ssh/id_ed25519

# 9. Test connection
python3 database.py
```

## 🎯 Why Use WSL Ubuntu?

### Advantages Over Windows

| Feature | Windows | WSL Ubuntu |
|---------|---------|------------|
| **SSH Support** | Via libraries (issues) | Native (perfect) |
| **DSSKey Issues** | Yes ❌ | No ✅ |
| **Performance** | Good | Better ⚡ |
| **Compatibility** | Some issues | Excellent ✅ |
| **Linux Tools** | Limited | Full access 🛠️ |
| **Debugging** | Harder | Easier 🔍 |

### Key Benefits

1. **No DSSKey warnings** - Native SSH support eliminates the paramiko/sshtunnel issues
2. **Better performance** - Faster I/O and networking
3. **Native tools** - Access to all Linux command-line tools
4. **Easier debugging** - Better error messages and logging
5. **Industry standard** - Most Python development happens on Linux

## 💻 Daily Workflow

### Starting Your Work Session

```bash
# 1. Open WSL Ubuntu terminal
wsl

# 2. Navigate to project
cd /mnt/c/Projects/Airlines

# 3. Activate virtual environment
source venv/bin/activate

# Your prompt should now show: (venv)
```

### Running Your Scripts

```bash
# Test database connection
python3 database.py

# Run comprehensive tests
python3 test_mariadb_connection.py

# Run examples
python3 mariadb_connection_example.py

# Run your main application
python3 main.py analyze --days-back 7
```

### Editing Files

**Option 1: VS Code (Recommended)**

```bash
# Open project in VS Code connected to WSL
code .
```

**Option 2: Terminal Editor**

```bash
# Use nano
nano database.py

# Or vim
vim database.py
```

**Option 3: Windows Editor**

- Edit files in Windows as usual
- WSL will see the changes immediately
- Files are at: `C:\Projects\Airlines\`

## 🔧 Environment Configuration

### .env File for WSL

Your `.env` file should use Linux paths for SSH keys:

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

**Note:** Replace `YOUR_USERNAME` with your WSL username (run `whoami` to find it)

Or use environment variable:

```env
MARIA_ID_ED25519=$HOME/.ssh/id_ed25519
```

### SSH Key Permissions

**Critical:** SSH keys must have correct permissions in WSL:

```bash
# Set correct permissions
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# Verify
ls -la ~/.ssh/
# Should show: -rw------- for id_ed25519
```

## 🧪 Testing

### Test SSH Connection

```bash
ssh -i ~/.ssh/id_ed25519 <ssh_user>@<server_ip>
```

### Test Database Connection

```bash
# Activate venv first
source venv/bin/activate

# Run test
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
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `WSL_UBUNTU_SETUP.md` | Complete setup guide |
| `WSL_QUICK_REFERENCE.md` | Quick command reference |
| `MARIADB_README.md` | MariaDB usage guide |
| `MARIADB_CONNECTION_GUIDE.md` | Detailed technical docs |
| `MARIADB_QUICK_REFERENCE.md` | Quick code snippets |

## 🎓 Learning WSL

### Essential Commands

```bash
# Navigate
cd /mnt/c/Projects/Airlines  # Go to Windows folder
cd ~                          # Go to home directory
pwd                           # Show current directory
ls -la                        # List files with details

# Virtual environment
source venv/bin/activate      # Activate
deactivate                    # Deactivate

# File operations
cp source dest                # Copy
mv source dest                # Move
rm file                       # Delete
nano file                     # Edit

# System
sudo apt update               # Update package list
sudo apt install package      # Install package
which python3                 # Find Python location
```

### Useful Aliases

Add to `~/.bashrc`:

```bash
# Edit bashrc
nano ~/.bashrc

# Add these lines at the end:
alias airlines='cd /mnt/c/Projects/Airlines && source venv/bin/activate'
alias dbtest='python3 database.py'

# Save and reload
source ~/.bashrc
```

Now you can just type:

```bash
airlines  # Instantly go to project and activate venv!
dbtest    # Test database connection
```

## 🔄 Switching Between Windows and WSL

### Access Windows Files from WSL

```bash
# Windows C: drive is mounted at /mnt/c/
cd /mnt/c/Projects/Airlines
```

### Access WSL Files from Windows

**File Explorer:**

```
\\wsl$\Ubuntu\home\YOUR_USERNAME\
```

**Command Line:**

```powershell
explorer.exe \\wsl$\Ubuntu\home\YOUR_USERNAME\
```

### Best Practice

**For this project:** Work from Windows location (`/mnt/c/Projects/Airlines`) so files are accessible from both Windows and WSL.

## ⚡ Performance Tips

1. **Use WSL 2** (not WSL 1)

   ```powershell
   wsl --set-version Ubuntu 2
   ```

2. **Work in WSL filesystem for intensive operations**

   ```bash
   # Copy project to WSL for better performance
   cp -r /mnt/c/Projects/Airlines ~/Airlines
   cd ~/Airlines
   ```

3. **Allocate more resources** (optional)
   Create `C:\Users\YOUR_USERNAME\.wslconfig`:

   ```ini
   [wsl2]
   memory=4GB
   processors=2
   ```

## 🆘 Troubleshooting

### WSL Not Installed?

```powershell
# In PowerShell as Administrator
wsl --install -d Ubuntu
```

### Can't Find Python?

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### SSH Connection Fails?

```bash
# Check key permissions
ls -la ~/.ssh/id_ed25519
# Should be: -rw-------

# Fix if needed
chmod 600 ~/.ssh/id_ed25519

# Test SSH directly
ssh -v -i ~/.ssh/id_ed25519 <ssh_user>@<server_ip>
```

### Module Not Found?

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 🎉 You're Ready

With WSL Ubuntu, you'll have:

- ✅ Native SSH support (no DSSKey issues)
- ✅ Better performance
- ✅ Full Linux toolset
- ✅ Easier debugging
- ✅ Industry-standard environment

## 📖 Next Steps

1. **Run the setup script:** `./wsl_setup.sh`
2. **Test the connection:** `python3 database.py`
3. **Read the guides:** Check `WSL_UBUNTU_SETUP.md`
4. **Start coding:** Your environment is ready!

---

**WSL Ubuntu provides the best environment for Python development and MariaDB connections!** 🐧🚀💻
