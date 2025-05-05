import pandas as pd
import os
import re

# === Setup paths ===
base_path = "06_XPS_Analysis/analysis"
xlsx_path = os.path.join(base_path, "THB_final.xlsx")
output_dir = base_path

# Function to detect fit columns - matching the one in your plotting scripts
def detect_fit_columns(df):
    return [col for col in df.columns if re.match(r'^fit\d*(\.\d+)?$', col)]

# === Sheets to export ===
sheets = {
    "AsDeposited": "THB.AsDeposited.parquet",
    "Water": "THB.Water.parquet",
    "UV_Water": "THB.UV_Water.parquet"
}

# === Convert each sheet ===
for sheet_name, parquet_name in sheets.items():
    print(f"\nProcessing sheet: {sheet_name}")
    
    # Read the Excel sheet
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
    
    # Basic integrity check for required columns
    required_columns = ['B.E.', 'raw', 'Background', 'Envelope', 'Region']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"❌ Missing columns in sheet '{sheet_name}': {missing}")
        continue
    
    # Check for fit columns
    fit_columns = detect_fit_columns(df)
    if not fit_columns:
        print(f"⚠️ Warning: No fit columns detected in sheet '{sheet_name}'")
    else:
        print(f"✅ Fit columns found in '{sheet_name}': {fit_columns}")
    
    # Optional: check for NaNs or inconsistent Region entries
    unique_regions = df['Region'].dropna().unique().tolist()
    print(f"✅ '{sheet_name}' regions found: {unique_regions}")
    
    # Save as parquet
    out_path = os.path.join(output_dir, parquet_name)
    df.to_parquet(out_path, index=False)
    print(f"📦 Saved: {out_path}")
    
    # Verify parquet file can be read back and contains expected columns
    try:
        test_df = pd.read_parquet(out_path)
        verified_fit_columns = detect_fit_columns(test_df)
        
        # Compare original and saved fit columns
        if set(fit_columns) != set(verified_fit_columns):
            print(f"❌ Fit columns mismatch after save!")
            print(f"Original: {fit_columns}")
            print(f"Saved: {verified_fit_columns}")
        else:
            print(f"✅ Verified all {len(fit_columns)} fit columns preserved")
            
    except Exception as e:
        print(f"❌ Failed to verify parquet file: {e}")