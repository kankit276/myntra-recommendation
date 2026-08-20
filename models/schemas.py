from pydantic import BaseModel
from typing import Optional

class Review(BaseModel):
    source_platform: str
    source_url: str
    date: str
    review_text: str
    product_mentioned: str = "general"
    rating: Optional[int] = None
    country_language: Optional[str] = None
