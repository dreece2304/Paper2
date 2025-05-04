import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("../data/raw/XPS/BTY_AD.csv")

# Setup figure
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Common settings
plt.rcParams.update({'font.size': 12})
colors_o1s = ['tab:blue', 'tab:green', 'tab:red']
colors_c1s = ['tab:blue', 'tab:green', 'tab:red', 'tab:orange', 'tab:purple']
color_al2p = 'tab:blue'

# --- O1s Spectrum ---
ax = axes[0]
ax.plot(df['B.E.'], df['raw O1s'], color='black', label='Raw')
for i, col in enumerate(['fit1', 'fit2', 'fit3']):
    ax.fill_between(df['B.E.'], df[col], alpha=0.5, color=colors_o1s[i], label=f'Fit {i+1}')
ax.plot(df['B.E.'], df['Envelope'], linestyle='--', color='black', label='Envelope')
ax.plot(df['B.E.'], df['Background'], linestyle=':', color='gray', label='Background')
ax.set_title("O 1s")
ax.set_xlabel("Binding Energy (eV)")
ax.set_ylabel("Intensity (a.u.)")
ax.invert_xaxis()
ax.legend(fontsize=9)

# --- C1s Spectrum ---
ax = axes[1]
ax.plot(df['B.E..1'], df['raw C1s'], color='black', label='Raw')
for i, col in enumerate(['fit1.1', 'fit2.1', 'fit3.1', 'fit4', 'fit5']):
    ax.fill_between(df['B.E..1'], df[col], alpha=0.5, color=colors_c1s[i], label=f'Fit {i+1}')
ax.plot(df['B.E..1'], df['Envelope.1'], linestyle='--', color='black', label='Envelope')
ax.plot(df['B.E..1'], df['Background.1'], linestyle=':', color='gray', label='Background')
ax.set_title("C 1s")
ax.set_xlabel("Binding Energy (eV)")
ax.invert_xaxis()
ax.legend(fontsize=9)

# --- Al 2p Spectrum ---
ax = axes[2]
ax.plot(df['B.E..2'], df['raw Al2p'], color='black', label='Raw')
ax.fill_between(df['B.E..2'], df['fit1.2'], alpha=0.5, color=color_al2p, label='Fit 1')
ax.plot(df['B.E..2'], df['Envelope.2'], linestyle='--', color='black', label='Envelope')
ax.plot(df['B.E..2'], df['Background.2'], linestyle=':', color='gray', label='Background')
ax.set_title("Al 2p")
ax.set_xlabel("Binding Energy (eV)")
ax.invert_xaxis()
ax.legend(fontsize=9)

# Layout
plt.tight_layout()
plt.savefig("BTY_AD_XPS_Figure_Paper2.png", dpi=600)
plt.show()
