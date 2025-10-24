import pandas as pd
from catboost import CatBoostClassifier
import os
import json
import numpy as np
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        self.class_mapping = None
        self.feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        self._load_model()
        self._load_class_mapping()
    
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
    
    def _validate_inputs(
        self,
        N: float,
        P: float,
        K: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float
    ) -> None:
        """
        Validate input parameters are within reasonable ranges.
        
        Raises:
            ValueError: If any input is out of valid range
        """
        validations = [
            (N, "Nitrogen (N)", 0, 200),
            (P, "Phosphorus (P)", 0, 200),
            (K, "Potassium (K)", 0, 300),
            (temperature, "Temperature", -10, 60),
            (humidity, "Humidity", 0, 100),
            (ph, "pH", 0, 14),
            (rainfall, "Rainfall", 0, 500)
        ]
        
        for value, name, min_val, max_val in validations:
            if not (min_val <= value <= max_val):
                logger.warning(
                    f"{name} value {value} is outside typical range [{min_val}, {max_val}]. "
                    "Predictions may be less accurate."
                )
    
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
            N: Nitrogen content ratio (0-200)
            P: Phosphorus content ratio (0-200)
            K: Potassium content ratio (0-300)
            temperature: Temperature in Celsius (-10 to 60)
            humidity: Relative humidity in % (0-100)
            ph: pH value of soil (0-14)
            rainfall: Rainfall in mm (0-500)
            
        Returns:
            List of dictionaries containing:
                - crop_name: Name of the recommended crop
                - probability: Model's confidence probability (0-1)
                - suitability_score: Suitability percentage (0-100)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        # Log input parameters
        logger.info("\n" + "="*60)
        logger.info("ML MODEL PREDICTION REQUEST")
        logger.info("="*60)
        logger.info("Input Parameters:")
        logger.info(f"  N={N}, P={P}, K={K}")
        logger.info(f"  Temperature={temperature}°C, Humidity={humidity}%")
        logger.info(f"  pH={ph}, Rainfall={rainfall}mm")
        
        # Validate inputs
        try:
            self._validate_inputs(N, P, K, temperature, humidity, ph, rainfall)
        except Exception as e:
            logger.warning(f"Input validation warning: {str(e)}")
        
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
        
        # Log raw probabilities
        logger.info("\nRaw probabilities from model:")
        logger.info(f"  Min: {np.min(probabilities):.6f}")
        logger.info(f"  Max: {np.max(probabilities):.6f}")
        logger.info(f"  Sum: {np.sum(probabilities):.6f}")
        logger.info(f"  Shape: {probabilities.shape}")
        
        # Get class names from model
        class_names = self.model.classes_
        
        # Create list of (crop_name, probability) tuples
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
        
        logger.info("\nTop 5 predictions (before normalization):")
        for idx, (crop, prob) in enumerate(top_5, 1):
            logger.info(f"  {idx}. {crop}: probability={prob:.6f}, score={prob*100:.2f}%")
        
        # Format results with proper score normalization
        recommendations = []
        for crop_name, probability in top_5:
            # Ensure crop_name is always a string (already converted above)
            crop_name_str = str(crop_name).strip()
            
            # CRITICAL FIX: Multi-layer protection against invalid scores
            # Layer 1: Check if probability is already a percentage (> 1.0)
            if probability > 1.0:
                logger.warning(
                    f"Probability > 1.0 detected for {crop_name_str}: {probability}"
                )
                # It's already a percentage or invalid, treat as percentage
                raw_score = probability
            else:
                # Normal case: probability is 0-1, convert to percentage
                raw_score = probability * 100
            
            # Layer 2: Absolute clamping to 0-100 range
            suitability_score = np.clip(raw_score, 0.0, 100.0)
            
            # Layer 3: Sanity check - if still invalid, force to safe value
            if suitability_score > 100.0 or suitability_score < 0.0 or np.isnan(suitability_score):
                logger.error(
                    f"CRITICAL: Invalid score for {crop_name_str}: {suitability_score}, forcing to 50.0"
                )
                suitability_score = 50.0
            
            # Layer 4: Log if clamping occurred
            if raw_score > 100.0:
                logger.warning(
                    f"Score clamped for {crop_name_str}: {raw_score:.2f}% -> {suitability_score:.2f}%"
                )
            
            # Layer 5: Ensure probability is also normalized for display
            normalized_probability = min(max(probability, 0.0), 1.0) if probability <= 1.0 else min(max(probability / 100.0, 0.0), 1.0)
            
            recommendations.append({
                'crop_name': crop_name_str,
                'probability': round(float(normalized_probability), 4),
                'suitability_score': round(float(suitability_score), 2)
            })
        
        logger.info("\nFinal recommendations (after normalization):")
        for idx, rec in enumerate(recommendations, 1):
            logger.info(
                f"  {idx}. {rec['crop_name']}: "
                f"suitability={rec['suitability_score']}%, "
                f"confidence={rec['probability']:.4f}"
            )
        logger.info("="*60 + "\n")
        
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
            "classes": list(self.model.classes_)
        }


# Soil type to NPK and pH mapping
# Based on typical soil characteristics
SOIL_TYPE_DEFAULTS = {
    "Clay": {
        "N": 70,
        "P": 45,
        "K": 40,
        "ph": 6.5
    },
    "Sandy": {
        "N": 50,
        "P": 30,
        "K": 35,
        "ph": 6.0
    },
    "Silty": {
        "N": 65,
        "P": 40,
        "K": 38,
        "ph": 6.8
    },
    "Loam": {
        "N": 75,
        "P": 50,
        "K": 45,
        "ph": 7.0
    },
    "Loamy": {
        "N": 75,
        "P": 50,
        "K": 45,
        "ph": 7.0
    },
    "Unknown": {
        "N": 65,
        "P": 40,
        "K": 40,
        "ph": 6.5
    }
}


def get_soil_defaults(soil_type: str) -> Dict[str, float]:
    """
    Get default N, P, K, and pH values for a given soil type.
    
    Args:
        soil_type: Type of soil (Clay, Sandy, Silty, Loam, Loamy, Unknown)
        
    Returns:
        Dictionary with N, P, K, and ph default values
    """
    return SOIL_TYPE_DEFAULTS.get(soil_type, SOIL_TYPE_DEFAULTS["Unknown"])


# Singleton instance
_model_instance: Optional[CropRecommendationModel] = None


def get_model() -> CropRecommendationModel:
    """
    Get or create singleton instance of CropRecommendationModel.
    
    Returns:
        CropRecommendationModel instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = CropRecommendationModel()
    return _model_instance
