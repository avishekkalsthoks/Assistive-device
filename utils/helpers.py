"""
Utility helpers for Smart Vision Guide
"""

import time


def debounce(wait_time):
    """
    Decorator to debounce a function.
    
    Args:
        wait_time: Minimum time between calls in seconds
    """
    def decorator(func):
        last_called = [0]
        
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - last_called[0] >= wait_time:
                last_called[0] = current_time
                return func(*args, **kwargs)
            return None
        
        return wrapper
    return decorator


def rate_limit(calls_per_second):
    """
    Decorator to rate limit a function.
    
    Args:
        calls_per_second: Maximum calls per second
    """
    min_interval = 1.0 / calls_per_second
    
    def decorator(func):
        last_called = [0]
        
        def wrapper(*args, **kwargs):
            current_time = time.time()
            elapsed = current_time - last_called[0]
            
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            last_called[0] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def retry(max_attempts=3, delay=1.0):
    """
    Decorator to retry a function on failure.
    
    Args:
        max_attempts: Maximum retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


def format_distance(distance_cm):
    """
    Format distance for speech output.
    
    Args:
        distance_cm: Distance in centimeters
    
    Returns:
        str: Formatted distance string
    """
    if distance_cm is None:
        return "unknown distance"
    
    if distance_cm < 100:
        return f"{int(distance_cm)} centimeters"
    else:
        meters = distance_cm / 100
        return f"{meters:.1f} meters"


def clean_text_for_speech(text):
    """
    Clean text for text-to-speech output.
    
    Args:
        text: Raw text
    
    Returns:
        str: Cleaned text suitable for TTS
    """
    if not text:
        return ""
    
    # Remove markdown formatting
    text = text.replace('*', '')
    text = text.replace('#', '')
    text = text.replace('`', '')
    text = text.replace('_', ' ')
    
    # Remove multiple spaces
    while '  ' in text:
        text = text.replace('  ', ' ')
    
    return text.strip()
