"""
AI model training script.
Trains both Random Forest and GAN models on collected data.
"""

import os
import sys
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.skill_predictor import SkillPredictor
from ai.level_gan import LevelGAN
from game.level import Level
from config.settings import METRICS_FILE, MIN_TRAINING_SAMPLES


def train_skill_predictor():
    """Train the Random Forest skill predictor."""
    print("\n" + "=" * 60)
    print("TRAINING SKILL PREDICTOR (Random Forest)")
    print("=" * 60)
    
    # Check if we have data
    if not os.path.exists(METRICS_FILE):
        print(f"No metrics data found at {METRICS_FILE}")
        print("Play some games to collect training data!")
        return False
    
    # Load data
    df = pd.read_csv(METRICS_FILE)
    print(f"\nFound {len(df)} gameplay sessions")
    
    if len(df) < MIN_TRAINING_SAMPLES:
        print(f"Need at least {MIN_TRAINING_SAMPLES} samples to train")
        print(f"Current: {len(df)} samples")
        print("Play more games to collect more data!")
        return False
    
    # Show data distribution
    print("\nSkill Level Distribution:")
    for skill, count in df['skill_level'].value_counts().items():
        print(f"  {skill}: {count}")
    
    # Train model
    predictor = SkillPredictor()
    success = predictor.train_model(force_retrain=True)
    
    if success:
        print("\n✓ Skill predictor trained successfully!")
    else:
        print("\n✗ Failed to train skill predictor")
    
    return success


def generate_synthetic_training_data():
    """Generate synthetic training data for initial model training."""
    print("\n" + "=" * 60)
    print("GENERATING SYNTHETIC TRAINING DATA")
    print("=" * 60)
    
    from ai.metrics_tracker import MetricsTracker
    
    tracker = MetricsTracker()
    
    # Generate novice-level data
    print("\nGenerating novice player data...")
    for i in range(15):
        metrics = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'level': i % 3,
            'completion_time': np.random.uniform(60, 120),
            'jumps': np.random.randint(50, 100),
            'deaths': np.random.randint(3, 10),
            'coins_collected': np.random.randint(0, 5),
            'enemies_defeated': np.random.randint(0, 2),
            'total_distance': np.random.uniform(1000, 2000),
            'precise_landings': np.random.randint(0, 3),
            'max_speed': np.random.uniform(4, 8),
            'air_time_ratio': np.random.uniform(0.2, 0.4),
            'completion_speed': np.random.uniform(15, 30),
            'skill_level': 'novice'
        }
        tracker.save_metrics(metrics)
    
    # Generate intermediate-level data
    print("Generating intermediate player data...")
    for i in range(15):
        metrics = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'level': i % 3,
            'completion_time': np.random.uniform(30, 60),
            'jumps': np.random.randint(30, 60),
            'deaths': np.random.randint(0, 3),
            'coins_collected': np.random.randint(5, 12),
            'enemies_defeated': np.random.randint(2, 5),
            'total_distance': np.random.uniform(2000, 3000),
            'precise_landings': np.random.randint(3, 8),
            'max_speed': np.random.uniform(8, 11),
            'air_time_ratio': np.random.uniform(0.3, 0.5),
            'completion_speed': np.random.uniform(40, 70),
            'skill_level': 'intermediate'
        }
        tracker.save_metrics(metrics)
    
    # Generate expert-level data
    print("Generating expert player data...")
    for i in range(15):
        metrics = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'level': i % 3,
            'completion_time': np.random.uniform(15, 30),
            'jumps': np.random.randint(15, 35),
            'deaths': np.random.randint(0, 1),
            'coins_collected': np.random.randint(10, 20),
            'enemies_defeated': np.random.randint(4, 8),
            'total_distance': np.random.uniform(2500, 3500),
            'precise_landings': np.random.randint(8, 15),
            'max_speed': np.random.uniform(10, 13),
            'air_time_ratio': np.random.uniform(0.4, 0.6),
            'completion_speed': np.random.uniform(80, 120),
            'skill_level': 'expert'
        }
        tracker.save_metrics(metrics)
    
    print(f"\n✓ Generated 45 synthetic training samples")
    print(f"Saved to {METRICS_FILE}")


def train_level_gan():
    """Train the GAN for level generation."""
    print("\n" + "=" * 60)
    print("TRAINING LEVEL GAN")
    print("=" * 60)
    
    # Create GAN
    gan = LevelGAN()
    
    # Generate training templates from existing levels
    print("\nGenerating level templates for training...")
    
    level_templates = []
    
    # Create template levels
    for level_num in range(3):
        for difficulty in ['novice', 'intermediate', 'expert']:
            level = Level(level_num, difficulty)
            
            # Encode level to vector
            encoded = gan.encode_level_template(
                level.platforms,
                level.coins,
                level.enemies
            )
            
            level_templates.append(encoded)
    
    print(f"Created {len(level_templates)} level templates")
    
    # Train GAN
    if len(level_templates) >= 5:
        gan.train(level_templates, epochs=50, batch_size=min(8, len(level_templates)))
        print("\n✓ GAN trained successfully!")
        return True
    else:
        print("\n✗ Not enough level templates for training")
        return False


def test_predictions():
    """Test the trained models."""
    print("\n" + "=" * 60)
    print("TESTING TRAINED MODELS")
    print("=" * 60)
    
    # Test skill predictor
    print("\nTesting Skill Predictor...")
    predictor = SkillPredictor()
    
    # Test cases
    test_cases = [
        {
            'name': 'Novice Player',
            'metrics': {
                'completion_time': 90,
                'jumps': 80,
                'deaths': 8,
                'coins_collected': 2,
                'enemies_defeated': 0,
                'total_distance': 1500,
                'precise_landings': 1,
                'max_speed': 6,
                'air_time_ratio': 0.25,
                'completion_speed': 18
            }
        },
        {
            'name': 'Expert Player',
            'metrics': {
                'completion_time': 20,
                'jumps': 25,
                'deaths': 0,
                'coins_collected': 18,
                'enemies_defeated': 7,
                'total_distance': 3000,
                'precise_landings': 12,
                'max_speed': 12,
                'air_time_ratio': 0.55,
                'completion_speed': 150
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        prediction = predictor.predict_skill(test['metrics'])
        print(f"  Predicted: {prediction}")
    
    # Test GAN
    print("\n\nTesting Level GAN...")
    gan = LevelGAN()
    
    if gan.is_trained:
        for difficulty in ['novice', 'intermediate', 'expert']:
            level_data = gan.generate_level(difficulty)
            print(f"\n{difficulty.capitalize()} Level:")
            print(f"  Platforms: {len(level_data['platforms'])}")
            print(f"  Coins: {len(level_data['coins'])}")
            print(f"  Enemies: {len(level_data['enemies'])}")
    else:
        print("GAN not trained yet")


def main():
    """Main training function."""
    print("=" * 60)
    print("AI MODEL TRAINING SYSTEM")
    print("=" * 60)
    
    print("\nOptions:")
    print("1. Generate synthetic training data")
    print("2. Train Random Forest skill predictor")
    print("3. Train Level GAN")
    print("4. Train all models")
    print("5. Test models")
    print("0. Exit")
    
    choice = input("\nEnter choice: ").strip()
    
    if choice == '1':
        generate_synthetic_training_data()
    elif choice == '2':
        train_skill_predictor()
    elif choice == '3':
        train_level_gan()
    elif choice == '4':
        generate_synthetic_training_data()
        train_skill_predictor()
        train_level_gan()
        test_predictions()
    elif choice == '5':
        test_predictions()
    elif choice == '0':
        print("Exiting...")
        return 0
    else:
        print("Invalid choice")
        return 1
    
    print("\nTraining complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
