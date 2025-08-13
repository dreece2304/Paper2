# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a scientific research project focused on materials characterization, specifically studying hybrid organic-inorganic thin films (metalcones) including alucone and zincone materials. The project analyzes various properties including growth characteristics, air stability, developer stability, and spectroscopic characterization through FTIR and XPS.

## Architecture and Structure

### Directory Organization
The project follows a numbered experimental structure:
- `01_Hybrid_Growth/` - Growth per cycle (GPC) analysis
- `02_Air_Stability/` - Time-based degradation studies
- `03_Developer_Stability_Patterning_Contrast/` - Etching and solvent stability
- `05_FTIR_Analysis/` - Fourier-transform infrared spectroscopy
- `06_XPS_Analysis/` - X-ray photoelectron spectroscopy
- `08_E-Beam_Studies/` - Electron beam lithography studies
- `shared/` - Common utilities and configuration

### Standard Directory Pattern
Each experimental directory follows the pattern:
- `analysis/` - Jupyter notebooks for data analysis
- `data/` - Raw and processed data files
  - `raw/` - Original experimental data
  - `processed/` - Cleaned and processed datasets
- `figures/` - Generated visualizations
  - `draft/` - Working figures
  - `final/` - Publication-ready figures

### Key Configuration Files
- `shared/utils/config.py` - Global constants including:
  - Organic compounds list: `['EG', 'CB', 'BTY', 'THB', 'MPD', 'DHB']`
  - Inorganic materials: `['Al', 'Zn']`
  - Solvent ordering for consistent analysis
  - Color schemes and figure sizing (18cm width)
- `shared/utils/plot_styles.py` - Publication-ready matplotlib styling
- `shared/utils/helpers.py` - Common utility functions for file operations and figure generation

### Data Processing Pipeline
1. Raw data (Excel, CSV, spectroscopy files) in `data/raw/`
2. Processing notebooks in `analysis/`
3. Processed data saved to `data/processed/`
4. Final figures exported to `figures/final/` in multiple formats (PDF, PNG, SVG)

## Development Commands

### Running Analysis
This project uses Jupyter notebooks for analysis. To run:
```bash
jupyter notebook  # or jupyter lab
```

### Complete Analysis Pipeline (TIFF Workflow)
Run the complete integrated workflow:
```python
# Complete pipeline: analysis + sync + LaTeX build
python run_analysis.py

# Generate TIFF figures only  
python run_analysis.py --no-build

# Sync existing figures to LaTeX and build
python run_analysis.py --skip-analysis

# Interactive menu for all options
python run_interactive.py
```

### Setup and Environment
Python-only setup for conda environments:
```python
# Install all required packages
python install_requirements.py

# Test environment and verify setup
python test_environment.py

# Setup PyCharm configurations  
python setup_pycharm.py

# Simple launcher with menu
python launcher.py
```

### Analysis Scripts (Python)
All Jupyter notebooks have been converted to Python scripts for better integration:
```python
# Run individual analysis (example)
cd 01_Hybrid_Growth/analysis && python Alucone_Zincone_GPC.py

# Run with custom options
python run_analysis.py --timeout 300 --clean-build

# Interactive menu for all operations
python run_interactive.py
```

### Data Loading
Use the centralized data loading utilities:
```python
from shared.scripts.data_loading import load_data
```

### Plotting Configuration
Always import and apply the standard plotting style:
```python
from shared.utils.plot_styles import set_plot_style
from shared.utils.config import *
set_plot_style()
```

## Code Conventions

### Imports
- Use centralized configuration from `shared/utils/config.py`
- Apply standard plotting styles from `shared/utils/plot_styles.py`
- Leverage shared utilities for file operations and data loading

### Figure Generation (TIFF-First Workflow)
- Use 18cm width standard (`fig_width_cm = 18`)
- **Primary format: TIFF** for LaTeX integration (lossless, high-quality)
- Save figures using `save_figure()` from `shared/utils/helpers.py`
- Follow consistent naming: `Fig{number}_{description}`
- Export to `figures/final/` directory only

```python
# Recommended figure saving
from shared.utils.helpers import save_figure, create_figure

fig, ax = create_figure(width_cm=18)
# ... plotting code ...
save_figure(fig, "Fig2_Metalcone_GPC", include_pdf=True, include_png=True)  # TIFF + PDF + PNG for all uses
```

### Data Consistency
- Use predefined organic compound ordering from config
- Follow solvent ordering for consistent analysis
- Apply standard color schemes (viridis palette)
- Maintain consistent axis styling and font choices (Verdana)

## File Types and Formats
- Analysis: Jupyter notebooks (.ipynb)
- Data: Excel (.xlsx), CSV, specialized formats (.sff, .vms, .spm)
- Figures: PDF (publication), PNG (preview), SVG (vector)
- Configuration: Python modules (.py)