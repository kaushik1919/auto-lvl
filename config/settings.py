# Game Configuration Settings

# Display Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Optimus Prime: Adaptive Platformer"

# Physics Constants
GRAVITY = 0.8
MAX_FALL_SPEED = 15
GROUND_FRICTION = 0.85
AIR_FRICTION = 0.95

# Player Physics (Sonic-style)
PLAYER_ACCELERATION = 0.6
PLAYER_MAX_SPEED = 12
PLAYER_JUMP_POWER = 16
PLAYER_SIZE = (48, 64)  # Increased size for better visibility
CHARACTER_SPRITE = "optimus_prime"

# Camera Settings
CAMERA_SMOOTH = 0.1
CAMERA_DEADZONE_WIDTH = 300
CAMERA_DEADZONE_HEIGHT = 200

# Parallax Layers
PARALLAX_SPEEDS = [0.2, 0.4, 0.6, 0.8]

# Difficulty Parameters (Base values)
DIFFICULTY_SETTINGS = {
    'novice': {
        'enemy_speed_multiplier': 0.6,
        'enemy_spawn_rate': 0.5,
        'platform_gap_multiplier': 0.7,
        'coin_frequency': 1.5,
        'trap_density': 0.3,
        'checkpoint_frequency': 1.5
    },
    'intermediate': {
        'enemy_speed_multiplier': 1.0,
        'enemy_spawn_rate': 1.0,
        'platform_gap_multiplier': 1.0,
        'coin_frequency': 1.0,
        'trap_density': 0.6,
        'checkpoint_frequency': 1.0
    },
    'expert': {
        'enemy_speed_multiplier': 1.5,
        'enemy_spawn_rate': 1.5,
        'platform_gap_multiplier': 1.3,
        'coin_frequency': 0.7,
        'trap_density': 1.0,
        'checkpoint_frequency': 0.7
    }
}

import sys
import os
from pathlib import Path

# AI/ML Settings
# Determine a writable data directory. Prefer the project's `data/` folder when
# it already exists and is writable (developer runs). Otherwise fall back to
# the user's Local App Data folder on Windows or the home directory on other OSes.
BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DATA = BASE_DIR / 'data'

def _choose_data_dir():
    # If project data exists and is writable, use it (convenient for dev).
    try:
        if PROJECT_DATA.exists() and os.access(str(PROJECT_DATA), os.W_OK):
            return PROJECT_DATA
    except Exception:
        # Fall through to user directory
        pass

    # Fallback: use a per-user location
    if sys.platform.startswith('win'):
        user_base = os.getenv('LOCALAPPDATA') or os.path.expanduser('~')
    else:
        user_base = os.getenv('XDG_DATA_HOME') or os.path.expanduser('~')

    return Path(user_base) / 'level-gen' / 'data'

DATA_DIR = Path(_choose_data_dir())
# Resolve to an absolute, user-writable path. In frozen EXEs __file__ can be
# in a read-only bundle or an unexpected location, so ensure we have an
# absolute, expanded path and fall back to the user's home directory when
# creation fails.
try:
    DATA_DIR = DATA_DIR.expanduser().resolve()
except Exception:
    DATA_DIR = Path(os.path.expanduser('~')) / '.level-gen' / 'data'

# Ensure the directory exists (safe; will create in user-writable location)
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    # If directory creation fails, fallback to a safe location in the user's
    # home directory and ensure that exists.
    DATA_DIR = Path(os.path.expanduser('~')) / '.level-gen' / 'data'
    DATA_DIR.mkdir(parents=True, exist_ok=True)

METRICS_FILE = str(DATA_DIR / 'player_metrics.csv')
MODEL_DIR = str(DATA_DIR / 'models') + os.sep
RETRAIN_THRESHOLD = 5  # Retrain after N level completions
MIN_TRAINING_SAMPLES = 10

# Level Generation
LEVEL_WIDTH = 5000
LEVEL_HEIGHT = 720
TILE_SIZE = 32
GAN_LATENT_DIM = 100

# Colors - Red/Black Theme
SKY_BLUE = (20, 10, 15)  # Dark background
GRASS_GREEN = (40, 0, 0)  # Dark red ground
PLATFORM_GRAY = (60, 10, 10)  # Dark red platforms
COIN_GOLD = (255, 50, 50)  # Bright red coins
ENEMY_RED = (200, 0, 0)  # Crimson enemies
PLAYER_BLUE = (255, 20, 20)  # Bright red Sonic

# Additional theme colors
DARK_RED = (100, 0, 0)
BLOOD_RED = (180, 0, 0)
CRIMSON = (220, 20, 60)
BLACK = (10, 10, 10)
GLOW_RED = (255, 100, 100)

# Particle Effects
PARTICLE_LIFETIME = 30
PARTICLE_COUNT = 10
