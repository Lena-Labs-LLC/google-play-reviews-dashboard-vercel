"""
Run the FastAPI backend server
"""

import uvicorn
import os

if __name__ == "__main__":
    # Set environment variables if needed
    # os.environ['GEMINI_API_KEY'] = 'your-key-here'
    
    print("Starting Google Play Reviews API Server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


