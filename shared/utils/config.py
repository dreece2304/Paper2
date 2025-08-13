"""
Global configuration constants shared across all figure and analysis notebooks.
"""

from matplotlib import cm
import seaborn as sns

# --- Organics: ordered for all figures ---
organics = ['EG', 'CB', 'BTY', 'THB', 'MPD', 'DHB']

# --- Solvents (exact names from data, ordered logically) ---
solvent_order = [
    '0.01 M HCl',
    '0.1 M KOH',
    'Water',
    'Ethanol',
    'Acetone',
    'Chloroform',
    'Toluene'
]

# --- Inorganics used in summary / axis titles ---
inorganics = ['Al', 'Zn']  # Based on TMA and DEZ precursors

# For heatmap
cmap_choice = cm.viridis  # actual matplotlib colormap

# For barplot
bar_palette_solvents = sns.color_palette("viridis", n_colors=len(solvent_order))
bar_palette_organics = sns.color_palette("mako", n_colors=len(organics))

# --- Color mapping if needed for UV/as-deposited variants ---
colors = {
    ('Al', False): cmap_choice(0.2),
    ('Al', True):  cmap_choice(0.5),
    ('Zn', False): cmap_choice(0.8),
    ('Zn', True):  cmap_choice(0.95),
}

# --- Figure sizing and scaling ---
# RSC Journal of Materials Chemistry A specifications
fig_width_cm = 17.1  # RSC double-column maximum width
fig_width_single_column_cm = 8.3  # RSC single-column width
fig_height_max_cm = 23.3  # RSC maximum height
cm2in = 1 / 2.54

# RSC-compliant figure dimensions
rsc_single_column_width_cm = 8.3
rsc_double_column_width_cm = 17.1
rsc_max_height_cm = 23.3

# --- For heatmaps and capped colorbar ---
vmin = 0
vmax = 1.5

# --- Aspect ratios ---
aspect_ratio_standard = 4 / 3
aspect_ratio_tall = 2 / 3
aspect_ratio_square = 1

viridis = cm.get_cmap("viridis")

color_asdeposited = viridis(0.2)
color_uvtreated = viridis(0.8)
