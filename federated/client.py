"""
Federated Learning Client for Crop Recommendation System
Each client trains a local CatBoost model on its data partition
"""

import flwr as fl
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import sys
import os


class CropClient(fl.client.NumPyClient):
    """
    Flower NumPy client for federated crop recommendation training.
    Each client trains a CatBoost model on its local data partition.
    """
    
    def __init__(self, client_id, data_partition):
        """
        Initialize the crop recommendation client.
        
        Args:
            client_id: Unique identifier for this client
            data_partition: Tuple of (X_train, X_test, y_train, y_test)
        """
        self.client_id = client_id
        self.X_train, self.X_test, self.y_train, self.y_test = data_partition
        
        # Get sorted crop names for consistent class ordering
        all_labels = pd.concat([self.y_train, self.y_test])
        self.sorted_crop_names = sorted(all_labels.unique())
        
        # Initialize CatBoost model
        # Create a client-specific temp directory to avoid permission issues
        temp_dir = os.path.join(os.getcwd(), f"catboost_temp_client_{client_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        self.model = CatBoostClassifier(
            iterations=100,
            learning_rate=0.1,
            depth=6,
            loss_function='MultiClass',
            eval_metric='Accuracy',
            random_seed=42,
            verbose=False,  # Suppress training output
            class_names=self.sorted_crop_names,
            train_dir=temp_dir,  # Specify custom temp directory
            allow_writing_files=False  # Disable writing intermediate files
        )
        
        print(f"\n[Client {self.client_id}] Initialized")
        print(f"  - Training samples: {len(self.X_train)}")
        print(f"  - Test samples: {len(self.X_test)}")
        print(f"  - Unique crops in partition: {len(self.sorted_crop_names)}")
    
    def get_parameters(self, config):
        """
        Return model parameters as a list of NumPy arrays.
        
        Note: CatBoost doesn't expose parameters in a simple NumPy format,
        so we return an empty list as a placeholder. In a production system,
        you would serialize the model properly.
        """
        # Placeholder - CatBoost model serialization is complex
        return []
    
    def fit(self, parameters, config):
        """
        Train the model on local data.
        
        Args:
            parameters: Model parameters from server (not used for CatBoost)
            config: Training configuration from server
            
        Returns:
            Tuple of (parameters, num_examples, metrics)
        """
        print(f"\n[Client {self.client_id}] Starting training round...")
        
        # Train model on local data
        self.model.fit(
            self.X_train,
            self.y_train,
            eval_set=(self.X_test, self.y_test),
            verbose=False,
            plot=False
        )
        
        # Evaluate on training data
        y_train_pred = self.model.predict(self.X_train)
        train_accuracy = accuracy_score(self.y_train, y_train_pred)
        
        print(f"[Client {self.client_id}] Training completed")
        print(f"  - Training accuracy: {train_accuracy * 100:.2f}%")
        print(f"  - Samples trained: {len(self.X_train)}")
        
        # Return parameters (empty for CatBoost), sample count, and metrics
        return [], len(self.X_train), {"train_accuracy": float(train_accuracy)}
    
    def evaluate(self, parameters, config):
        """
        Evaluate the model on local test data.
        
        Args:
            parameters: Model parameters from server (not used for CatBoost)
            config: Evaluation configuration from server
            
        Returns:
            Tuple of (loss, num_examples, metrics)
        """
        print(f"\n[Client {self.client_id}] Starting evaluation...")
        
        # Evaluate on test data
        y_test_pred = self.model.predict(self.X_test)
        test_accuracy = accuracy_score(self.y_test, y_test_pred)
        
        # Calculate loss (1 - accuracy for simplicity)
        loss = 1.0 - test_accuracy
        
        print(f"[Client {self.client_id}] Evaluation completed")
        print(f"  - Test accuracy: {test_accuracy * 100:.2f}%")
        print(f"  - Test loss: {loss:.4f}")
        print(f"  - Samples evaluated: {len(self.X_test)}")
        
        # Return loss, sample count, and metrics
        return float(loss), len(self.X_test), {"test_accuracy": float(test_accuracy)}


def load_data_partition(client_id, num_clients=3):
    """
    Load and partition the crop recommendation dataset for a specific client.
    
    Args:
        client_id: ID of the client (0-indexed)
        num_clients: Total number of clients in the federation
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test) for this client's partition
    """
    print(f"\n[Client {client_id}] Loading data partition...")
    
    # Load the full dataset
    data_path = os.path.join("..", "Crop_recommendation.csv")
    if not os.path.exists(data_path):
        # Try alternative path
        data_path = "Crop_recommendation.csv"
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            "Dataset not found. Tried: ../Crop_recommendation.csv and Crop_recommendation.csv"
        )
    
    df = pd.read_csv(data_path)
    print(f"[Client {client_id}] Dataset loaded: {len(df)} total samples")
    
    # Shuffle dataset for random partitioning
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Calculate partition size
    partition_size = len(df) // num_clients
    start_idx = client_id * partition_size
    
    # Last client gets remaining samples
    if client_id == num_clients - 1:
        end_idx = len(df)
    else:
        end_idx = start_idx + partition_size
    
    # Get this client's partition
    client_data = df.iloc[start_idx:end_idx]
    
    print(f"[Client {client_id}] Partition assigned:")
    print(f"  - Partition range: [{start_idx}:{end_idx}]")
    print(f"  - Partition size: {len(client_data)} samples")
    print(f"  - Percentage of total: {len(client_data)/len(df)*100:.1f}%")
    
    # Separate features and target
    X = client_data.drop('label', axis=1)
    y = client_data['label']
    
    # Split into train and test sets (80/20 split)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y if len(y.unique()) > 1 else None
    )
    
    print(f"[Client {client_id}] Data split completed:")
    print(f"  - Training samples: {len(X_train)}")
    print(f"  - Test samples: {len(X_test)}")
    print(f"  - Unique crops: {y.nunique()}")
    
    return X_train, X_test, y_train, y_test


def start_client(client_id):
    """
    Start a federated learning client.
    
    Args:
        client_id: Unique identifier for this client (0-indexed)
    """
    print("=" * 70)
    print(f"FEDERATED LEARNING CLIENT {client_id} - CROP RECOMMENDATION SYSTEM")
    print("=" * 70)
    
    try:
        # Load data partition for this client
        data_partition = load_data_partition(client_id, num_clients=3)
        
        # Create client instance
        numpy_client = CropClient(client_id, data_partition)
        
        print(f"\n[Client {client_id}] Connecting to server at 127.0.0.1:8080...")
        print(f"[Client {client_id}] Ready for federated training\n")
        
        # Start Flower client using modern API (to avoid deprecation warning)
        fl.client.start_client(
            server_address="127.0.0.1:8080",
            client=numpy_client.to_client()  # Convert NumPyClient to Client
        )
        
        print(f"\n[Client {client_id}] Training completed successfully")
        
    except KeyboardInterrupt:
        print(f"\n\n[Client {client_id}] Interrupted by user")
    except ConnectionError as e:
        print(f"\n\n[Client {client_id}] Connection Error: Could not connect to server")
        print("Make sure the server is running at 127.0.0.1:8080")
        print(f"Error details: {str(e)}")
    except Exception as e:
        print(f"\n\n[Client {client_id}] Error: {str(e)}")
        raise


if __name__ == "__main__":
    # Get client ID from command line arguments
    if len(sys.argv) != 2:
        print("Usage: python client.py <client_id>")
        print("Example: python client.py 0")
        print("\nClient ID should be 0, 1, or 2 for a 3-client setup")
        sys.exit(1)
    
    try:
        client_id = int(sys.argv[1])
        if client_id < 0:
            raise ValueError("Client ID must be non-negative")
        
        start_client(client_id)
        
    except ValueError as e:
        print(f"Error: Invalid client ID. {str(e)}")
        print("Client ID must be a non-negative integer (e.g., 0, 1, 2)")
        sys.exit(1)