#!/usr/bin/env python3
"""
Test script for AI responses without posting to Play Store.
This script allows you to test AI responses locally before using them in production.
"""

import os
import sys

# Fix Windows encoding issues
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

from ai_response import AIResponseGenerator

def test_ai_responses():
    """Test AI responses with sample reviews."""
    
    print("AI Response Test Script")
    print("=" * 50)
    
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("ERROR: GEMINI_API_KEY not found!")
        print("Please set your Gemini API key:")
        print("Windows: set GEMINI_API_KEY=your_key_here")
        print("Linux/Mac: export GEMINI_API_KEY=your_key_here")
        return
    
    # Initialize AI generator
    try:
        ai_generator = AIResponseGenerator()
        print("SUCCESS: AI Generator initialized successfully")
    except Exception as e:
        print(f"ERROR: Failed to initialize AI generator: {e}")
        return
    
    # Sample reviews for testing
    test_reviews = [
        {
            "review_id": "test_1",
            "rating": 5,
            "comment": "Harika bir uygulama! Çok beğendim 👍",
            "language": "tr"
        },
        {
            "review_id": "test_2", 
            "rating": 1,
            "comment": "Uygulama sürekli çöküyor, hiç çalışmıyor",
            "language": "tr"
        },
        {
            "review_id": "test_3",
            "rating": 3,
            "comment": "Orta seviyede, bazı özellikler eksik",
            "language": "tr"
        },
        {
            "review_id": "test_4",
            "rating": 5,
            "comment": "Excellent app! Love the features",
            "language": "en"
        },
        {
            "review_id": "test_5",
            "rating": 2,
            "comment": "App crashes frequently, needs fixing",
            "language": "en"
        },
        {
            "review_id": "test_6",
            "rating": 4,
            "comment": "Good app but could be better",
            "language": "en"
        },
        {
            "review_id": "test_7",
            "rating": 5,
            "comment": "Отличное приложение! Рекомендую",
            "language": "ru"
        },
        {
            "review_id": "test_8",
            "rating": 1,
            "comment": "Приложение не работает, деньги потрачены зря",
            "language": "ru"
        }
    ]
    
    print(f"\nTesting {len(test_reviews)} sample reviews...")
    print("=" * 50)
    
    for i, review in enumerate(test_reviews, 1):
        print(f"\nTest {i}:")
        print(f"   Review ID: {review['review_id']}")
        print(f"   Rating: {review['rating']} stars")
        print(f"   Language: {review['language']}")
        print(f"   Comment: {review['comment']}")
        
        try:
            # Generate AI response
            ai_response = ai_generator.generate_response(
                review['comment'], 
                review['rating'], 
                review['review_id']
            )
            
            if ai_response:
                print(f"   AI Response: {ai_response}")
                print(f"   Length: {len(ai_response)} characters")
                
                # Check if response is appropriate
                if len(ai_response) > 350:
                    print("   WARNING: Response too long!")
                elif len(ai_response) < 10:
                    print("   WARNING: Response too short!")
                else:
                    print("   SUCCESS: Response length OK")
            else:
                print("   ERROR: Failed to generate response")
                
        except Exception as e:
            print(f"   ERROR: {e}")
        
        print("-" * 50)
    
    # Show statistics
    print(f"\nTest Statistics:")
    stats = ai_generator.get_stats()
    print(f"   Total responses generated: {stats.get('total_replies', 0)}")
    
    if stats.get('languages'):
        print(f"   Languages tested: {', '.join(stats['languages'].keys())}")
    
    if stats.get('ratings'):
        print(f"   Ratings tested: {', '.join(map(str, stats['ratings'].keys()))}")
    
    print(f"\nSUCCESS: Test completed! Check the responses above.")
    print("TIP: If responses look good, you can use --dry-run mode in the main CLI")

def test_specific_review():
    """Test AI response for a specific review."""
    
    print("\nTest Specific Review")
    print("=" * 30)
    
    # Get user input
    comment = input("Enter review comment: ").strip()
    if not comment:
        print("ERROR: No comment provided")
        return
    
    try:
        rating = int(input("Enter rating (1-5): "))
        if rating < 1 or rating > 5:
            print("ERROR: Invalid rating")
            return
    except ValueError:
        print("ERROR: Invalid rating")
        return
    
    # Initialize AI generator
    try:
        ai_generator = AIResponseGenerator()
    except Exception as e:
        print(f"ERROR: Failed to initialize AI generator: {e}")
        return
    
    # Generate response
    print(f"\nGenerating response...")
    ai_response = ai_generator.generate_response(comment, rating, "test_custom")
    
    if ai_response:
        print(f"\nSUCCESS: AI Response:")
        print(f"   {ai_response}")
        print(f"\nLength: {len(ai_response)} characters")
        print(f"Detected Language: {ai_generator.detect_language(comment)}")
    else:
        print("ERROR: Failed to generate response")

def main():
    """Main function."""
    print("AI Response Testing Tool")
    print("This tool helps you test AI responses safely before using them in production.")
    print()
    
    # Automatically run sample tests
    print("Running automatic sample tests...")
    test_ai_responses()
    
    print("\n" + "="*60)
    print("Test completed! Check the responses above.")
    print("If responses look good, you can use --dry-run mode in the main CLI")
    print("="*60)

if __name__ == "__main__":
    main()
