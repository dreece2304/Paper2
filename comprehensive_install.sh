#!/bin/bash
# Comprehensive Scientific Analysis Environment Setup
# For FTIR spectroscopy, interactive analysis, and publication-quality output

echo "🚀 Installing mamba for faster package management..."
conda install -c conda-forge mamba -y

echo "📦 Installing comprehensive scientific analysis environment..."

# COMPREHENSIVE MAMBA INSTALLATION (all conda-available packages)
mamba install -c conda-forge \
    `# Core Scientific Stack` \
    numpy pandas matplotlib seaborn scipy scikit-learn statsmodels \
    `# Jupyter & Interactive Development` \
    jupyter jupyterlab ipython ipywidgets bqplot voila \
    `# Advanced Plotting & Visualization` \
    plotly bokeh holoviews panel param altair plotnine \
    `# Interactive Apps & Dashboards` \
    streamlit dash gradio \
    `# Peak Fitting & Spectroscopy Analysis` \
    lmfit uncertainties peakutils \
    `# Advanced Analysis & Statistics` \
    emcee corner sympy \
    `# Signal Processing` \
    pywavelets scikit-image \
    `# Machine Learning & Dimensionality Reduction` \
    umap-learn hdbscan \
    `# Performance & Parallel Computing` \
    numba dask joblib \
    `# Color & Style Enhancement` \
    colorcet cmocean palettable \
    `# File I/O & Data Formats` \
    h5py netcdf4 pyarrow openpyxl xlsxwriter xlrd \
    `# Development & Code Quality` \
    black isort mypy pre-commit pytest \
    `# Image Processing & Graphics` \
    pillow imageio scikit-image \
    `# LaTeX & Document Processing` \
    pandoc \
    `# Network & Web Tools` \
    requests beautifulsoup4 \
    -y

echo "🔬 Installing specialized packages via pip (not available in conda)..."

# SPECIALIZED PACKAGES (pip-only)
pip install \
    `# Advanced Spectroscopy` \
    pybaselines rampy specutils hyperspy jcamp \
    `# Advanced Peak Analysis` \
    multipeak baseline-correction \
    `# Chemistry & Molecular Tools` \
    pubchempy chemparse \
    `# Enhanced Interactive Tools` \
    ipympl plotly-dash-components \
    `# LaTeX Integration` \
    pylatex latexify-py \
    `# Paper & Bibliography Management` \
    scholarly bibtexparser \
    `# Advanced Visualization` \
    distinctipy mplcursors \
    `# Performance Profiling` \
    memory-profiler line-profiler \
    `# Additional Utilities` \
    tqdm rich click typer

echo "✅ Installation complete!"
echo "🎯 Next steps:"
echo "1. Restart your Jupyter kernel"
echo "2. Test with: python -c 'import lmfit, plotly, streamlit; print(\"All packages working!\")'"
echo "3. Consider installing LaTeX system separately for document compilation"