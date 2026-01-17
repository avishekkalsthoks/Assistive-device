"""
Audio Handler for Smart Vision Guide
Text-to-Speech and Audio Playback
"""

import os
import subprocess
import threading
from gtts import gTTS
from config.settings import TTS_LANGUAGE, TTS_SLOW, AUDIO_TEMP_FILE


class AudioHandler:
    """Handles text-to-speech and audio playback."""
    
    def __init__(self):
        """Initialize audio handler."""
        self.is_speaking = False
        self.current_process = None
        self.interrupt_flag = threading.Event()
    
    def speak(self, text, block=True):
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
            block: If True, wait for speech to complete
        """
        if not text or not text.strip():
            return
        
        # Clear interrupt flag
        self.interrupt_flag.clear()
        
        if block:
            self._speak_sync(text)
        else:
            thread = threading.Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_sync(self, text):
        """Synchronous speech output."""
        self.is_speaking = True
        
        try:
            # Generate speech
            tts = gTTS(text=text, lang=TTS_LANGUAGE, slow=TTS_SLOW)
            tts.save(AUDIO_TEMP_FILE)
            
            if not os.path.exists(AUDIO_TEMP_FILE):
                print("Error: TTS file not created")
                return
            
            # Play audio
            self.current_process = subprocess.Popen(
                ['mpg123', '-q', AUDIO_TEMP_FILE],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for playback with interrupt check
            while self.current_process.poll() is None:
                if self.interrupt_flag.is_set():
                    self.current_process.terminate()
                    break
                self.interrupt_flag.wait(timeout=0.05)
            
        except FileNotFoundError:
            # mpg123 not installed, try alternative
            print("mpg123 not found, trying alternative...")
            try:
                subprocess.run(['afplay', AUDIO_TEMP_FILE], check=True)
            except FileNotFoundError:
                print("No audio player found. Install mpg123.")
        except Exception as e:
            print(f"TTS error: {e}")
        finally:
            self.is_speaking = False
            self.current_process = None
            
            # Clean up temp file
            try:
                if os.path.exists(AUDIO_TEMP_FILE):
                    os.remove(AUDIO_TEMP_FILE)
            except Exception:
                pass
    
    def stop(self):
        """Stop current speech."""
        self.interrupt_flag.set()
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
        self.is_speaking = False
    
    def is_busy(self):
        """Check if currently speaking."""
        return self.is_speaking


# Singleton instance
_audio_handler = None

def get_audio_handler():
    """Get or create the singleton audio handler."""
    global _audio_handler
    if _audio_handler is None:
        _audio_handler = AudioHandler()
    return _audio_handler


def speak(text, block=True):
    """Convenience function for speaking text."""
    get_audio_handler().speak(text, block)
