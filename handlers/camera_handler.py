"""
Camera Handler for Smart Vision Guide
Optimized for Raspberry Pi Zero 2W with low memory footprint
"""

import cv2
import time
from config.settings import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT


class CameraHandler:
    """Handles camera capture with memory optimization for Pi Zero 2W."""
    
    def __init__(self):
        """Initialize camera handler."""
        self.camera_index = CAMERA_INDEX
        self.width = CAMERA_WIDTH
        self.height = CAMERA_HEIGHT
        self.last_frame = None
        self.last_capture_time = 0
    
    def capture_frame(self):
        """
        Capture a single frame from the camera.
        Opens and closes camera for each capture to save memory.
        
        Returns:
            numpy.ndarray: Captured frame, or None if capture failed
        """
        cap = None
        try:
            cap = cv2.VideoCapture(self.camera_index)
            
            if not cap.isOpened():
                print("Error: Could not open camera")
                return None
            
            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Capture frame
            ret, frame = cap.read()
            
            if ret and frame is not None:
                self.last_frame = frame
                self.last_capture_time = time.time()
                return frame
            else:
                print("Error: Could not read frame")
                return None
                
        except Exception as e:
            print(f"Camera error: {e}")
            return None
            
        finally:
            if cap is not None:
                cap.release()
    
    def get_last_frame(self):
        """
        Get the last captured frame if recent enough.
        
        Returns:
            numpy.ndarray: Last frame if within 5 seconds, else None
        """
        if self.last_frame is not None:
            if time.time() - self.last_capture_time < 5.0:
                return self.last_frame
        return None
    
    def test_camera(self):
        """
        Test if the camera is working.
        
        Returns:
            bool: True if camera works, False otherwise
        """
        frame = self.capture_frame()
        return frame is not None


# Singleton instance
_camera_handler = None

def get_camera_handler():
    """Get or create the singleton camera handler."""
    global _camera_handler
    if _camera_handler is None:
        _camera_handler = CameraHandler()
    return _camera_handler
