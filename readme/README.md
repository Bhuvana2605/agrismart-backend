# Crop Recommendation System - Backend API

FastAPI-based backend service for crop recommendations based on soil type, weather conditions, and environmental parameters.

## Features

- **Soil Detection**: Integrates with ISRIC SoilGrids API to detect soil type from coordinates
- **Weather Data**: Fetches real-time weather data from OpenWeatherMap API
- **Crop Recommendations**: Provides intelligent crop recommendations based on soil and climate conditions

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update the `.env` file with your OpenWeatherMap API key:

```env
OPENWEATHER_API_KEY=your_actual_api_key_here
```

Get a free API key from: https://openweathermap.org/api

### 3. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/`
- Returns API status

### Detect Soil Type
- **POST** `/api/detect-soil`
- **Request Body**:
  ```json
  {
    "lat": 28.6139,
    "lon": 77.2090
  }
  ```
- **Response**:
  ```json
  {
    "soil_type": "Loamy",
    "properties": {
      "clay": 250,
      "sand": 400,
      "silt": 350
    },
    "message": "Soil type detected successfully at coordinates (28.6139, 77.209)"
  }
  ```

### Get Weather Data
- **POST** `/api/weather`
- **Request Body**:
  ```json
  {
    "lat": 28.6139,
    "lon": 77.2090
  }
  ```
- **Response**:
  ```json
  {
    "temperature": 25.5,
    "humidity": 65.0,
    "rainfall": 0.0,
    "weather_description": "clear sky",
    "location": "New Delhi"
  }
  ```

### Get Crop Recommendations
- **POST** `/api/recommend`
- **Request Body**:
  ```json
  {
    "soil_type": "Loamy",
    "temperature": 25.5,
    "rainfall": 800,
    "humidity": 65.0
  }
  ```
- **Response**:
  ```json
  {
    "recommendations": [
      {
        "crop_name": "Maize",
        "suitability_score": 100.0,
        "reason": "Suitable soil type (Loamy); Optimal temperature (25.5°C); Adequate rainfall (800mm)"
      },
      {
        "crop_name": "Wheat",
        "suitability_score": 85.0,
        "reason": "Suitable soil type (Loamy); Optimal temperature (25.5°C); Rainfall acceptable (800mm)"
      }
    ],
    "input_parameters": {
      "soil_type": "Loamy",
      "temperature": 25.5,
      "rainfall": 800,
      "humidity": 65.0
    }
  }
  ```

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Supported Crops

The system provides recommendations for:
- Rice
- Wheat
- Cotton
- Maize
- Sugarcane
- Soybean
- Groundnut
- Potato
- Tomato
- Barley

## Technology Stack

- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **httpx**: Async HTTP client for external API calls
- **Pydantic**: Data validation
- **python-dotenv**: Environment variable management

## CORS Configuration

CORS is enabled for all origins by default. For production, update the `allow_origins` in `main.py` to your frontend URL.
