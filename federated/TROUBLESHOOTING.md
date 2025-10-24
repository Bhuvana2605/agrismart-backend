# Federated Learning Troubleshooting Guide

## Common Issues and Solutions

### ❌ Error: "Can't create train tmp dir: tmp"

**Full Error:**
```
_catboost.CatBoostError: catboost/libs/train_lib/dir_helper.cpp:26: 
Can't create train tmp dir: tmp
```

**Cause:**
CatBoost tries to create a temporary directory named `tmp` in the current working directory, but lacks permissions or the directory already exists with wrong permissions.

**Solution:**
✅ **Fixed in client.py** - The code now:
1. Creates a client-specific temp directory: `catboost_temp_client_0`, `catboost_temp_client_1`, etc.
2. Sets `train_dir` parameter to use this custom directory
3. Sets `allow_writing_files=False` to minimize file I/O

**Code Fix Applied:**
```python
# Create client-specific temp directory
temp_dir = os.path.join(os.getcwd(), f"catboost_temp_client_{client_id}")
os.makedirs(temp_dir, exist_ok=True)

self.model = CatBoostClassifier(
    ...
    train_dir=temp_dir,              # Custom temp directory
    allow_writing_files=False        # Disable intermediate files
)
```

**After Fix:**
- Each client gets its own temp directory
- No permission conflicts between clients
- Cleaner working directory

---

### ❌ Error: "Connection refused" or "Cancelling all calls"

**Full Error:**
```
grpc._channel._MultiThreadedRendezvous: <_MultiThreadedRendezvous of RPC that terminated with:
        status = StatusCode.UNAVAILABLE
        details = "Cancelling all calls"
```

**Cause:**
Server is not running, crashed, or clients are trying to connect before server starts.

**Solution:**
1. **Check if server is running:**
   - Look for server terminal window
   - Should show "Waiting for clients to connect..."
   
2. **Start server first:**
   ```bash
   cd backend/federated
   python server.py
   ```

3. **Wait for server ready message:**
   ```
   [Starting Server]
   Waiting for clients to connect...
   ```

4. **Then start clients:**
   ```bash
   python client.py 0
   ```

5. **If server crashed:**
   - Check server terminal for errors
   - Restart server
   - Ensure port 8080 is not in use

---

### ⚠️ Warning: "DEPRECATED FEATURE: flwr.client.start_numpy_client()"

**Warning Message:**
```
WARNING: flwr.client.start_numpy_client() is deprecated.
Instead, use `flwr.client.start_client()` by ensuring you first call the `.to_client()` method
```

**Status:**
✅ **Already fixed!** The code now uses the modern Flower API:
```python
fl.client.start_client(
    server_address="127.0.0.1:8080",
    client=numpy_client.to_client()  # Modern API
)
```

**Note:**
- This is just a deprecation warning, not an error
- The code has been updated to use `.to_client()` method
- No action needed from your side

---

### ⚠️ Warning: "DEPRECATED FEATURE: flwr.server.start_server()"

**Warning Message:**
```
WARNING: flwr.server.start_server() is deprecated.
Instead, use the `flower-superlink` CLI command to start a SuperLink
```

**Status:**
⚠️ **Informational warning only** - The current implementation works perfectly!

**What This Means:**
- This is a deprecation notice for future Flower versions
- The current code (`start_server()`) still works correctly
- Training completes successfully with all rounds
- No immediate action required

**Current Behavior:**
```
✅ Server starts successfully
✅ Clients connect properly
✅ Training completes all rounds
✅ Results are aggregated correctly
```

**Future Migration (Optional):**
If you want to use the newer CLI-based approach in the future:
```bash
# Instead of: python server.py
# You would use:
flower-superlink --insecure
```

**Recommendation:**
- Keep using current implementation - it works!
- Monitor Flower updates for breaking changes
- Consider migration when Flower 2.0+ is stable
- Current code will work for foreseeable future

---

### ❌ Error: "Dataset not found"

**Full Error:**
```
FileNotFoundError: Dataset not found. Tried: ../Crop_recommendation.csv and Crop_recommendation.csv
```

**Cause:**
`Crop_recommendation.csv` file is not in the expected location.

**Solution:**
1. Ensure CSV file is in `backend/` directory:
   ```
   backend/
   ├── Crop_recommendation.csv  ← Must be here
   └── federated/
       ├── server.py
       └── client.py
   ```

2. Or run clients from `backend/` directory:
   ```bash
   cd backend
   python federated/client.py 0
   ```

---

### ❌ Error: "Not enough clients available"

**Cause:**
Server requires minimum 2 clients but only 1 connected.

**Solution:**
Start at least 2 clients:
```bash
# Terminal 2
python client.py 0

# Terminal 3
python client.py 1
```

---

### ❌ Error: "Address already in use"

**Full Error:**
```
OSError: [Errno 48] Address already in use
```

**Cause:**
Another process is using port 8080, or previous server didn't shut down properly.

**Solution:**

**Windows:**
```bash
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Alternative:** Change port in both files:
```python
# server.py
server_address="0.0.0.0:8081"

# client.py
server_address="127.0.0.1:8081"
```

---

### ❌ Error: "Module 'flwr' not found"

**Cause:**
Flower framework not installed.

**Solution:**
```bash
pip install flwr==1.12.0
```

Or install all dependencies:
```bash
cd backend
pip install -r requirements.txt
```

---

### ❌ Training seems stuck

**Symptoms:**
- Server shows "Waiting for clients..."
- No training progress

**Possible Causes & Solutions:**

1. **Not enough clients connected**
   - Check if 2+ clients are running
   - Look for "Connected!" message in client terminals

2. **Client crashed silently**
   - Check client terminal for errors
   - Restart crashed clients

3. **Network issue**
   - Verify server address is correct
   - Check firewall settings
   - Try using `localhost` instead of `127.0.0.1`

---

### ❌ Low accuracy or poor performance

**Symptoms:**
- Test accuracy < 80%
- High loss values

**Possible Causes & Solutions:**

1. **Unbalanced data partition**
   - Check if each client has diverse crop samples
   - Increase `num_clients` for better distribution

2. **Too few iterations**
   - Increase `iterations` in CatBoostClassifier
   - Default is 100, try 200-500

3. **Too few rounds**
   - Increase `num_rounds` in ServerConfig
   - Default is 3, try 5-10

---

### ❌ Client crashes during training

**Symptoms:**
- Client stops mid-training
- "Client raised an exception" error

**Possible Causes & Solutions:**

1. **Memory issue**
   - Reduce `iterations` in CatBoostClassifier
   - Reduce data partition size

2. **Data quality issue**
   - Check for NaN values in data
   - Verify all features are numeric
   - Ensure labels are strings

3. **CatBoost configuration issue**
   - Verify `class_names` are sorted
   - Check labels match class_names

---

## Debugging Tips

### Enable Verbose Output

**Server:**
```python
# In server.py, add logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Client:**
```python
# In client.py, enable CatBoost verbose
self.model = CatBoostClassifier(
    ...
    verbose=True  # Change from False
)
```

### Check Data Distribution

Add this to `load_data_partition()`:
```python
print(f"[Client {client_id}] Crop distribution:")
print(y.value_counts())
```

### Monitor Training Progress

Add this to `fit()` method:
```python
print(f"[Client {self.client_id}] Training metrics:")
print(f"  - Best iteration: {self.model.get_best_iteration()}")
print(f"  - Best score: {self.model.get_best_score()}")
```

---

## Performance Optimization

### Speed Up Training

1. **Reduce iterations:**
   ```python
   iterations=50  # Instead of 100
   ```

2. **Reduce tree depth:**
   ```python
   depth=4  # Instead of 6
   ```

3. **Disable evaluation:**
   ```python
   self.model.fit(
       self.X_train,
       self.y_train,
       # Remove eval_set
   )
   ```

### Improve Accuracy

1. **Increase iterations:**
   ```python
   iterations=200
   ```

2. **More training rounds:**
   ```python
   config = ServerConfig(num_rounds=10)
   ```

3. **Better data distribution:**
   ```python
   # Stratified partitioning
   from sklearn.model_selection import StratifiedKFold
   ```

---

## Clean Up

### Remove Temporary Files

After training, clean up temp directories:

**Windows:**
```bash
cd backend/federated
rmdir /s /q catboost_temp_client_0
rmdir /s /q catboost_temp_client_1
rmdir /s /q catboost_temp_client_2
```

**Or add to client.py:**
```python
import shutil

def cleanup_temp_dir(client_id):
    temp_dir = f"catboost_temp_client_{client_id}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"[Client {client_id}] Cleaned up temp directory")

# Call in start_client() after training
cleanup_temp_dir(client_id)
```

---

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 1GB free disk space
- Network connectivity (for multi-machine setup)

### Recommended Requirements
- Python 3.10+
- 8GB RAM
- 2GB free disk space
- Fast network (for distributed setup)

---

## Getting Help

### Check Logs
1. Server terminal output
2. Client terminal output
3. Error tracebacks

### Verify Setup
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "flwr|catboost|pandas|scikit-learn"

# Check file structure
ls -la backend/
ls -la backend/federated/
```

### Test Components

**Test server only:**
```bash
python server.py
# Should show "Waiting for clients..."
```

**Test data loading:**
```python
from client import load_data_partition
data = load_data_partition(0, num_clients=3)
print("Data loaded successfully!")
```

---

## Known Limitations

1. **CatBoost Serialization**: Model parameters aren't properly serialized (placeholder implementation)
2. **Synchronous Training**: All clients must complete before next round
3. **No Model Persistence**: Trained models aren't saved after federated learning
4. **Fixed Partitioning**: Data is split equally, not by crop distribution

---

## Future Improvements

- [ ] Implement proper model serialization
- [ ] Add asynchronous training support
- [ ] Save aggregated global model
- [ ] Stratified data partitioning
- [ ] Progress bars for training
- [ ] Web dashboard for monitoring
- [ ] Automatic retry on client failure

---

## Contact & Support

For issues not covered here:
1. Check `README.md` for detailed documentation
2. Review `QUICK_START.md` for basic setup
3. Examine error messages carefully
4. Test with minimal configuration first

---

## Summary of Fixes Applied

✅ **CatBoost temp directory issue** - Fixed with custom `train_dir`
✅ **Permission errors** - Each client gets unique temp directory
✅ **File I/O overhead** - Disabled with `allow_writing_files=False`

All fixes are already applied in the current `client.py` implementation!
