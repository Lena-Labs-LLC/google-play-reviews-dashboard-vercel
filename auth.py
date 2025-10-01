"""
Authentication module for Google Play Developer API.
Handles service account authentication and API client setup.
"""

import os
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GooglePlayAuth:
    """Handles authentication for Google Play Developer API."""
    
    def __init__(self, service_account_data=None):
        """
        Initialize the authentication client.
        
        Args:
            service_account_data (dict): Service account JSON data as dictionary
        """
        self.service_account_data = service_account_data
        self.service = None
        
    def authenticate(self):
        """
        Authenticate with Google Play Developer API.
        
        Returns:
            googleapiclient.discovery.Resource: Authenticated API service object
            
        Raises:
            ValueError: If service account data is not provided
            Exception: If authentication fails
        """
        try:
            # Check if service account data is provided
            if not self.service_account_data:
                raise ValueError(
                    "Service account data not provided. "
                    "Please provide service account JSON data."
                )
            
            # Define the scopes required for Google Play Developer API
            scopes = [
                'https://www.googleapis.com/auth/androidpublisher'
            ]
            
            # Load credentials from service account data
            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_data, 
                scopes=scopes
            )
            
            # Build the Google Play Developer API service
            self.service = build('androidpublisher', 'v3', credentials=credentials)
            
            logger.info("Successfully authenticated with Google Play Developer API")
            return self.service
            
        except ValueError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def get_service(self):
        """
        Get the authenticated API service.
        
        Returns:
            googleapiclient.discovery.Resource: Authenticated API service object
        """
        if self.service is None:
            self.authenticate()
        return self.service

