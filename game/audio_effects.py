"""
Sound and music management system.
Handles audio playback with adaptive music based on difficulty.
"""

import pygame
import os


class SoundManager:
    """
    Manages game audio including sound effects and music.
    Adapts music tempo/intensity based on difficulty and game state.
    """
    
    def __init__(self):
        """Initialize sound manager."""
        # Initialize mixer with better quality
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Sound effect placeholders
        self.sounds = {
            'jump': None,
            'coin': None,
            'enemy_hit': None,
            'enemy_defeat': None,
            'level_complete': None,
            'death': None
        }
        
        # Music tracks (placeholders)
        self.music_tracks = {
            'novice': None,
            'intermediate': None,
            'expert': None,
            'menu': None
        }
        
        # Current state
        self.current_track = None
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # Generate synthetic sounds
        self.generate_synthetic_sounds()
    
    def generate_synthetic_sounds(self):
        """Generate simple synthetic sound effects using pygame."""
        # For now, create placeholder sounds
        # In production, these would be actual audio files
        
        try:
            # Create simple beep sounds using pygame
            # These are very basic - proper sounds should be audio files
            
            # Jump sound (rising pitch)
            self.sounds['jump'] = self._create_beep(frequency=440, duration=0.1)
            
            # Coin sound (high pitch ding)
            self.sounds['coin'] = self._create_beep(frequency=880, duration=0.15)
            
            # Enemy hit (low thud)
            self.sounds['enemy_hit'] = self._create_beep(frequency=200, duration=0.2)
            
            # Enemy defeat (descending tone)
            self.sounds['enemy_defeat'] = self._create_beep(frequency=600, duration=0.25)
            
            # Level complete (victory jingle)
            self.sounds['level_complete'] = self._create_beep(frequency=660, duration=0.3)
            
            # Death sound (sad trombone)
            self.sounds['death'] = self._create_beep(frequency=180, duration=0.4)
            
        except Exception as e:
            print(f"Could not generate sounds: {e}")
    
    def _create_beep(self, frequency=440, duration=0.2, volume=0.5):
        """
        Create a simple beep sound.
        
        Args:
            frequency: Tone frequency in Hz
            duration: Sound duration in seconds
            volume: Volume (0-1)
            
        Returns:
            pygame.mixer.Sound object or None
        """
        try:
            sample_rate = 22050
            n_samples = int(round(duration * sample_rate))
            
            # Generate sine wave
            import numpy as np
            buf = np.zeros((n_samples, 2), dtype=np.int16)
            max_sample = 2 ** (16 - 1) - 1
            
            for i in range(n_samples):
                t = float(i) / sample_rate
                # Sine wave with envelope
                envelope = 1.0 - (i / n_samples)  # Fade out
                value = int(max_sample * volume * envelope * np.sin(2.0 * np.pi * frequency * t))
                buf[i][0] = value
                buf[i][1] = value
            
            sound = pygame.sndarray.make_sound(buf)
            return sound
            
        except ImportError:
            # numpy not available for sound generation
            return None
        except Exception as e:
            print(f"Error creating beep: {e}")
            return None
    
    def play_sound(self, sound_name):
        """
        Play a sound effect.
        
        Args:
            sound_name: Name of sound to play
        """
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].set_volume(self.sfx_volume)
                self.sounds[sound_name].play()
            except Exception as e:
                pass  # Silently fail if sound can't play
    
    def play_music(self, difficulty='intermediate'):
        """
        Play background music for difficulty level.
        
        Args:
            difficulty: Difficulty level (novice/intermediate/expert)
        """
        # For now, no music playback
        # In production, load and play appropriate music track
        self.current_track = difficulty
    
    def stop_music(self):
        """Stop background music."""
        try:
            pygame.mixer.music.stop()
        except:
            pass
    
    def set_music_volume(self, volume):
        """
        Set music volume.
        
        Args:
            volume: Volume level (0-1)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except:
            pass
    
    def set_sfx_volume(self, volume):
        """
        Set sound effects volume.
        
        Args:
            volume: Volume level (0-1)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))


class ParticleSystem:
    """
    Advanced particle system for visual effects.
    Creates explosions, trails, and environmental effects.
    """
    
    def __init__(self):
        """Initialize particle system."""
        self.particles = []
        self.max_particles = 500
    
    def create_explosion(self, x, y, color=(255, 200, 50), count=20):
        """
        Create explosion effect.
        
        Args:
            x, y: Center position
            color: Particle color
            count: Number of particles
        """
        import random
        import math
        
        for _ in range(count):
            angle = random.random() * math.pi * 2
            speed = random.uniform(2, 8)
            
            particle = {
                'x': x,
                'y': y,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed,
                'lifetime': random.randint(20, 40),
                'max_lifetime': 40,
                'size': random.randint(2, 6),
                'color': color,
                'gravity': 0.2
            }
            
            self.particles.append(particle)
        
        # Limit total particles
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]
    
    def create_trail(self, x, y, color=(100, 180, 255), vel_x=0, vel_y=0):
        """
        Create trail particle.
        
        Args:
            x, y: Position
            color: Particle color
            vel_x, vel_y: Initial velocity
        """
        particle = {
            'x': x,
            'y': y,
            'vel_x': vel_x * -0.3,
            'vel_y': vel_y * -0.3,
            'lifetime': 15,
            'max_lifetime': 15,
            'size': 4,
            'color': color,
            'gravity': 0
        }
        
        self.particles.append(particle)
    
    def update(self, dt):
        """
        Update all particles.
        
        Args:
            dt: Delta time
        """
        for particle in self.particles[:]:
            # Update position
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            
            # Apply gravity
            particle['vel_y'] += particle.get('gravity', 0)
            
            # Update lifetime
            particle['lifetime'] -= 1
            
            # Remove dead particles
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def render(self, screen, camera_offset):
        """
        Render all particles.
        
        Args:
            screen: Pygame surface
            camera_offset: Camera position tuple
        """
        for particle in self.particles:
            # Calculate alpha based on lifetime
            alpha = int((particle['lifetime'] / particle['max_lifetime']) * 255)
            
            # Calculate position
            x = int(particle['x'] - camera_offset[0])
            y = int(particle['y'] - camera_offset[1])
            
            # Only render if on screen
            if -20 < x < screen.get_width() + 20 and -20 < y < screen.get_height() + 20:
                size = particle['size']
                color = (*particle['color'], alpha)
                
                # Create particle surface with alpha
                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                
                screen.blit(particle_surf, (x - size, y - size))
    
    def clear(self):
        """Clear all particles."""
        self.particles.clear()
