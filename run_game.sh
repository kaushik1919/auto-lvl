#!/bin/bash
# Quick start script for AI Sonic Platformer (Linux/Mac)

echo "========================================"
echo "AI-Driven Sonic Platformer - Quick Start"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Running setup..."
    python3 setup.py
    echo ""
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "Checking dependencies..."
python -c "import pygame" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if models are trained
if [ ! -f "data/models/skill_predictor.pkl" ]; then
    echo ""
    echo "No trained models found!"
    echo "Would you like to generate training data and train models? (y/n)"
    read -r train
    if [ "$train" = "y" ] || [ "$train" = "Y" ]; then
        echo ""
        echo "Generating synthetic data and training models..."
        python -c "import sys; sys.path.insert(0, '.'); from train_models import generate_synthetic_training_data, train_skill_predictor, train_level_gan; generate_synthetic_training_data(); train_skill_predictor(); train_level_gan()"
    fi
fi

echo ""
echo "========================================"
echo "Starting game..."
echo "========================================"
echo ""

# Run the game
python main.py

echo ""
echo "Game closed. Thanks for playing!"
