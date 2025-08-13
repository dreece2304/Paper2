#!/usr/bin/env python3
"""
Analysis script converted from 03_final_figure_air_stability.ipynb

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
import seaborn as sns

# Project imports
from shared.utils.plot_styles import set_plot_style
from shared.utils.helpers import save_figure, create_figure
from shared.utils.config import *
from shared.scripts.data_loading import load_csv, load_excel

# Set global plot style
set_plot_style()

# Analysis code from notebook



# Cell: 1
# %% [markdown]
"""
# Final Air Stability Figure
Creates a polished six-panel figure showing normalized thickness decay in air for Alucone and Zincone hybrid films (as-deposited and UV-treated).
"""

# %% [Setup]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

from shared.utils.config import organics, inorganics, colors
from shared.utils.helpers import create_figure, save_figure
from shared.scripts.data_loading import load_excel

# === LaTeX TIFF Figure Generation ===
latex_figures_dir = Path("/mnt/c/Users/dreec/PycharmProjects/Paper2/LaTeX/High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_/Figures")
latex_figures_dir.mkdir(exist_ok=True)
print(f"📁 LaTeX figures will be saved to: {latex_figures_dir}")

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
    print(f"✅ LaTeX figure saved: {filename}.tiff")
    return saved_files


# === LaTeX TIFF Figure Generation ===
latex_figures_dir = Path("/mnt/c/Users/dreec/PycharmProjects/Paper2/LaTeX/High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_/Figures")
latex_figures_dir.mkdir(exist_ok=True)
print(f"📁 LaTeX figures will be saved to: {latex_figures_dir}")

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
    print(f"✅ LaTeX figure saved: {filename}.tiff")
    return saved_files


# Section-specific settings
time_limit_minutes = 60
sampling_rate = 10

# Excel file paths (local to this section)
excel_map = {
    'Al': '../data/raw/alucone.xlsx',
    'Zn': '../data/raw/zincone.xlsx'
}

# %% [Data Loading and Preprocessing]

def preprocess_series(x, y, limit_minutes=60, step=10):
    """
    Normalize thickness and downsample.
    """
    y_norm = y / y.iloc[0] if y.iloc[0] != 0 else y
    mask = x <= limit_minutes
    return (
        x[mask].iloc[::step].reset_index(drop=True),
        y_norm[mask].iloc[::step].reset_index(drop=True)
    )

# Load and preprocess data
data = {}
for metal, filepath in excel_map.items():
    df = load_excel(filepath)
    cols = df.columns.tolist()
    pairs = [(cols[i], cols[i+1]) for i in range(0, len(cols), 2) if i+1 < len(cols)]
    metal_dict = {}
    for xcol, ycol in pairs:
        uv_flag = ycol.endswith(' UV')
        org = ycol.replace(' UV', '')
        if org in organics:
            x_proc, y_proc = preprocess_series(df[xcol], df[ycol], time_limit_minutes, sampling_rate)
            metal_dict.setdefault(org, {})[uv_flag] = (x_proc, y_proc)
    data[metal] = metal_dict

# Calculate global axis limits
all_x = [arr[0].values for md in data.values() for series in md.values() for arr in series.values()]
all_y = [arr[1].values for md in data.values() for series in md.values() for arr in series.values()]
x_min, x_max = np.min(np.concatenate(all_x)), np.max(np.concatenate(all_x))
y_min, y_max = 0, np.max(np.concatenate(all_y)) * 1.15

# %% [Plotting]

# Create figure
fig, axes = create_figure(rows=3, cols=2, width_cm=fig_width_cm, aspect_ratio=2/3, sharex=False, sharey=False)
panel_labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']

# Plot loop
for idx, org in enumerate(organics):
    ax = axes[idx]
    for metal in inorganics:
        series = data.get(metal, {}).get(org, {})
        for uv_flag, linestyle in [(False, '-'), (True, '--')]:
            if uv_flag in series:
                x, y = series[uv_flag]
                label = f"{metal} ({'UV-treated' if uv_flag else 'As-deposited'})"
                ax.plot(
                    x, y,
                    color=colors[(metal, uv_flag)],
                    linestyle=linestyle,
                    linewidth=1.5,
                    label=label
                )
    # Panel label
    ax.text(0.04, 0.97, panel_labels[idx],
            transform=ax.transAxes,
            fontweight='bold',
            va='top', ha='left')
    # Set consistent limits across all panels - ensure 60 minute mark is visible
    ax.set_xlim(x_min, min(x_max, 60))  # Ensure we show up to 60 minutes
    ax.set_ylim(y_min, y_max)
    
    # X-axis ticks: 0, 10, 20, 30, 40, 50, 60 with minor ticks every 5 minutes
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    
    # Y-axis ticks: 0, 0.25, 0.5, 0.75, 1.0, 1.25 with minor ticks 
    ax.yaxis.set_major_locator(MultipleLocator(0.25))
    ax.yaxis.set_minor_locator(MultipleLocator(0.125))  # Minor ticks every 0.125 for at least one between majors
    
    # Remove grid lines and ensure proper tick formatting
    ax.grid(False)
    ax.tick_params(direction='in', which='both', length=4, width=1.0, colors='black')
    ax.tick_params(axis='y', which='major', left=True, right=True, top=False, bottom=False)
    ax.tick_params(axis='x', which='major', left=False, right=False, top=True, bottom=True)  # Added top=True for x-axis
    
    # Ensure all panels show tick labels (since sharex/sharey are now False)
    ax.tick_params(axis='x', labelbottom=True, labeltop=False)
    ax.tick_params(axis='y', labelleft=True, labelright=False)
    
    # Get panel position for shared 0 label logic
    row, col = idx // 2, idx % 2  # Get row and column position
    
    # Hide 0 labels except on bottom-left corner - cleaner approach
    if not (row == 2 and col == 0):  # Not bottom-left panel
        # Hide 0 tick labels by replacing with empty string
        xlabels = ax.get_xticklabels()
        ylabels = ax.get_yticklabels()
        
        # Replace 0 labels with empty strings
        for label in xlabels:
            if label.get_text() == '0':
                label.set_text('')
        for label in ylabels:
            if label.get_text() == '0.0' or label.get_text() == '0':
                label.set_text('')
    
    # Ensure consistent spine formatting
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
        spine.set_color('black')
    
    # Add individual axis labels to each panel
    ax.set_xlabel('Time (minutes)')
    ax.set_ylabel('Normalized thickness')

# Hide unused subplots (if fewer than 6 organics, unlikely here)
for i in range(len(organics), len(axes)):
    axes[i].axis('off')

# Create single shared legend at the bottom
# Get handles and labels from the first subplot that has data
handles, labels = None, None
for ax in axes:
    if ax.get_legend_handles_labels()[0]:  # If this axis has legend data
        handles, labels = ax.get_legend_handles_labels()
        break

if handles and labels:
    # Create shared legend below all panels
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.08), 
              ncol=len(labels), frameon=True, edgecolor='black', fancybox=False, framealpha=1.0)

# Layout adjustment - increased margins for individual labels and shared legend
fig.subplots_adjust(
    left=0.12, right=0.96,
    bottom=0.25, top=0.92,  # Increased bottom margin for lower legend position
    wspace=0.25, hspace=0.35  # Increased spacing for individual axis labels
)

# Save figure
save_figure(fig, filename="Fig3_Air_Stability", include_pdf=True, include_png=True)
save_for_latex(fig, "Fig3_Air_Stability")
# plt.show() removed - causes warnings in non-interactive environments

