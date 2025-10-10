@echo off
REM Quick start script for AI Sonic Platformer (Windows)

echo ========================================
echo AI-Driven Sonic Platformer - Quick Start
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Running setup...
    python setup.py
    echo.
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import pygame" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check if models are trained
if not exist "data\models\skill_predictor.pkl" (
    echo.
    echo No trained models found!
    echo Would you like to generate training data and train models? (y/n)
    set /p train=
    if /i "%train%"=="y" (
        echo.
        echo Generating synthetic data and training models...
        python -c "import sys; sys.path.insert(0, '.'); from train_models import generate_synthetic_training_data, train_skill_predictor, train_level_gan; generate_synthetic_training_data(); train_skill_predictor(); train_level_gan()"
    )
)

echo.
echo ========================================
echo Starting game...
echo ========================================
echo.

REM Run the game
python main.py

echo.
echo Game closed. Thanks for playing!
pause
