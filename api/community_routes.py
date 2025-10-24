"""
API routes for community features: feedback, posts, and translation.

Translation Configuration:
- Set LIBRETRANSLATE_API_URL in .env (default: https://libretranslate.com/translate)
- Optionally set LIBRETRANSLATE_API_KEY for private instances
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging

# MongoDB
from db import get_collection

# LibreTranslate utility
from utils.translation import translate_text as libretranslate_translate

# Pydantic models
from models.community_models import (
    FeedbackRequest,
    FeedbackResponse,
    CommunityPostRequest,
    CommunityPostResponse,
    TranslationRequest,
    TranslationResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["community"])


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback to the database.
    
    Args:
        feedback: FeedbackRequest containing name, email, message, and language
        
    Returns:
        FeedbackResponse with success status and feedback ID
        
    Raises:
        HTTPException: If database operation fails
    """
    try:
        # Get feedbacks collection
        feedbacks_collection = get_collection("feedbacks")
        
        # Prepare feedback document
        feedback_doc = {
            "name": feedback.name,
            "email": feedback.email,
            "message": feedback.message,
            "language": feedback.language,
            "created_at": datetime.utcnow(),
            "status": "pending"  # Can be used for tracking feedback review status
        }
        
        # Insert into database
        result = await feedbacks_collection.insert_one(feedback_doc)
        
        logger.info(f"Feedback submitted successfully by {feedback.name} ({feedback.email})")
        
        return FeedbackResponse(
            success=True,
            message="Feedback submitted successfully. Thank you for your input!",
            feedback_id=str(result.inserted_id)
        )
        
    except RuntimeError as e:
        # Database not initialized
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is not available. Please try again later."
        )
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.post("/community-post", response_model=CommunityPostResponse, status_code=status.HTTP_201_CREATED)
async def create_community_post(post: CommunityPostRequest):
    """
    Create a new community post.
    
    Args:
        post: CommunityPostRequest containing author, title, content, and language
        
    Returns:
        CommunityPostResponse with success status and post ID
        
    Raises:
        HTTPException: If database operation fails
    """
    try:
        # Get community_posts collection
        posts_collection = get_collection("community_posts")
        
        # Prepare post document
        post_doc = {
            "author": post.author,
            "title": post.title,
            "content": post.content,
            "language": post.language,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "likes": 0,
            "comments": [],
            "status": "published"  # Can be used for moderation
        }
        
        # Insert into database
        result = await posts_collection.insert_one(post_doc)
        
        logger.info(f"Community post created successfully by {post.author}: '{post.title}'")
        
        return CommunityPostResponse(
            success=True,
            message="Community post created successfully!",
            post_id=str(result.inserted_id)
        )
        
    except RuntimeError as e:
        # Database not initialized
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is not available. Please try again later."
        )
    except Exception as e:
        logger.error(f"Error creating community post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create community post: {str(e)}"
        )


@router.post("/translate", response_model=TranslationResponse)
async def translate_text_endpoint(translation_request: TranslationRequest):
    """
    Translate text to the target language using LibreTranslate API.
    
    Configuration:
    - Set LIBRETRANSLATE_API_URL in .env (default: https://libretranslate.com/translate)
    - Optionally set LIBRETRANSLATE_API_KEY for private instances
    
    Args:
        translation_request: TranslationRequest containing text, target_language, and optional source_language
        
    Returns:
        TranslationResponse with translated text and metadata
    """
    # Get source language from request or default to 'auto'
    source_lang = getattr(translation_request, 'source_language', 'auto')
    
    # Call LibreTranslate utility
    result = await libretranslate_translate(
        text=translation_request.text,
        target_language=translation_request.target_language,
        source_language=source_lang
    )
    
    # Return the result (already in TranslationResponse format)
    return TranslationResponse(**result)


@router.get("/feedback/stats")
async def get_feedback_stats():
    """
    Get statistics about submitted feedback (optional utility endpoint).
    
    Returns:
        Dictionary with feedback statistics
    """
    try:
        feedbacks_collection = get_collection("feedbacks")
        
        total_count = await feedbacks_collection.count_documents({})
        pending_count = await feedbacks_collection.count_documents({"status": "pending"})
        
        return {
            "total_feedbacks": total_count,
            "pending_feedbacks": pending_count,
            "reviewed_feedbacks": total_count - pending_count
        }
        
    except Exception as e:
        logger.error(f"Error fetching feedback stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch feedback statistics: {str(e)}"
        )


@router.get("/community-posts/recent")
async def get_recent_posts(limit: int = 10):
    """
    Get recent community posts (optional utility endpoint).
    
    Args:
        limit: Maximum number of posts to return (default: 10)
        
    Returns:
        List of recent community posts
    """
    try:
        posts_collection = get_collection("community_posts")
        
        # Find recent posts, sorted by creation date (descending)
        cursor = posts_collection.find(
            {"status": "published"}
        ).sort("created_at", -1).limit(limit)
        
        posts = []
        async for post in cursor:
            # Convert ObjectId to string for JSON serialization
            post["_id"] = str(post["_id"])
            # Convert datetime to ISO format string
            post["created_at"] = post["created_at"].isoformat()
            post["updated_at"] = post["updated_at"].isoformat()
            posts.append(post)
        
        return {
            "success": True,
            "count": len(posts),
            "posts": posts
        }
        
    except Exception as e:
        logger.error(f"Error fetching recent posts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent posts: {str(e)}"
        )
