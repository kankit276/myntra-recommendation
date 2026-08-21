import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GroqClient:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()

        self.api_key = os.getenv("GROQ_API_KEY", "")
        if not self.api_key:
            raise ValueError("No Groq API key found. Set GROQ_API_KEY in your .env file.")

        self.url = "https://api.groq.com/openai/v1/chat/completions"
        print("  GroqClient initialized")

    async def generate_json_async(self, session, system_prompt, user_prompt):
        import asyncio
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        for attempt in range(10):
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            try:
                async with session.post(self.url, headers=headers, json=payload, timeout=30) as response:
                    if response.status == 429:
                        wait = 15 * (attempt + 1)
                        print(f"    ⏳ Rate-limited. Backoff {wait}s (attempt {attempt + 1}/10)...")
                        await asyncio.sleep(wait)
                        continue

                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"API Error {response.status}: {text}")

                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
            except Exception as e:
                if attempt == 9:
                    raise e
                wait = min(2 ** (attempt + 1), 60)
                print(f"    ⚠ Attempt {attempt + 1}/10 failed: {e}. Retrying in {wait}s...")
                await asyncio.sleep(wait)
