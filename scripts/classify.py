import pandas as pd
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from config.prompts import build_system_prompt, build_user_prompt
from models.schemas import ClassifiedReview
from utils.llm_client import GeminiClient

def main():
    if not os.path.exists(settings.CLEAN_DATA_PATH):
        print(f"File not found: {settings.CLEAN_DATA_PATH}")
        return
        
    try:
        client = GeminiClient()
    except ValueError as e:
        print(e)
        print("Please add your GEMINI_API_KEY to the .env file to run classification.")
        return
        
    df = pd.read_csv(settings.CLEAN_DATA_PATH)
    print(f"Loaded {len(df)} tagged reviews.")
    
    # Checkpoint load
    classified_data = []
    if os.path.exists(settings.CLASSIFIED_DATA_PATH):
        with open(settings.CLASSIFIED_DATA_PATH, 'r') as f:
            classified_data = json.load(f)
            print(f"Loaded {len(classified_data)} existing classifications from checkpoint.")
            
    processed_urls = {item.get("source_url") for item in classified_data if item.get("source_url")}
    
    system_prompt = build_system_prompt("Myntra")
    
    count = 0
    for idx, row in df.iterrows():
        source_url = row.get("source_url")
        if source_url in processed_urls:
            continue
            
        user_prompt = build_user_prompt(
            review_text=row["review_text"],
            platform=row["source_platform"],
            source_url=source_url,
            date=row["date"],
            rating=row["rating"]
        )
        
        try:
            print(f"Classifying row {idx}...")
            response_json_str = client.generate_json(system_prompt, user_prompt)
            response_dict = json.loads(response_json_str)
            validated = ClassifiedReview(**response_dict)
            
            combined = {
                "source_platform": row["source_platform"],
                "source_url": source_url,
                "date": row["date"],
                "review_text": row["review_text"],
                "rating": row["rating"],
                "signal_type": row.get("signal_type", "none_detected")
            }
            combined.update(validated.model_dump())
            
            classified_data.append(combined)
            processed_urls.add(source_url)
            count += 1
            
            # Checkpoint every 25 rows
            if count % 25 == 0:
                with open(settings.CLASSIFIED_DATA_PATH, 'w') as f:
                    json.dump(classified_data, f, indent=2)
                print(f"Checkpoint saved: {len(classified_data)} total classified.")
                
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            
    # Final save
    with open(settings.CLASSIFIED_DATA_PATH, 'w') as f:
        json.dump(classified_data, f, indent=2)
    print(f"Classification complete. Total classified: {len(classified_data)}")

if __name__ == "__main__":
    main()
