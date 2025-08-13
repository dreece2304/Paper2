# shared/utils/xps_utils.py
"""
XPS-specific utility functions for data processing and plotting.
UPDATED: Fixed numpy.trapz deprecation warnings
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
import warnings


def validate_xps_data(df, region_name):
    """
    Validate XPS data for a specific region.

    Args:
        df: DataFrame containing XPS data
        region_name: Name of the XPS region (e.g., 'O 1s', 'C 1s', 'Al 2p')

    Returns:
        bool: True if data is valid
    """
    required_columns = ['B.E.', 'raw', 'Background', 'Envelope', 'Region']

    # Check if required columns exist
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        warnings.warn(f"Missing columns for {region_name}: {missing_cols}")
        return False

    # Filter data for the region
    region_df = df[df['Region'] == region_name]
    if len(region_df) == 0:
        warnings.warn(f"No data found for region: {region_name}")
        return False

    # Check for reasonable binding energy ranges
    be_ranges = {
        'O 1s': (520, 550),
        'C 1s': (270, 310),
        'Al 2p': (60, 95),
        'Zn 2p': (1010, 1060),
        'N 1s': (390, 410),
        'Si 2p': (95, 110)
    }

    if region_name in be_ranges:
        be_min, be_max = be_ranges[region_name]
        region_be = region_df['B.E.']
        if not ((region_be >= be_min) & (region_be <= be_max)).any():
            warnings.warn(f"Binding energies for {region_name} outside expected range {be_ranges[region_name]}")
            return False

    return True


def background_subtract_normalize(raw_data, background_data, method='minmax'):
    """
    Perform background subtraction and normalization of XPS data.

    Args:
        raw_data: Raw intensity data (array-like)
        background_data: Background intensity data (array-like)
        method: Normalization method ('minmax', 'max', 'area')

    Returns:
        normalized_data: Background-subtracted and normalized data
    """
    # Convert to numpy arrays
    raw_data = np.array(raw_data)
    background_data = np.array(background_data)

    # Background subtraction
    corrected_data = raw_data - background_data

    # Handle negative values (set to small positive value to avoid log issues)
    corrected_data = np.maximum(corrected_data, 0.001 * np.max(corrected_data))

    # Normalization
    if method == 'minmax':
        data_min = np.min(corrected_data)
        data_max = np.max(corrected_data)
        if data_max > data_min:
            normalized_data = (corrected_data - data_min) / (data_max - data_min)
        else:
            normalized_data = np.zeros_like(corrected_data)

    elif method == 'max':
        data_max = np.max(corrected_data)
        if data_max > 0:
            normalized_data = corrected_data / data_max
        else:
            normalized_data = np.zeros_like(corrected_data)

    elif method == 'area':
        data_area = np.trapezoid(corrected_data)  # FIXED: Updated from trapz
        if data_area > 0:
            normalized_data = corrected_data / data_area
        else:
            normalized_data = np.zeros_like(corrected_data)

    else:
        raise ValueError(f"Unknown normalization method: {method}")

    return normalized_data


def get_xps_colors(n_fits=6, colormap='viridis'):
    """
    Generate consistent colors for XPS fit components.

    Args:
        n_fits: Number of fit components
        colormap: Matplotlib colormap name

    Returns:
        list: List of color hex codes
    """
    cmap = plt.colormaps[colormap]
    if n_fits == 1:
        colors = [cmap(0.5)]
    else:
        colors = [cmap(i / (n_fits - 1)) for i in range(n_fits)]

    return [to_hex(color) for color in colors]


def calculate_spectral_metrics(be_values, intensity_values):
    """
    Calculate useful spectral metrics for XPS peaks.

    Args:
        be_values: Binding energy values
        intensity_values: Intensity values

    Returns:
        dict: Dictionary containing spectral metrics
    """
    # Find peak position (maximum intensity)
    max_idx = np.argmax(intensity_values)
    peak_position = be_values[max_idx]
    peak_intensity = intensity_values[max_idx]

    # Calculate peak area (trapezoidal integration) - FIXED: Updated from trapz
    peak_area = np.trapezoid(intensity_values, be_values)

    # Calculate FWHM (Full Width at Half Maximum)
    half_max = peak_intensity / 2
    indices_above_half_max = np.where(intensity_values >= half_max)[0]

    if len(indices_above_half_max) > 1:
        fwhm = be_values[indices_above_half_max[-1]] - be_values[indices_above_half_max[0]]
    else:
        fwhm = np.nan

    # Calculate centroid (intensity-weighted average) - FIXED: Updated from trapz
    if peak_area > 0:
        centroid = np.trapezoid(be_values * intensity_values, be_values) / peak_area
    else:
        centroid = np.nan

    return {
        'peak_position': peak_position,
        'peak_intensity': peak_intensity,
        'peak_area': peak_area,
        'fwhm': fwhm,
        'centroid': centroid
    }


def export_spectral_data(dataframes_dict, output_dir='../data/processed/'):
    """
    Export processed XPS data to CSV files for further analysis.

    Args:
        dataframes_dict: Dictionary of {sample_name: DataFrame} containing XPS data
        output_dir: Directory to save processed data
    """
    import os

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for sample_name, df in dataframes_dict.items():
        # Save raw data
        output_file = os.path.join(output_dir, f"{sample_name}_processed.csv")
        df.to_csv(output_file, index=False)
        print(f"✓ Saved processed data: {output_file}")

        # Calculate and save spectral metrics
        metrics_data = []
        for region in df['Region'].unique():
            region_df = df[df['Region'] == region]
            if len(region_df) > 0:
                be_values = region_df['B.E.'].values
                raw_data = region_df['raw'].values
                background_data = region_df['Background'].values

                # Background-corrected data
                corrected_data = background_subtract_normalize(raw_data, background_data, method='max')

                # Calculate metrics
                metrics = calculate_spectral_metrics(be_values, corrected_data)
                metrics['Sample'] = sample_name
                metrics['Region'] = region
                metrics_data.append(metrics)

        # Save metrics
        if metrics_data:
            metrics_df = pd.DataFrame(metrics_data)
            metrics_file = os.path.join(output_dir, f"{sample_name}_metrics.csv")
            metrics_df.to_csv(metrics_file, index=False)
            print(f"✓ Saved spectral metrics: {metrics_file}")