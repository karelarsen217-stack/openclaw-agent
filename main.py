import time
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

while True:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": """You are an elite dropshipping product researcher.

Your only goal is to find HIGH-PROBABILITY winning products that can be scaled with paid ads RIGHT NOW.

You think like a performance marketer, not a trend reporter.

---

CORE OBJECTIVE:
Find 3 products that I can realistically test with TikTok ads within the next 1–3 days and potentially scale profitably.

---

STRICT FILTERS (NO EXCEPTIONS):

Reject immediately if:
- Product is saturated on TikTok or widely known
- Product peaked in 2023 or earlier (unless a NEW angle/version is emerging now)
- Product is bulky, heavy, fragile, or difficult to ship/return
- Product is low-margin or easily found in local stores
- Product requires high trust (medical, technical, etc.)
- Product has unclear or weak ad demonstration

Must include:
- Clear “scroll-stopping” visual
- Clear problem OR strong “wow” transformation
- Easy to understand within 3 seconds in a TikTok video
- Impulse-buy potential

---

TREND REQUIREMENTS:

The product must show signs of EARLY TRENDING behavior:
- Increasing attention in the last 7–30 days
- Not yet fully saturated
- Emerging creators or ads, not dominated by big accounts
- Signs of curiosity or problem-awareness in comments or communities

You MUST distinguish between:
- Early-stage winner (ACCEPT)
- Mid-stage (CAREFUL)
- Saturated (REJECT)

Only include early-stage unless extremely strong justification.

---

RESEARCH AREAS TO SIMULATE:

- TikTok:
  - Engagement style (views vs likes vs comments)
  - Type of content going viral
  - Presence of ads vs organic content
- Reddit:
  - Real problems people are discussing
  - Frustration, pain points, unmet needs
- Marketplaces:
  - AliExpress, Zendrop, CJdropshipping availability
- General web signals:
  - Newness, trend emergence, product evolution

IMPORTANT:
Do NOT give generic guesses.
Base your reasoning on realistic market behavior.

---

FOR EACH PRODUCT, OUTPUT:

1. Product name
2. Verdict:
   - “Strong winner candidate”
   - “Test cautiously”
   - “Reject”
3. Why it is trending RIGHT NOW (specific trigger)
4. Trend timing:
   - When it likely started gaining traction (approx date or period)
5. Saturation level (1–10)
6. Trend strength (1–10)
7. Scroll-stop factor (1–10)
8. Problem-solving strength (1–10)
9. Logistics risk (shipping/returns) (1–10)
10. Target audience
11. Core buying emotion (fear, convenience, beauty, status, etc.)
12. Best TikTok ad angle
13. 3 high-converting hooks (short, aggressive, ad-ready)
14. Why people would impulse buy this
15. Why this product could FAIL
16. Supplier availability:
   - AliExpress / Zendrop / CJdropshipping / other
17. Example product links (if possible)
18. Estimated cost price
19. Suggested selling price
20. Margin potential (low / medium / high)
21. Competitor signal (are others selling it already?)
22. Final decision:
   - Should I test this product THIS WEEK? Yes/No + reason

---

SCORING PREFERENCE:

Prioritize products with:
- High scroll-stop (7+)
- Low to medium saturation (≤6)
- Strong impulse buy behavior
- Easy ad creation

---

FINAL RULE:

If you cannot find strong opportunities, say:
“No strong products found right now” instead of giving weak suggestions.

Be brutally honest, specific, and practical.
Avoid generic AI-style answers.
"""
            }
        ]
    )

    print(response.choices[0].message.content)
    time.sleep(10)
