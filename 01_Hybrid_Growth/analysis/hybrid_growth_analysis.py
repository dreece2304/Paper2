#!/usr/bin/env python3
"""
Analysis script converted from Alucone_Zincone_GPC.ipynb

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

# Project imports
from shared.utils.plot_styles import set_plot_style
from shared.utils.helpers import save_figure, create_figure
from shared.utils.config import *
from shared.scripts.data_loading import load_csv, load_excel

# Set global plot style
set_plot_style()

# Analysis code from notebook



# Cell: 1
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shared.utils.plot_styles import set_plot_style
from shared.utils.helpers import save_figure, get_figure_size
from shared.utils.config import fig_width_cm, organics

# Set styling
set_plot_style()

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


# Load and clean data
gpc_df = pd.read_csv("../data/processed/Alucone_Zincone_GPC.csv")
gpc_df['Organic'] = pd.Categorical(gpc_df['Organic'], categories=organics, ordered=True)
gpc_df['Metal'] = gpc_df['Inorganic'].map({'TMA': 'Al', 'DEZ': 'Zn'})

figsize = get_figure_size(fig_width_cm, aspect_ratio=4/3)

# --- Plot A: Thickness ---
fig1, ax1 = plt.subplots(figsize=figsize)

sns.barplot(
    data=gpc_df,
    x='Organic', y='Thickness',
    hue='Metal',
    ax=ax1,
    palette='viridis'
)

ax1.set_xlabel("Organic Precursor")
ax1.set_ylabel("Thickness (nm)")
ax1.legend(title="Metal", edgecolor='black', fancybox=False, framealpha=1.0)

# Remove grid lines and set proper y-axis limits
ax1.grid(False)
ax1.set_ylim(0, gpc_df['Thickness'].max() * 1.1)

# Ensure axis lines are black and consistent thickness
for spine in ax1.spines.values():
    spine.set_color('black')
    spine.set_linewidth(1.0)

# Fix y-axis tick marks and labels - thickness ranges from ~49 to ~668 nm
ax1.yaxis.set_major_locator(plt.MultipleLocator(100))  # Major ticks every 100 nm
ax1.yaxis.set_minor_locator(plt.MultipleLocator(50))   # Minor ticks every 50 nm

# Force tick marks to be visible with explicit settings
ax1.tick_params(axis='y', which='major', direction='in', colors='black', length=6, width=1.0, 
                left=True, right=True, top=False, bottom=False)
ax1.tick_params(axis='y', which='minor', direction='in', colors='black', length=3, width=0.5,
                left=True, right=True, top=False, bottom=False)
ax1.tick_params(axis='x', which='major', direction='in', colors='black', length=6, width=1.0,
                left=False, right=False, top=False, bottom=True)

fig1.tight_layout()
save_figure(fig1, "Fig2a_Metalcone_Thickness", folder="../figures/draft/", include_pdf=True, include_png=True)

# --- Plot B: GPC ---
fig2, ax2 = plt.subplots(figsize=figsize)

sns.barplot(
    data=gpc_df,
    x='Organic', y='GPC',
    hue='Metal',
    ax=ax2,
    palette='viridis'
)

ax2.set_xlabel("Organic Precursor")
ax2.set_ylabel("Growth Per Cycle (Å/cycle)")
ax2.legend(title="Metal", edgecolor='black', fancybox=False, framealpha=1.0)

# Remove grid lines and set proper y-axis limits
ax2.grid(False)
ax2.set_ylim(0, gpc_df['GPC'].max() * 1.1)

# Ensure axis lines are black and consistent thickness
for spine in ax2.spines.values():
    spine.set_color('black')
    spine.set_linewidth(1.0)

# Fix y-axis tick marks and labels - GPC ranges from ~0.49 to ~6.67 Å/cycle
ax2.yaxis.set_major_locator(plt.MultipleLocator(1))    # Major ticks every 1 Å/cycle
ax2.yaxis.set_minor_locator(plt.MultipleLocator(0.5))  # Minor ticks every 0.5 Å/cycle

# Force tick marks to be visible with explicit settings
ax2.tick_params(axis='y', which='major', direction='in', colors='black', length=6, width=1.0,
                left=True, right=True, top=False, bottom=False)
ax2.tick_params(axis='y', which='minor', direction='in', colors='black', length=3, width=0.5,
                left=True, right=True, top=False, bottom=False)
ax2.tick_params(axis='x', which='major', direction='in', colors='black', length=6, width=1.0,
                left=False, right=False, top=False, bottom=True)

fig2.tight_layout()
save_figure(fig2, "Fig2_Metalcone_GPC", include_pdf=True, include_png=True)

# plt.show() removed - causes warnings in non-interactive environments

