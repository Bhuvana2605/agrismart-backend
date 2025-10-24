import httpx
import os
from typing import Optional, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_market_price(crop_name: str, state: Optional[str] = None) -> Optional[float]:
    """
    Fetch the latest modal price for a crop from the data.gov.in API.
    
    Args:
        crop_name: Name of the crop/commodity (e.g., "Rice", "Wheat", "Cotton")
        state: Optional state name to filter results (e.g., "Maharashtra", "Punjab")
        
    Returns:
        Latest modal price in INR per quintal, or None if not found
        
    Raises:
        None - handles errors gracefully and returns None on failure
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv("DATA_GOV_API_KEY")
        if not api_key:
            logger.warning("DATA_GOV_API_KEY not configured in environment variables")
            return None
        
        # API endpoint for agricultural market prices
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        
        # Prepare query parameters
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": 10  # Get recent records
        }
        
        # Add commodity filter if crop name provided
        if crop_name:
            params["filters[commodity]"] = crop_name
        
        # Add state filter if provided
        if state:
            params["filters[state]"] = state
        
        # Make async HTTP request with timeout
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            
            # Handle rate limiting (429 status code)
            if response.status_code == 429:
                logger.warning("Rate limit exceeded for data.gov.in API")
                return None
            
            # Raise exception for other HTTP errors
            response.raise_for_status()
            data = response.json()
        
        # Parse response and extract modal price
        if "records" in data and len(data["records"]) > 0:
            # Get the first (most recent) record
            record = data["records"][0]
            
            # Try to extract modal price from different possible field names
            modal_price = None
            for field in ["modal_price", "modal", "price", "modal_price_rs_quintal"]:
                if field in record:
                    try:
                        modal_price = float(record[field])
                        break
                    except (ValueError, TypeError):
                        continue
            
            if modal_price is not None:
                logger.info(f"Found market price for {crop_name}: ₹{modal_price}/quintal")
                return modal_price
            else:
                logger.warning(f"Modal price field not found in API response for {crop_name}")
                return None
        else:
            logger.info(f"No market price data found for {crop_name}" + (f" in {state}" if state else ""))
            return None
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching market price for {crop_name}: {e.response.status_code}")
        return None
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching market price for {crop_name}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching market price for {crop_name}: {str(e)}")
        return None


def normalize_crop_name_for_api(crop_name: str) -> str:
    """
    Normalize crop names to match common commodity names in the API.
    
    Args:
        crop_name: Crop name from ML model
        
    Returns:
        Normalized commodity name for API query
    """
    # Mapping of ML model crop names to API commodity names
    crop_mapping = {
        "rice": "Rice",
        "wheat": "Wheat",
        "maize": "Maize",
        "chickpea": "Gram",
        "kidneybeans": "Rajma",
        "pigeonpeas": "Arhar (Tur/Red Gram)",
        "mothbeans": "Moth",
        "mungbean": "Moong",
        "blackgram": "Urad",
        "lentil": "Masur",
        "pomegranate": "Pomegranate",
        "banana": "Banana",
        "mango": "Mango",
        "grapes": "Grapes",
        "watermelon": "Watermelon",
        "muskmelon": "Muskmelon",
        "apple": "Apple",
        "orange": "Orange",
        "papaya": "Papaya",
        "coconut": "Coconut",
        "cotton": "Cotton",
        "jute": "Jute",
        "coffee": "Coffee"
    }
    
    # Normalize input
    normalized = crop_name.strip().lower()
    
    # Return mapped name or original (title case)
    return crop_mapping.get(normalized, crop_name.title())


async def get_market_prices_batch(crop_names: list[str], state: Optional[str] = None) -> Dict[str, Optional[float]]:
    """
    Fetch market prices for multiple crops in batch.
    
    Args:
        crop_names: List of crop names
        state: Optional state name to filter results
        
    Returns:
        Dictionary mapping crop names to their market prices
    """
    prices = {}
    
    for crop_name in crop_names:
        # Normalize crop name for better API matching
        normalized_name = normalize_crop_name_for_api(crop_name)
        price = await get_market_price(normalized_name, state)
        prices[crop_name] = price
    
    return prices
