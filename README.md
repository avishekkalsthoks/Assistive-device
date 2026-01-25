# Smart Vision Guide

**Assistive Navigation Device for Visually Impaired People**  
*Optimized for Raspberry Pi Zero 2W with Google AI Studio (Gemini API)*

---

## Overview

Smart Vision Guide is a wearable assistive device that helps visually impaired individuals navigate their environment independently. It uses:

- **Google AI Studio (Gemini API)** for intelligent image analysis
- **Object Detection** to identify obstacles and provide navigation guidance
- **OCR (Optical Character Recognition)** to read text from signs, labels, and documents
- **Voice Control** for hands-free operation
- **Ultrasonic Sensor** for close-range obstacle detection
- **Text-to-Speech** for audio feedback

## Hardware Requirements

| Component | Model | Purpose |
|-----------|-------|---------|
| Raspberry Pi Zero 2W | - | Main computer ($15) |
| Pi Camera Module | V2 (8MP) | Image capture ($25) |
| Ultrasonic Sensor | HC-SR04 | Close-range detection ($3) |
| Buzzer | Active 3.3V | Audio alerts ($1) |
| USB Microphone | Mini USB | Voice input ($8) |
| USB Audio Adapter | Generic | Audio output ($5) |
| Speaker | 3W portable | TTS output ($5) |
| Power Bank | 10,000mAh | Power supply ($20) |
| MicroSD Card | 32GB+ | Storage ($8) |
| Cables & Wiring | - | Connections ($5) |

**Total Estimated Cost: ~$95 USD**

### Wiring Diagram

```
Raspberry Pi Zero 2W GPIO:
┌─────────────────────────────────────┐
│ GPIO 17 ─────────── Buzzer (+)      │
│ GPIO 23 ─────────── HC-SR04 Trig    │
│ GPIO 24 ─────────── HC-SR04 Echo    │
│ 5V      ─────────── HC-SR04 VCC     │
│ GND     ─────────── Common Ground   │
└─────────────────────────────────────┘
```

## Voice Commands

| Command | Action |
|---------|--------|
| **"Hello Vision"** | Activate the system |
| **"Guide me"** | Start navigation mode |
| **"Stop guidance"** | Pause navigation |
| **"Read text"** | Read visible text (OCR) |
| **"Describe"** | Get full scene description |
| **"Chat"** | Enter conversation mode |
| **"System exit"** | Shutdown the device |

## Quick Start

### 1. Get OpenRouter API Key
Create or retrieve an API key from your OpenRouter account and keep it ready.

### 2. Setup (On Raspberry Pi)
```bash
git clone https://github.com/avishekkalsthoks/Assistive-device.git
cd Assistive-device
chmod +x setup_pi.sh
./setup_pi.sh
```

### 3. Configure
```bash
cp .env.example .env
nano .env # Add your OPENROUTER_API_KEY
```

### 4. Run
```bash
source venv/bin/activate
python main.py
```

## System Architecture

The project is designed as a **Voice-First** interface:
1. **User speaks** command ("Hello Vision")
2. **Pi Zero** captures image and sends to **Gemini API**
3. **Gemini** analyzes image (obstacles, text, etc.) and returns text
4. **Pi Zero** converts text to speech and plays audio

## License
MIT License