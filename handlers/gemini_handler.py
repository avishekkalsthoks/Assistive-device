"""
OpenRouter-based handler (replaces previous Gemini client).

This handler encodes captured frames as JPEG, embeds them as data-URI
image payloads and calls the OpenRouter chat completions endpoint.
"""

import base64
import json
import requests
import cv2
from config.settings import OPENROUTER_API_KEY, OPENROUTER_URL, OPENROUTER_MODEL, PROMPTS, JPEG_QUALITY


class GeminiHandler:
    """Handler that talks to OpenRouter using the same interface as before."""

    def __init__(self):
        self.initialized = False
        self._initialize()

    def _initialize(self):
        if not OPENROUTER_API_KEY or 'your-openrouter' in OPENROUTER_API_KEY:
            print("OpenRouter API key not configured. Set OPENROUTER_API_KEY in .env.")
            self.initialized = False
            return

        # Quick connectivity check (non-blocking failure handled)
        try:
            resp = requests.options(OPENROUTER_URL, timeout=3)
            if resp.status_code in (200, 204, 400, 401):
                self.initialized = True
                print(f"OpenRouter endpoint reachable: {OPENROUTER_URL}")
            else:
                print(f"OpenRouter endpoint check returned: {resp.status_code}")
                self.initialized = True
        except Exception as e:
            print(f"OpenRouter initialization warning: {e}")
            # Still allow runtime attempts
            self.initialized = True

    def _encode_frame(self, frame):
        try:
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            return buffer.tobytes()
        except Exception as e:
            print(f"Error encoding frame: {e}")
            return None

    def _frame_to_data_uri(self, jpeg_bytes):
        try:
            b64 = base64.b64encode(jpeg_bytes).decode('ascii')
            return f"data:image/jpeg;base64,{b64}"
        except Exception as e:
            print(f"Error encoding image to data URI: {e}")
            return None

    def _post_chat(self, prompt, image_data_uri=None):
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json'
        }

        # Build message content (text + optional image)
        content = [
            {
                'type': 'text',
                'text': prompt
            }
        ]

        if image_data_uri:
            content.append({
                'type': 'image_url',
                'image_url': {'url': image_data_uri}
            })

        payload = {
            'model': OPENROUTER_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': content
                }
            ]
        }

        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"OpenRouter request error: {e}")
            return None

    def _extract_text_from_response(self, resp_json):
        if not resp_json:
            return None

        # Try common OpenRouter response shapes
        try:
            choices = resp_json.get('choices') if isinstance(resp_json, dict) else None
            if choices and len(choices) > 0:
                for choice in choices:
                    message = choice.get('message') or {}
                    content = message.get('content') if isinstance(message, dict) else None
                    if isinstance(content, list):
                        # Look for first text-like content
                        for item in content:
                            if item.get('type') in ('output_text', 'text'):
                                txt = item.get('text') or item.get('content')
                                if txt:
                                    return txt.strip()
                        # Fallback: some APIs put text directly
                        first = content[0]
                        if isinstance(first, dict):
                            txt = first.get('text') or first.get('content')
                            if txt:
                                return txt.strip()

            # Some responses return a top-level 'output' or 'result'
            if isinstance(resp_json, dict):
                if 'output' in resp_json:
                    out = resp_json['output']
                    if isinstance(out, str):
                        return out.strip()
                if 'result' in resp_json and isinstance(resp_json['result'], str):
                    return resp_json['result'].strip()

        except Exception as e:
            print(f"Error parsing OpenRouter response: {e}")

        return None

    def analyze_image(self, frame, mode="navigation"):
        if frame is None:
            return "No image captured."

        prompt = PROMPTS.get(mode, PROMPTS.get('navigation', 'Describe the image.'))

        jpeg = self._encode_frame(frame)
        if not jpeg:
            return "Error processing image."

        data_uri = self._frame_to_data_uri(jpeg)
        resp = self._post_chat(prompt, image_data_uri=data_uri)
        text = self._extract_text_from_response(resp)
        if not text:
            return "Sorry, I couldn't analyze the scene. Please try again."

        # Basic cleanup
        return text.replace('*', '').replace('#', '').replace('`', '')

    def chat(self, user_message, context_frame=None):
        prompt = f"{PROMPTS.get('chat')}\n\nUser says: {user_message}"

        data_uri = None
        if context_frame is not None:
            jpeg = self._encode_frame(context_frame)
            if jpeg:
                data_uri = self._frame_to_data_uri(jpeg)

        resp = self._post_chat(prompt, image_data_uri=data_uri)
        text = self._extract_text_from_response(resp)
        if not text:
            return "Sorry, I couldn't process that. Please try again."

        return text.replace('*', '').replace('#', '').replace('`', '')

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
