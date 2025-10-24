"""
Federated Learning Setup Verification Script
Checks if all prerequisites are met before starting federated learning
"""

import sys
import os
import subprocess

def main():
    print("=" * 60)
    print("FEDERATED LEARNING SETUP VERIFICATION")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Check Python version
    print("\n[1/5] Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        all_checks_passed = False
    
    # Check packages
    print("\n[2/5] Checking installed packages...")
    required_packages = {
        "flwr": "Flower framework",
        "catboost": "CatBoost classifier",
        "pandas": "Data manipulation",
        "sklearn": "Scikit-learn"
    }
    
    for pkg, description in required_packages.items():
        try:
            __import__(pkg)
            print(f"✓ {pkg} installed ({description})")
        except ImportError:
            print(f"✗ {pkg} NOT installed ({description})")
            all_checks_passed = False
    
    # Check dataset
    print("\n[3/5] Checking dataset...")
    dataset_paths = ["../Crop_recommendation.csv", "Crop_recommendation.csv"]
    dataset_found = False
    
    for path in dataset_paths:
        if os.path.exists(path):
            try:
                import pandas as pd
                df = pd.read_csv(path)
                print(f"✓ Dataset found at: {path}")
                print(f"  - Shape: {df.shape}")
                print(f"  - Columns: {list(df.columns)}")
                dataset_found = True
                break
            except Exception as e:
                print(f"⚠ Dataset found but error reading: {str(e)}")
                all_checks_passed = False
    
    if not dataset_found:
        print("✗ Dataset NOT found")
        print("  Expected locations:")
        for path in dataset_paths:
            print(f"    - {os.path.abspath(path)}")
        all_checks_passed = False
    
    # Check files
    print("\n[4/5] Checking federated learning files...")
    required_files = {
        "server.py": "Federated server",
        "client.py": "Federated client"
    }
    
    for file, description in required_files.items():
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✓ {file} exists ({description}, {size} bytes)")
        else:
            print(f"✗ {file} NOT found ({description})")
            all_checks_passed = False
    
    # Check port
    print("\n[5/5] Checking port 8080...")
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if ":8080" in result.stdout:
            print("⚠ Port 8080 is in use")
            print("  You may need to:")
            print("  1. Kill the process using the port")
            print("  2. Or change the port in server.py and client.py")
        else:
            print("✓ Port 8080 is available")
    except Exception as e:
        print(f"⚠ Could not check port status: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    if all_checks_passed:
        print("\n✅ All checks passed! You're ready to start!")
        print("\nNext steps:")
        print("1. Terminal 1: python server.py")
        print("2. Terminal 2: python client.py 0")
        print("3. Terminal 3: python client.py 1")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install packages: pip install -r ../requirements.txt")
        print("- Ensure dataset is in backend/ directory")
        print("- Check Python version: python --version")
    
    print("\nFor detailed help, see:")
    print("- QUICK_START.md - Quick start guide")
    print("- TROUBLESHOOTING.md - Troubleshooting guide")
    print("- PRE_RUN_CHECKLIST.md - Complete checklist")
    
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
