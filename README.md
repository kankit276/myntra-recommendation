# AI-Powered Discovery Engine (Myntra Use Case)

This project is an AI-powered discovery engine for Myntra to analyze user feedback at scale, specifically focusing on identifying why users add items to their wishlists but do not purchase them. It translates raw feedback from various sources into structured insights, opportunity rankings, and barrier frequencies.

## Architecture & Phases
This project is built phase-wise:
- **Phase 0:** Scope and foundations (Config & Taxonomy)
- **Phase 1:** Data ingestion and canonical model (Scraping)
- **Phase 2:** Normalization and validation (Cleaning & Tagging)
- **Phase 3:** Integration layer (Retrieval + Prompt assembly)
- **Phase 4:** Recommendation engine (LLM classification)
- **Phase 5:** Output and experience (Analytics & Aggregation)
- **Phase 6:** Frontend (Streamlit UI)

## Stack
- Python
- Streamlit
- Pydantic
- python-dotenv

## Setup
1. Clone the repository
2. Create a virtual environment and install dependencies (e.g. `pip install -r requirements.txt`)
3. Copy `.env.example` to `.env` and fill in your chosen API keys (Groq, Gemini, or OpenAI)
4. Execute the phases step-by-step.

## How to Run the Project

You can execute the pipeline step-by-step from data acquisition to the final UI.

### 1. Data Collection (Scraping)
Run any of the scrapers to pull raw reviews. The output is saved to `data/raw_reviews.csv`.
```bash
python scripts/scrape_google_play.py
python scripts/scrape_app_store.py
python scripts/scrape_youtube.py
python scripts/scrape_reddit.py
```

### 2. Data Cleaning & Tagging
Clean the raw data (deduplication, spam filtering) and tag implicit/explicit signals. This generates `data/tagged_reviews.csv`.
```bash
python scripts/clean_data.py
python scripts/tag_signals.py
```

### 3. AI Classification
Process the tagged reviews through the LLM to extract the 7-dimension taxonomy. The output is saved to `data/classified.json`.
*(Ensure your API keys are set in `.env`)*
```bash
python scripts/classify.py
```

### 4. Aggregation & Scoring
Aggregate the LLM output into quantified, scored opportunity areas. This generates `data/opportunities.json`.
```bash
python scripts/normalize_segments.py  # Optional: cleans up free-text segments
python scripts/aggregate.py
```

### 5. Launch the Dashboard
Run the Streamlit web app to visualize the final Discovery Engine.
```bash
streamlit run app.py
```

## Supported Data Sources
- Google Play Store
- Apple App Store
- Reddit
- YouTube

## Non-goals
- No live integrations with Myntra API
- No real-time scraping during demo to avoid scope creep
