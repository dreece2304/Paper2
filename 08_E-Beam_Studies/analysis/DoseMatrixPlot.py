import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os
os.makedirs("figures", exist_ok=True)

# Parameters
square_size = 1.0  # visual units
gap = 1.5  # visual units
pitch = square_size + gap
n_cols = 5
n_rows = 4
dose_start = 200
dose_step = 500
num_doses = n_cols * n_rows

# Dose values
doses = [dose_start + i * dose_step for i in range(num_doses)]

# Normalize dose for colormap
norm = mcolors.Normalize(vmin=min(doses), vmax=max(doses))
cmap = cm.get_cmap('viridis')

# Setup figure and axis
fig, ax = plt.subplots(figsize=(8, 6))

# Draw matrix squares
for idx, dose in enumerate(doses):
    row = idx // n_cols
    col = idx % n_cols
    x = col * pitch
    y = -row * pitch  # top-down layout
    color = cmap(norm(dose))

    rect = patches.Rectangle((x, y), square_size, square_size,
                             edgecolor='black', facecolor=color, linewidth=1)
    ax.add_patch(rect)
    ax.text(x + square_size / 2, y + square_size / 2, f"{dose}",
            ha='center', va='center', fontsize=9,
            color='white' if norm(dose) > 0.5 else 'black')

# Final layout cleanup
ax.set_aspect('equal')
ax.relim()  # Recalculate limits from patches
ax.autoscale_view()  # Adjust view based on contents
ax.set_xticks([])  # Hide ticks but keep layout
ax.set_yticks([])
ax.tick_params(left=False, bottom=False)
for spine in ax.spines.values():
    spine.set_visible(False)

# Add colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', fraction=0.035, pad=0.02)
cbar.set_label('Dose (µC/cm²)', fontsize=10)

# Create subfolder if needed
os.makedirs("figures/final", exist_ok=True)

# Save the plot
plt.savefig("figures/final/dose_matrix_mockup_clean.pdf", format='pdf', dpi=300)

plt.show()
