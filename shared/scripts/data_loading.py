import pandas as pd

def load_csv(filepath):
    """
    Load a CSV file into a pandas DataFrame.
    Args:
        filepath: Path to CSV file
    Returns:
        pandas DataFrame
    """
    return pd.read_csv(filepath)

def load_excel(filepath, sheet_name=0):
    """
    Load an Excel file into a pandas DataFrame.
    Args:
        filepath: Path to Excel file
        sheet_name: Sheet name or index (default is first sheet)
    Returns:
        pandas DataFrame
    """
    return pd.read_excel(filepath, sheet_name=sheet_name)

def load_pickle(filepath):
    """
    Load a pickle file (for serialized Python objects like dicts, DataFrames).
    Args:
        filepath: Path to pickle file
    Returns:
        Loaded Python object
    """
    import pickle
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def save_pickle(obj, filepath):
    """
    Save a Python object to a pickle file.
    Args:
        obj: Object to save
        filepath: Path to output pickle file
    """
    import pickle
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)
