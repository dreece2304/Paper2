#!/usr/bin/env python3
"""
Python script to help configure PyCharm for the Paper2 project.
This replaces XML-based run configurations with Python instructions.
"""

import sys
import os
from pathlib import Path

def print_pycharm_setup():
    """Print instructions for setting up PyCharm configurations."""
    project_dir = Path(__file__).parent
    
    print("Paper2 PyCharm Setup Instructions")
    print("=" * 50)
    print()
    
    print("🔧 INTERPRETER SETUP:")
    print("1. File → Settings → Project → Python Interpreter")
    print("2. Add Interpreter → Conda Environment")
    print("3. Choose your conda environment or create new one")
    print()
    
    print("📁 PROJECT STRUCTURE:")
    print("Mark these directories as Sources Root:")
    print(f"  - {project_dir}")
    print(f"  - {project_dir / 'shared'}")
    print()
    
    print("🏃 RUN CONFIGURATIONS:")
    print("Create these Python run configurations manually:")
    print()
    
    configs = [
        {
            "name": "1. Install Requirements",
            "script": "install_requirements.py",
            "description": "Install all required packages",
            "env_vars": {"PYTHONUNBUFFERED": "1"}
        },
        {
            "name": "2. Test Environment", 
            "script": "test_environment.py",
            "description": "Verify setup works",
            "env_vars": {"PYTHONUNBUFFERED": "1", "MPLBACKEND": "Agg"}
        },
        {
            "name": "3. Interactive Launcher",
            "script": "run_interactive.py", 
            "description": "Interactive menu for analysis",
            "env_vars": {"PYTHONUNBUFFERED": "1", "MPLBACKEND": "Agg"},
            "emulate_terminal": True
        },
        {
            "name": "4. Complete Pipeline",
            "script": "run_analysis.py",
            "description": "Full analysis + LaTeX build",
            "env_vars": {"PYTHONUNBUFFERED": "1", "MPLBACKEND": "Agg"}
        },
        {
            "name": "5. Figures Only",
            "script": "run_analysis.py",
            "parameters": "--no-build",
            "description": "Generate figures without LaTeX", 
            "env_vars": {"PYTHONUNBUFFERED": "1", "MPLBACKEND": "Agg"}
        }
    ]
    
    for config in configs:
        print(f"📋 {config['name']}:")
        print(f"   Script: {config['script']}")
        if config.get('parameters'):
            print(f"   Parameters: {config['parameters']}")
        print(f"   Working Directory: {project_dir}")
        print(f"   Environment Variables:")
        for var, value in config['env_vars'].items():
            print(f"     {var}={value}")
        if config.get('emulate_terminal'):
            print(f"   ✓ Emulate terminal in output console")
        print(f"   Description: {config['description']}")
        print()
    
    print("🔑 ENVIRONMENT VARIABLES (for all configs):")
    print("  PYTHONUNBUFFERED=1    # Real-time output")
    print("  MPLBACKEND=Agg        # Matplotlib backend for conda/WSL")
    print()
    
    print("📂 WORKING DIRECTORY (for all configs):")
    print(f"  {project_dir}")
    print()

def create_launch_script():
    """Create a simple launcher script that users can run directly."""
    launcher_content = '''#!/usr/bin/env python3
"""
Simple launcher for Paper2 project.
Run this script to get started with the analysis pipeline.
"""

import sys
import os
from pathlib import Path

# Set matplotlib backend for compatibility
import matplotlib
matplotlib.use('Agg')

# Add project to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """Main launcher function."""
    print("Paper2 Project Launcher")
    print("=" * 30)
    print()
    print("Choose what to run:")
    print("1. Install requirements")
    print("2. Test environment") 
    print("3. Interactive launcher")
    print("4. Complete analysis pipeline")
    print("0. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter choice (0-4): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\\nGoodbye!")
            return 0
        
        if choice == "0":
            return 0
        elif choice == "1":
            from install_requirements import main as install_main
            install_main()
        elif choice == "2":
            from test_environment import main as test_main
            test_main()
        elif choice == "3":
            from run_interactive import main as interactive_main
            interactive_main()
        elif choice == "4":
            from run_analysis import main as analysis_main
            analysis_main()
        else:
            print("Invalid choice. Please enter 0-4.")
        
        print("\\n" + "-" * 30)

if __name__ == "__main__":
    exit(main())
'''
    
    launcher_path = Path(__file__).parent / "launcher.py"
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    print(f"✅ Created launcher script: {launcher_path}")
    return launcher_path

def main():
    """Main setup function."""
    print_pycharm_setup()
    
    print("🚀 GETTING STARTED:")
    print("1. First, install packages:")
    print("   python install_requirements.py")
    print()
    print("2. Test the environment:")
    print("   python test_environment.py")
    print() 
    print("3. Use the interactive launcher:")
    print("   python run_interactive.py")
    print()
    print("4. Or use the simple launcher:")
    
    launcher_path = create_launch_script()
    print(f"   python {launcher_path.name}")
    print()
    
    print("💡 TIP: Create PyCharm run configurations for easy access")
    print("   to these scripts using the settings above.")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())