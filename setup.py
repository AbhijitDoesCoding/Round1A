#!/usr/bin/env python3
"""
Setup script for the PDF Outline Extractor solution
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        sys.exit(1)

def main():
    """Main setup function"""
    print("🚀 Setting up PDF Outline Extractor...")
    
    # Create necessary directories
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # Install requirements
    install_requirements()
    
    print("\n✅ Setup complete!")
    print("\nUsage:")
    print("python3 round1a_outline_extractor.py input/ output/")

if __name__ == "__main__":
    main()