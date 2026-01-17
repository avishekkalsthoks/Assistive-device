"""
Voice Recognition Handler for Smart Vision Guide
Uses Google Speech-to-Text for voice command recognition
"""

import speech_recognition as sr
import threading
import time
from config.settings import COMMANDS


class VoiceHandler:
    """Handles voice recognition and command parsing."""
    
    def __init__(self):
        """Initialize voice handler."""
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.running = False
        self.callback = None
        self.listen_thread = None
        
        # Adjust recognizer settings for Pi Zero 2W
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def initialize_microphone(self, device_index=None):
        """
        Initialize the microphone.
        
        Args:
            device_index: Specific microphone index, or None for default
        
        Returns:
            bool: True if successful
        """
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            
            # Adjust for ambient noise
            with self.microphone as source:
                print("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("Microphone initialized successfully")
            return True
            
        except Exception as e:
            print(f"Microphone error: {e}")
            return False
    
    def parse_command(self, transcript):
        """
        Parse a transcript to identify commands.
        
        Args:
            transcript: Raw speech transcript
        
        Returns:
            tuple: (command_type, transcript) or (None, transcript)
        """
        transcript_lower = transcript.lower().strip()
        
        for command_type, phrases in COMMANDS.items():
            for phrase in phrases:
                if phrase in transcript_lower:
                    return (command_type, transcript)
        
        return (None, transcript)
    
    def listen_once(self, timeout=5):
        """
        Listen for a single voice input.
        
        Args:
            timeout: Maximum time to wait for speech
        
        Returns:
            str: Recognized text, or None if failed
        """
        if self.microphone is None:
            if not self.initialize_microphone():
                return None
        
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Recognize speech using Google
            text = self.recognizer.recognize_google(audio)
            print(f"Heard: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"Voice error: {e}")
            return None
    
    def start_continuous_listening(self, callback):
        """
        Start continuous voice recognition in background.
        
        Args:
            callback: Function to call with (command_type, transcript)
        """
        self.callback = callback
        self.running = True
        
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        print("Continuous listening started")
    
    def _listen_loop(self):
        """Background listening loop."""
        if self.microphone is None:
            if not self.initialize_microphone():
                print("Could not initialize microphone for continuous listening")
                return
        
        while self.running:
            try:
                with self.microphone as source:
                    self.is_listening = True
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
                    self.is_listening = False
                
                # Recognize in a separate thread to not block
                threading.Thread(
                    target=self._process_audio,
                    args=(audio,),
                    daemon=True
                ).start()
                
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Listen loop error: {e}")
                time.sleep(1)
        
        self.is_listening = False
    
    def _process_audio(self, audio):
        """Process recorded audio."""
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"Heard: {text}")
            
            command_type, transcript = self.parse_command(text)
            
            if self.callback:
                self.callback(command_type, transcript)
                
        except sr.UnknownValueError:
            pass  # Could not understand
        except sr.RequestError as e:
            print(f"Recognition request error: {e}")
        except Exception as e:
            print(f"Audio processing error: {e}")
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.running = False
        self.is_listening = False
        print("Voice recognition stopped")


# Singleton instance
_voice_handler = None

def get_voice_handler():
    """Get or create the singleton voice handler."""
    global _voice_handler
    if _voice_handler is None:
        _voice_handler = VoiceHandler()
    return _voice_handler
