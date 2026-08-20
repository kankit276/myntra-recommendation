# Phase Implementation Log

## Phase 0: Scope and Foundations
- **Objective**: Set up the project structure, configuration, and taxonomies.
- **What was done**:
  - Created `config/taxonomy.json` containing the 7 dimensions (save reasons, barriers, missing info, etc.) from the architecture doc.
  - Created `config/settings.py` to securely load API keys and paths using `pydantic` and `python-dotenv`.
  - Created `.env.example` as a template for API keys.
  - Updated `README.md` with setup instructions.

## Phase 1: Data Ingestion and Canonical Model
- **Objective**: Pull raw data from public sources and standardize it.
- **What was done**:
  - Defined the `Review` canonical schema in `models/schemas.py`.
  - Created `scripts/scrape_google_play.py` to pull reviews from the Myntra Android app using `google-play-scraper`. (Successfully scraped 113 reviews).
  - Created `scripts/scrape_reddit.py` using `praw` (currently designed to gracefully skip if no API keys are present).
  - Wrote unit tests in `tests/test_scrapers.py`.

## Phase 2: Normalization and Validation
- **Objective**: Clean the scraped data and tag implicit/explicit wishlist signals.
- **What was done**:
  - Created `scripts/clean_data.py` to remove duplicate reviews and reviews under 10 characters (spam filtering).
  - Created `scripts/tag_signals.py` to tag explicit ("added to wishlist") and implicit ("saved for later") signals based on keyword matching.
  - Wrote unit tests in `tests/test_clean_tag.py`.
  - Processed the 113 raw reviews to generate `data/tagged_reviews.csv`.

## Phase 3: Integration Layer (Prompt Assembly)
- **Objective**: Dynamically build prompts based on the taxonomy for the LLM.
- **What was done**:
  - Created `config/prompts.py` with two functions: `build_system_prompt()` (which reads from `taxonomy.json`) and `build_user_prompt()`.
  - Wrote unit tests in `tests/test_prompts.py`.

## Phase 4: Recommendation Engine (LLM Classification)
- **Objective**: Feed the cleaned data into an LLM to extract the 7 dimensions.
- **What was done**:
  - Defined the `ClassifiedReview` schema in `models/schemas.py`.
  - Created `utils/retry.py` for exponential backoff on API failures.
  - Built `utils/llm_client.py` configured for Google's `gemini-1.5-flash` model via `google-generativeai`.
  - Wrote `scripts/classify.py` to loop through the tagged reviews, query the LLM, validate output using Pydantic, and checkpoint every 25 rows to `data/classified.json`.

## Phase 5: Output and experience (Analytics)
- **Objective**: Aggregate the LLM classifications and generate ranked opportunities.
- **What was done**:
  - Created `scripts/aggregate.py` to calculate opportunity scores based on the 5-factor model (Frequency, Severity, Closeness, Segment Clarity, Non-discount Solvability).
  - Built mapping logic for frequencies and decision stages to numeric scores (1-5).
  - Exported the final ranked JSON to `data/opportunities.json` for the frontend.
  - (Note: Added `mock_classify.py` fallback to unblock development when preview API models lacked text generation support).
