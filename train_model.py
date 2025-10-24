import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from catboost import CatBoostClassifier
import os
import json

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
    
    # Create class mapping (sorted list of unique crop names)
    sorted_crop_names = sorted(y.unique())
    class_mapping = {i: name for i, name in enumerate(sorted_crop_names)}
    
    # Note: CatBoost with class_names expects string labels, not encoded integers
    # So we use y directly (string labels) instead of encoding
    
    print("✓ Data preprocessed")
    print(f"  - Feature shape: {X.shape}")
    print(f"  - Target classes: {len(sorted_crop_names)}")
    print(f"  - Class mapping created: {len(class_mapping)} crops")
    
    # Check for missing values
    if X.isnull().sum().sum() > 0:
        print(f"  - Warning: Found {X.isnull().sum().sum()} missing values, filling with mean")
        X = X.fillna(X.mean())
    
    # 3. Split train/test sets
    print("\n[3/6] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,  # Use original string labels, not encoded
        test_size=0.2, 
        random_state=42, 
        stratify=y  # Stratify by original labels
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
        class_names=sorted_crop_names  # Pass actual crop names
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
        target_names=sorted_crop_names,  # Use sorted crop names
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
    
    # Save class mapping as JSON
    class_mapping_path = os.path.join(models_dir, "class_mapping.json")
    with open(class_mapping_path, 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    print(f"✓ Class mapping saved to: {class_mapping_path}")
    
    # Save label mapping (for reference)
    label_mapping_path = os.path.join(models_dir, "label_mapping.txt")
    with open(label_mapping_path, 'w') as f:
        for idx, label in enumerate(sorted_crop_names):
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
    
    return model, sorted_crop_names, test_accuracy

if __name__ == "__main__":
    try:
        model, crop_names, accuracy = train_crop_model()
        print(f"\nFinal Model Accuracy: {accuracy * 100:.2f}%")
        print(f"Trained on {len(crop_names)} crop types")
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        raise
