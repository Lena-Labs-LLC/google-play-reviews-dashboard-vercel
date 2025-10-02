import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { review_text, rating, review_id } = body;

    if (!review_text || !rating) {
      return NextResponse.json(
        { success: false, message: 'Review text and rating are required' },
        { status: 400 }
      );
    }

    // Get Gemini API key from environment or request
    const geminiApiKey = process.env.GEMINI_API_KEY || body.gemini_api_key;
    
    if (!geminiApiKey) {
      // Return mock response if no API key
      const mockResponse = generateMockResponse(rating, review_text);
      return NextResponse.json({
        success: true,
        response: mockResponse,
        length: mockResponse.length,
        language: detectLanguage(review_text)
      });
    }

    try {
      // Initialize Gemini AI
      const genAI = new GoogleGenerativeAI(geminiApiKey);
      const model = genAI.getGenerativeModel({ model: "gemini-pro" });

      // Create prompt based on rating and language
      const language = detectLanguage(review_text);
      const prompt = createPrompt(review_text, rating, language);

      // Generate AI response
      const result = await model.generateContent(prompt);
      const response = await result.response;
      const aiResponse = response.text();

      return NextResponse.json({
        success: true,
        response: aiResponse,
        length: aiResponse.length,
        language: language
      });

    } catch (aiError) {
      console.error('AI generation failed:', aiError);
      // Fallback to mock response
      const mockResponse = generateMockResponse(rating, review_text);
      return NextResponse.json({
        success: true,
        response: mockResponse,
        length: mockResponse.length,
        language: detectLanguage(review_text),
        note: "AI unavailable, using template response"
      });
    }

  } catch (error) {
    console.error('AI preview error:', error);
    return NextResponse.json(
      { success: false, message: 'AI preview failed' },
      { status: 500 }
    );
  }
}

function detectLanguage(text: string): string {
  // Simple language detection
  const turkishChars = /[çğıöşüÇĞIİÖŞÜ]/;
  return turkishChars.test(text) ? 'tr' : 'en';
}

function createPrompt(reviewText: string, rating: number, language: string): string {
  const isPositive = rating >= 4;
  const isNeutral = rating === 3;
  
  if (language === 'tr') {
    if (isPositive) {
      return `Bir mobil uygulama geliştiricisi olarak, aşağıdaki pozitif kullanıcı yorumuna profesyonel, samimi ve minnettarlık dolu bir yanıt yazın. Yanıt 350 karakteri geçmemeli ve Türkçe olmalı:

Kullanıcı yorumu: "${reviewText}"
Puan: ${rating}/5

Yanıtınız şunları içermeli:
- Teşekkür
- Pozitif geri bildirimi takdir etme
- Gelecekteki güncellemeler hakkında kısa bilgi
- Samimi ve profesyonel ton`;
    } else if (isNeutral) {
      return `Bir mobil uygulama geliştiricisi olarak, aşağıdaki nötr kullanıcı yorumuna yapıcı ve iyileştirme odaklı bir yanıt yazın. Yanıt 350 karakteri geçmemeli ve Türkçe olmalı:

Kullanıcı yorumu: "${reviewText}"
Puan: ${rating}/5

Yanıtınız şunları içermeli:
- Geri bildirim için teşekkür
- İyileştirme çabalarından bahsetme
- Kullanıcının önerilerini dikkate aldığınızı belirtme`;
    } else {
      return `Bir mobil uygulama geliştiricisi olarak, aşağıdaki negatif kullanıcı yorumuna anlayışlı, özür dileyen ve çözüm odaklı bir yanıt yazın. Yanıt 350 karakteri geçmemeli ve Türkçe olmalı:

Kullanıcı yorumu: "${reviewText}"
Puan: ${rating}/5

Yanıtınız şunları içermeli:
- Samimi özür
- Sorunu anlayışla karşılama
- Çözüm için çalıştığınızı belirtme
- İletişim kurma isteği`;
    }
  } else {
    // English prompts
    if (isPositive) {
      return `As a mobile app developer, write a professional, warm, and grateful response to the following positive user review. Keep it under 350 characters in English:

User review: "${reviewText}"
Rating: ${rating}/5

Your response should include:
- Gratitude
- Appreciation for positive feedback
- Brief mention of future updates
- Warm and professional tone`;
    } else if (isNeutral) {
      return `As a mobile app developer, write a constructive and improvement-focused response to the following neutral user review. Keep it under 350 characters in English:

User review: "${reviewText}"
Rating: ${rating}/5

Your response should include:
- Thanks for feedback
- Mention of improvement efforts
- Acknowledgment of user suggestions`;
    } else {
      return `As a mobile app developer, write an understanding, apologetic, and solution-focused response to the following negative user review. Keep it under 350 characters in English:

User review: "${reviewText}"
Rating: ${rating}/5

Your response should include:
- Sincere apology
- Understanding of the issue
- Mention of working on a solution
- Invitation to contact for support`;
    }
  }
}

function generateMockResponse(rating: number, reviewText: string): string {
  const language = detectLanguage(reviewText);
  
  if (language === 'tr') {
    if (rating >= 4) {
      return "Pozitif geri bildiriminiz için çok teşekkür ederiz! Uygulamayı beğenmeniz bizim için çok değerli. Ekibimiz sürekli yeni özellikler üzerinde çalışıyor ve deneyiminizi daha da iyileştirmek için elimizden geleni yapıyoruz.";
    } else if (rating === 3) {
      return "Geri bildiriminiz için teşekkürler! Önerilerinizi dikkate alıyoruz ve uygulamayı sürekli iyileştirmek için çalışıyoruz. Gelecek güncellemelerde daha iyi bir deneyim sunmayı hedefliyoruz.";
    } else {
      return "Yaşadığınız sorun için samimi özürlerimizi sunarız. Ekibimiz bu konular üzerinde aktif olarak çalışıyor ve en kısa sürede çözüm sunmayı hedefliyoruz. Desteğe ihtiyacınız olursa bizimle iletişime geçmekten çekinmeyin.";
    }
  } else {
    if (rating >= 4) {
      return "Thank you so much for your positive feedback! We're thrilled that you're enjoying the app. Our team is constantly working on new features to make your experience even better.";
    } else if (rating === 3) {
      return "Thank you for your feedback! We appreciate you taking the time to share your thoughts. We're constantly working to improve the app experience and will consider your suggestions.";
    } else {
      return "Thank you for bringing this to our attention. We sincerely apologize for any inconvenience you've experienced. Our team is actively working on improvements and we'd love to make this right for you.";
    }
  }
}
