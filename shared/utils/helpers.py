import os

def ensure_dir(path):
    """
    Create a directory if it doesn't exist yet.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def save_figure(fig, filename, folder="../figures/final/", formats=("png", "pdf")):
    """
    Save a Matplotlib figure in multiple formats.
    Args:
        fig: Matplotlib figure object
        filename: Filename without extension
        folder: Target save folder
        formats: Tuple of formats to save (e.g., ("png", "pdf"))
    """
    ensure_dir(folder)
    for fmt in formats:
        fig.savefig(os.path.join(folder, f"{filename}.{fmt}"), bbox_inches='tight')
    print(f"Saved figure: {filename} in {formats}")
