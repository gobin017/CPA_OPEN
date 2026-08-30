import random
import time
from playwright.sync_api import sync_playwright

def clicker():
    with sync_playwright() as p:
        # Rotate real residential proxies
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-blink-features=AutomationControlled",
            f"--proxy-server={os.getenv('PROXY_URL', 'http://residential-proxy-ip:port')}"
        ])
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
                page.fill("input[name*='name']", "AxionTest")
                page.fill("input[name*='email']", f"test{random.randint(100000,999999)}@example.com")
                page.fill("input[name*='zip']", str(random.randint(10000,99999)))
                page.click("button[type='submit'], input[type='submit']")
                time.sleep(random.uniform(3, 7))
                context.close()
                # Fake real traffic to hide the loop
                page.goto("https://theracker.co.uk/")
                print(f"✅ Clicked from real residential proxy at {time.strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"❌ Error: {e}")
            time.sleep(CLICK_INTERVAL)
