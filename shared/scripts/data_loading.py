import pandas as pd
import os

def load_csv(filepath):
    """
    Load a CSV file into a pandas DataFrame.
    Args:
        filepath (str): Path to the CSV file.
    Returns:
        pd.DataFrame
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_csv(filepath)

def load_excel(filepath, sheet_name=0):
    """
    Load an Excel file into a pandas DataFrame.
    Args:
        filepath (str): Path to Excel file.
        sheet_name: Sheet name or index (default is first sheet).
    Returns:
        pd.DataFrame
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_excel(filepath, sheet_name=sheet_name)
