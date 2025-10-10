"""
Player character with Sonic-style physics implementation.
Features smooth acceleration, momentum-based movement, and responsive controls.
"""

import pygame
from config.settings import *


class Player:
    """
    Player character with advanced Sonic-inspired physics.
    Implements acceleration, momentum, smooth jumping, and collision detection.
    """
    
    def __init__(self, x, y):
        """Initialize player at starting position."""
        self.x = x
        self.y = y
        self.width, self.height = PLAYER_SIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Physics properties
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        
        # Animation state
        self.animation_frame = 0
        self.animation_timer = 0
        self.state = 'idle'  # idle, running, jumping, falling
        
        # Particle trail for high-speed movement
        self.particles = []
        
        # Create player surface (placeholder - will be sprite later)
        self.create_sprite()
    
    def create_sprite(self):
        """Create Shadow the Hedgehog pixel art sprites."""
        self.sprites = {
            'idle': self._create_shadow_idle(),
            'run': [self._create_shadow_run(i) for i in range(4)],
            'jump': self._create_shadow_jump(),
            'fall': self._create_shadow_fall()
        }
    
    def _create_shadow_idle(self):
        """Create Shadow idle sprite - pixel art style."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Shadow's color palette
        black = (20, 20, 20)
        dark_red = (140, 0, 0)
        bright_red = (220, 0, 0)
        tan = (210, 170, 130)
        white = (255, 255, 255)
        dark_gray = (60, 60, 60)
        
        # Body - black with red stripes
        # Main body (black circle base)
        center_x, center_y = self.width // 2, self.height // 2 + 2
        
        # Draw black body
        for y in range(-8, 9):
            for x in range(-8, 9):
                if x*x + y*y <= 64:  # Circle radius 8
                    surf.set_at((center_x + x, center_y + y), black)
        
        # Red stripes on quills (top spikes)
        spike_positions = [
            (-10, -4), (-8, -8), (-6, -10),  # Left spikes
            (0, -11), (6, -10), (8, -8), (10, -4)  # Top and right spikes
        ]
        
        for sx, sy in spike_positions:
            # Draw spike
            for i in range(5):
                px = center_x + sx + (1 if sx > 0 else -1 if sx < 0 else 0) * i // 2
                py = center_y + sy - i // 3
                if 0 <= px < self.width and 0 <= py < self.height:
                    surf.set_at((px, py), black)
                    # Red stripe on spike
                    if i > 1:
                        surf.set_at((px + 1, py), dark_red)
        
        # Muzzle/mouth area (tan)
        for y in range(3):
            for x in range(-3, 4):
                if abs(x) + y < 5:
                    surf.set_at((center_x + x, center_y + 3 + y), tan)
        
        # Eyes (red with white pupils)
        # Left eye
        eye_y = center_y - 2
        surf.set_at((center_x - 4, eye_y - 1), white)
        surf.set_at((center_x - 4, eye_y), bright_red)
        surf.set_at((center_x - 4, eye_y + 1), bright_red)
        surf.set_at((center_x - 3, eye_y), bright_red)
        surf.set_at((center_x - 5, eye_y), bright_red)
        
        # Right eye
        surf.set_at((center_x + 4, eye_y - 1), white)
        surf.set_at((center_x + 4, eye_y), bright_red)
        surf.set_at((center_x + 4, eye_y + 1), bright_red)
        surf.set_at((center_x + 3, eye_y), bright_red)
        surf.set_at((center_x + 5, eye_y), bright_red)
        
        # Air shoes (bottom - red and white)
        shoe_y = center_y + 10
        # Left shoe
        for x in range(-6, -2):
            surf.set_at((center_x + x, shoe_y), bright_red)
            surf.set_at((center_x + x, shoe_y + 1), dark_red)
            surf.set_at((center_x + x, shoe_y - 1), white)
        
        # Right shoe
        for x in range(3, 7):
            surf.set_at((center_x + x, shoe_y), bright_red)
            surf.set_at((center_x + x, shoe_y + 1), dark_red)
            surf.set_at((center_x + x, shoe_y - 1), white)
        
        return surf
    
    def _create_shadow_run(self, frame):
        """Create Shadow running animation sprite."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Shadow's color palette
        black = (20, 20, 20)
        dark_red = (140, 0, 0)
        bright_red = (220, 0, 0)
        tan = (210, 170, 130)
        white = (255, 255, 255)
        
        # Animate with vertical bob
        offset_y = 2 if frame % 2 == 0 else -2
        center_x, center_y = self.width // 2, self.height // 2 + offset_y
        
        # Speed blur trail (red)
        import math
        for i in range(3):
            trail_x = center_x - i * 6
            trail_alpha = 120 - i * 40
            if trail_x > 0:
                for y in range(-6, 7):
                    for x in range(-2, 2):
                        if x*x + y*y <= 25 and trail_x + x < self.width:
                            r, g, b = bright_red
                            color = pygame.Color(r, g, b, trail_alpha)
                            surf.set_at((trail_x + x, center_y + y), color)
        
        # Main black body
        for y in range(-7, 8):
            for x in range(-7, 8):
                if x*x + y*y <= 49:
                    surf.set_at((center_x + x, center_y + y), black)
        
        # Spikes leaning back (running pose)
        spike_angle = -30 if frame < 2 else -40
        for i, base_angle in enumerate([-60, -30, 0, 30, 60]):
            angle = base_angle + spike_angle
            rad = math.radians(angle)
            for dist in range(3, 10):
                sx = int(center_x + math.cos(rad) * dist)
                sy = int(center_y - 8 + math.sin(rad) * dist)
                if 0 <= sx < self.width and 0 <= sy < self.height:
                    surf.set_at((sx, sy), black)
                    if dist > 5:
                        surf.set_at((sx + 1, sy), dark_red)
        
        # Eyes (red)
        eye_y = center_y - 2
        surf.set_at((center_x - 3, eye_y), bright_red)
        surf.set_at((center_x + 3, eye_y), bright_red)
        
        # Muzzle
        for x in range(-2, 3):
            surf.set_at((center_x + x, center_y + 3), tan)
        
        # Shoes (animated)
        shoe_y = center_y + 9
        leg_offset = 2 if frame % 2 == 0 else -2
        
        # Front leg
        for x in range(2, 6):
            surf.set_at((center_x + x, shoe_y + leg_offset), bright_red)
            surf.set_at((center_x + x, shoe_y + leg_offset - 1), white)
        
        # Back leg
        for x in range(-6, -2):
            surf.set_at((center_x + x, shoe_y - leg_offset), bright_red)
            surf.set_at((center_x + x, shoe_y - leg_offset - 1), white)
        
        return surf
    
    def _create_shadow_jump(self):
        """Create Shadow jumping/spin attack sprite."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        black = (20, 20, 20)
        dark_red = (140, 0, 0)
        bright_red = (220, 0, 0)
        
        center_x, center_y = self.width // 2, self.height // 2
        
        # Spinning ball effect
        import math
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            for dist in range(3, 10):
                x = int(center_x + math.cos(rad) * dist)
                y = int(center_y + math.sin(rad) * dist)
                if 0 <= x < self.width and 0 <= y < self.height:
                    surf.set_at((x, y), black)
                    # Red stripe effect
                    if angle % 90 == 0 and dist > 6:
                        surf.set_at((x, y), bright_red)
        
        # Core black ball
        for y in range(-6, 7):
            for x in range(-6, 7):
                if x*x + y*y <= 36:
                    surf.set_at((center_x + x, center_y + y), black)
        
        # Spinning motion blur
        for i in range(3):
            blur_alpha = 100 - i * 30
            for y in range(-4, 5):
                for x in range(-4, 5):
                    if x*x + y*y <= 16:
                        blur_y = center_y + y + i * 3
                        if 0 <= blur_y < self.height:
                            r, g, b = dark_red
                            surf.set_at((center_x + x, blur_y), pygame.Color(r, g, b, blur_alpha))
        
        return surf
    
    def _create_shadow_fall(self):
        """Create Shadow falling sprite."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        black = (20, 20, 20)
        dark_red = (140, 0, 0)
        bright_red = (220, 0, 0)
        tan = (210, 170, 130)
        
        center_x, center_y = self.width // 2, self.height // 2 + 3
        
        # Main body
        for y in range(-7, 8):
            for x in range(-7, 8):
                if x*x + y*y <= 49:
                    surf.set_at((center_x + x, center_y + y), black)
        
        # Spikes pointing up (falling pose)
        import math
        for base_angle in [-60, -30, 0, 30, 60]:
            rad = math.radians(base_angle - 90)
            for dist in range(3, 9):
                sx = int(center_x + math.cos(rad) * dist)
                sy = int(center_y + math.sin(rad) * dist)
                if 0 <= sx < self.width and 0 <= sy < self.height:
                    surf.set_at((sx, sy), black)
                    if dist > 5:
                        surf.set_at((sx, sy + 1), dark_red)
        
        # Eyes
        eye_y = center_y - 1
        surf.set_at((center_x - 3, eye_y), bright_red)
        surf.set_at((center_x + 3, eye_y), bright_red)
        
        # Muzzle
        for x in range(-2, 3):
            surf.set_at((center_x + x, center_y + 3), tan)
        
        # Air trail above (falling down)
        for i in range(2):
            trail_y = center_y - 10 - i * 3
            if trail_y > 0:
                for x in range(-3, 4):
                    r, g, b = dark_red
                    surf.set_at((center_x + x, trail_y), pygame.Color(r, g, b, 80 - i * 30))
        
        return surf
    
    def handle_input(self, keys):
        """
        Process player input for movement.
        Implements smooth acceleration and deceleration.
        """
        # Horizontal movement with acceleration
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x -= PLAYER_ACCELERATION
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x += PLAYER_ACCELERATION
            self.facing_right = True
        else:
            # Apply friction when no input
            if self.on_ground:
                self.vel_x *= GROUND_FRICTION
            else:
                self.vel_x *= AIR_FRICTION
        
        # Clamp horizontal speed
        self.vel_x = max(-PLAYER_MAX_SPEED, min(PLAYER_MAX_SPEED, self.vel_x))
        
        # Jumping (only when on ground)
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -PLAYER_JUMP_POWER
            self.on_ground = False
    
    def update(self, dt, platforms):
        """
        Update player physics and animation.
        
        Args:
            dt: Delta time in seconds
            platforms: List of platform rects for collision detection
        """
        # Apply gravity
        if not self.on_ground:
            self.vel_y += GRAVITY
            self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Update rect for collision detection
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Handle collisions
        self.handle_collisions(platforms)
        
        # Update animation state
        self.update_animation(dt)
        
        # Update particles for speed effect
        self.update_particles()
        if abs(self.vel_x) > PLAYER_MAX_SPEED * 0.7:
            self.spawn_particle()
    
    def handle_collisions(self, platforms):
        """
        Handle collision detection and response with platforms.
        
        Args:
            platforms: List of platform rectangles
        """
        self.on_ground = False
        
        for platform in platforms:
            if self.rect.colliderect(platform):
                # Vertical collision
                if self.vel_y > 0:  # Falling
                    if self.rect.bottom > platform.top and self.rect.bottom < platform.top + 20:
                        self.rect.bottom = platform.top
                        self.y = self.rect.y
                        self.vel_y = 0
                        self.on_ground = True
                elif self.vel_y < 0:  # Jumping up
                    if self.rect.top < platform.bottom and self.rect.top > platform.bottom - 20:
                        self.rect.top = platform.bottom
                        self.y = self.rect.y
                        self.vel_y = 0
                
                # Horizontal collision
                if self.vel_x > 0:  # Moving right
                    if self.rect.right > platform.left and self.rect.right < platform.left + abs(self.vel_x) + 5:
                        self.rect.right = platform.left
                        self.x = self.rect.x
                        self.vel_x = 0
                elif self.vel_x < 0:  # Moving left
                    if self.rect.left < platform.right and self.rect.left > platform.right - abs(self.vel_x) - 5:
                        self.rect.left = platform.right
                        self.x = self.rect.x
                        self.vel_x = 0
    
    def update_animation(self, dt):
        """Update animation state and frame."""
        # Determine animation state
        if not self.on_ground:
            if self.vel_y < 0:
                self.state = 'jump'
            else:
                self.state = 'fall'
        elif abs(self.vel_x) > 0.5:
            self.state = 'run'
        else:
            self.state = 'idle'
        
        # Update animation timer
        if self.state == 'run':
            self.animation_timer += dt * abs(self.vel_x)
            if self.animation_timer > 0.1:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
    
    def spawn_particle(self):
        """Create particle for Shadow's speed trail effect."""
        particle = {
            'x': self.x + self.width // 2,
            'y': self.y + self.height // 2,
            'vel_x': -self.vel_x * 0.2,
            'vel_y': 0,
            'lifetime': PARTICLE_LIFETIME,
            'color': (140, 0, 0)  # Dark red particles for Shadow
        }
        self.particles.append(particle)
        
        # Limit particle count
        if len(self.particles) > 50:
            self.particles.pop(0)
    
    def update_particles(self):
        """Update particle positions and lifetimes."""
        for particle in self.particles[:]:
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            particle['lifetime'] -= 1
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def render(self, screen, camera_offset):
        """
        Render player and particles.
        
        Args:
            screen: Pygame surface to render to
            camera_offset: (x, y) tuple for camera position
        """
        # Render particles
        for particle in self.particles:
            alpha = int((particle['lifetime'] / PARTICLE_LIFETIME) * 255)
            color = (*particle['color'], alpha)
            size = int((particle['lifetime'] / PARTICLE_LIFETIME) * 6) + 2
            pos_x = int(particle['x'] - camera_offset[0])
            pos_y = int(particle['y'] - camera_offset[1])
            
            # Create particle surface with alpha
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (size, size), size)
            screen.blit(particle_surf, (pos_x - size, pos_y - size))
        
        # Get current sprite
        if self.state == 'run':
            sprite = self.sprites['run'][self.animation_frame]
        else:
            sprite = self.sprites.get(self.state, self.sprites['idle'])
        
        # Flip sprite if facing left
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        
        # Render player
        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        screen.blit(sprite, (render_x, render_y))
        
        # Debug: Draw hitbox
        # debug_rect = pygame.Rect(render_x, render_y, self.width, self.height)
        # pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)
    
    def reset(self, x, y):
        """Reset player to starting position."""
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.particles.clear()
