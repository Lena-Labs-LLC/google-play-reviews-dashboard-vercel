"""
AI Response module for Google Play Reviews CLI.
Handles AI-generated responses to app reviews using OpenAI GPT.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIResponseGenerator:
    """Handles AI-generated responses to app reviews."""
    
    def __init__(self, knowledge_base_path: str = "knowledge_base.json", 
                 history_path: str = "reply_history.json"):
        """
        Initialize the AI response generator.
        
        Args:
            knowledge_base_path (str): Path to the knowledge base JSON file
            history_path (str): Path to store reply history
        """
        self.knowledge_base_path = knowledge_base_path
        self.history_path = history_path
        self.knowledge_base = self._load_knowledge_base()
        self.reply_history = self._load_reply_history()
        
        # Initialize Gemini client
        self.gemini_client = self._init_gemini_client()
        
        # Response rules based on rating
        self.response_rules = {
            1: "apologize_and_support",
            2: "apologize_and_support", 
            3: "neutral_improvement",
            4: "thank_and_engage",
            5: "thank_and_engage"
        }
        
        # Forbidden words/phrases to avoid
        self.forbidden_words = [
            "sorry", "apologize", "unfortunately", "regret", "disappointed",
            "terrible", "awful", "hate", "worst", "useless", "broken"
        ]
    
    def _init_gemini_client(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            # Check if API key is set
            if not os.getenv('GEMINI_API_KEY'):
                logger.warning("GEMINI_API_KEY not found. Set it as environment variable.")
                return None
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            return genai.GenerativeModel('gemini-2.0-flash-exp')
        except ImportError:
            logger.error("Google Generative AI library not installed. Install with: pip install google-generativeai")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            return None
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load the app knowledge base from JSON file."""
        try:
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default knowledge base
                default_kb = {
                    "app_name": "Your App",
                    "description": "A great mobile application",
                    "features": [
                        "Feature 1: Description",
                        "Feature 2: Description",
                        "Feature 3: Description"
                    ],
                    "faqs": [
                        {
                            "question": "How do I use this app?",
                            "answer": "Simply download and follow the on-screen instructions."
                        },
                        {
                            "question": "Is this app free?",
                            "answer": "Yes, our app is completely free to use."
                        }
                    ],
                    "target_users": "General mobile users",
                    "support_contact": "support@yourapp.com"
                }
                self._save_knowledge_base(default_kb)
                return default_kb
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            return {}
    
    def _save_knowledge_base(self, kb: Dict[str, Any]):
        """Save knowledge base to file."""
        try:
            with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
                json.dump(kb, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {e}")
    
    def _load_reply_history(self) -> List[Dict[str, Any]]:
        """Load reply history from file."""
        try:
            if os.path.exists(self.history_path):
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Failed to load reply history: {e}")
            return []
    
    def _save_reply_history(self):
        """Save reply history to file."""
        try:
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self.reply_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save reply history: {e}")
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the review text.
        
        Args:
            text (str): Review text
            
        Returns:
            str: Detected language code
        """
        # Simple language detection based on common patterns
        text_lower = text.lower()
        
        # Turkish patterns
        if any(word in text_lower for word in ['çok', 'güzel', 'harika', 'teşekkür', 'sağol', 'iyi', 'kötü']):
            return 'tr'
        
        # Spanish patterns
        if any(word in text_lower for word in ['muy', 'bueno', 'excelente', 'gracias', 'malo', 'buena']):
            return 'es'
        
        # French patterns
        if any(word in text_lower for word in ['très', 'bon', 'excellent', 'merci', 'mauvais', 'bien']):
            return 'fr'
        
        # German patterns
        if any(word in text_lower for word in ['sehr', 'gut', 'ausgezeichnet', 'danke', 'schlecht', 'toll']):
            return 'de'
        
        # Russian patterns
        if any(word in text_lower for word in ['очень', 'хорошо', 'отлично', 'спасибо', 'плохо', 'классно']):
            return 'ru'
        
        # Indonesian patterns
        if any(word in text_lower for word in ['sangat', 'bagus', 'bagus', 'terima', 'kasih', 'buruk']):
            return 'id'
        
        # Persian patterns
        if any(word in text_lower for word in ['خیلی', 'خوب', 'عالی', 'ممنون', 'بد', 'عالی']):
            return 'fa'
        
        # Default to English
        return 'en'
    
    def generate_response(self, review_text: str, rating: int, review_id: str) -> Optional[str]:
        """
        Generate AI response for a review.
        
        Args:
            review_text (str): The review text
            rating (int): Star rating (1-5)
            review_id (str): Review ID for tracking
            
        Returns:
            Optional[str]: Generated response or None if failed
        """
        if not self.gemini_client:
            logger.error("Gemini client not available")
            return None
        
        try:
            # Detect language
            language = self.detect_language(review_text)
            
            # Get response rule based on rating
            rule = self.response_rules.get(rating, "neutral_improvement")
            
            # Build prompt
            prompt = self._build_prompt(review_text, rating, language, rule)
            
            # Generate response using Gemini
            response = self.gemini_client.generate_content(
                f"You are a professional app developer responding to user reviews. Be helpful, friendly, and concise.\n\n{prompt}",
                generation_config={
                    "max_output_tokens": 100,
                    "temperature": 0.7,
                }
            )
            
            ai_response = response.text.strip()
            
            # Validate and filter response
            validated_response = self._validate_response(ai_response, language)
            
            if validated_response:
                # Log to history
                self._log_reply(review_id, review_text, rating, ai_response, validated_response, language)
                return validated_response
            else:
                logger.warning(f"Generated response failed validation for review {review_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return None
    
    def _build_prompt(self, review_text: str, rating: int, language: str, rule: str) -> str:
        """Build the prompt for AI generation."""
        
        # Language-specific instructions
        language_instructions = {
            'tr': "Respond in Turkish. Be polite and professional.",
            'es': "Respond in Spanish. Be polite and professional.", 
            'fr': "Respond in French. Be polite and professional.",
            'de': "Respond in German. Be polite and professional.",
            'ru': "Respond in Russian. Be polite and professional.",
            'id': "Respond in Indonesian. Be polite and professional.",
            'fa': "Respond in Persian. Be polite and professional.",
            'en': "Respond in English. Be polite and professional."
        }
        
        # Rule-specific instructions
        rule_instructions = {
            'apologize_and_support': f"For low ratings (1-2 stars): Apologize sincerely, offer direct support, and ask for specific feedback. Mention our support contact: {self.knowledge_base.get('support_contact', 'support@yourapp.com')}",
            'neutral_improvement': "For medium ratings (3 stars): Acknowledge the feedback neutrally, promise improvements, and encourage continued use.",
            'thank_and_engage': "For high ratings (4-5 stars): Thank enthusiastically, encourage sharing, and invite them to explore more features."
        }
        
        # Build knowledge base context
        kb_context = f"""
App Information:
- Name: {self.knowledge_base.get('app_name', 'Your App')}
- Description: {self.knowledge_base.get('description', 'A great mobile application')}
- Key Features: {', '.join(self.knowledge_base.get('features', []))}
- Target Users: {self.knowledge_base.get('target_users', 'General mobile users')}

FAQ Answers:
{self._format_faqs()}
"""
        
        prompt = f"""
{language_instructions.get(language, language_instructions['en'])}

{rule_instructions[rule]}

{kb_context}

Review Details:
- Rating: {rating}/5 stars
- Review Text: "{review_text}"

Requirements:
- Maximum 350 characters
- Professional but friendly tone
- Use relevant app features if applicable
- Address specific concerns mentioned in the review
- Don't be robotic or generic

Generate a response:
"""
        return prompt
    
    def _format_faqs(self) -> str:
        """Format FAQs for the prompt."""
        faqs = self.knowledge_base.get('faqs', [])
        if not faqs:
            return "No FAQs available."
        
        formatted = []
        for faq in faqs[:5]:  # Limit to 5 most relevant FAQs
            formatted.append(f"Q: {faq['question']}\nA: {faq['answer']}")
        
        return "\n\n".join(formatted)
    
    def _validate_response(self, response: str, language: str) -> Optional[str]:
        """
        Validate and filter the AI response.
        
        Args:
            response (str): Generated response
            language (str): Detected language
            
        Returns:
            Optional[str]: Validated response or None if invalid
        """
        if not response:
            return None
        
        # Check length
        if len(response) > 350:
            response = response[:347] + "..."
        
        # Check for forbidden words (case insensitive)
        response_lower = response.lower()
        for word in self.forbidden_words:
            if word in response_lower:
                logger.warning(f"Response contains forbidden word: {word}")
                return None
        
        # Basic content validation
        if len(response.strip()) < 10:
            logger.warning("Response too short")
            return None
        
        # Check for appropriate language
        if language != 'en':
            # Simple check if response contains expected language characters
            if language == 'tr' and not any(char in response for char in 'çğıöşüÇĞIİÖŞÜ'):
                logger.warning("Response may not be in Turkish")
            elif language == 'ru' and not any(char in response for char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'):
                logger.warning("Response may not be in Russian")
        
        return response.strip()
    
    def _log_reply(self, review_id: str, review_text: str, rating: int, 
                   original_response: str, final_response: str, language: str):
        """Log the reply to history."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "review_id": review_id,
            "review_text": review_text,
            "rating": rating,
            "language": language,
            "original_ai_response": original_response,
            "final_response": final_response,
            "character_count": len(final_response)
        }
        
        self.reply_history.append(log_entry)
        self._save_reply_history()
        
        logger.info(f"Logged reply for review {review_id}")
    
    def get_reply_history(self) -> List[Dict[str, Any]]:
        """Get the reply history."""
        return self.reply_history
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about generated replies."""
        if not self.reply_history:
            return {"total_replies": 0}
        
        total_replies = len(self.reply_history)
        languages = {}
        ratings = {}
        
        for entry in self.reply_history:
            lang = entry.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1
            
            rating = entry.get('rating', 0)
            ratings[rating] = ratings.get(rating, 0) + 1
        
        return {
            "total_replies": total_replies,
            "languages": languages,
            "ratings": ratings,
            "average_length": sum(entry.get('character_count', 0) for entry in self.reply_history) / total_replies
        }
