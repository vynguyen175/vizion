"""
Simple startup test to verify all imports work.
Run this to check if the app can start properly.
"""

import sys

def test_imports():
    """Test all required imports."""
    errors = []
    
    try:
        import streamlit as st
        print("✓ streamlit")
    except Exception as e:
        errors.append(f"streamlit: {e}")
    
    try:
        import pandas as pd
        print("✓ pandas")
    except Exception as e:
        errors.append(f"pandas: {e}")
    
    try:
        import bcrypt
        print("✓ bcrypt")
    except Exception as e:
        errors.append(f"bcrypt: {e}")
    
    try:
        from sqlalchemy import create_engine
        print("✓ sqlalchemy")
    except Exception as e:
        errors.append(f"sqlalchemy: {e}")
    
    try:
        import nbformat
        print("✓ nbformat")
    except Exception as e:
        errors.append(f"nbformat: {e}")
    
    try:
        import papermill
        print("✓ papermill")
    except Exception as e:
        errors.append(f"papermill: {e}")
    
    try:
        import sklearn
        print("✓ scikit-learn")
    except Exception as e:
        errors.append(f"scikit-learn: {e}")
    
    try:
        from reportlab.lib.pagesizes import letter
        print("✓ reportlab")
    except Exception as e:
        errors.append(f"reportlab: {e}")
    
    return errors

def test_local_imports():
    """Test local module imports."""
    errors = []
    
    try:
        from db import get_session, engine, Base
        print("✓ db module")
    except Exception as e:
        errors.append(f"db module: {e}")
    
    try:
        from models import User, Dataset, AnalysisHistory
        print("✓ models module")
    except Exception as e:
        errors.append(f"models module: {e}")
    
    try:
        from analyzer import analyze_csv
        print("✓ analyzer module")
    except Exception as e:
        errors.append(f"analyzer module: {e}")
    
    try:
        from notebook_generator import generate_ml_notebook
        print("✓ notebook_generator module")
    except Exception as e:
        errors.append(f"notebook_generator module: {e}")
    
    try:
        from notebook_runner import execute_notebook
        print("✓ notebook_runner module")
    except Exception as e:
        errors.append(f"notebook_runner module: {e}")
    
    try:
        from report_generator import generate_model_card_pdf
        print("✓ report_generator module")
    except Exception as e:
        errors.append(f"report_generator module: {e}")
    
    return errors

if __name__ == "__main__":
    print("=" * 60)
    print("VIZION STARTUP TEST")
    print("=" * 60)
    print("\nTesting external package imports...")
    print("-" * 60)
    
    ext_errors = test_imports()
    
    print("\nTesting local module imports...")
    print("-" * 60)
    
    local_errors = test_local_imports()
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if not ext_errors and not local_errors:
        print("\n✓ ALL TESTS PASSED!")
        print("\nYour app should start successfully.")
        print("Run: streamlit run app.py")
        sys.exit(0)
    else:
        print("\n✗ ERRORS FOUND:")
        for error in ext_errors + local_errors:
            print(f"  - {error}")
        print("\nFix these errors before deploying.")
        sys.exit(1)
