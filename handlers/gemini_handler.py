"""
Gemini API Handler for Smart Vision Guide
Handles all communication with Google AI Studio
"""

import google.generativeai as genai
import cv2
from config.settings import GEMINI_API_KEY, GEMINI_MODEL, PROMPTS, JPEG_QUALITY


class GeminiHandler:
    """Handles all Gemini API interactions for image analysis."""
    
    def __init__(self):
        """Initialize the Gemini API client."""
        self.model = None
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Configure and initialize the Gemini model."""
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            self.initialized = True
            print(f"Gemini API initialized with model: {GEMINI_MODEL}")
        except Exception as e:
            print(f"Error initializing Gemini API: {e}")
            self.initialized = False
    
    def _encode_frame(self, frame):
        """Encode a frame as JPEG bytes."""
        try:
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            return buffer.tobytes()
        except Exception as e:
            print(f"Error encoding frame: {e}")
            return None
    
    def analyze_image(self, frame, mode="navigation"):
        """
        Analyze an image using the Gemini API.
        
        Args:
            frame: OpenCV image frame (numpy array)
            mode: Type of analysis - "navigation", "ocr", "describe", "chat"
        
        Returns:
            str: Analysis result text
        """
        if not self.initialized:
            return "Vision system not available. Please check API configuration."
        
        if frame is None:
            return "No image captured."
        
        # Get the appropriate prompt
        prompt = PROMPTS.get(mode, PROMPTS["navigation"])
        
        # Encode frame
        image_bytes = self._encode_frame(frame)
        if image_bytes is None:
            return "Error processing image."
        
        try:
            # Create content with image
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                }
            ])
            
            # Extract and clean the response text
            result = response.text.strip()
            
            # Remove any markdown or special formatting
            result = result.replace('*', '').replace('#', '').replace('`', '')
            
            return result
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "Sorry, I couldn't analyze the scene. Please try again."
    
    def chat(self, user_message, context_frame=None):
        """
        Handle a chat conversation, optionally with image context.
        
        Args:
            user_message: The user's question or statement
            context_frame: Optional image for context
        
        Returns:
            str: Chat response
        """
        if not self.initialized:
            return "Chat system not available."
        
        try:
            prompt = f"{PROMPTS['chat']}\n\nUser says: {user_message}"
            
            if context_frame is not None:
                image_bytes = self._encode_frame(context_frame)
                if image_bytes:
                    response = self.model.generate_content([
                        prompt,
                        {
                            "mime_type": "image/jpeg",
                            "data": image_bytes
                        }
                    ])
                else:
                    response = self.model.generate_content(prompt)
            else:
                response = self.model.generate_content(prompt)
            
            result = response.text.strip()
            result = result.replace('*', '').replace('#', '').replace('`', '')
            
            return result
            
        except Exception as e:
            print(f"Chat error: {e}")
            return "Sorry, I couldn't process that. Please try again."
    
    def get_navigation_guidance(self, frame):
        """Get navigation guidance for obstacle avoidance."""
        return self.analyze_image(frame, "navigation")
    
    def read_text(self, frame):
        """Read text from an image (OCR)."""
        return self.analyze_image(frame, "ocr")
    
    def describe_scene(self, frame):
        """Get a complete scene description."""
        return self.analyze_image(frame, "describe")


# Singleton instance
_gemini_handler = None

def get_gemini_handler():
    """Get or create the singleton Gemini handler."""
    global _gemini_handler
    if _gemini_handler is None:
        _gemini_handler = GeminiHandler()
    return _gemini_handler
