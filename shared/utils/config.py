"""
Global configuration constants shared across all figure and analysis notebooks.
"""

import matplotlib.pyplot as plt

# --- Organics: Ordered list for panels and plots ---
organics = ['MPD', 'EG', 'THB', 'BTY', 'DHB', 'CB']

# --- Inorganics: General metal labels (used where direct metals are listed) ---
inorganics = ['Al', 'Zn']  # Used for general analysis; actual precursors are TMA and DEZ

solvent_order = [
    'HCl', 'KOH',    # Aqueous acid/base
    'Water',         # Neutral aqueous
    'Ethanol',       # Polar protic
    'Acetone',       # Polar aprotic
    'Chloroform',    # Nonpolar
    'Toluene'        # Nonpolar
]


# --- Color Map Settings: Viridis colormap with assignments per condition ---
cmap = plt.get_cmap('viridis')

# You can adjust these colors as needed (or make conditional color logic in your notebook)
colors = {
    ('Al', False): cmap(0.2),   # Al-based, as-deposited
    ('Al', True):  cmap(0.5),   # Al-based, UV-treated
    ('Zn', False): cmap(0.8),   # Zn-based, as-deposited
    ('Zn', True):  cmap(0.95),  # Zn-based, UV-treated
}

# --- Figure Sizing Constants ---
cm2in = 1 / 2.54                      # Conversion factor from centimeters to inches
full_width_cm = 18                   # Full manuscript figure width (common journal standard)
aspect_ratio_standard = 4 / 3        # Landscape default
aspect_ratio_tall = 2 / 3            # Tall figure layout (e.g. 6-panel)
aspect_ratio_square = 1              # Square grid (e.g. heatmaps)
