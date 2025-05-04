import matplotlib.pyplot as plt
import seaborn as sns

def set_plot_style():
    """
    Set the global plot style for all figures to match publication standards.
    """

    # Update matplotlib defaults
    plt.rcParams.update({
        # Fonts
        'font.family': 'sans-serif',
        'font.sans-serif': ['Verdana'],
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,

        # Line styles
        'lines.linewidth': 1.5,  # For all line plots

        # Axis spine styling
        'axes.linewidth': 3,        # Thick black frame
        'axes.edgecolor': 'black',

        # Tick markers on all sides
        'xtick.top': True,
        'xtick.bottom': True,
        'ytick.left': True,
        'ytick.right': True,
        'xtick.direction': 'in',
        'ytick.direction': 'in',

        # Grid — off by default for line plots
        'axes.grid': False,

        # Color map default
        'image.cmap': 'viridis',

        # Legend
        'legend.frameon': False,
        'legend.fontsize': 10,

        # Resolution
        'figure.dpi': 300,
        'savefig.dpi': 300,
    })

    # Seaborn theme baseline
    sns.set_theme(style="white", palette="viridis")
