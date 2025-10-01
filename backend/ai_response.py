"""
AI Response module for Google Play Reviews CLI.
Handles AI-generated responses to app reviews using OpenAI GPT.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIResponseGenerator:
    """Handles AI-generated responses to app reviews using Google's Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI response generator.
        
        Args:
            api_key (str, optional): Google Gemini API key. If not provided, 
                                   will try to get from environment variable.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.reply_history = []
        
        if not self.api_key:
            logger.warning("No Gemini API key provided. AI features will be disabled.")
            return
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
        
        logger.info("AI Response Generator initialized successfully")
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection based on common patterns.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Detected language code
        """
        # Simple heuristic-based language detection
        turkish_indicators = ['ç', 'ğ', 'ı', 'ö', 'ş', 'ü', 'Ç', 'Ğ', 'İ', 'Ö', 'Ş', 'Ü']
        
        if any(char in text for char in turkish_indicators):
            return 'tr'
        
        # Check for common English words
        english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
        words = text.lower().split()
        
        if any(word in words for word in english_words):
            return 'en'
        
        # Default to English if uncertain
        return 'en'
    
    def generate_response(self, review_text: str, rating: int, review_id: str) -> Optional[str]:
        """
        Generate an AI response for a review.
        
        Args:
            review_text (str): The review text
            rating (int): Star rating (1-5)
            review_id (str): Unique review ID
            
        Returns:
            Optional[str]: Generated response text, or None if generation failed
        """
        if not self.api_key:
            logger.error("No API key available for AI generation")
            return None
        
        try:
            # Detect language
            language = self.detect_language(review_text)
            
            # Create context-aware prompt
            if language == 'tr':
                prompt = self._create_turkish_prompt(review_text, rating)
            else:
                prompt = self._create_english_prompt(review_text, rating)
            
            logger.info(f"Generating AI response for review {review_id} (rating: {rating}, language: {language})")
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                ai_response = response.text.strip()
                
                # Record in history
                self.reply_history.append({
                    'review_id': review_id,
                    'review_text': review_text,
                    'rating': rating,
                    'language': language,
                    'response': ai_response,
                    'timestamp': self.get_current_timestamp()
                })
                
                logger.info(f"Successfully generated AI response: {ai_response[:50]}...")
                return ai_response
            else:
                logger.error("Failed to generate response from Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None
    
    def _create_english_prompt(self, review_text: str, rating: int) -> str:
        """Create a prompt for English reviews."""
        if rating >= 4:
            sentiment = "positive"
            tone = "grateful and encouraging"
        elif rating == 3:
            sentiment = "neutral"
            tone = "understanding and helpful"
        else:
            sentiment = "negative"
            tone = "apologetic and solution-focused"
        
        prompt = f"""
You are a professional customer support representative for a mobile app. 
A user left a {sentiment} review with {rating} stars:

Review: "{review_text}"

Please write a professional, helpful response that is:
- {tone}
- Under 200 characters
- Professional but friendly
- Addresses any concerns mentioned
- Encourages continued use of the app

Response:"""
        
        return prompt
    
    def _create_turkish_prompt(self, review_text: str, rating: int) -> str:
        """Create a prompt for Turkish reviews."""
        if rating >= 4:
            sentiment = "olumlu"
            tone = "minnettar ve teşvik edici"
        elif rating == 3:
            sentiment = "nötr"
            tone = "anlayışlı ve yardımcı"
        else:
            sentiment = "olumsuz"
            tone = "özür dileyici ve çözüm odaklı"
        
        prompt = f"""
Sen bir mobil uygulama için profesyonel müşteri hizmetleri temsilcisisin.
Bir kullanıcı {rating} yıldızla {sentiment} bir yorum bırakmış:

Yorum: "{review_text}"

Lütfen şu özelliklere sahip profesyonel ve yardımcı bir yanıt yaz:
- {tone}
- 200 karakterden az
- Profesyonel ama samimi
- Belirtilen endişeleri ele alan
- Uygulamanın kullanımını teşvik eden

Yanıt:"""
        
        return prompt
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get AI response statistics.
        
        Returns:
            Dict[str, Any]: Statistics about AI responses
        """
        if not self.reply_history:
            return {
                'total_responses': 0,
                'language_breakdown': {},
                'rating_breakdown': {},
                'last_response': None
            }
        
        # Calculate statistics
        total_responses = len(self.reply_history)
        
        # Language breakdown
        language_breakdown = {}
        for entry in self.reply_history:
            lang = entry.get('language', 'unknown')
            language_breakdown[lang] = language_breakdown.get(lang, 0) + 1
        
        # Rating breakdown
        rating_breakdown = {}
        for entry in self.reply_history:
            rating = entry.get('rating', 0)
            rating_breakdown[str(rating)] = rating_breakdown.get(str(rating), 0) + 1
        
        # Last response
        last_response = self.reply_history[-1] if self.reply_history else None
        
        return {
            'total_responses': total_responses,
            'language_breakdown': language_breakdown,
            'rating_breakdown': rating_breakdown,
            'last_response': last_response,
            'api_configured': bool(self.api_key)
        }
    
    def get_reply_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of AI-generated replies.
        
        Returns:
            List[Dict[str, Any]]: List of reply history entries
        """
        return self.reply_history.copy()
    
    def save_history(self, filename: str = "ai_reply_history.json"):
        """
        Save reply history to a file.
        
        Args:
            filename (str): Name of the file to save to
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.reply_history, f, indent=2, ensure_ascii=False)
            logger.info(f"Reply history saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save reply history: {e}")
    
    def load_history(self, filename: str = "ai_reply_history.json"):
        """
        Load reply history from a file.
        
        Args:
            filename (str): Name of the file to load from
        """
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.reply_history = json.load(f)
                logger.info(f"Reply history loaded from {filename}")
            else:
                logger.info(f"No history file found at {filename}")
        except Exception as e:
            logger.error(f"Failed to load reply history: {e}")
            self.reply_history = []
