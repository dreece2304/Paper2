import pandas as pd
import matplotlib.pyplot as plt
import os

# === Setup ===
base_path = "06_XPS_Analysis/analysis"
excel_path = os.path.join(base_path, "THB_final.xlsx")  # Your fixed file
sheets = ["AsDeposited", "Water", "UV_Water"]
regions = ["C 1s", "O 1s", "Al 2p"]

# Create output directory
os.makedirs(os.path.join(base_path, "bg_checks"), exist_ok=True)

# === Check background values ===
for sheet in sheets:
    print(f"\nChecking sheet: {sheet}")
    
    df = pd.read_excel(excel_path, sheet_name=sheet)
    
    for region in regions:
        print(f"  Region: {region}")
        
        region_df = df[df['Region'] == region].copy()
        
        if region_df.empty:
            print(f"    No data for {region}")
            continue
            
        # Sort by binding energy
        region_df = region_df.sort_values('B.E.')
        
        # Quick checks
        bg_range = (region_df['Background'].min(), region_df['Background'].max())
        env_range = (region_df['Envelope'].min(), region_df['Envelope'].max())
        raw_range = (region_df['raw'].min(), region_df['raw'].max())
        
        print(f"    Background range: {bg_range}")
        print(f"    Envelope range: {env_range}")
        print(f"    Raw data range: {raw_range}")
        
        # Check if background is less than raw across the spectrum
        bg_below_raw = (region_df['Background'] <= region_df['raw']).all()
        print(f"    Background below raw everywhere: {bg_below_raw}")
        
        # Plot to check
        fig, ax = plt.subplots(figsize=(8, 5))
        
        ax.plot(region_df['B.E.'], region_df['raw'], 'o-', label='Raw Data', markersize=3)
        ax.plot(region_df['B.E.'], region_df['Background'], 'r-', label='Background')
        ax.plot(region_df['B.E.'], region_df['Envelope'], 'g-', label='Envelope')
        
        ax.set_title(f"{sheet} - {region}")
        ax.set_xlabel('Binding Energy (eV)')
        ax.set_ylabel('Intensity')
        ax.legend()
        ax.invert_xaxis()
        
        # Save the diagnostic plot
        plt.tight_layout()
        plt.savefig(os.path.join(base_path, "bg_checks", f"{sheet}_{region.replace(' ', '_')}_check.png"))
        plt.close()
        
print("\nDiagnostic plots saved to:", os.path.join(base_path, "bg_checks"))