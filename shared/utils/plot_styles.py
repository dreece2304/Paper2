import matplotlib.pyplot as plt
import seaborn as sns


def set_plot_style():
    """
    Set the global plot style for all figures: font, sizes, line widths, colormaps.
    """
    # General matplotlib style
    plt.rcParams.update({
        # Fonts
        'font.family': 'sans-serif',
        'font.sans-serif': ['Verdana'],  # use Verdana or a clean sans serif
        'font.size': 10,  # base font size
        'axes.titlesize': 12,  # axes title
        'axes.labelsize': 11,  # axes labels
        'xtick.labelsize': 10,  # x tick labels
        'ytick.labelsize': 10,  # y tick labels

        # Lines
        'lines.linewidth': 2,  # line thickness

        # Axes
        'axes.linewidth': 1,  # thickness of axes borders
        'axes.spines.top': False,  # no top spine
        'axes.spines.right': False,  # no right spine

        # Grid
        'axes.grid': True,
        'grid.linestyle': '--',
        'grid.linewidth': 0.5,

        # Colormap default
        'image.cmap': 'viridis',

        # Legend
        'legend.frameon': False,
        'legend.fontsize': 10,

        # Figure
        'figure.dpi': 300,
        'savefig.dpi': 300,
    })

    # Set Seaborn style
    sns.set_theme(style="whitegrid", palette="viridis")


# Quick call to set the style immediately if imported
set_plot_style()
