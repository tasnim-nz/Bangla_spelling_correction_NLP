#!/bin/bash
# Bananriti Project Setup Script
# Sets up the complete development environment

echo "=================================================="
echo "বানানরীতি (Bananriti) - Project Setup"
echo "Bangla Spelling Error Correction System"
echo "=================================================="
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Create virtual environment
echo "[2/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "Virtual environment created at: ./venv"
else
    echo "Virtual environment already exists at: ./venv"
fi
echo ""

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated"
echo ""

# Upgrade pip
echo "[4/5] Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo ""

# Install requirements
echo "[5/5] Installing dependencies..."
pip install -r requirements.txt
echo ""

echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "Project structure is ready at:"
echo "  ./1_Data_Preprocessing/"
echo "  ./2_Error_Generation/"
echo "  ./3_Noisy_Channel_Model/"
echo "  ./4_BanglaT5_Model/"
echo "  ./5_Evaluation/"
echo "  ./resources/"
echo "  ./utils/"
echo ""
