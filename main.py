#!/usr/bin/env python3
"""
Google Play Reviews CLI Application
Command-line interface for managing Google Play app reviews.
"""

import argparse
import sys
import os
from typing import List, Dict, Any

# Fix Windows encoding issues
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Import our custom modules
from auth import GooglePlayAuth
from reviews import GooglePlayReviews

# Try to import rich for better output formatting
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    # Disable rich on Windows to avoid encoding issues
    import sys
    if sys.platform.startswith('win'):
        RICH_AVAILABLE = False
        print("Rich disabled on Windows to avoid encoding issues.")
    else:
        RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not found. Install with 'pip install rich' for better output formatting.")

class GooglePlayReviewsCLI:
    """Main CLI application class."""
    
    def __init__(self):
        """Initialize the CLI application."""
        self.console = Console() if RICH_AVAILABLE else None
        self.auth = GooglePlayAuth()
        self.reviews_handler = None
        self.package_name = None
        
    def setup_package_name(self, package_name: str, enable_ai: bool = False):
        """
        Set up the package name and initialize reviews handler.
        
        Args:
            package_name (str): The package name of the app
            enable_ai (bool): Whether to enable AI response generation
        """
        self.package_name = package_name
        try:
            service = self.auth.get_service()
            self.reviews_handler = GooglePlayReviews(service, package_name, enable_ai)
        except Exception as e:
            self._print_error(f"Failed to initialize reviews handler: {e}")
            sys.exit(1)
    
    def _print_success(self, message: str):
        """Print success message with appropriate formatting."""
        if RICH_AVAILABLE:
            self.console.print(f"[green]✓[/green] {message}")
        else:
            print(f"[SUCCESS] {message}")
    
    def _print_error(self, message: str):
        """Print error message with appropriate formatting."""
        if RICH_AVAILABLE:
            self.console.print(f"[red]✗[/red] {message}")
        else:
            print(f"[ERROR] {message}")
    
    def _print_info(self, message: str):
        """Print info message with appropriate formatting."""
        if RICH_AVAILABLE:
            self.console.print(f"[blue]ℹ[/blue] {message}")
        else:
            print(f"[INFO] {message}")
    
    def _print_warning(self, message: str):
        """Print warning message with appropriate formatting."""
        if RICH_AVAILABLE:
            self.console.print(f"[yellow]⚠[/yellow] {message}")
        else:
            print(f"[WARNING] {message}")
    
    def list_reviews(self, max_results: int = 5):
        """
        List the latest reviews.
        
        Args:
            max_results (int): Maximum number of reviews to display
        """
        try:
            if not self.reviews_handler:
                self._print_error("Reviews handler not initialized. Please provide package name.")
                return
            
            self._print_info(f"Fetching latest {max_results} reviews for {self.package_name}...")
            
            reviews = self.reviews_handler.list_reviews(max_results)
            
            if not reviews:
                self._print_warning("No reviews found.")
                return
            
            if RICH_AVAILABLE:
                # Create a rich table for better formatting
                table = Table(title=f"Latest {len(reviews)} Reviews")
                table.add_column("Review ID", style="cyan", no_wrap=True)
                table.add_column("Rating", style="magenta", justify="center")
                table.add_column("Comment", style="white")
                
                for review in reviews:
                    rating_display = f"⭐ {review['rating']}" if review['rating'] != 'N/A' else "N/A"
                    comment = review['userComment'][:100] + "..." if len(review['userComment']) > 100 else review['userComment']
                    table.add_row(review['reviewId'], rating_display, comment)
                
                self.console.print(table)
            else:
                # Fallback to simple text output with detailed information
                print(f"\nLatest {len(reviews)} Reviews:")
                print("=" * 80)
                for i, review in enumerate(reviews, 1):
                    print(f"\n{i}. Review ID: {review['reviewId']}")
                    print(f"   Rating: {review['rating']} stars")
                    print(f"   Comment: {review['userComment']}")
                    print(f"   Language: {review['language']}")
                    print(f"   Device: {review['device']}")
                    print(f"   App Version: {review['appVersion']}")
                    print(f"   Android Version: {review['androidVersion']}")
                    print(f"   Thumbs Up: {review['thumbsUp']}")
                    if review['hasReply']:
                        print(f"   Developer Reply: {review['replyText']}")
                        print(f"   Reply Date: {review['replyDate']}")
                    else:
                        print(f"   Developer Reply: No reply yet")
                    print("-" * 80)
            
            self._print_success(f"Successfully displayed {len(reviews)} reviews")
            
        except Exception as e:
            self._print_error(f"Failed to list reviews: {e}")
    
    def reply_to_review(self, review_id: str, reply_text: str):
        """
        Reply to a specific review.
        
        Args:
            review_id (str): The ID of the review to reply to
            reply_text (str): The text of the reply
        """
        try:
            if not self.reviews_handler:
                self._print_error("Reviews handler not initialized. Please provide package name.")
                return
            
            self._print_info(f"Replying to review {review_id}...")
            
            success = self.reviews_handler.reply_to_review(review_id, reply_text)
            
            if success:
                self._print_success(f"Successfully replied to review {review_id}")
                if RICH_AVAILABLE:
                    panel = Panel(
                        f"[green]Reply sent:[/green]\n{reply_text}",
                        title="Review Reply",
                        border_style="green"
                    )
                    self.console.print(panel)
                else:
                    print(f"\nReply sent: {reply_text}")
            else:
                self._print_error(f"Failed to reply to review {review_id}")
                
        except Exception as e:
            self._print_error(f"Failed to reply to review: {e}")
    
    def auto_reply(self, max_results: int = 5, live: bool = False):
        """
        Automatically generate and post AI responses to reviews.
        
        Args:
            max_results (int): Maximum number of reviews to process
            live (bool): If True, actually post responses. Default is dry-run mode.
        """
        try:
            if not self.reviews_handler:
                self._print_error("Reviews handler not initialized. Please provide package name.")
                return
            
            if not self.reviews_handler.enable_ai:
                self._print_error("AI is not enabled. Use --enable-ai flag.")
                return
            
            # Determine if we should actually post
            actually_post = live
            
            self._print_info(f"Starting auto-reply process for {max_results} reviews...")
            if actually_post:
                self._print_warning("LIVE MODE - Responses will be posted to Play Store!")
                self._print_warning("This action cannot be undone!")
                print("\n" + "="*60)
                print("WARNING: Posting AI responses to real reviews!")
                print("="*60)
            else:
                self._print_warning("DRY RUN MODE - No replies will be posted (add --live to post)")
            
            results = self.reviews_handler.auto_reply_to_reviews(max_results, not actually_post)
            
            # Display results
            print(f"\nAuto-Reply Results:")
            print("=" * 50)
            print(f"Processed: {results['processed']}")
            print(f"Successful: {results['successful']}")
            print(f"Failed: {results['failed']}")
            print(f"Skipped: {results['skipped']}")
            
            if results['details']:
                print(f"\nDetails:")
                print("-" * 50)
                for detail in results['details']:
                    status = detail['status']
                    review_id = detail['review_id']
                    if status == 'success':
                        self._print_success(f"Review {review_id}: {detail.get('response', '')[:50]}...")
                    elif status == 'dry_run_success':
                        self._print_info(f"DRY RUN - Review {review_id}: {detail.get('response', '')[:50]}...")
                    elif status == 'skipped':
                        self._print_warning(f"Review {review_id}: Skipped ({detail.get('reason', 'unknown')})")
                    else:
                        self._print_error(f"Review {review_id}: Failed ({detail.get('reason', 'unknown')})")
            
            if results['successful'] > 0:
                self._print_success(f"Successfully processed {results['successful']} reviews")
            
        except Exception as e:
            self._print_error(f"Failed to auto-reply: {e}")
    
    def show_ai_stats(self):
        """Show AI response statistics."""
        try:
            if not self.reviews_handler:
                self._print_error("Reviews handler not initialized.")
                return
            
            stats = self.reviews_handler.get_ai_stats()
            
            if "error" in stats:
                self._print_error(f"AI stats error: {stats['error']}")
                return
            
            print(f"\nAI Response Statistics:")
            print("=" * 40)
            print(f"Total Replies: {stats.get('total_replies', 0)}")
            
            if stats.get('languages'):
                print(f"\nLanguages:")
                for lang, count in stats['languages'].items():
                    print(f"  {lang}: {count}")
            
            if stats.get('ratings'):
                print(f"\nBy Rating:")
                for rating, count in stats['ratings'].items():
                    print(f"  {rating} stars: {count}")
            
            if stats.get('average_length'):
                print(f"\nAverage Response Length: {stats['average_length']:.1f} characters")
            
        except Exception as e:
            self._print_error(f"Failed to get AI stats: {e}")
    
    def show_reply_history(self, limit: int = 10):
        """Show recent AI reply history."""
        try:
            if not self.reviews_handler:
                self._print_error("Reviews handler not initialized.")
                return
            
            history = self.reviews_handler.get_reply_history()
            
            if not history:
                self._print_warning("No reply history found.")
                return
            
            # Show most recent entries
            recent_history = history[-limit:] if len(history) > limit else history
            
            print(f"\nRecent AI Reply History (Last {len(recent_history)}):")
            print("=" * 80)
            
            for entry in reversed(recent_history):  # Show newest first
                print(f"\nReview ID: {entry['review_id']}")
                print(f"Rating: {entry['rating']} stars")
                print(f"Language: {entry['language']}")
                print(f"Original Review: {entry['review_text'][:100]}...")
                print(f"AI Response: {entry['final_response']}")
                print(f"Character Count: {entry['character_count']}")
                print(f"Timestamp: {entry['timestamp']}")
                print("-" * 80)
            
        except Exception as e:
            self._print_error(f"Failed to get reply history: {e}")
    
    def run(self):
        """Run the CLI application."""
        parser = argparse.ArgumentParser(
            description="Google Play Reviews CLI - Manage app reviews",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python main.py --package com.example.app list
  python main.py --package com.example.app reply REVIEW_ID "Thank you for your feedback!"
  python main.py --package com.example.app list --max-results 10
            """
        )
        
        parser.add_argument(
            '--package', '-p',
            required=True,
            help='Package name of the app (e.g., com.example.app)'
        )
        
        parser.add_argument(
            '--enable-ai',
            action='store_true',
            help='Enable AI response generation (requires GEMINI_API_KEY)'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List latest reviews')
        list_parser.add_argument(
            '--max-results', '-n',
            type=int,
            default=5,
            help='Maximum number of reviews to display (default: 5)'
        )
        
        # Reply command
        reply_parser = subparsers.add_parser('reply', help='Reply to a review')
        reply_parser.add_argument('review_id', help='ID of the review to reply to')
        reply_parser.add_argument('text', help='Reply text')
        
        # Auto-reply command
        auto_reply_parser = subparsers.add_parser('auto-reply', help='Automatically reply to reviews using AI')
        auto_reply_parser.add_argument(
            '--max-results', '-n',
            type=int,
            default=5,
            help='Maximum number of reviews to process (default: 5)'
        )
        auto_reply_parser.add_argument(
            '--live',
            action='store_true',
            help='Actually post responses to Play Store (use with caution!)'
        )
        
        # AI stats command
        stats_parser = subparsers.add_parser('ai-stats', help='Show AI response statistics')
        
        # History command
        history_parser = subparsers.add_parser('history', help='Show AI reply history')
        history_parser.add_argument(
            '--limit', '-l',
            type=int,
            default=10,
            help='Maximum number of history entries to show (default: 10)'
        )
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # Set up package name with AI support
        self.setup_package_name(args.package, args.enable_ai)
        
        # Execute the appropriate command
        if args.command == 'list':
            self.list_reviews(args.max_results)
        elif args.command == 'reply':
            self.reply_to_review(args.review_id, args.text)
        elif args.command == 'auto-reply':
            self.auto_reply(args.max_results, args.live)
        elif args.command == 'ai-stats':
            self.show_ai_stats()
        elif args.command == 'history':
            self.show_reply_history(args.limit)

def main():
    """Main entry point."""
    try:
        cli = GooglePlayReviewsCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
