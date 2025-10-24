"""
Federated Learning Server for Crop Recommendation System
Uses Flower framework to coordinate distributed model training across multiple clients
"""

import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.server import ServerConfig


def start_federated_server():
    """
    Start the Flower federated learning server.
    
    Configuration:
    - Address: 0.0.0.0:8080 (accessible from all network interfaces)
    - Strategy: FedAvg (Federated Averaging)
    - Rounds: 3 training rounds
    - Minimum clients: 2 for training and evaluation
    """
    print("=" * 70)
    print("FEDERATED LEARNING SERVER - CROP RECOMMENDATION SYSTEM")
    print("=" * 70)
    
    print("\n[Server Configuration]")
    print("  - Strategy: FedAvg (Federated Averaging)")
    print("  - Training Rounds: 3")
    print("  - Minimum Fit Clients: 2")
    print("  - Minimum Evaluate Clients: 2")
    print("  - Minimum Available Clients: 2")
    print("  - Server Address: 0.0.0.0:8080")
    
    # Configure FedAvg strategy
    strategy = FedAvg(
        fraction_fit=1.0,              # Use 100% of available clients for training
        fraction_evaluate=1.0,         # Use 100% of available clients for evaluation
        min_fit_clients=2,             # Minimum 2 clients must be available for training
        min_evaluate_clients=2,        # Minimum 2 clients must be available for evaluation
        min_available_clients=2,       # Wait for at least 2 clients to connect
    )
    
    # Configure server
    config = ServerConfig(
        num_rounds=3  # Number of federated learning rounds
    )
    
    print("\n[Server Status]")
    print("✓ Strategy configured: FedAvg")
    print("✓ Server configuration set")
    print("\n[Starting Server]")
    print("Waiting for clients to connect...")
    print("(Press Ctrl+C to stop the server)\n")
    
    try:
        # Start Flower server
        fl.server.start_server(
            server_address="0.0.0.0:8080",
            config=config,
            strategy=strategy,
        )
    except KeyboardInterrupt:
        print("\n\n[Server Shutdown]")
        print("✓ Server stopped gracefully")
    except Exception as e:
        print("\n\n[Server Error]")
        print(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    start_federated_server()