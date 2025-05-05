import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import re

# === Setup ===
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False

# === File Paths ===
base_path = "06_XPS_Analysis/analysis"
parquet_files = [
    ("As Deposited", f"{base_path}/AsDeposited.parquet"),
    ("Water Exposed", f"{base_path}/Water.parquet"),
    ("Water Exposed UV", f"{base_path}/UV_Water.parquet")
]
exposure_labels = [label for label, _ in parquet_files]
region_order = ["C 1s", "O 1s", "Al 2p"]
fit_colors = ['#857bbe', '#4e9ad4', '#89c79c', '#d8b26e', '#c26666']

# === Helper ===
def detect_fit_columns(df):
    return [
        col for col in df.columns
        if re.match(r'^fit\d*(\.\d+)?$', col)
        and df[col].notna().any()
        and df[col].nunique(dropna=True) > 1
        and (df[col].max() - df[col].min()) > 1e-3
    ]

# === Plotting ===
fig, axes = plt.subplots(3, 3, figsize=(10, 7), sharex=False, sharey=False)

for row, (label, file) in enumerate(parquet_files):
    df = pd.read_parquet(file)
    for col, region in enumerate(region_order):
        ax = axes[row, col]
        region_df = df[df['Region'] == region]
        x = region_df['B.E.']
        bg = region_df['Background'] if 'Background' in region_df else 0

        # Raw data (baseline-subtracted)
        if 'raw' in region_df.columns:
            ax.plot(x, region_df['raw'] - bg, 'x', color='black', markersize=3)

        # Envelope (baseline-subtracted)
        if 'Envelope' in region_df.columns:
            ax.plot(x, region_df['Envelope'] - bg, '-', lw=1, color='black')

        # Fits (baseline-subtracted)
        fits = detect_fit_columns(region_df)
        for j, colname in enumerate(fits):
            y = region_df[colname] - bg
            ax.fill_between(x, y, alpha=0.5, color=fit_colors[j % len(fit_colors)], clip_on=True)

        ax.invert_xaxis()

        # Titles & labels
        if row == 0:
            ax.set_title(region)
        if col == 0:
            ax.set_ylabel(label, fontsize=10)
        else:
            ax.set_ylabel("")

        if row == 2:
            ax.set_xlabel("Binding Energy (eV)")
        else:
            ax.set_xticklabels([])

        if col == 1:
            ax.set_ylabel("Intensity (a.u.)")
        else:
            ax.set_yticklabels([])

# === Export ===
plt.tight_layout()
plt.savefig("XPS_3x3_Composite.pdf", dpi=600, bbox_inches='tight')
plt.savefig("XPS_3x3_Composite.png", dpi=600, bbox_inches='tight')
plt.savefig("XPS_3x3_Composite.svg", bbox_inches='tight')
plt.show()
print("✅ Saved: PDF, PNG, and SVG")
