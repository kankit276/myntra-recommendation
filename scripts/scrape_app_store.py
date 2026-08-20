import sys
import os
import pandas as pd
from app_store_scraper import AppStore
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

def main():
    print("Scraping App Store for Myntra...")
    # Myntra's App Store ID is 907394059
    myntra = AppStore(country="in", app_name="myntra-fashion-shopping-app", app_id="907394059")
    myntra.review(how_many=200)
    
    reviews = []
    for r in myntra.reviews:
        text = r.get("review")
        if not text or len(str(text).split()) < 3:
            continue
            
        reviews.append({
            "source_platform": "Apple App Store",
            "date": r.get("date", datetime.now()).isoformat() if hasattr(r.get("date"), "isoformat") else str(r.get("date", "")),
            "review_text": text,
            "rating": r.get("rating"),
            "author_name": r.get("userName")
        })
        
    df_new = pd.DataFrame(reviews)
    if not df_new.empty:
        os.makedirs(os.path.dirname(settings.RAW_DATA_PATH), exist_ok=True)
        if os.path.exists(settings.RAW_DATA_PATH):
            df_existing = pd.read_csv(settings.RAW_DATA_PATH)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.drop_duplicates(subset=["review_text"], inplace=True)
        else:
            df_combined = df_new
            
        df_combined.to_csv(settings.RAW_DATA_PATH, index=False)
        print(f"Added {len(df_new)} iOS reviews. Total raw reviews now: {len(df_combined)}")
    else:
        print("No valid App Store reviews found.")

if __name__ == "__main__":
    main()
