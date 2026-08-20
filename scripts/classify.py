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
from utils.llm_client import XAIClient

async def process_row(session, client, idx, row, system_prompt):
    user_prompt = build_user_prompt(
        review_text=row['review_text'],
        platform=row['source_platform'],
        source_url=row['source_url'],
        date=row['date'],
        rating=row.get('rating')
    )
    print(f"Classifying row {idx}...")
    try:
        json_output = await client.generate_json_async(session, system_prompt, user_prompt)
        parsed = json.loads(json_output)
        validated = ClassifiedReview(**parsed)
        
        combined = row.to_dict()
        combined.update(validated.model_dump())
        return combined
    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        return None

async def main_async():
    if not os.path.exists(settings.CLEAN_DATA_PATH):
        print(f"File not found: {settings.CLEAN_DATA_PATH}. Run clean_data.py first.")
        return
        
    try:
        client = XAIClient()
    except ValueError as e:
        print(e)
        print("Please check your .env file or configuration.")
        return

    df = pd.read_csv(settings.CLEAN_DATA_PATH)
    print(f"Loaded {len(df)} tagged reviews for async classification.")
    
    system_prompt = build_system_prompt()
    classified_data = []
    
    start_idx = 0
    if os.path.exists(settings.CLASSIFIED_DATA_PATH):
        try:
            with open(settings.CLASSIFIED_DATA_PATH, 'r') as f:
                classified_data = json.load(f)
            start_idx = len(classified_data)
            print(f"Loaded {start_idx} existing classifications from checkpoint.")
        except Exception:
            print("Could not load checkpoint, starting fresh.")
            
    if start_idx >= len(df):
        print("All rows already classified.")
        return

    async with aiohttp.ClientSession() as session:
        batch_size = 10
        for i in range(start_idx, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            tasks = []
            for idx, row in batch.iterrows():
                tasks.append(process_row(session, client, idx, row, system_prompt))
                
            results = await asyncio.gather(*tasks)
            
            for res in results:
                if res:
                    classified_data.append(res)
                    
            os.makedirs(os.path.dirname(settings.CLASSIFIED_DATA_PATH), exist_ok=True)
            with open(settings.CLASSIFIED_DATA_PATH, 'w') as f:
                json.dump(classified_data, f, indent=2)
            print(f"Checkpointed at row {i + len(batch)}")

    print(f"Async classification complete. Total successfully classified: {len(classified_data)} out of {len(df)}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
