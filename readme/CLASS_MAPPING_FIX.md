# Class Mapping Fix - Crop Names Instead of Numeric Indices

## Issue
CatBoost model was returning numeric indices (0, 1, 2, etc.) instead of actual crop names, causing confusion in predictions.

## Solution
Implemented a class mapping system that:
1. Creates a sorted mapping of indices to crop names during training
2. Saves the mapping as JSON for runtime use
3. Loads and applies the mapping during prediction

---

## Complete Updated Code

### 1. `train_model.py` - Complete Updated File

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from catboost import CatBoostClassifier
import os
import json  # NEW: Added for class mapping

def train_crop_model():
    """
    Train a CatBoost classifier for crop recommendation.
    """
    print("=" * 60)
    print("CROP RECOMMENDATION MODEL TRAINING")
    print("=" * 60)
    
    # 1. Load the dataset
    print("\n[1/6] Loading dataset...")
    data_path = "Crop_recommendation.csv"
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")
    
    df = pd.read_csv(data_path)
    print("✓ Dataset loaded successfully")
    print(f"  - Total samples: {len(df)}")
    print(f"  - Features: {list(df.columns[:-1])}")
    print(f"  - Target: {df.columns[-1]}")
    print(f"  - Unique crops: {df['label'].nunique()}")
    print(f"  - Crop types: {sorted(df['label'].unique())}")
    
    # 2. Preprocess data
    print("\n[2/6] Preprocessing data...")
    
    # Separate features and target
    X = df.drop('label', axis=1)
    y = df['label']
    
    # NEW: Create class mapping (sorted list of unique crop names)
    sorted_crop_names = sorted(y.unique())
    class_mapping = {i: name for i, name in enumerate(sorted_crop_names)}
    
    # Encode crop labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print("✓ Data preprocessed")
    print(f"  - Feature shape: {X.shape}")
    print(f"  - Target classes: {len(label_encoder.classes_)}")
    print(f"  - Class mapping created: {len(class_mapping)} crops")  # NEW
    
    # Check for missing values
    if X.isnull().sum().sum() > 0:
        print(f"  - Warning: Found {X.isnull().sum().sum()} missing values, filling with mean")
        X = X.fillna(X.mean())
    
    # 3. Split train/test sets
    print("\n[3/6] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, 
        test_size=0.2, 
        random_state=42, 
        stratify=y_encoded
    )
    
    print("✓ Data split completed")
    print(f"  - Training samples: {len(X_train)}")
    print(f"  - Testing samples: {len(X_test)}")
    
    # 4. Train CatBoost model
    print("\n[4/6] Training CatBoost classifier...")
    
    model = CatBoostClassifier(
        iterations=500,
        learning_rate=0.1,
        depth=6,
        loss_function='MultiClass',
        eval_metric='Accuracy',
        random_seed=42,
        verbose=100,
        early_stopping_rounds=50,
        class_names=sorted_crop_names  # NEW: Pass actual crop names
    )
    
    model.fit(
        X_train, y_train,
        eval_set=(X_test, y_test),
        plot=False
    )
    
    print("✓ Model training completed")
    
    # 5. Evaluate model
    print("\n[5/6] Evaluating model...")
    
    # Training accuracy
    y_train_pred = model.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    
    # Testing accuracy
    y_test_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    
    print("✓ Model evaluation completed")
    print(f"  - Training Accuracy: {train_accuracy * 100:.2f}%")
    print(f"  - Testing Accuracy: {test_accuracy * 100:.2f}%")
    
    # Detailed classification report
    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)
    print(classification_report(
        y_test, 
        y_test_pred, 
        target_names=label_encoder.classes_,
        digits=3
    ))
    
    # 6. Save model
    print("\n[6/6] Saving model...")
    
    # Create models directory if it doesn't exist
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "crop_model.cbm")
    model.save_model(model_path)
    
    print(f"✓ Model saved to: {model_path}")
    
    # NEW: Save class mapping as JSON
    class_mapping_path = os.path.join(models_dir, "class_mapping.json")
    with open(class_mapping_path, 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    print(f"✓ Class mapping saved to: {class_mapping_path}")
    
    # Save label encoder mapping (for reference)
    label_mapping_path = os.path.join(models_dir, "label_encoder.txt")
    with open(label_mapping_path, 'w') as f:
        for idx, label in enumerate(label_encoder.classes_):
            f.write(f"{idx}: {label}\n")
    
    print(f"✓ Label mapping saved to: {label_mapping_path}")
    
    # 7. Feature importance
    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE")
    print("=" * 60)
    
    feature_importance = model.get_feature_importance()
    feature_names = X.columns
    
    # Create feature importance dataframe
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': feature_importance
    }).sort_values('Importance', ascending=False)
    
    print(importance_df.to_string(index=False))
    
    # Save feature importance
    importance_path = os.path.join(models_dir, "feature_importance.csv")
    importance_df.to_csv(importance_path, index=False)
    print(f"\n✓ Feature importance saved to: {importance_path}")
    
    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    return model, label_encoder, test_accuracy

if __name__ == "__main__":
    try:
        model, label_encoder, accuracy = train_crop_model()
        print(f"\nFinal Model Accuracy: {accuracy * 100:.2f}%")
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        raise
```

### Key Changes in `train_model.py`:
1. **Line 7**: Added `import json`
2. **Lines 40-41**: Create class mapping: `class_mapping = {i: name for i, name in enumerate(sorted_crop_names)}`
3. **Line 82**: Pass `class_names=sorted_crop_names` to CatBoostClassifier
4. **Lines 131-136**: Save class mapping as JSON file

---

### 2. `ml_service.py` - Complete Updated File

```python
import pandas as pd
from catboost import CatBoostClassifier
import os
import json  # NEW: Added for class mapping
from typing import List, Dict, Optional


class CropRecommendationModel:
    """
    Machine Learning service for crop recommendation using trained CatBoost model.
    """
    
    def __init__(self, model_path: str = "models/crop_model.cbm"):
        """
        Initialize the model by loading the trained CatBoost classifier.
        
        Args:
            model_path: Path to the saved CatBoost model file
        """
        self.model_path = model_path
        self.model = None
        self.class_mapping = None  # NEW: Added class_mapping attribute
        self.feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        self._load_model()
        self._load_class_mapping()  # NEW: Load class mapping
    
    def _load_model(self):
        """Load the trained CatBoost model from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. "
                "Please train the model first using train_model.py"
            )
        
        self.model = CatBoostClassifier()
        self.model.load_model(self.model_path)
        print(f"✓ Model loaded successfully from {self.model_path}")
    
    # NEW: Method to load class mapping
    def _load_class_mapping(self):
        """Load the class mapping from JSON file."""
        class_mapping_path = "models/class_mapping.json"
        if os.path.exists(class_mapping_path):
            with open(class_mapping_path, 'r') as f:
                self.class_mapping = json.load(f)
            print(f"✓ Class mapping loaded from {class_mapping_path}")
        else:
            print(f"⚠ Warning: Class mapping file not found at {class_mapping_path}")
            self.class_mapping = None
    
    def predict(
        self,
        N: float,
        P: float,
        K: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float
    ) -> List[Dict[str, any]]:
        """
        Predict top 5 crop recommendations based on soil and environmental parameters.
        
        Args:
            N: Nitrogen content ratio
            P: Phosphorus content ratio
            K: Potassium content ratio
            temperature: Temperature in Celsius
            humidity: Relative humidity in %
            ph: pH value of soil
            rainfall: Rainfall in mm
            
        Returns:
            List of dictionaries containing:
                - crop_name: Name of the recommended crop (STRING)
                - probability: Model's confidence probability (0-1)
                - suitability_score: Suitability percentage (0-100)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        # Create input dataframe with proper feature order
        input_data = pd.DataFrame({
            'N': [N],
            'P': [P],
            'K': [K],
            'temperature': [temperature],
            'humidity': [humidity],
            'ph': [ph],
            'rainfall': [rainfall]
        })
        
        # Get prediction probabilities for all classes
        probabilities = self.model.predict_proba(input_data)[0]
        
        # Get class names from model
        class_names = self.model.classes_
        
        # NEW: Create list of (crop_name, probability) tuples with class mapping
        crop_predictions = []
        for i in range(len(class_names)):
            crop_class = class_names[i]
            
            # Convert to crop name using class_mapping if available
            if self.class_mapping is not None:
                crop_name = self.class_mapping.get(str(crop_class), str(crop_class))
            else:
                crop_name = str(crop_class)
            
            # Apply title case for proper capitalization
            crop_name = crop_name.title()
            
            crop_predictions.append((crop_name, float(probabilities[i])))
        
        # Sort by probability (descending) and get top 5
        crop_predictions.sort(key=lambda x: x[1], reverse=True)
        top_5 = crop_predictions[:5]
        
        # Format results
        recommendations = []
        for crop_name, probability in top_5:
            # Ensure crop_name is always a string (already converted above)
            crop_name_str = str(crop_name).strip()
            recommendations.append({
                'crop_name': crop_name_str,
                'probability': round(probability, 4),
                'suitability_score': round(probability * 100, 2)
            })
        
        return recommendations
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        if self.model is None:
            return {"status": "Model not loaded"}
        
        return {
            "model_type": "CatBoostClassifier",
            "model_path": self.model_path,
            "feature_names": self.feature_names,
            "num_classes": len(self.model.classes_),
            "classes": list(self.model.classes_),
            "class_mapping_loaded": self.class_mapping is not None
        }


# Soil type to NPK and pH mapping
SOIL_TYPE_DEFAULTS = {
    "Clay": {"N": 70, "P": 45, "K": 40, "ph": 6.5},
    "Sandy": {"N": 50, "P": 30, "K": 35, "ph": 6.0},
    "Silty": {"N": 65, "P": 40, "K": 38, "ph": 6.8},
    "Loam": {"N": 75, "P": 50, "K": 45, "ph": 7.0},
    "Loamy": {"N": 75, "P": 50, "K": 45, "ph": 7.0},
    "Unknown": {"N": 65, "P": 40, "K": 40, "ph": 6.5}
}


def get_soil_defaults(soil_type: str) -> Dict[str, float]:
    """Get default N, P, K, and pH values for a given soil type."""
    return SOIL_TYPE_DEFAULTS.get(soil_type, SOIL_TYPE_DEFAULTS["Unknown"])


# Singleton instance
_model_instance: Optional[CropRecommendationModel] = None


def get_model() -> CropRecommendationModel:
    """Get or create singleton instance of CropRecommendationModel."""
    global _model_instance
    if _model_instance is None:
        _model_instance = CropRecommendationModel()
    return _model_instance
```

### Key Changes in `ml_service.py`:
1. **Line 4**: Added `import json`
2. **Line 22**: Added `self.class_mapping = None` attribute
3. **Line 25**: Call `self._load_class_mapping()` in __init__
4. **Lines 39-48**: New `_load_class_mapping()` method
5. **Lines 99-112**: Convert numeric indices to crop names using class_mapping
6. **Line 110**: Apply `.title()` for proper capitalization

---

### 3. `api/routes.py` - Minor Update

```python
# In recommend_crops function, line 229-230:

# Ensure crop_name is a properly formatted string (already title-cased from ml_service)
crop_name = str(pred['crop_name']).strip()
```

**Change**: Removed `.capitalize()` since ml_service already applies `.title()` for proper capitalization.

---

## How It Works

### Training Phase (train_model.py)
```
1. Load dataset with crop labels: ['rice', 'wheat', 'cotton', ...]
2. Sort crop names alphabetically: ['apple', 'banana', 'chickpea', ...]
3. Create mapping: {0: 'apple', 1: 'banana', 2: 'chickpea', ...}
4. Train CatBoost with class_names parameter
5. Save model to crop_model.cbm
6. Save mapping to class_mapping.json
```

### Prediction Phase (ml_service.py)
```
1. Load model from crop_model.cbm
2. Load mapping from class_mapping.json
3. Get prediction: model returns class index (e.g., 5)
4. Convert to name: class_mapping['5'] = 'jute'
5. Apply title case: 'jute' → 'Jute'
6. Return: {'crop_name': 'Jute', 'probability': 0.92, 'suitability_score': 92.0}
```

---

## Example class_mapping.json

```json
{
  "0": "apple",
  "1": "banana",
  "2": "blackgram",
  "3": "chickpea",
  "4": "coconut",
  "5": "coffee",
  "6": "cotton",
  "7": "grapes",
  "8": "jute",
  "9": "kidneybeans",
  "10": "lentil",
  "11": "maize",
  "12": "mango",
  "13": "mothbeans",
  "14": "mungbean",
  "15": "muskmelon",
  "16": "orange",
  "17": "papaya",
  "18": "pigeonpeas",
  "19": "pomegranate",
  "20": "rice",
  "21": "watermelon"
}
```

---

## Testing the Fix

### Step 1: Retrain the Model
```bash
cd backend
python train_model.py
```

**Expected Output:**
```
[2/6] Preprocessing data...
✓ Data preprocessed
  - Feature shape: (2200, 7)
  - Target classes: 22
  - Class mapping created: 22 crops  ← NEW

[6/6] Saving model...
✓ Model saved to: models/crop_model.cbm
✓ Class mapping saved to: models/class_mapping.json  ← NEW
```

### Step 2: Start the Server
```bash
uvicorn main:app --reload
```

**Expected Console Output:**
```
✓ Model loaded successfully from models/crop_model.cbm
✓ Class mapping loaded from models/class_mapping.json  ← NEW
```

### Step 3: Test Prediction
```bash
curl -X POST "http://localhost:8000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "soil_type": "Loam",
    "temperature": 25,
    "rainfall": 1000,
    "humidity": 75
  }'
```

**Expected Response:**
```json
{
  "recommendations": [
    {
      "crop_name": "Rice",  ← Actual crop name, not "5" or "20"
      "suitability_score": 92.34,
      "reason": "Highly suitable based on ML model prediction..."
    },
    {
      "crop_name": "Jute",  ← Properly capitalized
      "suitability_score": 87.12,
      "reason": "Highly suitable based on ML model prediction..."
    }
  ]
}
```

---

## Files Generated After Training

```
models/
├── crop_model.cbm              # Trained CatBoost model
├── class_mapping.json          # NEW: Index to crop name mapping
├── label_encoder.txt           # Reference mapping (human-readable)
└── feature_importance.csv      # Feature importance scores
```

---

## Benefits

✅ **Readable Output**: Returns "Rice" instead of "20"  
✅ **Consistent Capitalization**: Uses .title() for "Rice", "Jute", "Cotton"  
✅ **Type Safety**: Always returns strings, never numeric indices  
✅ **Maintainable**: Mapping stored separately from model  
✅ **Backward Compatible**: Falls back to str(crop_class) if mapping missing  

---

## Troubleshooting

### Issue: Still getting numeric indices
**Solution**: Retrain the model with `python train_model.py` to generate class_mapping.json

### Issue: class_mapping.json not found
**Solution**: Ensure you run train_model.py before starting the API server

### Issue: Crop names not capitalized
**Solution**: The .title() method is applied in ml_service.py line 110

### Issue: Different crop names than expected
**Solution**: Check class_mapping.json to see the actual mapping used during training

---

## Summary

The fix ensures that:
1. ✅ CatBoost model is trained with actual crop names via `class_names` parameter
2. ✅ Class mapping is saved as JSON during training
3. ✅ Class mapping is loaded during prediction
4. ✅ Numeric indices are converted to crop names using the mapping
5. ✅ Crop names are properly formatted with .title() capitalization
6. ✅ All crop names are guaranteed to be strings in API responses

**Result**: API now returns "Rice", "Wheat", "Cotton" instead of numeric indices!
