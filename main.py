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
TARGET_URL = os.getenv("TARGET_URL", "https://surveys2cash.com/register")  # your new offer
CLICK_INTERVAL = int(os.getenv("CLICK_INTERVAL", "12"))
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
                context = browser.new_context(
                    user_agent=random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
                    ])
                )
                page = context.new_page()
                page.goto(TARGET_URL, wait_until="domcontentloaded")
                
                # Surveys2Cash form selectors (updated from repo)
                page.fill('input[name="first_name"]', "AxionTest")
                page.fill('input[name="last_name"]', "Test")
                page.fill('input[name="street_address"]', "123 Test St")
                page.fill('input[name="zip"]', str(random.randint(10000, 99999)))
                page.select_option('select[name="state"]', label="California")
                page.fill('input[name="email"]', f"test{random.randint(100000,999999)}@example.com")
                page.select_option('select[name="gender"]', label="Male")
                page.fill('input[name="date_of_birth"]', "01/01/1990")  # approx
                
                page.click('button:has-text("CONTINUE")')
                
                time.sleep(random.uniform(5, 12))
                context.close()
                
                # Fake real traffic
                page.goto("https://theracker.co.uk/")
                print(f"✅ Clicked Surveys2Cash at {time.strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"❌ Error: {e}")
            time.sleep(CLICK_INTERVAL)

threading.Thread(target=clicker, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
