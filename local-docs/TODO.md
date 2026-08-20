# Project Enhancements & TODOs

## Data Acquisition Enhancements
- [x] **Reddit Scraper (Unauthenticated/RSS)**: Since PRAW API keys can take days to get approved, implement an RSS-based scraper for Reddit using `requests` and `feedparser` (e.g., pulling from `reddit.com/r/IndianFashionAddicts/search.rss?q=myntra`).
- [ ] **Apify Integration**: Alternatively, use Apify to download Reddit or Instagram conversations, and write a small script to parse Apify JSON exports into our `models/schemas.py` format.
- [x] **YouTube Comments**: Add a YouTube scraper using the Google API Python client to pull comments from Myntra clothing haul videos. (YouTube API keys are instant to generate).
- [x] **App Store (iOS) Reviews**: Integrate `app-store-scraper` to pull reviews from the Apple App Store to complement the Android Play Store data.

## Processing Enhancements
- [x] **Fuzzy Deduplication**: The current deduplication only drops exact text matches. Implement fuzzy matching (e.g., using `thefuzz` library) to catch similar spam reviews instead of just exact matches.
- [x] **Batching LLM Calls**: Currently we process reviews one by one. If we move to a model that supports large context efficiently, we could batch 10-20 reviews per prompt to save execution time.
- [x] **Async Requests**: Use `asyncio` and an async LLM client in `scripts/classify.py` to speed up the classification phase by processing multiple reviews concurrently.
