"""
Quick diagnostic and testing utility.
Helps verify installation and debug issues.
"""

import sys
import os


def check_python():
    """Check Python version."""
    print("=" * 60)
    print("CHECKING PYTHON VERSION")
    print("=" * 60)
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.8 or higher required")
        return False


def check_dependencies():
    """Check if all dependencies are installed."""
    print("\n" + "=" * 60)
    print("CHECKING DEPENDENCIES")
    print("=" * 60)
    
    dependencies = [
        ('pygame', 'Game engine'),
        ('numpy', 'Numerical computing'),
        ('pandas', 'Data processing'),
        ('sklearn', 'Machine learning'),
        ('torch', 'Deep learning'),
        ('joblib', 'Model persistence'),
        ('PIL', 'Image processing')
    ]
    
    all_installed = True
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✓ {module:15s} - {description}")
        except ImportError:
            print(f"✗ {module:15s} - {description} (NOT INSTALLED)")
            all_installed = False
    
    if all_installed:
        print("\n✓ All dependencies installed correctly")
    else:
        print("\n✗ Some dependencies missing")
        print("Run: pip install -r requirements.txt")
    
    return all_installed


def check_file_structure():
    """Check if all required files exist."""
    print("\n" + "=" * 60)
    print("CHECKING FILE STRUCTURE")
    print("=" * 60)
    
    required_files = [
        'main.py',
        'config/settings.py',
        'game/engine.py',
        'game/player.py',
        'game/camera.py',
        'game/level.py',
        'game/entities.py',
        'ai/metrics_tracker.py',
        'ai/skill_predictor.py',
        'ai/difficulty_adjuster.py',
        'ai/level_gan.py'
    ]
    
    all_exist = True
    
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✓ {filepath}")
        else:
            print(f"✗ {filepath} (MISSING)")
            all_exist = False
    
    if all_exist:
        print("\n✓ All required files present")
    else:
        print("\n✗ Some files missing")
    
    return all_exist


def check_data_directories():
    """Check if data directories exist."""
    print("\n" + "=" * 60)
    print("CHECKING DATA DIRECTORIES")
    print("=" * 60)
    
    directories = [
        'data',
        'data/models',
        'data/levels'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✓ {directory}/")
        else:
            print(f"! {directory}/ (Will be created on first run)")
            os.makedirs(directory, exist_ok=True)
    
    print("\n✓ Data directories ready")
    return True


def check_models():
    """Check if AI models are trained."""
    print("\n" + "=" * 60)
    print("CHECKING AI MODELS")
    print("=" * 60)
    
    models = {
        'data/models/skill_predictor.pkl': 'Random Forest Skill Predictor',
        'data/models/scaler.pkl': 'Feature Scaler',
        'data/models/level_generator.pth': 'GAN Generator',
        'data/models/level_discriminator.pth': 'GAN Discriminator'
    }
    
    models_exist = 0
    
    for filepath, name in models.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024  # KB
            print(f"✓ {name:30s} ({size:.1f} KB)")
            models_exist += 1
        else:
            print(f"! {name:30s} (Not trained yet)")
    
    if models_exist == 0:
        print("\n! No models trained yet")
        print("Run: python train_models.py")
    elif models_exist < len(models):
        print(f"\n! Only {models_exist}/{len(models)} models trained")
        print("Run: python train_models.py")
    else:
        print("\n✓ All AI models trained")
    
    return models_exist > 0


def test_imports():
    """Test if game modules can be imported."""
    print("\n" + "=" * 60)
    print("TESTING MODULE IMPORTS")
    print("=" * 60)
    
    modules = [
        'config.settings',
        'game.engine',
        'game.player',
        'game.camera',
        'game.level',
        'game.entities',
        'ai.metrics_tracker',
        'ai.skill_predictor',
        'ai.difficulty_adjuster',
        'ai.level_gan'
    ]
    
    all_imported = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module} - {str(e)[:50]}")
            all_imported = False
    
    if all_imported:
        print("\n✓ All modules import successfully")
    else:
        print("\n✗ Some modules failed to import")
    
    return all_imported


def test_game_initialization():
    """Test if game can initialize."""
    print("\n" + "=" * 60)
    print("TESTING GAME INITIALIZATION")
    print("=" * 60)
    
    try:
        import pygame
        pygame.init()
        
        # Try to create display
        screen = pygame.display.set_mode((100, 100))
        print("✓ Pygame initialized")
        
        # Try to create game objects
        from game.player import Player
        player = Player(0, 0)
        print("✓ Player created")
        
        from game.camera import Camera
        camera = Camera(1000, 720)
        print("✓ Camera created")
        
        from game.level import Level
        level = Level(0)
        print("✓ Level generated")
        
        pygame.quit()
        
        print("\n✓ Game initialization successful")
        return True
        
    except Exception as e:
        print(f"\n✗ Game initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_system():
    """Test if AI system works."""
    print("\n" + "=" * 60)
    print("TESTING AI SYSTEM")
    print("=" * 60)
    
    try:
        from ai.metrics_tracker import MetricsTracker
        tracker = MetricsTracker()
        print("✓ Metrics tracker created")
        
        from ai.skill_predictor import SkillPredictor
        predictor = SkillPredictor()
        print("✓ Skill predictor created")
        
        from ai.difficulty_adjuster import DifficultyAdjuster
        adjuster = DifficultyAdjuster()
        print("✓ Difficulty adjuster created")
        
        from ai.level_gan import LevelGAN
        gan = LevelGAN()
        print("✓ Level GAN created")
        
        # Test prediction (will use heuristic if not trained)
        test_metrics = {
            'completion_time': 60,
            'jumps': 50,
            'deaths': 2,
            'coins_collected': 10,
            'enemies_defeated': 3,
            'total_distance': 2000,
            'precise_landings': 5,
            'max_speed': 10,
            'air_time_ratio': 0.4,
            'completion_speed': 33
        }
        
        skill = predictor.predict_skill(test_metrics)
        print(f"✓ Skill prediction works: {skill}")
        
        print("\n✓ AI system functional")
        return True
        
    except Exception as e:
        print(f"\n✗ AI system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_full_diagnostic():
    """Run complete diagnostic check."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "AI SONIC PLATFORMER - DIAGNOSTIC" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = {}
    
    results['python'] = check_python()
    results['dependencies'] = check_dependencies()
    results['files'] = check_file_structure()
    results['directories'] = check_data_directories()
    results['models'] = check_models()
    results['imports'] = test_imports()
    results['game_init'] = test_game_initialization()
    results['ai_system'] = test_ai_system()
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print()
    
    if passed == total:
        print("✅ ALL CHECKS PASSED!")
        print("Your game is ready to play!")
        print("\nRun: python main.py")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nFailed checks:")
        for name, result in results.items():
            if not result:
                print(f"  - {name}")
        
        print("\nSuggested fixes:")
        if not results['python']:
            print("  - Upgrade Python to 3.8 or higher")
        if not results['dependencies']:
            print("  - Run: pip install -r requirements.txt")
        if not results['files']:
            print("  - Re-download the project files")
        if not results['models']:
            print("  - Run: python train_models.py (option 4)")
        if not results['imports']:
            print("  - Check for missing dependencies")
        if not results['game_init']:
            print("  - Check error messages above")
        if not results['ai_system']:
            print("  - Install AI dependencies (sklearn, torch)")
    
    print("\n" + "=" * 60)


def quick_fix():
    """Attempt to fix common issues."""
    print("\n" + "=" * 60)
    print("QUICK FIX")
    print("=" * 60)
    
    print("\nCreating missing directories...")
    directories = ['data', 'data/models', 'data/levels', 'assets']
    for d in directories:
        os.makedirs(d, exist_ok=True)
        print(f"✓ {d}/")
    
    print("\nChecking data files...")
    from ai.metrics_tracker import MetricsTracker
    tracker = MetricsTracker()
    tracker.ensure_csv_exists()
    print("✓ Metrics file ready")
    
    print("\n✓ Quick fix complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnostic tool for AI Sonic Platformer')
    parser.add_argument('--quick-fix', action='store_true', help='Attempt to fix common issues')
    parser.add_argument('--test-game', action='store_true', help='Test game initialization only')
    parser.add_argument('--test-ai', action='store_true', help='Test AI system only')
    
    args = parser.parse_args()
    
    if args.quick_fix:
        quick_fix()
    elif args.test_game:
        test_game_initialization()
    elif args.test_ai:
        test_ai_system()
    else:
        run_full_diagnostic()
