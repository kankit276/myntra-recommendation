import json
import os
import sys
from collections import defaultdict, Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

def map_frequency(percentage):
    if percentage < 0.05: return 1
    if percentage < 0.10: return 2
    if percentage < 0.15: return 3
    if percentage < 0.25: return 4
    return 5

def map_closeness(stage_counts):
    weights = {"browsing": 1, "saving": 2, "evaluating": 3, "ready_to_buy": 4, "abandoned": 5}
    total = sum(stage_counts.values())
    if total == 0: return 1
    weighted_sum = sum(count * weights.get(stage, 1) for stage, count in stage_counts.items())
    return round(weighted_sum / total)

def main():
    if not os.path.exists(settings.CLASSIFIED_DATA_PATH):
        print(f"File not found: {settings.CLASSIFIED_DATA_PATH}. Run classify.py first.")
        return

    with open(settings.CLASSIFIED_DATA_PATH, 'r') as f:
        data = json.load(f)
        
    total_reviews = len(data)
    if total_reviews == 0:
        print("No classified data found.")
        return
        
    barrier_stats = defaultdict(lambda: {
        "count": 0, 
        "stages": Counter(), 
        "segments": Counter(), 
        "quotes": [],
        "missing_info": Counter()
    })
    
    for item in data:
        barriers = item.get("purchase_barriers", [])
        if not isinstance(barriers, list):
            barriers = [barriers]
            
        stage = item.get("decision_stage", "unknown")
        segment = item.get("user_segment_clues", "")
        quote = item.get("key_quote", "")
        missing = item.get("missing_information", [])
        if not isinstance(missing, list):
            missing = [missing]
            
        for b in barriers:
            if b == "not_applicable": continue
            stats = barrier_stats[b]
            stats["count"] += 1
            stats["stages"][stage] += 1
            if segment and segment != "not_applicable":
                stats["segments"][segment] += 1
            if quote and quote != "not_applicable":
                stats["quotes"].append({"quote": quote, "url": item.get("source_url")})
            for m in missing:
                if m != "not_applicable":
                    stats["missing_info"][m] += 1

    opportunities = []
    for barrier, stats in barrier_stats.items():
        freq_pct = stats["count"] / total_reviews
        freq_score = map_frequency(freq_pct)
        closeness_score = map_closeness(stats["stages"])
        
        severity_score = 4
        segment_clarity = 3
        non_discount_solvability = 5 if barrier != "price_concern" else 2
        
        total_score = freq_score * severity_score * closeness_score * segment_clarity * non_discount_solvability
        normalized_score = min(100, round((total_score / (5*5*5*5*5)) * 100))
        
        top_segment = stats["segments"].most_common(1)[0][0] if stats["segments"] else "General"
        top_missing = stats["missing_info"].most_common(3)
        
        opp = {
            "name": barrier.replace("_", " ").title(),
            "barrier_id": barrier,
            "score": normalized_score,
            "components": {
                "frequency": freq_score,
                "severity": severity_score,
                "closeness": closeness_score,
                "segment_clarity": segment_clarity,
                "non_discount_solvability": non_discount_solvability
            },
            "matching_count": stats["count"],
            "percentage": round(freq_pct * 100, 1),
            "top_segment": top_segment,
            "missing_info": [m[0] for m in top_missing],
            "evidence": stats["quotes"][:5]
        }
        opportunities.append(opp)
        
    opportunities.sort(key=lambda x: x["score"], reverse=True)
    
    os.makedirs(os.path.dirname(settings.OPPORTUNITIES_PATH), exist_ok=True)
    with open(settings.OPPORTUNITIES_PATH, 'w') as f:
        json.dump(opportunities, f, indent=2)
        
    print(f"Aggregated {len(opportunities)} opportunities. Saved to {settings.OPPORTUNITIES_PATH}")

if __name__ == "__main__":
    main()
