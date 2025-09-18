# TikTok → YouTube Auto Uploader Bot

This bot:
- Scrapes TikTok videos from a username
- Downloads them without watermark
- Uploads 20 per day to YouTube
- Spreads uploads randomly between 9 AM – 11 PM
- Keeps track so it never re-uploads
- Runs automatically on Render with self-ping

## Setup

1. **Google API Credentials**
   - Enable YouTube Data API v3 in Google Cloud Console
   - Download `client_secret.json`
   - Run locally once: `python uploader.py`
   - Upload generated `token.json` and `client_secret.json` to Render

2. **Deploy on Render**
   - Push to GitHub, connect to Render
   - Deploy as Web Service

3. **Customize**
   - Edit `uploader.py` → change TikTok `username`

Done ✅
