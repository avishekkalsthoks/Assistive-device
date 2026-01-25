# Software Setup Guide: Smart Vision Guide (Fresh Install)

This guide provides a clean, step-by-step software setup for the **Raspberry Pi Zero 2W** running **Raspberry Pi OS 10 (Buster)** with a **Pi Camera Rev 1.3**.

---

## 1. Prerequisites
*   **Raspberry Pi Zero 2W**
*   **Raspberry Pi OS 10 (Buster)** (Legacy/Oldstable)
*   **Pi Camera Rev 1.3**
*   **Active Internet Connection** (for API calls and installation)
*   **OpenRouter API Key**

---

## 2. Initial System Preparation

Connect to your Pi via SSH and run these commands to update the system and install essential tools.

```bash
# Update package lists and upgrade existing packages
sudo apt-get update
sudo apt-get upgrade -y

# Install core system dependencies
sudo apt-get install -y \
    git \
    python3-pip \
    python3-venv \
    mpg123 \
    portaudio19-dev \
    libasound2-dev \
    libatlas-base-dev \
    v4l-utils
```

---

## 3. Enable Camera interface (Buster 10)

For Raspberry Pi OS 10 (Buster), we need to ensure the legacy camera interface is enabled.

1.  Run the configuration tool:
    ```bash
    sudo raspi-config
    ```
2.  Navigate to **Interfacing Options** (or **Interface Options**).
3.  Select **Camera** and choose **YES** to enable it.
4.  Finish and **Reboot** if prompted:
    ```bash
    sudo reboot
    ```

---

## 4. Project Installation

Clone the repository and set up the Python environment.

```bash
# Clone the repository
git clone https://github.com/avishekkalsthoks/Assistive-device.git Smart-Vision-Guide
cd Smart-Vision-Guide

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
# Note: We use opencv-python-headless to avoid system library conflicts on Buster
pip install -r requirements.txt
```

---

## 5. Configuration

1.  **Environment Variables**:
    Create a `.env` file from the example:
    ```bash
    cp .env.example .env
    nano .env
    ```
    Enter your **OPENROUTER_API_KEY** in the file:
    ```text
    OPENROUTER_API_KEY=your_key_here
    ```
    Press `Ctrl+O`, `Enter`, then `Ctrl+X` to save and exit.

2.  **Audio Configuration** (For USB Audio/Earphones):
    If using a USB audio adapter, you may need to set it as default:
    ```bash
    nano ~/.asoundrc
    ```
    Paste the following:
    ```text
    defaults.pcm.card 1
    defaults.ctl.card 1
    ```

---

## 6. Bluetooth Audio Setup (Optional)

If you are using Bluetooth earphones, follow these steps to pair and connect them.

1.  **Install Bluetooth modules**:
    ```bash
    sudo apt-get install -y pulseaudio-module-bluetooth bluez
    ```

2.  **Pair your device**:
    Run the Bluetooth control tool:
    ```bash
    sudo bluetoothctl
    ```
    Inside the `bluetoothctl` prompt, type these commands:
    ```text
    power on
    agent on
    default-agent
    scan on
    # Wait for your earphones to appear (e.g., AA:BB:CC:11:22:33 Earphones)
    pair AA:BB:CC:11:22:33
    trust AA:BB:CC:11:22:33
    connect AA:BB:CC:11:22:33
    exit
    ```

3.  **Set as Default Output**:
    Buster uses PulseAudio for Bluetooth. You can ensure audio routes to the headset using:
    ```bash
    pacmd set-default-sink 1
    ```

---

## 7. Running the Application

Always ensure your virtual environment is active before running:

```bash
cd ~/Smart-Vision-Guide
source venv/bin/activate
python main.py
```

### Voice Commands:
*   **"Hello Vision"**: Activate the system
*   **"Read text"**: Perform OCR on the current view
*   **"Describe"**: Get a full scene description
*   **"System exit"**: Shut down the app

---

## 8. Troubleshooting (Buster & Rev 1.3 Camera)

*   **Camera Not Detected**: 
    Run `vcgencmd get_camera`. It should return `supported=1 detected=1`. If `detected=0`, check the ribbon cable seating (metal pins face the HDMI port on Pi Zero).
*   **Permission Errors**: 
    Ensure your user is in the `video` and `audio` groups:
    ```bash
    sudo usermod -a -G video,audio $USER
    ```
*   **Memory Issues**:
    The Pi Zero 2W has 512MB RAM. The `opencv-python-headless` package and single-frame capture logic in this project are specifically optimized for this.

---

## 9. Auto-Start on Boot (Optional)

To run the guide automatically whenever the Pi starts:

```bash
sudo cp smart-vision.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smart-vision
sudo systemctl start smart-vision
```
