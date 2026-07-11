# MediaDownloaderHub 📥

A full-stack media downloading application and Telegram Bot. This project allows users to download videos and media from various platforms (like TikTok, YouTube, Instagram, etc.) through a clean web interface or directly via a Telegram bot.

## 🚀 Tech Stack

- **Frontend:** Vue 3, Vite, Vue Router (Deployed on [Vercel](https://vercel.com/))
- **Backend (API):** Python, Flask, Gunicorn (Deployed on [Render.com](https://render.com/))
- **Bot Worker:** `python-telegram-bot` (Runs concurrently with the backend)
- **Database:** PostgreSQL via [Neon.tech](https://neon.tech/) (Local fallback to SQLite)
- **Media Processing:** `yt-dlp` and `ffmpeg`

## ✨ Features
- **Universal Downloader:** Download videos from dozens of platforms.
- **Telegram Bot Integration:** Send a link to the bot to get your video immediately.
- **User Authentication:** Register, Login, and Google OAuth support.
- **Download History:** Keep track of previously downloaded files.

## 🛠️ Local Development Setup

### 1. Backend Setup
```bash
cd backend

# Install requirements
pip install -r requirements.txt

# You will need ffmpeg installed on your system!
# Windows: Download from gyan.dev
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# Run the Flask API and the Telegram Bot
# Ensure you have a .env file configured first!
python app.py
python bot.py
```

### 2. Frontend Setup
```bash
cd frontend

# Install Node modules
npm install

# Start the Vite development server
npm run dev
```

## 🌍 Deployment Architecture

This project is configured to be hosted **100% for free**:
1. **Database:** Create a free Postgres database on Neon.tech.
2. **Backend & Bot:** Deployed on Render.com using the included `Dockerfile` and `start.sh` script to run both processes simultaneously. 
3. **Frontend:** Deployed on Vercel as a static site. API URLs point to the Render backend.
4. **Keep-Awake:** UptimeRobot is used to ping the Render backend every 10 minutes to prevent the free tier from sleeping, ensuring the Telegram bot stays online 24/7.
