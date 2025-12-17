#!/usr/bin/env python3
"""
Human Behavior Simulator for Anti-Detection
Implements sophisticated patterns to mimic human behavior
"""

import asyncio
import random
import time
import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)


class HumanBehaviorSimulator:
    """Advanced human behavior simulation to avoid detection"""
    
    def __init__(self, mode: str = "moderate"):
        """
        Initialize with behavior mode
        Modes: stealth, moderate, aggressive
        """
        self.mode = mode
        self.session_start = time.time()
        self.action_count = 0
        self.last_action_time = time.time()
        
        # Configure based on mode
        self.config = self._get_mode_config(mode)
        
        # Activity patterns (human circadian rhythm)
        self.active_hours = self.config['active_hours']
        self.break_intervals = self.config['break_intervals']
        self.typing_speed = self.config['typing_speed']  # chars per minute
        
        # Session tracking
        self.messages_read = 0
        self.files_downloaded = 0
        self.channels_joined = 0
        self.last_break_time = time.time()
        
    def _get_mode_config(self, mode: str) -> dict:
        """Get configuration based on mode"""
        configs = {
            'stealth': {
                'active_hours': (9, 23),  # 9 AM to 11 PM
                'break_intervals': (1800, 3600),  # 30-60 min breaks
                'typing_speed': (180, 300),  # 180-300 chars/min
                'min_delay': 2.0,
                'max_delay': 15.0,
                'jitter_range': (0.1, 2.0),
                'scroll_delay': (0.5, 3.0),
                'mouse_movement_probability': 0.3,
                'typo_probability': 0.05,
                'max_actions_per_minute': 10,
                'daily_limit': 500  # max actions per day
            },
            'moderate': {
                'active_hours': (8, 24),  # 8 AM to midnight
                'break_intervals': (900, 2400),  # 15-40 min breaks
                'typing_speed': (200, 400),
                'min_delay': 1.0,
                'max_delay': 8.0,
                'jitter_range': (0.05, 1.0),
                'scroll_delay': (0.3, 2.0),
                'mouse_movement_probability': 0.2,
                'typo_probability': 0.03,
                'max_actions_per_minute': 20,
                'daily_limit': 1000
            },
            'aggressive': {
                'active_hours': (0, 24),  # 24/7
                'break_intervals': (300, 900),  # 5-15 min breaks
                'typing_speed': (300, 600),
                'min_delay': 0.5,
                'max_delay': 3.0,
                'jitter_range': (0.01, 0.5),
                'scroll_delay': (0.1, 1.0),
                'mouse_movement_probability': 0.1,
                'typo_probability': 0.01,
                'max_actions_per_minute': 40,
                'daily_limit': 5000
            }
        }
        return configs.get(mode, configs['moderate'])
    
    async def human_delay(self, 
                         min_seconds: Optional[float] = None,
                         max_seconds: Optional[float] = None,
                         action_type: str = "generic") -> None:
        """
        Apply human-like delay with various factors
        """
        # Use config defaults if not specified
        if min_seconds is None:
            min_seconds = self.config['min_delay']
        if max_seconds is None:
            max_seconds = self.config['max_delay']
        
        # Base delay with Gaussian distribution (more human-like than uniform)
        mean_delay = (min_seconds + max_seconds) / 2
        std_dev = (max_seconds - min_seconds) / 6  # 99.7% within range
        delay = np.random.normal(mean_delay, std_dev)
        delay = max(min_seconds, min(max_seconds, delay))  # Clamp to range
        
        # Add factors based on action type
        factors = {
            'read_message': 1.0,
            'scroll': 0.5,
            'type': 0.3,
            'click': 0.2,
            'download': 1.5,
            'join_channel': 2.0,
            'search': 1.2,
            'think': 1.8  # Simulating thinking/decision time
        }
        delay *= factors.get(action_type, 1.0)
        
        # Fatigue simulation (slower over time)
        session_duration = (time.time() - self.session_start) / 3600  # hours
        fatigue_factor = 1.0 + (session_duration * 0.1)  # 10% slower per hour
        delay *= fatigue_factor
        
        # Time of day factor (slower late at night)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            delay *= 1.3  # 30% slower late night/early morning
        
        # Add micro-jitter (human reaction time variation)
        jitter_min, jitter_max = self.config['jitter_range']
        jitter = random.uniform(jitter_min, jitter_max)
        delay += jitter
        
        # Rate limiting check
        self._check_rate_limits()
        
        # Update tracking
        self.action_count += 1
        self.last_action_time = time.time()
        
        # Apply the delay
        await asyncio.sleep(delay)
        
        # Randomly add mouse movement or scroll
        if random.random() < self.config['mouse_movement_probability']:
            await self._simulate_mouse_movement()
        
        # Check if break needed
        await self._check_break_needed()
    
    async def simulate_reading(self, text_length: int) -> None:
        """Simulate reading text based on length"""
        # Average reading speed: 200-300 words per minute
        # Assuming average word length of 5 characters
        words = text_length / 5
        reading_speed = random.uniform(200, 300)  # words per minute
        reading_time = (words / reading_speed) * 60  # seconds
        
        # Add variation for skimming vs careful reading
        if text_length < 100:
            reading_time *= 0.5  # Quick glance
        elif text_length > 1000:
            reading_time *= 0.7  # Skimming long text
        
        # Apply with some randomness
        reading_time *= random.uniform(0.8, 1.2)
        
        await asyncio.sleep(reading_time)
        self.messages_read += 1
    
    async def simulate_typing(self, text: str, with_corrections: bool = True) -> str:
        """
        Simulate human typing with optional typos and corrections
        Returns potentially modified text with typos
        """
        chars_per_min = random.uniform(*self.config['typing_speed'])
        chars_per_sec = chars_per_min / 60
        
        typed_text = []
        
        for char in text:
            # Typing delay per character
            char_delay = 1 / chars_per_sec
            char_delay *= random.uniform(0.5, 1.5)  # Variation
            
            # Occasionally make typos
            if with_corrections and random.random() < self.config['typo_probability']:
                # Common typo patterns
                typo_patterns = [
                    (char, char + char),  # Double character
                    (char, ''),  # Missing character
                    (char, self._get_nearby_key(char))  # Wrong key
                ]
                typo_char, correction = random.choice(typo_patterns)
                
                # Type the typo
                typed_text.append(typo_char)
                await asyncio.sleep(char_delay)
                
                # Realize mistake and backspace
                await asyncio.sleep(random.uniform(0.2, 0.8))
                if typo_char:
                    typed_text.pop()
                
                # Type correction
                typed_text.append(char)
                await asyncio.sleep(char_delay)
            else:
                typed_text.append(char)
                await asyncio.sleep(char_delay)
            
            # Occasional pauses (thinking)
            if char in '.,!?\n':
                await asyncio.sleep(random.uniform(0.3, 1.0))
        
        return ''.join(typed_text)
    
    def _get_nearby_key(self, char: str) -> str:
        """Get a nearby key on QWERTY keyboard (common typo)"""
        keyboard_layout = {
            'q': 'wa', 'w': 'qeas', 'e': 'wrd', 'r': 'etf', 't': 'ryg',
            'y': 'tuh', 'u': 'yij', 'i': 'uok', 'o': 'ipl', 'p': 'ol',
            'a': 'qwsz', 's': 'awedx', 'd': 'serfx', 'f': 'drtgc',
            'g': 'ftyhv', 'h': 'gyujb', 'j': 'huikn', 'k': 'jiolm',
            'l': 'kop', 'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb',
            'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
        }
        
        char_lower = char.lower()
        if char_lower in keyboard_layout:
            nearby = keyboard_layout[char_lower]
            return random.choice(nearby)
        return char
    
    async def _simulate_mouse_movement(self) -> None:
        """Simulate random mouse movement"""
        # Random pause as if moving mouse
        await asyncio.sleep(random.uniform(0.1, 0.5))
    
    async def _simulate_scroll(self) -> None:
        """Simulate scrolling behavior"""
        scroll_delay = random.uniform(*self.config['scroll_delay'])
        await asyncio.sleep(scroll_delay)
    
    def _check_rate_limits(self) -> None:
        """Check if we're acting too fast"""
        current_time = time.time()
        time_since_last = current_time - self.last_action_time
        
        # If acting too fast, add extra delay
        min_interval = 60 / self.config['max_actions_per_minute']
        if time_since_last < min_interval:
            extra_delay = min_interval - time_since_last
            time.sleep(extra_delay)
    
    async def _check_break_needed(self) -> None:
        """Check if it's time for a break (human pattern)"""
        current_time = time.time()
        time_since_break = current_time - self.last_break_time
        
        min_break, max_break = self.config['break_intervals']
        break_interval = random.uniform(min_break, max_break)
        
        if time_since_break > break_interval:
            # Take a break
            break_duration = random.uniform(60, 300)  # 1-5 minutes
            logger.info(f"Taking a {break_duration:.0f} second break (human simulation)")
            await asyncio.sleep(break_duration)
            self.last_break_time = current_time
    
    def should_be_active(self) -> bool:
        """Check if we should be active based on time of day"""
        current_hour = datetime.now().hour
        min_hour, max_hour = self.config['active_hours']
        
        if min_hour <= current_hour < max_hour:
            # Random chance of being active (not always on)
            return random.random() < 0.9
        return False
    
    async def simulate_session_start(self) -> None:
        """Simulate starting a new session"""
        # Gradual ramp-up (not instant activity)
        logger.info("Starting session with gradual ramp-up")
        
        # Initial delay (opening app, waiting to load)
        await asyncio.sleep(random.uniform(3, 10))
        
        # Gradual activity increase
        for i in range(3):
            await self.human_delay(
                min_seconds=2,
                max_seconds=5,
                action_type='think'
            )
    
    async def simulate_session_end(self) -> None:
        """Simulate ending a session"""
        # Gradual slow-down
        logger.info("Ending session with gradual slow-down")
        
        for i in range(3):
            await self.human_delay(
                min_seconds=1,
                max_seconds=3,
                action_type='generic'
            )
    
    def get_stats(self) -> dict:
        """Get current session statistics"""
        session_duration = (time.time() - self.session_start) / 60  # minutes
        
        return {
            'mode': self.mode,
            'session_duration_minutes': round(session_duration, 2),
            'total_actions': self.action_count,
            'messages_read': self.messages_read,
            'files_downloaded': self.files_downloaded,
            'channels_joined': self.channels_joined,
            'actions_per_minute': round(self.action_count / max(session_duration, 1), 2)
        }
    
    async def wait_between_channels(self) -> None:
        """Special delay between joining channels"""
        # Humans don't instantly jump between channels
        base_delay = random.uniform(5, 30)
        
        # Add extra delay if we've joined many channels recently
        if self.channels_joined > 10:
            base_delay *= 1.5
        if self.channels_joined > 20:
            base_delay *= 2
        
        await asyncio.sleep(base_delay)
        self.channels_joined += 1
    
    async def wait_before_download(self, file_size_mb: float) -> None:
        """Delay before downloading based on file size"""
        # Humans evaluate files before downloading
        think_time = random.uniform(1, 5)
        
        # Larger files = more consideration
        if file_size_mb > 10:
            think_time *= 1.5
        if file_size_mb > 50:
            think_time *= 2
        
        await asyncio.sleep(think_time)
        self.files_downloaded += 1


def test_simulator():
    """Test the human behavior simulator"""
    import asyncio
    
    async def run_test():
        simulator = HumanBehaviorSimulator(mode='moderate')
        
        print("Testing human behavior simulator...")
        print(f"Mode: {simulator.mode}")
        
        # Test various actions
        print("\n1. Simulating session start...")
        await simulator.simulate_session_start()
        
        print("\n2. Simulating reading (100 chars)...")
        await simulator.simulate_reading(100)
        
        print("\n3. Simulating typing...")
        text = await simulator.simulate_typing("Hello world!", with_corrections=True)
        print(f"   Typed: {text}")
        
        print("\n4. Simulating channel join...")
        await simulator.wait_between_channels()
        
        print("\n5. Simulating file download consideration (5MB)...")
        await simulator.wait_before_download(5.0)
        
        print("\n6. Generic action with delay...")
        await simulator.human_delay(action_type='click')
        
        print("\nSession stats:")
        stats = simulator.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    asyncio.run(run_test())


if __name__ == "__main__":
    test_simulator()