# CatBoost Training Fix - String Labels vs Encoded Labels

## Error
```
_catboost.CatBoostError: catboost/private/libs/target/target_converter.cpp:279: 
Not all class names are numeric, but specified target data is
```

## Root Cause
When using `class_names` parameter in CatBoostClassifier, CatBoost expects **string labels** (e.g., 'rice', 'wheat'), but we were passing **numeric encoded labels** (e.g., 0, 1, 2) from LabelEncoder.

## Solution
Remove label encoding and train CatBoost directly with original string labels.

---

## Changes Made to `train_model.py`

### 1. Removed LabelEncoder (Line 1-6)
```python
# BEFORE
from sklearn.preprocessing import LabelEncoder

# AFTER
# (removed - not needed)
```

### 2. Removed Label Encoding (Lines 39-49)
```python
# BEFORE
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,  # Using encoded labels
    ...
)

# AFTER
# Note: CatBoost with class_names expects string labels, not encoded integers
# So we use y directly (string labels) instead of encoding

X_train, X_test, y_train, y_test = train_test_split(
    X, y,  # Using original string labels
    ...
)
```

### 3. Updated Classification Report (Line 114)
```python
# BEFORE
target_names=label_encoder.classes_

# AFTER
target_names=sorted_crop_names
```

### 4. Updated Return Value (Line 170)
```python
# BEFORE
return model, label_encoder, test_accuracy

# AFTER
return model, sorted_crop_names, test_accuracy
```

---

## How It Works Now

### Training Flow
```
1. Load dataset with string labels: ['rice', 'wheat', 'cotton', ...]
2. Create sorted crop names: ['apple', 'banana', 'chickpea', ...]
3. Create class mapping: {0: 'apple', 1: 'banana', ...}
4. Train CatBoost with:
   - X_train (features)
   - y_train (STRING labels: 'rice', 'wheat', etc.)
   - class_names=['apple', 'banana', ...] (sorted)
5. CatBoost internally handles the encoding
6. Save model and class_mapping.json
```

### Key Points
- ✅ CatBoost with `class_names` parameter handles encoding internally
- ✅ We pass string labels directly: 'rice', 'wheat', 'cotton'
- ✅ CatBoost maps them to the sorted `class_names` list
- ✅ Model predictions return indices that map to sorted crop names
- ✅ Our class_mapping.json converts indices back to names

---

## Complete Fixed Code Section

```python
# Separate features and target
X = df.drop('label', axis=1)
y = df['label']  # Keep as strings: 'rice', 'wheat', etc.

# Create class mapping (sorted list of unique crop names)
sorted_crop_names = sorted(y.unique())
class_mapping = {i: name for i, name in enumerate(sorted_crop_names)}

# Note: CatBoost with class_names expects string labels, not encoded integers
# So we use y directly (string labels) instead of encoding

print("✓ Data preprocessed")
print(f"  - Feature shape: {X.shape}")
print(f"  - Target classes: {len(sorted_crop_names)}")
print(f"  - Class mapping created: {len(class_mapping)} crops")

# Split with string labels
X_train, X_test, y_train, y_test = train_test_split(
    X, y,  # Use original string labels
    test_size=0.2, 
    random_state=42, 
    stratify=y  # Stratify by original labels
)

# Train with class_names parameter
model = CatBoostClassifier(
    iterations=500,
    learning_rate=0.1,
    depth=6,
    loss_function='MultiClass',
    eval_metric='Accuracy',
    random_seed=42,
    verbose=100,
    early_stopping_rounds=50,
    class_names=sorted_crop_names  # Sorted crop names
)

# Fit with string labels
model.fit(
    X_train, y_train,  # y_train contains strings: 'rice', 'wheat', etc.
    eval_set=(X_test, y_test),
    plot=False
)
```

---

## Testing the Fix

### Run Training
```bash
cd backend
python train_model.py
```

### Expected Output
```
============================================================
CROP RECOMMENDATION MODEL TRAINING
============================================================

[1/6] Loading dataset...
✓ Dataset loaded successfully
  - Total samples: 2200
  - Features: ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
  - Target: label
  - Unique crops: 22

[2/6] Preprocessing data...
✓ Data preprocessed
  - Feature shape: (2200, 7)
  - Target classes: 22
  - Class mapping created: 22 crops

[3/6] Splitting data...
✓ Data split completed
  - Training samples: 1760
  - Testing samples: 440

[4/6] Training CatBoost classifier...
0:      learn: 2.8234567        test: 2.8345678         best: 2.8345678 (0)     total: 15ms     remaining: 7.5s
100:    learn: 0.0234567        test: 0.0345678         best: 0.0345678 (100)   total: 1.5s     remaining: 5.9s
...
✓ Model training completed

[5/6] Evaluating model...
✓ Model evaluation completed
  - Training Accuracy: 99.xx%
  - Testing Accuracy: 99.xx%

[6/6] Saving model...
✓ Model saved to: models/crop_model.cbm
✓ Class mapping saved to: models/class_mapping.json
✓ Label mapping saved to: models/label_mapping.txt

============================================================
MODEL TRAINING COMPLETED SUCCESSFULLY!
============================================================

Final Model Accuracy: 99.xx%
Trained on 22 crop types
```

---

## Files Generated

```
models/
├── crop_model.cbm              # Trained CatBoost model
├── class_mapping.json          # Index to crop name mapping
├── label_mapping.txt           # Human-readable mapping
└── feature_importance.csv      # Feature importance scores
```

### Example class_mapping.json
```json
{
  "0": "apple",
  "1": "banana",
  "2": "blackgram",
  "3": "chickpea",
  ...
  "21": "watermelon"
}
```

---

## Why This Works

### CatBoost Behavior with class_names
When you provide `class_names` parameter:
1. CatBoost expects target labels to match the class_names (strings)
2. CatBoost internally creates the mapping: class_name → index
3. During training, it converts string labels to indices automatically
4. During prediction, it returns indices that correspond to class_names order

### Our Implementation
1. We provide sorted crop names as `class_names`
2. We train with original string labels from dataset
3. CatBoost handles the encoding internally
4. We save the same mapping as JSON for prediction time
5. During prediction, ml_service.py uses class_mapping.json to convert indices back to names

---

## Common Mistakes to Avoid

❌ **Don't do this:**
```python
# Encoding labels when using class_names
y_encoded = label_encoder.fit_transform(y)
model = CatBoostClassifier(class_names=sorted_crop_names)
model.fit(X_train, y_encoded)  # ERROR: Numeric labels with string class_names
```

✅ **Do this:**
```python
# Use string labels directly when using class_names
model = CatBoostClassifier(class_names=sorted_crop_names)
model.fit(X_train, y_train)  # OK: String labels with string class_names
```

---

## Summary

| Aspect | Before (Wrong) | After (Fixed) |
|--------|---------------|---------------|
| **Import** | LabelEncoder imported | LabelEncoder removed |
| **Labels** | Encoded to integers (0,1,2) | String labels ('rice','wheat') |
| **Training** | y_encoded passed to fit() | y (strings) passed to fit() |
| **CatBoost** | Confused by mismatch | Works correctly |
| **Error** | CatBoostError | ✓ Training succeeds |

**Key Takeaway**: When using `class_names` parameter in CatBoostClassifier, always train with string labels, not encoded integers!
