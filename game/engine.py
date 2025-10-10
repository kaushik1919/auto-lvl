"""
Main game engine managing game state, rendering, and updates.
Central hub for all game systems and components.
"""

import pygame
import random
from config.settings import *
from game.player import Player
from game.camera import Camera
from game.level import Level
from ai.metrics_tracker import MetricsTracker
from ai.skill_predictor import SkillPredictor
from ai.difficulty_adjuster import DifficultyAdjuster


class GameEngine:
    """
    Core game engine managing all systems and game loop.
    Coordinates rendering, physics, AI, and state management.
    """
    
    def __init__(self, screen):
        """
        Initialize game engine.
        
        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        self.running = True
        self.paused = False
        
        # Initialize game state
        self.current_level = 0
        self.game_state = 'playing'  # playing, paused, game_over, level_complete

        # Initialize player (start on/near ground to avoid immediate fall)
        self.player = Player(100, 600)

        # Initialize level system
        self.level = Level(self.current_level)

        # Initialize camera
        self.camera = Camera(self.level.width, self.level.height)

        # Initialize AI systems
        self.metrics_tracker = MetricsTracker()
        self.skill_predictor = SkillPredictor()
        self.difficulty_adjuster = DifficultyAdjuster()

        # Load current difficulty settings
        self.current_difficulty = 'intermediate'
        self.difficulty_params = DIFFICULTY_SETTINGS[self.current_difficulty].copy()

        # UI Font - Try Latitude Sans or similar bold sans-serif fonts
        font_loaded = False
        
        # Try to find Latitude Sans or similar fonts
        font_options = [
            'Latitude Sans',
            'Bahnschrift',  # Windows modern sans-serif
            'Segoe UI',     # Windows default
            'Arial',        # Fallback
        ]
        
        for font_name in font_options:
            try:
                self.font_small = pygame.font.SysFont(font_name, 32, bold=True)
                self.font_large = pygame.font.SysFont(font_name, 64, bold=True)
                print(f"Using font: {font_name}")
                font_loaded = True
                break
            except:
                continue
        
        if not font_loaded:
            # Final fallback to default
            self.font_small = pygame.font.Font(None, 32)
            self.font_large = pygame.font.Font(None, 64)
            print("Using default font")

        # Performance tracking
        self.level_start_time = pygame.time.get_ticks()

        print(f"Game initialized - Level {self.current_level + 1}")
        print(f"Initial difficulty: {self.current_difficulty}")
    
    def render_text_outlined(self, font, text, color, outline_color=(0, 0, 0)):
        """
        Render text with outline for game-style look.
        
        Args:
            font: Pygame font object
            text: Text to render
            color: Main text color
            outline_color: Outline color (default black)
        
        Returns:
            Surface with outlined text
        """
        # Render outline (offset in 8 directions)
        outline_surf = font.render(text, True, outline_color)
        outline_rect = outline_surf.get_rect()
        
        # Create surface large enough for text + outline
        final_surf = pygame.Surface((outline_rect.width + 4, outline_rect.height + 4), pygame.SRCALPHA)
        
        # Draw outline
        for dx, dy in [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]:
            final_surf.blit(outline_surf, (2 + dx, 2 + dy))
        
        # Draw main text
        main_surf = font.render(text, True, color)
        final_surf.blit(main_surf, (2, 2))
        
        return final_surf
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: Pygame event object
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle_pause()
            elif event.key == pygame.K_r and self.game_state == 'game_over':
                self.restart_level()
    
    def toggle_pause(self):
        """Toggle pause state."""
        if self.game_state == 'playing':
            self.game_state = 'paused'
            self.paused = True
        elif self.game_state == 'paused':
            self.game_state = 'playing'
            self.paused = False
    
    def update(self, dt):
        """
        Update game state and all systems.
        
        Args:
            dt: Delta time in seconds
        """
        if self.paused or self.game_state != 'playing':
            return
        
        # Get input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        # Update player
        self.player.update(dt, self.level.get_collision_platforms())
        
        # Update level entities
        self.level.update(dt, self.player, self.difficulty_params)
        
        # Check enemy collisions (handle damage)
        for enemy in self.level.enemies:
            if enemy.check_player_collision(self.player):
                # Player was hit by enemy - die and respawn
                self.metrics_tracker.record_death()
                self.player.reset(100, 600)
                print("Player hit by enemy! Respawning...")
        
        # Track metrics
        self.metrics_tracker.update(self.player, self.level)
        
        # Update camera
        self.camera.update(self.player, dt)
        
        # Check win/loss conditions
        self.check_game_state()
    
    def check_game_state(self):
        """Check for level completion or game over."""
        # Check if player fell off map
        if self.player.y > self.level.height + 100:
            self.metrics_tracker.record_death()
            self.game_state = 'game_over'
            print("Game Over - Player fell!")
        
        # Check if player reached goal
        if self.level.check_goal_reached(self.player):
            self.complete_level()
    
    def complete_level(self):
        """Handle level completion and AI learning."""
        self.game_state = 'level_complete'
        
        # Calculate completion time
        completion_time = (pygame.time.get_ticks() - self.level_start_time) / 1000.0
        
        # Save metrics
        metrics_data = self.metrics_tracker.get_level_summary(
            self.current_level,
            completion_time
        )
        self.metrics_tracker.save_metrics(metrics_data)
        
        print("\n" + "=" * 60)
        print(f"LEVEL {self.current_level + 1} COMPLETE!")
        print("=" * 60)
        print(f"Time: {completion_time:.2f}s")
        print(f"Coins: {self.metrics_tracker.coins_collected}")
        print(f"Enemies Defeated: {self.metrics_tracker.enemies_defeated}")
        print(f"Deaths: {self.metrics_tracker.deaths}")
        print(f"Jumps: {self.metrics_tracker.jumps}")
        
        # Predict skill level
        predicted_skill = self.skill_predictor.predict_skill(metrics_data)
        print(f"\nPredicted Skill Level: {predicted_skill.upper()}")
        
        # Adjust difficulty for next level
        self.current_difficulty = predicted_skill
        self.difficulty_params = self.difficulty_adjuster.adjust_difficulty(
            predicted_skill,
            self.current_level + 1
        )
        
        print(f"Next level difficulty adjusted to: {predicted_skill}")
        print("=" * 60)
        
        # Move to next level after delay
        pygame.time.wait(3000)
        self.next_level()
    
    def next_level(self):
        """Progress to next level."""
        self.current_level += 1
        
        # Generate new level with adjusted difficulty
        self.level = Level(
            self.current_level,
            difficulty=self.current_difficulty,
            params=self.difficulty_params
        )
        
        # Reset player
        self.player.reset(100, 600)
        
        # Reset camera
        self.camera = Camera(self.level.width, self.level.height)
        
        # Reset metrics
        self.metrics_tracker.reset_level()
        
        # Reset timer
        self.level_start_time = pygame.time.get_ticks()
        
        # Resume gameplay
        self.game_state = 'playing'
        
        print(f"\nStarting Level {self.current_level + 1} - Difficulty: {self.current_difficulty}")
    
    def restart_level(self):
        """Restart current level."""
        self.player.reset(100, 600)
        self.level = Level(
            self.current_level,
            difficulty=self.current_difficulty,
            params=self.difficulty_params
        )
        self.camera = Camera(self.level.width, self.level.height)
        self.metrics_tracker.reset_level()
        self.level_start_time = pygame.time.get_ticks()
        self.game_state = 'playing'
        print("Level restarted")
    
    def render(self):
        """Render all game elements."""
        # Clear screen
        self.screen.fill(SKY_BLUE)
        
        # Render parallax background
        self.camera.render_background(self.screen)
        
        # Get camera offset
        cam_offset = self.camera.get_offset()
        
        # Render level
        self.level.render(self.screen, cam_offset)
        
        # Render player
        self.player.render(self.screen, cam_offset)
        
        # Render UI
        self.render_ui()
        
        # Render state-specific overlays
        if self.game_state == 'paused':
            self.render_pause_screen()
        elif self.game_state == 'game_over':
            self.render_game_over_screen()
        elif self.game_state == 'level_complete':
            self.render_level_complete_screen()
    
    def render_ui(self):
        """Render HUD elements with game-style outlined text."""
        # Score/Coins
        coins_text = self.render_text_outlined(
            self.font_small,
            f"Coins: {self.metrics_tracker.coins_collected}",
            (255, 215, 0)  # Gold
        )
        self.screen.blit(coins_text, (10, 10))
        
        # Level
        level_text = self.render_text_outlined(
            self.font_small,
            f"Level: {self.current_level + 1}",
            (255, 120, 120)  # Light red
        )
        self.screen.blit(level_text, (10, 40))
        
        # Difficulty
        difficulty_text = self.render_text_outlined(
            self.font_small,
            f"Difficulty: {self.current_difficulty.capitalize()}",
            (220, 100, 100)  # Muted red
        )
        self.screen.blit(difficulty_text, (10, 70))
        
        # Time
        elapsed = (pygame.time.get_ticks() - self.level_start_time) / 1000.0
        time_text = self.render_text_outlined(
            self.font_small,
            f"Time: {elapsed:.1f}s",
            (255, 120, 120)  # Light red
        )
        self.screen.blit(time_text, (SCREEN_WIDTH - 120, 10))
    
    def render_pause_screen(self):
        """Render pause overlay with game-style text."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((30, 20, 20))  # Dark gray-red overlay
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.render_text_outlined(self.font_large, "PAUSED", (255, 200, 100))
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
    
    def render_game_over_screen(self):
        """Render game over overlay with dramatic game-style text."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 10, 10))  # Very dark red
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.render_text_outlined(self.font_large, "GAME OVER", (255, 50, 50))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(game_over_text, text_rect)
        
        restart_text = self.render_text_outlined(self.font_small, "Press R to Restart", (220, 180, 100))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(restart_text, restart_rect)
    
    def render_level_complete_screen(self):
        """Render level complete overlay with victory game-style text."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((50, 30, 30))  # Dark red victory
        self.screen.blit(overlay, (0, 0))
        
        complete_text = self.render_text_outlined(self.font_large, "LEVEL COMPLETE!", (100, 255, 100))
        text_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(complete_text, text_rect)
    
    def cleanup(self):
        """Clean up resources and save final data."""
        print("\nShutting down game...")
        # Save any remaining metrics
        self.metrics_tracker.cleanup()
        print("Goodbye!")
