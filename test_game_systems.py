"""Quick test to verify game systems work correctly."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")
try:
    from config.settings import *
    print("✓ Config imported")
    
    from game.player import Player
    print("✓ Player imported")
    
    from game.entities import Platform, Coin, Enemy, Goal
    print("✓ Entities imported")
    
    from ai.metrics_tracker import MetricsTracker
    print("✓ Metrics tracker imported")
    
    print("\nTesting metrics tracker...")
    tracker = MetricsTracker()
    print(f"✓ Tracker initialized - Deaths: {tracker.deaths}, Coins: {tracker.coins_collected}")
    
    print("\nTesting player creation...")
    player = Player(100, 600)
    print(f"✓ Player created at ({player.x}, {player.y})")
    
    print("\nTesting enemy creation...")
    enemy = Enemy(200, 600, 'walker', 1.0)
    print(f"✓ Enemy created - Alive: {enemy.alive}")
    
    print("\nTesting goal creation...")
    goal = Goal(1000, 500)
    print(f"✓ Goal created at ({goal.x}, {goal.y})")
    
    print("\n" + "="*50)
    print("All systems operational!")
    print("="*50)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
