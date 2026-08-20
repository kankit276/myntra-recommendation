import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

def clean_dataframe(df):
    initial_count = len(df)
    
    # Drop duplicates
    df = df.drop_duplicates(subset=["review_text"])
    dedup_count = len(df)
    print(f"Removed {initial_count - dedup_count} duplicates.")
    
    # Filter short strings (spam, < 10 chars)
    df = df.dropna(subset=["review_text"])
    df["review_length"] = df["review_text"].astype(str).str.len()
    
    invalid_mask = df["review_length"] < 10
    invalid_count = invalid_mask.sum()
    print(f"Validation: Removed {invalid_count} reviews with < 10 characters (too short/spam).")
    
    df = df[~invalid_mask].copy()
    df = df.drop(columns=["review_length"])
    
    return df

def main():
    if not os.path.exists(settings.RAW_DATA_PATH):
        print(f"File not found: {settings.RAW_DATA_PATH}")
        return
        
    df = pd.read_csv(settings.RAW_DATA_PATH)
    print(f"Loaded {len(df)} raw reviews.")
    
    cleaned_df = clean_dataframe(df)
    
    cleaned_path = settings.DATA_DIR / "cleaned_reviews_temp.csv"
    cleaned_df.to_csv(cleaned_path, index=False)
    print(f"Saved {len(cleaned_df)} cleaned reviews to {cleaned_path}")

if __name__ == "__main__":
    main()
