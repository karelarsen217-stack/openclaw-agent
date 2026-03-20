import time
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

while True:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": """Find 3 trending products in the last 7–30 days.

Include:
- Product name
- Why trending
- Target audience
- Ad angle
"""
                }
            ]
        )

        print(response.choices[0].message.content)

    except Exception as e:
        print("Error:", e)

    time.sleep(10)
