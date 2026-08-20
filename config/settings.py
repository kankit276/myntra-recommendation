import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME = "Myntra Discovery Engine"
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Base directories
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    CONFIG_DIR = BASE_DIR / "config"
    
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Data paths
    RAW_DATA_PATH = DATA_DIR / "raw_reviews.csv"
    CLEAN_DATA_PATH = DATA_DIR / "tagged_reviews.csv"
    CLASSIFIED_DATA_PATH = DATA_DIR / "classified.json"
    OPPORTUNITIES_PATH = DATA_DIR / "opportunities.json"
    
    # Config paths
    TAXONOMY_PATH = CONFIG_DIR / "taxonomy.json"

settings = Settings()
