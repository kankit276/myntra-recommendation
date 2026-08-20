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

## Supported Data Sources
- Google Play Store
- Apple App Store
- Reddit
- YouTube

## Non-goals
- No live integrations with Myntra API
- No real-time scraping during demo to avoid scope creep
