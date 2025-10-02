import { NextRequest, NextResponse } from 'next/server';

// Mock AI responses based on rating
const generateMockResponse = (rating: number, reviewText: string) => {
  if (rating >= 4) {
    return "Thank you so much for your positive feedback! We're thrilled that you're enjoying the app. Your support means a lot to our team and motivates us to keep improving.";
  } else if (rating === 3) {
    return "Thank you for your feedback! We appreciate you taking the time to share your thoughts. We're constantly working to improve the app experience and will consider your suggestions.";
  } else {
    return "Thank you for bringing this to our attention. We sincerely apologize for any inconvenience you've experienced. Our team is actively working on improvements and we'd love to make this right for you.";
  }
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { review_text, rating, review_id } = body;
    
    // Simulate AI processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const mockResponse = generateMockResponse(rating, review_text);
    
    return NextResponse.json({
      success: true,
      response: mockResponse,
      length: mockResponse.length,
      language: "en"
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, message: 'AI preview failed' },
      { status: 500 }
    );
  }
}
