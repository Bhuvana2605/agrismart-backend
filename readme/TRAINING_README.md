# Model Training Guide

## Overview
This guide explains how to train the CatBoost classifier for crop recommendation using the `train_model.py` script.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Required files:**
   - `Crop_recommendation.csv` - Dataset with crop features and labels

## Dataset Format

The CSV file should contain the following columns:
- `N` - Nitrogen content ratio
- `P` - Phosphorus content ratio
- `K` - Potassium content ratio
- `temperature` - Temperature in Celsius
- `humidity` - Relative humidity in %
- `ph` - pH value of soil
- `rainfall` - Rainfall in mm
- `label` - Crop name (target variable)

## Running the Training Script

```bash
cd backend
python train_model.py
```

## What the Script Does

1. **Loads Dataset** - Reads `Crop_recommendation.csv`
2. **Preprocesses Data** - Encodes crop labels and handles missing values
3. **Splits Data** - 80% training, 20% testing (stratified split)
4. **Trains Model** - Uses CatBoost with 500 iterations
5. **Evaluates Performance** - Calculates accuracy and classification metrics
6. **Saves Artifacts** - Saves model and metadata to `models/` folder
7. **Displays Feature Importance** - Shows which features matter most

## Output Files

After training, the following files are created in the `models/` directory:

- **`crop_model.cbm`** - Trained CatBoost model
- **`label_encoder.txt`** - Mapping of encoded labels to crop names
- **`feature_importance.csv`** - Feature importance scores

## Model Configuration

The CatBoost classifier uses:
- **Iterations:** 500
- **Learning Rate:** 0.1
- **Depth:** 6
- **Loss Function:** MultiClass
- **Early Stopping:** 50 rounds

## Expected Output

```
==============================================================
CROP RECOMMENDATION MODEL TRAINING
==============================================================

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

[3/6] Splitting data...
✓ Data split completed
  - Training samples: 1760
  - Testing samples: 440

[4/6] Training CatBoost classifier...
[Training progress...]
✓ Model training completed

[5/6] Evaluating model...
✓ Model evaluation completed
  - Training Accuracy: 99.xx%
  - Testing Accuracy: 99.xx%

[6/6] Saving model...
✓ Model saved to: models/crop_model.cbm
✓ Label mapping saved to: models/label_encoder.txt

==============================================================
FEATURE IMPORTANCE
==============================================================
[Feature importance table]
```

## Using the Trained Model

After training, you can load and use the model:

```python
from catboost import CatBoostClassifier
import pandas as pd

# Load model
model = CatBoostClassifier()
model.load_model('models/crop_model.cbm')

# Make predictions
features = pd.DataFrame({
    'N': [90],
    'P': [42],
    'K': [43],
    'temperature': [20.8],
    'humidity': [82.0],
    'ph': [6.5],
    'rainfall': [202.9]
})

prediction = model.predict(features)
print(f"Recommended crop: {prediction[0]}")
```

## Troubleshooting

### Missing Dependencies
```bash
pip install pandas scikit-learn catboost numpy
```

### Dataset Not Found
Ensure `Crop_recommendation.csv` is in the same directory as `train_model.py`

### Low Accuracy
- Check dataset quality
- Adjust model hyperparameters
- Increase training iterations
- Verify data preprocessing

## Next Steps

1. Integrate the trained model into the FastAPI endpoints
2. Create a prediction endpoint using the saved model
3. Add model versioning and monitoring
4. Implement model retraining pipeline
