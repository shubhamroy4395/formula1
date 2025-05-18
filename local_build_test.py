#!/usr/bin/env python3
"""
Validation script to test if all dependencies install and work properly
"""
import sys
import subprocess
import importlib
import pkg_resources

def print_header(message):
    print("\n" + "="*80)
    print(f" {message}")
    print("="*80)

def check_python_version():
    print_header("Checking Python Version")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if Python version is compatible with Streamlit Cloud (Python 3.12)
    major, minor = sys.version_info.major, sys.version_info.minor
    print(f"Major version: {major}, Minor version: {minor}")
    
    if major != 3 or minor < 9:
        print("⚠️ WARNING: Local Python version may not match Streamlit Cloud (Python 3.12)")
        print("   This could lead to different behavior between local and cloud environments.")
    else:
        print("✅ Python version looks good!")

def check_packages():
    print_header("Checking Required Packages")
    required_packages = [
        "setuptools", "fastf1", "pandas", "matplotlib", "numpy", 
        "streamlit", "dateutil", "requests", "tabulate"
    ]
    
    all_good = True
    for package in required_packages:
        try:
            imported = importlib.import_module(package)
            version = pkg_resources.get_distribution(package.replace("dateutil", "python-dateutil")).version
            print(f"✅ {package.replace('dateutil', 'python-dateutil')}: {version}")
        except (ImportError, pkg_resources.DistributionNotFound) as e:
            print(f"❌ {package.replace('dateutil', 'python-dateutil')} not found: {e}")
            all_good = False
    
    if all_good:
        print("\nAll required packages are installed!")
    else:
        print("\n⚠️ Some packages are missing. Try running:")
        print("   pip install -r requirements.txt")

def test_imports():
    print_header("Testing Critical Imports")
    
    try:
        print("Importing setuptools...")
        import setuptools
        print("✅ setuptools imported successfully")
    except ImportError as e:
        print(f"❌ setuptools import failed: {e}")
    
    try:
        print("\nImporting fastf1...")
        import fastf1
        print(f"✅ fastf1 imported successfully (version: {fastf1.__version__})")
    except ImportError as e:
        print(f"❌ fastf1 import failed: {e}")
    
    try:
        print("\nImporting pandas...")
        import pandas as pd
        print(f"✅ pandas imported successfully (version: {pd.__version__})")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
    
    try:
        print("\nImporting numpy...")
        import numpy as np
        print(f"✅ numpy imported successfully (version: {np.__version__})")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
    
    try:
        print("\nImporting streamlit...")
        import streamlit as st
        print(f"✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")

def test_fastf1_functions():
    print_header("Testing FastF1 API Functions")
    
    try:
        import fastf1
        from datetime import datetime
        
        # Try to get current year calendar
        current_year = datetime.now().year
        print(f"Attempting to fetch F1 calendar for {current_year}...")
        calendar = fastf1.get_event_schedule(current_year, backend='ergast')
        
        if calendar is not None and not calendar.empty:
            print(f"✅ Successfully fetched {len(calendar)} races for {current_year}")
            print(f"   First race: {calendar['EventName'].iloc[0]} in {calendar['Location'].iloc[0]}")
        else:
            print(f"⚠️ Calendar fetched but returned no data for {current_year}")
    except Exception as e:
        print(f"❌ Error testing FastF1 API: {e}")

def main():
    print_header("LOCAL BUILD TEST")
    print("This script will test if your environment is properly set up")
    
    check_python_version()
    check_packages()
    test_imports()
    test_fastf1_functions()
    
    print_header("TEST COMPLETE")
    print("If all tests passed, your local environment should be ready for deployment")
    print("Remember that Streamlit Cloud uses Python 3.12, so any version-specific")
    print("issues might still appear in deployment even if everything works locally")

if __name__ == "__main__":
    main() 