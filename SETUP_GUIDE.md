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
    *   Paste your Google Gemini API Key.
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
