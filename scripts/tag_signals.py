import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

EXPLICIT_KEYWORDS = ["wishlist", "wishlisted", "wish list", "added to wishlist", "in my wishlist", "save to wishlist"]
IMPLICIT_KEYWORDS = ["saved for later", "bookmarked", "keeping an eye on", "might get it later", "waiting for sale", "added to cart", "shortlisted", "waiting for price drop", "still deciding"]

def tag_row(text):
    text_lower = str(text).lower()
    
    for kw in EXPLICIT_KEYWORDS:
        if kw in text_lower:
            return "explicit"
            
    for kw in IMPLICIT_KEYWORDS:
        if kw in text_lower:
            return "implicit"
            
    return "none_detected"

def main():
    cleaned_path = settings.DATA_DIR / "cleaned_reviews_temp.csv"
    if not os.path.exists(cleaned_path):
        print(f"Cleaned data not found at {cleaned_path}. Run clean_data.py first.")
        return
        
    df = pd.read_csv(cleaned_path)
    print(f"Tagging {len(df)} reviews...")
    
    df["signal_type"] = df["review_text"].apply(tag_row)
    
    explicit_count = (df["signal_type"] == "explicit").sum()
    implicit_count = (df["signal_type"] == "implicit").sum()
    none_count = (df["signal_type"] == "none_detected").sum()
    
    print(f"Tagging complete. Explicit: {explicit_count}, Implicit: {implicit_count}, None detected: {none_count}")
    
    df.to_csv(settings.CLEAN_DATA_PATH, index=False)
    print(f"Saved tagged data to {settings.CLEAN_DATA_PATH}")
    
    # Optionally remove the temp file
    if os.path.exists(cleaned_path):
        os.remove(cleaned_path)

if __name__ == "__main__":
    main()
