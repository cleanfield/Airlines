# 🚀 WSL Ubuntu - Getting Started in 5 Minutes

## Step 1: Open WSL Ubuntu (30 seconds)

### Option A: From Start Menu

1. Click Start
2. Type "Ubuntu"
3. Click "Ubuntu" app

### Option B: From PowerShell/CMD

```powershell
wsl
```

You should see a terminal that looks like:

```
username@computername:/mnt/c/Users/username$
```

---

## Step 2: Navigate to Project (10 seconds)

```bash
cd /mnt/c/Projects/Airlines
```

Verify you're in the right place:

```bash
ls
```

You should see files like: `database.py`, `requirements.txt`, `.env`

---

## Step 3: Run Automated Setup (3-5 minutes)

```bash
# Make setup script executable
chmod +x wsl_setup.sh

# Run the setup script
./wsl_setup.sh
```

The script will:

- ✅ Install Python and dependencies
- ✅ Create virtual environment
- ✅ Install Python packages
- ✅ Configure SSH keys
- ✅ Update .env file
- ✅ Test connections

**Just sit back and watch!** ☕

---

## Step 4: Test Database Connection (30 seconds)

```bash
# Activate virtual environment
source venv/bin/activate

# Test connection
python3 database.py
```

Expected output:

```
=== Database Connection Test ===

Establishing SSH tunnel to <server_ip>...
✓ Loaded Ed25519 key
SSH tunnel established on local port XXXXX
Database connection established successfully!
```

---

## Step 5: Start Coding! 🎉

You're ready! Here are some commands to try:

### Run Examples

```bash
python3 mariadb_connection_example.py
```

### Run Tests

```bash
python3 test_mariadb_connection.py
```

### Run Your Application

```bash
python3 main.py analyze --days-back 7
```

### Interactive Python

```bash
python3

>>> from database import DatabaseManager
>>> with DatabaseManager() as db:
...     print("Connected to MariaDB!")
```

---

## 📋 Cheat Sheet

### Every Time You Start Working

```bash
# 1. Open WSL
wsl

# 2. Go to project
cd /mnt/c/Projects/Airlines

# 3. Activate virtual environment
source venv/bin/activate

# 4. Start coding!
```

### Common Commands

```bash
# Test database
python3 database.py

# Run your app
python3 main.py analyze

# Edit files
code .                    # VS Code
nano database.py          # Terminal editor

# Check Python version
python3 --version

# List installed packages
pip list

# Deactivate virtual environment
deactivate
```

---

## 🆘 Quick Troubleshooting

### "wsl: command not found"

**Solution:** Install WSL first

```powershell
# In PowerShell as Administrator
wsl --install -d Ubuntu
```

### "Permission denied" on setup script

**Solution:**

```bash
chmod +x wsl_setup.sh
```

### "Module not found"

**Solution:**

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### SSH connection fails

**Solution:**

```bash
# Check key permissions
chmod 600 ~/.ssh/id_ed25519

# Test SSH
ssh -i ~/.ssh/id_ed25519 <ssh_user>@<server_ip>
```

---

## 💡 Pro Tips

1. **Create an alias** for quick access:

   ```bash
   echo "alias airlines='cd /mnt/c/Projects/Airlines && source venv/bin/activate'" >> ~/.bashrc
   source ~/.bashrc
   
   # Now just type:
   airlines
   ```

2. **Use VS Code** with WSL:

   ```bash
   code .
   ```

   This opens VS Code connected to WSL for the best experience!

3. **Tab completion** - Press Tab to autocomplete paths and commands

4. **Command history** - Press ↑ to see previous commands

5. **Keep venv activated** - While working on the project

---

## 📚 Full Documentation

- **`WSL_SETUP_SUMMARY.md`** - Complete overview
- **`WSL_UBUNTU_SETUP.md`** - Detailed setup guide  
- **`WSL_QUICK_REFERENCE.md`** - Command reference
- **`MARIADB_README.md`** - Database usage guide

---

## ✅ Success Checklist

After setup, you should be able to:

- [ ] Open WSL Ubuntu terminal
- [ ] Navigate to `/mnt/c/Projects/Airlines`
- [ ] Activate virtual environment with `source venv/bin/activate`
- [ ] See `(venv)` in your prompt
- [ ] Run `python3 database.py` successfully
- [ ] See "Database connection established successfully!"

If all checked ✅ - **You're ready to code!** 🎉

---

## 🎯 What's Next?

1. **Explore the examples:**

   ```bash
   python3 mariadb_connection_example.py
   ```

2. **Read the documentation:**
   - Start with `MARIADB_README.md`
   - Check `WSL_QUICK_REFERENCE.md` for commands

3. **Integrate with your app:**
   - Use `DatabaseManager` in your scripts
   - Save flight data to database
   - Query and analyze data

4. **Customize your environment:**
   - Set up aliases
   - Configure VS Code
   - Install additional tools

---

**You're all set! Happy coding with WSL Ubuntu! 🐧💻🚀**
