"""
MongoDB Atlas database connection using Motor (async MongoDB driver for Python).

Configuration:
- Set MONGO_URI in .env with your MongoDB Atlas connection string
- Format: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority
- Get your connection string from MongoDB Atlas dashboard: Clusters > Connect > Connect your application
- Optionally set MONGO_DB_NAME (defaults to 'crop_recommendation_db')

Example .env:
    MONGO_URI=mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net/crop_recommendation_db?retryWrites=true&w=majority
    MONGO_DB_NAME=crop_recommendation_db

Note: This uses load_dotenv() in main.py to load environment variables at startup.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MongoDB client and database instances
mongo_client: AsyncIOMotorClient = None
database = None


async def connect_to_mongodb():
    """
    Connect to MongoDB using the connection string from environment variables.
    This should be called on application startup.
    """
    global mongo_client, database
    
    try:
        # Get MongoDB URI from environment variable
        mongo_uri = os.getenv("MONGO_URI")
        
        if not mongo_uri:
            logger.error("MONGO_URI not found in environment variables")
            raise ValueError("MONGO_URI environment variable is required")
        
        # Get database name from environment variable or use default
        db_name = os.getenv("MONGO_DB_NAME", "crop_recommendation_db")
        
        # Create MongoDB client
        mongo_client = AsyncIOMotorClient(mongo_uri)
        
        # Test the connection
        await mongo_client.admin.command('ping')
        
        # Get database instance
        database = mongo_client[db_name]
        
        logger.info(f"✓ Successfully connected to MongoDB database: {db_name}")
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
        raise


async def close_mongodb_connection():
    """
    Close the MongoDB connection.
    This should be called on application shutdown.
    """
    global mongo_client
    
    if mongo_client:
        mongo_client.close()
        logger.info("✓ MongoDB connection closed")


def get_database():
    """
    Get the MongoDB database instance.
    
    Returns:
        AsyncIOMotorDatabase: The MongoDB database instance
        
    Raises:
        RuntimeError: If database is not initialized
    """
    if database is None:
        raise RuntimeError(
            "Database not initialized. Call connect_to_mongodb() first."
        )
    return database


def get_collection(collection_name: str):
    """
    Get a MongoDB collection by name.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        AsyncIOMotorCollection: The MongoDB collection instance
    """
    db = get_database()
    return db[collection_name]
