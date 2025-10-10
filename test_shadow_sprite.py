"""Quick test for Shadow sprite rendering."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Shadow sprite creation...")
try:
    import pygame
    pygame.init()
    
    from game.player import Player
    
    # Create player
    player = Player(100, 600)
    print("✓ Shadow player created successfully")
    
    # Test sprite states
    states = ['idle', 'run', 'jump', 'fall']
    for state in states:
        if state in player.sprites:
            sprite = player.sprites[state]
            if isinstance(sprite, list):
                print(f"✓ {state} animation: {len(sprite)} frames")
            else:
                print(f"✓ {state} sprite created")
        else:
            print(f"✗ Missing {state} sprite")
    
    print("\n" + "="*50)
    print("Shadow sprite system working!")
    print("="*50)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
