import os
import sys
import pandas as pd
from google_play_scraper import reviews, Sort

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import Review
from config.settings import settings

def scrape_play_store(app_id="com.myntra.android", count=100):
    result, continuation_token = reviews(
        app_id,
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        count=count
    )
    
    parsed_reviews = []
    for r in result:
        # Focus on reviews with some meaningful text length
        if not r.get("content") or len(r["content"].split()) < 3:
            continue
            
        review_obj = Review(
            source_platform="google_play",
            source_url=f"https://play.google.com/store/apps/details?id={app_id}&reviewId={r['reviewId']}",
            date=r['at'].isoformat() if r.get('at') else "",
            review_text=r['content'],
            rating=r['score'],
            country_language="IN/en"
        )
        parsed_reviews.append(review_obj.model_dump())
        
    return parsed_reviews

def main():
    print(f"Scraping Google Play Store...")
    os.makedirs(os.path.dirname(settings.RAW_DATA_PATH), exist_ok=True)
    
    data = scrape_play_store(count=200)
    df = pd.DataFrame(data)
    
    if os.path.exists(settings.RAW_DATA_PATH):
        existing_df = pd.read_csv(settings.RAW_DATA_PATH)
        df = pd.concat([existing_df, df], ignore_index=True)
        df.drop_duplicates(subset=["review_text"], inplace=True)
        
    df.to_csv(settings.RAW_DATA_PATH, index=False)
    print(f"Saved {len(data)} reviews to {settings.RAW_DATA_PATH}")

if __name__ == "__main__":
    main()
