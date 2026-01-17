#!/usr/bin/env python3
"""
Smart Vision Guide - Main Application
Assistive Device for Visually Impaired People
Optimized for Raspberry Pi Zero 2W with Google AI Studio (Gemini API)

Features:
- Object Detection for navigation assistance
- OCR for reading text from signs, labels, etc.
- Voice-controlled operation
- Ultrasonic obstacle detection
- Text-to-speech output

Usage:
    python main.py

Voice Commands:
    "Hi Siri" - Activate the system
    "Guide me" - Start navigation mode
    "Stop guidance" - Pause navigation
    "Read text" - Read visible text (OCR)
    "Describe" - Get scene description
    "Chat" - Enter conversation mode
    "System exit" - Shutdown
"""

import threading
import time
import signal
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import MESSAGES, CAPTURE_INTERVAL
from handlers.audio_handler import get_audio_handler, speak
from handlers.camera_handler import get_camera_handler
from handlers.gemini_handler import get_gemini_handler
from handlers.voice_handler import get_voice_handler
from handlers.gpio_handler import get_gpio_handler


class SmartVisionGuide:
    """Main application controller for the Smart Vision Guide."""
    
    def __init__(self):
        """Initialize the Smart Vision Guide."""
        print("=" * 50)
        print("Smart Vision Guide - Raspberry Pi Zero 2W")
        print("=" * 50)
        
        # System state
        self.running = False
        self.system_active = False
        self.guidance_active = False
        self.chat_active = False
        
        # Threading events
        self.events = {
            'running': threading.Event(),
            'guidance': threading.Event(),
            'chat': threading.Event(),
        }
        
        # Initialize handlers
        self.audio = get_audio_handler()
        self.camera = get_camera_handler()
        self.gemini = get_gemini_handler()
        self.voice = get_voice_handler()
        self.gpio = get_gpio_handler()
        
        # Worker threads
        self.guidance_thread = None
        self.ultrasonic_thread = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\nReceived shutdown signal...")
        self.shutdown()
    
    def initialize(self):
        """Initialize all hardware and services."""
        print("\nInitializing components...")
        
        # Test camera
        print("  [1/4] Testing camera...")
        if self.camera.test_camera():
            print("        Camera OK")
        else:
            print("        Camera FAILED - check connection")
        
        # Initialize GPIO
        print("  [2/4] Initializing GPIO...")
        if self.gpio.initialize():
            print("        GPIO OK")
        else:
            print("        GPIO simulation mode")
        
        # Initialize voice
        print("  [3/4] Initializing microphone...")
        if self.voice.initialize_microphone():
            print("        Microphone OK")
        else:
            print("        Microphone FAILED - checking connection")
        
        # Check Gemini
        print("  [4/4] Checking Gemini API...")
        if self.gemini.initialized:
            print("        Gemini API OK")
        else:
            print("        Gemini API FAILED - check API key")
        
        print("\nInitialization complete!")
        print("-" * 50)
    
    def handle_voice_command(self, command_type, transcript):
        """
        Process voice commands.
        
        Args:
            command_type: Parsed command type or None
            transcript: Raw transcript text
        """
        print(f"Command: {command_type} | Text: {transcript}")
        
        # Handle activation
        if command_type == "activate":
            self.system_active = True
            speak(MESSAGES["activated"])
            return
        
        # Ignore commands if system not active (except activation)
        if not self.system_active:
            return
        
        # Handle each command type
        if command_type == "guide":
            self.start_guidance()
        
        elif command_type == "stop_guide":
            self.stop_guidance()
        
        elif command_type == "read_text":
            self.read_text()
        
        elif command_type == "describe":
            self.describe_scene()
        
        elif command_type == "chat":
            self.start_chat()
        
        elif command_type == "exit_chat":
            self.stop_chat()
        
        elif command_type == "exit":
            speak(MESSAGES["shutdown"])
            self.shutdown()
        
        # If in chat mode and no recognized command, treat as chat input
        elif self.chat_active and command_type is None:
            self.handle_chat_input(transcript)
    
    def start_guidance(self):
        """Start navigation guidance mode."""
        if self.events['guidance'].is_set():
            return  # Already running
        
        speak(MESSAGES["guidance_start"])
        self.events['guidance'].set()
        self.guidance_active = True
        
        # Start guidance thread
        self.guidance_thread = threading.Thread(target=self._guidance_loop)
        self.guidance_thread.daemon = True
        self.guidance_thread.start()
        
        # Start ultrasonic monitoring
        self.ultrasonic_thread = threading.Thread(target=self._ultrasonic_loop)
        self.ultrasonic_thread.daemon = True
        self.ultrasonic_thread.start()
    
    def stop_guidance(self):
        """Stop navigation guidance mode."""
        self.events['guidance'].clear()
        self.guidance_active = False
        speak(MESSAGES["guidance_stop"])
    
    def _guidance_loop(self):
        """Background loop for navigation guidance."""
        print("Guidance thread started")
        
        while self.events['running'].is_set() and self.events['guidance'].is_set():
            start_time = time.time()
            
            # Capture frame
            frame = self.camera.capture_frame()
            
            if frame is not None:
                # Get navigation guidance from Gemini
                result = self.gemini.get_navigation_guidance(frame)
                
                # Skip generic responses
                if result and "no obstacle" not in result.lower():
                    print(f"Navigation: {result}")
                    speak(result)
            else:
                print("Camera capture failed")
            
            # Maintain capture interval
            elapsed = time.time() - start_time
            sleep_time = max(CAPTURE_INTERVAL - elapsed, 0)
            
            # Sleep in small intervals to allow quick shutdown
            sleep_end = time.time() + sleep_time
            while time.time() < sleep_end and self.events['guidance'].is_set():
                time.sleep(0.1)
        
        print("Guidance thread stopped")
    
    def _ultrasonic_loop(self):
        """Background loop for ultrasonic obstacle detection."""
        print("Ultrasonic thread started")
        last_warning_time = 0
        
        while self.events['running'].is_set() and self.events['guidance'].is_set():
            distance = self.gpio.measure_distance()
            
            if distance is not None:
                # Beep based on distance
                self.gpio.alert_by_distance(distance)
                
                # Voice warning for very close obstacles (not too frequent)
                if distance < 20 and (time.time() - last_warning_time) > 3:
                    speak(MESSAGES["obstacle_warning"], block=False)
                    last_warning_time = time.time()
            
            time.sleep(0.2)  # 5 Hz measurement rate
        
        print("Ultrasonic thread stopped")
    
    def read_text(self):
        """Perform OCR on current view."""
        speak("Reading text...")
        
        frame = self.camera.capture_frame()
        
        if frame is not None:
            result = self.gemini.read_text(frame)
            print(f"OCR: {result}")
            speak(result)
        else:
            speak(MESSAGES["error_camera"])
    
    def describe_scene(self):
        """Get complete scene description."""
        speak("Analyzing scene...")
        
        frame = self.camera.capture_frame()
        
        if frame is not None:
            result = self.gemini.describe_scene(frame)
            print(f"Scene: {result}")
            speak(result)
        else:
            speak(MESSAGES["error_camera"])
    
    def start_chat(self):
        """Start conversation mode."""
        self.chat_active = True
        self.events['chat'].set()
        speak(MESSAGES["chat_start"])
    
    def stop_chat(self):
        """Stop conversation mode."""
        self.chat_active = False
        self.events['chat'].clear()
        speak(MESSAGES["chat_end"])
    
    def handle_chat_input(self, text):
        """Handle chat conversation."""
        # Optionally capture context image
        frame = self.camera.capture_frame()
        
        result = self.gemini.chat(text, context_frame=frame)
        print(f"Chat response: {result}")
        speak(result)
    
    def run(self):
        """Main application loop."""
        self.running = True
        self.events['running'].set()
        
        # Initialize
        self.initialize()
        
        # Startup announcement
        speak(MESSAGES["startup"])
        
        # Start voice recognition
        try:
            self.voice.start_continuous_listening(self.handle_voice_command)
        except Exception as e:
            print(f"Voice recognition not available: {e}")
            speak("Voice recognition failed. Check microphone.")
        
        print("\nSystem ready! Say 'Hi Siri' to activate.")
        print("-" * 50)
        
        try:
            # Main loop - keep running until shutdown
            while self.running and self.events['running'].is_set():
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of all resources."""
        print("\nShutting down...")
        
        self.running = False
        
        # Clear all events
        for event in self.events.values():
            event.clear()
        
        # Stop voice recognition
        self.voice.stop_listening()
        
        # Stop audio
        self.audio.stop()
        
        # Clean up GPIO
        self.gpio.cleanup()
        
        # Wait for threads to finish
        time.sleep(0.5)
        
        print("Shutdown complete. Goodbye!")
        sys.exit(0)


def main():
    """Entry point for Smart Vision Guide."""
    app = SmartVisionGuide()
    app.run()


if __name__ == "__main__":
    main()
