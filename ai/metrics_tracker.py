"""
Player performance metrics tracking system.
Collects and analyzes gameplay data for machine learning.
"""

import pandas as pd
import os
import time
from datetime import datetime
from config.settings import METRICS_FILE


class MetricsTracker:
    """
    Tracks player performance metrics during gameplay.
    Collects data for skill prediction and difficulty adjustment.
    """
    
    def __init__(self):
        """Initialize metrics tracker."""
        # Current level metrics
        self.jumps = 0
        self.deaths = 0
        self.coins_collected = 0
        self.enemies_defeated = 0
        self.total_distance = 0
        self.precise_landings = 0  # Landings near platform edge
        
        # Performance tracking
        self.last_player_x = 0
        self.max_speed_reached = 0
        self.air_time = 0
        self.ground_time = 0
        
        # Initialize CSV if it doesn't exist
        self.ensure_csv_exists()
    
    def ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist.

        This method is defensive: if the configured `METRICS_FILE` parent
        directory can't be created (common when the EXE runs from a
        read-only location), it falls back to a per-user directory under the
        user's home directory and updates the module-level `METRICS_FILE` so
        that subsequent reads/writes go to a writable location.
        """
        global METRICS_FILE
        try:
            from pathlib import Path

            metrics_path = Path(METRICS_FILE)
            parent = metrics_path.parent

            # If parent is empty (relative path without folder), use project CWD
            if str(parent) == '' or str(parent) == '.':
                parent = Path('.')

            # Try to create the directory where METRICS_FILE points
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                # Fall back to the user's home local data folder
                fallback = Path(os.path.expanduser('~')) / '.level-gen' / 'data'
                try:
                    fallback.mkdir(parents=True, exist_ok=True)
                    metrics_path = fallback / metrics_path.name
                    METRICS_FILE = str(metrics_path)
                    parent = fallback
                except Exception as e2:
                    print(f"Warning: could not create fallback metrics directory '{fallback}': {e2}")
                    print(f"Original error creating '{parent}': {e}")
        except Exception as e:
            print(f"Warning: metrics directory setup failed: {e}")

        if not os.path.exists(METRICS_FILE):
            df = pd.DataFrame(columns=[
                'timestamp',
                'level',
                'completion_time',
                'jumps',
                'deaths',
                'coins_collected',
                'enemies_defeated',
                'total_distance',
                'precise_landings',
                'max_speed',
                'air_time_ratio',
                'completion_speed',
                'skill_level'
            ])
            df.to_csv(METRICS_FILE, index=False)
            print(f"Created metrics file: {METRICS_FILE}")
        else:
            # Helpful debug: show where metrics are expected to be written
            print(f"Metrics file already exists or will be at: {METRICS_FILE}")
    
    def update(self, player, level):
        """
        Update metrics based on current game state.
        
        Args:
            player: Player object
            level: Current level object
        """
        # Track jump
        if not player.on_ground and player.vel_y < 0:
            # Only count when just jumped (velocity is negative and was on ground)
            if hasattr(self, '_was_on_ground') and self._was_on_ground:
                self.jumps += 1
        
        self._was_on_ground = player.on_ground
        
        # Track distance traveled
        distance_delta = abs(player.x - self.last_player_x)
        self.total_distance += distance_delta
        self.last_player_x = player.x
        
        # Track max speed
        current_speed = abs(player.vel_x)
        self.max_speed_reached = max(self.max_speed_reached, current_speed)
        
        # Track air/ground time
        if player.on_ground:
            self.ground_time += 1
        else:
            self.air_time += 1
        
        # Track coin collection
        initial_coins = self.coins_collected
        self.coins_collected = sum(1 for coin in level.coins if coin.collected)
        
        # Track enemy defeats
        initial_enemies = self.enemies_defeated
        self.enemies_defeated = sum(1 for enemy in level.enemies if not enemy.alive)
        
        # Track precise landings (landing near edge of platform)
        if player.on_ground and hasattr(self, '_was_airborne') and self._was_airborne:
            for platform in level.platforms:
                if player.rect.colliderect(platform.rect):
                    # Check if landing near edge
                    edge_threshold = 20
                    player_center = player.rect.centerx
                    
                    if (abs(player_center - platform.rect.left) < edge_threshold or
                        abs(player_center - platform.rect.right) < edge_threshold):
                        self.precise_landings += 1
                    break
        
        self._was_airborne = not player.on_ground
    
    def record_death(self):
        """Record a player death."""
        self.deaths += 1
    
    def get_level_summary(self, level_number, completion_time):
        """
        Get summary of level performance.
        
        Args:
            level_number: Completed level index
            completion_time: Time to complete in seconds
            
        Returns:
            Dictionary of metrics
        """
        # Calculate derived metrics
        air_time_ratio = self.air_time / max(self.air_time + self.ground_time, 1)
        completion_speed = self.total_distance / max(completion_time, 1)
        
        # Determine skill level (will be overridden by ML model)
        skill_level = self._estimate_skill_level(completion_time)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'level': level_number,
            'completion_time': round(completion_time, 2),
            'jumps': self.jumps,
            'deaths': self.deaths,
            'coins_collected': self.coins_collected,
            'enemies_defeated': self.enemies_defeated,
            'total_distance': round(self.total_distance, 2),
            'precise_landings': self.precise_landings,
            'max_speed': round(self.max_speed_reached, 2),
            'air_time_ratio': round(air_time_ratio, 3),
            'completion_speed': round(completion_speed, 2),
            'skill_level': skill_level
        }
    
    def _estimate_skill_level(self, completion_time):
        """
        Simple heuristic skill estimation (fallback).
        
        Args:
            completion_time: Seconds to complete level
            
        Returns:
            Skill level string
        """
        # Score based on performance
        score = 0
        
        # Fast completion
        if completion_time < 30:
            score += 3
        elif completion_time < 60:
            score += 2
        else:
            score += 1
        
        # Low deaths
        if self.deaths == 0:
            score += 3
        elif self.deaths <= 2:
            score += 2
        else:
            score += 1
        
        # Coin collection
        if self.coins_collected > 10:
            score += 2
        elif self.coins_collected > 5:
            score += 1
        
        # Precise landings
        if self.precise_landings > 5:
            score += 2
        elif self.precise_landings > 2:
            score += 1
        
        # Map score to skill level
        if score >= 8:
            return 'expert'
        elif score >= 5:
            return 'intermediate'
        else:
            return 'novice'
    
    def save_metrics(self, metrics_dict):
        """
        Save metrics to CSV file.
        
        Args:
            metrics_dict: Dictionary of metrics to save
        """
        try:
            # Read existing data
            df = pd.read_csv(METRICS_FILE)
            
            # Append new row
            new_row = pd.DataFrame([metrics_dict])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save back to CSV
            df.to_csv(METRICS_FILE, index=False)
            
            print(f"Metrics saved to {METRICS_FILE}")
            
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def reset_level(self):
        """Reset metrics for new level."""
        self.jumps = 0
        self.deaths = 0
        self.coins_collected = 0
        self.enemies_defeated = 0
        self.total_distance = 0
        self.precise_landings = 0
        self.last_player_x = 0
        self.max_speed_reached = 0
        self.air_time = 0
        self.ground_time = 0
        
        # Reset tracking flags
        self._was_on_ground = False
        self._was_airborne = False
    
    def cleanup(self):
        """Clean up resources."""
        print("Metrics tracker cleaned up")
    
    def load_historical_data(self):
        """
        Load all historical metrics data.
        
        Returns:
            Pandas DataFrame of all metrics
        """
        try:
            if os.path.exists(METRICS_FILE):
                return pd.read_csv(METRICS_FILE)
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"Error loading metrics: {e}")
            return pd.DataFrame()
