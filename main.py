from flask import Flask, jsonify
import sqlite3
import random
import time
import threading
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
TARGET_URL = os.getenv("TARGET_URL", "https://trianglerockers.com/show.php?l=0&u=2550466&id=73209")
CLICK_INTERVAL = int(os.getenv("CLICK_INTERVAL", "12"))
TEST_MODE = os.getenv("TEST_MODE", "10") == "10"
DATABASE = "clicks.db"

conn = sqlite3.connect(DATABASE)
conn.execute("CREATE TABLE IF NOT EXISTS stats (clicks INTEGER, earnings REAL, errors INTEGER)")
conn.commit()

@app.before_request
def init_db():
    with app.app_context():
        conn.execute("INSERT OR IGNORE INTO stats (clicks, earnings, errors) VALUES (0, 0, 0)")
        conn.commit()

@app.after_request
def log_response(response):
    return response

@app.route("/stats")
def get_stats():
    c = conn.cursor()
    c.execute("SELECT * FROM stats")
    return jsonify(c.fetchone())

def clicker():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        while True:
            try:
                context = browser.new_context(user_agent=random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
                ]))
                page = context.new_page()
                page.goto(TARGET_URL, wait_until="domcontentloaded")
                page.fill("input[name*='name']", "AxionTest")
                page.fill("input[name*='email']", f"test{random.randint(100000,999999)}@example.com")
                page.fill("input[name*='zip']", str(random.randint(10000,99999)))
                page.click("button[type='submit'], input[type='submit']")
                time.sleep(random.uniform(3, 7))
                context.close()
                conn.execute("UPDATE stats SET clicks=clicks+1 WHERE rowid=1")
                conn.commit()
                print(f"✅ Clicked at {time.strftime('%H:%M:%S')}")
            except Exception as e:
                conn.execute("UPDATE stats SET errors=errors+1 WHERE rowid=1")
                conn.commit()
                print(f"❌ Error: {e}")
            time.sleep(CLICK_INTERVAL)

threading.Thread(target=clicker, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
