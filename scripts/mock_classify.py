import json
import os
import sys
import pandas as pd
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from config.prompts import load_taxonomy

def main():
    if not os.path.exists(settings.CLEAN_DATA_PATH):
        print(f"File not found: {settings.CLEAN_DATA_PATH}. Run clean_data.py first.")
        return
        
    df = pd.read_csv(settings.CLEAN_DATA_PATH)
    taxonomy = load_taxonomy()
    
    classified_data = []
    
    segments = ["occasion shopper", "budget-conscious college student", "first-time buyer", "size-sensitive shopper", "trend-led shopper", "not_applicable"]
    
    for idx, row in df.iterrows():
        # Generate some dummy but plausible data based on the taxonomy
        barrier = random.choice(taxonomy["purchase_barriers"])
        missing = random.sample(taxonomy["missing_information"], k=random.randint(1, 2))
        ext_beh = random.sample(taxonomy["external_behaviour"], k=random.randint(0, 1))
        
        combined = {
            "source_platform": row["source_platform"],
            "source_url": row.get("source_url", f"https://example.com/review/{idx}"),
            "date": row["date"],
            "review_text": row["review_text"],
            "rating": row["rating"],
            "signal_type": row.get("signal_type", "none_detected"),
            
            "save_reason": random.choice(taxonomy["save_reason"]),
            "purchase_barriers": [barrier],
            "missing_information": missing,
            "decision_stage": random.choice(taxonomy["decision_stage"]),
            "external_behaviour": ext_beh,
            "user_segment_clues": random.choice(segments),
            "signal_confidence": random.choice(["high", "medium", "low"]),
            "key_quote": row["review_text"][:50] + "..." if len(str(row["review_text"])) > 50 else row["review_text"],
            "insight_summary": f"User is hesitating due to {barrier}."
        }
        classified_data.append(combined)
        
    os.makedirs(os.path.dirname(settings.CLASSIFIED_DATA_PATH), exist_ok=True)
    with open(settings.CLASSIFIED_DATA_PATH, 'w') as f:
        json.dump(classified_data, f, indent=2)
        
    print(f"Mock Classification complete. Total mock classified: {len(classified_data)}")

if __name__ == "__main__":
    main()
