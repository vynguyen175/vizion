"""
Quick test script to verify ML notebook integration is working.
Run this before launching the full Streamlit app.
"""

import sys
import importlib

def test_imports():
    """Test if all required packages are installed."""
    print("Testing package imports...")
    print("=" * 60)
    
    required_packages = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('sklearn', 'scikit-learn'),
        ('nbformat', 'nbformat'),
        ('papermill', 'papermill'),
        ('nbconvert', 'nbconvert'),
        ('reportlab', 'reportlab'),
        ('jinja2', 'jinja2'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('streamlit', 'streamlit')
    ]
    
    all_good = True
    
    for package_import, package_name in required_packages:
        try:
            importlib.import_module(package_import)
            print(f"✅ {package_name:20s} - OK")
        except ImportError:
            print(f"❌ {package_name:20s} - MISSING")
            all_good = False
    
    print("=" * 60)
    
    if all_good:
        print("\n🎉 All packages installed successfully!")
        return True
    else:
        print("\n❌ Some packages are missing. Run:")
        print("   pip install -r requirements.txt")
        return False


def test_modules():
    """Test if custom modules can be imported."""
    print("\nTesting custom modules...")
    print("=" * 60)
    
    modules = [
        'notebook_generator',
        'notebook_runner',
        'report_generator',
        'analyzer',
        'models',
        'db'
    ]
    
    all_good = True
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module:25s} - OK")
        except Exception as e:
            print(f"❌ {module:25s} - ERROR: {str(e)[:40]}")
            all_good = False
    
    print("=" * 60)
    
    if all_good:
        print("\n🎉 All custom modules loaded successfully!")
        return True
    else:
        print("\n❌ Some modules have errors. Check the files above.")
        return False


def test_functions():
    """Test if key functions work."""
    print("\nTesting key functions...")
    print("=" * 60)
    
    try:
        import pandas as pd
        from notebook_generator import detect_column_types, suggest_ml_task
        
        # Create sample dataframe
        df = pd.DataFrame({
            'age': [25, 30, 35, 40],
            'salary': [50000, 60000, 70000, 80000],
            'department': ['IT', 'HR', 'IT', 'Finance'],
            'performance': ['Good', 'Excellent', 'Good', 'Average']
        })
        
        # Test column type detection
        col_types = detect_column_types(df)
        print(f"✅ detect_column_types    - OK")
        print(f"   Found: {len(col_types['numeric'])} numeric, {len(col_types['categorical'])} categorical")
        
        # Test ML task suggestion
        task = suggest_ml_task(df, 'performance')
        print(f"✅ suggest_ml_task        - OK")
        print(f"   Suggested: {task['task_type']}")
        
        print("=" * 60)
        print("\n🎉 All function tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Function test failed: {str(e)}")
        print("=" * 60)
        return False


def main():
    """Run all tests."""
    print("\n" + "🔍 VIZION ML INTEGRATION TEST".center(60))
    print("=" * 60 + "\n")
    
    test1 = test_imports()
    test2 = test_modules()
    test3 = test_functions()
    
    print("\n" + "=" * 60)
    print("FINAL RESULT".center(60))
    print("=" * 60)
    
    if test1 and test2 and test3:
        print("\n✅ ALL TESTS PASSED!")
        print("\nYou're ready to run:")
        print("   streamlit run app.py")
        print("\n🚀 Vizion ML Notebook integration is ready!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before running the app.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
