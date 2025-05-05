import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import re

# Setup
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False

# Load file
df = pd.read_excel("06_XPS_Analysis/data/raw/Hi_res/BTYWater.xlsx")

# Extract columns
x = df['B.E.']
raw = df['raw C 1s']
background = df['Background']
envelope = df['Envelope'] - background  # subtract background

# Detect fit columns
fit_cols = [col for col in df.columns if re.match(r'^fit\d+$', col)]

# Plotting
plt.figure(figsize=(6, 4))

# Raw data as crosses (baseline-corrected)
plt.plot(x, raw - background, 'x', color='black', markersize=3, label='Raw')

# Envelope as line (baseline-corrected)
plt.plot(x, envelope, '-', color='black', linewidth=1, label='Envelope')

# Plot fits (baseline-subtracted and filled)
fit_colors = ['#857bbe', '#4e9ad4', '#89c79c', '#d8b26e', '#c26666']
for i, col in enumerate(fit_cols):
    y = df[col] - background
    plt.fill_between(x, y, alpha=0.5, color=fit_colors[i % len(fit_colors)], label=f'Fit {i+1}')

plt.xlabel("Binding Energy (eV)")
plt.ylabel("Intensity (a.u.)")
plt.title("C 1s – Water Exposed (Background-Subtracted)")
plt.gca().invert_xaxis()
plt.legend(fontsize=8)
plt.tight_layout()
plt.show()
