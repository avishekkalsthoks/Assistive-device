"""
Vision Handler for Smart Vision Guide
Version: 3.0 (OpenRouter HTTP implementation)
"""

import requests
import json
import base64
import cv2
from config.settings import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_URL, PROMPTS, JPEG_QUALITY

class GeminiHandler:
    """Handles vision API interactions via OpenRouter."""
    
    def __init__(self):
        """Initialize the handler."""
        self.api_key = OPENROUTER_API_KEY
        self.url = OPENROUTER_URL
        self.model = OPENROUTER_MODEL
        self.initialized = True if self.api_key and "your-openrouter" not in self.api_key else False
        
        if self.initialized:
            print(f"OpenRouter Handler initialized with model: {self.model}")
        else:
            print("Warning: OpenRouter API Key missing or invalid.")

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
        """Analyze an image using the OpenRouter API."""
        if not self.initialized:
            return "Vision system not available. Please check API configuration."
        
        if frame is None:
            return "No image captured."

        prompt = PROMPTS.get(mode, PROMPTS["navigation"])
        image_base64 = self._encode_frame(frame)
        
        if not image_base64:
            return "Error processing image."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/avishekkalsthoks/Smart-Vision-Guide",
            "X-Title": "Smart Vision Guide",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract text from OpenRouter response
            result = data['choices'][0]['message']['content'].strip()
            
            # Clean formatting
            result = result.replace('*', '').replace('#', '').replace('`', '')
            return result
            
        except Exception as e:
            print(f"OpenRouter API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return "I couldn't reach the vision server. Please check your connection."

    def chat(self, user_message, context_frame=None):
        """Handle a chat conversation via OpenRouter."""
        if not self.initialized:
            return "Chat system not available."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/avishekkalsthoks/Smart-Vision-Guide",
            "X-Title": "Smart Vision Guide",
        }
        
        content = [{"type": "text", "text": f"{PROMPTS['chat']}\n\nUser says: {user_message}"}]
        
        if context_frame is not None:
            image_base64 = self._encode_frame(context_frame)
            if image_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                })

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}]
        }

        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status()
            data = response.json()
            result = data['choices'][0]['message']['content'].strip()
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
