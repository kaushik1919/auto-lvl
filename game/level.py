"""
Level management system with procedural generation support.
Handles level layouts, entity spawning, and difficulty scaling.
"""

import pygame
import random
import math
from config.settings import *
from game.entities import Platform, Coin, Enemy, Goal


class Level:
    """
    Level manager handling layout, entities, and procedural generation.
    """
    
    def __init__(self, level_number, difficulty='intermediate', params=None):
        """
        Initialize level.
        
        Args:
            level_number: Current level index
            difficulty: Skill level (novice/intermediate/expert)
            params: Difficulty parameters dict
        """
        self.level_number = level_number
        self.difficulty = difficulty
        self.params = params or DIFFICULTY_SETTINGS[difficulty].copy()
        
        self.width = LEVEL_WIDTH
        self.height = LEVEL_HEIGHT
        self.spawn_point = (100, 600)
        
        # Entity lists
        self.platforms = []
        self.coins = []
        self.enemies = []
        self.goal = None
        
        # Generate level
        self.generate_level()
        
        print(f"Generated level {level_number + 1} with {len(self.platforms)} platforms, "
              f"{len(self.coins)} coins, {len(self.enemies)} enemies")
    
    def generate_level(self):
        """Generate level layout based on difficulty and level number."""
        # For now, use template-based generation
        # Later will be replaced with GAN-generated layouts
        
        if self.level_number < 3:
            # Use hand-crafted tutorial levels
            self._generate_tutorial_level()
        else:
            # Use procedural generation
            self._generate_procedural_level()
    
    def _generate_tutorial_level(self):
        """Generate beginner-friendly tutorial levels."""
        if self.level_number == 0:
            # Level 1: Basic platforming
            # Ground
            self.platforms.append(Platform(0, 650, 1000, 70))
            
            # Simple platform stairs
            for i in range(5):
                x = 200 + i * 150
                y = 600 - i * 50
                self.platforms.append(Platform(x, y, 120, 20))
                
                # Add coin above each platform
                if i > 0:
                    self.coins.append(Coin(x + 50, y - 40))
            
            # Extended ground
            self.platforms.append(Platform(1000, 650, 2000, 70))
            
            # Some floating platforms
            self.platforms.append(Platform(1500, 500, 200, 20))
            self.platforms.append(Platform(1850, 450, 200, 20))
            self.platforms.append(Platform(2200, 400, 200, 20))
            
            # Add coins
            for x in range(1550, 2250, 100):
                self.coins.append(Coin(x, 350))
            
            # Add a few enemies
            self.enemies.append(Enemy(1200, 600, 'walker', 
                                     self.params['enemy_speed_multiplier']))
            self.enemies.append(Enemy(2000, 600, 'walker',
                                     self.params['enemy_speed_multiplier']))
            
            # Goal at end
            self.goal = Goal(2600, 300)
            
        elif self.level_number == 1:
            # Level 2: Introduce gaps and more enemies
            self.platforms.append(Platform(0, 650, 400, 70))
            
            # Gap jumps
            platform_x = 500
            for i in range(6):
                gap = 150 * self.params['platform_gap_multiplier']
                self.platforms.append(Platform(int(platform_x), 650, 120, 20))
                
                # Coins over gaps
                if i < 5:
                    self.coins.append(Coin(int(platform_x + 120 + gap // 2), 550))
                
                # Enemies on some platforms
                if i % 2 == 0 and i > 0:
                    self.enemies.append(Enemy(platform_x + 30, 600, 'walker',
                                             self.params['enemy_speed_multiplier']))
                
                platform_x += 120 + gap
            
            # Final stretch
            self.platforms.append(Platform(int(platform_x), 650, 1500, 70))
            
            # More enemies
            num_enemies = int(3 * self.params['enemy_spawn_rate'])
            for i in range(num_enemies):
                x = platform_x + 200 + i * 300
                self.enemies.append(Enemy(x, 600, 'walker',
                                         self.params['enemy_speed_multiplier']))
            
            # Goal
            self.goal = Goal(platform_x + 1400, 550)
            
        else:
            # Level 3: Mixed challenges
            self._generate_procedural_level()
    
    def _generate_procedural_level(self):
        """Generate level using procedural algorithms."""
        # This will later be replaced by GAN generation
        # For now, use rule-based procedural generation
        # Start platform (ground) and guaranteed safe spawn platform
        self.platforms.append(Platform(0, 650, 300, 70))
        # Safe spawn platform under player start
        spawn_x = 100
        spawn_y = 520
        self.platforms.append(Platform(spawn_x - 50, spawn_y, 200, 20))
        self.spawn_point = (spawn_x, spawn_y - PLAYER_SIZE[1])

        current_x = 350
        current_y = 650
        
        # Generate level in chunks
        num_chunks = 8 + self.level_number
        
        for chunk in range(num_chunks):
            chunk_type = random.choice(['stairs', 'gaps', 'floating', 'ground'])
            
            if chunk_type == 'stairs':
                # Ascending or descending stairs
                direction = random.choice([-1, 1])
                num_stairs = random.randint(3, 6)
                
                for i in range(num_stairs):
                    width = random.randint(100, 150)
                    self.platforms.append(Platform(int(current_x), int(current_y), width, 20))
                    
                    # Add coin
                    if random.random() < self.params['coin_frequency'] * 0.8:
                        self.coins.append(Coin(int(current_x + width // 2), int(current_y - 50)))
                    
                    # Add enemy occasionally
                    if random.random() < self.params['enemy_spawn_rate'] * 0.3:
                        self.enemies.append(Enemy(current_x + 20, current_y - 50, 'walker',
                                                 self.params['enemy_speed_multiplier']))
                    
                    current_x += width + 50
                    current_y += direction * random.randint(40, 70)
                    current_y = max(300, min(650, current_y))
            
            elif chunk_type == 'gaps':
                # Series of platforms with gaps
                num_platforms = random.randint(4, 7)
                
                for i in range(num_platforms):
                    width = random.randint(80, 130)
                    gap = random.randint(120, 200) * self.params['platform_gap_multiplier']
                    
                    self.platforms.append(Platform(int(current_x), int(current_y), width, 20))
                    
                    # Coin over gap
                    if random.random() < self.params['coin_frequency']:
                        self.coins.append(Coin(int(current_x + width + gap // 2), 
                                              int(current_y - 80)))
                    
                    current_x += width + gap
            
            elif chunk_type == 'floating':
                # Floating platforms at various heights
                base_y = current_y
                num_floaters = random.randint(3, 6)
                
                for i in range(num_floaters):
                    y_offset = random.randint(-150, 50)
                    width = random.randint(90, 140)
                    
                    self.platforms.append(Platform(int(current_x), 
                                                  int(base_y + y_offset), 
                                                  width, 20))
                    
                    # Coins on platforms
                    if random.random() < self.params['coin_frequency']:
                        self.coins.append(Coin(int(current_x + width // 2), 
                                              int(base_y + y_offset - 40)))
                    
                    current_x += width + random.randint(100, 180)
            
            else:  # ground
                # Long ground section
                length = random.randint(400, 800)
                self.platforms.append(Platform(int(current_x), int(current_y), int(length), 70))
                
                # Scatter coins
                num_coins = int(length / 100 * self.params['coin_frequency'])
                for i in range(num_coins):
                    coin_x = current_x + random.randint(50, int(length - 50))
                    self.coins.append(Coin(int(coin_x), int(current_y - 50)))
                
                # Add enemies
                num_enemies = int((length / 300) * self.params['enemy_spawn_rate'])
                for i in range(num_enemies):
                    enemy_x = current_x + random.randint(100, int(length - 100))
                    self.enemies.append(Enemy(enemy_x, current_y - 50, 'walker',
                                             self.params['enemy_speed_multiplier']))
                
                current_x += length + 100
        
        # Add goal at the end
        self.goal = Goal(current_x - 100, current_y - 100)
        
        # Update level width
        self.width = max(self.width, int(current_x + 200))
    
    def get_collision_platforms(self):
        """Get list of platform rectangles for collision detection."""
        return [p.rect for p in self.platforms]
    
    def update(self, dt, player, difficulty_params):
        """
        Update all level entities.
        
        Args:
            dt: Delta time
            player: Player object
            difficulty_params: Current difficulty settings
        """
        # Update platforms (for moving platforms)
        for platform in self.platforms:
            platform.update(dt)
        
        # Update coins
        for coin in self.coins[:]:
            collected = coin.update(dt, player)
            if collected:
                # Coin was collected - metrics tracker will count it
                self.coins.remove(coin)
        
        # Update enemies
        platform_rects = self.get_collision_platforms()
        for enemy in self.enemies:
            enemy.update(dt, platform_rects)
        
        # Update goal
        if self.goal:
            self.goal.update(dt)
    
    def check_goal_reached(self, player):
        """
        Check if player reached the goal.
        
        Args:
            player: Player object
            
        Returns:
            True if goal was reached
        """
        if self.goal:
            return self.goal.rect.colliderect(player.rect)
        return False
    
    def render(self, screen, camera_offset):
        """
        Render all level entities.
        
        Args:
            screen: Pygame surface
            camera_offset: Camera position tuple
        """
        # Render platforms
        for platform in self.platforms:
            platform.render(screen, camera_offset)
        
        # Render coins
        for coin in self.coins:
            coin.render(screen, camera_offset)
        
        
        # Render enemies
        for enemy in self.enemies:
            enemy.render(screen, camera_offset)
        
        # Render goal
        if self.goal:
            self.goal.render(screen, camera_offset)
