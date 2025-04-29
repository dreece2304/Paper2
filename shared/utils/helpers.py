import os
import matplotlib.pyplot as plt


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_figure(fig, filename, folder="../figures/final/", formats=("png", "pdf")):
    ensure_dir(folder)
    for fmt in formats:
        fig.savefig(os.path.join(folder, f"{filename}.{fmt}"), bbox_inches='tight')
    print(f"Saved {filename} as {formats}")


def cm_to_in(cm):
    return cm / 2.54


def get_figure_size(width_cm=18, aspect_ratio=4 / 3):
    """
    Calculate figure size (width, height) in inches given width in cm and aspect ratio.
    """
    width_in = cm_to_in(width_cm)
    height_in = width_in / aspect_ratio
    return (width_in, height_in)


def create_figure(rows=1, cols=1, width_cm=18, aspect_ratio=4 / 3, sharex=False, sharey=False):
    """
    Create a figure and axes with standard manuscript sizing.

    Args:
        rows (int): number of subplot rows
        cols (int): number of subplot columns
        width_cm (float): desired figure width in cm
        aspect_ratio (float): width/height ratio
        sharex (bool): share x-axis
        sharey (bool): share y-axis

    Returns:
        fig, axes
    """
    figsize = get_figure_size(width_cm, aspect_ratio)
    fig, axes = plt.subplots(rows, cols, figsize=figsize, sharex=sharex, sharey=sharey)

    # Flatten axes if more than 1 panel
    if rows * cols > 1:
        axes = axes.flatten()

    return fig, axes
