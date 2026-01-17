"""
GPIO Handler for Smart Vision Guide
Ultrasonic Sensor, Buzzer, and Button Control for Raspberry Pi Zero 2W

Note: This module uses lgpio which is designed for Raspberry Pi.
On non-Pi systems, it will run in simulation mode.
"""

import time
import threading

# Try to import lgpio, fall back to simulation mode if not available
try:
    import lgpio
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("lgpio not available - running in simulation mode")

from config.settings import (
    BUZZER_PIN, 
    ULTRASONIC_TRIG_PIN, 
    ULTRASONIC_ECHO_PIN,
    BUTTON_MAIN_PIN,
    BUTTON_GUIDE_PIN,
    OBSTACLE_DISTANCE_THRESHOLD,
    OBSTACLE_CRITICAL_DISTANCE
)


class GPIOHandler:
    """Handles GPIO operations for ultrasonic sensor, buzzer, and buttons."""
    
    def __init__(self):
        """Initialize GPIO handler."""
        self.gpio_handle = None
        self.initialized = False
        self.running = False
        self.distance_callback = None
        self.button_callback = None
        self.monitor_thread = None
        self.button_thread = None
        self.last_distance = None
    
    def initialize(self):
        """Initialize GPIO pins."""
        if not GPIO_AVAILABLE:
            print("GPIO simulation mode - no hardware control")
            self.initialized = True
            return True
        
        try:
            self.gpio_handle = lgpio.gpiochip_open(0)
            
            # Setup buzzer as output
            lgpio.gpio_claim_output(self.gpio_handle, BUZZER_PIN)
            
            # Setup ultrasonic sensor
            lgpio.gpio_claim_output(self.gpio_handle, ULTRASONIC_TRIG_PIN)
            lgpio.gpio_claim_input(self.gpio_handle, ULTRASONIC_ECHO_PIN)
            
            # Setup buttons as inputs with pull-up
            lgpio.gpio_claim_input(self.gpio_handle, BUTTON_MAIN_PIN, lgpio.SET_PULL_UP)
            lgpio.gpio_claim_input(self.gpio_handle, BUTTON_GUIDE_PIN, lgpio.SET_PULL_UP)
            
            # Ensure buzzer is off
            lgpio.gpio_write(self.gpio_handle, BUZZER_PIN, 0)
            
            self.initialized = True
            print("GPIO initialized successfully")
            return True
            
        except Exception as e:
            print(f"GPIO initialization error: {e}")
            self.initialized = False
            return False
    
    def measure_distance(self):
        """
        Measure distance using ultrasonic sensor.
        
        Returns:
            float: Distance in cm, or None if measurement failed
        """
        if not GPIO_AVAILABLE or not self.initialized:
            return None
        
        try:
            # Send trigger pulse
            lgpio.gpio_write(self.gpio_handle, ULTRASONIC_TRIG_PIN, 0)
            time.sleep(0.00001)
            lgpio.gpio_write(self.gpio_handle, ULTRASONIC_TRIG_PIN, 1)
            time.sleep(0.00001)
            lgpio.gpio_write(self.gpio_handle, ULTRASONIC_TRIG_PIN, 0)
            
            # Wait for echo
            timeout = time.time() + 0.1
            pulse_start = pulse_end = time.time()
            
            # Wait for echo to go high
            while lgpio.gpio_read(self.gpio_handle, ULTRASONIC_ECHO_PIN) == 0:
                pulse_start = time.time()
                if time.time() > timeout:
                    return None
            
            # Wait for echo to go low
            while lgpio.gpio_read(self.gpio_handle, ULTRASONIC_ECHO_PIN) == 1:
                pulse_end = time.time()
                if time.time() > timeout:
                    return None
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2  # Speed of sound = 343 m/s
            
            # Validate range (2cm - 400cm for HC-SR04)
            if 2 <= distance <= 400:
                self.last_distance = distance
                return distance
            
            return None
            
        except Exception as e:
            print(f"Distance measurement error: {e}")
            return None
    
    def read_button(self, pin):
        """
        Read button state.
        
        Args:
            pin: GPIO pin number
        
        Returns:
            bool: True if button is pressed (active low)
        """
        if not GPIO_AVAILABLE or not self.initialized:
            return False
        
        try:
            # Buttons are active low (pressed = 0)
            return lgpio.gpio_read(self.gpio_handle, pin) == 0
        except Exception as e:
            print(f"Button read error: {e}")
            return False
    
    def is_main_button_pressed(self):
        """Check if main button is pressed."""
        return self.read_button(BUTTON_MAIN_PIN)
    
    def is_guide_button_pressed(self):
        """Check if guide button is pressed."""
        return self.read_button(BUTTON_GUIDE_PIN)
    
    def beep(self, duration=0.1):
        """
        Sound the buzzer.
        
        Args:
            duration: Beep duration in seconds
        """
        if not GPIO_AVAILABLE or not self.initialized:
            print(f"[BEEP - {duration}s]")  # Simulation
            return
        
        try:
            lgpio.gpio_write(self.gpio_handle, BUZZER_PIN, 1)
            time.sleep(duration)
            lgpio.gpio_write(self.gpio_handle, BUZZER_PIN, 0)
        except Exception as e:
            print(f"Buzzer error: {e}")
    
    def beep_pattern(self, pattern):
        """
        Play a beep pattern.
        
        Args:
            pattern: List of (on_time, off_time) tuples
        """
        for on_time, off_time in pattern:
            self.beep(on_time)
            time.sleep(off_time)
    
    def beep_confirm(self):
        """Single short beep to confirm button press."""
        self.beep(0.05)
    
    def beep_error(self):
        """Double beep to indicate error."""
        self.beep_pattern([(0.1, 0.1), (0.1, 0)])
    
    def alert_by_distance(self, distance):
        """
        Sound alert based on distance.
        
        Args:
            distance: Distance in cm
        """
        if distance is None:
            return
        
        if distance < OBSTACLE_CRITICAL_DISTANCE:
            # Critical - rapid beeping
            self.beep(0.1)
            time.sleep(0.05)
            self.beep(0.1)
        elif distance < OBSTACLE_DISTANCE_THRESHOLD:
            # Warning - single beep
            self.beep(0.1)
    
    def start_distance_monitoring(self, callback=None, interval=0.2):
        """
        Start continuous distance monitoring.
        
        Args:
            callback: Function to call with distance
            interval: Measurement interval in seconds
        """
        self.running = True
        self.distance_callback = callback
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_loop(self, interval):
        """Distance monitoring loop."""
        while self.running:
            distance = self.measure_distance()
            
            if distance is not None and self.distance_callback:
                self.distance_callback(distance)
            
            time.sleep(interval)
    
    def start_button_monitoring(self, callback):
        """
        Start monitoring buttons for presses.
        
        Args:
            callback: Function to call with button name ("main" or "guide")
        """
        self.button_callback = callback
        self.running = True
        
        self.button_thread = threading.Thread(target=self._button_loop)
        self.button_thread.daemon = True
        self.button_thread.start()
        
        print("Button monitoring started")
    
    def _button_loop(self):
        """Button monitoring loop with debounce."""
        last_main_state = False
        last_guide_state = False
        last_main_press = 0
        last_guide_press = 0
        debounce_time = 0.3  # 300ms debounce
        
        while self.running:
            current_time = time.time()
            
            # Check main button
            main_pressed = self.is_main_button_pressed()
            if main_pressed and not last_main_state:
                if current_time - last_main_press > debounce_time:
                    self.beep_confirm()
                    if self.button_callback:
                        self.button_callback("main")
                    last_main_press = current_time
            last_main_state = main_pressed
            
            # Check guide button
            guide_pressed = self.is_guide_button_pressed()
            if guide_pressed and not last_guide_state:
                if current_time - last_guide_press > debounce_time:
                    self.beep_confirm()
                    if self.button_callback:
                        self.button_callback("guide")
                    last_guide_press = current_time
            last_guide_state = guide_pressed
            
            time.sleep(0.05)  # 50ms polling interval
    
    def stop_monitoring(self):
        """Stop all monitoring."""
        self.running = False
    
    def cleanup(self):
        """Clean up GPIO resources."""
        self.running = False
        
        if GPIO_AVAILABLE and self.gpio_handle is not None:
            try:
                lgpio.gpio_write(self.gpio_handle, BUZZER_PIN, 0)
                lgpio.gpiochip_close(self.gpio_handle)
            except Exception as e:
                print(f"GPIO cleanup error: {e}")
        
        self.initialized = False
        print("GPIO cleaned up")


# Singleton instance
_gpio_handler = None

def get_gpio_handler():
    """Get or create the singleton GPIO handler."""
    global _gpio_handler
    if _gpio_handler is None:
        _gpio_handler = GPIOHandler()
    return _gpio_handler
