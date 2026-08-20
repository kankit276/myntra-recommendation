from pydantic import BaseModel
from typing import Optional, List

class Review(BaseModel):
    source_platform: str
    source_url: str
    date: str
    review_text: str
    product_mentioned: str = "general"
    rating: Optional[int] = None
    country_language: Optional[str] = None

class ClassifiedReview(BaseModel):
    save_reason: str
    purchase_barriers: List[str]
    missing_information: List[str]
    decision_stage: str
    external_behaviour: List[str]
    user_segment_clues: str
    signal_confidence: str
    key_quote: str
    insight_summary: str
