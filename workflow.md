# Smart Vision Guide — Workflow

Purpose
-------
- Assist visually impaired users by capturing camera frames, sending them to a cloud LLM/vision API (OpenRouter/Gemini replacement), and returning concise spoken guidance, OCR, or scene descriptions.

Core Components
---------------
- `main.py`: Application lifecycle, threads, event flags, command dispatch.
- `handlers/camera_handler.py`: Opens/releases camera for each capture, returns frames (640x480 by default).
- `handlers/voice_handler.py`: Uses `speech_recognition` (Google STT) for continuous listening and command parsing.
- `handlers/audio_handler.py`: Uses `gTTS` to generate MP3 and plays via system player (`mpg123`/`aplay`/`ffplay`).
- `handlers/gemini_handler.py`: Encodes frames to JPEG, converts to data-URI, posts to OpenRouter chat completions, parses text responses.
- `utils/helpers.py` and `config/settings.py`: Utility decorators, configuration values, prompts and command mappings.

High-level Data Flow (Molecular)
--------------------------------
- Startup
  - `main.py` constructs `SmartVisionGuide` → creates singletons via `get_*_handler()` for audio, camera, gemini (OpenRouter), voice.
  - `run()` sets `events['running']` and calls `initialize()` which tests camera, initializes microphone, and checks OpenRouter reachability.

- Voice → Command dispatch
  - `VoiceHandler` runs a background listening loop, records audio segments, uses Google STT to transcribe, then `parse_command()` matches phrases in `COMMANDS` and calls `SmartVisionGuide.handle_voice_command(command_type, transcript)`.

- Activation gating
  - Wake word (`"hi siri"`) toggles `system_active`; other commands are ignored until activation.

- Modes
  - Guidance: `start_guidance()` spawns `_guidance_loop()` that repeatedly captures frames, calls `GeminiHandler.get_navigation_guidance(frame)`, and speaks concise navigation advice. The loop respects `CAPTURE_INTERVAL` and checks events for quick stop.
  - OCR/Describe: `read_text()` and `describe_scene()` capture a single frame, call the appropriate `gemini` method, and speak the result.
  - Chat: `start_chat()` enables conversational mode; non-command transcripts get passed to `gemini.chat(text, context_frame)` which may include a context image.

- TTS pipeline
  - `AudioHandler` uses `gTTS` to create a temporary MP3 file, selects an available system audio player, spawns playback as a subprocess, and supports interruption.

- Gemini/OpenRouter pipeline
  - `GeminiHandler` encodes frames as JPEG (`JPEG_QUALITY`), base64-encodes into a data-URI, sends a JSON payload to `OPENROUTER_URL` with `OPENROUTER_MODEL`, and extracts text from the response.

Threads & Synchronization
-------------------------
- `threading.Event` objects coordinate `running`, `guidance`, and `chat` background threads.
- Voice loop spawns worker threads for recognition to keep the microphone loop responsive.
- Guidance loop runs as a daemon thread; main thread sleeps in a loop and shuts down gracefully on signals.

Raspberry Pi (Zero 2W) Considerations
--------------------------------------
- Memory & CPU constraints: camera opened/released per-capture, reduced resolution (640x480), `JPEG_QUALITY=70`, and `CAPTURE_INTERVAL=3.0s` to lower CPU/network usage.
- Heavy visual/LLM work is offloaded to OpenRouter/Gemini to avoid on-device inference.
- `gTTS` (cloud TTS) and Google STT require internet connectivity.

Hardware & OS Mapping
---------------------
- Camera: USB webcam or Pi Camera (CSI). Ensure drivers and v4l2 support are enabled.
- Microphone: USB microphone or audio HAT. `speech_recognition` typically requires PortAudio/PyAudio.
- Speaker: 3.5mm or USB DAC; install `mpg123` or another player.
- OS: Raspberry Pi OS (Lite recommended). Enable camera/microphone in system settings.

Dependencies & System Packages
-----------------------------
- Python packages (virtualenv recommended): `opencv-python` (or headless), `speech_recognition`, `pyaudio` (or system PortAudio), `gTTS`, `requests`, `python-dotenv`.
- System packages: `mpg123` or `ffmpeg`, `portaudio19-dev`, and libraries required to build OpenCV if needed.

Common Failure Modes & Mitigation
---------------------------------
- No internet: STT and OpenRouter calls fail — consider offline alternatives like Vosk (STT) and offline TTS (`espeak`, `pico2wave`).
- Camera failure: `camera.test_camera()` will fail — check connections and device index.
- Missing audio player: `AudioHandler` will print a warning; install `mpg123` or `ffmpeg`.

Practical Deployment Steps
--------------------------
Run these on the Pi to prepare the environment and run the app (inspect `setup_pi.sh` first):

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip mpg123 libatlas-base-dev portaudio19-dev ffmpeg
python3 -m venv svg-venv
source svg-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Set environment variables in a .env file (OPENROUTER_API_KEY, etc.)
python3 main.py
```

Performance Tuning Recommendations
----------------------------------
- Increase `CAPTURE_INTERVAL` to 5–10s to save bandwidth/CPU.
- Reduce `CAMERA_WIDTH`/`CAMERA_HEIGHT` to 320x240 for faster encoding and upload.
- Replace `gTTS` with `espeak` or `pico2wave` for offline TTS and lower latency.
- Use Vosk or other offline STT to avoid Google STT network dependency.

Security & Keys
---------------
- Keep `OPENROUTER_API_KEY` (and any other API keys) in a `.env` file and do not commit them to source control.

Next Steps
----------
- I can: generate a Pi install script tailored to `requirements.txt`, swap `gTTS` for offline TTS, or convert STT to an offline engine like Vosk. Tell me which action you want next.
