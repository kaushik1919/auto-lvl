"""
Camera system with smooth tracking and parallax scrolling.
Provides cinematic camera movement and depth perception.
"""

import pygame
from config.settings import *


class Camera:
    """
    Advanced camera system with smooth following and parallax layers.
    """
    
    def __init__(self, width, height):
        """
        Initialize camera.
        
        Args:
            width: Level width in pixels
            height: Level height in pixels
        """
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.level_width = width
        self.level_height = height
        
        # Parallax background layers
        self.parallax_layers = []
        self.create_parallax_layers()
    
    def create_parallax_layers(self):
        """Create parallax background layers with red/black theme."""
        # Create gradient dark red to black layers
        for i, speed in enumerate(PARALLAX_SPEEDS):
            layer_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # Create gradient from dark red to black
            for y in range(SCREEN_HEIGHT):
                progress = y / SCREEN_HEIGHT
                r = int(40 - progress * 30)  # Dark red to black
                g = int(10 - progress * 10)
                b = int(15 - progress * 15)
                pygame.draw.line(layer_surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
            # Add ominous red clouds/fog
            cloud_color = (80, 0, 0, 100)
            num_clouds = 5 + i * 2
            for j in range(num_clouds):
                x = (j * SCREEN_WIDTH // num_clouds + i * 100) % (SCREEN_WIDTH + 200)
                y = 50 + (j % 3) * 80
                
                # Draw dark red fog as overlapping circles
                cloud_surf = pygame.Surface((80, 40), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surf, cloud_color, (20, 20), 15)
                pygame.draw.circle(cloud_surf, cloud_color, (40, 20), 20)
                pygame.draw.circle(cloud_surf, cloud_color, (60, 20), 15)
                layer_surf.blit(cloud_surf, (x, y))
            
            self.parallax_layers.append({
                'surface': layer_surf,
                'speed': speed,
                'offset': 0
            })
    
    def update(self, target, dt):
        """
        Smoothly follow target with deadzone.
        
        Args:
            target: Player object to follow
            dt: Delta time in seconds
        """
        # Calculate target position (center on player)
        self.target_x = target.x + target.width // 2 - SCREEN_WIDTH // 2
        self.target_y = target.y + target.height // 2 - SCREEN_HEIGHT // 2
        
        # Apply deadzone (camera doesn't move if player is in center area)
        deadzone_left = SCREEN_WIDTH // 2 - CAMERA_DEADZONE_WIDTH // 2
        deadzone_right = SCREEN_WIDTH // 2 + CAMERA_DEADZONE_WIDTH // 2
        deadzone_top = SCREEN_HEIGHT // 2 - CAMERA_DEADZONE_HEIGHT // 2
        deadzone_bottom = SCREEN_HEIGHT // 2 + CAMERA_DEADZONE_HEIGHT // 2
        
        player_screen_x = target.x - self.x
        player_screen_y = target.y - self.y
        
        # Horizontal deadzone
        if player_screen_x < deadzone_left:
            self.target_x = target.x - deadzone_left
        elif player_screen_x > deadzone_right:
            self.target_x = target.x - deadzone_right
        else:
            self.target_x = self.x
        
        # Vertical deadzone
        if player_screen_y < deadzone_top:
            self.target_y = target.y - deadzone_top
        elif player_screen_y > deadzone_bottom:
            self.target_y = target.y - deadzone_bottom
        else:
            self.target_y = self.y
        
        # Smooth camera movement (lerp)
        self.x += (self.target_x - self.x) * CAMERA_SMOOTH
        self.y += (self.target_y - self.y) * CAMERA_SMOOTH
        
        # Clamp camera to level bounds
        self.x = max(0, min(self.x, self.level_width - SCREEN_WIDTH))
        self.y = max(0, min(self.y, self.level_height - SCREEN_HEIGHT))
        
        # Update parallax layer offsets
        for layer in self.parallax_layers:
            layer['offset'] = self.x * layer['speed']
    
    def render_background(self, screen):
        """
        Render parallax background layers.
        
        Args:
            screen: Pygame surface to render to
        """
        for layer in self.parallax_layers:
            offset = int(layer['offset']) % SCREEN_WIDTH
            
            # Draw layer twice for seamless scrolling
            screen.blit(layer['surface'], (-offset, 0))
            if offset > 0:
                screen.blit(layer['surface'], (SCREEN_WIDTH - offset, 0))
    
    def get_offset(self):
        """
        Get camera offset for rendering world objects.
        
        Returns:
            Tuple of (x, y) offset
        """
        return (int(self.x), int(self.y))
    
    def apply(self, rect):
        """
        Apply camera offset to a rectangle.
        
        Args:
            rect: Pygame Rect object
            
        Returns:
            New Rect with camera offset applied
        """
        return pygame.Rect(
            rect.x - int(self.x),
            rect.y - int(self.y),
            rect.width,
            rect.height
        )
