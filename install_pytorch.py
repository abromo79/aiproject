#!/usr/bin/env python3
"""
PyTorch Installation Helper Script
This script helps install PyTorch for the breast cancer analysis system.
"""

import subprocess
import sys
import platform

def install_pytorch():
    """Install PyTorch based on system configuration"""
    
    print("🔧 Breast Cancer AI System - PyTorch Installation")
    print("=" * 50)
    
    # Detect system
    system = platform.system().lower()
    print(f"Detected system: {system}")
    
    # Check if PyTorch is already installed
    try:
        import torch
        print("✅ PyTorch is already installed!")
        print(f"Version: {torch.__version__}")
        return True
    except ImportError:
        print("❌ PyTorch not found. Installing...")
    
    # Installation commands based on system
    if system == "windows":
        print("\n📦 Installing PyTorch for Windows (CPU version)...")
        cmd = [sys.executable, "-m", "pip", "install", "torch", "torchvision", "--index-url", "https://download.pytorch.org/whl/cpu"]
    else:
        print("\n📦 Installing PyTorch (CPU version)...")
        cmd = [sys.executable, "-m", "pip", "install", "torch", "torchvision"]
    
    try:
        print("⏳ Please wait, this may take a few minutes...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ PyTorch installed successfully!")
        
        # Verify installation
        try:
            import torch
            print(f"✅ Verification successful! PyTorch version: {torch.__version__}")
            return True
        except ImportError:
            print("❌ Installation verification failed.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main installation function"""
    print("Breast Cancer AI Analysis System")
    print("PyTorch Installation Helper")
    print("=" * 40)
    
    success = install_pytorch()
    
    if success:
        print("\n🎉 Installation Complete!")
        print("You can now use the image analysis feature.")
        print("\nTo start the server:")
        print("  python manage.py runserver")
        print("\nTo access image analysis:")
        print("  http://127.0.0.1:8000/image-predict/")
    else:
        print("\n❌ Installation Failed!")
        print("Please try manual installation:")
        print("  pip install torch torchvision")
        print("\nFor GPU support (if you have CUDA):")
        print("  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")

if __name__ == "__main__":
    main()
