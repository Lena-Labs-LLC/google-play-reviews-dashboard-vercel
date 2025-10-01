# Vercel Deployment Guide

Bu rehber, Google Play Reviews Dashboard uygulamasını Vercel'e deploy etmek için gerekli adımları içerir.

## Ön Gereksinimler

1. **GitHub hesabı** - Kodunuzu public repository'de saklamanız gerekiyor
2. **Vercel hesabı** - [vercel.com](https://vercel.com) üzerinden ücretsiz hesap oluşturun
3. **Google Cloud Console hesabı** - Service account oluşturmak için
4. **Google AI Studio hesabı** - Gemini API key almak için

## Deployment Adımları

### 1. GitHub Repository Oluşturun

```bash
# Projeyi GitHub'a push edin
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/google-play-reviews-dashboard.git
git push -u origin main
```

### 2. Vercel'e Deploy Edin

1. [Vercel Dashboard](https://vercel.com/dashboard)'a gidin
2. "New Project" butonuna tıklayın
3. GitHub repository'nizi seçin
4. Root Directory'yi `frontend` olarak ayarlayın
5. "Deploy" butonuna tıklayın

### 3. Backend'i Ayrı Olarak Deploy Edin

1. Vercel Dashboard'da yeni bir proje oluşturun
2. Aynı GitHub repository'yi seçin
3. Root Directory'yi `backend` olarak ayarlayın
4. "Deploy" butonuna tıklayın

### 4. Environment Variables Ayarlayın

Frontend projesinde:
- `NEXT_PUBLIC_API_URL`: Backend URL'iniz (örn: `https://your-backend.vercel.app`)

Backend projesinde:
- Herhangi bir environment variable gerekmez (kullanıcı bazlı sistem)

### 5. Domain Ayarları

1. Frontend projenizde "Settings" > "Domains" bölümüne gidin
2. Custom domain ekleyin (opsiyonel)
3. Backend URL'ini frontend'e environment variable olarak ekleyin

## Kullanım

1. Uygulamanıza gidin
2. "Sign up" ile yeni hesap oluşturun
3. Google Service Account JSON dosyanızı yükleyin
4. Gemini API key'inizi girin
5. Package name'inizi girin ve configure edin
6. Review'larınızı yönetmeye başlayın!

## Güvenlik Notları

- API keyler artık kullanıcı bazlı saklanıyor
- Service account dosyaları güvenli şekilde şifreleniyor
- Her kullanıcının kendi verileri izole edilmiş durumda
- Session token'lar güvenli şekilde yönetiliyor

## Sorun Giderme

### CORS Hatası
- Backend'de CORS ayarlarını kontrol edin
- Frontend URL'inin backend CORS listesinde olduğundan emin olun

### API Key Hatası
- Service account dosyasının doğru formatta olduğundan emin olun
- Gemini API key'inin geçerli olduğunu kontrol edin

### Build Hatası
- Python dependencies'lerin doğru yüklendiğinden emin olun
- Node.js version'ının uyumlu olduğunu kontrol edin

## Destek

Herhangi bir sorun yaşarsanız:
1. Vercel logs'larını kontrol edin
2. GitHub issues bölümünde sorun bildirin
3. Console'da hata mesajlarını inceleyin

