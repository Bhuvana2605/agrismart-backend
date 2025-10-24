# Market Price Integration Documentation

## Overview
This document describes the integration of live crop market price data from the data.gov.in API into the FastAPI backend.

## Changes Made

### 1. New Utility Module: `utils/market_price.py`

Created a new Python utility module that provides functions to fetch live market prices from the data.gov.in API.

**Key Functions:**

- **`get_market_price(crop_name, state=None)`**
  - Fetches the latest modal price for a specific crop
  - Parameters:
    - `crop_name`: Name of the crop/commodity (e.g., "Rice", "Wheat", "Cotton")
    - `state`: Optional state name to filter results (e.g., "Maharashtra", "Punjab")
  - Returns: Latest modal price in INR per quintal, or `None` if not found
  - Handles errors gracefully (rate limiting, timeouts, HTTP errors)

- **`get_market_prices_batch(crop_names, state=None)`**
  - Fetches market prices for multiple crops efficiently
  - Returns: Dictionary mapping crop names to their market prices

- **`normalize_crop_name_for_api(crop_name)`**
  - Normalizes ML model crop names to match API commodity names
  - Includes mapping for common crops (e.g., "chickpea" → "Gram")

**Features:**
- Async/await support for non-blocking API calls
- 10-second timeout to prevent hanging requests
- Rate limiting detection (HTTP 429)
- Comprehensive error handling and logging
- Automatic crop name normalization

### 2. Updated API Routes: `api/routes.py`

**Changes to `CropRecommendation` Model:**
```python
class CropRecommendation(BaseModel):
    crop_name: str
    suitability_score: float
    reason: str
    market_price: Optional[float] = Field(None, description="Market price in INR per quintal")
```

**Updated Endpoints:**

#### `/api/recommend` (POST)
- Now fetches market prices for all recommended crops
- Calls `get_market_prices_batch()` to fetch prices efficiently
- Adds `market_price` field to each crop recommendation
- Market price is `null` if data is unavailable

#### `/api/recommend-from-location` (POST)
- Automatically includes market prices in the response
- Uses the same market price integration as `/recommend`
- No additional configuration needed

### 3. Environment Configuration: `.env`

The `.env` file already contains the required API key:

```env
# Data.gov.in API Key for market price data
DATA_GOV_API_KEY=579b464db66ec23bdd00000185de4f38abbd449168f4df70123a7daf
```

**To update or change the API key:**
1. Get a free API key from: https://data.gov.in/
2. Update the `DATA_GOV_API_KEY` value in the `.env` file
3. Restart the FastAPI server

### 4. Environment Variable Loading: `main.py`

No changes needed! The existing code already loads environment variables:

```python
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

## API Response Examples

### Before Integration
```json
{
  "recommendations": [
    {
      "crop_name": "Rice",
      "suitability_score": 95.5,
      "reason": "Highly suitable based on ML model prediction..."
    }
  ]
}
```

### After Integration
```json
{
  "recommendations": [
    {
      "crop_name": "Rice",
      "suitability_score": 95.5,
      "reason": "Highly suitable based on ML model prediction...",
      "market_price": 2150.0
    },
    {
      "crop_name": "Wheat",
      "suitability_score": 87.3,
      "reason": "Highly suitable based on ML model prediction...",
      "market_price": 2025.0
    }
  ]
}
```

**Note:** `market_price` will be `null` if:
- The API key is not configured
- The crop is not found in the market database
- The API is rate-limited or unavailable
- A network error occurs

## Testing the Integration

### 1. Start the FastAPI Server
```bash
cd backend
python main.py
```

### 2. Test the `/recommend` Endpoint
```bash
curl -X POST "http://localhost:8000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "soil_type": "Loamy",
    "temperature": 25.5,
    "rainfall": 150.0,
    "humidity": 70.0
  }'
```

### 3. Test the `/recommend-from-location` Endpoint
```bash
curl -X POST "http://localhost:8000/api/recommend-from-location" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 28.6139,
    "lon": 77.2090
  }'
```

### 4. Check Logs
The market price utility logs all API calls:
```
INFO:utils.market_price:Found market price for Rice: ₹2150.0/quintal
INFO:utils.market_price:No market price data found for Pomegranate
```

## Error Handling

The integration is designed to be fault-tolerant:

1. **Missing API Key**: Returns `null` for market prices, logs warning
2. **API Rate Limiting**: Returns `null`, logs rate limit warning
3. **Network Timeout**: Returns `null` after 10 seconds
4. **HTTP Errors**: Returns `null`, logs error details
5. **Invalid Response**: Returns `null`, logs parsing error

**The crop recommendation system continues to work even if market prices are unavailable.**

## Data Source

- **API**: data.gov.in Agricultural Market Prices API
- **Endpoint**: `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070`
- **Data**: Daily market prices (modal prices) for various agricultural commodities across India
- **Unit**: INR per quintal (100 kg)

## Future Enhancements

Potential improvements:
1. Add state-based filtering for more accurate regional prices
2. Cache market prices to reduce API calls
3. Add historical price trends
4. Include min/max prices in addition to modal price
5. Add price prediction based on historical data

## Troubleshooting

### Market prices are always null
- Check if `DATA_GOV_API_KEY` is set in `.env`
- Verify the API key is valid at https://data.gov.in/
- Check server logs for error messages
- Test the API directly: `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=YOUR_KEY&format=json&limit=1`

### Rate limiting issues
- The free tier has rate limits
- Consider implementing caching
- Space out API requests

### Crop names not matching
- Check the `normalize_crop_name_for_api()` function in `utils/market_price.py`
- Add custom mappings for your specific crops
