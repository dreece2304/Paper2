#%%
import pandas as pd
import numpy as np
import re
from IPython.display import display, HTML
import matplotlib.pyplot as plt
import os

#%%
def process_xps_file(filepath):
    """
    Process a single XPS Excel file and return a DataFrame
    """
    filename = os.path.basename(filepath)
    print(f"\nProcessing {filename}...")
    
    output_columns = ['B.E.', 'raw', 'fit1', 'fit2', 'fit3', 'fit4', 'fit5', 'fit6', 'Envelope', 'Background', 'Region']
    
    try:
        excel_data = pd.read_excel(filepath, header=None)
        print(f"  Loaded successfully: {excel_data.shape[0]} rows, {excel_data.shape[1]} columns")
        
        headers = excel_data.iloc[6]
        c1s_be_col = None
        if pd.notna(headers[9]) and "B.E." in str(headers[9]):
            c1s_be_col = 9
            print(f"  C 1s B.E. found at column 9")
        elif pd.notna(headers[8]) and "B.E." in str(headers[8]):
            c1s_be_col = 8
            print(f"  C 1s B.E. found at column 8")
        else:
            print(f"  ERROR: C 1s B.E. column not found!")
        
        regions_info = []

        # O 1s
        regions_info.append({
            'name': 'O 1s',
            'be_col': 0,
            'raw_col': 1,
            'fit_cols': [2, 3, 4, 5] if pd.notna(headers[5]) and 'O 1s' in str(headers[5]) else [2, 3, 4],
            'bg_col': 6 if 'Background' in str(headers[6]) else 5,
            'env_col': 7 if 'Envelope' in str(headers[7]) else 6
        })

        # C 1s
        if c1s_be_col == 9:
            regions_info.append({
                'name': 'C 1s',
                'be_col': 9,
                'raw_col': 10,
                'fit_cols': [11, 12, 13, 14],
                'bg_col': 15,
                'env_col': 16
            })
        elif c1s_be_col == 8:
            regions_info.append({
                'name': 'C 1s',
                'be_col': 8,
                'raw_col': 9,
                'fit_cols': [10, 11, 12, 13, 14],
                'bg_col': 15,
                'env_col': 16
            })

        # Al 2p
        regions_info.append({
            'name': 'Al 2p',
            'be_col': 18,
            'raw_col': 19,
            'fit_cols': [20],
            'bg_col': 21,
            'env_col': 22
        })

        all_data = []
        data_rows = excel_data.iloc[7:]

        for idx, row in data_rows.iterrows():
            for region in regions_info:
                try:
                    be_value = row.iloc[region['be_col']]
                    if pd.isna(be_value): continue
                    be_float = float(be_value)
                    if region['name'] == 'O 1s' and not (520 <= be_float <= 550): continue
                    if region['name'] == 'C 1s' and not (270 <= be_float <= 310): continue
                    if region['name'] == 'Al 2p' and not (60 <= be_float <= 95): continue

                    row_data = [be_float]
                    row_data.append(float(row.iloc[region['raw_col']]) if not pd.isna(row.iloc[region['raw_col']]) else np.nan)
                    for i in range(6):
                        if i < len(region['fit_cols']):
                            fit_val = row.iloc[region['fit_cols'][i]]
                            row_data.append(float(fit_val) if not pd.isna(fit_val) else np.nan)
                        else:
                            row_data.append(np.nan)
                    env = row.iloc[region['env_col']]
                    row_data.append(float(env) if not pd.isna(env) else np.nan)
                    bg = row.iloc[region['bg_col']]
                    row_data.append(float(bg) if not pd.isna(bg) else np.nan)
                    row_data.append(region['name'])

                    all_data.append(row_data)

                except Exception:
                    continue

        df = pd.DataFrame(all_data, columns=output_columns)
        print(f"  Processed {len(df)} data points")
        for r in ['O 1s', 'C 1s', 'Al 2p']:
            r_df = df[df['Region'] == r]
            if len(r_df) > 0:
                print(f"    {r}: {len(r_df)} points, B.E. range {r_df['B.E.'].min():.1f} - {r_df['B.E.'].max():.1f} eV")
            else:
                print(f"    {r}: No valid data points found")
        return df

    except Exception as e:
        print(f"  Error processing {filename}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

#%%
# Define data directory path
data_dir = '../data/raw/'

# List of input files
input_filenames = ['BTY_AD.xlsx', 'BTY_H2O.xlsx', 'BTY_UV.xlsx']

# Create full paths
input_files = [os.path.join(data_dir, filename) for filename in input_filenames]

# Check which files exist
existing_files = []
print(f"Looking for files in: {os.path.abspath(data_dir)}")
print("-" * 60)

for filepath, filename in zip(input_files, input_filenames):
    if os.path.exists(filepath):
        existing_files.append(filepath)
        print(f"✓ Found: {filename}")
    else:
        print(f"✗ Not found: {filename}")

print(f"\nWill process {len(existing_files)} files")

#%%
# Process all valid input files
all_dataframes = {}

for filepath in existing_files:
    key = os.path.basename(filepath).split('.')[0]
    df = process_xps_file(filepath)
    if df is not None:
        all_dataframes[key] = df

#%%
# Final 1x3 panel figure with shaded fits, fixed Al 2p, and background-subtracted raw data
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Use Viridis colormap (modern API)
viridis = plt.colormaps["viridis"]

# Setup panel and sample info
regions = ['O 1s', 'C 1s', 'Al 2p']
sample_order = ['BTY_AD', 'BTY_UV', 'BTY_H2O']
sample_labels = ['As Deposited', 'Water Exposed', 'UV + Water']
panel_labels = ['(a)', '(b)', '(c)']
offset_step = 1.2

fig, axes = plt.subplots(1, 3, figsize=(15, 6), constrained_layout=True)

# Generate peak color mapping by peak center position
peak_color_map = {}
all_peak_positions = set()

for df in all_dataframes.values():
    for region in regions:
        r_df = df[df['Region'] == region]
        for fit_col in [f'fit{i}' for i in range(1, 7)]:
            if fit_col in r_df.columns:
                peaks = r_df.loc[r_df[fit_col].notna()]
                if not peaks.empty:
                    peak_pos = peaks.loc[peaks[fit_col].idxmax(), 'B.E.']
                    all_peak_positions.add(round(peak_pos, 1))

sorted_peaks = sorted(all_peak_positions)
for i, pos in enumerate(sorted_peaks):
    peak_color_map[pos] = viridis(i / max(1, len(sorted_peaks) - 1))

# Plotting per region
for col_idx, region in enumerate(regions):
    ax = axes[col_idx]
    x_min, x_max = np.inf, -np.inf

    for sample_idx, sample_key in enumerate(sample_order):
        df = all_dataframes[sample_key]
        region_df = df[df['Region'] == region].sort_values('B.E.').copy()
        if region_df.empty:
            continue

        x_vals = region_df['B.E.'].values
        y_raw = region_df['raw'].values - region_df['Background'].values
        y_norm = (y_raw - np.min(y_raw)) / (np.max(y_raw) - np.min(y_raw))
        offset = sample_idx * offset_step

        # X limits based on signal
        sig_mask = y_norm > 0.05
        if np.any(sig_mask):
            x_min = min(x_min, np.min(x_vals[sig_mask]) - 0.5)
            x_max = max(x_max, np.max(x_vals[sig_mask]) + 0.5)

        # Plot raw data
        ax.plot(x_vals, y_norm + offset, 'kx', label=sample_labels[sample_idx])

        # Envelope
        envelope = region_df['Envelope'].values
        env_norm = (envelope - np.min(y_raw)) / (np.max(y_raw) - np.min(y_raw))
        ax.plot(x_vals, env_norm + offset, color='red', alpha=0.3, linewidth=1.2,
                label='Envelope' if sample_idx == 0 else "")

        # Fits
        for i, fit_col in enumerate([f'fit{i}' for i in range(1, 7)]):
            if fit_col in region_df and region_df[fit_col].notna().any():
                fit_y = region_df[fit_col].values
                fit_norm = (fit_y - np.min(y_raw)) / (np.max(y_raw) - np.min(y_raw))
                peak_pos = round(x_vals[np.nanargmax(fit_y)], 1)
                color = peak_color_map.get(peak_pos, 'gray')
                ax.fill_between(x_vals, offset, fit_norm + offset, color=color, alpha=0.4, linewidth=0)
                ax.plot(x_vals, fit_norm + offset, '-', color=color, linewidth=1)

    # Axis formatting
    ax.set_title(f"{panel_labels[col_idx]} {region}", fontsize=12, loc='left')
    ax.set_xlim(x_min, x_max)
    ax.invert_xaxis()
    ax.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    if col_idx == 0:
        ax.set_ylabel("Normalized Intensity + Offset")
    else:
        ax.set_yticklabels([])

    ax.set_xlabel("Binding Energy (eV)")

plt.suptitle("XPS Spectra Comparison by Region", fontsize=14)
plt.show()

#%%
# Clean XPS Figure - Publication Quality with Optimized Layout
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import make_interp_spline
import pandas as pd

# Golden ratio for overall figure, but square panels
PHI = 1.618033988749

def create_fake_xps_data():
    """Generate realistic XPS data for testing"""
    
    regions_info = {
        'O 1s': {'range': (528, 545), 'peaks': [532.2, 533.8], 'widths': [1.2, 1.5], 'intensities': [1.0, 0.6]},
        'C 1s': {'range': (280, 295), 'peaks': [284.8, 286.2, 288.5], 'widths': [1.1, 1.3, 1.2], 'intensities': [1.0, 0.7, 0.4]},
        'Al 2p': {'range': (70, 80), 'peaks': [74.1], 'widths': [1.0], 'intensities': [1.0]}
    }
    
    sample_variations = {
        'BTY_AD': {'shift': 0.0, 'intensity_factor': 1.0, 'noise_level': 0.015},
        'BTY_UV': {'shift': 0.15, 'intensity_factor': 0.85, 'noise_level': 0.020},
        'BTY_H2O': {'shift': 0.25, 'intensity_factor': 1.15, 'noise_level': 0.025}
    }
    
    all_dataframes = {}
    
    for sample, variation in sample_variations.items():
        data_rows = []
        
        for region, info in regions_info.items():
            be_start, be_end = info['range']
            be_values = np.linspace(be_start, be_end, 250)
            
            # Realistic background
            background = 800 + 40 * (be_values - be_start) + 150 * np.exp(-(be_values - be_start) / 6)
            
            # Generate peaks
            fits = {}
            envelope = np.zeros_like(be_values)
            
            for i, (peak_pos, width, base_intensity) in enumerate(zip(info['peaks'], info['widths'], info['intensities'])):
                shifted_pos = peak_pos + variation['shift']
                intensity = 2500 * base_intensity * variation['intensity_factor']
                
                fit = intensity * np.exp(-0.5 * ((be_values - shifted_pos) / width) ** 2)
                fits[f'fit{i+1}'] = fit
                envelope += fit
            
            total_signal = envelope + background
            noise_std = variation['noise_level'] * np.max(total_signal)
            noise = np.random.normal(0, noise_std, len(be_values))
            raw_data = total_signal + noise
            
            for j, be in enumerate(be_values):
                row = {
                    'Region': region,
                    'B.E.': be,
                    'raw': raw_data[j],
                    'Background': background[j],
                    'Envelope': envelope[j] + background[j]
                }
                
                for fit_name, fit_data in fits.items():
                    row[fit_name] = fit_data[j] + background[j]
                
                for k in range(1, 7):
                    if f'fit{k}' not in row:
                        row[f'fit{k}'] = np.nan
                
                data_rows.append(row)
        
        all_dataframes[sample] = pd.DataFrame(data_rows)
    
    return all_dataframes

# Generate test data (replace with your actual data)
all_dataframes = create_fake_xps_data()

# Publication settings
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 12,
    'axes.linewidth': 2.0,
    'axes.labelweight': 'bold',
    'axes.titleweight': 'bold',
    'xtick.major.width': 1.5,
    'ytick.major.width': 1.5,
    'legend.frameon': True,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white'
})

# Figure layout: Golden ratio width, square panels
panel_size = 4.0  # Square panels work better for XPS
fig_width = panel_size * 3 * 1.1  # 3 panels + spacing
fig_height = panel_size * 1.0      # Single row

fig, axes = plt.subplots(1, 3, figsize=(fig_width, fig_height))

# Ensure square aspect ratio for each panel
for ax in axes:
    ax.set_aspect('equal', adjustable='box')

# Viridis colors - convert to hex to avoid warnings
viridis = plt.colormaps['viridis']
fit_colors = [mcolors.to_hex(viridis(i/5)) for i in range(6)]
sample_colors = [mcolors.to_hex(viridis(x)) for x in [0.2, 0.6, 0.9]]

# Sample and region info
sample_order = ['BTY_AD', 'BTY_UV', 'BTY_H2O']
sample_labels = ['As Deposited', 'Water Exposed', 'UV + Water']
regions = ['O 1s', 'C 1s', 'Al 2p']
panel_labels = ['a', 'b', 'c']

# Font sizes with clear hierarchy
base_font = 12
title_font = 16
label_font = 10

# Plot each region
for col_idx, region in enumerate(regions):
    ax = axes[col_idx]
    
    # Collect and normalize data
    region_data = {}
    
    for sample_idx, sample_key in enumerate(sample_order):
        if sample_key in all_dataframes:
            df = all_dataframes[sample_key]
            region_df = df[df['Region'] == region].sort_values('B.E.').copy()
            
            if len(region_df) > 0:
                background = region_df['Background'].values
                raw_corrected = region_df['raw'].values - background
                
                # Min-max normalization
                data_min, data_max = np.min(raw_corrected), np.max(raw_corrected)
                if data_max > data_min:
                    raw_normalized = (raw_corrected - data_min) / (data_max - data_min)
                else:
                    raw_normalized = raw_corrected
                
                # Normalize fits
                fits_normalized = {}
                for fit_col in ['fit1', 'fit2', 'fit3', 'fit4', 'fit5', 'fit6']:
                    if region_df[fit_col].notna().any():
                        fit_corrected = region_df[fit_col].values - background
                        if data_max > data_min:
                            fits_normalized[fit_col] = (fit_corrected - data_min) / (data_max - data_min)
                        else:
                            fits_normalized[fit_col] = fit_corrected
                
                # Normalize envelope
                envelope_corrected = region_df['Envelope'].values - background
                if data_max > data_min:
                    envelope_normalized = (envelope_corrected - data_min) / (data_max - data_min)
                else:
                    envelope_normalized = envelope_corrected
                
                region_data[sample_key] = {
                    'raw_normalized': raw_normalized,
                    'envelope_normalized': envelope_normalized,
                    'fits_normalized': fits_normalized,
                    'be_values': region_df['B.E.'].values
                }
    
    # Clear, well-spaced offsets to avoid overlap
    offset_spacing = 1.5  # Generous spacing between samples
    
    # Plot each sample with clear separation
    for sample_idx, sample_key in enumerate(sample_order):
        if sample_key in region_data:
            data = region_data[sample_key]
            be_values = data['be_values']
            
            # Vertical offset
            y_offset = sample_idx * offset_spacing
            
            # Apply offsets
            raw_normalized = data['raw_normalized'] + y_offset
            envelope_normalized = data['envelope_normalized'] + y_offset
            
            # Plot individual fits with clean styling
            for i, fit_col in enumerate(['fit1', 'fit2', 'fit3', 'fit4', 'fit5', 'fit6']):
                if fit_col in data['fits_normalized']:
                    fit_normalized = data['fits_normalized'][fit_col] + y_offset
                    
                    # Clean fills and lines
                    ax.fill_between(be_values, y_offset, fit_normalized, 
                                   color=fit_colors[i], alpha=0.6, 
                                   edgecolor='none', zorder=2)
                    ax.plot(be_values, fit_normalized, '-', 
                           color=fit_colors[i], linewidth=1.5, 
                           zorder=3, alpha=0.9)
            
            # Envelope line
            ax.plot(be_values, envelope_normalized, '-', 
                   color='darkred', linewidth=2.0, alpha=0.9, zorder=4)
            
            # Experimental data - smaller markers, less frequent
            marker_indices = np.arange(0, len(be_values), 6)  # Every 6th point
            ax.scatter(be_values[marker_indices], raw_normalized[marker_indices],
                      color=sample_colors[sample_idx], s=8, alpha=0.8,
                      edgecolors='white', linewidths=0.3, zorder=5)
    
    # Clean, non-overlapping labels positioned outside data area
    max_y = 3 * offset_spacing + 0.5  # Above all data
    
    for sample_idx, sample_key in enumerate(sample_order):
        if sample_key in region_data:
            # Position labels horizontally across the top
            label_x_positions = [0.2, 0.5, 0.8]  # Left, center, right
            label_x = be_values[int(len(be_values) * label_x_positions[sample_idx])]
            label_y = max_y + 0.2
            
            ax.text(label_x, label_y, sample_labels[sample_idx], 
                   fontsize=label_font, fontweight='bold', 
                   ha='center', va='bottom', color=sample_colors[sample_idx],
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                            alpha=0.9, edgecolor=sample_colors[sample_idx], 
                            linewidth=1.0))
    
    # Axis formatting
    ax.set_xlabel('Binding Energy (eV)', fontsize=base_font, fontweight='bold')
    if col_idx == 0:
        ax.set_ylabel('Intensity (normalized, offset)', fontsize=base_font, fontweight='bold')
    
    # Title
    ax.set_title(region, fontsize=title_font, fontweight='bold', pad=15)
    
    # Panel label
    ax.text(0.05, 0.95, f'({panel_labels[col_idx]})', transform=ax.transAxes,
           fontsize=14, fontweight='bold', va='top', ha='left', zorder=10,
           bbox=dict(boxstyle='circle,pad=0.3', facecolor='white', 
                    alpha=0.95, edgecolor='black', linewidth=1.5))
    
    # Axis limits and styling
    ax.invert_xaxis()
    ax.set_yticklabels([])
    
    # Set x-axis limits with small padding
    all_be_values = []
    for sample_key in region_data:
        all_be_values.extend(region_data[sample_key]['be_values'])
    
    if all_be_values:
        be_min, be_max = min(all_be_values), max(all_be_values)
        be_range = be_max - be_min
        ax.set_xlim(be_max + 0.03 * be_range, be_min - 0.03 * be_range)
    
    # Set y-axis limits to show all data plus labels
    ax.set_ylim(-0.2, max_y + 0.6)
    
    # Clean ticks
    ax.tick_params(axis='x', labelsize=10, width=1.5, length=4, direction='in')
    ax.tick_params(axis='y', width=1.5, length=3)
    
    # Frame
    for spine in ax.spines.values():
        spine.set_linewidth(2.0)
        spine.set_edgecolor('black')
    
    # Minimal grid
    ax.grid(True, alpha=0.1, linewidth=0.5, color='gray', zorder=1)

# Add legend to first panel
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='gray', linestyle='None', 
              markersize=3, markerfacecolor='gray', markeredgecolor='white',
              label='Experimental'),
    plt.Line2D([0], [0], color='darkred', linewidth=2.0, label='Envelope'),
    plt.patches.Patch(color=fit_colors[0], alpha=0.6, label='Components')
]
axes[0].legend(handles=legend_elements, loc='upper left', 
              fontsize=9, frameon=True, framealpha=0.9)

# Layout
plt.tight_layout()
plt.subplots_adjust(wspace=0.3)  # More space between panels

plt.show()

# Save with clean naming
base_name = 'XPS_publication_figure'

fig.savefig(f'{base_name}.tiff', dpi=600, format='tiff', bbox_inches='tight')
fig.savefig(f'{base_name}.pdf', format='pdf', bbox_inches='tight')
fig.savefig(f'{base_name}.png', dpi=300, format='png', bbox_inches='tight')

plt.rcdefaults()

print("✓ Clean XPS figure created")
print("✓ Square panels for optimal XPS visualization")
print("✓ Clear spacing to eliminate overlaps")
print("✓ Professional styling with viridis colors")
#%%
# Publication-Quality XPS Figure - Journal of Materials Chemistry A
# Golden Ratio Design with Viridis Color Scheme
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import make_interp_spline
import pandas as pd

# Golden ratio constant for aesthetic proportions
PHI = 1.618033988749

def create_fake_xps_data():
    """Generate realistic XPS data for testing and development"""
    
    # Define regions with realistic binding energy ranges and peak parameters
    regions_info = {
        'O 1s': {'range': (528, 545), 'peaks': [532.2, 533.8], 'widths': [1.2, 1.5], 'intensities': [1.0, 0.6]},
        'C 1s': {'range': (280, 295), 'peaks': [284.8, 286.2, 288.5], 'widths': [1.1, 1.3, 1.2], 'intensities': [1.0, 0.7, 0.4]},
        'Al 2p': {'range': (70, 80), 'peaks': [74.1], 'widths': [1.0], 'intensities': [1.0]}
    }
    
    # Sample-specific variations (realistic chemical changes)
    sample_variations = {
        'BTY_AD': {'shift': 0.0, 'intensity_factor': 1.0, 'noise_level': 0.015},
        'BTY_UV': {'shift': 0.15, 'intensity_factor': 0.85, 'noise_level': 0.020},
        'BTY_H2O': {'shift': 0.25, 'intensity_factor': 1.15, 'noise_level': 0.025}
    }
    
    all_dataframes = {}
    
    for sample, variation in sample_variations.items():
        data_rows = []
        
        for region, info in regions_info.items():
            # Create high-resolution binding energy array
            be_start, be_end = info['range']
            be_values = np.linspace(be_start, be_end, 250)
            
            # Realistic background model (Shirley-type + linear)
            background = 800 + 40 * (be_values - be_start) + 150 * np.exp(-(be_values - be_start) / 6)
            
            # Generate individual peak components
            fits = {}
            envelope = np.zeros_like(be_values)
            
            for i, (peak_pos, width, base_intensity) in enumerate(zip(info['peaks'], info['widths'], info['intensities'])):
                # Apply chemical shift and intensity scaling
                shifted_pos = peak_pos + variation['shift']
                intensity = 2500 * base_intensity * variation['intensity_factor']
                
                # Create realistic Gaussian peak
                fit = intensity * np.exp(-0.5 * ((be_values - shifted_pos) / width) ** 2)
                fits[f'fit{i+1}'] = fit
                envelope += fit
            
            # Total signal = peaks + background
            total_signal = envelope + background
            
            # Add realistic experimental noise
            noise_std = variation['noise_level'] * np.max(total_signal)
            noise = np.random.normal(0, noise_std, len(be_values))
            raw_data = total_signal + noise
            
            # Create structured data
            for j, be in enumerate(be_values):
                row = {
                    'Region': region,
                    'B.E.': be,
                    'raw': raw_data[j],
                    'Background': background[j],
                    'Envelope': envelope[j] + background[j]
                }
                
                # Add individual fit components
                for fit_name, fit_data in fits.items():
                    row[fit_name] = fit_data[j] + background[j]
                
                # Ensure all fit columns exist (fill with NaN if missing)
                for k in range(1, 7):
                    if f'fit{k}' not in row:
                        row[f'fit{k}'] = np.nan
                
                data_rows.append(row)
        
        all_dataframes[sample] = pd.DataFrame(data_rows)
    
    return all_dataframes

# Generate synthetic data for testing (replace with your actual data)
all_dataframes = create_fake_xps_data()

# Set publication-quality matplotlib parameters
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 12,
    'axes.linewidth': 2.2,
    'axes.labelweight': 'bold',
    'axes.titleweight': 'bold',
    'xtick.major.width': 1.8,
    'ytick.major.width': 1.8,
    'xtick.minor.width': 1.2,
    'ytick.minor.width': 1.2,
    'legend.frameon': True,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# Create figure with golden ratio dimensions
fig_height = 6.0
fig_width = fig_height * PHI
fig, axes = plt.subplots(1, 3, figsize=(fig_width, fig_height))

# Define consistent viridis color scheme
viridis = plt.colormaps['viridis']
# Convert to explicit hex colors to avoid matplotlib warnings
fit_colors = [plt.colors.to_hex(viridis(i/5)) for i in range(6)]
sample_colors = [plt.colors.to_hex(viridis(x)) for x in [0.15, 0.55, 0.85]]

# Sample and region definitions
sample_order = ['BTY_AD', 'BTY_UV', 'BTY_H2O']
sample_labels = ['As Deposited', 'Water Exposed', 'UV + Water']
regions = ['O 1s', 'C 1s', 'Al 2p']
panel_labels = ['a', 'b', 'c']

# Golden ratio-based font hierarchy
base_font = 12
medium_font = int(base_font * PHI**0.5)  # ≈15pt
large_font = int(base_font * PHI)        # ≈19pt
title_font = int(base_font * PHI**1.3)   # ≈21pt

# Plot each region (panel) with optimized design
for col_idx, region in enumerate(regions):
    ax = axes[col_idx]
    
    # Data collection and normalization
    region_data = {}
    
    # First pass: collect and normalize data
    for sample_idx, sample_key in enumerate(sample_order):
        if sample_key in all_dataframes:
            df = all_dataframes[sample_key]
            region_df = df[df['Region'] == region].sort_values('B.E.').copy()
            
            if len(region_df) > 0:
                background = region_df['Background'].values
                raw_corrected = region_df['raw'].values - background
                
                # Min-max normalization for consistent scaling
                data_min, data_max = np.min(raw_corrected), np.max(raw_corrected)
                if data_max > data_min:
                    raw_normalized = (raw_corrected - data_min) / (data_max - data_min)
                else:
                    raw_normalized = raw_corrected
                
                # Normalize fit components consistently
                fits_normalized = {}
                for fit_col in ['fit1', 'fit2', 'fit3', 'fit4', 'fit5', 'fit6']:
                    if region_df[fit_col].notna().any():
                        fit_corrected = region_df[fit_col].values - background
                        if data_max > data_min:
                            fits_normalized[fit_col] = (fit_corrected - data_min) / (data_max - data_min)
                        else:
                            fits_normalized[fit_col] = fit_corrected
                
                # Normalize envelope
                envelope_corrected = region_df['Envelope'].values - background
                if data_max > data_min:
                    envelope_normalized = (envelope_corrected - data_min) / (data_max - data_min)
                else:
                    envelope_normalized = envelope_corrected
                
                region_data[sample_key] = {
                    'raw_normalized': raw_normalized,
                    'envelope_normalized': envelope_normalized,
                    'fits_normalized': fits_normalized,
                    'be_values': region_df['B.E.'].values
                }
    
    # Optimized golden ratio spacing
    offset_base = 1.3 * (PHI - 1)  # ≈0.80 for excellent separation
    
    # Second pass: create publication-quality plots
    for sample_idx, sample_key in enumerate(sample_order):
        if sample_key in region_data:
            data = region_data[sample_key]
            be_values = data['be_values']
            
            # Calculate vertical offset using golden ratio
            y_offset = sample_idx * offset_base * PHI**0.65
            
            # Apply offsets to normalized data
            raw_normalized = data['raw_normalized'] + y_offset
            envelope_normalized = data['envelope_normalized'] + y_offset
            
            # Plot individual peak components with professional styling
            for i, fit_col in enumerate(['fit1', 'fit2', 'fit3', 'fit4', 'fit5', 'fit6']):
                if fit_col in data['fits_normalized']:
                    fit_normalized = data['fits_normalized'][fit_col] + y_offset
                    
                    # Smooth interpolation for publication quality
                    if len(be_values) > 10:
                        try:
                            # Sort data for interpolation
                            sort_indices = np.argsort(be_values)
                            be_sorted = be_values[sort_indices]
                            fit_sorted = fit_normalized[sort_indices]
                            
                            # Create smooth curve
                            spl = make_interp_spline(be_sorted, fit_sorted, k=2)
                            be_smooth = np.linspace(be_sorted.min(), be_sorted.max(), 300)
                            fit_smooth = spl(be_smooth)
                            
                            # Professional fill and line
                            ax.fill_between(be_smooth, y_offset, fit_smooth, 
                                           color=fit_colors[i], alpha=0.5, 
                                           edgecolor='none', zorder=3)
                            ax.plot(be_smooth, fit_smooth, '-', 
                                   color=fit_colors[i], linewidth=1.8, 
                                   zorder=4, alpha=0.9)
                        except:
                            # Fallback for problematic data
                            ax.fill_between(be_values, y_offset, fit_normalized, 
                                           color=fit_colors[i], alpha=0.5, zorder=3)
                            ax.plot(be_values, fit_normalized, '-', 
                                   color=fit_colors[i], linewidth=1.8, zorder=4)
            
            # Envelope line (sum of all components)
            ax.plot(be_values, envelope_normalized, '-', 
                   color='#800000', linewidth=2.5, alpha=0.9, zorder=5)
            
            # Experimental data points
            subsample = slice(None, None, 4)  # Every 4th point for cleaner appearance
            ax.plot(be_values[subsample], raw_normalized[subsample], 'o',
                   color=sample_colors[sample_idx], markersize=2.2, alpha=0.8,
                   markeredgecolor='white', markeredgewidth=0.3, zorder=6)
            
            # Smart label positioning to avoid overlap
            label_positions = [(0.78, 0.15), (0.22, 0.52), (0.78, 0.85)]
            pos_x_frac, pos_y_frac = label_positions[sample_idx]
            
            label_x = be_values[int(len(be_values) * pos_x_frac)]
            data_range = np.max(raw_normalized) - np.min(raw_normalized)
            label_y = np.min(raw_normalized) + data_range * pos_y_frac
            
            ax.text(label_x, label_y, sample_labels[sample_idx], 
                   fontsize=medium_font-3, fontweight='600', 
                   ha='center', va='center', color=sample_colors[sample_idx],
                   bbox=dict(boxstyle='round,pad=0.25', facecolor='white', 
                            alpha=0.95, edgecolor=sample_colors[sample_idx], 
                            linewidth=1.0))
    
    # Professional axis formatting
    ax.set_xlabel('Binding Energy (eV)', fontsize=medium_font, 
                  fontweight='bold', labelpad=8)
    if col_idx == 0:
        ax.set_ylabel('Intensity (normalized, offset)', fontsize=medium_font, 
                     fontweight='bold', labelpad=10)
    
    # Region title with golden ratio spacing
    ax.set_title(region, fontsize=large_font, fontweight='bold', 
                pad=int(12 * PHI**0.5))
    
    # Panel label with professional styling
    ax.text(0.05, 0.95, f'({panel_labels[col_idx]})', transform=ax.transAxes,
           fontsize=int(title_font * 0.75), fontweight='bold', 
           va='top', ha='left', zorder=10,
           bbox=dict(boxstyle='circle,pad=0.35', facecolor='white', 
                    alpha=0.95, edgecolor='black', linewidth=1.8))
    
    # Optimize axis limits and styling
    ax.invert_xaxis()
    ax.set_yticklabels([])
    
    # Set precise x-axis limits based on data
    all_be_values = []
    for sample_key in region_data:
        all_be_values.extend(region_data[sample_key]['be_values'])
    
    if all_be_values:
        be_min, be_max = min(all_be_values), max(all_be_values)
        be_range = be_max - be_min
        ax.set_xlim(be_max + 0.02 * be_range, be_min - 0.02 * be_range)
    
    # Professional tick formatting
    ax.tick_params(axis='x', labelsize=base_font, width=1.8, length=5,
                  direction='in', pad=5)
    ax.tick_params(axis='y', width=1.8, length=4)
    
    # Frame styling
    for spine in ax.spines.values():
        spine.set_linewidth(2.2)
        spine.set_edgecolor('#2c3e50')
        spine.set_zorder(20)
    
    # Minimal scientific grid
    ax.grid(True, alpha=0.06, linewidth=0.4, linestyle='-', color='gray', zorder=1)
    
    # Add legend to first panel only
    if col_idx == 0:
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='gray', linestyle='None', 
                      markersize=3, markerfacecolor='gray', markeredgecolor='white',
                      label='Experimental'),
            plt.Line2D([0], [0], color='#800000', linewidth=2.5, label='Envelope'),
            plt.patches.Patch(color=fit_colors[0], alpha=0.5, label='Components')
        ]
        ax.legend(handles=legend_elements, loc='upper left', 
                 fontsize=base_font-2, frameon=True, fancybox=True, 
                 framealpha=0.95, edgecolor='gray')

# Final layout optimization
plt.tight_layout()
plt.subplots_adjust(wspace=0.15)

# Display the figure
plt.show()

# Save with standardized naming convention
base_filename = 'XPS_publication_figure'

# High-resolution TIFF for journal submission
fig.savefig(f'{base_filename}.tiff', dpi=600, format='tiff', 
           facecolor='white', edgecolor='none')
print(f"✓ Saved: {base_filename}.tiff (600 DPI)")

# Vector PDF with metadata
fig.savefig(f'{base_filename}.pdf', format='pdf', 
           facecolor='white', edgecolor='none',
           metadata={'Title': 'XPS Analysis - Publication Figure',
                    'Subject': 'X-ray Photoelectron Spectroscopy',
                    'Keywords': 'XPS, Materials Chemistry, Surface Analysis'})
print(f"✓ Saved: {base_filename}.pdf (vector)")

# High-quality PNG for presentations
fig.savefig(f'{base_filename}.png', dpi=300, format='png', 
           facecolor='white', edgecolor='none')
print(f"✓ Saved: {base_filename}.png (300 DPI)")

# EPS for journals preferring this format
fig.savefig(f'{base_filename}.eps', format='eps', 
           facecolor='white', edgecolor='none')
print(f"✓ Saved: {base_filename}.eps (vector)")

# Reset matplotlib to defaults
plt.rcdefaults()

print(f"\n🎨 Publication-Quality XPS Figure Complete:")
print(f"   • Golden ratio dimensions: {PHI:.3f}:1")
print(f"   • Viridis color scheme with explicit hex codes")
print(f"   • Min-max normalized data for optimal comparison")
print(f"   • Professional typography and spacing")
print(f"   • Journal of Materials Chemistry A standards")
print(f"   • Standardized file naming: '{base_filename}.*'")
print(f"   • Multiple formats: TIFF (600 DPI), PDF, PNG, EPS")
#%%
# Create overlay plots with normalized intensities for better comparison
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, region in enumerate(regions):
    ax = axes[idx]
    
    # Plot each sample with different colors
    colors = {'BTY_AD': 'blue', 'BTY_UV': 'red', 'BTY_H2O': 'green'}
    linestyles = {'BTY_AD': '-', 'BTY_UV': '--', 'BTY_H2O': ':'}
    
    for sample_key, sample_label in zip(sample_order, sample_labels):
        if sample_key in all_dataframes:
            df = all_dataframes[sample_key]
            region_df = df[df['Region'] == region].sort_values('B.E.')
            
            if len(region_df) > 0:
                # Normalize the raw data to max = 1 for comparison
                normalized_raw = region_df['raw'] / region_df['raw'].max()
                
                ax.plot(region_df['B.E.'], normalized_raw, 
                       color=colors[sample_key], 
                       linestyle=linestyles[sample_key],
                       label=sample_label, 
                       linewidth=2)
    
    ax.set_xlabel('Binding Energy (eV)')
    ax.set_ylabel('Normalized Intensity')
    ax.set_title(f'{region} - All Samples (Normalized)', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.invert_xaxis()

plt.suptitle('Normalized XPS Comparison', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

# Save this figure too
fig.savefig('BTY_normalized_comparison.png', dpi=300, bbox_inches='tight')
print("\n✓ Normalized comparison figure saved as 'BTY_normalized_comparison.png'")
#%%
import matplotlib.pyplot as plt
import seaborn as sns

def set_plot_style():
    """
    Set the global plot style for all figures to match publication standards.
    """

    # Update matplotlib defaults
    plt.rcParams.update({
        # Fonts
        'font.family': 'sans-serif',
        'font.sans-serif': ['Verdana'],
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,

        # Line styles
        'lines.linewidth': 1.5,  # For all line plots

        # Axis spine styling
        'axes.linewidth': 3,        # Thick black frame
        'axes.edgecolor': 'black',

        # Tick markers on all sides
        'xtick.top': True,
        'xtick.bottom': True,
        'ytick.left': True,
        'ytick.right': True,
        'xtick.direction': 'in',
        'ytick.direction': 'in',

        # Grid — off by default for line plots
        'axes.grid': False,

        # Color map default
        'image.cmap': 'viridis',

        # Legend
        'legend.frameon': False,
        'legend.fontsize': 10,

        # Resolution
        'figure.dpi': 300,
        'savefig.dpi': 300,
    })

    # Seaborn theme baseline
    sns.set_theme(style="white", palette="viridis")

# Apply the style
set_plot_style()
#%%
# Create 1x3 panel figure with stacked samples - Journal of Materials Chemistry A format
fig, axes = plt.subplots(1, 3, figsize=(15, 6))

# Define the order of samples and regions
sample_order = ['BTY_AD', 'BTY_UV', 'BTY_H2O']  
sample_labels = ['As Deposited', 'Water Exposed', 'UV + Water']  # More descriptive labels
regions = ['O 1s', 'C 1s', 'Al 2p']

# Panel labels
panel_labels = ['(a)', '(b)', '(c)']

# Get viridis colormap for fits
import matplotlib.cm as cm
viridis = plt.colormaps['viridis']
fit_colors = [viridis(i/5) for i in range(6)]  # 6 colors from viridis

# Define offset values for stacking samples (increase these for more separation)
base_offsets = [0, 0.6, 1.2]  # Offset multipliers for each sample

# Plot each region (column)
for col_idx, region in enumerate(regions):
    ax = axes[col_idx]
    
    # Calculate max intensity for this region to normalize offsets
    max_intensity = 0
    region_data = {}
    
    # First pass: collect data and find max intensity
    for sample_idx, sample_key in enumerate(sample_order):
        if sample_key in all_dataframes:
            df = all_dataframes[sample_key]
            region_df = df[df['Region'] == region].sort_values('B.E.').copy()
            
            if len(region_df) > 0:
                background = region_df['Background'].values
                raw_corrected = region_df['raw'].values - background
                region_data[sample_key] = {
                    'df': region_df,
                    'background': background,
                    'raw_corrected': raw_corrected,
                    'be_values': region_df['B.E.'].values
                }
                max_intensity = max(max_intensity, np.max(raw_corrected))
    
    # Calculate offset value based on max intensity
    offset_value = max_intensity * 0.8  # 80% of max intensity for separation
    
    # Second pass: plot with offsets
    for sample_idx, sample_key in enumerate(sample_order):
        if sample_key in region_data:
            data = region_data[sample_key]
            region_df = data['df']
            background = data['background']
            be_values = data['be_values']
            
            # Calculate offset for this sample
            y_offset = base_offsets[sample_idx] * offset_value
            
            # Raw data minus background
            raw_corrected = data['raw_corrected'] + y_offset
            
            # Envelope minus background
            envelope_corrected = region_df['Envelope'].values - background + y_offset
            
            # Plot individual fits (background-subtracted) with filled areas
            for i, fit_col in enumerate(['fit1', 'fit2', 'fit3', 'fit4', 'fit5', 'fit6']):
                if region_df[fit_col].notna().any():
                    fit_corrected = region_df[fit_col].values - background + y_offset
                    # Fill area under fit
                    ax.fill_between(be_values, y_offset, fit_corrected, 
                                   color=fit_colors[i], alpha=0.4)
                    # Draw fit line (thicker for journal quality)
                    ax.plot(be_values, fit_corrected, 
                           '-', color=fit_colors[i], linewidth=2.0)
            
            # Plot envelope as red line (thicker and more visible)
            ax.plot(be_values, envelope_corrected, 
                   'r-', linewidth=2.5, alpha=0.6)
            
            # Plot raw data as black circles (better for publication)
            ax.plot(be_values, raw_corrected, 
                   'ko', markersize=2.5, markeredgewidth=0.5, alpha=0.8)
            
            # Add sample label on the right side of each trace
            mid_idx = len(be_values) // 2
            ax.text(be_values[mid_idx] - 2, raw_corrected[mid_idx], sample_labels[sample_idx], 
                   fontsize=11, fontweight='bold', ha='right', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))
    
    # Formatting for journal quality
    ax.set_xlabel('Binding Energy (eV)', fontsize=14, fontweight='bold')
    if col_idx == 0:
        ax.set_ylabel('Intensity (normalized, offset)', fontsize=14, fontweight='bold')
    
    # Set title for each region
    ax.set_title(f'{region}', fontsize=16, fontweight='bold', pad=20)
    
    # Add panel label in upper left corner
    ax.text(0.05, 0.95, panel_labels[col_idx], transform=ax.transAxes,
           fontsize=16, fontweight='bold', va='top', ha='left',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='black'))
    
    # Invert x-axis (typical for XPS)
    ax.invert_xaxis()
    
    # Remove y-axis tick labels (since we're using offset data)
    ax.set_yticklabels([])
    
    # Improve tick formatting
    ax.tick_params(axis='x', labelsize=12, width=2, length=6)
    ax.tick_params(axis='y', width=2, length=6)
    
    # Apply thick black frame for journal quality
    for spine in ax.spines.values():
        spine.set_linewidth(3)
        spine.set_edgecolor('black')
    
    # Set appropriate margins
    ax.margins(x=0.02, y=0.05)

# Overall figure formatting
plt.tight_layout()

# Adjust spacing between subplots
plt.subplots_adjust(wspace=0.15)

# Show the plot
plt.show()

# Save in multiple formats for publication
# High-resolution TIFF (300 DPI)
fig.savefig('XPS_journal_figure.tiff', dpi=300, bbox_inches='tight', 
           facecolor='white', edgecolor='none', format='tiff')
print("✓ Figure saved as 'XPS_journal_figure.tiff' (300 DPI)")

# PDF (vector format for publications)
fig.savefig('XPS_journal_figure.pdf', bbox_inches='tight', 
           facecolor='white', edgecolor='none', format='pdf')
print("✓ Figure saved as 'XPS_journal_figure.pdf' (vector format)")

# PNG backup (for presentations/web)
fig.savefig('XPS_journal_figure.png', dpi=300, bbox_inches='tight', 
           facecolor='white', edgecolor='none', format='png')
print("✓ Figure saved as 'XPS_journal_figure.png' (300 DPI backup)")
#%%

#%%

#%%

#%%

#%%

#%%
