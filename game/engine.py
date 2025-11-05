"""
Main game engine managing game state, rendering, and updates.
Central hub for all game systems and components.
"""

import pygame
from pathlib import Path
from config.settings import *
from game.player import Player
from game.camera import Camera
from game.level import Level
from ai.metrics_tracker import MetricsTracker
from ai.skill_predictor import SkillPredictor
from ai.difficulty_adjuster import DifficultyAdjuster


MAX_LEVELS = 5
PLAYER_START_LIVES = 3


HIGH_SCORE_PATH = Path(DATA_DIR) / 'highscore.txt'
DEFAULT_HIGH_SCORE = {'name': 'Kaushik', 'score': 7290}


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
        self.is_paused = False
        
        # Initialize game state
        self.current_level = 0
        self.game_state = 'START_MENU'
        self.lives = PLAYER_START_LIVES
        self.spawn_point = (100, 600)

        # Initialize level system
        self.level = Level(self.current_level)
        self.spawn_point = getattr(self.level, 'spawn_point', self.spawn_point)

        # Initialize player (start on/near ground to avoid immediate fall)
        self.player = Player(*self.spawn_point)

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

        # Score tracking and player identity
        self.high_score_path = HIGH_SCORE_PATH
        self.high_score_info = self.load_highscore()
        self.high_score_message_until = 0
        self.coins_collected_total = 0
        self.enemies_defeated_total = 0
        self.player_name = ""
        self.start_menu_input = ""
        self.start_menu_flash_timer = 0.0
        self.start_menu_prompt_visible = True
        self.should_exit = False
        self.last_run_summary = None
        self.game_complete_message_time = None

        # Performance tracking
        self.elapsed_time = 0.0
        pygame.key.start_text_input()

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

    def load_highscore(self):
        """Load persistent high score and player name from disk."""
        info = DEFAULT_HIGH_SCORE.copy()
        try:
            if self.high_score_path.exists():
                best_score = info['score']
                best_name = info['name']
                for line in self.high_score_path.read_text(encoding='utf-8').splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if ',' in line:
                        name_part, score_part = line.split(',', 1)
                    else:
                        name_part, score_part = '---', line
                    try:
                        score_value = int(score_part.strip())
                    except ValueError:
                        continue
                    if score_value > best_score:
                        best_score = score_value
                        best_name = name_part.strip() or '---'
                info = {'name': best_name, 'score': best_score}
        except Exception as exc:
            print(f"Warning: could not load high score: {exc}")
        return info

    def save_highscore(self, player_name, score):
        """Persist the provided high score entry to disk."""
        try:
            self.high_score_path.parent.mkdir(parents=True, exist_ok=True)
            entry = f"{player_name},{score}\n"
            self.high_score_path.write_text(entry, encoding='utf-8')
        except Exception as exc:
            print(f"Warning: could not save high score: {exc}")

    def update_highscore_if_needed(self):
        """Check the current score against the stored high score."""
        current_score = getattr(self.player, 'score', 0)
        if current_score > self.high_score_info.get('score', 0):
            winner_name = self.player_name.strip() or '---'
            self.high_score_info = {
                'name': winner_name,
                'score': current_score
            }
            self.save_highscore(winner_name, current_score)
            self.high_score_message_until = pygame.time.get_ticks() + 2000

    def start_new_game(self):
        """Begin a new play session after collecting player name."""
        pygame.key.stop_text_input()
        self.current_level = 0
        self.current_difficulty = 'intermediate'
        self.difficulty_params = DIFFICULTY_SETTINGS[self.current_difficulty].copy()
        self.metrics_tracker = MetricsTracker()
        self.level = Level(
            self.current_level,
            difficulty=self.current_difficulty,
            params=self.difficulty_params
        )
        self.spawn_point = getattr(self.level, 'spawn_point', (100, 600))
        self.player = Player(*self.spawn_point)
        self.player.reset_score()
        self.camera = Camera(self.level.width, self.level.height)
        self.coins_collected_total = 0
        self.enemies_defeated_total = 0
        self.elapsed_time = 0.0
        self.game_state = 'PLAYING'
        self.is_paused = False
        self.last_run_summary = None
        self.game_complete_message_time = None
        self.should_exit = False
        self.lives = PLAYER_START_LIVES

    def return_to_start_menu(self):
        """Reset to the start menu to collect a new player name."""
        self.game_state = 'START_MENU'
        self.current_level = 0
        self.player_name = ""
        self.start_menu_input = ""
        self.start_menu_flash_timer = 0.0
        self.start_menu_prompt_visible = True
        self.is_paused = False
        self.last_run_summary = None
        self.coins_collected_total = 0
        self.enemies_defeated_total = 0
        self.elapsed_time = 0.0
        self.game_complete_message_time = None
        self.should_exit = False
        self.lives = PLAYER_START_LIVES
        if hasattr(self, 'player') and self.player:
            self.player.reset_score()
        if hasattr(self, 'metrics_tracker') and self.metrics_tracker:
            self.metrics_tracker.reset_level()
        pygame.key.start_text_input()

    def _update_start_menu(self, dt):
        """Animate start menu prompt flashing."""
        self.start_menu_flash_timer += dt
        if self.start_menu_flash_timer >= 0.5:
            self.start_menu_flash_timer = 0.0
            self.start_menu_prompt_visible = not self.start_menu_prompt_visible

    def _append_player_name_character(self, text):
        """Append printable characters to the start menu name input."""
        for char in text:
            if len(self.start_menu_input) >= 16:
                break
            if char.isprintable() and char not in {'\r', '\n'}:
                self.start_menu_input += char

    def trigger_game_over(self, reason):
        """Switch to the game over screen and capture final stats."""
        self.game_state = 'GAME_OVER'
        self.is_paused = False
        self.update_highscore_if_needed()
        self.last_run_summary = {
            'player_name': self.player_name or '---',
            'score': getattr(self.player, 'score', 0),
            'high_score': self.high_score_info.copy(),
            'level': self.current_level + 1,
            'reason': reason
        }

    def handle_player_death(self, cause):
        """Reduce lives and respawn or end the run when the player dies."""
        cause_messages = {
            'enemy': "Player hit by enemy!",
            'fell': "Player fell!"
        }
        self.metrics_tracker.record_death()
        self.lives -= 1

        if self.lives <= 0:
            self.trigger_game_over(cause)
            message = cause_messages.get(cause, "Player defeated!")
            print(f"{message} No lives remaining.")
            return

        self.player.reset_to_spawn()
        self.camera.update(self.player, 0)
        message = cause_messages.get(cause, "Player defeated!")
        print(f"{message} Respawning... Lives remaining: {self.lives}")
    
    def handle_event(self, event):
        """Handle pygame events for all game states."""
        if event.type == pygame.KEYDOWN:
            if self.game_state == 'START_MENU':
                if event.key == pygame.K_ESCAPE:
                    self.should_exit = True
                elif event.key == pygame.K_RETURN:
                    candidate = self.start_menu_input.strip()
                    if candidate:
                        self.player_name = candidate
                        self.start_new_game()
                elif event.key == pygame.K_BACKSPACE:
                    self.start_menu_input = self.start_menu_input[:-1]
            elif self.game_state == 'PLAYING':
                if event.key == pygame.K_p:
                    self.toggle_pause()
            elif self.game_state == 'PAUSED':
                if event.key == pygame.K_p:
                    self.toggle_pause()
            elif self.game_state == 'GAME_OVER':
                if event.key == pygame.K_r:
                    self.return_to_start_menu()
                elif event.key == pygame.K_ESCAPE:
                    self.should_exit = True
            elif self.game_state == 'GAME_COMPLETE':
                if event.key == pygame.K_ESCAPE:
                    self.should_exit = True
        elif event.type == pygame.TEXTINPUT and self.game_state == 'START_MENU':
            if event.text:
                self._append_player_name_character(event.text)
    
    def toggle_pause(self):
        """Toggle pause state."""
        if self.game_state == 'PLAYING':
            self.game_state = 'PAUSED'
            self.is_paused = True
        elif self.game_state == 'PAUSED':
            self.game_state = 'PLAYING'
            self.is_paused = False
    
    def update(self, dt):
        """
        Update game state and all systems.
        
        Args:
            dt: Delta time in seconds
        """
        if self.game_state == 'START_MENU':
            self._update_start_menu(dt)
            return

        if self.game_state == 'GAME_COMPLETE':
            if (
                self.game_complete_message_time is not None
                and pygame.time.get_ticks() - self.game_complete_message_time > 3000
            ):
                self.should_exit = True
            return

        if self.game_state in {'PAUSED', 'GAME_OVER', 'LEVEL_COMPLETE'}:
            return

        if self.game_state != 'PLAYING':
            return

        if not self.is_paused:
            self.elapsed_time += dt
        
        # Get input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        coins_before = len(self.level.coins)

        # Update player
        self.player.update(dt, self.level.get_collision_platforms())
        
        # Update level entities
        self.level.update(dt, self.player, self.difficulty_params)

        coins_after = len(self.level.coins)
        collected_coins = max(0, coins_before - coins_after)
        if collected_coins:
            self.player.collect_coin(collected_coins)
            self.coins_collected_total += collected_coins
        
        # Check enemy collisions (handle damage)
        for enemy in self.level.enemies:
            was_alive = enemy.alive
            player_hit = enemy.check_player_collision(self.player)

            if was_alive and not enemy.alive:
                self.player.defeat_enemy()
                self.enemies_defeated_total += 1

            if player_hit:
                # Player was hit by enemy - handle life loss
                self.handle_player_death('enemy')
                return
        
        # Track metrics
        self.metrics_tracker.update(self.player, self.level)
        self.metrics_tracker.coins_collected = self.coins_collected_total
        self.metrics_tracker.enemies_defeated = self.enemies_defeated_total
        
        # Update camera
        self.camera.update(self.player, dt)
        
        # Check win/loss conditions
        self.check_game_state()
    
    def check_game_state(self):
        """Check for level completion or game over."""
        # Check if player fell off map
        if self.player.y > self.level.height + 100:
            self.handle_player_death('fell')
            return
        
        # Check if player reached goal
        if self.level.check_goal_reached(self.player):
            self.complete_level()
    
    def complete_level(self):
        """Handle level completion and AI learning."""
        self.game_state = 'LEVEL_COMPLETE'
        
        # Calculate completion time
        completion_time = self.elapsed_time
        
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

        self.update_highscore_if_needed()

        if self.current_level + 1 >= MAX_LEVELS:
            self.game_state = 'GAME_COMPLETE'
            self.game_complete_message_time = pygame.time.get_ticks()
            return
        
        # Move to next level after delay
        pygame.time.wait(3000)
        self.next_level()
    
    def next_level(self):
        """Progress to next level."""
        if self.current_level + 1 >= MAX_LEVELS:
            self.game_state = 'GAME_COMPLETE'
            self.game_complete_message_time = pygame.time.get_ticks()
            return

        self.current_level += 1

        # Generate new level with adjusted difficulty
        self.level = Level(
            self.current_level,
            difficulty=self.current_difficulty,
            params=self.difficulty_params
        )
        self.spawn_point = getattr(self.level, 'spawn_point', self.spawn_point)
        self.player.set_spawn_point(*self.spawn_point)
        
        # Reset player
        self.player.reset_to_spawn()
        
        # Reset camera
        self.camera = Camera(self.level.width, self.level.height)
        
        # Reset metrics
        self.metrics_tracker.reset_level()
        self.coins_collected_total = 0
        self.enemies_defeated_total = 0
        
        # Reset timer
        self.elapsed_time = 0.0
        
        # Resume gameplay
        self.game_state = 'PLAYING'
        self.is_paused = False
        self.should_exit = False
        
        print(f"\nStarting Level {self.current_level + 1} - Difficulty: {self.current_difficulty}")
    
    def restart_level(self):
        """Restart current level."""
        self.lives = PLAYER_START_LIVES
        self.level = Level(
            self.current_level,
            difficulty=self.current_difficulty,
            params=self.difficulty_params
        )
        self.spawn_point = getattr(self.level, 'spawn_point', self.spawn_point)
        self.player.set_spawn_point(*self.spawn_point)
        self.player.reset_to_spawn()
        self.camera = Camera(self.level.width, self.level.height)
        self.metrics_tracker.reset_level()
        self.coins_collected_total = 0
        self.enemies_defeated_total = 0
        self.elapsed_time = 0.0
        self.game_state = 'PLAYING'
        self.is_paused = False
        self.should_exit = False
        print("Level restarted")
    
    def render(self):
        """Render all game elements."""
        if self.game_state == 'START_MENU':
            self.render_start_menu()
            return

        if self.game_state == 'GAME_COMPLETE':
            self.render_game_complete_screen()
            return

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
        if self.game_state == 'PAUSED':
            self.render_pause_screen()
        elif self.game_state == 'GAME_OVER':
            self.render_game_over_screen()
        elif self.game_state == 'LEVEL_COMPLETE':
            self.render_level_complete_screen()
        elif self.game_state == 'GAME_COMPLETE':
            self.render_game_complete_screen()
    
    def render_start_menu(self):
        """Render the animated start menu with name entry."""
        self.screen.fill(SKY_BLUE)

        title_text = self.render_text_outlined(
            self.font_large,
            TITLE,
            (255, 120, 120)
        )
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        prompt_text = self.render_text_outlined(
            self.font_small,
            "Enter your name:",
            (255, 215, 0)
        )
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(prompt_text, prompt_rect)

        input_box = pygame.Rect(0, 0, 420, 56)
        input_box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (40, 20, 20), input_box, border_radius=8)
        pygame.draw.rect(self.screen, (255, 120, 120), input_box, width=3, border_radius=8)

        name_display = self.start_menu_input or "PLAYER"
        name_text = self.render_text_outlined(self.font_small, name_display, (255, 255, 255))
        name_rect = name_text.get_rect(center=input_box.center)
        self.screen.blit(name_text, name_rect)

        if self.start_menu_prompt_visible:
            enter_text = self.render_text_outlined(
                self.font_small,
                "Press ENTER to Start",
                (255, 180, 180)
            )
            enter_rect = enter_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            self.screen.blit(enter_text, enter_rect)

        esc_text = self.render_text_outlined(
            self.font_small,
            "Press ESC to Quit",
            (200, 200, 200)
        )
        esc_rect = esc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        self.screen.blit(esc_text, esc_rect)

        high_info = self.high_score_info
        high_summary = self.render_text_outlined(
            self.font_small,
            f"High Score: {high_info.get('score', 0)} by {high_info.get('name', '---')}",
            (180, 255, 255)
        )
        summary_rect = high_summary.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        self.screen.blit(high_summary, summary_rect)

    def render_ui(self):
        """Render HUD elements with score, level info, and timers."""
        if self.game_state == 'START_MENU':
            return

        left_margin = 15
        top_margin = 15

        score_text = self.render_text_outlined(
            self.font_small,
            f"Score: {self.player.score}",
            (255, 215, 0)
        )
        self.screen.blit(score_text, (left_margin, top_margin))
        y_offset = top_margin + score_text.get_height() + 6

        level_text = self.render_text_outlined(
            self.font_small,
            f"Level: {self.current_level + 1}",
            (255, 120, 120)
        )
        self.screen.blit(level_text, (left_margin, y_offset))
        y_offset += level_text.get_height() + 6

        difficulty_text = self.render_text_outlined(
            self.font_small,
            f"Difficulty: {self.current_difficulty.capitalize()}",
            (220, 100, 100)
        )
        self.screen.blit(difficulty_text, (left_margin, y_offset))
        y_offset += difficulty_text.get_height() + 6

        lives_text = self.render_text_outlined(
            self.font_small,
            f"Lives: {self.lives}",
            (255, 180, 180)
        )
        self.screen.blit(lives_text, (left_margin, y_offset))
        y_offset += lives_text.get_height() + 6

        elapsed = self.elapsed_time
        time_text = self.render_text_outlined(
            self.font_small,
            f"Time: {elapsed:.1f}s",
            (255, 120, 120)
        )

        high_info = self.high_score_info
        high_label = self.render_text_outlined(
            self.font_small,
            f"High Score: {high_info.get('score', 0)} by {high_info.get('name', '---')}",
            (180, 255, 255)
        )
        high_rect = high_label.get_rect(topright=(SCREEN_WIDTH - left_margin, top_margin))
        self.screen.blit(high_label, high_rect)

        time_rect = time_text.get_rect(topright=(SCREEN_WIDTH - left_margin, high_rect.bottom + 6))
        self.screen.blit(time_text, time_rect)

        if pygame.time.get_ticks() < self.high_score_message_until:
            new_high_text = self.render_text_outlined(
                self.font_small,
                "New High Score!",
                (255, 120, 120)
            )
            new_high_rect = new_high_text.get_rect(
                center=(SCREEN_WIDTH // 2, max(high_rect.bottom, time_rect.bottom) + 20)
            )
            self.screen.blit(new_high_text, new_high_rect)
    
    def render_pause_screen(self):
        """Render pause overlay with game-style text."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((30, 20, 20))  # Dark gray-red overlay
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.render_text_outlined(self.font_large, "PAUSED", (255, 200, 100))
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)

        resume_text = self.render_text_outlined(self.font_small, "Press P to Resume", (220, 180, 120))
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(resume_text, resume_rect)
    
    def render_game_over_screen(self):
        """Render game over overlay with dramatic game-style text."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 10, 10))  # Very dark red
        self.screen.blit(overlay, (0, 0))
        
        summary = self.last_run_summary or {
            'player_name': self.player_name or '---',
            'score': getattr(self.player, 'score', 0),
            'high_score': self.high_score_info
        }
        reason = summary.get('reason')
        title = "LEVEL COMPLETE" if reason == 'level_complete' else "GAME OVER"
        title_color = (100, 255, 100) if reason == 'level_complete' else (255, 50, 50)
        game_over_text = self.render_text_outlined(self.font_large, title, title_color)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        self.screen.blit(game_over_text, text_rect)

        info_y = text_rect.bottom + 30
        player_line = self.render_text_outlined(
            self.font_small,
            f"Player: {summary.get('player_name', '---')}",
            (255, 215, 0)
        )
        player_rect = player_line.get_rect(center=(SCREEN_WIDTH // 2, info_y))
        self.screen.blit(player_line, player_rect)

        score_line = self.render_text_outlined(
            self.font_small,
            f"Score: {summary.get('score', 0)}",
            (255, 255, 255)
        )
        score_rect = score_line.get_rect(center=(SCREEN_WIDTH // 2, player_rect.bottom + 30))
        self.screen.blit(score_line, score_rect)

        high_data = summary.get('high_score', self.high_score_info)
        high_line = self.render_text_outlined(
            self.font_small,
            f"High Score: {high_data.get('score', 0)} by {high_data.get('name', '---')}",
            (180, 255, 255)
        )
        high_rect = high_line.get_rect(center=(SCREEN_WIDTH // 2, score_rect.bottom + 30))
        self.screen.blit(high_line, high_rect)

        restart_text = self.render_text_outlined(
            self.font_small,
            "Press R to Restart",
            (220, 180, 100)
        )
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, high_rect.bottom + 60))
        self.screen.blit(restart_text, restart_rect)

        quit_text = self.render_text_outlined(
            self.font_small,
            "Press ESC to Quit",
            (220, 180, 180)
        )
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, restart_rect.bottom + 40))
        self.screen.blit(quit_text, quit_rect)
    
    def render_level_complete_screen(self):
        """Render level complete overlay with victory game-style text."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((50, 30, 30))  # Dark red victory
        self.screen.blit(overlay, (0, 0))
        
        complete_text = self.render_text_outlined(self.font_large, "LEVEL COMPLETE!", (100, 255, 100))
        text_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(complete_text, text_rect)

    def render_game_complete_screen(self):
        """Render the final congratulations screen."""
        self.screen.fill(SKY_BLUE)

        trophy_text = self.render_text_outlined(self.font_large, "CONGRATULATIONS!", (255, 215, 0))
        trophy_rect = trophy_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(trophy_text, trophy_rect)

        message_text = self.render_text_outlined(
            self.font_small,
            "You Finished the Game!",
            (255, 255, 255)
        )
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(message_text, message_rect)

        thanks_text = self.render_text_outlined(
            self.font_small,
            "Thanks for playing!",
            (180, 255, 255)
        )
        thanks_rect = thanks_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(thanks_text, thanks_rect)
    
    def cleanup(self):
        """Clean up resources and save final data."""
        print("\nShutting down game...")
        try:
            pygame.key.stop_text_input()
        except Exception:
            pass
        # Save any remaining metrics
        self.metrics_tracker.cleanup()
        print("Goodbye!")
