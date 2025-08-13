#!/usr/bin/env python3
"""
Interactive FTIR spectrum viewer for peak identification
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('QtAgg')  # Use Qt backend (works with both Qt5 and Qt6)

import matplotlib.pyplot as plt
import pandas as pd
import json
import os

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def create_interactive_viewer():
    """Create interactive plot with hover functionality"""
    
    # Load FTIR data
    data_file = "../data/processed/BTYFTIR_Final.xlsx"
    if not os.path.exists(data_file):
        print(f"❌ File not found: {data_file}")
        return
    
    print(f"✅ Loading data from: {data_file}")
    ftir_data = pd.read_excel(data_file, header=None)
    ftir_data.columns = ['Wavenumber_AsDep', 'Intensity_AsDep', 
                         'Wavenumber_UV', 'Intensity_UV']
    
    # Extract arrays
    x_asdep = ftir_data['Wavenumber_AsDep'].dropna().values
    y_asdep = ftir_data['Intensity_AsDep'].dropna().values
    x_uv = ftir_data['Wavenumber_UV'].dropna().values
    y_uv = ftir_data['Intensity_UV'].dropna().values
    
    # Normalize data
    y_asdep = (y_asdep - y_asdep.min()) / (y_asdep.max() - y_asdep.min())
    y_uv = (y_uv - y_uv.min()) / (y_uv.max() - y_uv.min())
    
    # Load JSON peaks
    json_file = "../outputs/ftir_peaks_changes.json"
    peaks_data = {}
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            peaks_data = data.get('peaks', {})
    
    # Create interactive plot
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Plot spectra with offset
    offset = 1.2
    line_asdep, = ax.plot(x_asdep, y_asdep + offset, 'b-', linewidth=1.5, 
                          label='As-deposited', alpha=0.8)
    line_uv, = ax.plot(x_uv, y_uv, 'r-', linewidth=1.5, 
                       label='UV-exposed', alpha=0.8)
    
    # Add baseline references
    ax.axhline(y=offset, color='blue', linestyle=':', alpha=0.3)
    ax.axhline(y=0, color='red', linestyle=':', alpha=0.3)
    
    # Mark peaks from JSON with labels
    peak_info = []
    for peak_wn, peak_data in peaks_data.items():
        try:
            wn = float(peak_wn)
            # Find closest point in spectrum
            idx_asdep = np.argmin(np.abs(x_asdep - wn))
            idx_uv = np.argmin(np.abs(x_uv - wn))
            
            # Plot markers
            ax.plot(wn, y_asdep[idx_asdep] + offset, 'bo', markersize=5, alpha=0.7)
            ax.plot(wn, y_uv[idx_uv], 'ro', markersize=5, alpha=0.7)
            
            # Store peak info for hover detection
            peak_info.append({
                'wn': wn,
                'label': peak_data.get('label', f'Peak {peak_wn}'),
                'asdep_int': peak_data.get('measured_asdep', 0),
                'uv_int': peak_data.get('measured_uv', 0),
                'change': peak_data.get('change_percent', 0)
            })
            
        except (ValueError, IndexError):
            continue
    
    # Set up the plot
    ax.set_xlim(4000, 400)
    ax.set_ylim(-0.2, 2.5)
    ax.set_xlabel('Wavenumber (cm⁻¹)', fontsize=12)
    ax.set_ylabel('Normalized Absorbance', fontsize=12)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Add region markers for reference
    regions = [
        (3500, 2.3, "O-H", "lightblue"),
        (2900, 2.3, "C-H", "lightgreen"), 
        (2200, 2.3, "C≡C", "lightyellow"),
        (1600, 2.3, "C=C", "lightcoral"),
        (1200, 2.3, "Al-O-C", "lightpink"),
        (700, 2.3, "Al-O", "lightgray")
    ]
    
    for x, y, label, color in regions:
        ax.text(x, y, label, fontsize=10, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7))
    
    # Add hover functionality
    def on_hover(event):
        if event.inaxes == ax and event.xdata is not None:
            x_pos = event.xdata
            
            # Find closest wavenumber in both spectra
            idx_asdep = np.argmin(np.abs(x_asdep - x_pos))
            idx_uv = np.argmin(np.abs(x_uv - x_pos))
            
            # Get intensities at cursor position
            int_asdep = y_asdep[idx_asdep]
            int_uv = y_uv[idx_uv]
            
            # Check if near any marked peaks (within 30 cm⁻¹)
            nearest_peak = None
            min_dist = float('inf')
            for peak in peak_info:
                dist = abs(peak['wn'] - x_pos)
                if dist < min_dist and dist < 30:
                    min_dist = dist
                    nearest_peak = peak
            
            # Update title with coordinates and peak info
            if nearest_peak:
                title = (f"Wavenumber: {x_pos:.0f} cm⁻¹ | Intensity: As-dep={int_asdep:.3f}, UV={int_uv:.3f} | "
                        f"PEAK: {nearest_peak['wn']:.0f} cm⁻¹ ({nearest_peak['label']}) "
                        f"Change: {nearest_peak['change']:.1f}%")
            else:
                title = f"Wavenumber: {x_pos:.0f} cm⁻¹ | Intensity: As-dep={int_asdep:.3f}, UV={int_uv:.3f}"
            
            ax.set_title(title, fontsize=10)
            fig.canvas.draw_idle()
    
    # Connect hover event
    fig.canvas.mpl_connect('motion_notify_event', on_hover)
    
    # Set initial title
    ax.set_title('Interactive FTIR Peak Viewer - Hover to see wavenumber and peak info', fontsize=12)
    
    # Print instructions and peak list
    print("\n" + "="*80)
    print("INTERACTIVE FTIR PEAK VIEWER")
    print("="*80)
    print("• Hover over the plot to see wavenumber and intensity values")
    print("• Blue circles: As-deposited peaks | Red circles: UV-exposed peaks")
    print("• When hovering near a marked peak, its info will be displayed")
    print("• Use this to verify which peaks you actually observe")
    print("• Close the plot window when finished")
    print("="*80)
    
    # Print current peak list for reference
    print(f"\nCURRENT PEAKS IN JSON ({len(peak_info)} total):")
    print(f"{'Wavenumber':<12} {'Label':<20} {'As-dep':<8} {'UV':<8} {'Change%':<8}")
    print("-" * 65)
    
    sorted_peaks = sorted(peak_info, key=lambda x: x['wn'], reverse=True)
    for peak in sorted_peaks:
        print(f"{peak['wn']:<12.0f} {peak['label']:<20} {peak['asdep_int']:<8.3f} "
              f"{peak['uv_int']:<8.3f} {peak['change']:<8.1f}")
    
    print("="*80)
    
    # Show the plot
    plt.tight_layout()
    plt.show()
    
    print("\n✅ Plot closed. Now you can tell me which peaks you actually observe!")
    return sorted_peaks

if __name__ == "__main__":
    create_interactive_viewer()