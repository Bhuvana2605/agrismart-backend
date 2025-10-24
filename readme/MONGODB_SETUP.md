# MongoDB and Community Features Setup Guide

## Overview
This guide explains how to set up MongoDB with Motor (async driver) and configure the new community features: Feedback API, Community Posts API, and Translation API.

## Architecture

### Files Created

1. **`db.py`** - MongoDB connection management
   - Async connection using Motor
   - Connection lifecycle management
   - Database and collection access functions

2. **`models/community_models.py`** - Pydantic models for request/response validation
   - `FeedbackRequest` / `FeedbackResponse`
   - `CommunityPostRequest` / `CommunityPostResponse`
   - `TranslationRequest` / `TranslationResponse`

3. **`api/community_routes.py`** - API endpoints
   - `/api/feedback` - Submit user feedback
   - `/api/community-post` - Create community posts
   - `/api/translate` - Translate text using Google Cloud Translate

4. **`main.py`** - Updated with MongoDB lifecycle and new routes

## Prerequisites

### 1. Install MongoDB

**Option A: Local MongoDB Installation**
```bash
# Windows (using Chocolatey)
choco install mongodb

# Or download from: https://www.mongodb.com/try/download/community

# Start MongoDB service
net start MongoDB
```

**Option B: MongoDB Atlas (Cloud)**
1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get your connection string

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `motor==3.3.2` - Async MongoDB driver
- `pymongo==4.6.1` - MongoDB Python driver
- `google-cloud-translate==3.15.0` - Google Cloud Translation API

### 3. Set Up Google Cloud Translation API

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable the Cloud Translation API
4. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Grant "Cloud Translation API User" role
   - Create and download JSON key file
5. Save the JSON key file securely (e.g., `google-credentials.json`)

## Environment Configuration

### .env File Setup

Your `.env` file should contain:

```env
# OpenWeatherMap API Key
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Data.gov.in API Key
DATA_GOV_API_KEY=your_data_gov_api_key_here

# MongoDB Connection String
# For local MongoDB:
MONGO_URI=mongodb://localhost:27017/crop_recommendation_db

# For MongoDB Atlas (cloud):
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/crop_recommendation_db?retryWrites=true&w=majority

# MongoDB Database Name (optional)
MONGO_DB_NAME=crop_recommendation_db

# Google Cloud Translation API Credentials
# Absolute path to your service account JSON key file
GOOGLE_APPLICATION_CREDENTIALS=C:/path/to/your/google-credentials.json
```

### Important Notes:

1. **MONGO_URI**: 
   - Local: `mongodb://localhost:27017/crop_recommendation_db`
   - Atlas: Get from MongoDB Atlas dashboard (Connect > Connect your application)
   - Include username/password if authentication is enabled

2. **GOOGLE_APPLICATION_CREDENTIALS**:
   - Must be an absolute path to the JSON key file
   - Use forward slashes (/) even on Windows
   - Example: `C:/Users/YourName/credentials/google-key.json`

3. **Security**:
   - Never commit `.env` file to version control
   - Keep API keys and credentials secure
   - Use environment-specific `.env` files for different deployments

## Database Collections

The application uses two MongoDB collections:

### 1. `feedbacks` Collection

**Schema:**
```json
{
  "_id": ObjectId,
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Great app! Very helpful for crop recommendations.",
  "language": "en",
  "created_at": ISODate("2025-01-20T12:00:00Z"),
  "status": "pending"
}
```

### 2. `community_posts` Collection

**Schema:**
```json
{
  "_id": ObjectId,
  "author": "Jane Smith",
  "title": "Best practices for rice cultivation",
  "content": "Here are some tips I've learned...",
  "language": "en",
  "created_at": ISODate("2025-01-20T12:00:00Z"),
  "updated_at": ISODate("2025-01-20T12:00:00Z"),
  "likes": 0,
  "comments": [],
  "status": "published"
}
```

## API Endpoints

### 1. Submit Feedback

**Endpoint:** `POST /api/feedback`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "This is my feedback about the application.",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully. Thank you for your input!",
  "feedback_id": "65a1b2c3d4e5f6g7h8i9j0k1"
}
```

**Validation Rules:**
- `name`: 1-100 characters, not just whitespace
- `email`: Valid email format
- `message`: 10-2000 characters, not just whitespace
- `language`: At least 2 characters (e.g., "en", "hi", "es")

### 2. Create Community Post

**Endpoint:** `POST /api/community-post`

**Request Body:**
```json
{
  "author": "Jane Smith",
  "title": "Best practices for rice cultivation",
  "content": "Here are some tips I've learned over the years about growing rice in different soil conditions...",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Community post created successfully!",
  "post_id": "65a1b2c3d4e5f6g7h8i9j0k2"
}
```

**Validation Rules:**
- `author`: 1-100 characters, not just whitespace
- `title`: 5-200 characters, not just whitespace
- `content`: 20-5000 characters, not just whitespace
- `language`: At least 2 characters

### 3. Translate Text

**Endpoint:** `POST /api/translate`

**Request Body:**
```json
{
  "text": "Hello, how are you?",
  "target_language": "hi"
}
```

**Response (Success):**
```json
{
  "success": true,
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "source_language": "en",
  "target_language": "hi",
  "error": null
}
```

**Response (Error):**
```json
{
  "success": false,
  "translated_text": null,
  "target_language": "hi",
  "error": "Translation service is not configured. Please set GOOGLE_APPLICATION_CREDENTIALS."
}
```

**Validation Rules:**
- `text`: 1-5000 characters, not just whitespace
- `target_language`: At least 2 characters (ISO 639-1 language code)

**Supported Language Codes:**
- `en` - English
- `hi` - Hindi
- `es` - Spanish
- `fr` - French
- `de` - German
- `zh` - Chinese
- `ja` - Japanese
- And many more...

### 4. Bonus Endpoints

**Get Feedback Statistics:**
```
GET /api/feedback/stats
```

**Get Recent Community Posts:**
```
GET /api/community-posts/recent?limit=10
```

## Testing the APIs

### 1. Start MongoDB

```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### 2. Start the FastAPI Server

```bash
cd backend
python main.py
```

You should see:
```
✓ Successfully connected to MongoDB database: crop_recommendation_db
INFO:     Application startup complete.
```

### 3. Test Feedback API

```bash
curl -X POST "http://localhost:8000/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Great application! Very helpful for farmers.",
    "language": "en"
  }'
```

### 4. Test Community Post API

```bash
curl -X POST "http://localhost:8000/api/community-post" \
  -H "Content-Type: application/json" \
  -d '{
    "author": "Jane Smith",
    "title": "Rice Cultivation Tips",
    "content": "Here are some best practices for growing rice in different soil conditions. First, ensure proper water management...",
    "language": "en"
  }'
```

### 5. Test Translation API

```bash
curl -X POST "http://localhost:8000/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, welcome to our crop recommendation system",
    "target_language": "hi"
  }'
```

### 6. Access API Documentation

Open your browser and go to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Error Handling

### MongoDB Connection Errors

If MongoDB is not running or connection fails:
```
Warning: Failed to connect to MongoDB: ...
Community features (feedback, posts, translation) will not be available.
```

The application will still start, but community endpoints will return 503 errors.

### Translation API Errors

If Google credentials are not configured:
```json
{
  "success": false,
  "error": "Translation service is not configured. Please set GOOGLE_APPLICATION_CREDENTIALS."
}
```

### Validation Errors

If request data is invalid:
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

## MongoDB Management

### View Data Using MongoDB Compass

1. Download MongoDB Compass: https://www.mongodb.com/products/compass
2. Connect using your `MONGO_URI`
3. Browse collections: `feedbacks` and `community_posts`

### Using MongoDB Shell

```bash
# Connect to MongoDB
mongosh

# Switch to database
use crop_recommendation_db

# View feedbacks
db.feedbacks.find().pretty()

# View community posts
db.community_posts.find().pretty()

# Count documents
db.feedbacks.countDocuments()
db.community_posts.countDocuments()
```

## Production Considerations

### 1. MongoDB Atlas (Recommended for Production)

- Use MongoDB Atlas for managed cloud database
- Enable authentication and IP whitelisting
- Use connection string with SSL: `mongodb+srv://...`

### 2. Security

- Use strong passwords for MongoDB
- Enable authentication in production
- Restrict CORS origins in `main.py`
- Rotate API keys regularly
- Use secrets management (e.g., AWS Secrets Manager, Azure Key Vault)

### 3. Performance

- Create indexes on frequently queried fields:
  ```javascript
  db.feedbacks.createIndex({ "created_at": -1 })
  db.community_posts.createIndex({ "created_at": -1 })
  db.community_posts.createIndex({ "author": 1 })
  ```

### 4. Monitoring

- Enable MongoDB monitoring in Atlas
- Log all API errors
- Set up alerts for failed connections

## Troubleshooting

### Issue: "Database not initialized" error

**Solution:** Ensure MongoDB is running and `MONGO_URI` is correct in `.env`

### Issue: Translation API not working

**Solution:** 
1. Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. Check that the JSON key file exists
3. Ensure Cloud Translation API is enabled in Google Cloud Console
4. Verify service account has correct permissions

### Issue: Connection timeout to MongoDB

**Solution:**
1. Check if MongoDB service is running
2. Verify firewall settings
3. For Atlas: Check IP whitelist settings

### Issue: "Email validation failed"

**Solution:** Ensure email format is valid (e.g., `user@example.com`)

## Next Steps

1. **Add Authentication**: Implement JWT-based authentication for community features
2. **Add Pagination**: Implement pagination for fetching posts
3. **Add Search**: Add full-text search for community posts
4. **Add Moderation**: Implement content moderation for posts and feedback
5. **Add Notifications**: Send email notifications for new feedback
6. **Add Caching**: Use Redis for caching translations and frequently accessed data

## Support

For issues or questions:
- Check logs in the console
- Review MongoDB connection status
- Verify all environment variables are set correctly
- Test each API endpoint individually using the provided curl commands
