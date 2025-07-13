#!/usr/bin/env python3
"""
XPS Setup Test Script
====================

This script tests that all dependencies and file structures are correctly set up
for the XPS analysis pipeline.

Usage:
    python test_xps_setup.py

Author: [Your Name]
Date: [Current Date]
"""

import sys
import os
from pathlib import Path
import importlib


def test_imports():
    """Test that all required packages can be imported."""
    print("🔍 Testing package imports...")

    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'pathlib'
    ]

    failed_imports = []

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            failed_imports.append(package)

    if failed_imports:
        print(f"\n❌ Missing packages: {', '.join(failed_imports)}")
        print("Install with: pip install pandas numpy matplotlib")
        return False
    else:
        print("✅ All required packages available")
        return True


def test_shared_utilities():
    """Test that shared utilities can be imported."""
    print("\n🔍 Testing shared utilities...")

    # Add shared utilities to path
    sys.path.append('../../shared')

    try:
        from utils.plot_styles import set_plot_style
        print("  ✓ plot_styles")
    except ImportError as e:
        print(f"  ✗ plot_styles: {e}")
        return False

    try:
        from utils.helpers import create_figure, save_figure
        print("  ✓ helpers")
    except ImportError as e:
        print(f"  ✗ helpers: {e}")
        return False

    try:
        from utils.config import viridis, color_asdeposited, color_uvtreated
        print("  ✓ config")
    except ImportError as e:
        print(f"  ✗ config: {e}")
        return False

    try:
        from utils.xps_utils import validate_xps_data, background_subtract_normalize
        print("  ✓ xps_utils")
    except ImportError as e:
        print(f"  ✗ xps_utils: {e}")
        return False

    print("✅ All shared utilities available")
    return True


def test_directory_structure():
    """Test that required directories exist or can be created."""
    print("\n🔍 Testing directory structure...")

    required_dirs = [
        '../data/raw/',
        '../figures/final/',
        '../data/processed/',
        '../../shared/utils/'
    ]

    all_good = True

    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ⚠️  {dir_path} (will be created)")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"    ✓ Created {dir_path}")
            except Exception as e:
                print(f"    ✗ Could not create {dir_path}: {e}")
                all_good = False

    if all_good:
        print("✅ Directory structure OK")
    else:
        print("❌ Directory structure issues")

    return all_good


def test_data_files():
    """Check for XPS data files."""
    print("\n🔍 Checking for XPS data files...")

    data_dir = Path('../data/raw/')
    expected_files = ['BTY_AD.xlsx', 'BTY_UV.xlsx', 'BTY_H2O.xlsx']

    found_files = []
    missing_files = []

    for filename in expected_files:
        filepath = data_dir / filename
        if filepath.exists():
            print(f"  ✓ {filename}")
            found_files.append(filename)
        else:
            print(f"  ✗ {filename}")
            missing_files.append(filename)

    if found_files:
        print(f"✅ Found {len(found_files)} data files")

    if missing_files:
        print(f"⚠️  Missing {len(missing_files)} data files:")
        for filename in missing_files:
            print(f"     - {filename}")
        print(f"   Place XPS files in: {data_dir.absolute()}")

    return len(found_files) > 0


def create_test_data():
    """Create minimal test data if no real data exists."""
    print("\n🔧 Creating test data...")

    import pandas as pd
    import numpy as np

    data_dir = Path('../data/raw/')
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create a minimal test Excel file
    test_file = data_dir / 'BTY_TEST.xlsx'

    # Create fake XPS data structure
    test_data = []

    # Add header rows (rows 0-6)
    for i in range(7):
        if i == 6:  # Header row
            test_data.append(['B.E.', 'raw', 'fit1', 'fit2', 'Background', 'Envelope'] + [None] * 20)
        else:
            test_data.append([None] * 26)

    # Add some data rows for O 1s
    for be in np.linspace(530, 540, 50):
        intensity = 1000 + 500 * np.exp(-0.5 * ((be - 532) / 1.2) ** 2) + np.random.normal(0, 20)
        background = 800 + 20 * np.random.normal(0, 1)
        row = [be, intensity, intensity - background, np.nan, background, intensity] + [None] * 20
        test_data.append(row)

    # Create DataFrame and save
    df = pd.DataFrame(test_data)

    try:
        df.to_excel(test_file, index=False, header=False)
        print(f"  ✓ Created test file: {test_file}")
        return True
    except Exception as e:
        print(f"  ✗ Could not create test file: {e}")
        return False


def run_basic_analysis_test():
    """Run a basic test of the analysis functions."""
    print("\n🔍 Testing basic analysis functions...")

    try:
        # Import analysis functions
        sys.path.append('.')
        from xps_analysis import process_xps_file, normalize_spectrum_data

        # Test normalization function
        import numpy as np
        raw_data = np.array([1000, 1200, 1100, 900])
        bg_data = np.array([800, 800, 800, 800])

        normalized = normalize_spectrum_data(raw_data, bg_data)

        if len(normalized) == len(raw_data):
            print("  ✓ normalize_spectrum_data")
        else:
            print("  ✗ normalize_spectrum_data")
            return False

        print("✅ Basic analysis functions working")
        return True

    except Exception as e:
        print(f"  ✗ Analysis function test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("XPS Analysis Setup Test")
    print("=" * 50)
    print("Testing setup for XPS analysis pipeline...")
    print("=" * 50)

    tests = [
        ("Package Imports", test_imports),
        ("Shared Utilities", test_shared_utilities),
        ("Directory Structure", test_directory_structure),
        ("Data Files", test_data_files),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))

    # If no data files found, offer to create test data
    data_test_passed = any(name == "Data Files" and result for name, result in results)
    if not data_test_passed:
        print("\n🤔 No XPS data files found. Create test data? (y/n): ", end="")
        response = input().lower().strip()
        if response in ['y', 'yes']:
            if create_test_data():
                print("✅ Test data created successfully")
                print("   You can now test the analysis with: python xps_analysis.py")

    # Run basic analysis test if imports worked
    imports_passed = any(name == "Package Imports" and result for name, result in results)
    utils_passed = any(name == "Shared Utilities" and result for name, result in results)

    if imports_passed and utils_passed:
        run_basic_analysis_test()

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")

    print(f"\nPassed: {passed_tests}/{total_tests} tests")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Ready to run XPS analysis.")
        print("Run: python xps_analysis.py")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please fix issues before running analysis.")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()