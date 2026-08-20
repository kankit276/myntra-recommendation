import sys
import os
import pandas as pd
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

def main():
    print("Scraping Reddit via RSS...")
    url = "https://www.reddit.com/r/IndianFashionAddicts/search.rss?q=myntra+wishlist&restrict_sr=on"
    
    feed = feedparser.parse(url)
    
    reviews = []
    for entry in feed.entries:
        soup = BeautifulSoup(entry.summary, 'html.parser')
        text = soup.get_text(separator=' ').strip()
        full_text = f"{entry.title}. {text}"
        
        if len(full_text.split()) < 5:
            continue
            
        reviews.append({
            "source_platform": "Reddit",
            "source_url": entry.link,
            "date": entry.get("published", datetime.now().isoformat()),
            "review_text": full_text,
            "rating": None,
            "author_name": entry.get("author", "unknown_user")
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
        print(f"Added {len(df_new)} Reddit posts via RSS. Total raw reviews now: {len(df_combined)}")
    else:
        print("No valid Reddit posts found via RSS.")

if __name__ == "__main__":
    main()
