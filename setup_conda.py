#!/usr/bin/env python3
"""
Setup script for conda environment in PyCharm.
Installs required packages and configures the environment.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_conda():
    """Check if conda is available."""
    try:
        result = subprocess.run(['conda', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Conda found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Conda not found in PATH")
            return False
    except FileNotFoundError:
        print("❌ Conda not found. Please install Anaconda or Miniconda.")
        return False

def get_current_env():
    """Get the current conda environment name."""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'base')
    print(f"Current conda environment: {conda_env}")
    return conda_env

def install_packages():
    """Install required packages from requirements.txt."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print("📦 Installing packages from requirements.txt...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All packages installed successfully")
            if result.stdout:
                print("Installation output:")
                print(result.stdout)
            return True
        else:
            print(f"❌ Package installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_installed_packages():
    """Check if all required packages are installed."""
    print("🔍 Checking installed packages...")
    
    required_packages = {
        'matplotlib': 'matplotlib',
        'numpy': 'numpy', 
        'pandas': 'pandas',
        'seaborn': 'seaborn',
        'yaml': 'pyyaml',
        'jupyter': 'jupyter'
    }
    
    all_installed = True
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} not found")
            all_installed = False
    
    return all_installed

def create_conda_env_file():
    """Create a conda environment.yml file for the project."""
    env_content = """name: paper2
channels:
  - conda-forge
  - defaults
dependencies:
  - python>=3.8
  - matplotlib>=3.5
  - numpy>=1.20
  - pandas>=1.3
  - seaborn>=0.11
  - pyyaml>=5.4
  - jupyter
  - jupyterlab
  - pip
  - pip:
    - # Add any pip-only packages here
"""
    
    env_file = Path(__file__).parent / "environment.yml"
    
    if env_file.exists():
        print(f"📄 Environment file already exists: {env_file}")
        return str(env_file)
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created conda environment file: {env_file}")
        return str(env_file)
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return None

def setup_pycharm_config():
    """Setup PyCharm configuration hints."""
    print("\n" + "=" * 50)
    print("PYCHARM CONFIGURATION")
    print("=" * 50)
    
    print("To configure PyCharm for this conda environment:")
    print()
    print("1. File → Settings → Project → Python Interpreter")
    print("2. Add Interpreter → Conda Environment → Existing environment")
    print(f"3. Select Python executable from your conda environment")
    print()
    print("Environment variables to add in Run Configurations:")
    print("  MPLBACKEND=Agg")
    print("  PYTHONUNBUFFERED=1")
    print()
    print("Working directory should be set to:")
    print(f"  {Path(__file__).parent}")
    print()

def main():
    """Main setup function."""
    print("Paper2 Conda Environment Setup")
    print("=" * 50)
    
    # Check conda availability
    if not check_conda():
        return 1
    
    # Get current environment
    current_env = get_current_env()
    
    # Check current packages
    if check_installed_packages():
        print("✅ All required packages are already installed!")
    else:
        print("📦 Some packages are missing. Installing...")
        if not install_packages():
            print("❌ Package installation failed")
            return 1
    
    # Create conda environment file
    env_file = create_conda_env_file()
    
    # Test the environment
    print("\n🔄 Testing environment...")
    try:
        # Set matplotlib backend
        import matplotlib
        matplotlib.use('Agg')
        
        # Test imports
        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        import yaml
        
        print("✅ All imports successful!")
        
        # Test basic functionality
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title("Test Plot")
        
        # Test saving
        test_dir = Path(__file__).parent / "test_output"
        test_dir.mkdir(exist_ok=True)
        fig.savefig(test_dir / "test.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print("✅ Figure generation test successful!")
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return 1
    
    # Show PyCharm configuration
    setup_pycharm_config()
    
    print("\n" + "=" * 50)
    print("NEXT STEPS")
    print("=" * 50)
    print("1. Configure PyCharm interpreter (see instructions above)")
    print("2. Run: python test_environment.py")
    print("3. Run: python run_interactive.py")
    print("4. Complete analysis scripts from notebook backups")
    print()
    
    if env_file:
        print("For new conda environment setup:")
        print(f"  conda env create -f {Path(env_file).name}")
        print("  conda activate paper2")
    
    print("\n✅ Setup complete!")
    return 0

if __name__ == "__main__":
    exit(main())