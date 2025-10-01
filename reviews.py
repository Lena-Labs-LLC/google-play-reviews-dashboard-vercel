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
    """Handles Google Play app reviews operations with AI integration."""
    
    def __init__(self, service, package_name: str, enable_ai: bool = False):
        """
        Initialize the reviews handler.
        
        Args:
            service: Authenticated Google Play Developer API service
            package_name (str): The package name of the app (e.g., com.example.app)
            enable_ai (bool): Whether to enable AI response generation
        """
        self.service = service
        self.package_name = package_name
        self.enable_ai = enable_ai
        self.ai_generator = AIResponseGenerator() if enable_ai else None
        
    def list_reviews(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        List the latest reviews for the app.
        
        Args:
            max_results (int): Maximum number of reviews to return (default: 5)
            
        Returns:
            List[Dict[str, Any]]: List of review dictionaries
            
        Raises:
            HttpError: If API request fails
            Exception: If an unexpected error occurs
        """
        try:
            logger.info(f"Fetching latest {max_results} reviews for package: {self.package_name}")
            
            # Call the Google Play Developer API to get reviews
            reviews_response = self.service.reviews().list(
                packageName=self.package_name,
                maxResults=max_results
            ).execute()
            
            reviews = reviews_response.get('reviews', [])
            
            # Format the reviews for display with all available data
            formatted_reviews = []
            for review in reviews:
                review_id = review.get('reviewId', 'N/A')
                
                # Get user comment details
                user_comment = review.get('comments', [{}])[0].get('userComment', {})
                rating = user_comment.get('starRating', 'N/A')
                comment_text = user_comment.get('text', 'No comment')
                comment_date = user_comment.get('lastModified', {}).get('seconds', 'N/A')
                device = user_comment.get('device', 'N/A')
                app_version_code = user_comment.get('appVersionCode', 'N/A')
                android_version = user_comment.get('androidOsVersion', 'N/A')
                language = user_comment.get('reviewerLanguage', 'N/A')
                
                # Get developer reply details
                developer_comment = review.get('comments', [{}])[0].get('developerComment', {})
                has_reply = bool(developer_comment)
                reply_text = developer_comment.get('text', '') if has_reply else ''
                reply_date = developer_comment.get('lastModified', {}).get('seconds', 'N/A') if has_reply else 'N/A'
                
                # Get review metadata
                review_date = review.get('lastModified', {}).get('seconds', 'N/A')
                thumbs_up_count = user_comment.get('thumbsUpCount', 0)
                
                formatted_reviews.append({
                    'reviewId': review_id,
                    'rating': rating,
                    'userComment': comment_text,
                    'commentDate': comment_date,
                    'reviewDate': review_date,
                    'device': device,
                    'appVersion': app_version_code,
                    'androidVersion': android_version,
                    'language': language,
                    'thumbsUp': thumbs_up_count,
                    'hasReply': has_reply,
                    'replyText': reply_text,
                    'replyDate': reply_date
                })
            
            logger.info(f"Successfully fetched {len(formatted_reviews)} reviews")
            return formatted_reviews
            
        except HttpError as e:
            error_msg = f"API request failed: {e}"
            logger.error(error_msg)
            raise HttpError(e.resp, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error while fetching reviews: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def reply_to_review(self, review_id: str, reply_text: str) -> bool:
        """
        Reply to a specific review.
        
        Args:
            review_id (str): The ID of the review to reply to
            reply_text (str): The text of the reply
            
        Returns:
            bool: True if reply was successful, False otherwise
            
        Raises:
            HttpError: If API request fails
            Exception: If an unexpected error occurs
        """
        try:
            logger.info(f"Replying to review {review_id} with text: {reply_text[:50]}...")
            
            # Prepare the reply body
            reply_body = {
                'replyText': reply_text
            }
            
            # Call the Google Play Developer API to reply to the review
            self.service.reviews().reply(
                packageName=self.package_name,
                reviewId=review_id,
                body=reply_body
            ).execute()
            
            logger.info(f"Successfully replied to review {review_id}")
            return True
            
        except HttpError as e:
            error_msg = f"API request failed: {e}"
            logger.error(error_msg)
            raise HttpError(e.resp, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error while replying to review: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_review_details(self, review_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific review.
        
        Args:
            review_id (str): The ID of the review
            
        Returns:
            Optional[Dict[str, Any]]: Review details or None if not found
        """
        try:
            logger.info(f"Fetching details for review {review_id}")
            
            # Call the Google Play Developer API to get review details
            review_response = self.service.reviews().get(
                packageName=self.package_name,
                reviewId=review_id
            ).execute()
            
            return review_response
            
        except HttpError as e:
            logger.error(f"Failed to fetch review details: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while fetching review details: {e}")
            return None
    
    def auto_reply_to_reviews(self, max_results: int = 5, dry_run: bool = False) -> Dict[str, Any]:
        """
        Automatically generate and post AI responses to reviews.
        
        Args:
            max_results (int): Maximum number of reviews to process
            dry_run (bool): If True, generate responses but don't post them
            
        Returns:
            Dict[str, Any]: Results summary
        """
        if not self.enable_ai or not self.ai_generator:
            raise Exception("AI is not enabled. Initialize with enable_ai=True")
        
        try:
            logger.info(f"Starting auto-reply process for {max_results} reviews")
            
            # Get reviews
            reviews = self.list_reviews(max_results)
            if not reviews:
                logger.warning("No reviews found to process")
                return {"processed": 0, "successful": 0, "failed": 0, "skipped": 0}
            
            results = {
                "processed": 0,
                "successful": 0,
                "failed": 0,
                "skipped": 0,
                "details": []
            }
            
            for review in reviews:
                results["processed"] += 1
                review_id = review['reviewId']
                rating = review['rating']
                comment = review['userComment']
                has_reply = review['hasReply']
                
                # Skip if already has a reply
                if has_reply:
                    logger.info(f"Skipping review {review_id} - already has reply")
                    results["skipped"] += 1
                    results["details"].append({
                        "review_id": review_id,
                        "status": "skipped",
                        "reason": "already_has_reply"
                    })
                    continue
                
                # Skip if no comment text
                if not comment or comment.strip() == "":
                    logger.info(f"Skipping review {review_id} - no comment text")
                    results["skipped"] += 1
                    results["details"].append({
                        "review_id": review_id,
                        "status": "skipped",
                        "reason": "no_comment"
                    })
                    continue
                
                try:
                    # Generate AI response
                    logger.info(f"Generating AI response for review {review_id}")
                    ai_response = self.ai_generator.generate_response(comment, rating, review_id)
                    
                    if not ai_response:
                        logger.warning(f"Failed to generate AI response for review {review_id}")
                        results["failed"] += 1
                        results["details"].append({
                            "review_id": review_id,
                            "status": "failed",
                            "reason": "ai_generation_failed"
                        })
                        continue
                    
                    logger.info(f"Generated response: {ai_response[:50]}...")
                    
                    if dry_run:
                        logger.info(f"DRY RUN: Would reply to {review_id} with: {ai_response}")
                        results["successful"] += 1
                        results["details"].append({
                            "review_id": review_id,
                            "status": "dry_run_success",
                            "response": ai_response
                        })
                    else:
                        # Post the reply
                        success = self.reply_to_review(review_id, ai_response)
                        if success:
                            logger.info(f"Successfully posted reply to review {review_id}")
                            results["successful"] += 1
                            results["details"].append({
                                "review_id": review_id,
                                "status": "success",
                                "response": ai_response
                            })
                        else:
                            logger.error(f"Failed to post reply to review {review_id}")
                            results["failed"] += 1
                            results["details"].append({
                                "review_id": review_id,
                                "status": "failed",
                                "reason": "api_post_failed",
                                "response": ai_response
                            })
                
                except Exception as e:
                    logger.error(f"Error processing review {review_id}: {e}")
                    results["failed"] += 1
                    results["details"].append({
                        "review_id": review_id,
                        "status": "failed",
                        "reason": str(e)
                    })
            
            logger.info(f"Auto-reply process completed. Processed: {results['processed']}, "
                       f"Successful: {results['successful']}, Failed: {results['failed']}, "
                       f"Skipped: {results['skipped']}")
            
            return results
            
        except Exception as e:
            error_msg = f"Unexpected error during auto-reply process: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """Get AI response statistics."""
        if not self.ai_generator:
            return {"error": "AI not enabled"}
        
        return self.ai_generator.get_stats()
    
    def get_reply_history(self) -> List[Dict[str, Any]]:
        """Get AI reply history."""
        if not self.ai_generator:
            return []
        
        return self.ai_generator.get_reply_history()
