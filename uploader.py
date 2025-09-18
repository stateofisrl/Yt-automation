import os
import time
import random
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def youtube_authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

youtube = youtube_authenticate()

def get_tiktok_videos(username, limit=200):
    urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://www.tiktok.com/@{username}")
        time.sleep(5)
        while len(urls) < limit:
            links = page.query_selector_all("a[href*='/video/']")
            for link in links:
                url = link.get_attribute("href")
                if url and url not in urls:
                    urls.append(url)
            page.mouse.wheel(0, 2000)
            time.sleep(2)
        browser.close()
    return urls[:limit]

def download_tiktok(url, filename="video.mp4"):
    api_url = f"https://api.snaptik.app/v1/video?url={url}"
    r = requests.get(api_url).json()
    no_watermark = r["download_url"]
    video = requests.get(no_watermark, stream=True)
    with open(filename, "wb") as f:
        for chunk in video.iter_content(chunk_size=1024):
            f.write(chunk)
    return filename

def upload_to_youtube(video_file, title, description="Uploaded from TikTok", tags=[]):
    body = {
        "snippet": {"title": title, "description": description, "tags": tags},
        "status": {"privacyStatus": "public"}
    }
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print("✅ Uploaded:", response["id"])
    return response["id"]

def daily_upload(username, daily_limit=20, start_hour=9, end_hour=23):
    if not os.path.exists("video_links.txt"):
        print("Fetching TikTok videos...")
        all_videos = get_tiktok_videos(username, limit=500)
        with open("video_links.txt", "w") as f:
            for v in all_videos:
                f.write(v + "\n")
    with open("video_links.txt", "r") as f:
        all_videos = f.read().splitlines()
    uploaded = set()
    if os.path.exists("uploaded.txt"):
        with open("uploaded.txt", "r") as f:
            uploaded = set(f.read().splitlines())
    remaining = [v for v in all_videos if v not in uploaded]
    if not remaining:
        print("🎉 All videos uploaded!")
        return
    today_batch = remaining[:daily_limit]
    print(f"📅 Today we will upload {len(today_batch)} videos")
    now = datetime.now()
    start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    if now > end_time:
        print("⏰ Too late today. Try again tomorrow.")
        return
    slots = sorted(random.sample(range(int((end_time - start_time).total_seconds())), len(today_batch)))
    schedule = [start_time + timedelta(seconds=s) for s in slots]
    for link, post_time in zip(today_batch, schedule):
        while datetime.now() < post_time:
            time.sleep(30)
        try:
            filename = download_tiktok(link)
            title = f"TikTok Video {link.split('/')[-1]}"
            vid_id = upload_to_youtube(filename, title)
            with open("uploaded.txt", "a") as f:
                f.write(link + "\n")
        except Exception as e:
            print("❌ Error:", e)
    print("✅ Finished today's batch.")

def run_bot():
    username = "premierleague"
    daily_upload(username, daily_limit=20, start_hour=9, end_hour=23)
