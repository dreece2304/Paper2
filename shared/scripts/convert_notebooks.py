#!/usr/bin/env python3
"""
Convert Jupyter notebooks to Python scripts with TIFF-optimized figure output.

This script converts all analysis notebooks to Python scripts and updates
figure saving calls to use the new TIFF-first workflow.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any

class NotebookConverter:
    """Convert Jupyter notebooks to Python scripts with optimizations."""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
    
    def convert_notebook(self, notebook_path: Path, output_path: Path = None) -> str:
        """
        Convert a single notebook to Python script.
        
        Args:
            notebook_path: Path to the .ipynb file
            output_path: Output path for .py file (optional)
            
        Returns:
            Path to the created Python script
        """
        if output_path is None:
            output_path = notebook_path.with_suffix('.py')
        
        # Load notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        python_code = self._extract_code_cells(notebook)
        python_code = self._optimize_for_tiff_workflow(python_code)
        python_code = self._add_script_header(python_code, notebook_path)
        
        # Write Python script
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        print(f"Converted {notebook_path.name} -> {output_path.name}")
        return str(output_path)
    
    def _extract_code_cells(self, notebook: Dict[str, Any]) -> str:
        """Extract and combine code cells from notebook."""
        code_lines = []
        
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = cell.get('source', [])
                if isinstance(source, list):
                    cell_code = ''.join(source)
                else:
                    cell_code = source
                
                # Skip empty cells and magic commands
                if cell_code.strip() and not cell_code.strip().startswith('%'):
                    # Add cell separator comment
                    code_lines.append(f"\n# Cell: {len(code_lines) + 1}\n")
                    code_lines.append(cell_code)
                    code_lines.append("\n")
        
        return ''.join(code_lines)
    
    def _optimize_for_tiff_workflow(self, code: str) -> str:
        """Update code for TIFF-first workflow."""
        
        # Replace old save_figure calls
        patterns = [
            # save_figure with formats parameter
            (r'save_figure\(([^,]+),\s*([^,]+)(?:,\s*[^,]+)?(?:,\s*formats=\([^)]+\))?\)',
             r'save_figure(\1, \2, include_pdf=True)'),
            
            # plt.savefig calls
            (r'plt\.savefig\([^)]+\)',
             'save_figure(plt.gcf(), "figure_name")  # TODO: Set proper filename'),
            
            # fig.savefig calls  
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\.savefig\([^)]+\)',
             r'save_figure(\1, "figure_name")  # TODO: Set proper filename'),
        ]
        
        for pattern, replacement in patterns:
            code = re.sub(pattern, replacement, code)
        
        return code
    
    def _add_script_header(self, code: str, original_path: Path) -> str:
        """Add proper imports and header to the script."""
        
        header = f'''#!/usr/bin/env python3
"""
Analysis script converted from {original_path.name}

This script generates publication-ready figures in TIFF format for LaTeX integration.
Run this script to regenerate all figures for this analysis.
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Standard imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Project imports
from shared.utils.plot_styles import set_plot_style
from shared.utils.helpers import save_figure, create_figure
from shared.utils.config import *
from shared.scripts.data_loading import load_csv, load_excel

# Set global plot style
set_plot_style()

# Analysis code from notebook
'''
        
        # Check if imports are already present and avoid duplicates
        existing_imports = set()
        for line in code.split('\n'):
            if line.strip().startswith(('import ', 'from ')):
                existing_imports.add(line.strip())
        
        # Remove duplicate imports from the header
        header_lines = header.split('\n')
        final_header_lines = []
        for line in header_lines:
            if line.strip().startswith(('import ', 'from ')):
                if line.strip() not in existing_imports:
                    final_header_lines.append(line)
            else:
                final_header_lines.append(line)
        
        return '\n'.join(final_header_lines) + '\n\n' + code
    
    def convert_all_notebooks(self, backup: bool = True) -> List[str]:
        """
        Convert all notebooks in the project to Python scripts.
        
        Args:
            backup: Create .ipynb.bak backups before conversion
            
        Returns:
            List of converted script paths
        """
        notebooks = list(self.project_root.glob("**/analysis/*.ipynb"))
        converted_scripts = []
        
        print(f"Found {len(notebooks)} notebooks to convert:")
        for nb in notebooks:
            print(f"  {nb.relative_to(self.project_root)}")
        
        for notebook_path in notebooks:
            if backup:
                backup_path = notebook_path.with_suffix('.ipynb.bak')
                if not backup_path.exists():
                    backup_path.write_bytes(notebook_path.read_bytes())
                    print(f"  Backed up to {backup_path.name}")
            
            script_path = self.convert_notebook(notebook_path)
            converted_scripts.append(script_path)
        
        return converted_scripts
    
    def update_analysis_structure(self) -> None:
        """Update analysis directories with proper __init__.py files."""
        
        analysis_dirs = [d for d in self.project_root.glob("*/analysis") if d.is_dir()]
        
        for analysis_dir in analysis_dirs:
            init_file = analysis_dir / "__init__.py"
            if not init_file.exists():
                init_content = f'''"""
{analysis_dir.parent.name} Analysis Module

This module contains analysis scripts for {analysis_dir.parent.name}.
All scripts generate TIFF figures for LaTeX integration.
"""
'''
                init_file.write_text(init_content)
                print(f"Created __init__.py in {analysis_dir}")


def main():
    """Command line interface for notebook conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert Jupyter notebooks to Python scripts")
    parser.add_argument("--no-backup", action="store_true", 
                       help="Don't create .ipynb.bak backup files")
    parser.add_argument("--single", type=str,
                       help="Convert single notebook file")
    
    args = parser.parse_args()
    
    converter = NotebookConverter()
    
    if args.single:
        notebook_path = Path(args.single)
        if notebook_path.exists():
            converter.convert_notebook(notebook_path)
        else:
            print(f"Notebook not found: {notebook_path}")
            return 1
    else:
        converted = converter.convert_all_notebooks(backup=not args.no_backup)
        converter.update_analysis_structure()
        print(f"\nConversion complete! Converted {len(converted)} notebooks.")
        print("\nNext steps:")
        print("1. Review the generated Python scripts")
        print("2. Update figure filenames in save_figure() calls")
        print("3. Run scripts to generate TIFF figures")
        print("4. Update LaTeX integration")
    
    return 0


if __name__ == "__main__":
    exit(main())