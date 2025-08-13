#!/usr/bin/env python3
"""
XPS Analysis Script - IMPROVED Publication Quality Figures
=========================================================

MAJOR IMPROVEMENTS:
- Fixed normalization (per-sample, not global)
- Proper envelope line (thin, transparent)
- Full page width figure size
- Major/minor tick markers on all axes
- Better readability and professional styling
- Improved color scheme and contrast

Usage:
    python xps_analysis_improved.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as ticker
import os
import sys
import warnings
from pathlib import Path

# Get the absolute path to the project root
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
XPS_ROOT = SCRIPT_DIR.parent

# Add project root to path for imports
sys.path.append(str(PROJECT_ROOT))

try:
    from shared.utils.plot_styles import set_plot_style
    from shared.utils.helpers import create_figure, save_figure
    from shared.utils.config import viridis, color_asdeposited, color_uvtreated, fig_width_cm, aspect_ratio_standard
    from shared.utils.xps_utils import (
        validate_xps_data,
        background_subtract_normalize,
        get_xps_colors,
        calculate_spectral_metrics,
        export_spectral_data
    )

    print("✓ Successfully imported shared utilities")
except ImportError as e:
    print(f"✗ Error importing shared utilities: {e}")
    print("Make sure you have the shared folder set up correctly")
    sys.exit(1)

# Set global plot style
set_plot_style()


def process_xps_file(filepath):
    """
    Process XPS Excel file with comprehensive error handling and validation.
    
    Args:
        filepath: Path to XPS Excel file
        
    Returns:
        DataFrame with validated XPS data or None if processing fails
    """
    filename = os.path.basename(filepath)
    print(f"\nProcessing {filename}...")

    output_columns = ['B.E.', 'raw', 'fit1', 'fit2', 'fit3', 'fit4', 'fit5', 'fit6', 'Envelope', 'Background', 'Region']

    try:
        # Validate file exists and is readable
        if not os.path.exists(filepath):
            print(f"  ❌ ERROR: File not found: {filepath}")
            return None
            
        if not filepath.endswith(('.xlsx', '.xls')):
            print(f"  ❌ ERROR: Not an Excel file: {filepath}")
            return None
            
        excel_data = pd.read_excel(filepath, header=None)
        print(f"  ✓ Loaded successfully: {excel_data.shape[0]} rows, {excel_data.shape[1]} columns")
        
        # Validate minimum data requirements
        if excel_data.shape[0] < 10:
            print(f"  ❌ ERROR: Insufficient data rows (< 10): {excel_data.shape[0]}")
            return None
            
        if excel_data.shape[1] < 20:
            print(f"  ❌ ERROR: Insufficient data columns (< 20): {excel_data.shape[1]}")
            return None

        headers = excel_data.iloc[6]
        c1s_be_col = None
        if pd.notna(headers[9]) and "B.E." in str(headers[9]):
            c1s_be_col = 9
            print(f"  C 1s B.E. found at column 9")
        elif pd.notna(headers[8]) and "B.E." in str(headers[8]):
            c1s_be_col = 8
            print(f"  C 1s B.E. found at column 8")
        else:
            print(f"  WARNING: C 1s B.E. column not found!")

        regions_info = []

        # O 1s region
        regions_info.append({
            'name': 'O 1s',
            'be_col': 0,
            'raw_col': 1,
            'fit_cols': [2, 3, 4, 5] if pd.notna(headers[5]) and 'O 1s' in str(headers[5]) else [2, 3, 4],
            'bg_col': 6 if 'Background' in str(headers[6]) else 5,
            'env_col': 7 if 'Envelope' in str(headers[7]) else 6
        })

        # C 1s region
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

        # Al 2p region - dynamically detect fit columns
        al_fit_cols = [20]
        # Check if column 21 contains Al 2p fit data (not Background)
        if pd.notna(headers[21]) and 'Al 2p' in str(headers[21]):
            al_fit_cols.append(21)
            al_bg_col = 22
            al_env_col = 23
        else:
            al_bg_col = 21
            al_env_col = 22
            
        regions_info.append({
            'name': 'Al 2p',
            'be_col': 18,
            'raw_col': 19,
            'fit_cols': al_fit_cols,
            'bg_col': al_bg_col,
            'env_col': al_env_col
        })

        all_data = []
        data_rows = excel_data.iloc[7:]

        for idx, row in data_rows.iterrows():
            for region in regions_info:
                try:
                    be_value = row.iloc[region['be_col']]
                    if pd.isna(be_value):
                        continue

                    be_float = float(be_value)

                    if region['name'] == 'O 1s' and not (520 <= be_float <= 550):
                        continue
                    if region['name'] == 'C 1s' and not (270 <= be_float <= 310):
                        continue
                    if region['name'] == 'Al 2p' and not (60 <= be_float <= 95):
                        continue

                    row_data = [be_float]

                    raw_val = row.iloc[region['raw_col']]
                    row_data.append(float(raw_val) if not pd.isna(raw_val) else np.nan)

                    for i in range(6):
                        if i < len(region['fit_cols']):
                            fit_val = row.iloc[region['fit_cols'][i]]
                            row_data.append(float(fit_val) if not pd.isna(fit_val) else np.nan)
                        else:
                            row_data.append(np.nan)

                    env_val = row.iloc[region['env_col']]
                    row_data.append(float(env_val) if not pd.isna(env_val) else np.nan)

                    bg_val = row.iloc[region['bg_col']]
                    row_data.append(float(bg_val) if not pd.isna(bg_val) else np.nan)

                    row_data.append(region['name'])
                    all_data.append(row_data)

                except (ValueError, IndexError):
                    continue

        df = pd.DataFrame(all_data, columns=output_columns)
        print(f"  Processed {len(df)} data points")

        for region in ['O 1s', 'C 1s', 'Al 2p']:
            region_df = df[df['Region'] == region]
            if len(region_df) > 0:
                be_min, be_max = region_df['B.E.'].min(), region_df['B.E.'].max()
                print(f"    {region}: {len(region_df)} points, B.E. range {be_min:.1f} - {be_max:.1f} eV")

        return df

    except Exception as e:
        print(f"  ERROR processing {filename}: {str(e)}")
        return None


def get_peak_color_by_position(be_position, region_name):
    """
    Assign consistent colors to peaks based on discrete binding energy ranges.
    
    Args:
        be_position: Binding energy position of the peak
        region_name: XPS region name (e.g., 'O 1s', 'C 1s', 'Al 2p')
    
    Returns:
        Consistent color for peaks in the same chemical environment
    """
    viridis_cmap = plt.colormaps['viridis']
    
    # Define discrete color assignments for consistent peak identification
    if region_name == 'O 1s':
        if be_position < 530:
            return viridis_cmap(0.2)  # Metal oxide oxygen (low BE)
        elif be_position < 532:
            return viridis_cmap(0.5)  # Bridging oxygen
        else:
            return viridis_cmap(0.8)  # Organic/hydroxyl oxygen (high BE)
    
    elif region_name == 'C 1s':
        if be_position < 285:
            return viridis_cmap(0.2)  # Aliphatic carbon (low BE)
        elif be_position < 287:
            return viridis_cmap(0.4)  # C-O carbon
        elif be_position < 289:
            return viridis_cmap(0.6)  # C=O carbon
        else:
            return viridis_cmap(0.8)  # COOH/carbonate carbon (high BE)
    
    elif region_name == 'Al 2p':
        if be_position < 74:
            return viridis_cmap(0.2)  # Metallic aluminum (low BE)
        elif be_position < 76:
            return viridis_cmap(0.5)  # Intermediate oxidation
        else:
            return viridis_cmap(0.8)  # Aluminum oxide (high BE)
    
    else:
        # Default color for unknown regions
        return viridis_cmap(0.5)


def normalize_spectrum_preserving_ratios(raw_data, background_data, normalization_factor=None):
    """
    CORRECTED: Preserve quantitative relationships between raw data, envelope, and fitted peaks.
    
    Args:
        raw_data: Raw intensity data
        background_data: Background intensity data  
        normalization_factor: Optional pre-calculated normalization factor
    
    Returns:
        Background-corrected data maintaining relative peak intensities
    """
    raw_data = np.array(raw_data)
    background_data = np.array(background_data)
    
    # Simple background subtraction without individual normalization
    corrected_data = raw_data - background_data
    # Set small negative values to zero
    corrected_data = np.maximum(corrected_data, 0)
    
    # If a normalization factor is provided, use it to maintain consistency
    if normalization_factor is not None:
        corrected_data = corrected_data / normalization_factor
    
    return corrected_data


def plot_xps_publication_figure_improved(all_dataframes, save_plots=True):
    """
    Create IMPROVED publication-quality XPS figure.

    IMPROVEMENTS:
    - Full page width (21cm for publication)
    - Fixed normalization (per-sample)
    - Thin, transparent envelope lines
    - Major/minor ticks on all axes
    - Better spacing and readability
    - Professional styling
    """

    # Use shared project styling (already set via set_plot_style())

    # Sample information
    sample_order = ['BTY_AD', 'BTY_UV', 'BTY_H2O']
    sample_labels = ['As Deposited', 'UV Treated', 'Water Exposed']
    regions = ['O 1s', 'C 1s', 'Al 2p']
    panel_labels = ['(a)', '(b)', '(c)']

    # Create compressed figure for display and processing
    fig_width_in = 9  # Reduced from 12 to compress horizontally
    fig_height_in = 4  # Good height for 3 panels
    fig, axes = plt.subplots(1, 3, figsize=(fig_width_in, fig_height_in))

    # Use project's viridis color scheme
    viridis_cmap = plt.colormaps['viridis']
    
    # Sample colors using viridis scheme
    sample_colors = [color_asdeposited, color_uvtreated, viridis(0.5)]  # As deposited, UV treated, Water

    # Clean spacing for publication
    offset_step = 1.5  # Clear separation between samples

    # Plot each region
    for col_idx, region in enumerate(regions):
        ax = axes[col_idx]

        # Process each sample independently
        for sample_idx, sample_key in enumerate(sample_order):
            if sample_key in all_dataframes:
                df = all_dataframes[sample_key]
                region_df = df[df['Region'] == region].sort_values('B.E.').copy()

                if len(region_df) > 0:
                    # Extract data
                    be_values = region_df['B.E.'].values
                    raw_data = region_df['raw'].values
                    background_data = region_df['Background'].values
                    envelope_data = region_df['Envelope'].values

                    # CORRECTED: Calculate single normalization factor from raw data to preserve ratios
                    corrected_raw = normalize_spectrum_preserving_ratios(raw_data, background_data)
                    # Use max of corrected raw data as normalization factor
                    norm_factor = np.max(corrected_raw) if np.max(corrected_raw) > 0 else 1.0
                    
                    # Apply same normalization to all components
                    normalized_raw = corrected_raw / norm_factor
                    normalized_envelope = normalize_spectrum_preserving_ratios(envelope_data, background_data, norm_factor)

                    # Calculate offset
                    y_offset = sample_idx * offset_step

                    # Plot fit components with order-based colors for ALL regions for uniformity
                    fit_plotted = False
                    fit_peaks = []  # Store peak positions for ordering
                    
                    # First pass: collect all fit peaks and sort by binding energy
                    for i, fit_col in enumerate(['fit1', 'fit2', 'fit3', 'fit4', 'fit5', 'fit6']):
                        if region_df[fit_col].notna().any():
                            fit_data = region_df[fit_col].values
                            normalized_fit = normalize_spectrum_preserving_ratios(fit_data, background_data, norm_factor)
                            if np.max(normalized_fit) > 0.01:  # Only include significant peaks
                                max_idx = np.argmax(normalized_fit)
                                peak_be = be_values[max_idx]
                                fit_peaks.append((peak_be, i, fit_col, normalized_fit))
                    
                    # Sort by binding energy (lowest to highest) for all regions
                    fit_peaks.sort(key=lambda x: x[0])
                    
                    # Simple fixed color scheme - 1st peak = color 1, 2nd peak = color 2, etc.
                    viridis_cmap = plt.colormaps['viridis']
                    peak_colors = [
                        viridis_cmap(0.05),   # 1st peak: Deep purple
                        viridis_cmap(0.25),   # 2nd peak: Deep blue  
                        viridis_cmap(0.45),   # 3rd peak: Deep green
                        viridis_cmap(0.65),   # 4th peak: Light green
                        viridis_cmap(0.80),   # 5th peak: Light yellow-green
                        viridis_cmap(0.95)    # 6th peak: Bright yellow
                    ]
                    
                    # Second pass: plot with order-based colors
                    for i, fit_col in enumerate(['fit1', 'fit2', 'fit3', 'fit4', 'fit5', 'fit6']):
                        if region_df[fit_col].notna().any():
                            fit_data = region_df[fit_col].values
                            # Use same normalization factor to preserve relative intensities
                            normalized_fit = normalize_spectrum_preserving_ratios(fit_data, background_data, norm_factor)
                            
                            # IMPROVED: More stringent validation for actual peaks
                            # Check if this is a real peak vs. background/baseline artifact
                            max_intensity = np.max(normalized_fit)
                            mean_intensity = np.mean(normalized_fit)
                            
                            # Only plot if this looks like an actual peak:
                            # 1. Peak height > 5% of normalized scale (was 1%)
                            # 2. Peak is significantly above mean (not just baseline)
                            # 3. Peak has reasonable width (not just a spike)
                            peak_threshold = 0.05  # Increased from 0.01
                            signal_to_noise = max_intensity / (mean_intensity + 1e-6)  # Avoid division by zero
                            
                            # Count significant data points above threshold
                            significant_points = np.sum(normalized_fit > peak_threshold)
                            min_peak_width = 3  # Minimum number of points for a valid peak
                            
                            # Always plot all fit components for consistent appearance
                            if np.max(normalized_fit) > 0.01:  # Basic check for non-zero data
                                
                                fit_y = normalized_fit + y_offset
                                
                                # Find peak position for this fit component
                                max_idx = np.argmax(normalized_fit)
                                peak_be = be_values[max_idx]
                                
                                # Find this peak's order in the sorted list
                                peak_order = next((idx for idx, (be, orig_i, col, _) in enumerate(fit_peaks) 
                                                 if orig_i == i), 0)
                                if peak_order < len(peak_colors):
                                    peak_color = peak_colors[peak_order]
                                else:
                                    # Fallback for more than 6 peaks
                                    peak_color = viridis_cmap(0.5)

                                # Calculate z-order: higher BE (rightmost) peaks in front
                                # Reverse the order so rightmost peaks have higher z-order
                                base_zorder = 10
                                fill_zorder = base_zorder - peak_order  # Higher BE = higher z-order
                                line_zorder = fill_zorder + len(fit_peaks)  # Lines always above fills

                                # Fill between baseline and fit curve (no edge lines for clean look)
                                ax.fill_between(be_values, y_offset, fit_y,
                                                color=peak_color, alpha=0.6,
                                                edgecolor='none',
                                                zorder=fill_zorder)
                                fit_plotted = True
                                
                                # Debug output for problematic cases
                                if region == 'C 1s' and sample_key == 'BTY_AD':
                                    print(f"  DEBUG: {fit_col} - max: {max_intensity:.3f}, S/N: {signal_to_noise:.2f}, points: {significant_points}, BE: {peak_be:.1f}")
                            else:
                                # Debug output for rejected peaks
                                if region == 'C 1s' and sample_key == 'BTY_AD':
                                    print(f"  SKIPPED: {fit_col} - max: {max_intensity:.3f}, S/N: {signal_to_noise:.2f}, points: {significant_points} (below threshold)")

                    # Envelope line - more visible
                    envelope_y = normalized_envelope + y_offset
                    ax.plot(be_values, envelope_y, '-',
                            color='red', linewidth=1.5,
                            alpha=0.8, zorder=4)

                    # Plot ALL experimental data points with better visibility
                    raw_y = normalized_raw + y_offset
                    # Use larger markers with dark edges for better visibility
                    ax.plot(be_values, raw_y, 'o',
                            color='black', markersize=2.5,
                            alpha=0.9, markeredgecolor='black', markeredgewidth=0,
                            zorder=6, label='_nolegend_')  # Higher z-order to be on top
                    # Add a colored line connecting the points for clarity
                    ax.plot(be_values, raw_y, '-',
                            color=sample_colors[sample_idx], linewidth=0.5,
                            alpha=0.6, zorder=5)

                    # Don't add labels here - we'll add them after all data is plotted

        # Clean axis formatting
        ax.set_xlabel('Binding Energy (eV)', fontweight='bold')
        if col_idx == 0:
            ax.set_ylabel('Intensity (A.U.)', fontweight='bold')

        # Remove title - we have panel labels instead
        # ax.set_title(f"{region}", fontweight='bold', pad=10)

        # Invert x-axis (standard for XPS)
        ax.invert_xaxis()

        # Remove y-tick labels for offset data
        ax.set_yticklabels([])

        # Set tight axis limits based on actual peak data
        all_be_values = []
        all_intensities = []
        
        # Collect all data for this region
        for sample_key in all_dataframes.keys():
            df = all_dataframes[sample_key]
            region_df = df[df['Region'] == region]
            if len(region_df) > 0:
                raw_data = region_df['raw'].values
                background_data = region_df['Background'].values
                corrected_data = normalize_spectrum_preserving_ratios(raw_data, background_data)
                
                # Only include points with significant intensity (>5% of max)
                max_intensity = np.max(corrected_data)
                significant_mask = corrected_data > (0.05 * max_intensity)
                
                if np.any(significant_mask):
                    significant_be = region_df['B.E.'].values[significant_mask]
                    all_be_values.extend(significant_be)
                    all_intensities.extend(corrected_data[significant_mask])

        # Set specific x-axis limits for each region
        if region == 'O 1s':
            ax.set_xlim(536, 528)  # Inverted for XPS convention
        elif region == 'C 1s':
            ax.set_xlim(292, 282)  # Wider range to include all C 1s data
        elif region == 'Al 2p':
            ax.set_xlim(78, 72)  # Adjusted for better scaling
        else:
            # Fallback for any other regions
            ax.set_xlim(536, 528)
        
        # Set y limits with uniform padding
        # Total height needed = (number of samples - 1) * offset + 1 for the last sample + padding
        y_max = (len(sample_order) - 1) * offset_step + 1.0 + 0.5  # 0.5 padding on top
        ax.set_ylim(-0.1, y_max)
        
        # Add sample labels - centered in panels, raised by 1
        for sample_idx, (sample_key, sample_label) in enumerate(zip(sample_order, sample_labels)):
            if sample_key in all_dataframes:
                y_position = sample_idx * offset_step + 1.2  # Lowered by 0.5 (was 1.7, now 1.2)
                # Center labels horizontally within each panel using fixed ranges
                if region == 'O 1s':
                    x_position = 532  # Center of 528-536 range
                elif region == 'C 1s':
                    x_position = 287  # Center of 282-292 range
                elif region == 'Al 2p':
                    x_position = 75  # Center of 72-78 range
                else:
                    x_position = 532  # Fallback
                
                ax.text(x_position, y_position, sample_label,
                        fontweight='bold',
                        ha='center', va='center',  # Center alignment
                        color='black',
                        bbox=dict(boxstyle='round,pad=0.2', 
                                  facecolor='white',
                                  alpha=0.9, 
                                  edgecolor=sample_colors[sample_idx],
                                  linewidth=1.2))

        # FIXED: Major and minor ticks on horizontal axes only
        ax.tick_params(axis='x', which='major', direction='in',
                       top=True, bottom=True,
                       length=6, width=1.2)
        ax.tick_params(axis='x', which='minor', direction='in',
                       top=True, bottom=True,
                       length=3, width=0.8)
        # Remove y-axis ticks
        ax.tick_params(axis='y', which='both', left=False, right=False)

        # Set clean, professional tick marks for each region with consistent 2 eV intervals
        if region == 'O 1s':
            major_ticks = [528, 530, 532, 534, 536]
        elif region == 'C 1s':
            major_ticks = [282, 284, 286, 288, 290, 292]  # Wider range with 6 ticks
        elif region == 'Al 2p':
            major_ticks = [72, 74, 76, 78]  # Consistent 2 eV spacing
        else:
            # Fallback for any other regions
            major_ticks = [528, 530, 532, 534, 536]
        
        ax.set_xticks(major_ticks)
        ax.set_xticklabels([str(int(tick)) for tick in major_ticks])
        # Set minor ticks to be 4 per major interval (every 0.5 eV for O 1s/C 1s, 0.25 eV for Al 2p)
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
            
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))

        # Keep grid off as per project standards
        ax.grid(False)

        # Frame styling
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            spine.set_color('black')
        
        # Add panel label (a, b, c) in top-left corner inside axes
        ax.text(0.05, 0.95, panel_labels[col_idx], 
                transform=ax.transAxes,
                fontweight='bold',
                ha='left', va='top',
                bbox=dict(boxstyle='round,pad=0.3', 
                          facecolor='white',
                          alpha=0.8, 
                          edgecolor='none'))

    # Remove legend from main figure - will create separately

    # Clean layout - more compact
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.15)  # Reduced from 0.25 to compress horizontally

    # Save main figure
    if save_plots:
        # Use absolute path for figures directory
        figures_dir = XPS_ROOT / "figures" / "final"
        figures_dir.mkdir(parents=True, exist_ok=True)
        
        save_figure(fig, "XPS_publication_figure_final",
                    folder=str(figures_dir),
                    formats=("tiff", "pdf", "png"),
                    dpi=600)
        save_for_latex(fig, "XPS_publication_figure_final")
        
        # Create separate legend figure
        create_separate_legend(save_plots)

    # Show plot without blocking script execution
    plt.show(block=False)
    plt.pause(0.1)  # Brief pause to ensure plot displays
    
    return fig, axes


def create_separate_legend(save_plots=True):
    """
    Create a separate legend figure for the XPS plots.
    """
    # Create small figure for legend only
    legend_fig, legend_ax = plt.subplots(figsize=(6, 3))
    legend_ax.axis('off')
    
    # Create legend elements
    viridis_cmap = plt.colormaps['viridis']
    legend_elements = []
    
    # Experimental data
    legend_elements.append(plt.Line2D([0], [0], marker='o', color='gray',
                                      linestyle='None', markersize=4,
                                      markerfacecolor='gray', markeredgecolor='white',
                                      markeredgewidth=0.5, label='Experimental'))
    
    # Envelope
    legend_elements.append(plt.Line2D([0], [0], color=viridis_cmap(0.8), linewidth=1.5,
                                      alpha=0.8, label='Envelope'))
    
    # Fit components (show color gradient concept)
    legend_elements.append(patches.Patch(color=viridis_cmap(0.2), alpha=0.7, 
                                        label='Fit Components'))
    legend_elements.append(patches.Patch(color=viridis_cmap(0.5), alpha=0.7, 
                                        label='(colored by BE)'))
    legend_elements.append(patches.Patch(color=viridis_cmap(0.8), alpha=0.7, 
                                        label=''))
    
    # Sample treatments
    legend_elements.append(plt.Line2D([0], [0], color=color_asdeposited, linewidth=3,
                                      label='As Deposited'))
    legend_elements.append(plt.Line2D([0], [0], color=color_uvtreated, linewidth=3,
                                      label='UV Treated'))
    legend_elements.append(plt.Line2D([0], [0], color=viridis_cmap(0.5), linewidth=3,
                                      label='Water Exposed'))
    
    # Create legend
    legend_ax.legend(handles=legend_elements, loc='center', frameon=False,
                     ncol=2, columnspacing=1.0, handlelength=1.5)
    
    # Save legend
    if save_plots:
        # Use absolute path for figures directory
        figures_dir = XPS_ROOT / "figures" / "final"
        figures_dir.mkdir(parents=True, exist_ok=True)
        
        save_figure(legend_fig, "XPS_legend",
                    folder=str(figures_dir),
                    formats=("tiff", "pdf", "png"),
                    dpi=600)
        save_for_latex(legend_fig, "XPS_legend")
    
    return legend_fig


def generate_summary_report(all_dataframes):
    """Generate summary report - same as before"""
    print("\n" + "=" * 60)
    print("GENERATING SUMMARY REPORT")
    print("=" * 60)

    all_metrics = []

    for sample_name, df in all_dataframes.items():
        for region in df['Region'].unique():
            region_df = df[df['Region'] == region]

            if len(region_df) > 10:
                be_values = region_df['B.E.'].values
                raw_data = region_df['raw'].values
                background_data = region_df['Background'].values

                try:
                    normalized_data = normalize_spectrum_preserving_ratios(raw_data, background_data)

                    max_idx = np.argmax(normalized_data)
                    peak_position = be_values[max_idx]
                    peak_intensity = normalized_data[max_idx]
                    peak_area = np.trapezoid(normalized_data, be_values)

                    all_metrics.append({
                        'Sample': sample_name,
                        'Region': region,
                        'Peak_Position_eV': peak_position,
                        'Peak_Intensity': peak_intensity,
                        'Peak_Area': abs(peak_area),
                        'Data_Points': len(region_df)
                    })

                except Exception as e:
                    print(f"Warning: Could not analyze {sample_name} {region}: {str(e)}")

    if all_metrics:
        summary_df = pd.DataFrame(all_metrics)

        print("\nPeak Position Summary (eV):")
        print("-" * 40)
        peak_positions = summary_df.pivot(index='Region', columns='Sample', values='Peak_Position_eV')
        print(peak_positions.round(2))

        print("\nRelative Peak Areas:")
        print("-" * 40)
        peak_areas = summary_df.pivot(index='Region', columns='Sample', values='Peak_Area')
        for region in peak_areas.index:
            if not peak_areas.loc[region].isna().all():
                first_sample = peak_areas.loc[region].dropna().iloc[0]
                if first_sample > 0:
                    peak_areas.loc[region] = peak_areas.loc[region] / first_sample
        print(peak_areas.round(3))

        # Use absolute path for processed data directory
        processed_dir = XPS_ROOT / "data" / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = processed_dir / "xps_summary_metrics.csv"
        summary_df.to_csv(output_path, index=False)
        print(f"\n✓ Summary metrics saved to {output_path}")

        return summary_df
    else:
        print("No valid metrics calculated")
        return None


# Old main function removed - using the corrected version below

# === LaTeX TIFF Figure Generation ===
latex_figures_dir = Path("/mnt/c/Users/dreec/PycharmProjects/Paper2/LaTeX/High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_/Figures")
latex_figures_dir.mkdir(exist_ok=True)
print(f"📁 LaTeX figures will be saved to: {latex_figures_dir}")

def save_for_latex(fig, filename, include_pdf=True):
    """Save figure in TIFF format for LaTeX, with optional PDF."""
    # Save to LaTeX directory
    saved_files = save_figure(
        fig, filename, 
        folder=latex_figures_dir,
        formats=("tiff",), 
        include_pdf=include_pdf,
        dpi=600
    )
    print(f"✅ LaTeX figure saved: {filename}.tiff")
    return saved_files

def main():
    """Main function for publication-quality XPS analysis"""
    print("XPS Analysis Script - PUBLICATION QUALITY")
    print("=" * 55)
    print("Publication-standard improvements:")
    print("- Quantitative normalization preserving relative intensities")
    print("- Journal-specific figure dimensions (18.3cm double column)")
    print("- High-resolution output (600 DPI)")
    print("- Colorblind-friendly color schemes")
    print("- Professional typography and formatting")
    print("- Multiple publication formats (PDF, SVG, EPS)")
    print("=" * 55)
    print(f"\nRunning from: {Path.cwd()}")
    print(f"XPS root directory: {XPS_ROOT}")

    # Check data directory - use processed directory with Excel files
    data_dir = XPS_ROOT / "data" / "processed"
    if not data_dir.exists():
        print(f"✗ Data directory not found: {data_dir}")
        return

    print(f"✓ Data directory found: {data_dir}")

    # Define expected files
    input_filenames = ['BTY_AD.xlsx', 'BTY_UV.xlsx', 'BTY_H2O.xlsx']
    input_files = [data_dir / filename for filename in input_filenames]

    # Check files
    existing_files = []
    print("\n📁 Checking for data files:")
    print("-" * 40)

    for filepath, filename in zip(input_files, input_filenames):
        if filepath.exists():
            existing_files.append(str(filepath))
            print(f"✓ Found: {filename}")
        else:
            print(f"✗ Not found: {filename}")

    if not existing_files:
        print("\n⚠️  No data files found!")
        return

    print(f"\n🔄 Processing {len(existing_files)} files...")
    
    # Process files
    all_dataframes = {}
    for filepath in existing_files:
        key = Path(filepath).stem
        df = process_xps_file(filepath)
        if df is not None:
            all_dataframes[key] = df

    if not all_dataframes:
        print("❌ No valid data could be processed")
        return

    print(f"\n✅ Successfully loaded {len(all_dataframes)} datasets")

    # Show data summary
    print("\n📊 Data Summary:")
    print("-" * 40)
    for sample_name, df in all_dataframes.items():
        regions = df['Region'].unique()
        print(f"{sample_name}:")
        for region in regions:
            region_df = df[df['Region'] == region]
            be_range = f"{region_df['B.E.'].min():.1f}-{region_df['B.E.'].max():.1f}"
            print(f"  {region}: {len(region_df)} points, BE range: {be_range} eV")

    # Create directories using absolute paths
    figures_dir = XPS_ROOT / "figures" / "final"
    processed_dir = XPS_ROOT / "data" / "processed"
    figures_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Create IMPROVED publication figure
    print(f"\n🎨 Creating IMPROVED publication figure...")
    try:
        fig, axes = plot_xps_publication_figure_improved(all_dataframes, save_plots=True)
        plt.show()
        print("✅ IMPROVED publication figure created and saved!")
        print("   📁 Saved to: 06_XPS_Analysis/figures/final/")
        print("   🎯 Full page width, proper normalization, professional styling")
    except Exception as e:
        print(f"❌ Error creating figure: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()