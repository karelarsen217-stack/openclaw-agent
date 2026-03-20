import os
import time
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SLEEP_SECONDS = 60  # kjører hvert minutt (perfekt for testing)

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

Find 3 trending products RIGHT NOW (last 7-30 days).

STRICT RULES:
- Must be trending recently (TikTok, Reddit, etc)
- Must solve a real problem
- Must NOT be saturated
- Must NOT be bulky/heavy
- Must have WOW factor
- Must be suitable for TikTok ads

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
        model="gpt-5.3",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


def main():
    while True:
        try:
            print("🔎 Scanner etter produkter...")

            products = get_products()

            # ENKEL FILTER (slipper at alt blir filtrert bort)
            if "Trend Score" in products:
                send_telegram(f"🔥 PRODUCT FOUND:\n\n{products}")
                print("✅ Sendt til Telegram")
            else:
                print("Ingen gode produkter denne runden")

        except Exception as e:
            err = f"Error: {str(e)}"
            print(err)
            send_telegram(err)

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
