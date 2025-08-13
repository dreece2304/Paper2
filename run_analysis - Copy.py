#!/usr/bin/env python3
"""
Unified Analysis Runner for Paper2 Project

This script orchestrates the complete analysis workflow:
1. Runs all analysis scripts to generate TIFF figures
2. Syncs figures to LaTeX directory
3. Optionally builds the LaTeX document

Usage:
    python run_analysis.py [options]
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional
import argparse
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from shared.scripts.latex_integration import LaTeXIntegrator

class AnalysisRunner:
    """Manages execution of analysis scripts and LaTeX integration."""
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent
        self.project_root = project_root
        self.integrator = LaTeXIntegrator(str(project_root))
        
        # Define analysis scripts in execution order
        self.analysis_scripts = [
            "01_Hybrid_Growth/analysis/hybrid_growth_analysis.py",
            "02_Air_Stability/analysis/air_stability_analysis.py", 
            "03_Developer_Stability_Patterning_Contrast/analysis/developer_stability_analysis.py",
            "05_FTIR_Analysis/analysis/ftir_analysis.py",
            "06_XPS_Analysis/analysis/xps_analysis.py",
            "08_E-Beam_Studies/analysis/ebeam_analysis.py",
        ]
    
    def validate_environment(self) -> bool:
        """Check if the environment is properly set up."""
        print("Validating environment...")
        
        # Check if analysis scripts exist
        missing_scripts = []
        for script_path in self.analysis_scripts:
            full_path = self.project_root / script_path
            if not full_path.exists():
                missing_scripts.append(script_path)
        
        if missing_scripts:
            print("❌ Missing analysis scripts:")
            for script in missing_scripts:
                print(f"  - {script}")
            return False
        
        # Check if shared utilities are available
        try:
            from shared.utils.plot_styles import set_plot_style
            from shared.utils.helpers import save_figure
            import shared.utils.config as config
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return False
        
        print("✅ Environment validation passed")
        return True
    
    def run_analysis_script(self, script_path: str, timeout: int = 300) -> Dict:
        """
        Run a single analysis script.
        
        Args:
            script_path: Relative path to the script
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with execution results
        """
        full_path = self.project_root / script_path
        script_name = Path(script_path).name
        
        print(f"\n🔄 Running {script_name}...")
        
        start_time = time.time()
        
        try:
            # Change to the script's directory for relative imports
            original_cwd = os.getcwd()
            script_dir = full_path.parent
            os.chdir(script_dir)
            
            # Run the script
            result = subprocess.run(
                [sys.executable, full_path.name],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ {script_name} completed successfully ({elapsed_time:.1f}s)")
                return {
                    'script': script_path,
                    'status': 'success',
                    'elapsed_time': elapsed_time,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                print(f"❌ {script_name} failed (exit code: {result.returncode})")
                print(f"STDERR: {result.stderr}")
                return {
                    'script': script_path,
                    'status': 'failed',
                    'elapsed_time': elapsed_time,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'exit_code': result.returncode
                }
        
        except subprocess.TimeoutExpired:
            print(f"⏰ {script_name} timed out after {timeout}s")
            return {
                'script': script_path,
                'status': 'timeout',
                'elapsed_time': timeout,
                'stdout': '',
                'stderr': f'Script timed out after {timeout} seconds'
            }
        
        except Exception as e:
            print(f"💥 {script_name} crashed: {e}")
            return {
                'script': script_path,
                'status': 'error',
                'elapsed_time': time.time() - start_time,
                'stdout': '',
                'stderr': str(e)
            }
        
        finally:
            os.chdir(original_cwd)
    
    def run_all_analyses(self, skip_failed: bool = True, timeout: int = 300) -> List[Dict]:
        """
        Run all analysis scripts in sequence.
        
        Args:
            skip_failed: Continue running other scripts if one fails
            timeout: Timeout per script in seconds
            
        Returns:
            List of execution results
        """
        print(f"\n🚀 Starting analysis pipeline...")
        print(f"Will run {len(self.analysis_scripts)} scripts")
        
        results = []
        start_time = time.time()
        
        for i, script_path in enumerate(self.analysis_scripts, 1):
            print(f"\n[{i}/{len(self.analysis_scripts)}] Processing: {script_path}")
            
            result = self.run_analysis_script(script_path, timeout)
            results.append(result)
            
            if result['status'] != 'success' and not skip_failed:
                print(f"❌ Stopping pipeline due to failure in {script_path}")
                break
        
        total_time = time.time() - start_time
        
        # Summary
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - successful
        
        print(f"\n📊 Analysis Pipeline Summary:")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⏱️  Total time: {total_time:.1f}s")
        
        return results
    
    def sync_and_build(self, build_latex: bool = True, clean_build: bool = False) -> Dict:
        """
        Sync figures to LaTeX and optionally build the document.
        
        Args:
            build_latex: Whether to build the LaTeX document
            clean_build: Whether to clean before building
            
        Returns:
            Dictionary with sync and build results
        """
        print(f"\n📁 Syncing figures to LaTeX...")
        
        # Sync figures
        sync_actions = self.integrator.sync_figures()
        if sync_actions:
            print(f"  Synchronized {len(sync_actions)} figures")
            for action in sync_actions[:5]:  # Show first 5
                print(f"    {action}")
            if len(sync_actions) > 5:
                print(f"    ... and {len(sync_actions) - 5} more")
        else:
            print("  All figures are up to date")
        
        result = {
            'sync_actions': sync_actions,
            'sync_status': 'success' if sync_actions is not None else 'failed'
        }
        
        if build_latex:
            print(f"\n📄 Building LaTeX document...")
            build_result = self.integrator.build_latex(clean=clean_build)
            
            if build_result.returncode == 0:
                print("✅ LaTeX build successful")
                result['build_status'] = 'success'
                result['build_output'] = build_result.stdout
            else:
                print("❌ LaTeX build failed")
                print(f"Error output: {build_result.stderr}")
                result['build_status'] = 'failed'
                result['build_output'] = build_result.stdout
                result['build_error'] = build_result.stderr
        
        return result
    
    def generate_report(self, analysis_results: List[Dict], sync_results: Dict) -> str:
        """Generate a summary report of the complete workflow."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# Paper2 Analysis Report
Generated: {timestamp}

## Analysis Scripts Execution
"""
        
        for result in analysis_results:
            status_emoji = {
                'success': '✅',
                'failed': '❌', 
                'timeout': '⏰',
                'error': '💥'
            }.get(result['status'], '❓')
            
            report += f"- {status_emoji} {result['script']} ({result['elapsed_time']:.1f}s)\n"
            
            if result['status'] != 'success' and result.get('stderr'):
                report += f"  Error: {result['stderr'][:100]}...\n"
        
        report += f"\n## Figure Synchronization\n"
        if sync_results.get('sync_actions'):
            report += f"Synchronized {len(sync_results['sync_actions'])} figures\n"
        else:
            report += "All figures were up to date\n"
        
        if 'build_status' in sync_results:
            build_emoji = '✅' if sync_results['build_status'] == 'success' else '❌'
            report += f"\n## LaTeX Build\n{build_emoji} Build {sync_results['build_status']}\n"
        
        return report


def main():
    """Command line interface for the analysis runner."""
    parser = argparse.ArgumentParser(description="Run complete Paper2 analysis pipeline")
    
    parser.add_argument("--skip-analysis", action="store_true",
                       help="Skip analysis scripts, only sync figures")
    parser.add_argument("--no-build", action="store_true", 
                       help="Don't build LaTeX document")
    parser.add_argument("--clean-build", action="store_true",
                       help="Clean LaTeX build files before building")
    parser.add_argument("--timeout", type=int, default=600,
                       help="Timeout per analysis script in seconds (default: 600)")
    parser.add_argument("--report", type=str,
                       help="Save report to file")
    
    args = parser.parse_args()
    
    runner = AnalysisRunner()
    
    # Validate environment
    if not runner.validate_environment():
        print("❌ Environment validation failed. Please fix issues before running.")
        return 1
    
    analysis_results = []
    
    # Run analysis scripts
    if not args.skip_analysis:
        analysis_results = runner.run_all_analyses(timeout=args.timeout)
        
        # Check if any critical scripts failed
        failed_scripts = [r for r in analysis_results if r['status'] != 'success']
        if failed_scripts:
            print(f"\n⚠️  {len(failed_scripts)} scripts failed. Check outputs above.")
    
    # Sync figures and build LaTeX
    sync_results = runner.sync_and_build(
        build_latex=not args.no_build,
        clean_build=args.clean_build
    )
    
    # Generate report
    report = runner.generate_report(analysis_results, sync_results)
    print(f"\n{report}")
    
    if args.report:
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to {args.report}")
    
    # Return appropriate exit code
    all_success = all(r['status'] == 'success' for r in analysis_results)
    sync_success = sync_results.get('sync_status') == 'success'
    build_success = sync_results.get('build_status', 'success') == 'success'
    
    if all_success and sync_success and build_success:
        print(f"\n🎉 Complete workflow finished successfully!")
        return 0
    else:
        print(f"\n⚠️  Workflow completed with some issues. Check the report above.")
        return 1


if __name__ == "__main__":
    exit(main())