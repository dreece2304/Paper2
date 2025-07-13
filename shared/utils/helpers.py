import os
import matplotlib.pyplot as plt


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_figure(fig, filename, folder="../figures/final/", formats=("tiff",), 
               include_pdf=False, include_png=False):
    """
    Save figure prioritizing TIFF format for LaTeX integration.
    
    Args:
        fig: matplotlib figure object
        filename: base filename (without extension)
        folder: directory path (can be relative or absolute)
        formats: tuple of file formats to save (default: tiff only)
        include_pdf: also save PDF version (for compatibility)
        include_png: also save PNG version (for web/preview)
    """
    # Build formats list
    format_list = list(formats)
    if include_pdf and "pdf" not in format_list:
        format_list.append("pdf")
    if include_png and "png" not in format_list:
        format_list.append("png")
    
    # Convert to absolute path if relative
    folder_path = os.path.abspath(folder)
    ensure_dir(folder_path)
    
    saved_files = []
    for fmt in format_list:
        filepath = os.path.join(folder_path, f"{filename}.{fmt}")
        
        # Set appropriate DPI and quality for each format
        save_kwargs = {'bbox_inches': 'tight'}
        if fmt in ['png', 'tiff']:
            save_kwargs['dpi'] = 600
        if fmt == 'tiff':
            save_kwargs['pil_kwargs'] = {'compression': 'lzw'}  # Lossless compression
        
        fig.savefig(filepath, **save_kwargs)
        saved_files.append(filepath)
    
    print(f"Saved {filename} in {len(format_list)} format(s) to {folder_path}")
    return saved_files


def save_figure_legacy(fig, filename, folder="../figures/final/", formats=("png", "pdf")):
    """
    Legacy figure saving function for backward compatibility.
    Use save_figure() with include_pdf=True, include_png=True for similar behavior.
    """
    return save_figure(fig, filename, folder, formats)


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
