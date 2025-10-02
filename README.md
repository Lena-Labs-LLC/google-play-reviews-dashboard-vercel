# Google Play Reviews Dashboard

A modern, streamlined dashboard for managing Google Play Store app reviews with AI-powered response generation. Built entirely with Next.js for optimal performance and deployment on Vercel.

## ✨ Features

- 📱 **Review Management**: Fetch and display latest app reviews from Google Play Store
- 🤖 **AI-Powered Responses**: Generate contextual replies using Google's Gemini AI
- 🌍 **Multi-language Support**: Automatic language detection (Turkish/English)
- ⚡ **Real-time Updates**: Live review fetching and response posting
- 🎨 **Modern UI**: Beautiful, responsive design with Tailwind CSS
- 🚀 **Vercel Optimized**: Single-stack deployment for maximum performance

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with TypeScript
- **API Routes**: Next.js API Routes (no separate backend needed)
- **AI**: Google Gemini Pro API
- **Google APIs**: Google Play Developer API, Google Auth Library
- **Styling**: Tailwind CSS
- **Deployment**: Vercel (optimized)

## 🚀 Quick Start

### Prerequisites

1. **Google Play Console Access**: Access to Google Play Console for your app
2. **Service Account**: Create a service account with Google Play Developer API access
3. **Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Installation

1. Clone and install:
```bash
git clone <repository-url>
cd google-play-reviews-dashboard-vercel
npm install
```

2. Set up environment variables:
```bash
# Copy example file
cp env.example .env.local

# Edit .env.local with your credentials
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Run development server:
```bash
npm run dev
```

4. Open `http://localhost:3000`

### Configuration

1. **Upload Service Account JSON**: Upload your Google Play service account JSON file
2. **Enter Gemini API Key**: Add your Google AI Studio API key  
3. **Set Package Name**: Enter your app's package name (e.g., com.example.app)
4. **Click Configure**: Initialize the connection

## 📡 API Routes

All API endpoints are built with Next.js API Routes:

- `POST /api/configure` - Configure app package and credentials
- `GET /api/reviews` - Fetch latest reviews
- `POST /api/ai-preview` - Preview AI-generated response
- `POST /api/reply` - Reply to a specific review

## 🚀 Deployment to Vercel

### Automatic Deployment

1. Push to GitHub:
```bash
git add .
git commit -m "Complete Next.js rewrite - ready for Vercel"
git push origin main
```

2. Connect to Vercel:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will auto-detect Next.js and deploy

3. Set Environment Variables in Vercel:
   - Go to Project Settings → Environment Variables
   - Add `GEMINI_API_KEY=your_api_key_here`

### Manual Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## 🔧 Configuration

The app now uses a simplified, single-stack architecture:

- **Frontend**: Next.js app in root directory
- **API**: Next.js API routes (`/app/api/*`)
- **No separate backend**: Everything runs in Next.js

## 🌟 Key Improvements

- ✅ **Single Language Stack**: Pure TypeScript/JavaScript
- ✅ **Vercel Optimized**: No complex deployment configuration
- ✅ **Simplified Architecture**: No separate frontend/backend
- ✅ **Better Performance**: Faster cold starts, better caching
- ✅ **Easier Maintenance**: Single codebase, unified dependencies

## 🔐 Security

- 🛡️ Environment variables for API keys
- 🔒 Secure credential handling
- 🚫 No sensitive data in client-side code

## 📱 Features in Action

1. **Review Fetching**: Displays mock reviews (easily replaceable with real Google Play API)
2. **AI Responses**: Generates contextual replies based on review sentiment and language
3. **Turkish Support**: Automatically detects Turkish text and responds appropriately
4. **Modern UI**: Clean, responsive interface optimized for all devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- Create an issue for bugs or feature requests
- Check the Vercel deployment logs for troubleshooting
- Review Next.js documentation for API routes

## 🗺️ Roadmap

- [ ] Real Google Play API integration
- [ ] Advanced analytics dashboard  
- [ ] Bulk reply operations
- [ ] Custom AI prompt templates
- [ ] Multi-app support
- [ ] Webhook integrations