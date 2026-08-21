import json
import os
import sys
import pandas as pd
import asyncio
import aiohttp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from config.prompts import build_system_prompt, build_user_prompt
from models.schemas import ClassifiedReview
from utils.llm_client import GroqClient

async def classify_row(session, client, row: dict, system_prompt: str) -> dict | None:
    """Classify a single row by calling the LLM API."""
    user_prompt = build_user_prompt(
        review_text=row["review_text"],
        platform=row["source_platform"],
        source_url=row["source_url"],
        date=row["date"],
        rating=row.get("rating"),
    )
    try:
        json_output = await client.generate_json_async(session, system_prompt, user_prompt)
        parsed = json.loads(json_output)
        validated = ClassifiedReview(**parsed)

        # Merge original row data with classified fields
        combined = dict(row)
        combined.update(validated.model_dump())
        return combined
    except Exception as e:
        print(f"  ✗ Error classifying row: {e}")
        return None

async def main_async():
    if not os.path.exists(settings.CLEAN_DATA_PATH):
        print(f"File not found: {settings.CLEAN_DATA_PATH}. Run clean_data.py first.")
        return

    try:
        client = GroqClient()
    except ValueError as e:
        print(e)
        print("Please check your .env file or configuration.")
        return

    # Load the CSV source data
    df = pd.read_csv(settings.CLEAN_DATA_PATH)
    print(f"Loaded {len(df)} tagged reviews from CSV.")

    system_prompt = build_system_prompt()
    classified_data = []

    async with aiohttp.ClientSession() as session:
        for index, row in df.iterrows():
            print(f"Classifying row {index + 1}/{len(df)}...")
            result = await classify_row(session, client, dict(row), system_prompt)
            if result:
                classified_data.append(result)
            
            # Simple rate limiting delay
            await asyncio.sleep(2)

    os.makedirs(os.path.dirname(settings.CLASSIFIED_DATA_PATH), exist_ok=True)
    with open(settings.CLASSIFIED_DATA_PATH, "w") as f:
        json.dump(classified_data, f, indent=2)

    print(f"\nClassification complete! Exported {len(classified_data)} reviews to {settings.CLASSIFIED_DATA_PATH}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
