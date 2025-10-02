import { NextRequest, NextResponse } from 'next/server';
import { google } from 'googleapis';

// Force dynamic rendering for this API route
export const dynamic = 'force-dynamic';

// Import global configuration
let globalAuth: any = null;
let globalPackageName: string | null = null;

// This is a workaround since we can't directly import from other API routes
// In a real app, you'd use a database or external state management
const getGlobalConfig = () => {
  // For now, we'll use a simple in-memory store
  // In production, use Redis, database, or environment variables
  return {
    auth: globalAuth,
    packageName: globalPackageName
  };
};

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const maxResults = parseInt(searchParams.get('max_results') || '10');

    // For now, return mock data since Google Play API setup is complex
    // In production, you'd use the actual Google Play API
    const mockReviews = [
      {
        reviewId: "gp:AOqpTOGVoKU8_VqbF_2H1234567890",
        rating: 5,
        userComment: "Harika bir uygulama! Yeni özellikler çok güzel.",
        language: "tr",
        device: "Pixel 7",
        appVersion: "2.1.0",
        androidVersion: "13",
        thumbsUp: 12,
        hasReply: false,
        replyText: "",
        submittedAt: new Date().toISOString()
      },
      {
        reviewId: "gp:AOqpTOGVoKU8_VqbF_2H1234567891",
        rating: 4,
        userComment: "İyi bir uygulama ama arayüzde iyileştirmeler yapılabilir.",
        language: "tr",
        device: "Samsung Galaxy S23",
        appVersion: "2.1.0",
        androidVersion: "13",
        thumbsUp: 8,
        hasReply: false,
        replyText: "",
        submittedAt: new Date().toISOString()
      },
      {
        reviewId: "gp:AOqpTOGVoKU8_VqbF_2H1234567892",
        rating: 2,
        userComment: "Uygulama sık sık çöküyor. Lütfen düzeltin!",
        language: "tr",
        device: "OnePlus 11",
        appVersion: "2.0.9",
        androidVersion: "12",
        thumbsUp: 3,
        hasReply: true,
        replyText: "Geri bildiriminiz için teşekkürler. Sorunu çözmek için çalışıyoruz.",
        submittedAt: new Date().toISOString()
      },
      {
        reviewId: "gp:AOqpTOGVoKU8_VqbF_2H1234567893",
        rating: 5,
        userComment: "Perfect! Exactly what I needed. Great job!",
        language: "en",
        device: "iPhone 14",
        appVersion: "2.1.0",
        androidVersion: "16",
        thumbsUp: 15,
        hasReply: false,
        replyText: "",
        submittedAt: new Date().toISOString()
      },
      {
        reviewId: "gp:AOqpTOGVoKU8_VqbF_2H1234567894",
        rating: 3,
        userComment: "Fena değil ama yükleme süreleri çok uzun.",
        language: "tr",
        device: "Xiaomi 13",
        appVersion: "2.1.0",
        androidVersion: "13",
        thumbsUp: 5,
        hasReply: false,
        replyText: "",
        submittedAt: new Date().toISOString()
      }
    ];

    // Return the requested number of reviews
    const reviews = mockReviews.slice(0, maxResults);

    return NextResponse.json({
      success: true,
      count: reviews.length,
      reviews: reviews
    });

  } catch (error) {
    console.error('Failed to fetch reviews:', error);
    return NextResponse.json(
      { success: false, message: 'Failed to fetch reviews' },
      { status: 500 }
    );
  }
}

// TODO: Implement real Google Play API integration
/*
async function fetchRealReviews(auth: any, packageName: string, maxResults: number) {
  const androidpublisher = google.androidpublisher('v3');
  
  const authClient = await auth.getClient();
  
  const response = await androidpublisher.reviews.list({
    auth: authClient,
    packageName: packageName,
    maxResults: maxResults
  });
  
  return response.data.reviews || [];
}
*/
