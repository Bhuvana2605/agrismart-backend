from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Import routers
from api.routes import router
from api.community_routes import router as community_router

# Import MongoDB connection functions
from db import connect_to_mongodb, close_mongodb_connection

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles MongoDB connection lifecycle.
    """
    # Startup: Connect to MongoDB
    try:
        await connect_to_mongodb()
    except Exception as e:
        print(f"Warning: Failed to connect to MongoDB: {e}")
        print("Community features (feedback, posts, translation) will not be available.")
    
    yield
    
    # Shutdown: Close MongoDB connection
    await close_mongodb_connection()


app = FastAPI(
    title="Crop Recommendation System",
    description="API for crop recommendation based on soil and environmental parameters",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "message": "Crop Recommendation System API is running"
    }

# Mount routes from api/routes.py
app.include_router(router)

# Mount community routes (feedback, posts, translation)
app.include_router(community_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )