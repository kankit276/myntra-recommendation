import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

def load_taxonomy():
    with open(settings.TAXONOMY_PATH, 'r') as f:
        return json.load(f)

def build_system_prompt(product_name="Myntra"):
    taxonomy = load_taxonomy()
    
    save_reasons = " | ".join(taxonomy["save_reason"])
    purchase_barriers = ", ".join(taxonomy["purchase_barriers"])
    missing_info = ", ".join(taxonomy["missing_information"])
    decision_stage = " | ".join(taxonomy["decision_stage"])
    external_behavior = ", ".join(taxonomy["external_behaviour"])
    
    prompt = f"""You are an expert user researcher analyzing public reviews and comments about
online fashion shopping in India, specifically about {product_name}.

Your task is to extract structured signals related to wishlist behaviour and
purchase decision-making. Focus on understanding WHY users save items and
what PREVENTS them from purchasing.

For each comment, extract the following fields. Use ONLY the categories
listed. If a field does not apply, use "not_applicable". A comment may have
multiple barriers, multiple missing-information items, and multiple
external behaviours.

TAXONOMY:
- save_reason: {save_reasons}
- purchase_barriers: [{purchase_barriers}] (multi-select, or ["not_applicable"])
- missing_information: [{missing_info}] (multi-select, or ["not_applicable"])
- decision_stage: {decision_stage}
- external_behaviour: [{external_behavior}] (multi-select, or ["not_applicable"])
- user_segment_clues: free text describing any observable user characteristics
- signal_confidence: high | medium | low
- key_quote: the most relevant 1-2 sentence excerpt, verbatim
- insight_summary: a one-sentence insight in your own words

Return your response as a JSON object matching the exact keys above. Do not include markdown formatting or backticks around the JSON.
"""
    return prompt

def build_user_prompt(review_text, platform, source_url, date, rating):
    return f"""Analyze the following review from {platform}:

---
"{review_text}"
---

Source URL: {source_url}
Date: {date}
Rating: {rating}
"""
