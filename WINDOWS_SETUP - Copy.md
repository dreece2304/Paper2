# Paper2 Windows Setup Guide

This guide helps you set up and run the Paper2 analysis pipeline in PyCharm on Windows 11.

## 🚀 Quick Start

### Option 1: Using PyCharm (Recommended)
1. Open PyCharm and load the Paper2 project
2. In the Run/Debug configurations dropdown, select:
   - **"Test Environment"** - Verify everything works
   - **"Complete Analysis Pipeline"** - Run everything
   - **"Generate Figures Only"** - Skip LaTeX build
   - **"Sync and Build LaTeX"** - Skip analysis, just build

### Option 2: Using Windows Batch File
1. Double-click `run_windows.bat` in the project folder
2. Follow the interactive menu

### Option 3: Using Command Line
```cmd
# Set environment for matplotlib
set MPLBACKEND=Agg

# Test environment
python test_environment.py

# Run complete pipeline
python run_analysis.py
```

## 🔧 Initial Setup

### 1. Python Environment
Ensure you have Python 3.8+ installed with required packages:
```cmd
pip install matplotlib pandas seaborn numpy pyyaml
```

### 2. PyCharm Configuration
- **File → Settings → Project → Python Interpreter**
- Ensure the correct Python environment is selected
- Add project root to PYTHONPATH if needed

### 3. Environment Variables (for PyCharm)
In Run Configurations, add these environment variables:
- `MPLBACKEND=Agg` (fixes matplotlib display issues)
- `PYTHONUNBUFFERED=1` (real-time output)

## 📁 File Structure

```
Paper2/
├── run_windows.bat              # Windows batch launcher
├── test_environment.py          # Environment verification
├── run_analysis.py             # Main analysis runner
├── .idea/runConfigurations/    # PyCharm run configs
├── */analysis/*.py             # Analysis scripts (converted from notebooks)
└── */analysis/*.ipynb.bak      # Original notebook backups
```

## 🔍 Troubleshooting

### Common Issues

**"Qt platform plugin" errors:**
- Fixed by setting `MPLBACKEND=Agg` 
- Already configured in run configurations

**Import errors:**
- Run `python test_environment.py` to diagnose
- Check Python interpreter in PyCharm settings

**Analysis scripts fail:**
- Scripts need manual completion from notebook backups
- See "Completing Analysis Scripts" section below

### Fixing Analysis Scripts
The converted Python scripts are templates. To complete them:

1. Open the `.py` file in PyCharm
2. Open the corresponding `.ipynb.bak` file 
3. Copy the analysis code from the notebook to the Python script
4. Replace the TODO section with your actual analysis
5. Ensure proper figure naming in `save_figure()` calls

**Example conversion:**
```python
# Replace this template code:
def main():
    print("⚠️  This script needs manual completion!")
    # TODO: Add analysis code
    
# With your actual analysis:
def main():
    # Load data
    df = pd.read_csv("../data/processed/your_data.csv")
    
    # Create figure
    fig, ax = create_figure(width_cm=18)
    ax.plot(df['x'], df['y'])
    
    # Save figure
    save_figure(fig, "Your_Figure_Name", include_pdf=True)
```

## 🎯 Workflow Steps

### 1. Environment Verification
```cmd
python test_environment.py
```
This checks:
- All Python packages are installed
- Shared utilities can be imported
- Figure generation works
- LaTeX integration is available

### 2. Complete Analysis Pipeline
```cmd
python run_analysis.py
```
This will:
- Run all analysis scripts to generate TIFF figures
- Sync figures to LaTeX directory
- Build the LaTeX document (if xelatex/biber available)

### 3. Individual Components
```cmd
# Generate figures only
python run_analysis.py --no-build

# Sync and build LaTeX only  
python run_analysis.py --skip-analysis

# Generate status report
python shared/scripts/latex_integration.py report
```

## 📊 PyCharm Run Configurations

The project includes pre-configured run configurations:

- **Test Environment**: Verify setup works
- **Complete Analysis Pipeline**: Full workflow
- **Generate Figures Only**: Analysis without LaTeX
- **Sync and Build LaTeX**: LaTeX build without analysis

Access these in the Run/Debug dropdown in PyCharm.

## 🔧 Manual Analysis Script Completion

Since the automatic notebook conversion creates templates, you'll need to complete the analysis scripts manually:

### Template Structure
```python
#!/usr/bin/env python3
"""Script description"""

# Imports (already configured)
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import matplotlib
matplotlib.use('Agg')  # For Windows compatibility

# Your imports...

def main():
    """Main analysis function."""
    # TODO: Add your analysis code here
    pass

if __name__ == "__main__":
    main()
```

### Key Points
1. **Imports are pre-configured** - use them as-is
2. **Add your analysis in main()** - copy from notebook backup
3. **Use save_figure()** for TIFF output
4. **Test individual scripts** before running pipeline

## 🆘 Getting Help

1. **Run environment test first**: `python test_environment.py`
2. **Check PyCharm console** for detailed error messages
3. **Use batch file** for interactive troubleshooting
4. **Check original notebooks** in `.ipynb.bak` files

## 📈 Next Steps

Once setup is working:
1. Complete the analysis scripts by copying from notebook backups
2. Test individual scripts in PyCharm
3. Run the complete pipeline
4. Check generated TIFF figures in `*/figures/final/`
5. Verify LaTeX integration works

The TIFF-first workflow ensures high-quality figures for publication while maintaining full automation.