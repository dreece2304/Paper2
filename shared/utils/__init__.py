# shared/utils/__init__.py

# Import existing utilities
from .plot_styles import set_plot_style
from .helpers import (
    ensure_dir, save_figure, cm_to_in,
    get_figure_size, create_figure
)
from .config import *

# Import XPS-specific utilities
from .xps_utils import (
    validate_xps_data,
    background_subtract_normalize,
    get_xps_colors,
    calculate_spectral_metrics,
    export_spectral_data
)

__all__ = [
    # Existing utilities
    'set_plot_style',
    'ensure_dir',
    'save_figure',
    'cm_to_in',
    'get_figure_size',
    'create_figure',
    # XPS utilities
    'validate_xps_data',
    'background_subtract_normalize',
    'get_xps_colors',
    'calculate_spectral_metrics',
    'export_spectral_data'
]