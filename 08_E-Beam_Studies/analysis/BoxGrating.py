import matplotlib.patches as patches
import matplotlib.colors as mcolors
from matplotlib import pyplot as plt

from shared.utils.plot_styles import set_plot_style
from shared.utils.helpers import create_figure, save_figure
from shared.utils.config import viridis

# Apply global styles
set_plot_style()

# Create figure and axis
fig, ax = create_figure(width_cm=18, aspect_ratio=4/3)
ax.set_aspect('equal')
ax.axis('off')

# Parameters
linewidths_nm = [500, 200, 100, 50, 10]
bar_display_widths = [12, 8, 6, 4, 2]  # Fixed, for display only
bar_height = 40
bars_per_group = 3
spacing_between_bars = 5
spacing_between_groups = 15
label_offset = 6

# Draw 4 boxes
box_size = 100
box_coords = [(-120, 100), (20, 100), (-120, -120), (20, -120)]
for x, y in box_coords:
    ax.add_patch(patches.Rectangle((x, y), box_size, box_size,
                                   edgecolor='black', facecolor='lightgrey'))

# Compute total width
group_widths = [(bars_per_group * (w + spacing_between_bars)) for w in bar_display_widths]
total_width = sum(group_widths) + spacing_between_groups * (len(group_widths) - 1)
x_cursor = -total_width / 2
y_base = 10
norm = mcolors.Normalize(vmin=min(linewidths_nm), vmax=max(linewidths_nm))

# Draw bars and labels
for lw_nm, w in zip(linewidths_nm, bar_display_widths):
    group_w = bars_per_group * (w + spacing_between_bars)
    color = viridis(norm(lw_nm))

    for i in range(bars_per_group):
        x = x_cursor + i * (w + spacing_between_bars)
        ax.add_patch(patches.Rectangle((x, y_base), w, bar_height, color=color))

    ax.text(x_cursor + group_w / 2, y_base + bar_height + label_offset,
            f"{lw_nm} nm", ha='center', va='bottom', fontsize=8)

    x_cursor += group_w + spacing_between_groups
# Autoscale and keep just enough margin
ax.relim()
ax.autoscale_view()

# Save figure
save_figure(fig, "box_grating_mockup_clean", folder="figures/final", formats=("pdf",))

plt.show()