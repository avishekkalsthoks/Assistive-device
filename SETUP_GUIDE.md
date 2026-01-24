# Smart Vision Guide — Clean Setup Guide (Raspberry Pi Zero 2W)

This guide provides a concise, tested set of commands to prepare a Raspberry Pi Zero 2W for the Smart Vision Guide (online OpenRouter-based operation). It focuses on a reproducible, minimal software install (no offline modes). Follow each step on the Pi via SSH.

Prerequisites
- Raspberry Pi Zero 2W
- MicroSD card (16GB+), power supply, Pi Camera (CSI) and USB microphone or USB audio adapter
- Network access (Wi‑Fi)

Quick overview
1. Flash OS and enable SSH/Wi‑Fi
2. Update system and install apt packages (OpenCV via apt, audio utils)
3. Clone repo, create Python venv and install pip deps
4. Create `.env` with `OPENROUTER_API_KEY`
5. Enable camera and test camera/audio
6. (Optional) Enable systemd auto-start

Step 0 — Prepare the SD card (headless)
- Use Raspberry Pi Imager and choose "Raspberry Pi OS (Legacy) Lite" or similar.
- In the Imager advanced options (Ctrl+Shift+X) set hostname (`smartvision`), enable SSH, and configure Wi‑Fi credentials.

Step 1 — First boot and SSH
1. Insert SD card, power the Pi. Wait ~2 minutes.
2. From your laptop: `ssh pi@smartvision.local` (or `ssh pi@<PI_IP>`).

Step 2 — System update and required apt packages
Run the following on the Pi (copy-paste):

```bash
sudo apt update && sudo apt upgrade -y

# Core tools and recommended packages
sudo apt install -y git python3-venv python3-pip python3-opencv v4l-utils \
  build-essential pkg-config libatlas-base-dev libjpeg-dev libtiff5-dev \
  portaudio19-dev python3-pyaudio ffmpeg mpg123 haveged

# Optional (Bluetooth audio):
sudo apt install -y pulseaudio pulseaudio-module-bluetooth bluez bluez-tools
```

Notes:
- We install `python3-opencv` and `python3-pyaudio` from apt to avoid heavy pip builds on Pi Zero 2W.
- `mpg123` is used for MP3 playback by the TTS handler.

Step 3 — Clone the repository

```bash
cd /home/pi
git clone https://github.com/avishekkalsthoks/Assistive-device.git Smart-Vision-Guide
cd Smart-Vision-Guide
```

Step 4 — Python virtual environment and pip packages

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install project requirements (we rely on apt for OpenCV/pyaudio)
pip install -r requirements.txt

# Ensure HTTP/env helpers are present
pip install requests python-dotenv pillow
```

Step 5 — Create `.env` and set OpenRouter key
1. Copy the template and edit the key:

```bash
cp .env.example .env
nano .env
# Set OPENROUTER_API_KEY=your_openrouter_key_here
```

Security: Never commit `.env`. It is in `.gitignore`.

Step 6 — Camera and audio quick tests

# Camera test (Python/OpenCV)
```bash
source venv/bin/activate
python3 - <<'PY'
import cv2
cap = cv2.VideoCapture(0)
print('camera open:', cap.isOpened())
if cap.isOpened():
    ret, frame = cap.read()
    print('frame ok:', ret)
    cap.release()
PY
```

# Audio/TTS test (generate a small TTS file and play)
```bash
python3 - <<'PY'
from gtts import gTTS
fn='/tmp/tts_test.mp3'
t= gTTS('Hello from Smart Vision Guide', lang='en')
t.save(fn)
print('saved', fn)
PY
mpg123 -q /tmp/tts_test.mp3 && echo 'played'
```

If the camera test prints `camera open: True` and `frame ok: True`, camera access is working. If audio playback fails, ensure `mpg123` is installed and your audio device is configured.

Step 7 — Enable camera (non-interactive)
```bash
sudo raspi-config nonint do_camera 1 || true
```

Step 8 — Systemd service (auto-start on boot)
Create the service file (run as root or with sudo):

```bash
sudo tee /etc/systemd/system/smart-vision.service > /dev/null <<'EOF'
[Unit]
Description=Smart Vision Guide
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Smart-Vision-Guide
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/pi/Smart-Vision-Guide/venv/bin/python /home/pi/Smart-Vision-Guide/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable smart-vision
sudo systemctl start smart-vision
sudo journalctl -u smart-vision -f
```

Step 9 — Runtime tuning for Pi Zero 2W
- If network calls are slow or you hit timeouts, reduce image size in `config/settings.py`:

```py
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
JPEG_QUALITY = 50
CAPTURE_INTERVAL = 4.0
```

Step 10 — Troubleshooting
- Camera not opening: ensure ribbon cable seating, `sudo raspi-config` camera enabled, and `python3-opencv` installed.
- Audio not playing: run `aplay -l` or `mpg123 --version` and verify device. For USB audio adapters, you may need to set ALSA defaults in `~/.asoundrc`.
- OpenRouter errors: check `.env` has `OPENROUTER_API_KEY` and check network connectivity. Inspect logs with `journalctl -u smart-vision -f`.

Security & housekeeping
- Keep `.env` local and out of version control. If your API key was exposed, rotate it immediately via the OpenRouter dashboard.
- Use `sudo journalctl -u smart-vision -b` to collect logs for debugging.

If you want, I can now:
- Update `setup_pi.sh` to implement this exact bootstrap script and remove any offline-only installs, or
- Add a `scripts/setup_env.sh` that creates `.env` from `.env.example` safely on the Pi.

End of guide.
# Complete Setup Guide: Smart Vision Guide on Raspberry Pi Zero 2W

This guide covers everything from flashing the OS to running the project.
**Scenario:** You have a Laptop (Windows/Mac), a Pi Zero 2W, and **NO monitor/keyboard** for the Pi.

---

## Phase 1: Hardware Checklist

Before starting, ensure you have:
1.  **Raspberry Pi Zero 2W**
2.  **MicroSD Card** (16GB or larger) + Card Reader
3.  **Power Supply** (Micro USB, 5V 2.5A)
4.  **Hardware Components:**
    *   Pi Camera Module (v2/v3) + Ribbon Cable for Pi Zero
    *   USB Microphone (with MicroUSB adapter/shim)
    *   Bluetooth Earphones (or USB Audio Adapter + Speaker)
    *   Ultrasonic Sensor (HC-SR04) + Resistors (1kΩ, 2kΩ) + Buzzer

---

## Phase 2: Installing Raspberry Pi OS (Headless)

Since we don't have a monitor, we will configure WiFi and SSH *before* booting.

### Step 1: Flash the OS
1.  Download and install **[Raspberry Pi Imager](https://www.raspberrypi.com/software/)** on your laptop.
2.  Insert your MicroSD card into the laptop.
3.  Open Raspberry Pi Imager:
    *   **Device:** Choose "Raspberry Pi Zero 2 W".
    *   **OS:** Choose "Raspberry Pi OS (Legacy, 64-bit) Lite".
        *   *Note: "Lite" has no desktop interface, which is perfect for this project (faster).*
    *   **Storage:** Select your SD card.

### Step 2: Configure Settings (Critical!)
**Before clicking "NEXT", click on "EDIT SETTINGS" (or press Ctrl+Shift+X).**

1.  **General Tab:**
    *   ✅ Set hostname: `smartvision`
    *   ✅ Set username and password:
        *   User: `pi`
        *   Password: `password` (or your choice)
    *   ✅ Configure Wireless LAN:
        *   SSID: `Your_WiFi_Name`
        *   Password: `Your_WiFi_Password`
        *   Country code: `US` (or your country)

2.  **Services Tab:**
    *   ✅ Enable SSH
    *   Select "Use password authentication"

3.  **Save & Write:**
    *   Click **SAVE**.
    *   Click **YES** to apply settings.
    *   Click **YES** to write data (this will erase the card).

---

## Phase 3: First Boot & Connection

1.  Insert the SD card into the Raspberry Pi Zero 2W.
2.  Connect the power cable (MicroUSB port labeled "PWR").
3.  Wait about 2-3 minutes for the first boot.

### Step 1: Connect via SSH
Open **Command Prompt (Windows)** or **Terminal (Mac/Linux)** on your laptop.

Type:
```bash
ssh pi@smartvision.local
```
*(If prompted "Are you sure...", type `yes` and Enter)*
 
### Full, copy-paste setup (one-shot)

If you prefer a single sequence to run on a fresh Pi Zero 2W (will install apt packages, create venv, and install pip deps), run the following as a single script (paste and run):

```bash
#!/bin/bash
set -e

sudo apt update && sudo apt upgrade -y

# Core packages
sudo apt install -y git python3-pip python3-venv python3-opencv v4l-utils \
    build-essential pkg-config libatlas-base-dev libjpeg-dev libtiff5-dev \
    portaudio19-dev libasound2-dev libportaudiocpp0 ffmpeg mpg123 python3-pyaudio \
    pulseaudio pulseaudio-module-bluetooth bluez bluez-tools haveged

# Clone repo
cd /home/$USER || exit 1
git clone https://github.com/avishekkalsthoks/Assistive-device.git Smart-Vision-Guide
cd Smart-Vision-Guide

# Create venv and install pip deps
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install requests python-dotenv pillow

# Enable camera (non-interactive)
sudo raspi-config nonint do_camera 1 || true

echo "Setup complete. Remember to edit .env and set OPENROUTER_API_KEY"
```

Save the above as `bootstrap_pi.sh`, `chmod +x bootstrap_pi.sh`, then run `./bootstrap_pi.sh`.
*(Enter the password you set, e.g., `password`)*

**Troubleshooting:**
*   If `smartvision.local` doesn't work, find the Pi's IP address using your router's admin page or a phone app like "Fing", then try `ssh pi@192.168.1.XXX`.

---

## Phase 4: Hardware Assembly

**⚠️ ALWAYS disconnect power before wiring!**

1.  **Camera:**
    *   Lift the clip on the CSI camera port.
    *   Insert the ribbon cable (metal contacts facing the board).
    *   Push the clip down to lock.
2.  **Ultrasonic Sensor (HC-SR04):**
    *   VCC -> 5V (Physical Pin 2)
    *   GND -> GND (Physical Pin 6)
    *   Trig -> GPIO 23 (Physical Pin 16)
    *   Echo -> GPIO 24 (Physical Pin 18) **(Use voltage divider! Pi inputs are 3.3V)**
3.  **Buzzer:**
    *   Positive (+) -> GPIO 17 (Physical Pin 11)
    *   Negative (-) -> GND (Physical Pin 9)
4.  **Microphone:**

If `pip install pyaudio` succeeds in your venv, you're good. If not, use the OS package and re-create the venv.
    *   Plug into the MicroUSB data port (using OTG adapter).

---

## Phase 5: Software Installation

Now that you are connected via SSH (`pi@smartvision`), run these commands:

### Step 1: Enable Hardware
```bash
sudo raspi-config
```
*   Go to **Interface Options** -> **Legacy Camera** -> **Enable**.
*   Go to **System Options** -> **Hostname** -> (Confirm it's unique).
*   **Finish** and **Reboot** (`sudo reboot`).

### Step 2: Download the Project
SSH back into the Pi (`ssh pi@smartvision.local`) and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install -y git

# Clone the project
git clone https://github.com/avishekkalsthoks/Assistive-device.git
cd Assistive-device
```

### Step 3: Run Setup Script
We included a script to do all the heavy lifting (installing Python, audio drivers, etc.).

```bash
chmod +x setup_pi.sh
./setup_pi.sh
```
*This will take 10-20 minutes. Grab a coffee!* ☕

### Additional packages recommended for Raspberry Pi Zero 2W (software setup)


The Pi Zero 2W is resource constrained. The steps below install lightweight system packages and optional components that improve reliability for an online-first setup.

Run these before `setup_pi.sh` or after, as needed:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Basic build & audio utils
sudo apt install -y git build-essential pkg-config libatlas-base-dev libjpeg-dev libtiff5-dev \
    portaudio19-dev libasound2-dev libportaudiocpp0 ffmpeg mpg123

# Camera support and Python/OpenCV (prefer apt package on Pi Zero to avoid long pip builds)
sudo apt install -y python3-opencv v4l-utils

# Bluetooth audio (optional)
sudo apt install -y pulseaudio pulseaudio-module-bluetooth bluez bluez-tools

# Optional entropy daemon (helps TLS on headless Pi)
sudo apt install -y haveged
```

Notes:
- Using `python3-opencv` from apt avoids compiling OpenCV on the Pi Zero. If `requirements.txt` contains `opencv-python-headless`, prefer removing it from `pip install` on the Pi and use the apt package instead.
- `mpg123` provides reliable MP3 playback for TTS output. `ffmpeg` can also be used for conversions.

### Python environment & pip

Create and activate a `venv`, then install Python requirements (adapt if you used apt OpenCV):

```bash
# create virtual env
python3 -m venv venv
source venv/bin/activate

# If you installed python3-opencv from apt, remove or edit the requirements file to avoid opencv pip wheel
pip install -r requirements.txt

# Install extras for OpenRouter and image handling
pip install requests python-dotenv pillow
```

### OpenRouter API key

Create the `.env` file (we included a template `.env` in the repo). Set your OpenRouter key:

```bash
cp .env.example .env
nano .env
# set OPENROUTER_API_KEY=your-key-here
```

### Speech recognition prerequisites

`SpeechRecognition` with `pyaudio` requires PortAudio headers (installed above). On Pi, if `pip install pyaudio` fails, install the OS package instead:

```bash
sudo apt install -y python3-pyaudio
```

<!-- Offline mode instructions removed per user request. This guide is focused on online OpenRouter/gTTS setup. -->

---

## Phase 6: Bluetooth Audio Setup

This needs to be done manually once to pair your headset.

1.  **Install Bluetooth tools:**
    ```bash
    sudo apt install -y pulseaudio-module-bluetooth bluez
    ```
2.  **Pair your Headset:**
    Run: `sudo bluetoothctl`
    Inside the menu:
    ```
    scan on
    # Wait for your headset name/address (e.g., AA:BB:CC:11:22:33)
    pair AA:BB:CC:11:22:33
    trust AA:BB:CC:11:22:33
    connect AA:BB:CC:11:22:33
    exit
    ```

---

## Phase 7: Final Configuration

1.  **Add your API Key:**
    ```bash
    cp .env.example .env
    nano .env
    ```
    *   Delete the placeholder text.
    *   Paste your OpenRouter API Key (set `OPENROUTER_API_KEY=`).
    *   Press `Ctrl+X`, then `Y`, then `Enter` to save.

2.  **Run the Project:**
    ```bash
    source venv/bin/activate
    python main.py
    ```

**Success!** You should hear "Smart Vision Guide Ready".

---

## Phase 8: Auto-Start (Optional)

To make it run automatically when you plug in the power bank:

```bash
sudo systemctl enable smart-vision
sudo systemctl start smart-vision
```
