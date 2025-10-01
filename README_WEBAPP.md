# Google Play Reviews Dashboard - Web Application

Modern web application for managing Google Play app reviews with AI-powered responses.

## 🏗️ Architecture

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI
- **AI**: Google Gemini 2.0 Flash
- **API**: Google Play Developer API

## 📦 Project Structure

```
.
├── backend/
│   ├── api.py                 # FastAPI server
│   ├── requirements.txt       # Python dependencies
│   └── run.py                # Server runner
├── frontend/
│   ├── app/
│   │   ├── page.tsx          # Main dashboard
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css       # Global styles
│   ├── package.json          # Node dependencies
│   └── next.config.mjs       # Next.js config
├── auth.py                   # Google Play authentication
├── reviews.py                # Reviews management
├── ai_response.py            # AI response generator
└── knowledge_base.json       # App knowledge base
```

## 🚀 Setup

### 1. Backend Setup

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
# Windows:
set GEMINI_API_KEY=your_gemini_api_key_here

# Linux/Mac:
export GEMINI_API_KEY=your_gemini_api_key_here

# Run the backend server
python run.py
```

Backend will run on: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Install Node dependencies
cd frontend
npm install

# Run the development server
npm run dev
```

Frontend will run on: `http://localhost:3000`

## 🎯 Features

### ✅ **Implemented**
- 📋 **Reviews Dashboard** - View all app reviews
- 🤖 **AI Preview** - Preview AI-generated responses
- ✏️ **Edit & Send** - Edit AI responses before sending
- 🔄 **Real-time Updates** - Refresh reviews anytime
- 🎨 **Modern UI** - Beautiful, responsive design
- 🌙 **Dark Mode** - Automatic dark mode support

### 🚧 **Coming Soon**
- 📊 **Analytics Dashboard** - Charts and statistics
- 📜 **Reply History** - View all sent replies
- 🔍 **Filter & Search** - Filter by rating, language, etc.
- 🔔 **Notifications** - Real-time review notifications
- ⚙️ **Settings** - Customize prompts and knowledge base
- 📱 **Mobile App** - React Native mobile version

## 📱 Usage

### 1. Configure Package

1. Open `http://localhost:3000`
2. Enter your app package name (e.g., `com.nanobanana.app`)
3. Click "Configure"

### 2. Manage Reviews

1. View latest reviews in the left panel
2. Click on a review to preview AI response
3. Edit the response if needed
4. Click "Send Reply" to post

### 3. Monitor Statistics

- Switch to "Stats" tab to view analytics
- Switch to "History" tab to view reply history

## 🔐 Security

- ✅ Service account authentication
- ✅ Secure API communication
- ✅ CORS protection
- ✅ Environment variable secrets

## 🛠️ API Endpoints

### Backend API

- `POST /configure` - Configure package
- `GET /reviews` - Get latest reviews
- `POST /reply` - Reply to a review
- `POST /auto-reply` - Auto-reply with AI
- `POST /ai-preview` - Preview AI response
- `GET /stats` - Get statistics
- `GET /history` - Get reply history
- `GET /health` - Health check

## 🎨 Customization

### Update Knowledge Base

Edit `knowledge_base.json` to customize:
- App name and description
- Features list
- FAQs
- Support contact

### Customize AI Prompts

Edit `ai_response.py` → `_build_prompt()` method

### Customize UI

Edit `frontend/app/page.tsx` and `frontend/app/globals.css`

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify `service_account.json` exists
- Check Python dependencies installed

### Frontend won't start
- Check if port 3000 is available
- Run `npm install` again
- Clear `.next` folder and rebuild

### API connection issues
- Ensure backend is running on port 8000
- Check CORS settings in `api.py`
- Verify network/firewall settings

### AI not working
- Check `GEMINI_API_KEY` is set
- Verify API key is valid
- Check Gemini API quotas

## 📝 Development

### Run in Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Build for Production

**Backend:**
```bash
cd backend
# Use a production WSGI server like Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

## 🚀 Deployment

### Deploy Backend
- Use Docker + Fly.io / Railway / Heroku
- Or use serverless functions (AWS Lambda, Google Cloud Functions)

### Deploy Frontend
- Deploy to Vercel (recommended for Next.js)
- Or use Netlify, AWS Amplify, or any Node.js hosting

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 💬 Support

For issues or questions, please open a GitHub issue.


