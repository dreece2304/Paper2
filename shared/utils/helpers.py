import os
import matplotlib.pyplot as plt
from pathlib import Path


def ensure_dir(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def save_figure(fig, filename, folder="../figures/final/", formats=("tiff",), 
               include_pdf=False, include_png=False, include_svg=False, dpi=600):
    """
    Save figure with publication-quality settings, prioritizing TIFF format for LaTeX.
    
    Args:
        fig: matplotlib figure object
        filename: base filename (without extension)
        folder: directory path (can be relative or absolute)
        formats: tuple of file formats to save (default: tiff only)
        include_pdf: also save PDF version (for compatibility/vector graphics)
        include_png: also save PNG version (for web/preview)
        include_svg: also save SVG version (for vector editing)
        dpi: resolution for raster formats (default: 600 for publication quality)
    """
    # Build comprehensive formats list
    format_list = list(formats)
    if include_pdf and "pdf" not in format_list:
        format_list.append("pdf")
    if include_png and "png" not in format_list:
        format_list.append("png")
    if include_svg and "svg" not in format_list:
        format_list.append("svg")
    
    # Convert to absolute path and ensure directory exists
    folder_path = Path(folder).resolve()
    ensure_dir(folder_path)
    
    saved_files = []
    for fmt in format_list:
        filepath = folder_path / f"{filename}.{fmt}"
        
        # Format-specific optimization settings
        save_kwargs = {
            'bbox_inches': 'tight',
            'pad_inches': 0.1,
            'facecolor': 'white',
            'edgecolor': 'none',
        }
        
        if fmt in ['png', 'tiff', 'jpg', 'jpeg']:
            # High-resolution raster formats
            save_kwargs['dpi'] = dpi
            if fmt == 'tiff':
                save_kwargs['pil_kwargs'] = {
                    'compression': 'lzw',  # Lossless compression
                }
            elif fmt == 'png':
                # PNG format - no special optimization parameters needed
                pass
                
        elif fmt == 'pdf':
            # Vector format - publication quality
            save_kwargs.update({
                'dpi': 300,  # Reasonable for vector
                'backend': 'pdf',
                'metadata': {
                    'Title': filename,
                    'Subject': 'Scientific Figure',
                    'Creator': 'Matplotlib/Python Scientific Analysis',
                }
            })
            
        elif fmt == 'svg':
            # Scalable vector graphics
            save_kwargs['format'] = 'svg'
            save_kwargs['dpi'] = 300
        
        # Apply tight layout before saving to ensure optimal spacing
        fig.tight_layout()
        
        try:
            fig.savefig(filepath, **save_kwargs)
            saved_files.append(str(filepath))
            print(f"✓ Saved: {filepath.name}")
        except Exception as e:
            print(f"✗ Failed to save {fmt}: {e}")
    
    print(f"📁 Saved {filename} in {len(saved_files)}/{len(format_list)} format(s) to {folder_path}")
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


def create_figure(rows=1, cols=1, width_cm=18, aspect_ratio=4 / 3, sharex=False, sharey=False,
                 constrained_layout=True, style='publication'):
    """
    Create a figure and axes with standard manuscript sizing and publication formatting.

    Args:
        rows (int): number of subplot rows
        cols (int): number of subplot columns  
        width_cm (float): desired figure width in cm (18cm = standard manuscript width)
        aspect_ratio (float): width/height ratio (4/3 = standard)
        sharex (bool): share x-axis across subplots
        sharey (bool): share y-axis across subplots
        constrained_layout (bool): use matplotlib's constrained layout for better spacing
        style (str): figure style preset ('publication', 'presentation', 'poster')

    Returns:
        fig, axes (or single ax if only one subplot)
    """
    # Adjust sizing based on style
    if style == 'presentation':
        width_cm *= 1.2  # Larger for presentations
        aspect_ratio *= 0.9  # Slightly wider
    elif style == 'poster':
        width_cm *= 1.5  # Much larger for posters
        aspect_ratio *= 0.8  # Wider format
    
    figsize = get_figure_size(width_cm, aspect_ratio)
    
    fig, axes = plt.subplots(
        rows, cols, 
        figsize=figsize, 
        sharex=sharex, 
        sharey=sharey,
        constrained_layout=constrained_layout,
        facecolor='white'
    )

    # Handle single vs multiple subplots
    if rows * cols == 1:
        # Single subplot - return axes directly
        axes = axes if hasattr(axes, 'plot') else axes
    else:
        # Multiple subplots - flatten for easy iteration
        axes = axes.flatten() if rows * cols > 1 else [axes]

    return fig, axes


def create_publication_figure(figsize_cm=(18, 12), nrows=1, ncols=1, **subplot_kw):
    """
    Convenience function to create publication-ready figures with optimal defaults.
    
    Args:
        figsize_cm: (width, height) in centimeters
        nrows, ncols: subplot grid dimensions
        **subplot_kw: additional arguments passed to plt.subplots()
    
    Returns:
        fig, ax (or axes array)
    """
    width_in = figsize_cm[0] / 2.54
    height_in = figsize_cm[1] / 2.54
    
    fig, ax = plt.subplots(
        nrows=nrows, 
        ncols=ncols,
        figsize=(width_in, height_in),
        constrained_layout=True,
        facecolor='white',
        **subplot_kw
    )
    
    return fig, ax
