import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import re
import seaborn as sns
from matplotlib import cm

# === Custom Publication-Ready Plot Style ===
def set_plot_style():
    mpl.rcParams.update({
        # Fonts
        'font.family': 'sans-serif',
        'font.sans-serif': ['Verdana'],
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,

        # Lines
        'lines.linewidth': 1.5,

        # Axes
        'axes.linewidth': 3,
        'axes.edgecolor': 'black',

        # Ticks
        'xtick.top': True,
        'xtick.bottom': True,
        'ytick.left': True,
        'ytick.right': True,
        'xtick.direction': 'in',
        'ytick.direction': 'in',

        # Grid
        'axes.grid': False,
        'grid.color': 'grey',
        'grid.alpha': 0.5,

        # Legend
        'legend.frameon': False,
        'legend.fontsize': 10,

        # Colors
        'image.cmap': 'viridis',

        # Figure output
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'figure.autolayout': False,
    })
    sns.set_theme(style="white", palette="viridis")

set_plot_style()

# === Data Paths and Parameters ===
base_path = "06_XPS_Analysis/analysis"
parquet_files = [
    ("As Deposited", f"{base_path}/BTY.AsDeposited.parquet"),
    ("Water Exposed", f"{base_path}/BTY.Water.parquet"),
    ("Water Exposed UV", f"{base_path}/BTY.UV_Water.parquet")
]

regions = ["C 1s", "O 1s", "Al 2p"]
fit_colors = [cm.viridis(x) for x in [0.2, 0.4, 0.6, 0.7, 0.85]]
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
fig, axes = plt.subplots(1, 3, figsize=(13, 5), dpi=300)

for idx, region in enumerate(regions):
    ax = axes[idx]

    for sheet, offset, label in zip(sheets, vertical_offsets, exposure_labels):
        df = pd.read_excel(excel_path, sheet_name=sheet)
        region_df = df[df['Region'] == region].copy()

        if region_df.empty:
            continue

        x = region_df['B.E.']
        bg = region_df['Background'] if 'Background' in region_df else 0

        # Subtract background
        region_df['raw'] -= bg
        region_df['Envelope'] -= bg
        fits = detect_fit_columns(region_df)
        for fit in fits:
            region_df[fit] -= bg

        # Normalize to max envelope across this exposure
        max_val = region_df[['raw', 'Envelope'] + fits].max().max()
        region_df[['raw', 'Envelope'] + fits] /= max_val

        # Plot raw data
        ax.plot(x, region_df['raw'] + offset, 'x', color='black', markersize=3, alpha=0.4)

        # Plot envelope
        ax.plot(x, region_df['Envelope'] + offset, '-', lw=1, color='black')

        # Plot filled fits above offset
        for j, fit in enumerate(fits):
            y = region_df[fit] + offset
            ax.fill_between(x, offset, y, alpha=0.6, color=fit_colors[j % len(fit_colors)], clip_on=True)

        # Exposure annotation
        ax.text(0.02, offset + 0.05, label, fontsize=8,
                va='bottom', ha='left', transform=ax.get_yaxis_transform())

    # Axes formatting
    ax.set_xlabel('Binding Energy (eV)')
    if idx == 0:
        ax.set_ylabel('Intensity (normalized, offset)')
    ax.set_title(region)
    ax.invert_xaxis()
    ax.set_xlim(xlims[region])
    ax.set_ylim(-0.2, vertical_offsets[-1] + 1.3)
    ax.set_yticklabels([])  # Remove y-axis tick labels

    # Ticks and spines
    ax.minorticks_on()
    ax.tick_params(axis='x', which='both', top=True, bottom=True, direction='in')
    ax.tick_params(axis='y', which='both', left=True, right=True, direction='in')
    for spine in ax.spines.values():
        spine.set_linewidth(3)
        spine.set_color('black')

# === Final Export ===
plt.tight_layout()
plt.savefig("THB_XPS_Final_Publication.pdf", bbox_inches='tight')
plt.savefig("THB_XPS_Final_Publication.png", bbox_inches='tight')
plt.show()