import requests
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from utils.retry import retry

class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"

    @retry((Exception,), tries=3, delay=2, backoff=2)
    def generate_json(self, system_prompt, user_prompt):
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json"
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
            
        result = response.json()
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected API response format: {result}")
