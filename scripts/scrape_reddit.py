import os
import sys
import datetime
import pandas as pd
import praw

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import Review
from config.settings import settings

def scrape_reddit(subreddit_name="IndianFashionAddicts", search_query="myntra wishlist", limit=50):
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = "MyntraResearchBot/0.1"
    
    parsed_reviews = []
    if not client_id or not client_secret:
        print("Reddit API credentials not found in ENV. Skipping Reddit scrape.")
        return parsed_reviews
        
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.search(search_query, limit=limit):
            content = submission.title + " " + (submission.selftext or "")
            if len(content.split()) < 5:
                continue
                
            review_obj = Review(
                source_platform="reddit",
                source_url=submission.url,
                date=datetime.datetime.fromtimestamp(submission.created_utc).isoformat(),
                review_text=content,
                rating=None,
                country_language="IN/en"
            )
            parsed_reviews.append(review_obj.model_dump())
    except Exception as e:
        print(f"Error scraping Reddit: {e}")
        
    return parsed_reviews

def main():
    print(f"Scraping Reddit...")
    os.makedirs(os.path.dirname(settings.RAW_DATA_PATH), exist_ok=True)
    
    data = scrape_reddit()
    if not data:
        return
        
    df = pd.DataFrame(data)
    if os.path.exists(settings.RAW_DATA_PATH):
        existing_df = pd.read_csv(settings.RAW_DATA_PATH)
        df = pd.concat([existing_df, df], ignore_index=True)
        df.drop_duplicates(subset=["review_text"], inplace=True)
        
    df.to_csv(settings.RAW_DATA_PATH, index=False)
    print(f"Saved {len(data)} reddit posts to {settings.RAW_DATA_PATH}")

if __name__ == "__main__":
    main()
