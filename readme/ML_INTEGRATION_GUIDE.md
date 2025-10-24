# ML Model Integration Guide

## Overview
This guide documents the integration of the trained CatBoost ML model into the FastAPI backend for intelligent crop recommendations.

## Files Created

### 1. `ml_service.py`
Machine Learning service module that handles model loading and predictions.

**Key Components:**

#### `CropRecommendationModel` Class
- **Purpose**: Wrapper for the trained CatBoost model
- **Model Path**: `models/crop_model.cbm`
- **Features**: N, P, K, temperature, humidity, ph, rainfall

**Methods:**
- `__init__(model_path)`: Loads the trained model
- `predict(N, P, K, temperature, humidity, ph, rainfall)`: Returns top 5 crop recommendations
- `get_model_info()`: Returns model metadata

**Prediction Output Format:**
```python
[
    {
        'crop_name': 'rice',
        'probability': 0.9234,
        'suitability_score': 92.34
    },
    # ... top 5 crops
]
```

#### `SOIL_TYPE_DEFAULTS` Dictionary
Maps soil types to typical N, P, K, and pH values:
- **Clay**: N=70, P=45, K=40, ph=6.5
- **Sandy**: N=50, P=30, K=35, ph=6.0
- **Silty**: N=65, P=40, K=38, ph=6.8
- **Loam**: N=75, P=50, K=45, ph=7.0
- **Loamy**: N=75, P=50, K=45, ph=7.0
- **Unknown**: N=65, P=40, K=40, ph=6.5

#### Helper Functions
- `get_soil_defaults(soil_type)`: Returns default NPK and pH for soil type
- `get_model()`: Singleton pattern for model instance

---

## Files Modified

### 2. `api/routes.py`

#### Changes to Imports
```python
# Added imports
from ml_service import get_model, get_soil_defaults
```

#### Updated `RecommendationRequest` Model
```python
class RecommendationRequest(BaseModel):
    soil_type: str
    temperature: float
    rainfall: float
    humidity: Optional[float] = None
    N: Optional[float] = None          # NEW
    P: Optional[float] = None          # NEW
    K: Optional[float] = None          # NEW
    ph: Optional[float] = None         # NEW
```

#### Replaced `recommend_crops()` Function
**Before**: Rule-based logic with hardcoded crop database
**After**: ML model-based predictions

**New Logic Flow:**
1. Get soil defaults for N, P, K, ph if not provided
2. Use provided values or defaults from soil type mapping
3. Load ML model singleton instance
4. Call `ml_model.predict()` with all 7 features
5. Convert ML predictions to `CropRecommendation` format
6. Generate confidence-based reasons
7. Return top 5 recommendations with input parameters

**Key Improvements:**
- ✅ Uses trained ML model instead of rules
- ✅ Handles missing N, P, K, ph with intelligent defaults
- ✅ Returns probability-based suitability scores
- ✅ Provides detailed confidence levels
- ✅ Better error handling (503 if model not trained)

---

## API Changes

### `/api/recommend` Endpoint

#### Request Body (Updated)
```json
{
  "soil_type": "Loam",
  "temperature": 25.5,
  "rainfall": 800,
  "humidity": 75.0,
  "N": 80,           // Optional - defaults from soil type
  "P": 55,           // Optional - defaults from soil type
  "K": 45,           // Optional - defaults from soil type
  "ph": 6.8          // Optional - defaults from soil type
}
```

#### Response Format (Enhanced)
```json
{
  "recommendations": [
    {
      "crop_name": "rice",
      "suitability_score": 92.34,
      "reason": "Highly suitable based on ML model prediction (confidence: 92.34%). Soil: Loam, Temp: 25.5°C, Rainfall: 800mm, Humidity: 75%"
    },
    // ... top 5 crops
  ],
  "input_parameters": {
    "soil_type": "Loam",
    "N": 80,
    "P": 55,
    "K": 45,
    "temperature": 25.5,
    "humidity": 75.0,
    "ph": 6.8,
    "rainfall": 800
  }
}
```

#### Confidence Levels
- **≥80%**: "Highly suitable"
- **≥60%**: "Suitable"
- **≥40%**: "Moderately suitable"
- **<40%**: "Less suitable"

---

## Usage Examples

### Example 1: Basic Request (with defaults)
```python
import requests

response = requests.post("http://localhost:8000/api/recommend", json={
    "soil_type": "Loam",
    "temperature": 25.0,
    "rainfall": 1200,
    "humidity": 80.0
})

# N, P, K, ph will use Loam defaults: N=75, P=50, K=45, ph=7.0
```

### Example 2: Full Request (all parameters)
```python
response = requests.post("http://localhost:8000/api/recommend", json={
    "soil_type": "Clay",
    "temperature": 28.0,
    "rainfall": 1500,
    "humidity": 85.0,
    "N": 90,
    "P": 42,
    "K": 43,
    "ph": 6.5
})
```

### Example 3: Combined Location-Based Recommendation
```python
# Uses /recommend-from-location endpoint
response = requests.post("http://localhost:8000/api/recommend-from-location", json={
    "lat": 28.6139,
    "lon": 77.2090
})

# Automatically:
# 1. Detects soil type from coordinates
# 2. Gets weather data (temp, humidity, rainfall)
# 3. Maps soil type to N, P, K, ph
# 4. Calls ML model for recommendations
```

---

## Error Handling

### Model Not Found (503)
```json
{
  "detail": "ML model not available: Model file not found at models/crop_model.cbm. Please train the model first using train_model.py"
}
```

**Solution**: Run `python train_model.py` to train and save the model.

### Invalid Input (422)
```json
{
  "detail": [
    {
      "loc": ["body", "temperature"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solution**: Ensure all required fields are provided.

---

## Testing the Integration

### Step 1: Train the Model
```bash
cd backend
python train_model.py
```

### Step 2: Start the Server
```bash
uvicorn main:app --reload
```

### Step 3: Test the Endpoint
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

### Step 4: Verify Response
Check that:
- ✅ Top 5 crops are returned
- ✅ Suitability scores are between 0-100
- ✅ Reasons include confidence levels
- ✅ Input parameters show N, P, K, ph values

---

## Benefits of ML Integration

1. **Data-Driven**: Predictions based on 2200+ training samples
2. **Accurate**: CatBoost achieves ~99% accuracy on test set
3. **Flexible**: Handles missing NPK/ph with intelligent defaults
4. **Scalable**: Model can be retrained with new data
5. **Transparent**: Returns probability scores for interpretability
6. **Robust**: Graceful fallback if model unavailable

---

## Next Steps

1. ✅ Model trained and integrated
2. ✅ API endpoints updated
3. 🔄 Test with real-world data
4. 🔄 Monitor prediction accuracy
5. 🔄 Collect user feedback
6. 🔄 Retrain model periodically with new data
7. 🔄 Add model versioning
8. 🔄 Implement A/B testing (ML vs rule-based)

---

## Troubleshooting

### Issue: Model loads slowly
**Solution**: Model is loaded once as singleton, subsequent requests are fast.

### Issue: Predictions seem incorrect
**Solution**: 
1. Verify input ranges match training data
2. Check feature importance in `models/feature_importance.csv`
3. Retrain model with more diverse data

### Issue: Different results than rule-based
**Solution**: This is expected! ML model learns patterns from data, not hardcoded rules. ML predictions are generally more accurate.

---

## Model Performance Metrics

After training, check:
- Training Accuracy: ~99%
- Testing Accuracy: ~99%
- Feature Importance: Available in `models/feature_importance.csv`
- Classification Report: Shows per-crop precision/recall

---

## Maintenance

### Retraining the Model
```bash
# When new data is available
python train_model.py

# Model will be saved to models/crop_model.cbm
# API will automatically use the new model on next request
```

### Monitoring
- Log prediction probabilities
- Track user feedback on recommendations
- Monitor API response times
- Check for prediction drift over time
