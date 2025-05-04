import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

############################################
# Configuration
############################################
organics = ['MPD', 'EG', 'THB', 'BTY', 'DHB', 'CB']
organics_uv = [f"{organic} UV" for organic in organics]

# File paths
filename_alucone = 'alucone.xlsx'
filename_zincone = 'zincone.xlsx'

# Plotting parameters
time_limit = 60
sampling_rate = 10

# Directory to save figures
output_dir = 'organic_figures'
os.makedirs(output_dir, exist_ok=True)

# Global figure settings for journal
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 12
mpl.rcParams['axes.linewidth'] = 1.5

fig_width_inches = 7
fig_height_inches = 7
rows = 3
cols = 3
num_plots = 6  # number of organics to plot (assuming 6)

############################################
# Functions
############################################
def preprocess_series(series, sampling_rate, time_limit):
    # Normalize so first value is 1
    first_value = series['y'].iloc[0]
    if first_value != 0:
        series['y'] = series['y'] / first_value

    # Filter by time limit
    mask = series['x'] <= time_limit
    series['x'] = series['x'][mask]
    series['y'] = series['y'][mask]

    # Downsample
    series['x'] = series['x'].iloc[::sampling_rate].reset_index(drop=True)
    series['y'] = series['y'].iloc[::sampling_rate].reset_index(drop=True)
    return series

def load_and_process_data(filename, organics, organics_uv, time_limit=60, sampling_rate=10):
    df = pd.read_excel(filename)
    columns = df.columns.tolist()

    # Identify column pairs
    column_pairs = []
    for i in range(0, len(columns), 2):
        if i + 1 < len(columns):
            column_pairs.append((columns[i], columns[i+1]))

    organic_series = []
    organicUV_series = []

    # Separate organics and organics UV
    for x_col, y_col in column_pairs:
        if y_col in organics:
            s = {'x': df[x_col], 'y': df[y_col], 'label': y_col}
            s = preprocess_series(s, sampling_rate, time_limit)
            organic_series.append(s)
        elif y_col in organics_uv:
            s = {'x': df[x_col], 'y': df[y_col], 'label': y_col}
            s = preprocess_series(s, sampling_rate, time_limit)
            organicUV_series.append(s)

    return organic_series, organicUV_series

def determine_limits(*series_lists):
    # Combine all for axis scaling
    all_x = pd.concat([s['x'] for slist in series_lists for s in slist])
    all_y = pd.concat([s['y'] for slist in series_lists for s in slist])
    x_min = all_x.min()
    x_max = all_x.max()
    y_min = 0
    y_max = all_y.max()
    return x_min, x_max, y_min, y_max

def setup_axes(ax, x_min, x_max, y_min, y_max):
    # Set limits
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max*1.05)

    # Spines
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
        spine.set_color('black')

    # Ticks
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(0.25))
    ax.yaxis.set_minor_locator(AutoMinorLocator(4))

    ax.tick_params(axis='both', which='major', labelsize=10, direction='in', length=6, width=1.5)
    ax.tick_params(axis='both', which='minor', labelsize=8, direction='in', length=3, width=1.2)

def plot_3x3_matrix_by_dataset(organics, organic_series, organicUV_series, color_as_deposited, color_uv_treated, x_min, x_max, y_min, y_max, figure_name):
    fig, axs = plt.subplots(rows, cols, figsize=(fig_width_inches, fig_height_inches))
    axs = axs.ravel()
    plt.subplots_adjust(wspace=0.3, hspace=0.3)

    index = 0
    for org in organics[:num_plots]:
        org_uv_label = f"{org} UV"
        organic = next((s for s in organic_series if s['label'] == org), None)
        organicUV = next((s for s in organicUV_series if s['label'] == org_uv_label), None)

        if organic is None or organicUV is None:
            continue

        ax = axs[index]
        index += 1

        ax.plot(organic['x'], organic['y'], color=color_as_deposited, linestyle='solid', linewidth=2)
        ax.plot(organicUV['x'], organicUV['y'], color=color_uv_treated, linestyle='dashed', linewidth=2)

        ax.set_xlabel('Time (minutes)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Normalized', fontsize=12, fontweight='bold')
        ax.set_title(f"{organic['label']}", fontsize=14, fontweight='bold')

        setup_axes(ax, x_min, x_max, y_min, y_max)

    # Turn off unused subplots
    for remaining_idx in range(index, rows*cols):
        axs[remaining_idx].axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, figure_name), dpi=300)
    plt.close(fig)

def plot_3x3_matrix_compare_materials(organics,
                                      organic_series_alucone, organicUV_series_alucone,
                                      organic_series_zincone, organicUV_series_zincone,
                                      compare_uv=False, x_min=None, x_max=None, y_min=None, y_max=None):
    # compare_uv=False means we compare organics only
    # compare_uv=True means we compare organic UV only

    fig, axs = plt.subplots(rows, cols, figsize=(fig_width_inches, fig_height_inches))
    axs = axs.ravel()
    plt.subplots_adjust(wspace=0.3, hspace=0.3)

    # Colors for alucone vs zincone comparison
    # Using a different colormap or distinct colors to differentiate materials
    color_alucone = mpl.colors.to_rgb("tab:blue")
    color_zincone = mpl.colors.to_rgb("tab:orange")

    index = 0
    for org in organics[:num_plots]:
        if compare_uv:
            # UV version
            label = f"{org} UV"
            alu = next((s for s in organicUV_series_alucone if s['label'] == label), None)
            zin = next((s for s in organicUV_series_zincone if s['label'] == label), None)
        else:
            # Non-UV
            label = org
            alu = next((s for s in organic_series_alucone if s['label'] == label), None)
            zin = next((s for s in organic_series_zincone if s['label'] == label), None)

        if alu is None or zin is None:
            continue

        ax = axs[index]
        index += 1

        # Plot alucone line
        ax.plot(alu['x'], alu['y'], color=color_alucone, linestyle='solid', linewidth=2, label='Alucone')
        # Plot zincone line
        ax.plot(zin['x'], zin['y'], color=color_zincone, linestyle='dashed', linewidth=2, label='Zincone')

        ax.set_xlabel('Time (minutes)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Normalized', fontsize=12, fontweight='bold')
        ax.set_title(f"{label}", fontsize=14, fontweight='bold')

        setup_axes(ax, x_min, x_max, y_min, y_max)

        # Optional: Add a legend to each subplot or just the first one
        # Here we add to each for clarity
        ax.legend(fontsize=10)

    # Turn off unused subplots
    for remaining_idx in range(index, rows*cols):
        axs[remaining_idx].axis('off')

    plt.tight_layout()
    # Determine figure name based on whether we are comparing UV or not
    if compare_uv:
        fig_name = "comparison_organicsUV_alucone_zincone.png"
    else:
        fig_name = "comparison_organics_alucone_zincone.png"

    plt.savefig(os.path.join(output_dir, fig_name), dpi=300)
    plt.close(fig)

############################################
# Main Execution
############################################
# Load and process data for alucone
organic_series_alucone, organicUV_series_alucone = load_and_process_data(filename_alucone, organics, organics_uv, time_limit, sampling_rate)

# Load and process data for zincone
organic_series_zincone, organicUV_series_zincone = load_and_process_data(filename_zincone, organics, organics_uv, time_limit, sampling_rate)

# Determine limits from all data
x_min, x_max, y_min, y_max = determine_limits(organic_series_alucone, organicUV_series_alucone,
                                              organic_series_zincone, organicUV_series_zincone)

# Colors for as deposited and UV treated (from viridis)
cmap = plt.get_cmap('viridis')
color_as_deposited = cmap(0.3)
color_uv_treated = cmap(0.7)

############################################
# Plot Figures
############################################
# Figure 1: Alucone only (organics + their UV)
plot_3x3_matrix_by_dataset(
    organics, organic_series_alucone, organicUV_series_alucone,
    color_as_deposited, color_uv_treated, x_min, x_max, y_min, y_max,
    figure_name="all_organics_3x3_alucone.png"
)

# Figure 2: Zincone only (organics + their UV)
plot_3x3_matrix_by_dataset(
    organics, organic_series_zincone, organicUV_series_zincone,
    color_as_deposited, color_uv_treated, x_min, x_max, y_min, y_max,
    figure_name="all_organics_3x3_zincone.png"
)

# Figure 3: Compare Alucone vs Zincone for organics only
plot_3x3_matrix_compare_materials(
    organics,
    organic_series_alucone, organicUV_series_alucone,
    organic_series_zincone, organicUV_series_zincone,
    compare_uv=False,
    x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max
)

# Figure 4: Compare Alucone vs Zincone for organics UV only
plot_3x3_matrix_compare_materials(
    organics,
    organic_series_alucone, organicUV_series_alucone,
    organic_series_zincone, organicUV_series_zincone,
    compare_uv=True,
    x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max
)

print("All four figures created successfully.")
