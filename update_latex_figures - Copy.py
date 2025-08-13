#!/usr/bin/env python3
"""
Update all Python analysis scripts to save TIFF files for LaTeX integration.
This script modifies analysis files to include LaTeX-compatible figure output.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def update_analysis_file(file_path, latex_figures_dir):
    """Update an analysis file to save TIFF figures for LaTeX."""
    
    print(f"Updating {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file already has LaTeX figure saving
    if "LaTeX TIFF figures" in content:
        print(f"  Already updated: {file_path}")
        return
    
    # Add LaTeX figure directory setup
    latex_setup = f'''
# === LaTeX TIFF Figure Generation ===
latex_figures_dir = Path("{latex_figures_dir}")
latex_figures_dir.mkdir(exist_ok=True)
print(f"📁 LaTeX figures will be saved to: {{latex_figures_dir}}")

def save_for_latex(fig, filename, include_pdf=True):
    """Save figure in TIFF format for LaTeX, with optional PDF."""
    # Save to LaTeX directory
    saved_files = save_figure(
        fig, filename, 
        folder=latex_figures_dir,
        formats=("tiff",), 
        include_pdf=include_pdf,
        dpi=600
    )
    print(f"✅ LaTeX figure saved: {{filename}}.tiff")
    return saved_files
'''
    
    # Find the position after imports but before main code
    lines = content.split('\n')
    insert_position = 0
    
    # Find last import or set_plot_style call
    for i, line in enumerate(lines):
        if (line.strip().startswith('import ') or 
            line.strip().startswith('from ') or 
            'set_plot_style()' in line):
            insert_position = i + 1
    
    # Insert LaTeX setup after imports
    lines.insert(insert_position, latex_setup)
    
    # Update save_figure calls to also save for LaTeX
    updated_lines = []
    for line in lines:
        updated_lines.append(line)
        
        # If we find a save_figure call, add LaTeX version
        if ('save_figure(' in line and 
            'save_for_latex(' not in line and
            not line.strip().startswith('#')):
            
            # Extract figure and filename from the save_figure call
            if 'fig,' in line or 'fig_' in line:
                # Try to extract filename
                parts = line.split('save_figure(')[1]
                if ',' in parts:
                    fig_part = parts.split(',')[0].strip()
                    filename_part = parts.split(',')[1].strip()
                    if '"' in filename_part or "'" in filename_part:
                        filename = filename_part.strip('"\'')
                        
                        # Add LaTeX save call
                        indent = len(line) - len(line.lstrip())
                        latex_call = ' ' * indent + f'save_for_latex({fig_part}, "{filename}")'
                        updated_lines.append(latex_call)
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"  ✅ Updated: {file_path}")

def main():
    """Update all analysis files to generate LaTeX figures."""
    
    project_root = Path(__file__).parent
    latex_figures_dir = project_root / "LaTeX" / "High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_" / "Figures"
    
    # Ensure LaTeX figures directory exists
    latex_figures_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all Python analysis files
    analysis_files = []
    
    # Search in analysis directories
    for analysis_dir in project_root.glob("*/analysis/"):
        for py_file in analysis_dir.glob("*.py"):
            if py_file.name.endswith('_analysis.py'):
                analysis_files.append(py_file)
    
    # Also check for specific known files
    known_files = [
        "05_FTIR_Analysis/analysis/ftir_analysis.py",
        "06_XPS_Analysis/analysis/xps_analysis.py",
        "01_Hybrid_Growth/analysis/hybrid_growth_analysis.py",
        "02_Air_Stability/analysis/air_stability_analysis.py", 
        "03_Developer_Stability_Patterning_Contrast/analysis/developer_stability_analysis.py"
    ]
    
    for file_path in known_files:
        full_path = project_root / file_path
        if full_path.exists():
            analysis_files.append(full_path)
    
    print(f"📝 Found {len(analysis_files)} analysis files to update:")
    for f in analysis_files:
        print(f"  - {f.relative_to(project_root)}")
    
    # Update each file
    for file_path in analysis_files:
        try:
            update_analysis_file(file_path, str(latex_figures_dir))
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
    
    print(f"\n🎯 LaTeX Figures Directory: {latex_figures_dir}")
    print("✅ All analysis files updated for LaTeX TIFF generation!")
    print("\n📋 Next steps:")
    print("1. Run your analysis scripts to generate TIFF files")
    print("2. Build LaTeX document with: build.bat full")

if __name__ == "__main__":
    main()