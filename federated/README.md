# Federated Learning Setup for Crop Recommendation System

## Overview
This federated learning implementation uses the **Flower framework** to enable distributed training of crop recommendation models across multiple clients without sharing raw data.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flower Server (0.0.0.0:8080)             │
│                                                              │
│  Strategy: FedAvg (Federated Averaging)                     │
│  Rounds: 3                                                   │
│  Min Clients: 2                                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Client 0│ │Client 1│ │Client 2│
   │        │ │        │ │        │
   │ 733    │ │ 733    │ │ 734    │
   │samples │ │samples │ │samples │
   └────────┘ └────────┘ └────────┘
```

## Files

### 1. `server.py`
Federated learning server that coordinates training across clients.

**Features:**
- FedAvg (Federated Averaging) strategy
- 3 training rounds
- Requires minimum 2 clients
- Listens on `0.0.0.0:8080`

### 2. `client.py`
Federated learning client that trains on local data partition.

**Features:**
- CatBoost classifier with 100 iterations
- Automatic data partitioning
- Local training and evaluation
- Connects to server at `127.0.0.1:8080`

## Installation

Ensure all dependencies are installed:

```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- `flwr==1.12.0` (Flower framework)
- `catboost==1.2.7`
- `pandas==2.2.3`
- `scikit-learn==1.5.2`

## Usage

### Step 1: Start the Server

Open a terminal and run:

```bash
cd backend/federated
python server.py
```

**Expected Output:**
```
======================================================================
FEDERATED LEARNING SERVER - CROP RECOMMENDATION SYSTEM
======================================================================

[Server Configuration]
  - Strategy: FedAvg (Federated Averaging)
  - Training Rounds: 3
  - Minimum Fit Clients: 2
  - Minimum Evaluate Clients: 2
  - Minimum Available Clients: 2
  - Server Address: 0.0.0.0:8080

[Server Status]
✓ Strategy configured: FedAvg
✓ Server configuration set

[Starting Server]
Waiting for clients to connect...
(Press Ctrl+C to stop the server)
```

### Step 2: Start Clients

Open **separate terminals** for each client:

**Terminal 2 - Client 0:**
```bash
cd backend/federated
python client.py 0
```

**Terminal 3 - Client 1:**
```bash
cd backend/federated
python client.py 1
```

**Terminal 4 - Client 2 (Optional):**
```bash
cd backend/federated
python client.py 2
```

**Expected Client Output:**
```
======================================================================
FEDERATED LEARNING CLIENT 0 - CROP RECOMMENDATION SYSTEM
======================================================================

[Client 0] Loading data partition...
[Client 0] Dataset loaded: 2200 total samples
[Client 0] Partition assigned:
  - Partition range: [0:733]
  - Partition size: 733 samples
  - Percentage of total: 33.3%

[Client 0] Data split completed:
  - Training samples: 586
  - Test samples: 147
  - Unique crops: 22

[Client 0] Initialized
  - Training samples: 586
  - Test samples: 147
  - Unique crops in partition: 22

[Client 0] Connecting to server at 127.0.0.1:8080...
[Client 0] Ready for federated training
```

### Step 3: Training Process

Once minimum clients (2) connect, training begins automatically:

**Server shows:**
```
INFO flower 2024-10-19 22:30:00,000 | app.py:163 | Starting Flower server
INFO flower 2024-10-19 22:30:05,000 | server.py:89 | FL starting
INFO flower 2024-10-19 22:30:05,000 | server.py:102 | [ROUND 1]
INFO flower 2024-10-19 22:30:10,000 | server.py:176 | fit progress: (1, 0.05, {'train_accuracy': 0.95})
INFO flower 2024-10-19 22:30:15,000 | server.py:215 | evaluate progress: (1, 0.05, {'test_accuracy': 0.94})
...
```

**Clients show:**
```
[Client 0] Starting training round...
[Client 0] Training completed
  - Training accuracy: 95.23%
  - Samples trained: 586

[Client 0] Starting evaluation...
[Client 0] Evaluation completed
  - Test accuracy: 94.56%
  - Test loss: 0.0544
  - Samples evaluated: 147
```

## Data Partitioning

The dataset is automatically partitioned among clients:

| Client | Samples | Percentage | Train | Test |
|--------|---------|------------|-------|------|
| 0      | 733     | 33.3%      | 586   | 147  |
| 1      | 733     | 33.3%      | 586   | 147  |
| 2      | 734     | 33.4%      | 587   | 147  |
| **Total** | **2200** | **100%** | **1760** | **440** |

- Each client gets roughly equal portion
- Data is shuffled before partitioning (random_state=42)
- Each partition is split 80/20 for train/test

## Training Configuration

### Server Configuration
```python
strategy = FedAvg(
    fraction_fit=1.0,              # Use 100% of available clients
    fraction_evaluate=1.0,         # Use 100% for evaluation
    min_fit_clients=2,             # Minimum 2 clients for training
    min_evaluate_clients=2,        # Minimum 2 clients for evaluation
    min_available_clients=2,       # Wait for 2 clients
)

config = ServerConfig(
    num_rounds=3                   # 3 federated rounds
)
```

### Client Configuration
```python
model = CatBoostClassifier(
    iterations=100,                # 100 boosting iterations
    learning_rate=0.1,             # Learning rate
    depth=6,                       # Tree depth
    loss_function='MultiClass',    # Multi-class classification
    eval_metric='Accuracy',        # Evaluation metric
    verbose=False,                 # Suppress output
    class_names=sorted_crop_names  # Sorted crop names
)
```

## Federated Learning Process

### Round 1
1. Server sends initial configuration to clients
2. Each client trains on local data (100 iterations)
3. Clients send training metrics back to server
4. Server aggregates results using FedAvg
5. Each client evaluates on local test data
6. Clients send evaluation metrics to server

### Rounds 2-3
Same process repeats with updated configurations

### Final Result
- Server aggregates all client results
- Each client has a trained model on local data
- No raw data is shared between clients

## Command Line Arguments

### Server
```bash
python server.py
# No arguments needed
```

### Client
```bash
python client.py <client_id>

# Examples:
python client.py 0  # Start client 0
python client.py 1  # Start client 1
python client.py 2  # Start client 2
```

**Client ID:**
- Must be a non-negative integer (0, 1, 2, ...)
- Should be unique for each client
- Determines which data partition the client receives

## Stopping the System

### Stop Server
Press `Ctrl+C` in the server terminal:
```
[Server Shutdown]
✓ Server stopped gracefully
```

### Stop Clients
Press `Ctrl+C` in each client terminal:
```
[Client 0] Interrupted by user
```

## Troubleshooting

### Issue: "Dataset not found"
**Solution:** Ensure `Crop_recommendation.csv` is in the `backend/` directory:
```bash
ls backend/Crop_recommendation.csv
```

### Issue: "Connection refused"
**Solution:** 
1. Ensure server is running first
2. Check server is listening on port 8080
3. Verify no firewall blocking port 8080

### Issue: "Not enough clients"
**Solution:** Start at least 2 clients (min_available_clients=2)

### Issue: Client crashes during training
**Solution:** 
1. Check data partition has enough samples
2. Ensure all crop classes are present in partition
3. Verify CatBoost is installed correctly

## Advanced Usage

### Change Number of Clients
Edit `client.py` line 208:
```python
data_partition = load_data_partition(client_id, num_clients=5)  # Change to 5 clients
```

Also update server `min_available_clients` in `server.py` line 39:
```python
min_available_clients=5,  # Wait for 5 clients
```

### Change Number of Rounds
Edit `server.py` line 44:
```python
config = ServerConfig(
    num_rounds=10  # Change to 10 rounds
)
```

### Change Training Iterations
Edit `client.py` line 39:
```python
self.model = CatBoostClassifier(
    iterations=200,  # Change to 200 iterations
    ...
)
```

## Benefits of Federated Learning

1. **Privacy**: Raw data never leaves client devices
2. **Scalability**: Can train on distributed data sources
3. **Collaboration**: Multiple parties can collaborate without sharing data
4. **Compliance**: Meets data privacy regulations (GDPR, HIPAA)
5. **Bandwidth**: Only model updates are shared, not raw data

## Limitations

1. **Communication Overhead**: Multiple rounds of communication needed
2. **Heterogeneity**: Clients may have different data distributions
3. **Stragglers**: Slow clients can delay training
4. **Model Serialization**: CatBoost doesn't easily serialize to NumPy arrays

## Future Improvements

- [ ] Implement proper CatBoost model serialization
- [ ] Add differential privacy
- [ ] Support for heterogeneous data distributions
- [ ] Client-side model caching
- [ ] Asynchronous federated learning
- [ ] Secure aggregation
- [ ] Model compression for faster communication

## References

- [Flower Framework Documentation](https://flower.dev/)
- [Federated Learning Paper](https://arxiv.org/abs/1602.05629)
- [CatBoost Documentation](https://catboost.ai/)

## License

This federated learning implementation is part of the Crop Recommendation System project.
