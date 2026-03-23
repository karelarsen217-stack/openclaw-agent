import os
import time
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SLEEP_SECONDS = 1800  # 30 minutter mellom hver kjøring

sent_ids = set()


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)


def get_products():
    prompt = """
You are an elite dropshipping product researcher.

ONLY find products that are TRENDING RIGHT NOW (last 7-30 days).

STRICT RULES:
- DO NOT show evergreen products
- DO NOT show saturated products
- DO NOT show products popular in 2022–2024
- ONLY early-stage or breakout trends

DATA SOURCES:
- TikTok (must analyze current videos)
- Reddit (r/dropshipping, r/tiktokmadebuyit)
- Google Trends
- News / emerging consumer trends

TIKTOK VALIDATION (REQUIRED):
- At least 5 videos posted in last 7–14 days
- Each video must have 10k+ views minimum
- Prefer low competition (few ads, many organic videos)

PRODUCT MUST:
- Solve a real problem
- Have strong “wow” or visual hook
- Be lightweight (max 1kg)
- Be cheap to source ($1–$15)
- Be suitable for paid ads

OUTPUT ONLY PRODUCTS WITH:
- Trend score 85–100 ONLY
- If below → DO NOT SHOW

FOR EACH PRODUCT INCLUDE:
- Product name
- WHY it is trending NOW (not before)
- TikTok data (views, recency)
- Competitor saturation (LOW/MED/HIGH)
- Supplier (AliExpress / Zendrop etc)
- Direct product link
- Cost price
- Selling price
- Profit margin
- FINAL VERDICT (ONLY: TEST NOW / SKIP)

If no strong products are found:
→ Output: "NO A+ PRODUCTS FOUND"

Return structured data:

Product Name:
Trend Score (0-100):
Why it's trending:
TikTok signal:
Competitor saturation:
Supplier:
Estimated cost:
Selling price:
Profit margin:
Product link:
Verdict:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


def main():
    while True:
        try:
            print("🔎 Scanner etter produkter...")

            products = get_products()
filtered = []
now = time.time()

for item in products:
    created = item.get("createTime", 0)
    days_old = (now - created) / 86400

    shares = item.get("stats", {}).get("shareCount", 0)
    comments = item.get("stats", {}).get("commentCount", 0)
    views = item.get("stats", {}).get("playCount", 0)

    caption = item.get("text", "").lower()

    banned = ["diy", "book", "books", "list", "hack"]
    if any(word in caption for word in banned):
        continue

    if days_old <= 30 and shares > 1000 and comments > 100 and views > 50000:
        filtered.append(item)

products = filtered
            if "Trend Score" in products:
                send_telegram(f"🔥 PRODUCT FOUND:\n\n{products}")
                print("✅ Sendt til Telegram")
            else:
                print("Ingen gode produkter denne runden")

        except Exception as e:
            err = f"Error: {str(e)}"
            print(err)
            send_telegram(err)

        print("😴 Sover i 30 minutter...")
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
