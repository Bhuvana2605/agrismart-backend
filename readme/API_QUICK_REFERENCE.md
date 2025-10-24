# API Quick Reference Guide

## New Community Features Endpoints

### 1. Submit Feedback
```http
POST /api/feedback
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Great application! Very helpful.",
  "language": "en"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Feedback submitted successfully. Thank you for your input!",
  "feedback_id": "65a1b2c3d4e5f6g7h8i9j0k1"
}
```

---

### 2. Create Community Post
```http
POST /api/community-post
Content-Type: application/json

{
  "author": "Jane Smith",
  "title": "Best practices for rice cultivation",
  "content": "Here are some tips I've learned over the years...",
  "language": "en"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Community post created successfully!",
  "post_id": "65a1b2c3d4e5f6g7h8i9j0k2"
}
```

---

### 3. Translate Text
```http
POST /api/translate
Content-Type: application/json

{
  "text": "Hello, welcome to our crop recommendation system",
  "target_language": "hi"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "translated_text": "नमस्ते, हमारे फसल अनुशंसा प्रणाली में आपका स्वागत है",
  "source_language": "en",
  "target_language": "hi",
  "error": null
}
```

---

### 4. Get Feedback Statistics (Bonus)
```http
GET /api/feedback/stats
```

**Response:**
```json
{
  "total_feedbacks": 42,
  "pending_feedbacks": 15,
  "reviewed_feedbacks": 27
}
```

---

### 5. Get Recent Posts (Bonus)
```http
GET /api/community-posts/recent?limit=10
```

**Response:**
```json
{
  "success": true,
  "count": 10,
  "posts": [
    {
      "_id": "65a1b2c3d4e5f6g7h8i9j0k2",
      "author": "Jane Smith",
      "title": "Best practices for rice cultivation",
      "content": "...",
      "language": "en",
      "created_at": "2025-01-20T12:00:00",
      "updated_at": "2025-01-20T12:00:00",
      "likes": 0,
      "comments": [],
      "status": "published"
    }
  ]
}
```

---

## Existing Crop Recommendation Endpoints

### 1. Detect Soil Type
```http
POST /api/detect-soil
Content-Type: application/json

{
  "lat": 28.6139,
  "lon": 77.2090
}
```

---

### 2. Get Weather Data
```http
POST /api/weather
Content-Type: application/json

{
  "lat": 28.6139,
  "lon": 77.2090
}
```

---

### 3. Get Crop Recommendations
```http
POST /api/recommend
Content-Type: application/json

{
  "soil_type": "Loamy",
  "temperature": 25.5,
  "rainfall": 150.0,
  "humidity": 70.0
}
```

**Response includes market prices:**
```json
{
  "recommendations": [
    {
      "crop_name": "Rice",
      "suitability_score": 95.5,
      "reason": "Highly suitable based on ML model prediction...",
      "market_price": 2150.0
    }
  ]
}
```

---

### 4. Combined Recommendation from Location
```http
POST /api/recommend-from-location
Content-Type: application/json

{
  "lat": 28.6139,
  "lon": 77.2090
}
```

---

## Common Language Codes

| Code | Language |
|------|----------|
| `en` | English |
| `hi` | Hindi |
| `es` | Spanish |
| `fr` | French |
| `de` | German |
| `zh` | Chinese |
| `ja` | Japanese |
| `ar` | Arabic |
| `pt` | Portuguese |
| `ru` | Russian |
| `bn` | Bengali |
| `ta` | Tamil |
| `te` | Telugu |
| `mr` | Marathi |
| `gu` | Gujarati |
| `kn` | Kannada |

---

## Error Responses

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Service Unavailable (503)
```json
{
  "detail": "Database service is not available. Please try again later."
}
```

### Internal Server Error (500)
```json
{
  "detail": "Failed to submit feedback: Connection timeout"
}
```

---

## Testing with cURL

### Feedback
```bash
curl -X POST "http://localhost:8000/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","message":"Great app!","language":"en"}'
```

### Community Post
```bash
curl -X POST "http://localhost:8000/api/community-post" \
  -H "Content-Type: application/json" \
  -d '{"author":"Jane","title":"Rice Tips","content":"Here are some tips...","language":"en"}'
```

### Translation
```bash
curl -X POST "http://localhost:8000/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello","target_language":"hi"}'
```

---

## Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide interactive testing interfaces for all endpoints.
