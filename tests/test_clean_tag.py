import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.clean_data import clean_dataframe
from scripts.tag_signals import tag_row

def test_cleaning():
    df = pd.DataFrame({
        "review_text": [
            "short", # < 10 chars
            "this is a very long and good review", 
            "short", # duplicate
            "another long review here",
            "just good" # < 10 chars
        ]
    })
    
    cleaned = clean_dataframe(df)
    assert len(cleaned) == 2
    assert "short" not in cleaned["review_text"].values

def test_tagging():
    assert tag_row("I added this to my wishlist yesterday") == "explicit"
    assert tag_row("I saved for later because I was unsure") == "implicit"
    assert tag_row("I just love this app") == "none_detected"
