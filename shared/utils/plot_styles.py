import matplotlib.pyplot as plt
import seaborn as sns

def set_plot_style():
    """
    Set the global plot style for all figures: font, sizes, line widths, colormaps.
    """
    plt.rcParams.update({
        # Fonts
        'font.family': 'sans-serif',
        'font.sans-serif': ['Verdana'],
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,

        # Lines
        'lines.linewidth': 2,

        # Axes
        'axes.linewidth': 1,
        'axes.spines.top': False,
        'axes.spines.right': False,

        # Grid
        'axes.grid': True,
        'grid.linestyle': '--',
        'grid.linewidth': 0.5,

        # Colormap
        'image.cmap': 'viridis',

        # Legend
        'legend.frameon': False,
        'legend.fontsize': 10,

        # DPI
        'figure.dpi': 300,
        'savefig.dpi': 300,
    })

    sns.set_theme(style="whitegrid", palette="viridis")

# Auto-apply when imported
set_plot_style()
