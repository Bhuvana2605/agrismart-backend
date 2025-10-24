from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from ml_service import get_model, get_soil_defaults
from utils.market_price import get_market_prices_batch

router = APIRouter(prefix="/api", tags=["crop-recommendation"])

# Request/Response Models
class LocationRequest(BaseModel):
    lat: float = Field(..., description="Latitude", ge=-90, le=90)
    lon: float = Field(..., description="Longitude", ge=-180, le=180)

class SoilDetectionResponse(BaseModel):
    soil_type: str
    properties: Dict[str, Any]
    message: str

class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    rainfall: float
    weather_description: str
    location: str

class RecommendationRequest(BaseModel):
    soil_type: str
    temperature: float
    rainfall: float
    humidity: Optional[float] = None
    N: Optional[float] = None
    P: Optional[float] = None
    K: Optional[float] = None
    ph: Optional[float] = None

class ManualRecommendationRequest(BaseModel):
    N: float = Field(..., description="Nitrogen content ratio")
    P: float = Field(..., description="Phosphorus content ratio")
    K: float = Field(..., description="Potassium content ratio")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Relative humidity in %")
    ph: float = Field(..., description="pH value of soil")
    rainfall: float = Field(..., description="Rainfall in mm")

class CropRecommendation(BaseModel):
    crop_name: str
    suitability_score: float
    reason: str
    market_price: Optional[float] = Field(None, description="Market price in INR per quintal")

class RecommendationResponse(BaseModel):
    recommendations: List[CropRecommendation]
    input_parameters: Dict[str, Any]

class CombinedRecommendationResponse(BaseModel):
    location_info: Dict[str, Any]
    detected_soil: SoilDetectionResponse
    current_weather: WeatherResponse
    recommendations: List[CropRecommendation]
    input_parameters: Dict[str, Any]


# Route 1: Detect Soil Type
@router.post("/detect-soil", response_model=SoilDetectionResponse)
async def detect_soil(location: LocationRequest):
    """
    Detect soil type using ISRIC SoilGrids API based on latitude and longitude.
    Returns default values if API fails to ensure endpoint always works.
    """
    try:
        # ISRIC SoilGrids API endpoint
        # Using the REST API to get soil properties at a specific location
        url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        
        params = {
            "lon": location.lon,
            "lat": location.lat,
            "property": ["clay", "sand", "silt", "phh2o"],  # soil properties
            "depth": ["0-5cm", "5-15cm"],  # top soil layers
            "value": "mean"
        }
        
        print(f"[SOIL API] Requesting soil data for lat={location.lat}, lon={location.lon}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Validate API response
        if not data or "properties" not in data:
            print("[SOIL API] Invalid response structure, using defaults")
            raise ValueError("Invalid API response structure")
        
        # Extract soil properties
        properties = {}
        soil_type = "Loam"  # Default soil type
        
        if "properties" in data and "layers" in data["properties"]:
            layers = data["properties"]["layers"]
            
            # Extract values for top layer (0-5cm)
            for layer in layers:
                prop_name = layer.get("name")
                if prop_name and "depths" in layer and len(layer["depths"]) > 0:
                    depth_data = layer["depths"][0]
                    if "values" in depth_data and "mean" in depth_data["values"]:
                        value = depth_data["values"]["mean"]
                        # Only store non-None values
                        if value is not None:
                            properties[prop_name] = value
            
            print(f"[SOIL API] Extracted properties: {properties}")
            
            # Determine soil type based on clay, sand, silt percentages
            # Handle None values from API by using 0 as fallback
            clay_raw = properties.get("clay")
            sand_raw = properties.get("sand")
            silt_raw = properties.get("silt")
            
            # Safe division with None checks
            clay = (clay_raw / 10) if clay_raw is not None else 0
            sand = (sand_raw / 10) if sand_raw is not None else 0
            silt = (silt_raw / 10) if silt_raw is not None else 0
            
            print(f"[SOIL API] Calculated percentages - Clay: {clay}%, Sand: {sand}%, Silt: {silt}%")
            
            # Simple soil classification
            if clay > 40:
                soil_type = "Clay"
            elif sand > 50:
                soil_type = "Sandy"
            elif silt > 40:
                soil_type = "Silty"
            elif clay > 25 and sand > 25:
                soil_type = "Loam"
            else:
                soil_type = "Loamy"
        
        print(f"[SOIL API] Detected soil type: {soil_type}")
        
        return SoilDetectionResponse(
            soil_type=soil_type,
            properties=properties if properties else {"clay": 0, "sand": 0, "silt": 0},
            message=f"Soil type detected successfully at coordinates ({location.lat}, {location.lon})"
        )
    
    except httpx.HTTPStatusError as e:
        print(f"[SOIL API ERROR] HTTP {e.response.status_code}: {str(e)}")
        # Return default soil data instead of raising exception
        return SoilDetectionResponse(
            soil_type="Loam",
            properties={"clay": 250, "sand": 400, "silt": 350},
            message=f"Using default soil type (API unavailable). Location: ({location.lat}, {location.lon})"
        )
    except Exception as e:
        print(f"[SOIL API ERROR] {type(e).__name__}: {str(e)}")
        # Return default soil data instead of raising exception
        return SoilDetectionResponse(
            soil_type="Loam",
            properties={"clay": 250, "sand": 400, "silt": 350},
            message=f"Using default soil type (error occurred). Location: ({location.lat}, {location.lon})"
        )


# Route 2: Get Weather Data
@router.post("/weather", response_model=WeatherResponse)
async def get_weather(location: LocationRequest):
    """
    Get weather data from OpenWeatherMap API based on latitude and longitude.
    Returns default values if API fails to ensure endpoint always works.
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            print("[WEATHER API] No API key found, using default weather data")
            # Return default weather instead of raising exception
            return WeatherResponse(
                temperature=25.0,
                humidity=65.0,
                rainfall=100.0,
                weather_description="Clear sky",
                location="Unknown location"
            )
        
        # OpenWeatherMap API endpoint
        url = "https://api.openweathermap.org/data/2.5/weather"
        
        params = {
            "lat": location.lat,
            "lon": location.lon,
            "appid": api_key,
            "units": "metric"  # Get temperature in Celsius
        }
        
        print(f"[WEATHER API] Requesting weather data for lat={location.lat}, lon={location.lon}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Validate API response structure
        if not data or "main" not in data:
            print("[WEATHER API] Invalid response structure, using defaults")
            raise ValueError("Invalid API response structure")
        
        # Extract weather information with None checks
        temperature = data.get("main", {}).get("temp")
        humidity = data.get("main", {}).get("humidity")
        
        # Ensure values are not None
        if temperature is None:
            temperature = 25.0
            print(f"[WEATHER API] Temperature is None, using default: {temperature}")
        if humidity is None:
            humidity = 65.0
            print(f"[WEATHER API] Humidity is None, using default: {humidity}")
        
        weather_description = "Clear sky"
        if data.get("weather") and len(data["weather"]) > 0:
            weather_description = data["weather"][0].get("description", "Clear sky")
        
        location_name = data.get("name", "Unknown location")
        
        # Calculate rainfall (if available in rain data)
        rainfall = 100.0  # Default rainfall
        if "rain" in data and data["rain"]:
            # Rain volume for last 1 hour or 3 hours
            rainfall = data["rain"].get("1h", data["rain"].get("3h", 100.0))
        
        print(f"[WEATHER API] Weather data - Temp: {temperature}°C, Humidity: {humidity}%, Rainfall: {rainfall}mm")
        
        return WeatherResponse(
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            weather_description=weather_description,
            location=location_name
        )
    
    except httpx.HTTPStatusError as e:
        print(f"[WEATHER API ERROR] HTTP {e.response.status_code}: {str(e)}")
        # Return default weather data instead of raising exception
        return WeatherResponse(
            temperature=25.0,
            humidity=65.0,
            rainfall=100.0,
            weather_description="Clear sky (API unavailable)",
            location="Unknown location"
        )
    except KeyError as e:
        print(f"[WEATHER API ERROR] Missing key: {str(e)}")
        # Return default weather data
        return WeatherResponse(
            temperature=25.0,
            humidity=65.0,
            rainfall=100.0,
            weather_description="Clear sky (data incomplete)",
            location="Unknown location"
        )
    except Exception as e:
        print(f"[WEATHER API ERROR] {type(e).__name__}: {str(e)}")
        # Return default weather data instead of raising exception
        return WeatherResponse(
            temperature=25.0,
            humidity=65.0,
            rainfall=100.0,
            weather_description="Clear sky (error occurred)",
            location="Unknown location"
        )


# Route 3: Get Crop Recommendations (ML-based)
@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_crops(request: RecommendationRequest):
    """
    Recommend crops using trained CatBoost ML model based on soil and environmental parameters.
    """
    try:
        # Get soil defaults for N, P, K, ph if not provided
        soil_defaults = get_soil_defaults(request.soil_type)
        
        # Use provided values or defaults from soil type
        N = request.N if request.N is not None else soil_defaults["N"]
        P = request.P if request.P is not None else soil_defaults["P"]
        K = request.K if request.K is not None else soil_defaults["K"]
        ph = request.ph if request.ph is not None else soil_defaults["ph"]
        humidity = request.humidity if request.humidity is not None else 70.0  # Default humidity
        
        # Get ML model instance
        ml_model = get_model()
        
        # Get predictions from ML model
        ml_predictions = ml_model.predict(
            N=N,
            P=P,
            K=K,
            temperature=request.temperature,
            humidity=humidity,
            ph=ph,
            rainfall=request.rainfall
        )
        
        # Convert ML predictions to CropRecommendation format
        recommendations = []
        crop_names = [str(pred['crop_name']).strip() for pred in ml_predictions]
        
        # Fetch market prices for all recommended crops
        market_prices = await get_market_prices_batch(crop_names, state=None)
        
        for pred in ml_predictions:
            # Ensure crop_name is a properly formatted string (already title-cased from ml_service)
            crop_name = str(pred['crop_name']).strip()
            
            # CRITICAL: Validate and clamp suitability score (defense-in-depth)
            score = pred['suitability_score']
            if score > 100.0:
                print(f"[API WARNING] Score {score}% > 100 for {crop_name}, clamping to 100")
                score = 100.0
            elif score < 0.0:
                print(f"[API WARNING] Score {score}% < 0 for {crop_name}, clamping to 0")
                score = 0.0
            
            # Generate reason based on suitability score
            if score >= 80:
                confidence = "Highly suitable"
            elif score >= 60:
                confidence = "Suitable"
            elif score >= 40:
                confidence = "Moderately suitable"
            else:
                confidence = "Less suitable"
            
            reason = (
                f"{confidence} based on ML model prediction "
                f"(confidence: {pred['probability']:.2%}). "
                f"Soil: {request.soil_type}, Temp: {request.temperature}°C, "
                f"Rainfall: {request.rainfall}mm, Humidity: {humidity}%"
            )
            
            # Get market price for this crop
            market_price = market_prices.get(crop_name)
            
            recommendations.append(
                CropRecommendation(
                    crop_name=crop_name,
                    suitability_score=score,
                    reason=reason,
                    market_price=market_price
                )
            )
        
        # Fallback if no recommendations
        if not recommendations:
            recommendations.append(
                CropRecommendation(
                    crop_name="No suitable crops found",
                    suitability_score=0.0,
                    reason="The ML model could not generate recommendations. Please check input parameters.",
                    market_price=None
                )
            )
        
        return RecommendationResponse(
            recommendations=recommendations,
            input_parameters={
                "soil_type": request.soil_type,
                "N": N,
                "P": P,
                "K": K,
                "temperature": request.temperature,
                "humidity": humidity,
                "ph": ph,
                "rainfall": request.rainfall
            }
        )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"ML model not available: {str(e)}. Please train the model first using train_model.py"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating crop recommendations: {str(e)}"
        )


# Route 4: Manual Crop Recommendation
@router.post("/recommend-manual", response_model=RecommendationResponse)
async def recommend_manual(request: ManualRecommendationRequest):
    """
    Recommend crops using manual NPK and weather inputs.
    For farmers without GPS or location access.
    """
    try:
        # Get ML model instance
        ml_model = get_model()
        
        # Get predictions from ML model
        ml_predictions = ml_model.predict(
            N=request.N,
            P=request.P,
            K=request.K,
            temperature=request.temperature,
            humidity=request.humidity,
            ph=request.ph,
            rainfall=request.rainfall
        )
        
        # Filter predictions where suitability_score > 5
        filtered_predictions = [
            pred for pred in ml_predictions 
            if pred['suitability_score'] > 5
        ]
        
        # If no predictions meet the threshold, use all predictions
        if not filtered_predictions:
            filtered_predictions = ml_predictions
        
        # Convert ML predictions to CropRecommendation format
        recommendations = []
        crop_names = [str(pred['crop_name']).strip().capitalize() for pred in filtered_predictions[:5]]
        
        # Fetch market prices for all recommended crops
        market_prices = await get_market_prices_batch(crop_names, state=None)
        
        for pred in filtered_predictions[:5]:  # Top 5 recommendations
            # Ensure crop_name is a properly formatted string
            crop_name = str(pred['crop_name']).strip().capitalize()
            
            # CRITICAL: Validate and clamp suitability score (defense-in-depth)
            score = pred['suitability_score']
            if score > 100.0:
                print(f"[API WARNING] Score {score}% > 100 for {crop_name}, clamping to 100")
                score = 100.0
            elif score < 0.0:
                print(f"[API WARNING] Score {score}% < 0 for {crop_name}, clamping to 0")
                score = 0.0
            
            # Generate reason based on suitability score
            if score >= 80:
                confidence = "Highly suitable"
            elif score >= 60:
                confidence = "Suitable"
            elif score >= 40:
                confidence = "Moderately suitable"
            else:
                confidence = "Less suitable"
            
            reason = (
                f"{confidence} based on ML model prediction "
                f"(confidence: {pred['probability']:.2%}). "
                f"N: {request.N}, P: {request.P}, K: {request.K}, "
                f"Temp: {request.temperature}°C, Humidity: {request.humidity}%, "
                f"pH: {request.ph}, Rainfall: {request.rainfall}mm"
            )
            
            # Get market price for this crop
            market_price = market_prices.get(crop_name)
            
            recommendations.append(
                CropRecommendation(
                    crop_name=crop_name,
                    suitability_score=score,
                    reason=reason,
                    market_price=market_price
                )
            )
        
        # Fallback if no recommendations
        if not recommendations:
            recommendations.append(
                CropRecommendation(
                    crop_name="No suitable crops found",
                    suitability_score=0.0,
                    reason="The ML model could not generate recommendations. Please check input parameters.",
                    market_price=None
                )
            )
        
        return RecommendationResponse(
            recommendations=recommendations,
            input_parameters={
                "N": request.N,
                "P": request.P,
                "K": request.K,
                "temperature": request.temperature,
                "humidity": request.humidity,
                "ph": request.ph,
                "rainfall": request.rainfall
            }
        )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"ML model not available: {str(e)}. Please train the model first using train_model.py"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating crop recommendations: {str(e)}"
        )


# Route 5: Combined Recommendation from Location
@router.post("/recommend-from-location", response_model=CombinedRecommendationResponse)
async def recommend_from_location(location: LocationRequest):
    """
    Get comprehensive crop recommendations based on location.
    Combines soil detection, weather data, and crop recommendations.
    """
    try:
        # Step 1: Detect soil type
        soil_response = await detect_soil(location)
        
        # Step 2: Get weather data
        weather_response = await get_weather(location)
        
        # Step 3: Create recommendation request
        recommendation_request = RecommendationRequest(
            soil_type=soil_response.soil_type,
            temperature=weather_response.temperature,
            rainfall=weather_response.rainfall,
            humidity=weather_response.humidity
        )
        
        # Step 4: Get crop recommendations
        recommendation_response = await recommend_crops(recommendation_request)
        
        # Step 5: Build combined response
        return CombinedRecommendationResponse(
            location_info={
                "latitude": location.lat,
                "longitude": location.lon,
                "name": weather_response.location
            },
            detected_soil=soil_response,
            current_weather=weather_response,
            recommendations=recommendation_response.recommendations,
            input_parameters=recommendation_response.input_parameters
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions from internal calls
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating combined recommendations: {str(e)}"
        )


# Translation Models
class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language code (en, te, hi)")

class TranslationResponse(BaseModel):
    translated_text: str


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text to target language using LibreTranslate API
    
    Supported languages:
    - en: English
    - te: Telugu (తెలుగు)
    - hi: Hindi (हिन्दी)
    """
    # Language code mapping
    lang_map = {
        'en': 'en',
        'te': 'te',  # Telugu
        'hi': 'hi'   # Hindi
    }
    
    target_lang = lang_map.get(request.target_language, 'en')
    
    # If target is English or text is empty, return as-is
    if target_lang == 'en' or not request.text or request.text.strip() == '':
        return TranslationResponse(translated_text=request.text)
    
    try:
        # Use LibreTranslate public API
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                'https://libretranslate.com/translate',
                json={
                    'q': request.text,
                    'source': 'en',
                    'target': target_lang,
                    'format': 'text'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                translated = data.get('translatedText', request.text)
                print(f"✅ Translation: '{request.text}' → '{translated}' ({target_lang})")
                return TranslationResponse(translated_text=translated)
            else:
                print(f"⚠️ Translation API error: {response.status_code}")
                # Fallback to original text
                return TranslationResponse(translated_text=request.text)
                
    except httpx.TimeoutException:
        print("⚠️ Translation timeout - using original text")
        return TranslationResponse(translated_text=request.text)
    except Exception as e:
        print(f"⚠️ Translation error: {str(e)} - using original text")
        # Fallback to original text on any error
        return TranslationResponse(translated_text=request.text)


# ========== PROFILE MANAGEMENT ==========

# In-memory storage (use MongoDB/PostgreSQL for production)
user_profiles = {}

class ProfileRequest(BaseModel):
    user_id: str
    name: str
    email: str
    phone: Optional[str] = ""
    location: Optional[str] = ""
    farm_size: Optional[str] = ""
    farm_type: Optional[str] = ""
    preferred_language: Optional[str] = "en"

@router.post("/profile/save")
async def save_profile(profile: ProfileRequest):
    """Save or update user profile"""
    try:
        profile_data = {
            'user_id': profile.user_id,
            'name': profile.name,
            'email': profile.email,
            'phone': profile.phone,
            'location': profile.location,
            'farm_size': profile.farm_size,
            'farm_type': profile.farm_type,
            'preferred_language': profile.preferred_language,
            'updated_at': datetime.now().isoformat()
        }
        
        user_profiles[profile.user_id] = profile_data
        print(f"✅ Profile saved for user: {profile.user_id}")
        
        return {
            'success': True,
            'message': 'Profile saved successfully',
            'profile': profile_data
        }
    except Exception as e:
        print(f"❌ Profile save error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile"""
    try:
        profile = user_profiles.get(user_id)
        
        if not profile:
            return {
                'success': False,
                'message': 'Profile not found',
                'profile': None
            }
        
        return {
            'success': True,
            'profile': profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== COMMUNITY & FEEDBACK ==========

# In-memory storage (use MongoDB/PostgreSQL for production)
community_posts = []

class FeedbackRequest(BaseModel):
    name: str
    email: Optional[str] = ""
    feedback_type: str
    message: str
    rating: int = 0
    show_in_community: bool = True

class CommunityPostRequest(BaseModel):
    author: str
    title: str
    content: str

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback and optionally post to community"""
    try:
        feedback_id = str(len(community_posts) + 1)
        
        feedback_data = {
            'id': feedback_id,
            'name': feedback.name,
            'email': feedback.email,
            'feedback_type': feedback.feedback_type,
            'message': feedback.message,
            'rating': feedback.rating,
            'timestamp': datetime.now().isoformat(),
            'show_in_community': feedback.show_in_community
        }
        
        # If user wants to share in community, add as post
        if feedback.show_in_community:
            community_post = {
                'id': feedback_id,
                'author': feedback.name,
                'title': f"Feedback: {feedback.feedback_type.title()}",
                'content': feedback.message,
                'type': 'feedback',
                'rating': feedback.rating,
                'timestamp': feedback_data['timestamp'],
                'likes': 0,
                'comments': 0
            }
            
            community_posts.insert(0, community_post)
            print(f"✅ Feedback posted to community: {feedback_id}")
        
        return {
            'success': True,
            'message': 'Feedback submitted successfully',
            'posted_to_community': feedback.show_in_community
        }
    except Exception as e:
        print(f"❌ Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/community-posts")
async def get_community_posts():
    """Get all community posts (including feedback posts)"""
    try:
        return {
            'success': True,
            'posts': community_posts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/community-post")
async def create_community_post(post: CommunityPostRequest):
    """Create a regular community post"""
    try:
        post_id = str(len(community_posts) + 1)
        
        post_data = {
            'id': post_id,
            'author': post.author,
            'title': post.title,
            'content': post.content,
            'type': 'post',
            'timestamp': datetime.now().isoformat(),
            'likes': 0,
            'comments': 0
        }
        
        community_posts.insert(0, post_data)
        print(f"✅ Community post created: {post_id}")
        
        return {
            'success': True,
            'message': 'Post created successfully',
            'post_id': post_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))