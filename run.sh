#!/bin/bash
# AI Idea to Reality POC - Streamlit Startup Script for Linux/Mac

set -e  # Exit on error

echo ""
echo "========================================"
echo "  I2POC Streamlit - Startup Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

echo "[+] Python found"
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
    echo "[+] Virtual environment created"
else
    echo "[+] Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[*] Activating virtual environment..."
source venv/bin/activate
echo "[+] Virtual environment activated"

# Install requirements
echo ""
echo "[*] Installing dependencies..."
pip install -q -r requirements.txt
echo "[+] Dependencies installed successfully"

# Check if .env file exists
echo ""
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    if [ -f ".env.example" ]; then
        echo "[*] Creating .env from .env.example..."
        cp .env.example .env
        echo "[+] .env created from .env.example"
        echo "[!] Please update .env with your credentials"
    else
        echo "ERROR: .env.example not found"
        exit 1
    fi
else
    echo "[+] .env file found"
fi

# Run the application
echo ""
echo "========================================"
echo "  Starting Streamlit Application..."
echo "========================================"
echo ""
echo "The app will open at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py --logger.level=info
