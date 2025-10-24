# Federated Learning Quick Start Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Server
Open a terminal:
```bash
cd backend/federated
python server.py
```
✅ Server will wait for clients to connect

### Step 2: Start Client 0
Open a **new terminal**:
```bash
cd backend/federated
python client.py 0
```
✅ Client 0 will connect and wait

### Step 3: Start Client 1
Open **another new terminal**:
```bash
cd backend/federated
python client.py 1
```
✅ Training will start automatically!

---

## 📊 What Happens

```
Terminal 1 (Server)          Terminal 2 (Client 0)         Terminal 3 (Client 1)
─────────────────────        ─────────────────────         ─────────────────────
[Server Starting]            
Waiting for clients...       
                             [Client 0 Connecting]
                             Loading data...
                             Connected!
                                                           [Client 1 Connecting]
                                                           Loading data...
                                                           Connected!
[Round 1 Starting]
Sending config...            [Training Round 1]            [Training Round 1]
                             Training on 586 samples...    Training on 586 samples...
                             Accuracy: 95.23%              Accuracy: 94.87%
Aggregating results...       
                             [Evaluating]                  [Evaluating]
                             Test Accuracy: 94.56%         Test Accuracy: 93.88%
[Round 1 Complete]

[Round 2 Starting]           [Training Round 2]            [Training Round 2]
...                          ...                           ...
```

---

## 🎯 Expected Results

After 3 rounds, you should see:

**Server Output:**
```
INFO: Round 1 complete - Avg loss: 0.05
INFO: Round 2 complete - Avg loss: 0.04
INFO: Round 3 complete - Avg loss: 0.03
INFO: Federated learning complete!
```

**Client Output:**
```
[Client 0] Training completed successfully
Final Test Accuracy: ~94-96%
```

---

## 🛠️ Windows Users

Use the batch script for easier startup:
```bash
cd backend/federated
run_federated.bat
```

Then select:
- Option 1 in first terminal (Server)
- Option 2 in second terminal (Client 0)
- Option 3 in third terminal (Client 1)

---

## ⚙️ Configuration

### Default Settings
- **Clients**: 3 (but minimum 2 required)
- **Rounds**: 3
- **Iterations per client**: 100
- **Data split**: 80% train, 20% test
- **Server address**: 0.0.0.0:8080

### Data Distribution
```
Total Dataset: 2200 samples

Client 0: 733 samples (33.3%)
  ├─ Train: 586 samples
  └─ Test:  147 samples

Client 1: 733 samples (33.3%)
  ├─ Train: 586 samples
  └─ Test:  147 samples

Client 2: 734 samples (33.4%)
  ├─ Train: 587 samples
  └─ Test:  147 samples
```

---

## 🔍 Monitoring

### Server Metrics
- Number of clients connected
- Training loss per round
- Evaluation accuracy per round
- Aggregated model performance

### Client Metrics
- Training accuracy
- Test accuracy
- Number of samples trained
- Training time per round

---

## 🐛 Common Issues

### "Can't create train tmp dir: tmp"
**Problem:** CatBoost permission error
**Solution:** ✅ Already fixed! Each client now uses its own temp directory
- Creates: `catboost_temp_client_0`, `catboost_temp_client_1`, etc.
- No manual action needed

### "Connection refused"
**Problem:** Server not running
**Solution:** Start server first (Step 1)

### "Dataset not found"
**Problem:** CSV file missing
**Solution:** Ensure `Crop_recommendation.csv` is in `backend/` folder

### "Not enough clients"
**Problem:** Only 1 client connected
**Solution:** Start at least 2 clients (minimum requirement)

### Training seems stuck
**Problem:** Waiting for minimum clients
**Solution:** Check if 2+ clients are connected

### More Issues?
See `TROUBLESHOOTING.md` for comprehensive debugging guide

---

## 🎓 Understanding Federated Learning

### What's Happening?

1. **Server** coordinates training across clients
2. **Clients** train on their local data (no data sharing!)
3. **FedAvg** aggregates model updates from all clients
4. Process repeats for 3 rounds

### Why Federated Learning?

✅ **Privacy**: Data stays on client devices
✅ **Scalability**: Train on distributed data
✅ **Collaboration**: Multiple parties can collaborate
✅ **Compliance**: Meets privacy regulations

### Data Flow

```
Round 1:
  Server → Clients: "Start training with config"
  Clients → Server: "Here are my model updates"
  Server: Aggregates updates using FedAvg
  
Round 2:
  Server → Clients: "Train with updated config"
  Clients → Server: "Here are my improved updates"
  Server: Aggregates again
  
Round 3:
  (Same process)
  
Final:
  Each client has trained model
  No raw data was shared!
```

---

## 📈 Performance Expectations

### Training Time
- **Per Round**: ~10-30 seconds (depends on hardware)
- **Total (3 rounds)**: ~30-90 seconds
- **Per Client**: 100 CatBoost iterations

### Accuracy
- **Expected**: 93-96% test accuracy
- **Varies by**: Data partition, crop distribution
- **Improves**: Over multiple rounds

---

## 🔄 Running Multiple Experiments

### Experiment 1: 2 Clients
```bash
# Terminal 1
python server.py

# Terminal 2
python client.py 0

# Terminal 3
python client.py 1
```

### Experiment 2: 3 Clients
```bash
# Terminal 1
python server.py

# Terminal 2
python client.py 0

# Terminal 3
python client.py 1

# Terminal 4
python client.py 2
```

---

## 📝 Next Steps

1. ✅ Complete this quick start
2. 📖 Read full `README.md` for details
3. 🔧 Experiment with different configurations
4. 📊 Analyze training metrics
5. 🚀 Integrate with main API

---

## 💡 Tips

- **Start server first**, then clients
- **Use separate terminals** for each process
- **Wait for "Ready"** message before starting next client
- **Press Ctrl+C** to stop any process gracefully
- **Check logs** for detailed training information

---

## 🆘 Need Help?

1. Check `README.md` for detailed documentation
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Ensure dataset exists: `ls ../Crop_recommendation.csv`
4. Check Python version: `python --version` (should be 3.8+)

---

## ✨ Success Indicators

You'll know it's working when you see:

✅ Server shows "FL starting"
✅ Clients show "Training completed"
✅ Accuracy metrics are displayed
✅ Multiple rounds complete successfully
✅ No error messages

Happy Federated Learning! 🎉
