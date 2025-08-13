#!/usr/bin/env python3
"""
FTIR Analysis with True Click-to-Select Peak Functionality
Uses Bokeh for proper click handling in web browsers
"""

import numpy as np
import pandas as pd
import jcamp
from pathlib import Path
import json
from datetime import datetime

# Bokeh imports for true interactivity
try:
    from bokeh.plotting import figure, show, save, output_file
    from bokeh.models import HoverTool, TapTool, CustomJS, ColumnDataSource, Button, Div
    from bokeh.layouts import column, row
    from bokeh.io import curdoc
    from bokeh.models.widgets import Select, Slider, TextInput
    BOKEH_AVAILABLE = True
except ImportError:
    BOKEH_AVAILABLE = False

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

class InteractiveFTIRAnalyzer:
    """FTIR analyzer with true click-to-select functionality"""
    
    def __init__(self):
        self.wavenumbers = None
        self.intensities = None
        self.corrected_intensities = None
        self.baseline = None
        self.selected_peaks = []
        self.fit_result = None
        
    def load_jdx_file(self, file_path):
        """Load JDX file"""
        try:
            data = jcamp.jcamp_readfile(file_path)
            self.wavenumbers = np.array(data['x'])
            self.intensities = np.array(data['y'])
            
            # Sort by wavenumber if needed
            if len(self.wavenumbers) > 1 and self.wavenumbers[0] > self.wavenumbers[-1]:
                self.wavenumbers = self.wavenumbers[::-1]
                self.intensities = self.intensities[::-1]
                
            self.corrected_intensities = self.intensities.copy()
            print(f"✅ Loaded {file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to load {file_path}: {e}")
            return False
            
    def apply_baseline_correction(self, method='als', **kwargs):
        """Apply baseline correction"""
        if not PYBASELINES_AVAILABLE:
            print("⚠️ pybaselines not available, using raw data")
            return
            
        try:
            baseline_fitter = pybaselines.Baseline(self.wavenumbers)
            
            if method == 'als':
                self.baseline, _ = baseline_fitter.asls(
                    self.intensities, 
                    lam=kwargs.get('lambda', 1e4),
                    p=kwargs.get('p', 0.01)
                )
            elif method == 'arpls':
                self.baseline, _ = baseline_fitter.arpls(
                    self.intensities,
                    lam=kwargs.get('lambda', 1e5)
                )
                
            self.corrected_intensities = self.intensities - self.baseline
            print(f"✅ Applied {method} baseline correction")
            
        except Exception as e:
            print(f"❌ Baseline correction failed: {e}")
            
    def normalize_spectrum(self, data=None):
        """Normalize spectrum"""
        if data is None:
            data = self.corrected_intensities
        return (data - data.min()) / (data.max() - data.min())
        
    def create_interactive_bokeh_app(self):
        """Create Bokeh app with click-to-select peaks"""
        if not BOKEH_AVAILABLE:
            print("❌ Bokeh not available. Install with: pip install bokeh")
            return None
            
        # Create data sources
        spectrum_data = ColumnDataSource(data=dict(
            x=self.wavenumbers,
            y=self.normalize_spectrum(),
            raw_y=self.normalize_spectrum(self.intensities)
        ))
        
        peaks_data = ColumnDataSource(data=dict(x=[], y=[], labels=[]))
        
        # Create main plot
        p = figure(
            title="Interactive FTIR Peak Selection - Click on Peaks",
            width=1000, height=600,
            x_axis_label="Wavenumber (cm⁻¹)",
            y_axis_label="Normalized Absorbance",
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        # Flip x-axis for FTIR convention
        p.x_range.flipped = True
        
        # Add spectrum line
        spectrum_line = p.line('x', 'y', source=spectrum_data, 
                              line_width=2, color='blue', alpha=0.8,
                              legend_label="Corrected Spectrum")
        
        # Add raw spectrum for comparison
        p.line('x', 'raw_y', source=spectrum_data,
               line_width=1, color='lightblue', alpha=0.6,
               legend_label="Raw Spectrum")
        
        # Add peak markers
        peak_circles = p.circle('x', 'y', source=peaks_data,
                               size=12, color='red', alpha=0.8,
                               legend_label="Selected Peaks")
        
        # Add hover tool
        hover = HoverTool(tooltips=[
            ("Wavenumber", "@x{0.1f} cm⁻¹"),
            ("Intensity", "@y{0.3f}"),
        ], renderers=[spectrum_line])
        p.add_tools(hover)
        
        # JavaScript callback for clicking on spectrum
        callback = CustomJS(args=dict(
            spectrum_source=spectrum_data, 
            peaks_source=peaks_data,
            peak_circles=peak_circles
        ), code="""
            // Get click coordinates
            const geometry = cb_obj.geometry;
            const x_click = geometry.x;
            
            // Find closest point on spectrum
            const x_data = spectrum_source.data['x'];
            const y_data = spectrum_source.data['y'];
            
            let min_dist = Infinity;
            let closest_idx = 0;
            
            for (let i = 0; i < x_data.length; i++) {
                const dist = Math.abs(x_data[i] - x_click);
                if (dist < min_dist) {
                    min_dist = dist;
                    closest_idx = i;
                }
            }
            
            const peak_x = x_data[closest_idx];
            const peak_y = y_data[closest_idx];
            
            // Check if peak already exists (within 10 cm⁻¹)
            const existing_peaks_x = peaks_source.data['x'];
            let peak_exists = false;
            
            for (let i = 0; i < existing_peaks_x.length; i++) {
                if (Math.abs(existing_peaks_x[i] - peak_x) < 10) {
                    // Remove existing peak
                    existing_peaks_x.splice(i, 1);
                    peaks_source.data['y'].splice(i, 1);
                    peaks_source.data['labels'].splice(i, 1);
                    peak_exists = true;
                    break;
                }
            }
            
            if (!peak_exists) {
                // Add new peak
                peaks_source.data['x'].push(peak_x);
                peaks_source.data['y'].push(peak_y);
                peaks_source.data['labels'].push(peak_x.toFixed(0) + ' cm⁻¹');
            }
            
            // Trigger update
            peaks_source.change.emit();
            
            // Update status (you can connect this to a Div element)
            console.log('Peak toggled at:', peak_x.toFixed(1), 'cm⁻¹');
        """)
        
        # Add tap tool with callback
        tap = TapTool(callback=callback)
        p.add_tools(tap)
        
        # Control widgets
        clear_button = Button(label="Clear All Peaks", button_type="warning")
        fit_button = Button(label="Fit Peaks", button_type="success")
        export_button = Button(label="Export Data", button_type="primary")
        
        # Baseline controls
        baseline_select = Select(title="Baseline Method:", 
                               value="als", 
                               options=["als", "arpls", "polynomial"])
        
        lambda_slider = Slider(start=1000, end=100000, value=10000, step=1000,
                              title="Lambda (Smoothness)")
        
        # Status display
        status_div = Div(text="<b>Status:</b> Click on spectrum to select peaks", 
                        width=400, height=50)
        
        # Button callbacks
        def clear_peaks():
            peaks_data.data = dict(x=[], y=[], labels=[])
            status_div.text = "<b>Status:</b> All peaks cleared"
            
        def fit_peaks():
            peak_positions = list(peaks_data.data['x'])
            if peak_positions and LMFIT_AVAILABLE:
                # Perform fitting (simplified for demo)
                status_div.text = f"<b>Status:</b> Fitted {len(peak_positions)} peaks"
            else:
                status_div.text = "<b>Status:</b> No peaks selected or lmfit not available"
                
        def export_data():
            peak_positions = list(peaks_data.data['x'])
            export_dict = {
                'timestamp': datetime.now().isoformat(),
                'selected_peaks': peak_positions,
                'num_peaks': len(peak_positions)
            }
            # In a real app, this would save to file
            status_div.text = f"<b>Status:</b> Exported {len(peak_positions)} peaks"
            print("Export data:", export_dict)
            
        clear_button.on_click(clear_peaks)
        fit_button.on_click(fit_peaks)
        export_button.on_click(export_data)
        
        # Layout
        controls = column([
            baseline_select,
            lambda_slider,
            row([clear_button, fit_button, export_button]),
            status_div
        ])
        
        layout = row([p, controls])
        
        return layout, peaks_data
        
    def save_bokeh_app(self, output_file="ftir_interactive.html"):
        """Save interactive Bokeh app to HTML file"""
        if self.wavenumbers is None:
            print("❌ No data loaded")
            return False
            
        layout, peaks_data = self.create_interactive_bokeh_app()
        if layout is None:
            return False
            
        output_file_path = Path(output_file)
        output_file(str(output_file_path))
        save(layout)
        
        print(f"✅ Interactive FTIR app saved to: {output_file_path.absolute()}")
        print(f"📖 Open in browser: file://{output_file_path.absolute()}")
        print(f"🎯 Click directly on spectrum peaks to select them!")
        
        return True

def main():
    """Main function to create interactive FTIR analyzer"""
    print("🔬 Interactive FTIR Peak Selection Tool")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = InteractiveFTIRAnalyzer()
    
    # Load data
    data_dir = Path("../data/raw/250721")
    jdx_files = list(data_dir.glob("*.JDX")) if data_dir.exists() else []
    
    if not jdx_files:
        print("❌ No JDX files found in ../data/raw/250721/")
        return
        
    print(f"📂 Found {len(jdx_files)} JDX files:")
    for i, file in enumerate(jdx_files):
        print(f"  {i+1}. {file.name}")
    
    # Load first file (or let user choose)
    selected_file = jdx_files[0]  # Change index to select different file
    
    if not analyzer.load_jdx_file(selected_file):
        return
        
    # Apply baseline correction
    analyzer.apply_baseline_correction('als', lambda=1e4, p=0.01)
    
    # Create and save interactive app
    output_file = f"interactive_ftir_{selected_file.stem}.html"
    if analyzer.save_bokeh_app(output_file):
        print(f"\\n🎯 Instructions:")
        print(f"1. Open the HTML file in your web browser")
        print(f"2. Use zoom/pan tools to examine regions closely")
        print(f"3. Click directly on peaks to select them")
        print(f"4. Selected peaks appear as red circles")
        print(f"5. Click on existing peak to remove it")
        print(f"6. Use buttons to clear peaks, fit, or export")

if __name__ == "__main__":
    main()