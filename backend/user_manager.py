"""
User management module for Google Play Reviews Dashboard
"""

import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class UserManager:
    def __init__(self):
        self.users_file = "users.json"
        self.sessions_file = "sessions.json"
        self.load_users()
        self.load_sessions()
    
    def load_users(self):
        """Load users from file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
        except Exception:
            self.users = {}
    
    def save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def load_sessions(self):
        """Load sessions from file"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    self.sessions = json.load(f)
            else:
                self.sessions = {}
        except Exception:
            self.sessions = {}
    
    def save_sessions(self):
        """Save sessions to file"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def register_user(self, username: str, password: str, service_account_data: Dict[str, Any], gemini_api_key: str) -> Dict[str, Any]:
        """Register a new user"""
        if username in self.users:
            return {
                "success": False,
                "message": "Username already exists"
            }
        
        hashed_password = self.hash_password(password)
        user_id = secrets.token_urlsafe(16)
        
        self.users[username] = {
            "user_id": user_id,
            "username": username,
            "password_hash": hashed_password,
            "service_account_data": service_account_data,
            "gemini_api_key": gemini_api_key,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self.save_users()
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id
        }
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and create session"""
        if username not in self.users:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
        
        user = self.users[username]
        hashed_password = self.hash_password(password)
        
        if user["password_hash"] != hashed_password:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
        
        # Generate session token
        session_token = self.generate_session_token()
        
        # Store session
        self.sessions[session_token] = {
            "username": username,
            "user_id": user["user_id"],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        self.users[username] = user
        
        self.save_sessions()
        self.save_users()
        
        return {
            "success": True,
            "message": "Login successful",
            "session_token": session_token,
            "user": {
                "username": username,
                "user_id": user["user_id"],
                "created_at": user["created_at"],
                "last_login": user["last_login"]
            }
        }
    
    def get_user_by_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user by session token"""
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        # Check if session is expired
        if datetime.now() > expires_at:
            del self.sessions[session_token]
            self.save_sessions()
            return None
        
        username = session["username"]
        if username not in self.users:
            return None
        
        user = self.users[username].copy()
        user["session_token"] = session_token
        return user
    
    def update_user_credentials(self, session_token: str, service_account_data: Optional[Dict[str, Any]] = None, gemini_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Update user credentials"""
        user = self.get_user_by_token(session_token)
        if not user:
            return {
                "success": False,
                "message": "Invalid session token"
            }
        
        username = user["username"]
        
        if service_account_data is not None:
            self.users[username]["service_account_data"] = service_account_data
        
        if gemini_api_key is not None:
            self.users[username]["gemini_api_key"] = gemini_api_key
        
        self.save_users()
        
        return {
            "success": True,
            "message": "Credentials updated successfully"
        }
    
    def logout_user(self, session_token: str) -> Dict[str, Any]:
        """Logout user by removing session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            self.save_sessions()
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
