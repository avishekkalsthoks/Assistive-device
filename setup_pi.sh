#!/bin/bash
# =============================================================================
# Raspberry Pi Zero 2W Setup Script for Smart Vision Guide
# Run this script on a fresh Raspberry Pi OS installation
# =============================================================================

echo "=============================================="
echo "Smart Vision Guide - Pi Zero 2W Setup"
echo "=============================================="

# Update system
echo ""
echo "[1/7] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo ""
echo "[2/7] Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    mpg123 \
    portaudio19-dev \
    libasound2-dev \
    libatlas-base-dev \
    libopencv-dev \
    python3-opencv

# Create virtual environment
echo ""
echo "[3/7] Creating Python virtual environment..."
cd ~/Smart-Vision-Guide
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo ""
echo "[4/7] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Enable camera interface
echo ""
echo "[5/7] Enabling camera interface..."
sudo raspi-config nonint do_camera 1

# Setup audio
echo ""
echo "[6/7] Configuring audio..."
# Create ALSA config for USB audio
if ! grep -q "defaults.ctl.card 1" ~/.asoundrc 2>/dev/null; then
    echo "defaults.ctl.card 1" >> ~/.asoundrc
    echo "defaults.pcm.card 1" >> ~/.asoundrc
    echo "Audio configured for USB adapter (card 1)"
fi

# Create systemd service for auto-start
echo ""
echo "[7/7] Creating systemd service..."
sudo tee /etc/systemd/system/smart-vision.service > /dev/null << EOF
[Unit]
Description=Smart Vision Guide
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/Smart-Vision-Guide
ExecStart=/home/$USER/Smart-Vision-Guide/venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Copy your .env file with GEMINI_API_KEY"
echo "2. Test the system: python main.py"
echo "3. Enable auto-start: sudo systemctl enable smart-vision"
echo ""
echo "To start now: sudo systemctl start smart-vision"
echo "To check logs: journalctl -u smart-vision -f"
echo ""
