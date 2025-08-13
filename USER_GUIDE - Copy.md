# Paper2 Project - Complete Integration User Guide

This guide explains how to use the fully integrated analysis and LaTeX workflow with TIFF-first figure generation.

## 🎯 Quick Start

For the complete workflow (analysis → figures → LaTeX):
```bash
make all
```

This single command will:
1. Run all analysis scripts to generate TIFF figures
2. Sync figures to the LaTeX directory  
3. Build the final PDF document

## 📁 Project Structure

```
Paper2/
├── 01_Hybrid_Growth/analysis/          # Growth per cycle analysis
├── 02_Air_Stability/analysis/          # Environmental stability studies  
├── 03_Developer_Stability_*/analysis/  # Chemical resistance analysis
├── 05_FTIR_Analysis/analysis/          # Spectroscopy analysis
├── 06_XPS_Analysis/analysis/           # Surface composition analysis
├── 08_E-Beam_Studies/analysis/         # Lithography studies
├── LaTeX/                              # Integrated LaTeX document
├── shared/
│   ├── utils/                          # Common plotting and utilities
│   ├── scripts/                        # Integration and conversion scripts
│   └── config/                         # Configuration files
├── run_analysis.py                     # Master analysis runner
└── Makefile                            # Convenient command shortcuts
```

## 🔄 Workflow Components

### 1. Analysis Scripts (Python)
All Jupyter notebooks have been converted to Python scripts for better automation:

- **Location**: `*/analysis/*.py`
- **Output**: TIFF figures in `*/figures/final/`
- **Integration**: Automatic imports of shared utilities

### 2. Figure Management (TIFF-First)
- **Primary format**: TIFF (lossless, publication-quality)
- **LaTeX compatibility**: XeLaTeX handles TIFF natively
- **Backup formats**: PDF/PNG available via `include_pdf=True`, `include_png=True`

### 3. LaTeX Integration
- **Automatic sync**: Figures copied from analysis to LaTeX/Figures/
- **Build system**: XeLaTeX + Biber for bibliography
- **Figure mapping**: Centralized in `shared/config/figure_mapping.yaml`

## 🚀 Available Commands

### Complete Workflows
```bash
make all            # Full pipeline: analysis + sync + build
make analysis       # Generate all figures (no LaTeX build)  
make build          # Sync figures + build LaTeX (no analysis)
```

### Individual Steps
```bash
make sync           # Sync figures to LaTeX only
make clean          # Clean LaTeX auxiliary files
make report         # Generate status report
```

### Development
```bash
make jupyter        # Start Jupyter for development
make test           # Run tests (if available)
make install-deps   # Install Python dependencies
make latex-deps     # Check LaTeX installation
```

## 🔧 Advanced Usage

### Custom Analysis Runs
```bash
# Run analysis with custom timeout
python run_analysis.py --timeout 900

# Skip building LaTeX
python run_analysis.py --no-build  

# Clean LaTeX build before compiling
python run_analysis.py --clean-build

# Generate and save report
python run_analysis.py --report analysis_report.md
```

### Manual Figure Operations  
```bash
# Sync specific analysis figures
python shared/scripts/latex_integration.py sync

# Update XPS figure mappings specifically
python shared/scripts/update_xps_figures.py

# Convert specific notebook to Python
python shared/scripts/convert_notebooks.py --single 06_XPS_Analysis/analysis/XPS_Figure_Best.ipynb
```

## 🎨 Creating New Analysis

### 1. Set Up Analysis Script
```python
#!/usr/bin/env python3
"""
New analysis script template
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Standard imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Project imports  
from shared.utils.plot_styles import set_plot_style
from shared.utils.helpers import save_figure, create_figure
from shared.utils.config import *

# Set global plot style
set_plot_style()

# Your analysis code here...

# Save figures
fig, ax = create_figure(width_cm=18)
# ... plotting code ...
save_figure(fig, "New_Figure_Name", include_pdf=True)
```

### 2. Update Figure Mapping
Add your new figures to `shared/config/figure_mapping.yaml`:
```yaml
your_analysis/figures/final/new_figure.tiff: Figures/new_figure.tiff
```

### 3. Update Analysis Runner
Add your script to `run_analysis.py`:
```python
self.analysis_scripts = [
    # ... existing scripts ...
    "your_analysis/analysis/your_script.py",
]
```

## 📊 Figure Quality Standards

### TIFF Configuration
- **DPI**: 600 for publication quality
- **Compression**: LZW (lossless)
- **Color**: Full color support
- **Size**: 18cm width standard

### Plot Styling
- **Font**: Verdana, 10pt base size
- **Lines**: 1.5pt width
- **Frames**: 3pt thick black borders
- **Ticks**: On all sides, inward direction
- **Colors**: Viridis palette default

## 🔍 Troubleshooting

### Common Issues

**Analysis Script Fails**
```bash
# Run individual script for debugging
cd 01_Hybrid_Growth/analysis
python Alucone_Zincone_GPC.py
```

**Figure Not Syncing**
```bash
# Check figure mapping
python shared/scripts/latex_integration.py report

# Force sync specific figure
python shared/scripts/latex_integration.py sync
```

**LaTeX Build Fails**  
```bash
# Check LaTeX dependencies
make latex-deps

# Clean and rebuild
make clean
make build
```

**Missing Dependencies**
```bash
# Install Python packages
make install-deps

# For conda users
conda env create -f environment.yml
```

### Debug Mode
For detailed debugging:
```bash
# Verbose analysis run
python run_analysis.py --timeout 1200 --report debug_report.txt

# Check individual components
python shared/scripts/latex_integration.py report
```

## 📋 Dependencies

### Required Python Packages
- matplotlib >= 3.5
- numpy >= 1.20  
- pandas >= 1.3
- seaborn >= 0.11
- pyyaml >= 5.4

### Required LaTeX Packages
- XeLaTeX (TeX Live or MiKTeX)
- biber (bibliography processor)
- Essential packages: fontspec, siunitx, biblatex, mhchem, chemfig, booktabs

### System Requirements
- Python 3.8+
- Git (for version control)
- 2GB+ free space (for LaTeX distribution)

## 🎯 Best Practices

1. **Always run `make all`** for complete workflow
2. **Test individual scripts** before running full pipeline  
3. **Keep figure names consistent** with paper structure
4. **Use TIFF for final figures**, PDF for compatibility
5. **Check `make report`** to verify sync status
6. **Commit Python scripts**, keep notebooks as backups
7. **Review LaTeX output** for figure quality

## 🆘 Getting Help

1. **Check logs**: Analysis scripts output detailed error messages
2. **Run reports**: `make report` shows current status
3. **Manual debugging**: Run individual scripts in their directories
4. **Environment issues**: Verify all dependencies with `make latex-deps`

This integrated workflow ensures reproducible, high-quality figure generation and seamless LaTeX document compilation. The TIFF-first approach provides publication-ready quality while maintaining full automation.