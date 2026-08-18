# AI-Powered Discovery Engine (Myntra Use Case)

## Problem Statement

You are tasked with building an AI-powered discovery engine for Myntra to analyze user feedback at scale. Millions of users add fashion products to their wishlists, but only a small proportion eventually purchase them. The engine must intelligently analyze public conversations and reviews to identify, quantify, and compare potential opportunity areas that could increase the wishlist-to-purchase conversion rate within 30 days, without offering monetary incentives.

## Objective

Design and implement an application that:
- Takes raw, unstructured public reviews and feedback from multiple sources (Play Store, App Store, Reddit, YouTube, Q&A).
- Uses a real-world dataset scraped specifically for Myntra.
- Leverages an LLM to generate structured, personalized insights (reasons for saving, barriers to purchase, decision stage).
- Displays clear and useful analytical results (opportunity rankings, barrier frequencies, metric trees) to the Product Manager user.

## System Workflow

1. **Data Ingestion**
   - Scrape reviews from Google Play, App Store, Reddit, and YouTube focusing on "Myntra".
   - Extract relevant fields such as source platform, date, review text, and product mentioned.
2. **Pre-processing & Tagging**
   - Clean data, remove spam, and perform deduplication.
   - Tag signals using keywords to identify implicit vs. explicit wishlist behaviors.
3. **Integration Layer**
   - Filter and prepare relevant raw data based on cleanliness.
   - Pass structured results into an LLM prompt.
   - Design a prompt that helps the LLM extract 7 dimensions of insights (barriers, stage, etc.).
4. **Classification & Analytics Engine**
   - Use the LLM to classify feedback into structured JSON.
   - Aggregate frequencies of barriers and intents.
   - Use a 5-factor scoring model to rank opportunities.
5. **Output Display**
   - Present top recommendations in a user-friendly format via a Web UI:
     - Hero statistics
     - Opportunity rankings with scores
     - Barrier frequencies
     - Metric Trees (Treemap)

---

## Architecture

## Phase-wise architecture: Myntra Discovery Engine

This document breaks the build into phases that map to the workflow: data ingestion → pre-processing → integration (filter + prompt prep) → LLM classification → output display.

### Phase 0 — Scope and foundations
| Item | Outcome |
|---|---|
| **Product slice** | Basic web UI — primary presentation of results and opportunities; CLI remains for dev/diagnostics/scraping. |
| **Stack** | Python, Streamlit, Pydantic, python-dotenv for secrets (.env for API keys, never committed). |
| **Dataset contract** | Support fields: `source_platform`, `review_text`, `rating`, `date`. |
| **Non-goals** | Explicitly defer live integrations with Myntra API and real-time scraping during demo to avoid scope creep. |
| **Exit criteria** | Written assumptions (stack, v1 UI, supported sources) and a local way to run the app end-to-end once later phases exist. |
| **Implemented artifacts** | `config/taxonomy.json`, `config/settings.py`, `repo README.md`, `.env.example`. |

### Phase 1 — Data ingestion and canonical model
| Layer | Responsibility |
|---|---|
| **Acquisition** | Download or stream from Google Play, App Store, Reddit, and YouTube. |
| **Normalization** | Clean types (ratings as numbers), handle missing values. |
| **Canonical schema** | Internal `Review` schema with: source, text, rating, date. |
| **Exit criteria** | A single module (or package) that loads data and outputs a standardized CSV collection; unit tests on parsing for a few sample rows. |
| **Implemented** | `scripts/scrape_google_play.py`, `scripts/scrape_reddit.py`, etc. |

### Phase 2 — Normalization and validation
| Component | Responsibility |
|---|---|
| **Preference model** | Structured fields: implicit vs explicit signals. |
| **Validation** | Reject or coerce invalid input (spam, < 10 chars); clear error messages. |
| **Exit criteria** | Data is cleaned, deduplicated, and outputted as `tagged_reviews.csv`; validation errors are user-visible. |
| **Implemented** | `scripts/clean_data.py`, `scripts/tag_signals.py`. |

### Phase 3 — Integration layer (retrieval + prompt assembly)
| Component | Responsibility |
|---|---|
| **Deterministic filter** | Apply hard filters first: only pass reviews that meet length and language requirements. |
| **Prompt builder** | System + user messages including: dynamic taxonomy from `taxonomy.json`, candidate table as JSON, instructions to extract 7 dimensions. |
| **Exit criteria** | Given scraped data, produce a stable prompt payload without calling the LLM yet. |
| **Implemented** | `config/prompts.py`, `models/schemas.py`. |

### Phase 4 — Recommendation engine (LLM)
| Concern | Approach |
|---|---|
| **Model I/O** | Thin client (`utils/llm_client.py`): temperature, max tokens, inject API key from environment. |
| **Structured output** | Ask for JSON (7 dimensions of analysis) — then parse and validate using Pydantic. |
| **Resilience** | Retry on transient errors; checkpoint and resume every 25 rows. |
| **Exit criteria** | End-to-end call returns classified items; parser validates structure; failures degrade gracefully. |
| **Implemented** | `scripts/classify.py`, `utils/retry.py`. |

### Phase 5 — Output and experience (Analytics)
| Surface | Responsibility |
|---|---|
| **Rendering** | For each opportunity: name, score, barrier frequency, AI explanation. |
| **Empty states** | "No reviews match filters" vs "LLM could not classify". |
| **Observability (light)**| Log latency, token usage, and filter counts. |
| **Exit criteria** | End-to-end readable output + telemetry; ranked opportunities JSON generated (`opportunities.json`). |
| **Implemented** | `scripts/aggregate.py`, `utils/logger.py`. |

### Phase 6 — Frontend (web UI)
| Concern | Approach |
|---|---|
| **Role** | Primary user-facing surface: sidebar filters + results dashboard. |
| **Data flow** | Browser talks to pre-computed JSONs via `@st.cache_data`. |
| **UI** | Results show Hero stats, Treemaps, Sankey charts, and Opportunities. |
| **UX** | Loading states, validation errors inline. |
| **Stack** | Streamlit (SPA equivalent in Python). Host locally for milestone 1. |
| **Exit criteria** | One demo path in the README: start UI, see ranked results or intentional empty state. |
| **Implemented** | `app.py`, `components/*.py`. |

---

## STEPS

- STEP 1 → Created a doc folder inside which we added `requirements.md` and `deliverable_1_approach_v2.md`
- STEP 2 → Generating the architecture
- STEP 3 → Generating the edge cases and taxonomy
- STEP 4 → Implement phase0 as per the `phased-architecture.md` (config files)
- STEP 5 → Implement phase1 in the separate folder as per the `phased-architecture.md` (scrapers)
- STEP 6 → Run phase1 so that data is downloaded
- STEP 7 → Implement phase2 as per the `phased-architecture.md` (clean and tag)
- STEP 8 → Implement phase3 as per the `phased-architecture.md` (prompts and schemas)
- STEP 9 → Implement phase4 as per the `phased-architecture.md`, LLM used in this phase will be Gemini/Groq.

**STEPs for creating API KEY on Gemini / Groq →**
- Create account on Groq https://groq.com/ or Google AI Studio
- Created an API KEY
- Add API key in ENV file: Create an `.env` file YOURSELF (`GROQ_API_KEY = <api-key>`)

- STEP 10 → Test phase4 with a live example and calibration batch.
- STEP 11 → Update the architecture after phase5 so that proper backend and frontend we have for this project.
- STEP 12 → Implement phase6 as per the `phased-architecture.md` (Streamlit UI).

---

## Prompts

- Prompt 1 → Write @docs/requirements.md in better way
- Prompt 2 → Create a phase-wise architecture for this @docs/requirements.md
- Prompt 3 → Generate the detailed edge cases and taxonomy for this project using @docs/requirements.md and @docs/phased-architecture.md
- Prompt 4 → Implement phase0 as per the @docs/phased-architecture.md
- Prompt 5 → Implement phase1 in the separate folder as per the @docs/phased-architecture.md
- Prompt 6 → Run phase1 so that data is downloaded
- Prompt 7 → Implement phase2 in the separate folder as per the @docs/phased-architecture.md
- Prompt 8 → Implement phase3 as per the @docs/phased-architecture.md in the separate folder
- Prompt 9 → Implement phase4 as per the @docs/phased-architecture.md in the separate folder, LLM used in this phase will be Gemini.
- Prompt 10 → Test phase4 with a live calibration batch of 20 reviews.
- Prompt 11 → Run the above command and tell me exact output from LLM.
- Prompt 12 → Implement phase5 (aggregation) as per the @docs/phased-architecture.md
- Prompt 13 → Implement phase6 (frontend) as per the @docs/phased-architecture.md in Streamlit.
- Prompt 14 → Run the frontend `streamlit run app.py` and test it locally.
- Prompt 15 → In frontend, add dynamic filtering in the sidebar.
- Prompt 16 → Stop backend and frontend.
- Prompt 17 → How can we deploy this project using free tools?
- Prompt 18 → In @docs/phased-architecture.md add one more phase for deployment.

---

## FRONTEND frameworks
- Streamlit (Primary choice for this project)
- Next.js (Alternative for advanced web app)
- React.js / Vite

Designing Tools →
- https://stitch.withgoogle.com/
- https://godly.website/

---

## OTHER AI TOOLS (If limits are exhausted)
- Cursor
- Google Antigravity
- Windsurf
- Qoder

---

## Deployment
- Develop it locally (in your PC)
- Push the code to Github
- Actual Deployment (Currently we have planned deployment on Streamlit Community Cloud)

**Tools**
- https://share.streamlit.io/ (Streamlit Community Cloud)
- https://dashboard.render.com/ (Backend - if separated)
- https://vercel.com/ (Frontend - if using Next.js)

**Two deployment Prompt (If migrating off Streamlit):**
- We don't want to deploy on Streamlit, we want two deployments: backend on render and frontend on vercel. First we can remove Streamlit changes and then we can generate a deployment plan for render and VERCEL.
- Do backend changes of render/railway as per the deployment docs.
- Do frontend changes for vercel as per the deployment docs.

**STEPS for Streamlit deployment:**
- Push these files to GitHub.
- Go to Streamlit Community Cloud → New app → pick the repo.
- Add Secrets in the Advanced Settings (API Keys).
- Deploy.

**How to be on track**
- https://www.youtube.com/@AndrejKarpathy
- https://www.youtube.com/@nicksaraev
- https://www.youtube.com/@nateherk
- Anthropic (Linkedin)
