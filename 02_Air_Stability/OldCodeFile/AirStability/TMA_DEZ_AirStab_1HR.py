import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

############################################
# Configuration
############################################
# Define the organics and their UV counterparts
organics = ['MPD', 'EG', 'THB', 'BTY', 'DHB', 'CB']
organics_uv = [f"{organic} UV" for organic in organics]

# File paths for TMA and DEZ data
filename_tma = 'alucone.xlsx'
filename_dez = 'zincone.xlsx'

# Directory to save figures
output_dir = 'organic_figures'
os.makedirs(output_dir, exist_ok=True)

# Figure layout
rows = 2
cols = 3
fig_width_inches = 10
fig_height_inches = 6

# Plot style: TMA = blue, DEZ = red
# no UV = circle, UV = triangle
color_tma = 'blue'
color_dez = 'red'
marker_no_uv = 'o'
marker_uv = '^'

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 12
mpl.rcParams['axes.linewidth'] = 1.5

############################################
# Functions
############################################

def load_data(filename, organics, organics_uv):
    """Load data from an Excel file and return series lists for organics and organics UV without filtering."""
    df = pd.read_excel(filename)
    columns = df.columns.tolist()

    # Identify column pairs
    column_pairs = []
    for i in range(0, len(columns), 2):
        if i + 1 < len(columns):
            column_pairs.append((columns[i], columns[i+1]))

    organic_series = []
    organicUV_series = []

    # Populate lists
    for x_col, y_col in column_pairs:
        # Here we do no normalization or filtering.
        s = {'x': df[x_col], 'y': df[y_col], 'label': y_col}
        if y_col in organics:
            organic_series.append(s)
        elif y_col in organics_uv:
            organicUV_series.append(s)
    return organic_series, organicUV_series

def find_series(series_list, label):
    return next((s for s in series_list if s['label'] == label), None)

def setup_axes(ax):
    # Basic axes styling
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
        spine.set_color('black')

    ax.tick_params(axis='both', which='major', labelsize=10, direction='in', length=6, width=1.5)
    ax.tick_params(axis='both', which='minor', labelsize=8, direction='in', length=3, width=1.2)

    # Optionally set tick locators if desired:
    # ax.xaxis.set_major_locator(MultipleLocator(10))
    # ax.xaxis.set_minor_locator(MultipleLocator(5))
    # ax.yaxis.set_major_locator(MultipleLocator(0.25))
    # ax.yaxis.set_minor_locator(AutoMinorLocator(4))

############################################
# Main Execution
############################################

# Load TMA and DEZ data
organic_series_tma, organicUV_series_tma = load_data(filename_tma, organics, organics_uv)
organic_series_dez, organicUV_series_dez = load_data(filename_dez, organics, organics_uv)

# Create figure
fig, axs = plt.subplots(rows, cols, figsize=(fig_width_inches, fig_height_inches))
axs = axs.ravel()

# We'll collect handles and labels for legend
legend_handles = []
legend_labels = []

# We'll define 4 conditions we want to plot:
# 1) TMA no UV (as-deposited)
# 2) TMA UV
# 3) DEZ no UV (as-deposited)
# 4) DEZ UV
# We will define their labeling once, and store handles from the first subplot.

condition_definitions = [
    ('TMA', False, color_tma, marker_no_uv, 'TMA As-Deposited'),
    ('TMA', True,  color_tma, marker_uv,    'TMA UV'),
    ('DEZ', False, color_dez, marker_no_uv, 'DEZ As-Deposited'),
    ('DEZ', True,  color_dez, marker_uv,    'DEZ UV')
]

for i, org in enumerate(organics):
    ax = axs[i]
    ax.set_title(org, fontsize=14, fontweight='bold')
    ax.set_xlabel('Time (minutes)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Measurement', fontsize=12, fontweight='bold')

    # Find corresponding series for TMA and DEZ, UV and no UV
    # no UV: label = org
    # UV: label = org + ' UV'
    org_label = org
    org_uv_label = f"{org} UV"

    tma_org = find_series(organic_series_tma, org_label)
    tma_org_uv = find_series(organicUV_series_tma, org_uv_label)
    dez_org = find_series(organic_series_dez, org_label)
    dez_org_uv = find_series(organicUV_series_dez, org_uv_label)

    # Plot each condition if data is available
    # We'll store handles from the first subplot for the legend
    plotted_on_this_ax = {}

    for (material, is_uv, color, marker, legend_label) in condition_definitions:
        if material == 'TMA':
            data = tma_org_uv if is_uv else tma_org
        else:
            data = dez_org_uv if is_uv else dez_org

        if data is not None:
            sc = ax.scatter(data['x'], data['y'], color=color, marker=marker, s=20, alpha=0.7)
            # Store handle and label only if not already stored (to avoid duplicates in legend)
            if i == 0:  # On first subplot, we record legend handles
                legend_handles.append(sc)
                legend_labels.append(legend_label)

    setup_axes(ax)

plt.tight_layout()

# Save main figure without legend
main_figure_name = "combined_2x3_all_data.png"
plt.savefig(os.path.join(output_dir, main_figure_name), dpi=300)
plt.close(fig)

# Create a separate figure for the legend
fig_legend = plt.figure(figsize=(3, 2))
fig_legend.legend(legend_handles, legend_labels, loc='center', frameon=False)
plt.axis('off')

legend_figure_name = "legend_only.png"
plt.savefig(os.path.join(output_dir, legend_figure_name), dpi=300, bbox_inches='tight', pad_inches=0)
plt.close(fig_legend)

print("Main figure and separate legend figure created successfully.")
