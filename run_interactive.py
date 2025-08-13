#!/usr/bin/env python3
"""
Interactive Python launcher for Paper2 analysis pipeline.
Works with conda environments in PyCharm.
"""

import sys
import os
from pathlib import Path

# Set matplotlib backend before any other imports
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for conda/PyCharm

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """Interactive menu for running analysis pipeline."""
    print("Paper2 Analysis Pipeline - Python Interactive")
    print("=" * 50)
    
    # Test environment first
    print("🔄 Testing environment...")
    try:
        from test_environment import main as test_main
        if test_main() != 0:
            print("❌ Environment test failed. Please fix issues before continuing.")
            return 1
    except Exception as e:
        print(f"❌ Environment test error: {e}")
        return 1
    
    print("\n✅ Environment test passed!")
    
    while True:
        print("\n" + "=" * 50)
        print("Choose an option:")
        print("1. Complete analysis pipeline (analysis + sync + LaTeX build)")
        print("2. Generate figures only (no LaTeX build)")
        print("3. Sync figures and build LaTeX only (no analysis)")
        print("4. Run individual analysis script")
        print("5. Generate status report")
        print("6. Test environment again")
        print("0. Exit")
        print("-" * 50)
        
        try:
            choice = input("Enter your choice (0-6): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return 0
        
        if choice == "0":
            print("Goodbye!")
            return 0
        elif choice == "1":
            run_complete_pipeline()
        elif choice == "2":
            run_figures_only()
        elif choice == "3":
            run_latex_only()
        elif choice == "4":
            run_individual_script()
        elif choice == "5":
            generate_report()
        elif choice == "6":
            from test_environment import main as test_main
            test_main()
        else:
            print("❌ Invalid choice. Please enter 0-6.")

def run_complete_pipeline():
    """Run the complete analysis pipeline."""
    print("\n🚀 Running complete analysis pipeline...")
    try:
        from run_analysis import main as analysis_main
        result = analysis_main()
        if result == 0:
            print("✅ Complete pipeline finished successfully!")
        else:
            print("⚠️ Pipeline completed with some issues.")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")

def run_figures_only():
    """Generate figures only."""
    print("\n📊 Generating figures only...")
    try:
        # Temporarily modify sys.argv to pass --no-build argument
        original_argv = sys.argv.copy()
        sys.argv = ['run_analysis.py', '--no-build']
        
        from run_analysis import main as analysis_main
        result = analysis_main()
        
        # Restore original argv
        sys.argv = original_argv
        
        if result == 0:
            print("✅ Figure generation completed successfully!")
        else:
            print("⚠️ Figure generation completed with some issues.")
    except Exception as e:
        print(f"❌ Figure generation failed: {e}")

def run_latex_only():
    """Sync figures and build LaTeX only."""
    print("\n📄 Syncing figures and building LaTeX...")
    try:
        # Temporarily modify sys.argv to pass --skip-analysis argument
        original_argv = sys.argv.copy()
        sys.argv = ['run_analysis.py', '--skip-analysis']
        
        from run_analysis import main as analysis_main
        result = analysis_main()
        
        # Restore original argv
        sys.argv = original_argv
        
        if result == 0:
            print("✅ LaTeX build completed successfully!")
        else:
            print("⚠️ LaTeX build completed with some issues.")
    except Exception as e:
        print(f"❌ LaTeX build failed: {e}")

def run_individual_script():
    """Run an individual analysis script."""
    print("\n🔍 Available analysis scripts:")
    
    # List available scripts
    scripts = [
        "01_Hybrid_Growth/analysis/Alucone_Zincone_GPC.py",
        "02_Air_Stability/analysis/03_final_figure_air_stability.py",
        "03_Developer_Stability_Patterning_Contrast/analysis/03_figures_heatma_bar.py",
        "05_FTIR_Analysis/analysis/FTIR_BTY_Final.py",
        "06_XPS_Analysis/analysis/XPS_Figure_Best.py"
    ]
    
    for i, script in enumerate(scripts, 1):
        script_name = Path(script).stem
        print(f"{i}. {script_name}")
    
    try:
        choice = input(f"\nEnter script number (1-{len(scripts)}): ").strip()
        script_idx = int(choice) - 1
        
        if 0 <= script_idx < len(scripts):
            script_path = project_root / scripts[script_idx]
            print(f"\n🔄 Running {script_path.name}...")
            
            # Change to script directory and run
            original_cwd = os.getcwd()
            os.chdir(script_path.parent)
            
            try:
                # Import and run the script
                spec = importlib.util.spec_from_file_location("analysis_script", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'main'):
                    module.main()
                else:
                    print("⚠️ Script doesn't have a main() function")
                    
            except Exception as e:
                print(f"❌ Script execution failed: {e}")
            finally:
                os.chdir(original_cwd)
        else:
            print("❌ Invalid script number.")
            
    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid input.")

def generate_report():
    """Generate and display status report."""
    print("\n📋 Generating status report...")
    try:
        from shared.scripts.latex_integration import LaTeXIntegrator
        integrator = LaTeXIntegrator()
        report = integrator.generate_build_report()
        
        print("\n" + "=" * 50)
        print("INTEGRATION STATUS REPORT")
        print("=" * 50)
        print(f"Timestamp: {report['timestamp']}")
        print(f"LaTeX directory: {report['latex_dir']}")
        print(f"Total mapped figures: {len(report['figures_status'])}")
        print(f"Missing figures: {len(report['missing_figures'])}")
        print(f"Outdated figures: {len(report['outdated_figures'])}")
        
        if report['missing_figures']:
            print("\nMissing figures:")
            for fig in report['missing_figures']:
                print(f"  - {fig}")
        
        if report['outdated_figures']:
            print("\nOutdated figures:")
            for fig in report['outdated_figures']:
                print(f"  - {fig}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")

if __name__ == "__main__":
    # Import required for individual script execution
    import importlib.util
    
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        exit(0)