import sys
import os
import pandas as pd
from thefuzz import fuzz

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

def fuzzy_deduplicate(df, threshold=90):
    print("Running fuzzy deduplication... this might take a moment.")
    texts = df['review_text'].tolist()
    to_drop = set()
    
    for i in range(len(texts)):
        if i in to_drop:
            continue
        for j in range(i + 1, len(texts)):
            if j in to_drop:
                continue
            if abs(len(str(texts[i])) - len(str(texts[j]))) > 50:
                continue
                
            ratio = fuzz.ratio(str(texts[i]).lower(), str(texts[j]).lower())
            if ratio >= threshold:
                to_drop.add(j)
                
    drop_count = len(to_drop)
    print(f"Fuzzy matching caught {drop_count} near-duplicate spam reviews.")
    return df.drop(index=list(to_drop)).reset_index(drop=True)

def main():
    if not os.path.exists(settings.RAW_DATA_PATH):
        print(f"No raw data found at {settings.RAW_DATA_PATH}")
        return

    df = pd.read_csv(settings.RAW_DATA_PATH)
    initial_count = len(df)
    
    # Basic cleaning
    df = df.dropna(subset=['review_text'])
    df['review_text'] = df['review_text'].astype(str).str.strip()
    df = df[df['review_text'].str.len() > 10]
    df = df.drop_duplicates(subset=['review_text'])
    
    # Fuzzy deduplication
    df = fuzzy_deduplicate(df, threshold=90)
    
    final_count = len(df)
    print(f"Cleaned {initial_count} rows down to {final_count} rows.")
    
    os.makedirs(os.path.dirname(settings.CLEAN_DATA_PATH), exist_ok=True)
    df.to_csv(settings.CLEAN_DATA_PATH, index=False)
    print(f"Clean data saved to {settings.CLEAN_DATA_PATH}")

if __name__ == "__main__":
    main()
