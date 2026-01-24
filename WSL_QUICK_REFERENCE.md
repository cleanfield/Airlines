# WSL Quick Reference for Airlines Project

## 🚀 Quick Start

### Open WSL Ubuntu

```powershell
# From Windows PowerShell or Command Prompt
wsl
```

### Navigate to Project

```bash
cd /mnt/c/Projects/Airlines
```

### Activate Virtual Environment

```bash
source venv/bin/activate
```

### Test Database Connection

```bash
python3 database.py
```

## 📦 One-Time Setup

### Run Automated Setup Script

```bash
# Navigate to project
cd /mnt/c/Projects/Airlines

# Make script executable
chmod +x wsl_setup.sh

# Run setup
./wsl_setup.sh
```

### Manual Setup Steps

```bash
# 1. Install Python
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy SSH keys
mkdir -p ~/.ssh
cp id_ed25519 ~/.ssh/
chmod 600 ~/.ssh/id_ed25519

# 6. Update .env file
nano .env
# Change: MARIA_ID_ED25519=$HOME/.ssh/id_ed25519
```

## 💻 Daily Usage

### Start Working

```bash
# 1. Open WSL
wsl

# 2. Go to project
cd /mnt/c/Projects/Airlines

# 3. Activate environment
source venv/bin/activate

# 4. Start coding!
```

### Run Scripts

```bash
# Test database
python3 database.py

# Run tests
python3 test_mariadb_connection.py

# Run examples
python3 mariadb_connection_example.py

# Run main application
python3 main.py analyze --days-back 7
```

### Interactive Python

```bash
python3

# In Python shell:
>>> from database import DatabaseManager
>>> with DatabaseManager() as db:
...     print("Connected!")
```

## 🔧 Common Commands

### WSL Management (from Windows)

```powershell
# List WSL distributions
wsl --list --verbose

# Start WSL
wsl

# Shutdown WSL
wsl --shutdown

# Restart Ubuntu
wsl --terminate Ubuntu
```

### File Navigation

```bash
# Windows C: drive
cd /mnt/c/

# Your project
cd /mnt/c/Projects/Airlines

# Home directory
cd ~

# List files
ls -la

# Current directory
pwd
```

### Virtual Environment

```bash
# Activate
source venv/bin/activate

# Deactivate
deactivate

# Check if active (should show venv path)
which python3
```

### SSH Operations

```bash
# Test SSH connection
ssh -i ~/.ssh/id_ed25519 <ssh_user>@<server_ip>

# Check SSH key
ls -la ~/.ssh/id_ed25519

# Fix permissions
chmod 600 ~/.ssh/id_ed25519

# View key fingerprint
ssh-keygen -l -f ~/.ssh/id_ed25519
```

### Package Management

```bash
# Install package
pip install package_name

# Install from requirements
pip install -r requirements.txt

# List installed packages
pip list

# Upgrade package
pip install --upgrade package_name
```

## 📝 Editing Files

### Using Nano (Terminal Editor)

```bash
# Edit file
nano database.py

# Save: Ctrl+O, Enter
# Exit: Ctrl+X
```

### Using VS Code

```bash
# Open current directory in VS Code
code .

# Open specific file
code database.py
```

### Using Vim

```bash
# Edit file
vim database.py

# Enter insert mode: i
# Save and exit: Esc, :wq
# Exit without saving: Esc, :q!
```

## 🔍 Debugging

### Check Python Version

```bash
python3 --version
pip3 --version
```

### Check Virtual Environment

```bash
# Should show venv path when activated
which python3

# Should show packages in venv
pip list
```

### Check Environment Variables

```bash
# View .env file
cat .env

# Check specific variable
echo $MARIA_SERVER
```

### View Logs

```bash
# Run with verbose output
python3 -v database.py

# Check system logs
dmesg | tail
```

### Network Debugging

```bash
# Test connectivity
ping <server_ip>

# Test SSH with verbose output
ssh -vvv -i ~/.ssh/id_ed25519 <ssh_user>@<server_ip>

# Check open connections
netstat -an | grep 3306
```

## 📂 File Operations

### Copy Files

```bash
# Windows to WSL
cp /mnt/c/source/file.txt ~/destination/

# WSL to Windows
cp ~/source/file.txt /mnt/c/destination/
```

### Permissions

```bash
# Make executable
chmod +x script.sh

# SSH key permissions
chmod 600 ~/.ssh/id_ed25519

# View permissions
ls -la filename
```

### Find Files

```bash
# Find by name
find . -name "*.py"

# Find and execute
find . -name "*.py" -exec grep "DatabaseManager" {} \;
```

## 🎯 Useful Aliases

Add to `~/.bashrc`:

```bash
# Edit bashrc
nano ~/.bashrc

# Add these lines:
alias airlines='cd /mnt/c/Projects/Airlines && source venv/bin/activate'
alias dbtest='python3 database.py'
alias activate='source venv/bin/activate'

# Reload bashrc
source ~/.bashrc
```

Now you can use:

```bash
airlines  # Go to project and activate venv
dbtest    # Test database connection
```

## 🆘 Troubleshooting

### "Command not found"

```bash
# Reinstall package
pip install package_name

# Check if venv is activated
source venv/bin/activate
```

### "Permission denied"

```bash
# Fix file permissions
chmod +x filename

# Fix SSH key
chmod 600 ~/.ssh/id_ed25519
```

### "Module not found"

```bash
# Activate venv
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### "Bad interpreter"

```bash
# Install dos2unix
sudo apt install dos2unix

# Convert file
dos2unix filename.py
```

## 📊 Performance

### Check Resource Usage

```bash
# CPU and memory
top

# Disk usage
df -h

# Directory size
du -sh *
```

### Clean Up

```bash
# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Remove old packages
pip cache purge
```

## 🔄 Git Operations (if using Git)

```bash
# Check status
git status

# Pull latest changes
git pull

# Commit changes
git add .
git commit -m "message"
git push
```

## 📱 VS Code Integration

### Connect VS Code to WSL

1. Install "WSL" extension in VS Code
2. Click green icon (bottom-left)
3. Select "Connect to WSL"
4. Open folder: `/mnt/c/Projects/Airlines`

### Or from terminal

```bash
cd /mnt/c/Projects/Airlines
code .
```

## 🎓 Learning Resources

- WSL Docs: <https://docs.microsoft.com/en-us/windows/wsl/>
- Ubuntu Commands: <https://ubuntu.com/tutorials/command-line-for-beginners>
- Python venv: <https://docs.python.org/3/library/venv.html>

---

## 🌟 Pro Tips

1. **Use Tab completion** - Press Tab to autocomplete commands and paths
2. **Use history** - Press ↑ to cycle through previous commands
3. **Use Ctrl+R** - Search command history
4. **Use Ctrl+C** - Cancel current command
5. **Use Ctrl+L** - Clear screen
6. **Create aliases** - For frequently used commands
7. **Keep venv activated** - While working on the project

---

**Happy coding in WSL! 🐧💻**
