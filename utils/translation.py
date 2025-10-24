"""
LibreTranslate integration for text translation.

Configuration:
- Set LIBRETRANSLATE_API_URL in .env (default: https://libretranslate.com/translate)
- Optionally set LIBRETRANSLATE_API_KEY if using a private instance or API key
- For self-hosted instances, update the URL to your instance endpoint

Example .env:
    LIBRETRANSLATE_API_URL=https://libretranslate.com/translate
    LIBRETRANSLATE_API_KEY=your_api_key_here  # Optional
"""
import httpx
import os
from typing import Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def translate_text(
    text: str,
    target_language: str,
    source_language: str = "auto"
) -> Dict[str, any]:
    """
    Translate text using LibreTranslate API.
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'hi', 'es', 'fr')
        source_language: Source language code (default: 'auto' for auto-detection)
        
    Returns:
        Dictionary with translation result:
        {
            "success": bool,
            "translated_text": str or None,
            "source_language": str or None,
            "target_language": str,
            "error": str or None
        }
    """
    try:
        # Get LibreTranslate API URL from environment variable
        # Default to public LibreTranslate instance if not set
        api_url = os.getenv(
            "LIBRETRANSLATE_API_URL",
            "https://libretranslate.com/translate"
        )
        
        # Get optional API key (required for some instances)
        api_key = os.getenv("LIBRETRANSLATE_API_KEY")
        
        # Prepare request payload
        payload = {
            "q": text,
            "source": source_language,
            "target": target_language,
            "format": "text"
        }
        
        # Add API key if provided
        if api_key:
            payload["api_key"] = api_key
        
        # Make HTTP POST request to LibreTranslate API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=payload)
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"LibreTranslate API error: HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = f"LibreTranslate API error: {error_data['error']}"
                except Exception:
                    pass
                
                logger.error(error_msg)
                return {
                    "success": False,
                    "translated_text": None,
                    "source_language": source_language if source_language != "auto" else None,
                    "target_language": target_language,
                    "error": error_msg
                }
            
            # Parse response
            result = response.json()
            translated_text = result.get("translatedText")
            detected_language = result.get("detectedLanguage", {})
            
            # Extract detected source language
            if isinstance(detected_language, dict):
                detected_source = detected_language.get("language", source_language)
            else:
                detected_source = detected_language if detected_language else source_language
            
            if not translated_text:
                logger.error("LibreTranslate API returned empty translation")
                return {
                    "success": False,
                    "translated_text": None,
                    "source_language": detected_source if detected_source != "auto" else None,
                    "target_language": target_language,
                    "error": "Translation returned empty result"
                }
            
            logger.info(
                f"Translation successful: {detected_source} -> {target_language}"
            )
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_language": detected_source if detected_source != "auto" else None,
                "target_language": target_language,
                "error": None
            }
            
    except httpx.TimeoutException:
        error_msg = "Translation request timed out"
        logger.error(error_msg)
        return {
            "success": False,
            "translated_text": None,
            "source_language": source_language if source_language != "auto" else None,
            "target_language": target_language,
            "error": error_msg
        }
    except httpx.RequestError as e:
        error_msg = f"Network error during translation: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "translated_text": None,
            "source_language": source_language if source_language != "auto" else None,
            "target_language": target_language,
            "error": error_msg
        }
    except Exception as e:
        error_msg = f"Unexpected error during translation: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "translated_text": None,
            "source_language": source_language if source_language != "auto" else None,
            "target_language": target_language,
            "error": error_msg
        }


def get_supported_languages() -> list:
    """
    Get list of commonly supported languages by LibreTranslate.
    
    Returns:
        List of language codes
    """
    return [
        "en", "ar", "az", "zh", "cs", "nl", "eo", "fi", "fr", "de", "el",
        "hi", "hu", "id", "ga", "it", "ja", "ko", "fa", "pl", "pt", "ru",
        "sk", "es", "sv", "tr", "uk", "vi", "bn", "ta", "te", "mr", "gu"
    ]
