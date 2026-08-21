import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

def normalize_segment(text):
    if not text:
        return "General/Unknown"
        
    t = str(text).lower()
    
    if t in ["", "none", "not_applicable", "none observed", "n/a"]:
        return "General/Unknown"
        
    if any(k in t for k in ["price", "budget", "cheap", "affordable", "expensive", "cost", "sale", "discount"]):
        return "Budget-Conscious Shopper"
        
    if any(k in t for k in ["size", "fit", "height", "weight", "body", "tall", "short", "plus size", "measurements"]):
        return "Size/Fit-Conscious Shopper"
        
    if any(k in t for k in ["occasion", "wedding", "festival", "diwali", "party", "gift", "event"]):
        return "Occasion Shopper"
        
    if any(k in t for k in ["quality", "authentic", "material", "fabric", "brand conscious", "premium"]):
        return "Quality/Brand-Conscious Shopper"
        
    if any(k in t for k in ["frustrated", "support", "refund", "return", "scam", "fake", "issue", "worst", "disappointed", "angry", "terrible", "bad experience"]):
        return "Frustrated/Support-Seeking Shopper"
        
    if any(k in t for k in ["frequent", "regular", "repeat", "loyal", "heavy user", "active"]):
        return "Frequent/Loyal Shopper"
        
    if any(k in t for k in ["first time", "new user"]):
        return "First-Time Shopper"
        
    return "General/Unknown"

def main():
    path = settings.CLASSIFIED_DATA_PATH
    if not os.path.exists(path):
        print("Data file not found.")
        return
        
    with open(path, 'r') as f:
        data = json.load(f)
        
    for row in data:
        raw_segment = row.get("user_segment_clues", "")
        row["user_segment_clues"] = normalize_segment(raw_segment)
        
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Normalized segments for {len(data)} rows.")

if __name__ == "__main__":
    main()
