import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import Review

def test_review_schema_parsing():
    data = {
        "source_platform": "google_play",
        "source_url": "http://example.com",
        "date": "2026-08-20T10:00:00",
        "review_text": "I really like this app but the wishlist needs work.",
        "rating": 4
    }
    
    review = Review(**data)
    
    assert review.source_platform == "google_play"
    assert review.rating == 4
    assert review.product_mentioned == "general" # Test default value
    assert "wishlist needs work" in review.review_text
