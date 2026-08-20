import sys
import os
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

def main():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY not found in environment.")
        return

    print("Scraping YouTube for Myntra haul comments...")
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # 1. Search for videos
    search_response = youtube.search().list(
        q="myntra clothing haul review",
        part="id,snippet",
        maxResults=10,
        type="video"
    ).execute()
    
    video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
    
    reviews = []
    # 2. Extract comments for each video
    for video_id in video_ids:
        try:
            comments_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                textFormat="plainText"
            ).execute()
            
            for item in comments_response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                text = comment['textDisplay']
                
                # filter out very short comments
                if len(text.split()) < 4:
                    continue
                    
                reviews.append({
                    "source_platform": "YouTube",
                    "source_url": f"https://www.youtube.com/watch?v={video_id}",
                    "date": comment.get('publishedAt', datetime.now().isoformat()),
                    "review_text": text,
                    "rating": None,
                    "author_name": comment.get('authorDisplayName', 'unknown')
                })
        except Exception as e:
            # Comments might be disabled for a video
            print(f"Skipping video {video_id}: {e}")
            
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
        print(f"Added {len(df_new)} YouTube comments. Total raw reviews now: {len(df_combined)}")
    else:
        print("No valid YouTube comments found.")

if __name__ == "__main__":
    main()
