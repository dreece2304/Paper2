#!/usr/bin/env python3
"""
Generate improved region-grouped LaTeX table with symbol system
"""

import json
import os
from collections import defaultdict

def generate_region_grouped_table(json_file='../outputs/ftir_peaks_changes.json', output_file='../outputs/ftir_peak_changes_improved.tex'):
    """Generate region-grouped LaTeX table with verified peaks"""
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    regions = data.get('regions', {})
    peaks = data.get('peaks', {})
    
    # Group peaks by region
    peaks_by_region = defaultdict(list)
    excluded_regions = {'artifact'}  # Don't show artifacts in main table
    
    for peak_wn, peak_data in peaks.items():
        region = peak_data.get('region', 'unknown')
        if region not in excluded_regions:
            peaks_by_region[region].append((peak_wn, peak_data))
    
    # Sort peaks within each region by wavenumber (descending)
    for region in peaks_by_region:
        peaks_by_region[region].sort(key=lambda x: x[1]['wavenumber'], reverse=True)
    
    # Define region order for table
    region_order = [
        'hydroxyl', 'ch_stretching', 'cc_stretching', 
        'carbonyl_alkene', 'ch_bending', 'al_o_c', 'al_o'
    ]
    
    # Start building LaTeX table
    latex_table = r"""\begin{table*}[ht]
\centering
\caption{FTIR Peak Assignments and Changes upon UV Exposure for Alucone Films}
\label{tab:ftir_peaks}
\begin{tabular}{llcccl}
\hline
\textbf{Region} & \textbf{Wavenumber} & \textbf{Assignment} & \textbf{Spectra} & \textbf{Change} & \textbf{Notes} \\
 & \textbf{(cm$^{-1}$)} &  &  &  &  \\
\hline
"""
    
    # Process each region
    for region_key in region_order:
        if region_key not in peaks_by_region:
            continue
            
        region_data = regions.get(region_key, {})
        region_name = region_data.get('display_label', region_key.replace('_', '-').title())
        region_peaks = peaks_by_region[region_key]
        
        if not region_peaks:
            continue
        
        # Add region header with merged cells
        first_row = True
        
        for i, (peak_wn, peak_data) in enumerate(region_peaks):
            # Get peak information
            wavenumber = peak_data.get('wavenumber', peak_wn)
            assignment = peak_data.get('label', 'Unknown')
            spectra = peak_data.get('spectrum_info', 'Unknown')
            symbol = peak_data.get('symbol', '~')
            notes = peak_data.get('notes', '')
            
            # Clean up assignment for LaTeX
            assignment_clean = assignment.replace('₂', '$_2$').replace('₃', '$_3$')
            assignment_clean = assignment_clean.replace('≡', r'$\equiv$')
            assignment_clean = assignment_clean.replace('⁻¹', '$^{-1}$')
            
            # Handle spectra info
            if 'As-dep' in spectra and 'trace' in spectra:
                spectra_clean = r'As-dep $\rightarrow$ trace'
            elif 'UV only' in spectra:
                spectra_clean = 'UV only'
            elif 'Both' in spectra:
                spectra_clean = 'Both'
            elif 'interference' in spectra.lower():
                spectra_clean = r'\textit{Obscured}'
            else:
                spectra_clean = spectra
            
            # Handle artifact interference peaks specially
            if 'expected' in peak_wn.lower() or 'interference' in peak_data.get('change_type', '').lower():
                assignment_clean = r'\textit{' + assignment_clean + '}'
                spectra_clean = r'\textit{Obscured}'
            
            # Build row
            if first_row:
                # First row of region gets the region name
                num_peaks = len(region_peaks)
                row = f"\\multirow{{{num_peaks}}}{{*}}{{\\textbf{{{region_name}}}}} & {wavenumber} & {assignment_clean} & {spectra_clean} & {symbol} & {notes} \\\\\n"
                first_row = False
            else:
                # Subsequent rows have empty region cell
                row = f" & {wavenumber} & {assignment_clean} & {spectra_clean} & {symbol} & {notes} \\\\\n"
            
            latex_table += row
        
        # Add some spacing between regions
        latex_table += "\\hline\n"
    
    # Handle special cases - show expected C≡C peaks separately if desired
    cc_expected_peaks = [(wn, data) for wn, data in peaks.items() 
                        if data.get('region') == 'cc_stretching' and 'expected' in wn]
    
    if cc_expected_peaks:
        latex_table += "\\multirow{" + str(len(cc_expected_peaks)) + "}{*}{\\textbf{Expected C≡C}} "
        for i, (peak_wn, peak_data) in enumerate(cc_expected_peaks):
            wavenumber = peak_data.get('wavenumber', peak_wn)
            assignment = peak_data.get('label', 'Unknown')
            symbol = peak_data.get('symbol', '⚠')
            notes = peak_data.get('notes', '')
            
            assignment_clean = r'\textit{' + assignment.replace('≡', r'$\equiv$') + '}'
            
            if i == 0:
                row = f"& {wavenumber} & {assignment_clean} & \\textit{{Obscured}} & {symbol} & {notes} \\\\\n"
            else:
                row = f" & {wavenumber} & {assignment_clean} & \\textit{{Obscured}} & {symbol} & {notes} \\\\\n"
            
            latex_table += row
        
        latex_table += "\\hline\n"
    
    # Close table
    latex_table += r"""\end{tabular}
\begin{flushleft}
\footnotesize
Symbols: $\uparrow$ increase, $\downarrow$ decrease, $\uparrow\uparrow$ major increase ($>70\%$), $\downarrow\downarrow$ major decrease ($>70\%$), $\sim$ stable ($<10\%$ change), $\triangleright$ artifact interference. \\
Spectra: Both = present in both as-deposited and UV-exposed; UV only = appears only after UV exposure; As-dep $\rightarrow$ trace = strong peak becomes very weak; Obscured = expected but masked by CO$_2$ interference.
\end{flushleft}
\end{table*}
"""
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_table)
    
    print(f"✅ Improved LaTeX table saved to {output_file}")
    
    # Print summary
    total_peaks = sum(len(region_peaks) for region_peaks in peaks_by_region.values())
    print(f"   - Total peaks in table: {total_peaks}")
    print(f"   - Regions included: {len([r for r in region_order if r in peaks_by_region])}")
    
    print("\nPeaks by region:")
    for region_key in region_order:
        if region_key in peaks_by_region:
            count = len(peaks_by_region[region_key])
            region_name = regions.get(region_key, {}).get('display_label', region_key)
            print(f"   - {region_name}: {count} peaks")
    
    return latex_table

def generate_artifact_table(json_file='../outputs/ftir_peaks_changes.json', output_file='../outputs/ftir_artifacts_table.tex'):
    """Generate separate table for artifacts and expected peaks"""
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    peaks = data.get('peaks', {})
    
    # Find artifact and expected peaks
    artifact_peaks = [(wn, data) for wn, data in peaks.items() 
                     if data.get('region') == 'artifact' or 'expected' in wn]
    
    if not artifact_peaks:
        print("No artifact peaks to show")
        return
    
    # Sort by wavenumber
    artifact_peaks.sort(key=lambda x: x[1]['wavenumber'], reverse=True)
    
    latex_table = r"""\begin{table}[ht]
\centering
\caption{Artifact Peaks and Expected Features in FTIR Spectrum}
\label{tab:ftir_artifacts}
\begin{tabular}{lcccl}
\hline
\textbf{Wavenumber} & \textbf{Assignment} & \textbf{Type} & \textbf{Change} & \textbf{Notes} \\
\textbf{(cm$^{-1}$)} &  &  &  &  \\
\hline
"""
    
    for peak_wn, peak_data in artifact_peaks:
        wavenumber = peak_data.get('wavenumber', peak_wn)
        assignment = peak_data.get('label', 'Unknown')
        symbol = peak_data.get('symbol', '⚠')
        notes = peak_data.get('notes', '')
        
        if 'expected' in peak_wn:
            peak_type = 'Expected'
        elif 'artifact' in peak_data.get('region', ''):
            peak_type = 'Artifact'
        else:
            peak_type = 'Other'
        
        assignment_clean = assignment.replace('≡', r'$\equiv$')
        assignment_clean = assignment_clean.replace('₂', '$_2$')
        
        latex_table += f"{wavenumber} & {assignment_clean} & {peak_type} & {symbol} & {notes} \\\\\n"
    
    latex_table += r"""\hline
\end{tabular}
\begin{flushleft}
\footnotesize
Expected peaks are theoretical assignments that may be obscured by atmospheric CO$_2$ interference in the 2300-2600 cm$^{-1}$ region.
\end{flushleft}
\end{table}
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_table)
    
    print(f"✅ Artifact table saved to {output_file}")
    return latex_table

if __name__ == "__main__":
    # Generate main table
    main_table = generate_region_grouped_table()
    
    # Generate artifact table
    artifact_table = generate_artifact_table()
    
    print("\n" + "="*60)
    print("TABLE GENERATION COMPLETE")
    print("="*60)
    print("Main table: ftir_peak_changes_improved.tex")
    print("Artifact table: ftir_artifacts_table.tex")
    print("="*60)