"""
FastAPI backend for Google Play Reviews Dashboard - Vercel Serverless
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import json

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    from auth import GooglePlayAuth
    from reviews import GooglePlayReviews
    from ai_response import AIResponseGenerator
    from user_manager import UserManager
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for missing modules
    GooglePlayAuth = None
    GooglePlayReviews = None
    AIResponseGenerator = None
    UserManager = None

app = FastAPI(
    title="Google Play Reviews API",
    description="API for managing Google Play app reviews with AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://*.vercel.app"],  # Next.js dev server + Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize user manager safely
user_manager = UserManager() if UserManager else None

# Global variables for auth and reviews handler
auth_handler = None
reviews_handler = None
package_name = None

# Pydantic models
class UserRegistration(BaseModel):
    username: str
    password: str
    service_account_data: Dict[str, Any]
    gemini_api_key: str

class UserLogin(BaseModel):
    username: str
    password: str

class PackageConfig(BaseModel):
    package_name: str
    enable_ai: bool = False
    service_account_data: Optional[Dict[str, Any]] = None
    gemini_api_key: Optional[str] = None

class ReplyRequest(BaseModel):
    review_id: str
    reply_text: str

class AutoReplyRequest(BaseModel):
    max_results: int = 5
    dry_run: bool = True

class AIPreviewRequest(BaseModel):
    review_text: str
    rating: int
    review_id: str

# Dependency to get current user
def get_current_user(authorization: str = Header(None)):
    """Get current user from session token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    session_token = authorization.split(" ")[1]
    user = user_manager.get_user_by_token(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return user

# Dependency to get reviews handler
def get_reviews_handler():
    global reviews_handler
    if not reviews_handler:
        raise HTTPException(status_code=400, detail="Package not configured. Call /configure first")
    return reviews_handler

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Google Play Reviews API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# User management endpoints
@app.post("/auth/register")
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    result = user_manager.register_user(
        username=user_data.username,
        password=user_data.password,
        service_account_data=user_data.service_account_data,
        gemini_api_key=user_data.gemini_api_key
    )
    return result

@app.post("/auth/login")
async def login_user(login_data: UserLogin):
    """Login user"""
    result = user_manager.authenticate_user(
        username=login_data.username,
        password=login_data.password
    )
    return result

@app.post("/auth/logout")
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout user"""
    # Note: We need to get the session token from the header
    # This is a simplified version - in production, you'd want to pass the token
    return {"success": True, "message": "Logged out successfully"}

@app.get("/auth/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return {
        "success": True,
        "user": {
            "username": current_user["username"],
            "created_at": current_user["created_at"],
            "last_login": current_user["last_login"]
        }
    }

@app.put("/auth/credentials")
async def update_credentials(
    service_account_data: Optional[Dict[str, Any]] = None,
    gemini_api_key: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user credentials"""
    result = user_manager.update_user_credentials(
        session_token=current_user.get("session_token"),
        service_account_data=service_account_data,
        gemini_api_key=gemini_api_key
    )
    return result

@app.post("/configure")
async def configure(config: PackageConfig):
    """Configure the API with package name and AI settings"""
    global auth_handler, reviews_handler, package_name
    
    try:
        # Check if required classes are available
        if not GooglePlayAuth or not GooglePlayReviews:
            raise HTTPException(status_code=500, detail="Backend modules not available")
        
        package_name = config.package_name
        
        # Use provided service account data
        if not config.service_account_data:
            raise HTTPException(status_code=400, detail="Service account data is required")
        
        auth_handler = GooglePlayAuth(service_account_data=config.service_account_data)
        service = auth_handler.authenticate()
        
        # Create AI generator with provided Gemini API key
        ai_generator = None
        if config.enable_ai:
            if not config.gemini_api_key:
                raise HTTPException(status_code=400, detail="Gemini API key is required for AI features")
            if not AIResponseGenerator:
                raise HTTPException(status_code=500, detail="AI module not available")
            ai_generator = AIResponseGenerator()
            # Set the API key for this session
            os.environ['GEMINI_API_KEY'] = config.gemini_api_key
        
        reviews_handler = GooglePlayReviews(service, package_name, config.enable_ai, ai_generator)
        
        return {
            "success": True,
            "message": f"Configured for package: {package_name}",
            "ai_enabled": config.enable_ai
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")

@app.get("/reviews")
async def get_reviews(
    max_results: int = 10,
    handler: GooglePlayReviews = Depends(get_reviews_handler)
):
    """Get latest reviews"""
    try:
        reviews = handler.list_reviews(max_results)
        return {
            "success": True,
            "count": len(reviews),
            "reviews": reviews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reviews: {str(e)}")

@app.post("/reply")
async def reply_to_review(
    request: ReplyRequest,
    handler: GooglePlayReviews = Depends(get_reviews_handler)
):
    """Reply to a specific review"""
    try:
        success = handler.reply_to_review(request.review_id, request.reply_text)
        return {
            "success": success,
            "review_id": request.review_id,
            "message": "Reply posted successfully" if success else "Failed to post reply"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reply: {str(e)}")

@app.post("/auto-reply")
async def auto_reply(
    request: AutoReplyRequest,
    handler: GooglePlayReviews = Depends(get_reviews_handler)
):
    """Automatically reply to reviews using AI"""
    try:
        if not handler.enable_ai:
            raise HTTPException(status_code=400, detail="AI is not enabled")
        
        results = handler.auto_reply_to_reviews(request.max_results, request.dry_run)
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-reply failed: {str(e)}")

@app.post("/ai-preview")
async def preview_ai_response(
    request: AIPreviewRequest,
    handler: GooglePlayReviews = Depends(get_reviews_handler)
):
    """Preview AI response without posting"""
    try:
        if not handler.enable_ai or not handler.ai_generator:
            raise HTTPException(status_code=400, detail="AI is not enabled")
        
        ai_response = handler.ai_generator.generate_response(
            request.review_text,
            request.rating,
            request.review_id
        )
        
        if not ai_response:
            raise HTTPException(status_code=500, detail="Failed to generate AI response")
        
        return {
            "success": True,
            "response": ai_response,
            "length": len(ai_response),
            "language": handler.ai_generator.detect_language(request.review_text)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI preview failed: {str(e)}")

@app.get("/stats")
async def get_stats(
    handler: GooglePlayReviews = Depends(get_reviews_handler)
):
    """Get AI response statistics"""
    try:
        if not handler.enable_ai:
            return {"success": False, "message": "AI not enabled"}
        
        stats = handler.get_ai_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/history")
async def get_history(
    limit: int = 20,
    handler: GooglePlayReviews = Depends(get_reviews_handler)
):
    """Get AI reply history"""
    try:
        if not handler.enable_ai:
            return {"success": False, "message": "AI not enabled"}
        
        history = handler.get_reply_history()
        # Return last N entries
        recent_history = history[-limit:] if len(history) > limit else history
        
        return {
            "success": True,
            "count": len(recent_history),
            "history": list(reversed(recent_history))  # Newest first
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "configured": reviews_handler is not None,
        "package": package_name
    }

# Vercel serverless function handler
from mangum import Mangum
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
