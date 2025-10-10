"""
Game entities: enemies, platforms, coins, obstacles, and interactive elements.
Implements behavior, rendering, and collision for all game objects.
"""

import pygame
import random
import math
from config.settings import *


class Platform:
    """Static platform for player collision."""
    
    def __init__(self, x, y, width, height, platform_type='normal'):
        """
        Initialize platform.
        
        Args:
            x, y: Position
            width, height: Dimensions
            platform_type: 'normal', 'moving', 'crumbling'
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.type = platform_type
        
        # Create visual
        self.create_surface()
    
    def create_surface(self):
        """Create platform visual with red/black theme."""
        self.surface = pygame.Surface((self.width, self.height))
        
        # Base color - dark red
        base_color = PLATFORM_GRAY
        if self.type == 'moving':
            base_color = (100, 20, 20)
        elif self.type == 'crumbling':
            base_color = (80, 10, 10)
        
        self.surface.fill(base_color)
        
        # Add highlight (brighter red)
        pygame.draw.rect(self.surface, (min(base_color[0] + 50, 255), 
                                       min(base_color[1] + 20, 255),
                                       base_color[2]),
                        (0, 0, self.width, 4))
        
        # Add shadow (darker/black)
        pygame.draw.rect(self.surface, (max(base_color[0] - 40, 0),
                                       0,
                                       0),
                        (0, self.height - 4, self.width, 4))
    
    def update(self, dt):
        """Update platform (for moving platforms)."""
        pass
    
    def render(self, screen, camera_offset):
        """Render platform."""
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        screen.blit(self.surface, (render_x, render_y))


class Coin:
    """Collectible coin that awards points."""
    
    def __init__(self, x, y):
        """Initialize coin at position."""
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.collected = False
        
        # Animation
        self.animation_offset = random.random() * math.pi * 2
        self.bob_time = 0
        
        # Particle effect on collection
        self.particles = []
    
    def update(self, dt, player):
        """Update coin animation and check collection."""
        if self.collected:
            # Update particles
            for particle in self.particles[:]:
                particle['y'] -= particle['vel_y']
                particle['vel_y'] -= 0.3
                particle['lifetime'] -= 1
                if particle['lifetime'] <= 0:
                    self.particles.remove(particle)
            return False  # Remove from game
        
        # Bobbing animation
        self.bob_time += dt * 3
        
        # Check collision with player
        if self.rect.colliderect(player.rect):
            self.collect()
            return True
        
        return False
    
    def collect(self):
        """Trigger coin collection."""
        self.collected = True
        
        # Spawn particles
        for _ in range(8):
            angle = random.random() * math.pi * 2
            speed = random.uniform(2, 4)
            self.particles.append({
                'x': self.x + self.width // 2,
                'y': self.y + self.height // 2,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed + 3,
                'lifetime': 20,
                'color': COIN_GOLD
            })
    
    def render(self, screen, camera_offset):
        """Render coin with animation."""
        if self.collected:
            # Render particles
            for particle in self.particles:
                pos_x = int(particle['x'] - camera_offset[0])
                pos_y = int(particle['y'] - camera_offset[1])
                alpha = int((particle['lifetime'] / 20) * 255)
                size = 3
                
                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                color = (*particle['color'], alpha)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                screen.blit(particle_surf, (pos_x - size, pos_y - size))
                
                # Update particle position for next frame
                particle['x'] += particle['vel_x']
            return
        
        # Calculate bobbing offset
        bob_offset = math.sin(self.bob_time + self.animation_offset) * 5
        
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1] + bob_offset)
        
        # Draw coin
        coin_rect = pygame.Rect(render_x, render_y, self.width, self.height)
        pygame.draw.circle(screen, COIN_GOLD, coin_rect.center, self.width // 2)
        pygame.draw.circle(screen, (255, 100, 100), coin_rect.center, self.width // 3)
        
        # Draw shine effect
        shine_offset = 4
        pygame.draw.circle(screen, (255, 150, 150), 
                          (coin_rect.centerx - shine_offset, coin_rect.centery - shine_offset), 
                          3)


class Enemy:
    """Moving enemy that damages player on contact."""
    
    def __init__(self, x, y, enemy_type='walker', speed_multiplier=1.0):
        """
        Initialize enemy.
        
        Args:
            x, y: Starting position
            enemy_type: 'walker', 'flyer', 'jumper'
            speed_multiplier: Difficulty-based speed adjustment
        """
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.type = enemy_type
        
        # Movement
        self.vel_x = 2 * speed_multiplier
        self.vel_y = 0
        self.direction = 1  # 1 = right, -1 = left
        
        # State
        self.alive = True
        self.on_ground = False
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
    
    def update(self, dt, platforms):
        """Update enemy movement and physics."""
        if not self.alive:
            return
        
        # Apply gravity for walkers
        if self.type == 'walker':
            self.vel_y += GRAVITY
            self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        
        # Movement based on type
        if self.type == 'walker':
            self.x += self.vel_x * self.direction
        elif self.type == 'flyer':
            # Sine wave movement
            self.x += self.vel_x * self.direction
            self.y += math.sin(self.x * 0.05) * 0.5
        
        # Update position
        self.y += self.vel_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Collision with platforms
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                # Land on platform
                if self.vel_y > 0 and self.rect.bottom > platform.top:
                    self.rect.bottom = platform.top
                    self.y = self.rect.y
                    self.vel_y = 0
                    self.on_ground = True
                
                # Turn around at edges or walls
                if self.type == 'walker':
                    if self.direction > 0 and self.rect.right > platform.right:
                        self.direction = -1
                    elif self.direction < 0 and self.rect.left < platform.left:
                        self.direction = 1
        
        # Animation
        self.animation_timer += dt * 10
        if self.animation_timer > 1:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
    
    def check_player_collision(self, player):
        """
        Check if enemy hit player.
        
        Returns:
            True if collision occurred
        """
        if self.alive and self.rect.colliderect(player.rect):
            # Check if player jumped on enemy
            if player.vel_y > 0 and player.rect.bottom < self.rect.centery:
                self.alive = False
                player.vel_y = -PLAYER_JUMP_POWER * 0.6  # Bounce
                return False
            else:
                return True  # Player was hit
        return False
    
    def render(self, screen, camera_offset):
        """Render enemy with enhanced menacing design."""
        if not self.alive:
            return
        
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        
        # Draw enemy with dark menacing look
        enemy_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        center_x, center_y = self.width // 2, self.height // 2
        
        # Outer dark glow
        import math
        for i in range(3):
            glow_radius = self.width // 2 + 4 - i
            alpha = 80 - i * 25
            pygame.draw.circle(enemy_surf, (100, 0, 0, alpha), (center_x, center_y), glow_radius)
        
        # Main body - dark red with black outline
        pygame.draw.circle(enemy_surf, (50, 0, 0), (center_x, center_y), self.width // 2 + 1)
        pygame.draw.circle(enemy_surf, ENEMY_RED, (center_x, center_y), self.width // 2)
        
        # Spiky protrusions
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle + self.animation_frame * 45)
            spike_len = 6
            end_x = center_x + math.cos(rad) * (self.width // 2 + spike_len)
            end_y = center_y + math.sin(rad) * (self.height // 2 + spike_len)
            # Dark spike
            pygame.draw.line(enemy_surf, (80, 0, 0), (center_x, center_y), (end_x, end_y), 4)
            # Bright tip
            pygame.draw.circle(enemy_surf, (255, 50, 50), (int(end_x), int(end_y)), 2)
        
        # Menacing eyes
        eye_offset = 2 if self.animation_frame == 0 else -2
        eye_y = center_y - 5
        eye_spacing = 8
        
        # Left eye - glowing red
        pygame.draw.circle(enemy_surf, (10, 10, 10), (center_x - eye_spacing, eye_y), 5)
        pygame.draw.circle(enemy_surf, (255, 0, 0), (center_x - eye_spacing + eye_offset, eye_y), 3)
        pygame.draw.circle(enemy_surf, (255, 100, 100), (center_x - eye_spacing + eye_offset, eye_y), 1)
        
        # Right eye - glowing red
        pygame.draw.circle(enemy_surf, (10, 10, 10), (center_x + eye_spacing, eye_y), 5)
        pygame.draw.circle(enemy_surf, (255, 0, 0), (center_x + eye_spacing + eye_offset, eye_y), 3)
        pygame.draw.circle(enemy_surf, (255, 100, 100), (center_x + eye_spacing + eye_offset, eye_y), 1)
        
        # Menacing teeth/mouth
        mouth_y = center_y + 8
        for i in range(3):
            tooth_x = center_x - 6 + i * 6
            pygame.draw.polygon(enemy_surf, (255, 255, 255), [
                (tooth_x, mouth_y),
                (tooth_x - 2, mouth_y + 4),
                (tooth_x + 2, mouth_y + 4)
            ])
        
        # Flip if moving left
        if self.direction < 0:
            enemy_surf = pygame.transform.flip(enemy_surf, True, False)
        
        screen.blit(enemy_surf, (render_x, render_y))


class Goal:
    """Level goal/finish line."""
    
    def __init__(self, x, y):
        """Initialize goal at position."""
        self.x = x
        self.y = y
        self.width = 50
        self.height = 100
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Animation
        self.animation_time = 0
    
    def update(self, dt):
        """Update animation."""
        self.animation_time += dt * 2
    
    def render(self, screen, camera_offset):
        """Render goal with red/black theme animation."""
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        
        # Draw pole (dark)
        pole_width = 8
        pole_x = render_x + self.width // 2 - pole_width // 2
        pygame.draw.rect(screen, (30, 0, 0), 
                        (pole_x, render_y, pole_width, self.height))
        
        # Draw flag with wave animation
        flag_segments = 10
        flag_height = self.height // 2
        flag_width = self.width - pole_width
        
        for i in range(flag_segments):
            y_progress = i / flag_segments
            wave_offset = math.sin(self.animation_time + y_progress * math.pi * 2) * 5
            
            segment_y = render_y + int(y_progress * flag_height)
            segment_height = flag_height // flag_segments + 1
            
            # Alternating red and black
            color = (200, 0, 0) if i % 2 == 0 else (20, 0, 0)
            
            flag_rect = pygame.Rect(
                int(pole_x + pole_width + wave_offset),
                segment_y,
                int(flag_width - wave_offset),
                segment_height
            )
            pygame.draw.rect(screen, color, flag_rect)
        
        # Glowing top
        pygame.draw.circle(screen, (255, 50, 50), (pole_x + pole_width // 2, render_y), 5)
        pygame.draw.circle(screen, (255, 150, 150), (pole_x + pole_width // 2, render_y), 3)
