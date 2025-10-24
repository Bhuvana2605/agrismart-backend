"""
Pydantic models for community features (feedback, posts, translation).
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the person providing feedback")
    email: EmailStr = Field(..., description="Email address for contact")
    message: str = Field(..., min_length=10, max_length=2000, description="Feedback message")
    language: str = Field(default="en", description="Language code (e.g., 'en', 'hi', 'es')")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate that name is not just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip()
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        """Validate that message is not just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty or just whitespace")
        return v.strip()
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        """Validate language code format."""
        if not v or len(v) < 2:
            raise ValueError("Language code must be at least 2 characters")
        return v.lower()


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    success: bool
    message: str
    feedback_id: Optional[str] = None


class CommunityPostRequest(BaseModel):
    """Request model for creating a community post."""
    author: str = Field(..., min_length=1, max_length=100, description="Author name")
    title: str = Field(..., min_length=5, max_length=200, description="Post title")
    content: str = Field(..., min_length=20, max_length=5000, description="Post content")
    language: str = Field(default="en", description="Language code (e.g., 'en', 'hi', 'es')")
    
    @field_validator('author')
    @classmethod
    def validate_author(cls, v):
        """Validate that author is not just whitespace."""
        if not v.strip():
            raise ValueError("Author name cannot be empty or just whitespace")
        return v.strip()
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate that title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or just whitespace")
        return v.strip()
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Validate that content is not just whitespace."""
        if not v.strip():
            raise ValueError("Content cannot be empty or just whitespace")
        return v.strip()
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        """Validate language code format."""
        if not v or len(v) < 2:
            raise ValueError("Language code must be at least 2 characters")
        return v.lower()


class CommunityPostResponse(BaseModel):
    """Response model for community post creation."""
    success: bool
    message: str
    post_id: Optional[str] = None


class TranslationRequest(BaseModel):
    """Request model for text translation."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to translate")
    target_language: str = Field(..., description="Target language code (e.g., 'hi', 'es', 'fr')")
    source_language: str = Field(default="auto", description="Source language code (default: 'auto' for auto-detection)")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """Validate that text is not just whitespace."""
        if not v.strip():
            raise ValueError("Text cannot be empty or just whitespace")
        return v.strip()
    
    @field_validator('target_language')
    @classmethod
    def validate_target_language(cls, v):
        """Validate language code format."""
        if not v or len(v) < 2:
            raise ValueError("Target language code must be at least 2 characters")
        return v.lower()


class TranslationResponse(BaseModel):
    """Response model for text translation."""
    success: bool
    translated_text: Optional[str] = None
    source_language: Optional[str] = None
    target_language: str
    error: Optional[str] = None
