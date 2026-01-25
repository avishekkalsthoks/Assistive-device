"""
Configuration Settings for Smart Vision Guide
Raspberry Pi Zero 2W with OpenRouter API
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# GEMINI API CONFIGURATION
# =============================================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your-api-key-here")
GEMINI_MODEL = "gemini-2.0-flash"  # Fast and cost-effective model

# =============================================================================
# OpenRouter (replacement for Gemini in this project)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "your-openrouter-api-key-here")
OPENROUTER_URL = os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemma-3-4b-it:free")
# =============================================================================

# =============================================================================
# CAMERA CONFIGURATION
# =============================================================================
CAMERA_INDEX = 0  # Default camera
CAMERA_WIDTH = 640  # Reduced resolution for Pi Zero 2W
CAMERA_HEIGHT = 480
JPEG_QUALITY = 70  # Balance between quality and upload speed

# =============================================================================
# TIMING CONFIGURATION
# =============================================================================
CAPTURE_INTERVAL = 3.0  # Seconds between captures in guidance mode
OCR_DELAY = 0.5  # Delay before OCR capture after command
SPEECH_RATE = 1.0  # TTS speech rate



# =============================================================================
# VOICE COMMANDS
# =============================================================================
WAKE_WORD = "hello vision"
COMMANDS = {
    "activate": ["hello vision", "hey assistant", "hello"],
    "guide": ["guide me", "start guidance", "navigate", "help me walk"],
    "stop_guide": ["stop guidance", "stop guiding", "pause"],
    "read_text": ["read text", "read this", "what does it say", "ocr"],
    "describe": ["describe", "what is around", "what do you see", "scene"],
    "exit": ["system exit", "shutdown", "goodbye", "bye"],
    "chat": ["chat", "talk to me", "conversation"],
    "exit_chat": ["exit chat", "stop chat", "end conversation"],
}

# =============================================================================
# PROMPTS FOR GEMINI API
# =============================================================================
PROMPTS = {
    "navigation": """You are helping a visually impaired person navigate safely.
Analyze this image and describe:
1. Any obstacles or objects in their path (specify left, center, or right)
2. Brief navigation advice

Keep your response under 25 words, natural and suitable for text-to-speech.
Example: "Chair on your left. Clear path ahead. Continue straight."
Do not use special characters or formatting.""",

    "ocr": """Act as a text reading assistant for a blind person.
Read all visible text in this image and organize it into logical, coherent sentences.
1. First, identify what type of text this is (e.g., "This is a street sign", "This is a menu", "This is a product label", "This is a document")
2. Then read the text in a natural, organized way - don't just list random words, combine them into meaningful sentences
3. If text appears fragmented or scattered, arrange it logically based on context
4. If no text is visible, say "No text detected in view"

Keep the response clear and concise for text-to-speech. Avoid special characters or formatting.
Example: "This is a store sign. It says 'Fresh Bakery, Open Daily 7 AM to 9 PM'." """,

    "describe": """Act as a spatial awareness assistant for a blind person.
Describe the scene in 3 to 4 concise sentences:
1. Identify the general environment (e.g., "You are in a living room", "You are on a sidewalk")
2. Locate key objects or obstacles relative to the user's position using clock-face directions (e.g., "A table is directly in front of you at 12 o'clock", "A doorway is at your 2 o'clock", "A chair is on your left at 9 o'clock")
3. Mention any people present and their positions using the same clock-face system
4. Specifically warn about floor-level hazards like cables, bags, steps, or uneven surfaces

Focus ONLY on facts needed for safe navigation. Avoid visual adjectives like "beautiful", "bright", or "colorful".
Keep response under 50 words, natural for text-to-speech. No special characters or formatting.""",

    "chat": """You are a helpful assistant for a visually impaired person.
Answer their question naturally and concisely.
Keep responses under 50 words unless more detail is specifically requested.
Be warm, helpful, and encouraging."""
}

# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================
TTS_LANGUAGE = "en"
TTS_SLOW = False
AUDIO_TEMP_FILE = "/tmp/tts_output.mp3"

# =============================================================================
# SYSTEM MESSAGES
# =============================================================================
MESSAGES = {
    "startup": "Smart Vision Guide ready. Say 'Hello Vision' to begin.",
    "activated": "System activated. Say 'guide me' for navigation, or 'describe' for scene description.",
    "guidance_start": "Guidance mode started. I'll help you navigate.",
    "guidance_stop": "Guidance paused.",
    "chat_start": "Chat mode. Ask me anything. Say 'exit chat' when done.",
    "chat_end": "Chat ended. Returning to standby.",
    "shutdown": "System shutting down. Goodbye.",
    "error_camera": "Camera error. Please check the connection.",
    "error_api": "Could not reach the server. Please check your internet connection.",
    "no_text": "No text detected in view.",
    "obstacle_warning": "Warning! Obstacle very close ahead.",
    "button_pressed": "Button pressed.",
    "reading_text": "Reading text...",
    "analyzing": "Analyzing scene...",
}
