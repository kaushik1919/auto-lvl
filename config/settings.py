# Game Configuration Settings

# Display Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "AI Sonic Platformer"

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

# AI/ML Settings
METRICS_FILE = 'data/player_metrics.csv'
MODEL_DIR = 'data/models/'
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
