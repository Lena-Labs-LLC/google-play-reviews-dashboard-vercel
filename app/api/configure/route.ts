import { NextRequest, NextResponse } from 'next/server';
import { google } from 'googleapis';
import { GoogleAuth } from 'google-auth-library';

// Global variables to store configuration
let globalAuth: GoogleAuth | null = null;
let globalPackageName: string | null = null;
let globalGeminiApiKey: string | null = null;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { package_name, service_account_data, gemini_api_key, enable_ai } = body;

    if (!package_name) {
      return NextResponse.json(
        { success: false, message: 'Package name is required' },
        { status: 400 }
      );
    }

    if (!service_account_data) {
      return NextResponse.json(
        { success: false, message: 'Service account data is required' },
        { status: 400 }
      );
    }

    // Create Google Auth instance
    try {
      globalAuth = new GoogleAuth({
        credentials: service_account_data,
        scopes: ['https://www.googleapis.com/auth/androidpublisher']
      });

      // Test authentication
      const authClient = await globalAuth.getClient();
      
      // Store configuration globally
      globalPackageName = package_name;
      globalGeminiApiKey = gemini_api_key;

      return NextResponse.json({
        success: true,
        message: `Configured for package: ${package_name}`,
        ai_enabled: enable_ai && !!gemini_api_key
      });

    } catch (authError) {
      console.error('Authentication failed:', authError);
      return NextResponse.json(
        { success: false, message: 'Invalid service account credentials' },
        { status: 400 }
      );
    }

  } catch (error) {
    console.error('Configuration error:', error);
    return NextResponse.json(
      { success: false, message: 'Configuration failed' },
      { status: 500 }
    );
  }
}

// Note: In production, use a proper state management solution like Redis or database
// These global variables are for demonstration purposes only
