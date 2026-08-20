import google.generativeai as genai
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from utils.retry import retry

class GeminiClient:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")
        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash as default, since it's fast and cheap 
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    @retry((Exception,), tries=3, delay=2, backoff=2)
    def generate_json(self, system_prompt, user_prompt):
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = self.model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                response_mime_type="application/json"
            )
        )
        return response.text
