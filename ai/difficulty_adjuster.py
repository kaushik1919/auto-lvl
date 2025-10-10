"""
Dynamic difficulty adjustment system.
Modifies game parameters based on predicted skill level.
"""

import copy
from config.settings import DIFFICULTY_SETTINGS


class DifficultyAdjuster:
    """
    Adjusts game difficulty parameters based on player skill.
    Ensures smooth transitions and balanced gameplay.
    """
    
    def __init__(self):
        """Initialize difficulty adjuster."""
        self.current_params = DIFFICULTY_SETTINGS['intermediate'].copy()
        self.target_params = self.current_params.copy()
        self.transition_progress = 1.0  # 0-1, 1 = fully transitioned
    
    def adjust_difficulty(self, predicted_skill, level_number):
        """
        Calculate difficulty parameters for next level.
        
        Args:
            predicted_skill: Predicted skill level (novice/intermediate/expert)
            level_number: Upcoming level number
            
        Returns:
            Dictionary of difficulty parameters
        """
        # Get base parameters for skill level
        base_params = DIFFICULTY_SETTINGS.get(predicted_skill, 
                                              DIFFICULTY_SETTINGS['intermediate']).copy()
        
        # Apply progressive difficulty scaling based on level number
        # Even within same skill tier, difficulty increases slightly with level
        level_scaling = 1.0 + (level_number * 0.05)  # 5% increase per level
        level_scaling = min(level_scaling, 1.5)  # Cap at 50% increase
        
        # Adjust parameters with level scaling
        adjusted_params = base_params.copy()
        
        # Scale certain parameters with level progression
        adjusted_params['enemy_speed_multiplier'] *= level_scaling
        adjusted_params['trap_density'] = min(adjusted_params['trap_density'] * level_scaling, 1.5)
        
        # Some parameters should decrease with skill
        if predicted_skill == 'expert':
            adjusted_params['checkpoint_frequency'] = max(0.5, 
                                                          adjusted_params['checkpoint_frequency'] / level_scaling)
        
        # Smooth transition from current to target parameters
        self.target_params = adjusted_params
        self.transition_progress = 0.0
        
        print(f"\nDifficulty Parameters for {predicted_skill.upper()} (Level {level_number + 1}):")
        print(f"  Enemy Speed: {adjusted_params['enemy_speed_multiplier']:.2f}x")
        print(f"  Enemy Spawn Rate: {adjusted_params['enemy_spawn_rate']:.2f}x")
        print(f"  Platform Gap: {adjusted_params['platform_gap_multiplier']:.2f}x")
        print(f"  Coin Frequency: {adjusted_params['coin_frequency']:.2f}x")
        print(f"  Trap Density: {adjusted_params['trap_density']:.2f}x")
        
        return adjusted_params
    
    def get_smooth_params(self, dt):
        """
        Get parameters with smooth transition applied.
        
        Args:
            dt: Delta time for transition
            
        Returns:
            Current difficulty parameters
        """
        if self.transition_progress < 1.0:
            # Smooth interpolation
            self.transition_progress = min(1.0, self.transition_progress + dt * 0.5)
            
            # Lerp between current and target
            smoothed_params = {}
            for key in self.current_params:
                current_val = self.current_params[key]
                target_val = self.target_params[key]
                smoothed_val = current_val + (target_val - current_val) * self.transition_progress
                smoothed_params[key] = smoothed_val
            
            return smoothed_params
        else:
            return self.target_params
    
    def finalize_transition(self):
        """Complete the transition to target parameters."""
        self.current_params = self.target_params.copy()
        self.transition_progress = 1.0
    
    def get_adaptive_spawn_rate(self, base_rate, skill_level):
        """
        Calculate adaptive spawn rate for entities.
        
        Args:
            base_rate: Base spawn probability
            skill_level: Current skill level
            
        Returns:
            Adjusted spawn rate
        """
        multiplier = self.current_params.get('enemy_spawn_rate', 1.0)
        return base_rate * multiplier
    
    def get_adaptive_enemy_speed(self, base_speed, skill_level):
        """
        Calculate adaptive enemy speed.
        
        Args:
            base_speed: Base enemy speed
            skill_level: Current skill level
            
        Returns:
            Adjusted speed
        """
        multiplier = self.current_params.get('enemy_speed_multiplier', 1.0)
        return base_speed * multiplier
    
    def should_spawn_coin(self, base_probability):
        """
        Determine if a coin should spawn based on difficulty.
        
        Args:
            base_probability: Base probability (0-1)
            
        Returns:
            Boolean indicating if coin should spawn
        """
        import random
        adjusted_prob = base_probability * self.current_params.get('coin_frequency', 1.0)
        return random.random() < adjusted_prob
    
    def get_platform_gap_size(self, base_gap):
        """
        Calculate platform gap size based on difficulty.
        
        Args:
            base_gap: Base gap distance
            
        Returns:
            Adjusted gap size
        """
        multiplier = self.current_params.get('platform_gap_multiplier', 1.0)
        return base_gap * multiplier
