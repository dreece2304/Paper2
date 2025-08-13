#!/usr/bin/env python3
"""
Professional FTIR Analysis Web App
Interactive peak fitting with baseline correction and publication-quality output
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import jcamp
from pathlib import Path
import json
from datetime import datetime
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

# Global constants
ORGANIC_COMPOUNDS = ['EG', 'CB', 'BTY', 'THB', 'MPD', 'DHB']
INORGANIC_MATERIALS = ['Al', 'Zn']
FIG_WIDTH_CM = 18

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

# Page configuration
st.set_page_config(
    page_title="FTIR Analysis Suite",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

class FTIRAnalyzer:
    """Professional FTIR analysis with advanced peak fitting"""
    
    def __init__(self):
        self.wavenumbers = None
        self.intensities = None
        self.corrected_intensities = None
        self.peaks = []
        self.baseline = None
        
    def load_jdx_file(self, file_path):
        """Load JDX file using jcamp library"""
        try:
            data = jcamp.jcamp_readfile(file_path)
            self.wavenumbers = np.array(data['x'])
            self.intensities = np.array(data['y'])
            
            # Sort by wavenumber if needed
            if self.wavenumbers[0] > self.wavenumbers[-1]:
                self.wavenumbers = self.wavenumbers[::-1]
                self.intensities = self.intensities[::-1]
                
            return True, data
        except Exception as e:
            return False, str(e)
            
    def apply_baseline_correction(self, method='als', **kwargs):
        """Apply baseline correction using pybaselines"""
        if not PYBASELINES_AVAILABLE:
            st.warning("pybaselines not available, using simple baseline")
            self.corrected_intensities = self.intensities
            return
            
        try:
            baseline_fitter = pybaselines.Baseline(self.wavenumbers)
            
            if method == 'als':
                self.baseline, params = baseline_fitter.asls(
                    self.intensities, 
                    lam=kwargs.get('lambda', 1e4),
                    p=kwargs.get('p', 0.01)
                )
            elif method == 'arpls':
                self.baseline, params = baseline_fitter.arpls(
                    self.intensities,
                    lam=kwargs.get('lambda', 1e5)
                )
            elif method == 'polynomial':
                self.baseline, params = baseline_fitter.poly(
                    self.intensities,
                    poly_order=kwargs.get('order', 3)
                )
                
            self.corrected_intensities = self.intensities - self.baseline
            
        except Exception as e:
            st.error(f"Baseline correction failed: {e}")
            self.corrected_intensities = self.intensities
            
    def normalize_spectrum(self, data=None):
        """Normalize spectrum to 0-1 range"""
        if data is None:
            data = self.corrected_intensities
        return (data - data.min()) / (data.max() - data.min())
        
    def fit_peaks_with_lmfit(self, peak_positions, model_type='gaussian'):
        """Fit multiple peaks using lmfit"""
        if not LMFIT_AVAILABLE:
            st.error("lmfit not available for advanced peak fitting")
            return None
            
        # Create composite model
        model = None
        params = None
        
        for i, pos in enumerate(peak_positions):
            prefix = f'peak{i}_'
            
            if model_type == 'gaussian':
                peak_model = GaussianModel(prefix=prefix)
            elif model_type == 'voigt':
                peak_model = VoigtModel(prefix=prefix)
            else:
                peak_model = LorentzianModel(prefix=prefix)
                
            if model is None:
                model = peak_model
                params = peak_model.make_params()
            else:
                model += peak_model
                params.update(peak_model.make_params())
                
            # Set initial parameters
            idx = np.argmin(np.abs(self.wavenumbers - pos))
            params[f'{prefix}center'].set(value=pos, min=pos-20, max=pos+20)
            params[f'{prefix}height'].set(value=self.corrected_intensities[idx], min=0)
            params[f'{prefix}sigma'].set(value=10, min=1, max=50)
            
        # Fit the model
        try:
            result = model.fit(self.corrected_intensities, params, x=self.wavenumbers)
            return result
        except Exception as e:
            st.error(f"Peak fitting failed: {e}")
            return None

def main():
    st.title("🔬 Professional FTIR Analysis Suite")
    st.markdown("**Advanced spectroscopic analysis with interactive peak fitting**")
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = FTIRAnalyzer()
    
    analyzer = st.session_state.analyzer
    
    # Sidebar controls
    st.sidebar.header("📂 Data Loading")
    
    # File selection
    data_dir = Path("../data/raw/250721")
    if data_dir.exists():
        jdx_files = list(data_dir.glob("*.JDX"))
        if jdx_files:
            selected_file = st.sidebar.selectbox(
                "Select FTIR file:",
                jdx_files,
                format_func=lambda x: x.name
            )
            
            if st.sidebar.button("Load File"):
                success, result = analyzer.load_jdx_file(selected_file)
                if success:
                    st.success(f"✅ Loaded {selected_file.name}")
                    st.json({"metadata": {k: str(v) for k, v in result.items() 
                            if k not in ['x', 'y'] and len(str(v)) < 100}})
                else:
                    st.error(f"❌ Failed to load file: {result}")
    
    if analyzer.wavenumbers is not None:
        # Baseline correction controls
        st.sidebar.header("📈 Baseline Correction")
        
        method = st.sidebar.selectbox(
            "Baseline method:",
            ['als', 'arpls', 'polynomial'] if PYBASELINES_AVAILABLE else ['none']
        )
        
        if method == 'als':
            lambda_param = st.sidebar.slider("Lambda (smoothness)", 1e3, 1e6, 1e4, format="%.0e")
            p_param = st.sidebar.slider("Asymmetry (p)", 0.001, 0.1, 0.01, format="%.3f")
            kwargs = {'lambda': lambda_param, 'p': p_param}
        elif method == 'arpls':
            lambda_param = st.sidebar.slider("Lambda", 1e3, 1e7, 1e5, format="%.0e")
            kwargs = {'lambda': lambda_param}
        elif method == 'polynomial':
            order = st.sidebar.slider("Polynomial order", 1, 6, 3)
            kwargs = {'order': order}
        else:
            kwargs = {}
            
        if st.sidebar.button("Apply Baseline Correction"):
            with st.spinner("Applying baseline correction..."):
                analyzer.apply_baseline_correction(method, **kwargs)
                st.success("✅ Baseline correction applied")
        
        # Peak fitting controls
        st.sidebar.header("🎯 Peak Fitting")
        
        # Peak selection methods
        st.sidebar.subheader("🎯 Peak Selection Methods")
        
        selection_method = st.sidebar.radio(
            "Choose method:",
            ["Manual Entry", "Auto-Detect", "Common FTIR Peaks"]
        )
        
        if selection_method == "Manual Entry":
            peak_positions_text = st.sidebar.text_area(
                "Peak positions (cm⁻¹, one per line):",
                placeholder="1650\n1500\n1200\n950",
                help="Hover over plot to see exact wavenumbers, then enter here"
            )
            
        elif selection_method == "Auto-Detect":
            height_threshold = st.sidebar.slider("Height threshold", 0.05, 0.5, 0.1)
            prominence_threshold = st.sidebar.slider("Prominence threshold", 0.01, 0.2, 0.05)
            
            if st.sidebar.button("Auto-Detect Peaks"):
                try:
                    from scipy.signal import find_peaks
                    normalized = analyzer.normalize_spectrum()
                    peaks_idx, properties = find_peaks(
                        normalized,
                        height=height_threshold,
                        prominence=prominence_threshold,
                        distance=10
                    )
                    
                    auto_peaks = [analyzer.wavenumbers[idx] for idx in peaks_idx]
                    st.session_state.auto_detected_peaks = auto_peaks
                    st.success(f"🎯 Detected {len(auto_peaks)} peaks")
                    
                except ImportError:
                    st.error("scipy not available for auto-detection")
                    
            if 'auto_detected_peaks' in st.session_state:
                selected_auto_peaks = st.sidebar.multiselect(
                    "Select peaks to fit:",
                    st.session_state.auto_detected_peaks,
                    default=st.session_state.auto_detected_peaks[:5],  # Top 5
                    format_func=lambda x: f"{x:.1f} cm⁻¹"
                )
                peak_positions_text = "\n".join([str(int(p)) for p in selected_auto_peaks])
            else:
                peak_positions_text = ""
                
        else:  # Common FTIR Peaks
            st.sidebar.write("**Select common FTIR peak regions:**")
            
            common_peaks = {
                "O-H stretch (3200-3600)": [3300, 3500],
                "C-H stretch (2800-3000)": [2850, 2920, 2960],
                "C=O stretch (1650-1750)": [1650, 1700],
                "C=C aromatic (1500-1600)": [1500, 1580],
                "C-H bend (1350-1500)": [1380, 1450],
                "C-O stretch (1000-1300)": [1050, 1200],
                "Al-O bonds (400-1000)": [500, 750, 950]
            }
            
            selected_regions = []
            for region, peaks in common_peaks.items():
                if st.sidebar.checkbox(region):
                    selected_regions.extend(peaks)
                    
            peak_positions_text = "\n".join([str(p) for p in selected_regions])
        
        if LMFIT_AVAILABLE:
            model_type = st.sidebar.selectbox(
                "Peak model:",
                ['gaussian', 'voigt', 'lorentzian']
            )
            
            if st.sidebar.button("Fit Peaks") and peak_positions_text:
                try:
                    positions = [float(pos.strip()) for pos in peak_positions_text.split('\n') if pos.strip()]
                    if positions:
                        with st.spinner("Fitting peaks..."):
                            result = analyzer.fit_peaks_with_lmfit(positions, model_type)
                            if result:
                                st.session_state.fit_result = result
                                st.success(f"✅ Fitted {len(positions)} peaks")
                except ValueError:
                    st.error("Invalid peak positions format")
        
        # Main plotting area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create interactive plot
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Raw vs Baseline Corrected', 'Peak Fitting Results'),
                vertical_spacing=0.1,
                row_heights=[0.4, 0.6]
            )
            
            # Top plot: Raw vs corrected
            if analyzer.corrected_intensities is not None:
                raw_norm = analyzer.normalize_spectrum(analyzer.intensities)
                corr_norm = analyzer.normalize_spectrum(analyzer.corrected_intensities)
                
                fig.add_trace(
                    go.Scatter(x=analyzer.wavenumbers, y=raw_norm, 
                             name='Raw', line=dict(color='lightblue')),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=analyzer.wavenumbers, y=corr_norm, 
                             name='Corrected', line=dict(color='blue')),
                    row=1, col=1
                )
                
                # Bottom plot: Peak fitting
                fig.add_trace(
                    go.Scatter(x=analyzer.wavenumbers, y=corr_norm, 
                             name='Spectrum', line=dict(color='darkblue', width=2)),
                    row=2, col=1
                )
                
                # Add fitted peaks if available
                if 'fit_result' in st.session_state:
                    result = st.session_state.fit_result
                    fitted_curve = result.best_fit
                    fig.add_trace(
                        go.Scatter(x=analyzer.wavenumbers, y=analyzer.normalize_spectrum(fitted_curve),
                                 name='Fitted', line=dict(color='red', dash='dash')),
                        row=2, col=1
                    )
                    
                    # Add individual peak components
                    for i, comp in enumerate(result.eval_components().values()):
                        fig.add_trace(
                            go.Scatter(x=analyzer.wavenumbers, y=analyzer.normalize_spectrum(comp),
                                     name=f'Peak {i+1}', line=dict(dash='dot'), opacity=0.7),
                            row=2, col=1
                        )
            
            # Configure layout
            fig.update_layout(height=800, showlegend=True)
            fig.update_xaxes(title_text="Wavenumber (cm⁻¹)", autorange="reversed")
            fig.update_yaxes(title_text="Normalized Absorbance")
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Analysis Results")
            
            if analyzer.corrected_intensities is not None:
                st.metric("Data Points", len(analyzer.wavenumbers))
                st.metric("Wavenumber Range", 
                         f"{analyzer.wavenumbers.min():.0f} - {analyzer.wavenumbers.max():.0f} cm⁻¹")
                
                if 'fit_result' in st.session_state:
                    result = st.session_state.fit_result
                    st.write("**Fit Statistics:**")
                    st.write(f"R²: {1 - result.residual.var() / np.var(analyzer.corrected_intensities):.4f}")
                    st.write(f"χ²: {result.chisqr:.2e}")
                    st.write(f"Reduced χ²: {result.redchi:.4f}")
                    
                    # Peak parameters
                    st.write("**Peak Parameters:**")
                    for i, (name, param) in enumerate(result.params.items()):
                        if 'center' in name:
                            st.write(f"Peak {name.split('_')[0]}: {param.value:.1f} ± {param.stderr:.1f} cm⁻¹")
            
            # Export options
            st.subheader("💾 Export Options")
            
            if st.button("Export Peak Data"):
                if 'fit_result' in st.session_state:
                    result = st.session_state.fit_result
                    export_data = {
                        'timestamp': datetime.now().isoformat(),
                        'file': selected_file.name if 'selected_file' in locals() else 'unknown',
                        'fit_statistics': {
                            'r_squared': float(1 - result.residual.var() / np.var(analyzer.corrected_intensities)),
                            'chi_squared': float(result.chisqr),
                            'reduced_chi_squared': float(result.redchi)
                        },
                        'parameters': {name: {'value': param.value, 'stderr': param.stderr} 
                                     for name, param in result.params.items()}
                    }
                    
                    st.download_button(
                        "Download Peak Analysis JSON",
                        json.dumps(export_data, indent=2),
                        file_name=f"ftir_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

if __name__ == "__main__":
    main()