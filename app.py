from flask import Flask
import threading
import time
import requests
import os
from uploader import run_bot

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅"

def scheduler():
    while True:
        print("⏰ Running daily bot...")
        run_bot()
        time.sleep(24 * 60 * 60)

def self_ping():
    while True:
        try:
            url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:10000")
            requests.get(url)
            print("🔄 Self-pinged:", url)
        except:
            pass
        time.sleep(300)

threading.Thread(target=scheduler, daemon=True).start()
threading.Thread(target=self_ping, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
