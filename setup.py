"""
Setup and installation script for the AI-Driven Sonic Platformer.
Helps users set up the environment and install dependencies.
"""

import subprocess
import sys
import os


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} detected")
    return True


def create_virtual_environment():
    """Create a virtual environment."""
    print("\nCreating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to create virtual environment")
        return False


def install_dependencies():
    """Install required packages."""
    print("\nInstalling dependencies...")
    
    # Determine pip path based on OS
    if sys.platform == "win32":
        pip_path = os.path.join("venv", "Scripts", "pip.exe")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
    
    # Upgrade pip first
    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        print("✓ Pip upgraded")
    except:
        print("⚠ Could not upgrade pip, continuing...")
    
    # Install requirements
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        print("\nYou can manually install with:")
        print(f"  {pip_path} install -r requirements.txt")
        return False


def create_data_directories():
    """Create necessary data directories."""
    print("\nCreating data directories...")
    
    directories = [
        "data",
        "data/models",
        "data/levels",
        "assets",
        "assets/sprites",
        "assets/sounds",
        "assets/music"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✓ Data directories created")
    return True


def print_next_steps():
    """Print instructions for running the game."""
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nTo run the game:")
    
    if sys.platform == "win32":
        print("  1. Activate virtual environment:")
        print("     venv\\Scripts\\activate")
        print("\n  2. Run the game:")
        print("     python main.py")
    else:
        print("  1. Activate virtual environment:")
        print("     source venv/bin/activate")
        print("\n  2. Run the game:")
        print("     python main.py")
    
    print("\n" + "=" * 60)
    print("CONTROLS:")
    print("  Arrow Keys / WASD - Move")
    print("  Space / Up Arrow  - Jump")
    print("  ESC               - Pause")
    print("=" * 60)
    print("\nThe game will automatically learn from your playstyle!")
    print("Enjoy the adaptive difficulty experience!\n")


def main():
    """Main setup function."""
    print("=" * 60)
    print("AI-Driven Sonic Platformer - Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    if not create_data_directories():
        return 1
    
    # Ask if user wants to create venv
    print("\nWould you like to create a virtual environment? (recommended)")
    response = input("Create venv? (y/n): ").lower().strip()
    
    if response == 'y':
        if not create_virtual_environment():
            print("\nContinuing without virtual environment...")
        else:
            if not install_dependencies():
                return 1
    else:
        print("\nSkipping virtual environment creation.")
        print("Make sure to install dependencies manually:")
        print("  pip install -r requirements.txt")
    
    # Print next steps
    print_next_steps()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
