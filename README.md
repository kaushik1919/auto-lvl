# AI-Driven Adaptive Platformer

A 2D platformer featuring Shadow the Hedgehog with intelligent adaptive difficulty using machine learning.

## Requirements

- Python 3.8 or higher
- 4GB RAM minimum

## Installation

1. Create and activate virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Running the Game

```powershell
python main.py
```

Or use the provided script:

```powershell
.\run_game.bat
```

## Controls

- Arrow Keys / WASD - Move
- Space / Up Arrow - Jump
- ESC - Pause
- R - Restart (when game over)

## How It Works

The game tracks your performance (jumps, deaths, coins, completion time) and uses machine learning to adapt difficulty:

- Random Forest classifier predicts skill level (novice/intermediate/expert)
- Difficulty parameters adjust automatically based on your performance
- GAN generates procedurally adapted levels after level 3
- All data stored locally in data/player_metrics.csv

## Training AI Models

Optional but recommended for better difficulty adaptation:

```powershell
python train_models.py
```

Choose option 4 for quick synthetic training (2-3 minutes).

## Troubleshooting

If the game won't start:

1. Check Python version: `python --version` (should be 3.8+)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Run diagnostics: `python diagnostic.py`

## File Structure

```
game/           - Core game engine and entities
ai/             - Machine learning modules
config/         - Game settings
data/           - Saved metrics and trained models
```

## Features

- Adaptive AI difficulty system
- Procedural level generation
- Performance tracking and analytics
- Machine learning-based skill prediction
- Smooth camera with parallax scrolling
- Particle effects and animations
