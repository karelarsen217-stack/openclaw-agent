import os
import time
import json
import hashlib
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MODEL = "gpt-4o-mini"
SLEEP_SECONDS = 1800  # 30 min. Sett til 10 for testing, tilbake til 1800 etterpå.

# Bare for å unngå å sende samme forslag om igjen mens appen kjører
sent_ids = set()


def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram env vars mangler.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # Telegram har maks lengde, så vi splitter ved behov
    chunks = [message[i:i + 3900] for i in range(0, len(message), 3900)]
    for chunk in chunks:
        resp = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": chunk,
                "disable_web_page_preview": False,
            },
            timeout=30,
        )
        print("Telegram status:", resp.status_code, resp.text[:300])


def stable_id(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def build_prompt() -> str:
    return """
You are an elite, brutally honest Shopify dropshipping product researcher and direct-response marketer.

Your only goal is to find HIGH-PROBABILITY A+ products that are worth testing with paid ads RIGHT NOW.

You must think like a real performance marketer with many years of e-commerce experience.
Do NOT act like a generic trend reporter.

HARD RULES:
- Focus on products showing signs of early trend growth NOW, preferably within the last 7–30 days
- Prefer products just starting to gain traction, not products that already had their big wave
- Reject products that peaked in 2023 or earlier, unless a clearly NEW angle/version has emerged now
- Reject products that are bulky, heavy, fragile, awkward to ship, or likely to create return/refund headaches
- Reject products that feel generic, boring, hard to demonstrate, or easy to buy in local physical stores
- Reject products with weak ad creatives or unclear “why now”
- Reject products that are obviously oversaturated on TikTok, Amazon, Temu, etc.
- Prefer products with visual wow-factor, problem-solving power, or emotional pull
- Prefer products easy to understand in 1–3 seconds in short-form video
- Prefer products with strong impulse-buy potential
- Prefer products suitable for TikTok-style paid ads

SIMULATE RESEARCH ACROSS:
- TikTok: freshness, views, comments, engagement style, ad presence, creator spread
- Reddit: pain points, frustration, unmet needs, problem awareness
- News / web / social signals: rising attention, new awareness, seasonal or cultural triggers
- Supplier / marketplace availability: AliExpress, Zendrop, CJdropshipping, DSers-compatible sources, Amazon, Temu

IMPORTANT:
- Be skeptical and practical
- Do not hallucinate confidence
- If evidence is weak, say so
- Give realistic estimates, not fake certainty
- Include direct product/supplier/search links whenever possible
- Focus on profitability and ad testability, not just “interesting” items

RETURN JSON ONLY in this exact structure:

{
  "products": [
    {
      "product_name": "string",
      "one_sentence_verdict": "Strong winner candidate / Test cautiously / Reject",
      "why_trending_now": "string",
      "trend_timing": "string",
      "earliest_signal_or_launch_clue": "string",
      "trend_freshness_score": 0,
      "saturation_score": 0,
      "scroll_stop_score": 0,
      "problem_solving_score": 0,
      "logistics_risk_score": 0,
      "impulse_buy_score": 0,
      "ad_creative_strength_score": 0,
      "winner_score": 0,
      "recommended_this_week": "Yes / No",
      "target_audience": "string",
      "core_buying_emotion": "string",
      "best_tiktok_ad_angle": "string",
      "three_hook_ideas": ["string", "string", "string"],
      "short_tiktok_script": "string",
      "why_people_impulse_buy": "string",
      "why_this_could_fail": "string",
      "supplier_availability": {
        "aliexpress": "string",
        "zendrop": "string",
        "cjdropshipping": "string",
        "other": "string"
      },
      "example_links": ["string", "string", "string"],
      "estimated_buy_price_usd": "string",
      "suggested_selling_price_usd": "string",
      "margin_potential": "Low / Medium / High",
      "competitor_signal": "string",
      "shipping_returns_note": "string",
      "final_reasoning": "string"
    }
  ]
}

SCORING GUIDELINES:
- trend_freshness_score: 1–10
- saturation_score: 1–10 where LOWER is better
- scroll_stop_score: 1–10
- problem_solving_score: 1–10
- logistics_risk_score: 1–10 where LOWER is better
- impulse_buy_score: 1–10
- ad_creative_strength_score: 1–10
- winner_score: 0–100 overall commercial test score

VERY IMPORTANT FILTER:
Only include products that are at least plausible.
If there are no strong products, return an empty "products" list.
Do not force weak ideas.
""".strip()


def get_products():
    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a strict JSON-only e-commerce product research engine."
            },
            {
                "role": "user",
                "content": build_prompt()
            }
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content
    return json.loads(content)


def is_a_plus(product: dict) -> bool:
    try:
        return (
            product.get("winner_score", 0) >= 80
            and product.get("trend_freshness_score", 0) >= 8
            and product.get("saturation_score", 10) <= 6
            and product.get("logistics_risk_score", 10) <= 5
            and product.get("scroll_stop_score", 0) >= 7
            and product.get("impulse_buy_score", 0) >= 7
            and product.get("ad_creative_strength_score", 0) >= 7
            and str(product.get("recommended_this_week", "")).lower() == "yes"
            and str(product.get("one_sentence_verdict", "")).lower() != "reject"
        )
    except Exception:
        return False


def format_product_message(product: dict) -> str:
    hooks = product.get("three_hook_ideas", [])
    links = product.get("example_links", [])

    msg = f"""🔥 A+ PRODUCT ALERT

Produkt: {product.get("product_name", "Ukjent")}
Verdict: {product.get("one_sentence_verdict", "-")}
Test denne uka: {product.get("recommended_this_week", "-")}
Winner score: {product.get("winner_score", "-")}/100

Hvorfor trender nå:
{product.get("why_trending_now", "-")}

Trend timing:
{product.get("trend_timing", "-")}
Tidligste signal / launch clue:
{product.get("earliest_signal_or_launch_clue", "-")}

Scores:
- Freshness: {product.get("trend_freshness_score", "-")}/10
- Saturation: {product.get("saturation_score", "-")}/10
- Scroll-stop: {product.get("scroll_stop_score", "-")}/10
- Problem-solving: {product.get("problem_solving_score", "-")}/10
- Logistics risk: {product.get("logistics_risk_score", "-")}/10
- Impulse buy: {product.get("impulse_buy_score", "-")}/10
- Ad creative strength: {product.get("ad_creative_strength_score", "-")}/10

Target audience:
{product.get("target_audience", "-")}

Core buying emotion:
{product.get("core_buying_emotion", "-")}

Best TikTok ad angle:
{product.get("best_tiktok_ad_angle", "-")}

3 hooks:
1. {hooks[0] if len(hooks) > 0 else "-"}
2. {hooks[1] if len(hooks) > 1 else "-"}
3. {hooks[2] if len(hooks) > 2 else "-"}

Kort TikTok script:
{product.get("short_tiktok_script", "-")}

Hvorfor folk impulskjøper:
{product.get("why_people_impulse_buy", "-")}

Hvorfor det kan feile:
{product.get("why_this_could_fail", "-")}

Pris:
- Innkjøp: {product.get("estimated_buy_price_usd", "-")}
- Salgspris: {product.get("suggested_selling_price_usd", "-")}
- Margin: {product.get("margin_potential", "-")}

Supplier availability:
- AliExpress: {product.get("supplier_availability", {}).get("aliexpress", "-")}
- Zendrop: {product.get("supplier_availability", {}).get("zendrop", "-")}
- CJdropshipping: {product.get("supplier_availability", {}).get("cjdropshipping", "-")}
- Other: {product.get("supplier_availability", {}).get("other", "-")}

Competitor signal:
{product.get("competitor_signal", "-")}

Shipping / returns note:
{product.get("shipping_returns_note", "-")}

Links:
{links[0] if len(links) > 0 else "-"}
{links[1] if len(links) > 1 else ""}
{links[2] if len(links) > 2 else ""}

Final reasoning:
{product.get("final_reasoning", "-")}
"""
    return msg.strip()


def main():
    while True:
        try:
            data = get_products()
            products = data.get("products", [])

            if not products:
                print("Ingen sterke produkter funnet i denne runden.")
                time.sleep(SLEEP_SECONDS)
                continue

            sent_any = False

            for product in products:
                if not is_a_plus(product):
                    print(f"Filtrert bort: {product.get('product_name', 'Ukjent')} (ikke A+ nok)")
                    continue

                message = format_product_message(product)
                pid = stable_id(message)

                if pid in sent_ids:
                    print(f"Allerede sendt: {product.get('product_name', 'Ukjent')}")
                    continue

                print("\n===== A+ PRODUCT =====\n")
                print(message)
                send_telegram(message)
                sent_ids.add(pid)
                sent_any = True

            if not sent_any:
                print("Ingen nye A+ produkter å sende i denne runden.")

        except Exception as e:
            err = f"Error: {str(e)}"
            print(err)
            send_telegram(err)

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
