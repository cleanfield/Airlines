#!/bin/bash
# WSL Ubuntu Setup Script for Airlines MariaDB Project
# Run this script in WSL Ubuntu to set up your environment

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Airlines Project - WSL Ubuntu Setup Script            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current user
CURRENT_USER=$(whoami)
echo "Setting up for user: $CURRENT_USER"
echo ""

# Step 1: Update system
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Updating system packages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo apt update
sudo apt upgrade -y
echo -e "${GREEN}✓ System updated${NC}"
echo ""

# Step 2: Install Python and dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Installing Python and tools..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential libssl-dev libffi-dev
echo -e "${GREEN}✓ Python installed${NC}"
python3 --version
pip3 --version
echo ""

# Step 3: Navigate to project
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Setting up project directory..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if we're in the project directory
if [ -f "requirements.txt" ] && [ -f "database.py" ]; then
    echo -e "${GREEN}✓ Already in Airlines project directory${NC}"
    PROJECT_DIR=$(pwd)
else
    # Try to find the project
    if [ -d "/mnt/c/Projects/Airlines" ]; then
        PROJECT_DIR="/mnt/c/Projects/Airlines"
        cd "$PROJECT_DIR"
        echo -e "${GREEN}✓ Found project at: $PROJECT_DIR${NC}"
    else
        echo -e "${RED}✗ Could not find Airlines project${NC}"
        echo "Please run this script from the Airlines project directory"
        exit 1
    fi
fi
echo ""

# Step 4: Create virtual environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Creating Python virtual environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Step 5: Install Python packages
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Installing Python packages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Python packages installed${NC}"
echo ""

# Step 6: Set up SSH keys
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 6: Setting up SSH keys..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create .ssh directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Copy SSH keys if they exist in project
if [ -f "id_ed25519" ]; then
    cp id_ed25519 ~/.ssh/
    cp id_ed25519.pub ~/.ssh/
    chmod 600 ~/.ssh/id_ed25519
    chmod 644 ~/.ssh/id_ed25519.pub
    echo -e "${GREEN}✓ SSH keys copied and permissions set${NC}"
    
    # Verify key
    echo "SSH key fingerprint:"
    ssh-keygen -l -f ~/.ssh/id_ed25519
else
    echo -e "${YELLOW}⚠ SSH keys not found in project directory${NC}"
    echo "Please copy your SSH keys manually:"
    echo "  cp /path/to/id_ed25519 ~/.ssh/"
    echo "  chmod 600 ~/.ssh/id_ed25519"
fi
echo ""

# Step 7: Update .env file
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 7: Updating .env file for WSL..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".env" ]; then
    # Create backup
    cp .env .env.backup
    echo -e "${GREEN}✓ Created backup: .env.backup${NC}"
    
    # Update SSH key paths
    sed -i "s|MARIA_ID_ED25519=.*|MARIA_ID_ED25519=$HOME/.ssh/id_ed25519|g" .env
    sed -i "s|MARIA_ID_ED25519_PUB=.*|MARIA_ID_ED25519_PUB=$HOME/.ssh/id_ed25519.pub|g" .env
    
    echo -e "${GREEN}✓ Updated .env file with WSL paths${NC}"
    echo "SSH key path set to: $HOME/.ssh/id_ed25519"
else
    echo -e "${RED}✗ .env file not found${NC}"
fi
echo ""

# Step 8: Test SSH connection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 8: Testing SSH connection..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get server from .env
if [ -f ".env" ]; then
    source .env
    
    if [ -n "$MARIA_SERVER" ] && [ -f ~/.ssh/id_ed25519 ]; then
        echo "Testing connection to $MARIA_SERVER..."
        
        # Add to known hosts if not already there
        ssh-keyscan -H $MARIA_SERVER >> ~/.ssh/known_hosts 2>/dev/null
        
        # Test SSH connection (with timeout)
        if timeout 5 ssh -i ~/.ssh/id_ed25519 -o ConnectTimeout=5 -o StrictHostKeyChecking=no $MARIA_SSH_USER@$MARIA_SERVER "echo 'SSH connection successful'" 2>/dev/null; then
            echo -e "${GREEN}✓ SSH connection successful${NC}"
        else
            echo -e "${YELLOW}⚠ Could not connect to SSH server${NC}"
            echo "This might be normal if the server is not accessible right now"
        fi
    else
        echo -e "${YELLOW}⚠ Skipping SSH test (missing configuration)${NC}"
    fi
fi
echo ""

# Step 9: Test database connection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 9: Testing database connection..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "database.py" ]; then
    echo "Running database connection test..."
    if timeout 30 python3 database.py; then
        echo -e "${GREEN}✓ Database connection test passed${NC}"
    else
        echo -e "${YELLOW}⚠ Database connection test failed or timed out${NC}"
        echo "You can test manually later with: python3 database.py"
    fi
else
    echo -e "${YELLOW}⚠ database.py not found${NC}"
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Your WSL Ubuntu environment is ready!"
echo ""
echo "Quick Start:"
echo "  1. Activate virtual environment:"
echo "     ${GREEN}source venv/bin/activate${NC}"
echo ""
echo "  2. Test database connection:"
echo "     ${GREEN}python3 database.py${NC}"
echo ""
echo "  3. Run comprehensive tests:"
echo "     ${GREEN}python3 test_mariadb_connection.py${NC}"
echo ""
echo "  4. Run your application:"
echo "     ${GREEN}python3 main.py analyze --days-back 7${NC}"
echo ""
echo "Documentation:"
echo "  - WSL_UBUNTU_SETUP.md - This setup guide"
echo "  - MARIADB_README.md - Complete MariaDB guide"
echo "  - MARIADB_QUICK_REFERENCE.md - Quick reference"
echo ""
echo "Project location: $PROJECT_DIR"
echo "Python: $(python3 --version)"
echo "Virtual environment: ${PROJECT_DIR}/venv"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
