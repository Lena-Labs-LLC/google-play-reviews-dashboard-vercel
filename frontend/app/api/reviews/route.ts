import { NextRequest, NextResponse } from 'next/server';

// Mock reviews data
const mockReviews = [
  {
    reviewId: "review_1",
    rating: 5,
    userComment: "Great app! Love the new features.",
    language: "en",
    device: "Pixel 7",
    appVersion: "2.1.0",
    androidVersion: "13",
    thumbsUp: 12,
    hasReply: false,
    replyText: ""
  },
  {
    reviewId: "review_2",
    rating: 4,
    userComment: "Good app but could use some improvements in the UI.",
    language: "en",
    device: "Samsung Galaxy S23",
    appVersion: "2.1.0",
    androidVersion: "13",
    thumbsUp: 8,
    hasReply: false,
    replyText: ""
  },
  {
    reviewId: "review_3",
    rating: 2,
    userComment: "App crashes frequently. Please fix!",
    language: "en",
    device: "OnePlus 11",
    appVersion: "2.0.9",
    androidVersion: "12",
    thumbsUp: 3,
    hasReply: true,
    replyText: "Thanks for the feedback. We're working on a fix."
  },
  {
    reviewId: "review_4",
    rating: 5,
    userComment: "Perfect! Exactly what I needed.",
    language: "en",
    device: "iPhone 14",
    appVersion: "2.1.0",
    androidVersion: "16",
    thumbsUp: 15,
    hasReply: false,
    replyText: ""
  },
  {
    reviewId: "review_5",
    rating: 3,
    userComment: "It's okay, but the loading times are too slow.",
    language: "en",
    device: "Xiaomi 13",
    appVersion: "2.1.0",
    androidVersion: "13",
    thumbsUp: 5,
    hasReply: false,
    replyText: ""
  }
];

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const maxResults = parseInt(searchParams.get('max_results') || '10');
    
    // Return mock reviews
    const reviews = mockReviews.slice(0, maxResults);
    
    return NextResponse.json({
      success: true,
      count: reviews.length,
      reviews: reviews
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, message: 'Failed to fetch reviews' },
      { status: 500 }
    );
  }
}
