import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import re
import seaborn as sns
from matplotlib import cm
import os
from matplotlib.ticker import MultipleLocator

# === Enhanced Publication-Ready Plot Style ===
def set_plot_style():
    mpl.rcParams.update({
        # Fonts - using Arial for best readability in publications
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'Verdana'],
        'font.size': 11,
        'axes.labelsize': 12,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,

        # Lines
        'lines.linewidth': 1.8,

        # Axes
        'axes.linewidth': 1.5,
        'axes.edgecolor': 'black',
        'axes.labelpad': 8,  # More space between axis and label

        # Ticks
        'xtick.top': True,
        'xtick.bottom': True,
        'ytick.left': True,
        'ytick.right': True,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.major.width': 1.5,
        'ytick.major.width': 1.5,
        'xtick.minor.width': 1.0,
        'ytick.minor.width': 1.0,
        'xtick.major.size': 5,
        'ytick.major.size': 5,
        'xtick.minor.size': 3,
        'ytick.minor.size': 3,

        # Grid
        'axes.grid': False,

        # Legend
        'legend.frameon': False,
        'legend.fontsize': 11,

        # Colors
        'image.cmap': 'viridis',

        # Figure output
        'figure.dpi': 300,
        'savefig.dpi': 600,
        'savefig.bbox': 'tight',
        'savefig.transparent': True,
    })
    sns.set_theme(style="ticks", palette="viridis")

set_plot_style()

# === Data Paths and Parameters ===
base_path = "06_XPS_Analysis/analysis"
excel_path = os.path.join(base_path, "THB_final.xlsx")

# Define sheets and labels for clarity
sheets = ["AsDeposited", "Water", "UV_Water"]
exposure_labels = ["As Deposited", "Water Exposed", "UV + Water"]

regions = ["C 1s", "O 1s", "Al 2p"]
# Enhanced color palette - more distinct colors for better contrast
fit_colors = [cm.viridis(x) for x in [0.15, 0.35, 0.55, 0.75, 0.9]]
vertical_offsets = [0, 1.5, 3]

# Explicit x-limits for clarity
xlims = {
    "C 1s": (294, 282),
    "O 1s": (536, 528),
    "Al 2p": (79, 70)
}

# === Helper ===
def detect_fit_columns(df):
    return [col for col in df.columns if re.match(r'^fit\d*(\.\d+)?$', col)]

# === Plotting ===
fig, axes = plt.subplots(1, 3, figsize=(14, 5.5), dpi=300, constrained_layout=True)

for idx, region in enumerate(regions):
    ax = axes[idx]
    print(f"Processing region: {region}")

    for sheet, offset, label in zip(sheets, vertical_offsets, exposure_labels):
        print(f"  Processing sheet: {sheet} for {label}")
        
        # Read directly from Excel 
        df = pd.read_excel(excel_path, sheet_name=sheet)
        region_df = df[df['Region'] == region].copy()

        if region_df.empty:
            print(f"  No data for {region} in {sheet}")
            continue
        
        # Sort by binding energy for consistent plotting
        region_df = region_df.sort_values('B.E.')
        print(f"  Found {len(region_df)} data points")

        x = region_df['B.E.']
        
        # SWAP Background and Envelope columns as needed
        bg = region_df['Envelope']  # Using Envelope as the background
        
        # Subtract background
        region_df['raw'] -= bg
        region_df['Background'] -= bg  # This is now treated as the envelope
        fits = detect_fit_columns(region_df)
        print(f"  Using fit columns: {fits}")
        
        for fit in fits:
            region_df[fit] -= bg

        # Normalize to max envelope across this exposure
        max_val = region_df[['raw', 'Background'] + fits].max().max()
        if max_val > 0:  # Prevent division by zero
            region_df[['raw', 'Background'] + fits] /= max_val

        # Plot raw data with enhanced markers
        ax.plot(x, region_df['raw'] + offset, '.', color='black', 
               markersize=2.5, alpha=0.5, markeredgewidth=0)

        # Plot envelope with enhanced linewidth
        ax.plot(x, region_df['Background'] + offset, '-', lw=1.8, color='black')

        # Plot filled fits above offset with enhanced colors
        for j, fit in enumerate(fits):
            y = region_df[fit] + offset
            ax.fill_between(x, offset, y, alpha=0.7, 
                           color=fit_colors[j % len(fit_colors)], 
                           clip_on=True, linewidth=0)

        # Exposure annotation with enhanced formatting
        ax.text(0.03, offset + 0.1, label, fontsize=11,
               va='bottom', ha='left', transform=ax.get_yaxis_transform(),
               bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

    # Enhanced axes formatting
    ax.set_xlabel('Binding Energy (eV)', weight='bold')
    if idx == 0:
        ax.set_ylabel('Intensity (normalized, offset)', weight='bold')
    
    # REMOVED: Title with region formatting
    # ax.set_title(region, fontsize=14, weight='bold', pad=10)
    
    ax.invert_xaxis()
    ax.set_xlim(xlims[region])
    ax.set_ylim(-0.2, vertical_offsets[-1] + 1.4)
    
    # More readable ticks
    ax.set_yticklabels([])  # Remove y-axis tick labels
    ax.xaxis.set_major_locator(MultipleLocator(2))  # Major ticks every 2 eV
    ax.xaxis.set_minor_locator(MultipleLocator(1))  # Minor ticks every 1 eV
    
    # Enhanced ticks and spines
    ax.minorticks_on()
    ax.tick_params(axis='x', which='both', top=True, bottom=True, direction='in')
    ax.tick_params(axis='y', which='both', left=True, right=True, direction='in')
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_color('black')
    


# Panel labels (a, b, c) - placed inside axes in top left
panel_labels = ['a)', 'b)', 'c)']
for i, ax in enumerate(axes):
    # Position text at 0.05, 0.95 in axes coordinates (top left inside)
    ax.text(0.05, 0.95, panel_labels[i], transform=ax.transAxes, 
           fontsize=12, fontweight='bold', va='top', ha='left')

# === Final Export with enhanced resolution ===
output_pdf = os.path.join(base_path, "THB_XPS_Final_Publication.pdf")
output_png = os.path.join(base_path, "THB_XPS_Final_Publication.png")
output_tiff = os.path.join(base_path, "THB_XPS_Final_Publication.tiff")  # TIFF for publication

plt.savefig(output_pdf, dpi=600, bbox_inches='tight')
plt.savefig(output_png, dpi=600, bbox_inches='tight')
plt.savefig(output_tiff, dpi=600, bbox_inches='tight')
plt.show()
print(f"✅ Saved high-resolution plots:")
print(f"  - {output_pdf}")
print(f"  - {output_png}")
print(f"  - {output_tiff}")