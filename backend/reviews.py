"""
Reviews module for Google Play Developer API.
Handles listing and replying to app reviews with AI integration.
"""

from googleapiclient.errors import HttpError
import logging
from typing import List, Dict, Any, Optional
from ai_response import AIResponseGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GooglePlayReviews:
    """Handles Google Play app reviews and AI-powered responses."""
    
    def __init__(self, service, package_name: str, enable_ai: bool = False, ai_generator: Optional[AIResponseGenerator] = None):
        """
        Initialize the reviews handler.
        
        Args:
            service: Authenticated Google Play Developer API service
            package_name (str): Android app package name
            enable_ai (bool): Whether to enable AI-powered responses
            ai_generator: AI response generator instance
        """
        self.service = service
        self.package_name = package_name
        self.enable_ai = enable_ai
        self.ai_generator = ai_generator
        self.reply_history = []
        
    def list_reviews(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List app reviews from Google Play.
        
        Args:
            max_results (int): Maximum number of reviews to return
            
        Returns:
            List[Dict[str, Any]]: List of review data
        """
        try:
            # Get reviews from Google Play Developer API
            reviews_request = self.service.reviews().list(
                packageName=self.package_name,
                maxResults=max_results
            )
            reviews_response = reviews_request.execute()
            
            reviews = []
            for review_data in reviews_response.get('reviews', []):
                review_info = review_data.get('reviewId', '')
                review_details = review_data.get('comments', [{}])[0]
                
                # Extract review information
                review = {
                    'reviewId': review_info,
                    'rating': review_data.get('starRating', 0),
                    'userComment': review_details.get('text', ''),
                    'language': review_details.get('reviewerLanguage', 'en'),
                    'device': review_details.get('deviceMetadata', {}).get('deviceModel', 'Unknown'),
                    'appVersion': review_details.get('appVersionCode', 0),
                    'androidVersion': review_details.get('deviceMetadata', {}).get('androidOsVersion', 'Unknown'),
                    'thumbsUp': review_data.get('thumbsUpCount', 0),
                    'hasReply': bool(review_data.get('comments', [{}])[0].get('developerComment')),
                    'replyText': review_data.get('comments', [{}])[0].get('developerComment', {}).get('text', '')
                }
                reviews.append(review)
            
            logger.info(f"Retrieved {len(reviews)} reviews for package {self.package_name}")
            return reviews
            
        except HttpError as e:
            logger.error(f"Failed to list reviews: {e}")
            raise Exception(f"Failed to fetch reviews: {e}")
    
    def reply_to_review(self, review_id: str, reply_text: str) -> bool:
        """
        Reply to a specific review.
        
        Args:
            review_id (str): ID of the review to reply to
            reply_text (str): Text of the reply
            
        Returns:
            bool: True if reply was successful, False otherwise
        """
        try:
            # Reply to the review
            reply_request = self.service.reviews().reply(
                packageName=self.package_name,
                reviewId=review_id,
                body={
                    'replyText': reply_text
                }
            )
            reply_request.execute()
            
            logger.info(f"Successfully replied to review {review_id}")
            
            # Record in history if AI is enabled
            if self.enable_ai:
                self.reply_history.append({
                    'review_id': review_id,
                    'reply_text': reply_text,
                    'timestamp': self.ai_generator.get_current_timestamp() if self.ai_generator else None,
                    'ai_generated': True
                })
            
            return True
            
        except HttpError as e:
            logger.error(f"Failed to reply to review {review_id}: {e}")
            return False
    
    def auto_reply_to_reviews(self, max_results: int = 5, dry_run: bool = True) -> List[Dict[str, Any]]:
        """
        Automatically reply to reviews using AI.
        
        Args:
            max_results (int): Maximum number of reviews to process
            dry_run (bool): If True, only preview responses without posting
            
        Returns:
            List[Dict[str, Any]]: Results of auto-reply process
        """
        if not self.enable_ai or not self.ai_generator:
            raise Exception("AI is not enabled or AI generator is not available")
        
        try:
            # Get reviews
            reviews = self.list_reviews(max_results)
            results = []
            
            for review in reviews:
                # Skip if already has a reply
                if review['hasReply']:
                    results.append({
                        'review_id': review['reviewId'],
                        'status': 'skipped',
                        'reason': 'Already has a reply'
                    })
                    continue
                
                # Skip if rating is 5 (positive review)
                if review['rating'] >= 5:
                    results.append({
                        'review_id': review['reviewId'],
                        'status': 'skipped',
                        'reason': 'Positive review (5 stars)'
                    })
                    continue
                
                try:
                    # Generate AI response
                    ai_response = self.ai_generator.generate_response(
                        review['userComment'],
                        review['rating'],
                        review['reviewId']
                    )
                    
                    if ai_response:
                        if not dry_run:
                            # Post the reply
                            success = self.reply_to_review(review['reviewId'], ai_response)
                            status = 'posted' if success else 'failed'
                        else:
                            status = 'preview'
                        
                        results.append({
                            'review_id': review['reviewId'],
                            'rating': review['rating'],
                            'review_text': review['userComment'],
                            'ai_response': ai_response,
                            'status': status
                        })
                    else:
                        results.append({
                            'review_id': review['reviewId'],
                            'status': 'failed',
                            'reason': 'Failed to generate AI response'
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing review {review['reviewId']}: {e}")
                    results.append({
                        'review_id': review['reviewId'],
                        'status': 'error',
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Auto-reply failed: {e}")
            raise
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """
        Get AI response statistics.
        
        Returns:
            Dict[str, Any]: AI response statistics
        """
        if not self.enable_ai:
            return {'ai_enabled': False}
        
        return {
            'ai_enabled': True,
            'total_replies': len(self.reply_history),
            'recent_replies': len([r for r in self.reply_history if r.get('timestamp')])
        }
    
    def get_reply_history(self) -> List[Dict[str, Any]]:
        """
        Get AI reply history.
        
        Returns:
            List[Dict[str, Any]]: Reply history
        """
        return self.reply_history.copy()
