"""
Main entry point for the AI-Driven Adaptive Sonic Platformer.
Initializes the game engine and starts the main game loop.
"""

import pygame
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.engine import GameEngine
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE


def main():
    """Initialize and run the game."""
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()
    
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    
    # Create game engine
    engine = GameEngine(screen)
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    print("=" * 60)
    print(TITLE)
    print("=" * 60)
    print("Controls:")
    print("  Arrow Keys / WASD - Move")
    print("  Space / Up Arrow - Jump")
    print("  P - Pause / Resume")
    print("  ESC - Quit (Menus)")
    print("=" * 60)
    print("Starting game...")
    print()
    
    while running:
        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            engine.handle_event(event)

        if getattr(engine, "should_exit", False):
            running = False
        
        # Update game state
        engine.update(dt)
        
        # Render
        engine.render()
        pygame.display.flip()
    
    # Cleanup
    engine.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
