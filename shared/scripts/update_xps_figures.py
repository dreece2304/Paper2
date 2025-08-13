#!/usr/bin/env python3
"""
Update XPS figures in LaTeX from the latest analysis outputs.

This script specifically handles the XPS analysis figures that may have
different naming conventions than expected in the LaTeX document.
"""

import sys
from pathlib import Path
import shutil

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from shared.scripts.latex_integration import LaTeXIntegrator

def update_xps_figures():
    """Update XPS figure mappings and sync to LaTeX."""
    
    integrator = LaTeXIntegrator()
    
    # Check what XPS figures are actually available
    xps_figures_dir = project_root / "06_XPS_Analysis" / "figures" / "final"
    
    if not xps_figures_dir.exists():
        print(f"XPS figures directory not found: {xps_figures_dir}")
        return
    
    available_figures = list(xps_figures_dir.glob("*.pdf"))
    print(f"Found {len(available_figures)} XPS figures:")
    for fig in available_figures:
        print(f"  {fig.name}")
    
    # Update figure mapping for XPS analysis
    xps_updates = {}
    
    # Map the main XPS publication figure
    if (xps_figures_dir / "XPS_publication_figure_final.pdf").exists():
        xps_updates["XPS_publication_figure_final.pdf"] = "BTY_XPS_Final_Publication.pdf"
    
    # Look for THB XPS figure
    thb_candidates = [
        "THB_XPS_Final_Publication.pdf",
        "THB_XPS_publication_figure_final.pdf", 
        "XPS_THB_final.pdf"
    ]
    
    for candidate in thb_candidates:
        if (xps_figures_dir / candidate).exists():
            xps_updates[candidate] = "THB_XPS_Final_Publication.pdf"
            break
    
    if xps_updates:
        print(f"\nUpdating XPS figure mappings:")
        for source, target in xps_updates.items():
            print(f"  {source} -> {target}")
        
        integrator.update_figure_references("06_XPS_Analysis", xps_updates)
        
        # Sync the updated figures
        actions = integrator.sync_figures()
        if actions:
            print(f"\nSynchronization actions:")
            for action in actions:
                print(f"  {action}")
        else:
            print("\nAll figures are up to date.")
    else:
        print("\nNo XPS figures found to update.")

if __name__ == "__main__":
    update_xps_figures()