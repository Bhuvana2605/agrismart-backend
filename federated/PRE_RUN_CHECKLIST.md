# Pre-Run Checklist for Federated Learning

Before starting federated learning, verify all requirements are met:

## ✅ Prerequisites Checklist

### 1. Python Environment
- [ ] Python 3.8+ installed
  ```bash
  python --version
  # Should show: Python 3.8.x or higher
  ```

### 2. Dependencies Installed
- [ ] All required packages installed
  ```bash
  pip list | findstr "flwr catboost pandas scikit-learn"
  ```
  
  **Expected output:**
  ```
  catboost         1.2.7
  flwr             1.12.0
  pandas           2.2.3
  scikit-learn     1.5.2
  ```

- [ ] If missing, install:
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

### 3. Dataset Available
- [ ] `Crop_recommendation.csv` exists in `backend/` directory
  ```bash
  dir ..\Crop_recommendation.csv
  # Or from backend directory:
  dir Crop_recommendation.csv
  ```

- [ ] Dataset has correct structure (2200 rows, 8 columns)
  ```python
  import pandas as pd
  df = pd.read_csv("../Crop_recommendation.csv")
  print(f"Shape: {df.shape}")  # Should be (2200, 8)
  print(f"Columns: {list(df.columns)}")
  ```

### 4. Port Availability
- [ ] Port 8080 is not in use
  ```bash
  netstat -ano | findstr :8080
  # Should return nothing if port is free
  ```

- [ ] If port is in use, kill the process or change port in both files

### 5. File Structure
- [ ] All federated learning files exist
  ```
  backend/
  ├── Crop_recommendation.csv     ✓
  └── federated/
      ├── server.py               ✓
      ├── client.py               ✓
      ├── README.md               ✓
      ├── QUICK_START.md          ✓
      └── TROUBLESHOOTING.md      ✓
  ```

### 6. Terminal Setup
- [ ] Have 3 terminal windows ready:
  - Terminal 1: For server
  - Terminal 2: For client 0
  - Terminal 3: For client 1

---

## 🚀 Quick Verification Script

Run this to verify everything at once:

```python
# verify_setup.py
import sys
import os
import subprocess

print("=" * 60)
print("FEDERATED LEARNING SETUP VERIFICATION")
print("=" * 60)

# Check Python version
print("\n[1/5] Checking Python version...")
version = sys.version_info
if version.major >= 3 and version.minor >= 8:
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
else:
    print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")

# Check packages
print("\n[2/5] Checking installed packages...")
required = ["flwr", "catboost", "pandas", "sklearn"]
for pkg in required:
    try:
        __import__(pkg)
        print(f"✓ {pkg} installed")
    except ImportError:
        print(f"✗ {pkg} NOT installed")

# Check dataset
print("\n[3/5] Checking dataset...")
dataset_paths = ["../Crop_recommendation.csv", "Crop_recommendation.csv"]
dataset_found = False
for path in dataset_paths:
    if os.path.exists(path):
        print(f"✓ Dataset found at: {path}")
        dataset_found = True
        break
if not dataset_found:
    print("✗ Dataset NOT found")

# Check files
print("\n[4/5] Checking federated learning files...")
files = ["server.py", "client.py"]
for file in files:
    if os.path.exists(file):
        print(f"✓ {file} exists")
    else:
        print(f"✗ {file} NOT found")

# Check port
print("\n[5/5] Checking port 8080...")
result = subprocess.run(
    ["netstat", "-ano"],
    capture_output=True,
    text=True
)
if ":8080" in result.stdout:
    print("⚠ Port 8080 is in use (may need to kill process)")
else:
    print("✓ Port 8080 is available")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nIf all checks passed, you're ready to start!")
print("Run: python server.py (in terminal 1)")
print("Then: python client.py 0 (in terminal 2)")
print("Then: python client.py 1 (in terminal 3)")
```

Save as `verify_setup.py` in `backend/federated/` and run:
```bash
cd backend/federated
python verify_setup.py
```

---

## 📋 Step-by-Step Startup

Once all checks pass, follow this exact sequence:

### Step 1: Start Server (Terminal 1)
```bash
cd backend/federated
python server.py
```

**Wait for:**
```
[Starting Server]
Waiting for clients to connect...
```

### Step 2: Start Client 0 (Terminal 2)
```bash
cd backend/federated
python client.py 0
```

**Wait for:**
```
[Client 0] Connecting to server at 127.0.0.1:8080...
[Client 0] Ready for federated training
```

### Step 3: Start Client 1 (Terminal 3)
```bash
cd backend/federated
python client.py 1
```

**Training starts automatically!**

---

## ⚠️ Common Issues During Startup

### Server doesn't start
- Check if port 8080 is in use
- Verify flwr is installed: `pip show flwr`
- Check for error messages in terminal

### Client can't connect
- Ensure server is running first
- Check server shows "Waiting for clients..."
- Verify server address is correct (127.0.0.1:8080)

### Dataset not found
- Verify CSV file location
- Check you're in the correct directory
- Try absolute path if needed

### CatBoost temp directory error
- ✅ Already fixed in code
- Each client creates its own temp directory
- No manual action needed

---

## 🎯 Success Indicators

You'll know everything is working when you see:

### Server Terminal
```
INFO: FL starting
INFO: [ROUND 1]
INFO: fit progress: (1, 0.05, {'train_accuracy': 0.95})
```

### Client Terminals
```
[Client 0] Starting training round...
[Client 0] Training completed
  - Training accuracy: 95.23%
[Client 0] Evaluation completed
  - Test accuracy: 94.56%
```

---

## 📞 Need Help?

If any check fails:
1. Review the specific error message
2. Check `TROUBLESHOOTING.md` for solutions
3. Verify all prerequisites are met
4. Try running verification script again

---

## 🔄 Quick Reset

If something goes wrong, reset everything:

```bash
# Stop all processes (Ctrl+C in each terminal)

# Clean up temp directories
cd backend/federated
rmdir /s /q catboost_temp_client_0
rmdir /s /q catboost_temp_client_1
rmdir /s /q catboost_temp_client_2

# Restart from Step 1
```

---

## ✨ Ready to Go!

Once all checks pass:
- ✅ Python 3.8+ installed
- ✅ All packages installed
- ✅ Dataset available
- ✅ Port 8080 free
- ✅ Files in place
- ✅ Terminals ready

**You're ready to start federated learning!** 🚀

Follow QUICK_START.md for the 3-step startup process.
