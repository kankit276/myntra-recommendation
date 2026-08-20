import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.prompts import build_system_prompt, build_user_prompt

def test_system_prompt():
    prompt = build_system_prompt("Myntra")
    assert "Myntra" in prompt
    assert "TAXONOMY:" in prompt
    assert "save_reason:" in prompt
    assert "not_applicable" in prompt

def test_user_prompt():
    prompt = build_user_prompt("Great app", "google_play", "http://x.com", "2026", 5)
    assert "google_play" in prompt
    assert "Great app" in prompt
    assert "http://x.com" in prompt
