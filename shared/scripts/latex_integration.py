#!/usr/bin/env python3
"""
LaTeX Integration Scripts for Paper2 Project

This module provides utilities for automating the integration between
data analysis notebooks and LaTeX document preparation.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import yaml
import json
from datetime import datetime

class LaTeXIntegrator:
    """Manages integration between analysis outputs and LaTeX document."""
    
    def __init__(self, project_root: str = None):
        """Initialize with project root directory."""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.latex_dir = self.project_root / "LaTeX" / "High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_"
        self.figures_mapping = self._load_figure_mapping()
    
    def _load_figure_mapping(self) -> Dict[str, str]:
        """Load or create figure mapping between analysis and LaTeX."""
        mapping_file = self.project_root / "shared" / "config" / "figure_mapping.yaml"
        
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        # Create default mapping based on current state
        default_mapping = {
            # Growth per cycle figures
            "01_Hybrid_Growth/figures/final/Fig2_Metalcone_GPC.pdf": "Figures/Fig2_Metalcone_GPC.pdf",
            "01_Hybrid_Growth/figures/final/Fig2a_Metalcone_Thickness.pdf": "Figures/Fig2a_Metalcone_Thickness.pdf",
            "01_Hybrid_Growth/figures/final/Fig2b_Metalcone_GPC.pdf": "Figures/Fig2b_Metalcone_GPC.pdf",
            
            # Air stability
            "02_Air_Stability/figures/final/air_stability_final.pdf": "Figures/air_stability_final.pdf",
            
            # Developer stability
            "03_Developer_Stability_Patterning_Contrast/figures/final/Fig4a_Heatmap_EtchStability.pdf": "Figures/Fig4a_Heatmap_EtchStability.pdf",
            "03_Developer_Stability_Patterning_Contrast/figures/final/Fig4b_Barplot_EtchStability.pdf": "Figures/Fig4b_Barplot_EtchStability.pdf",
            "03_Developer_Stability_Patterning_Contrast/figures/final/Fig4c_BarplotOrganicGroupedBySolvent.pdf": "Figures/Fig4c_BarplotOrganicGroupedBySolvent.pdf",
            
            # FTIR analysis
            "05_FTIR_Analysis/figures/final/Fig3b_FTIR_Subpanels.pdf": "Figures/Fig3b_FTIR_Subpanels.pdf",
            
            # XPS analysis - need to map from new analysis
            "06_XPS_Analysis/figures/final/XPS_publication_figure_final.pdf": "Figures/BTY_XPS_Final_Publication.pdf",
            
            # E-beam studies
            "figures/final/dose_matrix_mockup_clean.pdf": "Figures/dose_matrix_mockup_clean.pdf",
            "figures/final/box_grating_mockup_clean.pdf": "Figures/box_grating_mockup_clean.pdf"
        }
        
        # Save default mapping
        mapping_file.parent.mkdir(parents=True, exist_ok=True)
        with open(mapping_file, 'w') as f:
            yaml.dump(default_mapping, f, default_flow_style=False, sort_keys=True)
        
        return default_mapping
    
    def sync_figures(self, dry_run: bool = False) -> List[str]:
        """
        Synchronize figures from analysis directories to LaTeX Figures folder.
        
        Args:
            dry_run: If True, only show what would be copied without doing it
            
        Returns:
            List of actions taken or that would be taken
        """
        actions = []
        latex_figures_dir = self.latex_dir / "Figures"
        
        for source_rel, target_rel in self.figures_mapping.items():
            source_path = self.project_root / source_rel
            target_path = latex_figures_dir / Path(target_rel).name
            
            if not source_path.exists():
                actions.append(f"WARNING: Source file not found: {source_path}")
                continue
            
            # Check if update is needed
            if target_path.exists():
                source_mtime = source_path.stat().st_mtime
                target_mtime = target_path.stat().st_mtime
                if source_mtime <= target_mtime:
                    continue  # Target is up to date
            
            action_msg = f"{'[DRY RUN] ' if dry_run else ''}Copy: {source_rel} -> {target_rel}"
            actions.append(action_msg)
            
            if not dry_run:
                latex_figures_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
        
        return actions
    
    def build_latex(self, clean: bool = False) -> subprocess.CompletedProcess:
        """
        Build the LaTeX document using XeLaTeX.
        
        Args:
            clean: If True, clean auxiliary files before building
            
        Returns:
            CompletedProcess result from xelatex
        """
        if clean:
            self.clean_latex_build()
        
        # Change to LaTeX directory for build
        original_cwd = os.getcwd()
        os.chdir(self.latex_dir)
        
        try:
            # Run xelatex twice for proper cross-references
            result1 = subprocess.run(['xelatex', '-interaction=nonstopmode', 'main.tex'], 
                                   capture_output=True, text=True)
            
            # Run biber for bibliography
            subprocess.run(['biber', 'main'], capture_output=True, text=True)
            
            # Run xelatex again for bibliography
            result2 = subprocess.run(['xelatex', '-interaction=nonstopmode', 'main.tex'], 
                                   capture_output=True, text=True)
            
            return result2
        finally:
            os.chdir(original_cwd)
    
    def clean_latex_build(self):
        """Clean LaTeX auxiliary files."""
        aux_extensions = ['.aux', '.bbl', '.blg', '.fdb_latexmk', '.fls', 
                         '.log', '.out', '.run.xml', '.bcf', '.toc', '.lof', '.lot']
        
        for file_path in self.latex_dir.iterdir():
            if file_path.suffix in aux_extensions:
                file_path.unlink()
    
    def update_figure_references(self, analysis_dir: str, figure_updates: Dict[str, str]):
        """
        Update figure mapping for a specific analysis directory.
        
        Args:
            analysis_dir: Directory name (e.g., "06_XPS_Analysis")
            figure_updates: Dict mapping new figure names to LaTeX figure names
        """
        for source_name, latex_name in figure_updates.items():
            source_rel = f"{analysis_dir}/figures/final/{source_name}"
            target_rel = f"Figures/{latex_name}"
            self.figures_mapping[source_rel] = target_rel
        
        # Save updated mapping
        mapping_file = self.project_root / "shared" / "config" / "figure_mapping.yaml"
        with open(mapping_file, 'w') as f:
            yaml.dump(self.figures_mapping, f, default_flow_style=False, sort_keys=True)
    
    def generate_build_report(self) -> Dict:
        """Generate a report on the current state of the integration."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "latex_dir": str(self.latex_dir),
            "figures_status": {},
            "missing_figures": [],
            "outdated_figures": []
        }
        
        latex_figures_dir = self.latex_dir / "Figures"
        
        for source_rel, target_rel in self.figures_mapping.items():
            source_path = self.project_root / source_rel
            target_path = latex_figures_dir / Path(target_rel).name
            
            status = {
                "source_exists": source_path.exists(),
                "target_exists": target_path.exists(),
                "up_to_date": False
            }
            
            if source_path.exists() and target_path.exists():
                source_mtime = source_path.stat().st_mtime
                target_mtime = target_path.stat().st_mtime
                status["up_to_date"] = source_mtime <= target_mtime
                
                if not status["up_to_date"]:
                    report["outdated_figures"].append(source_rel)
            elif source_path.exists() and not target_path.exists():
                report["missing_figures"].append(source_rel)
            
            report["figures_status"][source_rel] = status
        
        return report


def main():
    """Command line interface for LaTeX integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LaTeX Integration for Paper2 Project")
    parser.add_argument("command", choices=["sync", "build", "clean", "report"], 
                       help="Command to execute")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without executing")
    parser.add_argument("--clean", action="store_true", 
                       help="Clean build files before building")
    
    args = parser.parse_args()
    
    integrator = LaTeXIntegrator()
    
    if args.command == "sync":
        actions = integrator.sync_figures(dry_run=args.dry_run)
        if actions:
            print("Figure synchronization actions:")
            for action in actions:
                print(f"  {action}")
        else:
            print("All figures are up to date.")
    
    elif args.command == "build":
        print("Building LaTeX document...")
        result = integrator.build_latex(clean=args.clean)
        if result.returncode == 0:
            print("Build successful!")
        else:
            print("Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
    
    elif args.command == "clean":
        integrator.clean_latex_build()
        print("Cleaned LaTeX auxiliary files.")
    
    elif args.command == "report":
        report = integrator.generate_build_report()
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()