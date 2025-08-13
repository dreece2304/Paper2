#!/usr/bin/env python3
"""
Test script to verify the Paper2 environment works in PyCharm/Windows.
"""

import sys
import os
from pathlib import Path

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for WSL/headless environments

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_imports():
    """Test that all required imports work."""
    print("🔄 Testing imports...")
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib imported successfully")
    except ImportError as e:
        print(f"❌ matplotlib import failed: {e}")
        return False
    
    try:
        import seaborn as sns
        print("✅ seaborn imported successfully")
    except ImportError as e:
        print(f"❌ seaborn import failed: {e}")
        return False
    
    try:
        from shared.utils.plot_styles import set_plot_style
        print("✅ plot_styles imported successfully")
    except ImportError as e:
        print(f"❌ plot_styles import failed: {e}")
        return False
    
    try:
        from shared.utils.helpers import save_figure, create_figure, get_figure_size
        print("✅ helpers imported successfully")
    except ImportError as e:
        print(f"❌ helpers import failed: {e}")
        return False
    
    try:
        import shared.utils.config as config
        print("✅ config imported successfully")
    except ImportError as e:
        print(f"❌ config import failed: {e}")
        return False
    
    return True

def test_figure_generation():
    """Test that figure generation works."""
    print("\n🔄 Testing figure generation...")
    
    try:
        from shared.utils.plot_styles import set_plot_style
        from shared.utils.helpers import save_figure, create_figure
        import matplotlib.pyplot as plt
        
        # Set plot style
        set_plot_style()
        
        # Create a simple test figure
        fig, ax = create_figure(width_cm=18)
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3], 'o-', label='Test Data')
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")
        ax.set_title("Environment Test Figure")
        ax.legend()
        
        # Save the figure
        save_figure(fig, "environment_test", include_pdf=True)
        print("✅ Test figure generated and saved successfully")
        
        plt.close(fig)
        return True
        
    except Exception as e:
        print(f"❌ Figure generation failed: {e}")
        return False

def test_latex_integration():
    """Test LaTeX integration components."""
    print("\n🔄 Testing LaTeX integration...")
    
    try:
        from shared.scripts.latex_integration import LaTeXIntegrator
        integrator = LaTeXIntegrator()
        
        # Generate a report (doesn't require LaTeX to be installed)
        report = integrator.generate_build_report()
        print("✅ LaTeX integration components working")
        print(f"Found {len(report['figures_status'])} mapped figures")
        return True
        
    except Exception as e:
        print(f"❌ LaTeX integration test failed: {e}")
        return False

def test_run_analysis():
    """Test the main analysis runner."""
    print("\n🔄 Testing analysis runner...")
    
    try:
        # Import and validate without running
        sys.path.append(str(project_root))
        from run_analysis import AnalysisRunner
        
        runner = AnalysisRunner()
        is_valid = runner.validate_environment()
        
        if is_valid:
            print("✅ Analysis runner validation passed")
            return True
        else:
            print("❌ Analysis runner validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Analysis runner test failed: {e}")
        return False

def main():
    """Run all environment tests."""
    print("🚀 Paper2 Environment Test")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    print("-" * 50)
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_imports()
    all_tests_passed &= test_figure_generation()
    all_tests_passed &= test_latex_integration()
    all_tests_passed &= test_run_analysis()
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! Environment is ready.")
        print("\nNext steps:")
        print("1. Complete the analysis scripts by copying code from .ipynb.bak files")
        print("2. Run individual scripts to test them")
        print("3. Use 'python run_analysis.py' for the complete workflow")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install missing packages: pip install matplotlib pandas seaborn numpy")
        print("- Check that you're running from the project root directory")
        print("- Verify PyCharm Python interpreter is set correctly")
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    exit(main())