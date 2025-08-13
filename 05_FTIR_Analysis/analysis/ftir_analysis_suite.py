#!/usr/bin/env python3
"""
FTIR Analysis Suite - Professional spectroscopic analysis
Command-line interface for batch processing and reproducible analysis
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime
import jcamp

import matplotlib.pyplot as plt

# Set publication-quality plot style
def set_plot_style():
    """Set publication-quality matplotlib style"""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'font.size': 10,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'grid.alpha': 0.3
    })

def create_figure(rows=1, cols=1, width_cm=18, aspect_ratio=4/3):
    """Create figure with specified dimensions"""
    width_in = width_cm / 2.54
    height_in = width_in / aspect_ratio
    figsize = (width_in, height_in)
    return plt.subplots(rows, cols, figsize=figsize, constrained_layout=True)

def save_figure(fig, filename, folder="../figures/final/", include_pdf=False, include_png=False, dpi=300):
    """Save figure in multiple formats"""
    from pathlib import Path
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Always save as TIFF (publication quality)
    fig.savefig(folder_path / f"{filename}.tiff", dpi=dpi, bbox_inches='tight')
    
    if include_pdf:
        fig.savefig(folder_path / f"{filename}.pdf", bbox_inches='tight')
    if include_png:
        fig.savefig(folder_path / f"{filename}.png", dpi=dpi, bbox_inches='tight')
    
    print(f"💾 Saved figure: {filename}")

# Global constants
ORGANIC_COMPOUNDS = ['EG', 'CB', 'BTY', 'THB', 'MPD', 'DHB']
INORGANIC_MATERIALS = ['Al', 'Zn']

# Advanced analysis imports
try:
    import lmfit
    from lmfit.models import GaussianModel, VoigtModel, LorentzianModel
    LMFIT_AVAILABLE = True
except ImportError:
    LMFIT_AVAILABLE = False
    
try:
    import pybaselines
    PYBASELINES_AVAILABLE = True
except ImportError:
    PYBASELINES_AVAILABLE = False

class FTIRAnalysisSuite:
    """Professional FTIR analysis with batch processing capabilities"""
    
    def __init__(self):
        self.wavenumbers = None
        self.intensities = None
        self.corrected_intensities = None
        self.baseline = None
        self.peaks = []
        self.fit_result = None
        self.metadata = {}
        
    def load_jdx_file(self, file_path):
        """Load JDX file and extract metadata"""
        try:
            data = jcamp.jcamp_readfile(file_path)
            self.wavenumbers = np.array(data['x'])
            self.intensities = np.array(data['y'])
            self.metadata = {k: v for k, v in data.items() if k not in ['x', 'y']}
            
            # Sort by wavenumber if needed
            if len(self.wavenumbers) > 1 and self.wavenumbers[0] > self.wavenumbers[-1]:
                self.wavenumbers = self.wavenumbers[::-1]
                self.intensities = self.intensities[::-1]
                
            print(f"✅ Loaded {file_path}: {len(self.wavenumbers)} points, "
                  f"range {self.wavenumbers.min():.0f}-{self.wavenumbers.max():.0f} cm⁻¹")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load {file_path}: {e}")
            return False
            
    def apply_baseline_correction(self, method='als', **kwargs):
        """Apply baseline correction with multiple algorithms"""
        if not PYBASELINES_AVAILABLE:
            print("⚠️ pybaselines not available, using raw data")
            self.corrected_intensities = self.intensities.copy()
            return
            
        try:
            baseline_fitter = pybaselines.Baseline(self.wavenumbers)
            
            if method == 'als':
                self.baseline, params = baseline_fitter.asls(
                    self.intensities, 
                    lam=kwargs.get('lambda', 1e4),
                    p=kwargs.get('p', 0.01)
                )
                print(f"✅ Applied ALS baseline correction (λ={kwargs.get('lambda', 1e4):.0e})")
                
            elif method == 'arpls':
                self.baseline, params = baseline_fitter.arpls(
                    self.intensities,
                    lam=kwargs.get('lambda', 1e5)
                )
                print(f"✅ Applied ARPLS baseline correction")
                
            elif method == 'whittaker':
                self.baseline, params = baseline_fitter.whittaker(
                    self.intensities,
                    lam=kwargs.get('lambda', 1e3)
                )
                print(f"✅ Applied Whittaker baseline correction")
                
            elif method == 'polynomial':
                self.baseline, params = baseline_fitter.poly(
                    self.intensities,
                    poly_order=kwargs.get('order', 3)
                )
                print(f"✅ Applied polynomial baseline correction (order {kwargs.get('order', 3)})")
                
            self.corrected_intensities = self.intensities - self.baseline
            
        except Exception as e:
            print(f"❌ Baseline correction failed: {e}")
            self.corrected_intensities = self.intensities.copy()
            
    def normalize_spectrum(self, data=None):
        """Normalize spectrum to 0-1 range"""
        if data is None:
            data = self.corrected_intensities
        return (data - data.min()) / (data.max() - data.min())
        
    def detect_peaks_automatically(self, height_threshold=0.1, prominence_threshold=0.05):
        """Automatically detect peaks using scipy"""
        try:
            from scipy.signal import find_peaks
            
            normalized = self.normalize_spectrum()
            peaks_idx, properties = find_peaks(
                normalized,
                height=height_threshold,
                prominence=prominence_threshold,
                width=2,
                distance=10
            )
            
            detected_peaks = []
            for idx in peaks_idx:
                detected_peaks.append({
                    'wavenumber': self.wavenumbers[idx],
                    'intensity': normalized[idx],
                    'prominence': properties['prominences'][list(peaks_idx).index(idx)]
                })
                
            # Sort by prominence (most prominent first)
            detected_peaks.sort(key=lambda x: x['prominence'], reverse=True)
            
            print(f"🎯 Auto-detected {len(detected_peaks)} peaks")
            for i, peak in enumerate(detected_peaks[:10]):  # Show top 10
                print(f"  {i+1}. {peak['wavenumber']:.1f} cm⁻¹ (prominence: {peak['prominence']:.3f})")
                
            return detected_peaks
            
        except ImportError:
            print("⚠️ scipy not available for peak detection")
            return []
            
    def fit_peaks_with_lmfit(self, peak_positions, model_type='gaussian', constraints=None):
        """Fit multiple peaks with advanced models"""
        if not LMFIT_AVAILABLE:
            print("❌ lmfit not available for peak fitting")
            return None
            
        print(f"🔧 Fitting {len(peak_positions)} peaks with {model_type} model...")
        
        # Create composite model
        model = None
        params = None
        
        for i, pos in enumerate(peak_positions):
            prefix = f'peak{i}_'
            
            if model_type == 'gaussian':
                peak_model = GaussianModel(prefix=prefix)
            elif model_type == 'voigt':
                peak_model = VoigtModel(prefix=prefix)
            elif model_type == 'lorentzian':
                peak_model = LorentzianModel(prefix=prefix)
            else:
                peak_model = GaussianModel(prefix=prefix)
                
            if model is None:
                model = peak_model
                params = peak_model.make_params()
            else:
                model += peak_model
                params.update(peak_model.make_params())
                
            # Set initial parameters
            idx = np.argmin(np.abs(self.wavenumbers - pos))
            height = self.corrected_intensities[idx]
            
            params[f'{prefix}center'].set(value=pos, min=pos-30, max=pos+30)
            params[f'{prefix}height'].set(value=height, min=0, max=2*height)
            params[f'{prefix}sigma'].set(value=10, min=2, max=50)
            
            # Apply constraints if provided
            if constraints and i < len(constraints):
                constraint = constraints[i]
                if 'center_range' in constraint:
                    cmin, cmax = constraint['center_range']
                    params[f'{prefix}center'].set(min=cmin, max=cmax)
                if 'width_range' in constraint:
                    wmin, wmax = constraint['width_range']
                    params[f'{prefix}sigma'].set(min=wmin, max=wmax)
                    
        # Fit the model
        try:
            result = model.fit(self.corrected_intensities, params, x=self.wavenumbers)
            self.fit_result = result
            
            # Calculate fit statistics
            r_squared = 1 - result.residual.var() / np.var(self.corrected_intensities)
            
            print(f"✅ Peak fitting completed:")
            print(f"   R² = {r_squared:.4f}")
            print(f"   χ² = {result.chisqr:.2e}")
            print(f"   Reduced χ² = {result.redchi:.4f}")
            
            # Print peak parameters
            print(f"\\n📊 Peak Parameters:")
            for name, param in result.params.items():
                if 'center' in name and param.stderr:
                    peak_num = name.split('_')[0]
                    sigma_name = name.replace('center', 'sigma')
                    height_name = name.replace('center', 'height')
                    
                    center = param.value
                    center_err = param.stderr
                    width = result.params[sigma_name].value
                    height = result.params[height_name].value
                    area = height * width * np.sqrt(2 * np.pi)  # Gaussian area
                    
                    print(f"   {peak_num}: {center:.1f} ± {center_err:.1f} cm⁻¹ "
                          f"(width: {width:.1f}, area: {area:.2f})")
                          
            return result
            
        except Exception as e:
            print(f"❌ Peak fitting failed: {e}")
            return None
            
    def create_analysis_plot(self, save_path=None):
        """Create comprehensive analysis plot"""
        set_plot_style()
        
        fig, ((ax1, ax2), (ax3, ax4)) = create_figure(rows=2, cols=2, width_cm=18, aspect_ratio=1.2)
        
        # Plot 1: Raw vs corrected spectrum
        if self.corrected_intensities is not None:
            raw_norm = self.normalize_spectrum(self.intensities)
            corr_norm = self.normalize_spectrum(self.corrected_intensities)
            
            ax1.plot(self.wavenumbers, raw_norm, 'lightblue', alpha=0.7, label='Raw')
            ax1.plot(self.wavenumbers, corr_norm, 'blue', linewidth=2, label='Corrected')
            if self.baseline is not None:
                baseline_norm = self.normalize_spectrum(self.baseline)
                ax1.plot(self.wavenumbers, baseline_norm, 'red', alpha=0.5, label='Baseline')
                
        ax1.set_xlim(4000, 400)
        ax1.set_xlabel('Wavenumber (cm⁻¹)')
        ax1.set_ylabel('Normalized Absorbance')
        ax1.set_title('Baseline Correction')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.invert_xaxis()
        
        # Plot 2: Peak fitting results
        if self.corrected_intensities is not None:
            corr_norm = self.normalize_spectrum(self.corrected_intensities)
            ax2.plot(self.wavenumbers, corr_norm, 'blue', linewidth=2, label='Data')
            
            if self.fit_result is not None:
                fitted_norm = self.normalize_spectrum(self.fit_result.best_fit)
                ax2.plot(self.wavenumbers, fitted_norm, 'red', linestyle='--', 
                        linewidth=2, label='Fitted')
                
                # Plot individual components
                components = self.fit_result.eval_components()
                colors = plt.cm.Set3(np.linspace(0, 1, len(components)))
                for i, (name, comp) in enumerate(components.items()):
                    comp_norm = self.normalize_spectrum(comp)
                    ax2.plot(self.wavenumbers, comp_norm, color=colors[i], 
                            linestyle=':', alpha=0.8, label=f'{name}')
                            
        ax2.set_xlim(4000, 400)
        ax2.set_xlabel('Wavenumber (cm⁻¹)')
        ax2.set_ylabel('Normalized Absorbance')
        ax2.set_title('Peak Fitting Results')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.invert_xaxis()
        
        # Plot 3: Residuals
        if self.fit_result is not None:
            residuals = self.fit_result.residual
            ax3.plot(self.wavenumbers, residuals, 'gray', alpha=0.7)
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax3.set_xlim(4000, 400)
            ax3.set_xlabel('Wavenumber (cm⁻¹)')
            ax3.set_ylabel('Residuals')
            ax3.set_title('Fit Residuals')
            ax3.grid(True, alpha=0.3)
            ax3.invert_xaxis()
        
        # Plot 4: Peak parameters (if available)
        if self.fit_result is not None:
            peak_centers = []
            peak_errors = []
            peak_labels = []
            
            for name, param in self.fit_result.params.items():
                if 'center' in name and param.stderr:
                    peak_centers.append(param.value)
                    peak_errors.append(param.stderr)
                    peak_labels.append(name.split('_')[0])
                    
            if peak_centers:
                x_pos = np.arange(len(peak_centers))
                ax4.errorbar(x_pos, peak_centers, yerr=peak_errors, 
                           fmt='o', capsize=5, capthick=2)
                ax4.set_xticks(x_pos)
                ax4.set_xticklabels(peak_labels)
                ax4.set_ylabel('Peak Center (cm⁻¹)')
                ax4.set_title('Peak Positions with Uncertainties')
                ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            save_figure(fig, save_path, include_pdf=True, include_png=True)
            print(f"💾 Saved analysis plot to {save_path}")
            
        return fig
        
    def export_results(self, output_path):
        """Export comprehensive analysis results"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'metadata': self.metadata,
            'data_info': {
                'num_points': len(self.wavenumbers) if self.wavenumbers is not None else 0,
                'wavenumber_range': [float(self.wavenumbers.min()), float(self.wavenumbers.max())] 
                                   if self.wavenumbers is not None else None
            }
        }
        
        if self.fit_result is not None:
            results['fit_statistics'] = {
                'r_squared': float(1 - self.fit_result.residual.var() / np.var(self.corrected_intensities)),
                'chi_squared': float(self.fit_result.chisqr),
                'reduced_chi_squared': float(self.fit_result.redchi),
                'num_parameters': len(self.fit_result.params)
            }
            
            results['peak_parameters'] = {}
            for name, param in self.fit_result.params.items():
                results['peak_parameters'][name] = {
                    'value': float(param.value),
                    'stderr': float(param.stderr) if param.stderr else None,
                    'min': float(param.min) if param.min is not None else None,
                    'max': float(param.max) if param.max is not None else None
                }
                
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"💾 Exported results to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Professional FTIR Analysis Suite")
    parser.add_argument("input_file", help="JDX file to analyze")
    parser.add_argument("--baseline", choices=['als', 'arpls', 'whittaker', 'polynomial'], 
                       default='als', help="Baseline correction method")
    parser.add_argument("--peaks", nargs='+', type=float, 
                       help="Manual peak positions (cm⁻¹)")
    parser.add_argument("--auto-peaks", action='store_true', 
                       help="Automatically detect peaks")
    parser.add_argument("--model", choices=['gaussian', 'voigt', 'lorentzian'], 
                       default='gaussian', help="Peak model type")
    parser.add_argument("--output", help="Output file prefix")
    parser.add_argument("--plot", action='store_true', help="Create analysis plot")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = FTIRAnalysisSuite()
    
    # Load data
    if not analyzer.load_jdx_file(args.input_file):
        return 1
        
    # Apply baseline correction
    analyzer.apply_baseline_correction(args.baseline)
    
    # Peak detection/fitting
    peak_positions = []
    
    if args.auto_peaks:
        detected = analyzer.detect_peaks_automatically()
        peak_positions = [p['wavenumber'] for p in detected[:10]]  # Top 10 peaks
        
    if args.peaks:
        peak_positions.extend(args.peaks)
        
    if peak_positions:
        analyzer.fit_peaks_with_lmfit(peak_positions, args.model)
        
    # Generate outputs
    if args.output:
        output_prefix = args.output
    else:
        input_path = Path(args.input_file)
        output_prefix = f"analysis_{input_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Export results
    analyzer.export_results(f"{output_prefix}.json")
    
    # Create plot
    if args.plot or not args.output:  # Default to creating plot
        analyzer.create_analysis_plot(output_prefix)
        
    print(f"\\n✅ Analysis complete! Files saved with prefix: {output_prefix}")
    
if __name__ == "__main__":
    sys.exit(main())