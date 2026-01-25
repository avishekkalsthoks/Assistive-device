"""
Gemini API Handler for Smart Vision Guide
Version: 2.0 (Lightweight HTTP implementation for Python 3.7+)
"""

import requests
import json
import base64
import cv2
from config.settings import GEMINI_API_KEY, GEMINI_MODEL, PROMPTS, JPEG_QUALITY

class GeminiHandler:
    """Handles all Gemini API interactions via direct HTTP requests."""
    
    def __init__(self):
        """Initialize the Gemini handler."""
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self.initialized = True if self.api_key and self.api_key != "your-api-key-here" else False
        
        if self.initialized:
            print(f"Gemini Handler (HTTP) initialized with model: {self.model}")
        else:
            print("Warning: Gemini API Key missing or invalid.")

    def _encode_frame(self, frame):
        """Encode a frame as JPEG bytes then Base64 string."""
        try:
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            print(f"Error encoding frame: {e}")
            return None

    def analyze_image(self, frame, mode="navigation"):
        """Analyze an image using the Gemini REST API."""
        if not self.initialized:
            return "Vision system not available. Please check API configuration."
        
        if frame is None:
            return "No image captured."

        prompt = PROMPTS.get(mode, PROMPTS["navigation"])
        image_base64 = self._encode_frame(frame)
        
        if not image_base64:
            return "Error processing image."

        # Gemini API Endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }]
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract text from response
            result = data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Clean formatting
            result = result.replace('*', '').replace('#', '').replace('`', '')
            return result
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "Camera analyzed the scene, but I couldn't process the result. Check your connection."

    def chat(self, user_message, context_frame=None):
        """Handle a chat conversation via REST API."""
        if not self.initialized:
            return "Chat system not available."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        parts = [{"text": f"{PROMPTS['chat']}\n\nUser says: {user_message}"}]
        
        if context_frame is not None:
            image_base64 = self._encode_frame(context_frame)
            if image_base64:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_base64
                    }
                })

        payload = {"contents": [{"parts": parts}]}

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            result = data['candidates'][0]['content']['parts'][0]['text'].strip()
            return result.replace('*', '').replace('#', '').replace('`', '')
        except Exception as e:
            print(f"Chat error: {e}")
            return "Sorry, I couldn't process that question."

    def get_navigation_guidance(self, frame):
        return self.analyze_image(frame, "navigation")
    
    def read_text(self, frame):
        return self.analyze_image(frame, "ocr")
    
    def describe_scene(self, frame):
        return self.analyze_image(frame, "describe")

# Singleton instance
_gemini_handler = None

def get_gemini_handler():
    global _gemini_handler
    if _gemini_handler is None:
        _gemini_handler = GeminiHandler()
    return _gemini_handler
