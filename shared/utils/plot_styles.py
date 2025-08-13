import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager

def set_plot_style():
    """
    Set the global plot style for all figures to match publication standards.
    Ensures consistent, high-quality formatting across all analyses.
    """

    # Update matplotlib defaults for publication quality
    plt.rcParams.update({
        # Fonts - RSC Journal optimized typography
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans', 'Verdana'],
        'font.size': 10,           # Base font size - RSC optimized
        'axes.titlesize': 12,      # Plot titles
        'axes.labelsize': 11,      # Axis labels
        'xtick.labelsize': 9,      # X-axis tick labels
        'ytick.labelsize': 9,      # Y-axis tick labels
        'legend.fontsize': 9,      # Legend text
        'figure.titlesize': 14,    # Figure suptitle

        # Text and math rendering
        'text.usetex': False,      # Use matplotlib's mathtext (more reliable)
        'mathtext.default': 'regular',
        
        # Line and marker styles - RSC journal optimized
        'lines.linewidth': 1.5,    # Reduced from 2.0 for journal compliance
        'lines.markersize': 6,     # Standard marker size
        'lines.markeredgewidth': 0.5,

        # Axis spine styling - professional look
        'axes.linewidth': 1.0,     # Reduced from 1.5 for journal compliance
        'axes.edgecolor': 'black', # Frame color
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.spines.top': True,
        'axes.spines.right': True,

        # Tick styling - consistent across all plots
        'xtick.top': True,
        'xtick.bottom': True,
        'ytick.left': True,
        'ytick.right': True,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.major.size': 4,     # Tick length
        'ytick.major.size': 4,
        'xtick.minor.size': 2,     # Minor tick length
        'ytick.minor.size': 2,
        'xtick.major.width': 1.0,  # Tick thickness
        'ytick.major.width': 1.0,
        'xtick.minor.width': 0.5,
        'ytick.minor.width': 0.5,

        # Grid - subtle when enabled
        'axes.grid': False,
        'axes.grid.axis': 'both',
        'grid.color': '#E5E5E5',
        'grid.linewidth': 0.8,
        'grid.alpha': 0.7,

        # Colors and colormaps
        'image.cmap': 'viridis',   # Default colormap
        'axes.prop_cycle': plt.cycler('color', 
            ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
             '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']),

        # Legend styling
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'legend.fancybox': True,
        'legend.numpoints': 1,
        'legend.scatterpoints': 1,
        'legend.borderpad': 0.4,
        'legend.columnspacing': 1.0,
        'legend.handlelength': 1.5,
        'legend.handletextpad': 0.5,

        # Figure and subplot spacing
        'figure.subplot.left': 0.1,
        'figure.subplot.bottom': 0.1,
        'figure.subplot.right': 0.9,
        'figure.subplot.top': 0.9,
        'figure.subplot.wspace': 0.2,
        'figure.subplot.hspace': 0.2,

        # Resolution and quality
        'figure.dpi': 150,         # Screen display
        'savefig.dpi': 600,        # High-res export
        'savefig.format': 'png',   # Default save format
        'savefig.bbox': 'tight',   # Tight bounding box
        'savefig.pad_inches': 0.1, # Padding around figure
        'savefig.transparent': False,
        
        # Error bars
        'errorbar.capsize': 3,
        
        # Scatter plots
        'scatter.marker': 'o',
        
        # Patches (bars, etc.)
        'patch.linewidth': 0.5,
        'patch.edgecolor': 'black',
    })

    # Seaborn theme - clean publication style
    sns.set_theme(
        style="whitegrid",         # Clean background with subtle grid
        palette="viridis",         # Consistent colormap
        color_codes=True,          # Enable seaborn color codes
        rc={
            'axes.spines.left': True,
            'axes.spines.bottom': True,
            'axes.spines.top': True,
            'axes.spines.right': True,
        }
    )
    
    # Disable seaborn's despine for our custom spine control
    sns.set_style("whitegrid", {"axes.spines.right": True, "axes.spines.top": True})


def apply_publication_formatting(ax, title=None, xlabel=None, ylabel=None, 
                                grid=False, legend_loc='best', tight_layout=True):
    """
    Apply consistent publication-quality formatting to individual axes.
    
    Args:
        ax: matplotlib axes object
        title: plot title (optional)
        xlabel: x-axis label (optional)
        ylabel: y-axis label (optional)
        grid: whether to show grid (default: False)
        legend_loc: legend location (default: 'best')
        tight_layout: whether to apply tight layout (default: True)
    """
    if title:
        ax.set_title(title, weight='bold', pad=15)
    if xlabel:
        ax.set_xlabel(xlabel, weight='bold')
    if ylabel:
        ax.set_ylabel(ylabel, weight='bold')
    
    # Grid control
    ax.grid(grid, alpha=0.3)
    
    # Ensure all spines are visible and properly styled
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_edgecolor('black')
    
    # Format legend if present
    if ax.get_legend():
        ax.legend(loc=legend_loc, fancybox=True, shadow=True, framealpha=0.9)
    
    # Ensure ticks are properly formatted
    ax.tick_params(which='both', direction='in', top=True, right=True)
    
    if tight_layout:
        plt.tight_layout()


def setup_colorbar(mappable, ax, label=None, shrink=0.8, aspect=20):
    """
    Create a consistently formatted colorbar.
    
    Args:
        mappable: the plot object to create colorbar for
        ax: axes object
        label: colorbar label (optional)
        shrink: colorbar size factor
        aspect: colorbar aspect ratio
    """
    cbar = plt.colorbar(mappable, ax=ax, shrink=shrink, aspect=aspect)
    if label:
        cbar.set_label(label, rotation=270, labelpad=20, weight='bold')
    cbar.ax.tick_params(labelsize=10)
    return cbar
