# LibreTranslate and MongoDB Atlas Setup Guide

## Overview
This guide explains the refactored backend setup using:
- **LibreTranslate** for translation (replacing Google Cloud Translate)
- **MongoDB Atlas** for cloud database (replacing local MongoDB)

## What Changed

### ✅ Removed
- ❌ Google Cloud Translation API
- ❌ Google Cloud credentials and service account setup
- ❌ `google-cloud-translate` dependency
- ❌ Local MongoDB references
- ❌ `GOOGLE_APPLICATION_CREDENTIALS` environment variable

### ✅ Added
- ✅ LibreTranslate API integration (free, open-source)
- ✅ MongoDB Atlas cloud database configuration
- ✅ `utils/translation.py` utility module
- ✅ `LIBRETRANSLATE_API_URL` and `LIBRETRANSLATE_API_KEY` environment variables

---

## LibreTranslate Configuration

### What is LibreTranslate?
LibreTranslate is a free, open-source machine translation API that:
- Works without API keys (public instance)
- Can be self-hosted for unlimited usage
- Supports 30+ languages
- No vendor lock-in

### Configuration in .env

```env
# LibreTranslate API URL
# Default: Public instance at https://libretranslate.com/translate
LIBRETRANSLATE_API_URL=https://libretranslate.com/translate

# API Key (optional, only for some instances)
LIBRETRANSLATE_API_KEY=
```

### Where to Set Configuration

**File:** `backend/.env`

**Options:**

1. **Public Instance (Default - No API Key)**
   ```env
   LIBRETRANSLATE_API_URL=https://libretranslate.com/translate
   LIBRETRANSLATE_API_KEY=
   ```

2. **Self-Hosted Instance**
   ```env
   LIBRETRANSLATE_API_URL=http://your-server:5000/translate
   LIBRETRANSLATE_API_KEY=
   ```

3. **Managed Instance with API Key**
   ```env
   LIBRETRANSLATE_API_URL=https://your-instance.com/translate
   LIBRETRANSLATE_API_KEY=your_api_key_here
   ```

### How It Works

The translation utility (`utils/translation.py`) uses `os.getenv()` to dynamically load configuration:

```python
# Get API URL from environment (with default fallback)
api_url = os.getenv(
    "LIBRETRANSLATE_API_URL",
    "https://libretranslate.com/translate"
)

# Get optional API key
api_key = os.getenv("LIBRETRANSLATE_API_KEY")
```

---

## MongoDB Atlas Configuration

### What is MongoDB Atlas?
MongoDB Atlas is a fully managed cloud database service that:
- Provides free tier (512MB storage)
- Handles backups, scaling, and security
- Accessible from anywhere
- No local MongoDB installation needed

### Setup Steps

#### 1. Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for a free account
3. Create a new project

#### 2. Create a Cluster
1. Click "Build a Cluster"
2. Choose "Shared" (Free tier)
3. Select cloud provider and region
4. Click "Create Cluster" (takes 3-5 minutes)

#### 3. Create Database User
1. Go to "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Set username and password (save these!)
5. Grant "Read and write to any database" role

#### 4. Configure Network Access
1. Go to "Network Access"
2. Click "Add IP Address"
3. Choose "Allow Access from Anywhere" (0.0.0.0/0) for development
4. Or add your specific IP address for production

#### 5. Get Connection String
1. Go to "Clusters"
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<password>` with your database user password
6. Replace `<dbname>` with `crop_recommendation_db`

**Example Connection String:**
```
mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net/crop_recommendation_db?retryWrites=true&w=majority
```

### Configuration in .env

```env
# MongoDB Atlas Connection String
MONGO_URI=mongodb+srv://your_username:your_password@cluster0.mongodb.net/crop_recommendation_db?retryWrites=true&w=majority

# Database Name (optional)
MONGO_DB_NAME=crop_recommendation_db
```

### Where to Set Configuration

**File:** `backend/.env`

**Important Notes:**
- Replace `your_username` with your MongoDB Atlas username
- Replace `your_password` with your MongoDB Atlas password
- Replace `cluster0` with your actual cluster name
- Keep the `?retryWrites=true&w=majority` parameters

---

## Code Structure

### Translation Utility: `utils/translation.py`

**Key Function:**
```python
async def translate_text(
    text: str,
    target_language: str,
    source_language: str = "auto"
) -> Dict[str, any]:
    """
    Translate text using LibreTranslate API.
    
    Configuration from .env:
    - LIBRETRANSLATE_API_URL: API endpoint
    - LIBRETRANSLATE_API_KEY: Optional API key
    """
```

**Features:**
- Async/await support
- Auto-detects source language
- Handles errors gracefully
- 30-second timeout
- Reads config from `os.getenv()`

### Database Connection: `db.py`

**Configuration:**
```python
async def connect_to_mongodb():
    """
    Connect to MongoDB Atlas using MONGO_URI from .env.
    
    Format: mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/<db>
    """
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME", "crop_recommendation_db")
```

**Features:**
- Async Motor driver
- Connection pooling
- Automatic reconnection
- Graceful error handling

### API Routes: `api/community_routes.py`

**Translation Endpoint:**
```python
@router.post("/translate", response_model=TranslationResponse)
async def translate_text_endpoint(translation_request: TranslationRequest):
    """
    Translate text using LibreTranslate.
    
    Request:
    {
      "text": "Hello",
      "target_language": "hi",
      "source_language": "auto"  // optional
    }
    """
```

---

## API Endpoints

### 1. POST /api/translate

**Request:**
```json
{
  "text": "Hello, how are you?",
  "target_language": "hi",
  "source_language": "auto"
}
```

**Response:**
```json
{
  "success": true,
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "source_language": "en",
  "target_language": "hi",
  "error": null
}
```

**Supported Languages:**
- `en` - English
- `hi` - Hindi
- `es` - Spanish
- `fr` - French
- `de` - German
- `zh` - Chinese
- `ja` - Japanese
- `ar` - Arabic
- `pt` - Portuguese
- `ru` - Russian
- `bn` - Bengali
- `ta` - Tamil
- `te` - Telugu
- `mr` - Marathi
- `gu` - Gujarati
- And 15+ more...

### 2. POST /api/feedback

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Great application!",
  "language": "en"
}
```

**Saves to MongoDB Atlas collection:** `feedbacks`

### 3. POST /api/community-post

**Request:**
```json
{
  "author": "Jane Smith",
  "title": "Rice Cultivation Tips",
  "content": "Here are some best practices...",
  "language": "en"
}
```

**Saves to MongoDB Atlas collection:** `community_posts`

---

## Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note:** `google-cloud-translate` has been removed from requirements.txt

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and set:
```env
# MongoDB Atlas (REQUIRED)
MONGO_URI=mongodb+srv://your_username:your_password@cluster0.mongodb.net/crop_recommendation_db?retryWrites=true&w=majority

# LibreTranslate (Optional - uses public instance by default)
LIBRETRANSLATE_API_URL=https://libretranslate.com/translate
LIBRETRANSLATE_API_KEY=
```

### 3. Start the Server

```bash
python main.py
```

**Expected Output:**
```
✓ Successfully connected to MongoDB database: crop_recommendation_db
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Testing

### Test Translation API

```bash
curl -X POST "http://localhost:8000/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, welcome to our crop recommendation system",
    "target_language": "hi",
    "source_language": "en"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "translated_text": "नमस्ते, हमारे फसल अनुशंसा प्रणाली में आपका स्वागत है",
  "source_language": "en",
  "target_language": "hi",
  "error": null
}
```

### Test Feedback API

```bash
curl -X POST "http://localhost:8000/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "message": "Testing MongoDB Atlas integration",
    "language": "en"
  }'
```

### View Data in MongoDB Atlas

1. Go to MongoDB Atlas dashboard
2. Click "Collections" on your cluster
3. Select database: `crop_recommendation_db`
4. View collections: `feedbacks`, `community_posts`

---

## Self-Hosting LibreTranslate (Optional)

For unlimited translations without rate limits:

### Using Docker

```bash
docker run -ti --rm -p 5000:5000 libretranslate/libretranslate
```

### Update .env

```env
LIBRETRANSLATE_API_URL=http://localhost:5000/translate
```

### Benefits
- No rate limits
- Faster response times
- Complete privacy
- Offline capability

---

## Troubleshooting

### Translation Errors

**Issue:** "Translation request timed out"
**Solution:** 
- Check internet connection
- Try self-hosted instance
- Increase timeout in `utils/translation.py`

**Issue:** "LibreTranslate API error: HTTP 429"
**Solution:**
- Rate limit reached on public instance
- Wait a few minutes or self-host

### MongoDB Atlas Connection Errors

**Issue:** "Failed to connect to MongoDB"
**Solutions:**
1. Check connection string format
2. Verify username/password are correct
3. Ensure IP address is whitelisted in Network Access
4. Check if cluster is running (not paused)

**Issue:** "Authentication failed"
**Solution:**
- Verify database user credentials
- Ensure user has read/write permissions
- Check password doesn't contain special characters (URL encode if needed)

### Environment Variable Issues

**Issue:** "MONGO_URI not found"
**Solution:**
- Ensure `.env` file exists in backend directory
- Check `load_dotenv()` is called in `main.py`
- Verify `.env` file has correct format (no quotes around values)

---

## Migration Checklist

If migrating from Google Cloud Translate:

- [x] Remove `google-cloud-translate` from requirements.txt
- [x] Remove `GOOGLE_APPLICATION_CREDENTIALS` from .env
- [x] Update `api/community_routes.py` to use LibreTranslate
- [x] Create `utils/translation.py` utility
- [x] Add `LIBRETRANSLATE_API_URL` to .env
- [x] Update MongoDB URI to Atlas connection string
- [x] Remove localhost MongoDB references
- [x] Test all endpoints
- [x] Update documentation

---

## Production Considerations

### LibreTranslate
- Use self-hosted instance for production
- Set up caching for frequently translated phrases
- Monitor API usage and response times
- Consider load balancing for high traffic

### MongoDB Atlas
- Use M10+ cluster for production (not free tier)
- Enable backup and point-in-time recovery
- Set up monitoring and alerts
- Use specific IP whitelisting (not 0.0.0.0/0)
- Enable authentication and encryption
- Create indexes for frequently queried fields

### Security
- Never commit `.env` file to version control
- Use environment-specific configuration
- Rotate credentials regularly
- Use secrets management service (AWS Secrets Manager, Azure Key Vault)
- Enable HTTPS/TLS for all connections

---

## Support Resources

- **LibreTranslate:** https://libretranslate.com/
- **LibreTranslate GitHub:** https://github.com/LibreTranslate/LibreTranslate
- **MongoDB Atlas:** https://www.mongodb.com/cloud/atlas
- **MongoDB Documentation:** https://docs.mongodb.com/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/

---

## Summary

✅ **No Google Cloud dependencies**  
✅ **Free translation service (LibreTranslate)**  
✅ **Cloud database (MongoDB Atlas)**  
✅ **Simple configuration via .env**  
✅ **Self-hosting option available**  
✅ **All translation via `os.getenv("LIBRETRANSLATE_API_URL")`**  

The backend is now fully configured for cloud deployment with no local dependencies!
