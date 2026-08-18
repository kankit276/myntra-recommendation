# Deliverable 1: AI-Powered Discovery Engine (v2)

## What this deliverable means

The first deliverable is a **testable AI-powered research system**, not just a spreadsheet of reviews or a chatbot that summarizes them.

The requirements ask for two things:

1. A public link to an AI Discovery Engine that a reviewer can test.
2. One slide in the final 10-slide deck explaining how the engine works.

The `[Link]` in the requirements is only a placeholder. You must create and deploy the link yourself. You do not need to have the final product solution ready at this stage. The purpose of the engine is to **discover and rank the right user problem** before conducting interviews.

> **Remember:** The engine is a means to an end. Its job is to produce defensible hypotheses for user interviews (Part 3). Optimize for credible, well-evidenced opportunity identification, not for engine sophistication.

---

## Step 0: Product — Myntra (confirmed)

**Myntra** is the chosen product for this project. Key advantages:

- **Highest public data volume** — largest user base, most Play Store reviews, most Reddit mentions
- **Mature wishlist feature** — includes notifications, price-drop alerts
- **Easiest interviewee recruitment** — most widely used among 18–35 demographics
- **Strong Reddit/YouTube coverage** — dedicated subreddit activity, many haul videos
- **Scale and marketplace breadth** — diverse competitive differentiation angle

---

## Step 1: Collect the data

### Target volume

Aim for **250–500 usable comments** spread across at least three source types. Quality matters more than quantity — 300 well-cleaned comments outweigh 1,000 noisy ones.

### Data collection toolkit

| Source | Tool | Volume Target | Notes |
|---|---|---|---|
| Google Play Store | `google-play-scraper` (npm) or Apify actor | 100–200 reviews | Filter to reviews mentioning shopping, wishlist, size, fit, quality, delivery |
| Apple App Store | `app-store-scraper` (npm) or Apify actor | 50–100 reviews | Smaller volume but often more detailed |
| Reddit | PRAW (Python) or manual search on r/IndianFashionAddicts, r/India | 50–100 posts/comments | Search terms: "myntra" + "wishlist", "saved for later", "didn't buy", "size", "return" |
| YouTube | YouTube Data API v3 or manual extraction | 30–50 comments | Focus on haul videos, review videos, sizing guides, return experience videos |
| Twitter/X | Search export, Apify, or manual screenshots | 20–50 posts | Search product name + shopping-related keywords |
| Product Q&A | Manual collection from the app/website | 20–30 entries | Captures pre-purchase questions directly |

### Schema for each record

Store every record with these fields:

```
source_platform     : string   (e.g., "google_play", "reddit", "youtube")
source_url          : string   (direct link to the original comment/post)
date                : string   (ISO date, e.g., "2026-03-15")
review_text         : string   (full text of the comment)
product_mentioned   : string   (specific product name if mentioned, else "general")
rating              : integer  (1–5 if available, null otherwise)
country_language    : string   (e.g., "IN/en", if detectable)
```

### Handling implicit wishlist signals

Most public reviews and Reddit posts **do not explicitly mention "wishlist."** You must identify implicit wishlist-adjacent behaviours through proxy signals.

**Keywords and phrases indicating wishlist-like behaviour:**

| Signal type | Example phrases |
|---|---|
| Explicit wishlist | "added to wishlist", "in my wishlist", "wishlisted it" |
| Save/bookmark | "saved for later", "bookmarked", "keeping an eye on" |
| Deferred purchase | "was thinking of buying", "might get it later", "still deciding" |
| Cart abandonment | "added to cart but didn't checkout", "left it in cart" |
| Price watching | "waiting for sale", "too expensive right now", "checking price" |
| Comparison | "choosing between X and Y", "can't decide", "shortlisted" |
| Fit/size hesitation | "not sure about the size", "wish I could try it on" |
| Event planning | "need it for a wedding", "looking for something for Diwali" |

Tag each comment with `signal_type: explicit | implicit` so analysis can be filtered or weighted accordingly. Give explicit mentions higher confidence weight.

### Data quality rules

- Remove duplicates (same user, same text, different dates).
- Remove empty or single-word reviews ("good", "nice", "ok").
- Remove reviews about app performance (crashes, loading, login) unless they clearly block the shopping journey.
- Remove obvious spam, promotional content, and bot-generated reviews.
- Retain the source URL for every record — this makes findings auditable.
- Use only public content and follow each platform's terms of use.

---

## Step 2: Define the taxonomy

Define categories **before** running the AI analysis so that classifications are consistent across all comments.

### Taxonomy v1

**Save reason** (why the user saved or wishlisted the item):
- `aspiration` — likes the design, wants to own it someday
- `event_planning` — saving for a specific occasion (wedding, festival, party)
- `comparison` — shortlisting to compare alternatives
- `price_watch` — waiting for a sale or price drop
- `availability_watch` — item out of stock, checking back later
- `bookmark` — using wishlist as a browsing bookmark, no clear purchase intent
- `gift_consideration` — considering as a gift for someone else

**Purchase barrier** (what prevents the purchase — allow multi-select):
- `fit_uncertainty` — unsure about size, fit, or drape on their body type
- `quality_uncertainty` — unsure about fabric, stitching, colour accuracy
- `price_concern` — finds the item expensive (but this is not about wanting a discount)
- `trust_issues` — doubts about seller legitimacy, fake reviews, product authenticity
- `decision_overload` — too many similar options, cannot choose
- `delivery_return_friction` — concerns about delivery time, return process, or return cost
- `styling_uncertainty` — unsure how to style or what to pair it with
- `stock_availability` — desired size or colour out of stock
- `social_validation` — needs approval from friends, family, or social circle
- `occasion_mismatch` — likes the item but has no immediate occasion to wear it

**Missing information** (unanswered questions after wishlisting — allow multi-select):
- `sizing_details` — body-type-specific fit, measurements, size chart accuracy
- `material_feel` — fabric quality, texture, weight, transparency
- `visual_accuracy` — does the actual product match the photos?
- `use_case_styling` — how to wear it, occasion suitability, pairing ideas
- `social_proof` — reviews from people with similar body type, style, or context
- `alternative_comparison` — how does this compare to similar items on the same or other platforms?

**Decision stage** (where the user is in the purchase journey):
- `browsing` — exploring, no specific intent
- `saving` — has identified interest, saving for later
- `evaluating` — actively comparing, reading reviews, seeking information
- `ready_to_buy` — high intent, looking for final push
- `abandoned` — decided not to buy, has moved on

**External behaviour** (what users do outside the app before purchasing):
- `youtube_search` — watches haul videos, review videos, styling guides
- `social_media` — checks Instagram, Pinterest for outfit ideas or real photos
- `friends_family` — asks friends or family for opinions
- `competitor_comparison` — checks the same or similar product on another platform
- `offline_trial` — visits a physical store to try before buying online
- `google_search` — searches for reviews, "is X worth it?", sizing advice

### Taxonomy evolution

This taxonomy is a starting point. After running the first 50 comments, review the classifications and:
- Add new categories if recurring themes don't fit existing ones.
- Merge categories that are functionally identical in your dataset.
- Document every change so the final taxonomy is traceable.

---

## Step 3: Design the AI classification prompt

The prompt is the core of the engine. A poorly designed prompt produces inconsistent, shallow output regardless of the model used.

### Recommended model

Use **GPT-4o-mini** for cost efficiency at scale. For validation runs on a subset, use **GPT-4o** or **Claude 3.5 Sonnet** to compare quality.

### Token cost estimate

250–500 comments × ~300 tokens input + ~200 tokens output per comment ≈ 125K–250K tokens total. On GPT-4o-mini, this costs approximately $0.05–$0.10. Negligible.

### System prompt

```text
You are an expert user researcher analyzing public reviews and comments about
online fashion shopping in India, specifically about {PRODUCT_NAME}.

Your task is to extract structured signals related to wishlist behaviour and
purchase decision-making. Focus on understanding WHY users save items and
what PREVENTS them from purchasing.

For each comment, extract the following fields. Use ONLY the categories
listed. If a field does not apply, use "not_applicable". A comment may have
multiple barriers, multiple missing-information items, and multiple
external behaviours.

TAXONOMY:
- save_reason: aspiration | event_planning | comparison | price_watch |
  availability_watch | bookmark | gift_consideration | not_applicable
- purchase_barriers: [fit_uncertainty, quality_uncertainty, price_concern,
  trust_issues, decision_overload, delivery_return_friction,
  styling_uncertainty, stock_availability, social_validation,
  occasion_mismatch] (multi-select, or ["not_applicable"])
- missing_information: [sizing_details, material_feel, visual_accuracy,
  use_case_styling, social_proof, alternative_comparison]
  (multi-select, or ["not_applicable"])
- decision_stage: browsing | saving | evaluating | ready_to_buy | abandoned
  | not_applicable
- external_behaviour: [youtube_search, social_media, friends_family,
  competitor_comparison, offline_trial, google_search]
  (multi-select, or ["not_applicable"])
- user_segment_clues: free text describing any observable user
  characteristics (e.g., "first-time buyer", "wedding shopper",
  "budget-conscious college student")
- signal_confidence: high | medium | low (how clearly does the comment
  express wishlist-related intent?)
- key_quote: the most relevant 1–2 sentence excerpt, verbatim
- insight_summary: a one-sentence insight in your own words

Return your response as a JSON object.
```

### User prompt (per comment)

```text
Analyze the following review from {PLATFORM}:

---
"{REVIEW_TEXT}"
---

Source URL: {SOURCE_URL}
Date: {DATE}
Rating: {RATING}
```

### Processing approach

- Process comments **one at a time** (not batched) to ensure each gets full attention.
- For ambiguous comments, the AI should still classify with `signal_confidence: low` rather than skipping.
- Run a **calibration batch** of 20 comments first, manually verify the output, and adjust the prompt before scaling.

### Prompt iteration checklist

After the calibration batch, check for:
- [ ] Are multi-barrier comments getting all relevant barriers tagged?
- [ ] Is `signal_confidence` being used appropriately (not everything marked "high")?
- [ ] Are `key_quote` selections actually the most relevant excerpts?
- [ ] Are segment clues specific enough to be useful for interview recruitment?
- [ ] Does the prompt handle non-English or mixed-language reviews?

---

## Step 4: Build the analysis workflow

### Architecture

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  CSV/JSON    │────▶│  Python      │────▶│  OpenAI API      │
│  raw data    │     │  processor   │     │  (classification)│
└──────────────┘     └──────────────┘     └──────────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐     ┌──────────────────┐
                     │  Structured  │◀────│  JSON responses  │
                     │  results DB  │     │                  │
                     └──────────────┘     └──────────────────┘
                            │
                            ▼
                     ┌──────────────────────────────┐
                     │  Streamlit app               │
                     │  - Hero summary              │
                     │  - Barrier analysis           │
                     │  - Opportunity scores         │
                     │  - Metric tree mapping        │
                     │  - Evidence explorer          │
                     └──────────────────────────────┘
```

### Recommended stack

| Component | Tool | Why |
|---|---|---|
| Data storage | CSV or SQLite | Simple, portable, no server needed |
| AI processing | Python script with OpenAI SDK | Direct control, easy to debug |
| Results storage | JSON file or SQLite | Pre-computed, fast to load |
| Frontend | Streamlit | Free deployment, fast to build, interactive |
| Deployment | Streamlit Community Cloud | Free, no credit card, public URL |

### Alternative stacks

- **n8n or Zapier:** If you prefer visual workflow builders. Good for chaining API calls but harder to debug classification quality.
- **LangChain + FastAPI + Vercel:** More engineering effort, but more flexible if you want a custom UI.
- **Google Colab + ngrok:** Quick prototype, but unstable for reviewer access.

---

## Step 5: What the AI must analyze

For every comment, extract structured signals across seven dimensions.

### Dimension 1: Save reason

Why did the user save or wishlist the item? Examples: liking the design, planning for an event, comparing alternatives, watching the price, watching availability, taking inspiration, bookmarking.

### Dimension 2: Wishlist intent type

Classify the item as likely genuine purchase intent, active consideration/comparison, price-watch behaviour, availability-watch behaviour, or simple bookmarking.

### Dimension 3: Purchase barriers

Look for fit/size uncertainty, quality uncertainty, price concern (non-discount), return hassle, delivery timing, lack of styling ideas, missing reviews, decision overload, social validation needs, and trust issues.

### Dimension 4: Missing information

Identify unanswered questions about model/body-type fit, fabric quality, colour accuracy, occasion suitability, reviews from similar people, and comparisons with alternatives.

### Dimension 5: Behaviour outside the app

Capture whether users search YouTube, ask friends, check Instagram, compare other marketplaces, or seek an offline trial before purchasing.

### Dimension 6: Segments and contexts

Tag clues such as new versus frequent shopper, occasion shopper, size-sensitive shopper, budget-conscious shopper, trend-led shopper, and similar useful segments.

### Dimension 7: Decision stage and evidence

Classify whether the person is browsing, saving, evaluating, ready to buy, or abandoning. Return a concise insight together with the exact source excerpt and link.

---

## Step 6: Convert findings into opportunity areas

### Aggregations the engine must display

- The most common barriers overall (bar chart with counts and percentages).
- Barriers broken down by source platform and user segment.
- The proportion of wishlists that appear to be true buying intent versus bookmarking.
- The unresolved questions users have after wishlisting.
- Which barriers occur closest to the purchase decision (highest decision stage).
- Representative quotes with clickable source links.
- A ranked list of opportunity areas.

### Opportunity scoring

Use a calibrated 1–5 scale for each factor:

| Factor | 1 (Low) | 2 | 3 | 4 | 5 (High) |
|---|---|---|---|---|---|
| **Frequency** | <5% of comments | 5–10% | 10–15% | 15–25% | >25% of comments |
| **Severity** | Minor annoyance, doesn't block purchase | Causes hesitation | Significant delay | Strong blocker for most | Complete deal-breaker |
| **Closeness to purchase** | Browsing stage | Saving stage | Evaluating stage | Ready-to-buy stage | Abandoned after high intent |
| **Segment clarity** | No clear segment identifiable | Vague segment | Identifiable segment | Clear, describable segment | Well-defined, recruitable segment |
| **Non-discount solvability** | Only solvable with pricing/coupons | Mostly pricing-dependent | Mixed — some UX solutions | Mostly solvable with UX/information | Fully solvable without discounts |

```text
Opportunity score = frequency × severity × closeness × segment_clarity × non_discount_solvability
```

**Score assignment process:**
1. **Frequency** — computed automatically from classification counts.
2. **Severity, closeness** — computed from AI classification (decision stage, barrier language intensity).
3. **Segment clarity, non-discount solvability** — assigned by the analyst (you) based on the evidence.
4. Normalize final scores to 0–100 for readability.

The last factor is critical because the assignment prohibits monetary incentives. "Give a coupon" cannot be the eventual solution, but "reduce fit uncertainty with better personalized size confidence" can.

---

## Step 7: Connect to the metric tree (Part 2 bridge)

Build the metric decomposition **into the engine** as a dedicated tab or view. This creates a seamless narrative from Part 1 → Part 2.

### Metric tree structure

```text
Wishlist → Purchase Conversion (30 days)
│
├── Wishlist Engagement Rate
│   (% users who revisit their wishlist within 30 days)
│   ├── Reminder/notification effectiveness
│   └── Wishlist organization and findability
│
├── Consideration-to-Intent Rate
│   (% who move from saving to actively evaluating)
│   ├── Information completeness (size, fit, reviews)
│   ├── Confidence level (social proof, visual accuracy)
│   └── Alternative comparison friction
│
├── Intent-to-Purchase Rate
│   (% who move from evaluating to buying)
│   ├── Price acceptability (non-discount signals)
│   ├── Urgency triggers (stock levels, occasion proximity, trend momentum)
│   └── Checkout friction and payment experience
│
└── Guardrail Metrics
    ├── Return rate from wishlist purchases
    ├── Wishlist abandonment rate (items removed without purchase)
    └── User satisfaction with purchase (post-purchase NPS)
```

When a reviewer clicks on an opportunity in the engine, show which metric tree node(s) it maps to. This makes the connection between discovery findings and business impact explicit.

---

## Step 8: Build the reviewer experience

The reviewer (evaluator) will spend **60–90 seconds** forming a first impression. Design for that window.

### Page structure

```text
┌─────────────────────────────────────────────────────┐
│  Hero Summary                                       │
│  "We analyzed 347 public conversations across 4     │
│   platforms. The #1 barrier to wishlist conversion   │
│   is fit uncertainty for occasion shoppers (42% of  │
│   high-intent comments)."                           │
├─────────────────────────────────────────────────────┤
│  Tab 1: Opportunity Ranking                         │
│  Tab 2: Barrier Analysis                            │
│  Tab 3: Metric Tree Mapping                         │
│  Tab 4: Evidence Explorer                           │
│  Tab 5: Data & Methodology                          │
├─────────────────────────────────────────────────────┤
│  [Re-run Analysis on Sample] button                 │
│  (runs AI classification live on 10–20 comments     │
│   so the reviewer can see the engine in action)     │
└─────────────────────────────────────────────────────┘
```

### Tab details

**Tab 1 — Opportunity Ranking:**
- Ranked list of 3–5 opportunity areas.
- Each shows: opportunity name, score, component scores, matching comment count, top segment, and a one-line hypothesis.
- Clicking an opportunity expands to show evidence quotes with source links.

**Tab 2 — Barrier Analysis:**
- Bar charts: barrier frequency overall, by platform, by segment.
- Sankey or flow diagram: save reason → barrier → decision stage.
- Filter controls for platform, segment, and decision stage.

**Tab 3 — Metric Tree Mapping:**
- Interactive metric tree visualization.
- Each opportunity mapped to the metric node it influences.
- Shows the hypothesized impact pathway.

**Tab 4 — Evidence Explorer:**
- Searchable, filterable table of all classified comments.
- Columns: source, date, review text, save reason, barriers, missing info, segment, decision stage, confidence.
- Clickable source URLs for verification.

**Tab 5 — Data & Methodology:**
- Data volume breakdown by source platform (table + pie chart).
- Taxonomy definitions.
- Sample of AI classification with human verification results.
- Data limitations acknowledgement.

### First-impression design principles

- The hero summary should be **the single most important finding**, stated as a clear, quantified claim.
- Use colour consistently: red for barriers, green for opportunities, amber for caution.
- Include a "How to read this" tooltip or short guide for first-time viewers.
- Loading states should show progress, not just a spinner.

---

## Step 9: Quality and credibility checks

### Automated checks

- Deduplicate records by review text similarity (exact match and fuzzy match at 90% threshold).
- Flag and exclude non-relevant reviews (app crashes, payment gateway issues, login problems) unless they clearly describe a shopping-journey blockage.
- Validate JSON structure of every AI response before storing.

### Manual verification

- Randomly sample **10–20%** of AI-classified comments (at least 30 records).
- For each, independently classify using the taxonomy and compare with the AI output.
- Calculate inter-rater agreement (aim for >75% agreement on primary barrier).
- Document disagreements and adjust the prompt or taxonomy if systematic errors emerge.

### Transparency in the engine

- Show the sample size for each source — do not imply a small sample represents all users.
- Separate directly observed evidence (user's own words) from AI-generated inference (the "insight_summary").
- Label each quote with its source platform and date.
- Include a "Data Limitations" section acknowledging:
  - App store reviews skew toward dissatisfied, vocal users.
  - Reddit skews toward power users and tech-savvy demographics.
  - Neither source represents the silent majority who wishlist and never return.
  - The analysis identifies *directional signals*, not statistically significant conclusions.

---

## Step 10: Deploy

### Recommended deployment: Streamlit Community Cloud

**Why Streamlit:**
- Free hosting, no credit card required.
- Public URL shareable with reviewers.
- Python-native — same language as the data processing pipeline.
- Built-in interactive widgets (filters, charts, tabs).
- Automatic redeployment on git push.

**Setup steps:**
1. Create a GitHub repository for the project.
2. Structure the repo:
   ```
   ├── app.py                  # Streamlit application
   ├── requirements.txt        # Python dependencies
   ├── data/
   │   ├── raw_reviews.csv     # Collected raw data
   │   └── classified.json     # Pre-computed AI classifications
   ├── analysis/
   │   ├── classify.py         # AI classification script
   │   ├── aggregate.py        # Aggregation and scoring logic
   │   └── prompts.py          # System and user prompts
   └── README.md
   ```
3. Deploy on [share.streamlit.io](https://share.streamlit.io) — connect the GitHub repo, select `app.py` as the entry point.
4. Store the OpenAI API key in Streamlit's secrets management (for the live re-run feature).
5. Test the public URL in an incognito browser window.

**Pre-compute vs. live analysis:**
- **Pre-compute** the full analysis and store results in `classified.json`. The app loads these results instantly on page load.
- **Live re-run** on a small sample (10–20 comments) when the reviewer clicks "Re-run Analysis." This demonstrates the engine is real, not just static charts.

### Alternative deployment options

| Platform | Pros | Cons |
|---|---|---|
| Hugging Face Spaces | Free, supports Streamlit and Gradio | Slower cold starts |
| Vercel + Next.js | Fast, professional look | More engineering effort |
| Railway | Easy deployment, free tier | Requires credit card for some plans |
| Render | Free tier, Docker support | Cold starts on free tier |
| Google Colab + ngrok | Fastest prototype | Unstable URL, not suitable for reviewer access |

---

## Slide for the final deck

Use one slide titled with the key message, not a generic label. For example:

> **"Fit uncertainty blocks 42% of high-intent wishlisted purchases for occasion shoppers"**

### Slide layout

```text
┌────────────────────────────────────────────────────────────────┐
│  TITLE: [Key finding as the slide title]                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  LEFT COLUMN (40%):                    RIGHT COLUMN (60%):     │
│                                                                │
│  Pipeline diagram:                     Top 3 opportunities     │
│                                        with scores:            │
│  347 public conversations                                      │
│         ↓                              1. Fit uncertainty      │
│  Cleaning & dedup                         Score: 87/100        │
│         ↓                                 42% of comments      │
│  AI extraction                                                 │
│  (7-dimension taxonomy)               2. Quality uncertainty   │
│         ↓                                 Score: 64/100        │
│  Theme & segment clustering               28% of comments      │
│         ↓                                                      │
│  Opportunity scoring                   3. Social validation    │
│         ↓                                 Score: 51/100        │
│  Interview hypotheses                     19% of comments      │
│                                                                │
│  Data: 4 platforms,                    Example:                 │
│  250+ comments,                        Raw quote → Structured  │
│  7 extraction dimensions               insight (mini example)  │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  FOOTER: Link to live engine • Font size 14 • Anonymous        │
└────────────────────────────────────────────────────────────────┘
```

### Slide rules (from requirements)

- Font size: 14 (strictly adhered to).
- No name anywhere on the slide.
- Slide title states the key message, not "Discovery Engine" or "Part 1."
- Background colour must ensure text readability.
- Colour choices must be accessible to colour-blind readers.
- Hyperlink the live engine URL.

---

## Expected output from the engine

The reviewer should see findings in a format similar to this:

> **Opportunity: Fit confidence for occasion-led shoppers**
> Score: 87/100 (Frequency: 5, Severity: 5, Closeness: 4, Segment clarity: 4, Non-discount solvability: 5)
>
> Users save outfits for a specific event (wedding, festival, party) but delay because they cannot predict fit, drape, or styling on their body type. They seek YouTube/Instagram photos and friend validation outside the app.

For every opportunity, show:

- Number and percentage of matching comments.
- Relevant segment or context.
- Top unresolved questions from the "missing information" dimension.
- Three to five linked evidence quotes (verbatim, with source URLs).
- Opportunity score with individual component scores.
- A clear hypothesis to validate in user interviews.
- The metric tree node(s) this opportunity maps to.

This creates the bridge from the discovery engine → metric decomposition → primary research.

---

## Execution timeline

| Day | Activity | Output |
|---|---|---|
| **Day 1** | Set up data collection scripts for Myntra, begin scraping | Raw data CSV (first 100+ records) |
| **Day 2** | Complete data collection, clean and deduplicate, finalize taxonomy | Clean CSV (250–500 records), taxonomy doc |
| **Day 2 evening** | Design and test AI prompt on 20-comment calibration batch | Validated prompt, calibration results |
| **Day 3** | Run full classification, manual verification of 10–20% sample | Classified JSON, verification log |
| **Day 3 evening** | Compute aggregations and opportunity scores | Aggregated results, ranked opportunities |
| **Day 4** | Build Streamlit app, deploy to Streamlit Cloud | Live public URL |
| **Day 4 evening** | Add metric tree tab, polish reviewer experience | Final engine ready for testing |

**Total: ~4 days.** This leaves sufficient time for Parts 2–7, which carry the bulk of the evaluation weight.

### Time-boxing discipline

If you find yourself spending more than 4 days on the engine:
- Ship with 3 core dimensions (barriers, missing info, segments) instead of all 7.
- Use pre-computed results only — skip the live re-run feature.
- Use simple bar charts instead of interactive visualizations.
- The engine must be "good enough to produce credible interview hypotheses" — not perfect.

---

## Checklist before submission

- [ ] Public URL works in an incognito browser.
- [ ] Hero summary loads within 3 seconds.
- [ ] At least 3 ranked opportunities are displayed with evidence.
- [ ] Every quote has a clickable source URL.
- [ ] Opportunity scores use the calibrated 1–5 scale.
- [ ] Metric tree tab shows connections to Part 2.
- [ ] Data limitations are acknowledged.
- [ ] Manual verification results (10–20% sample) are documented.
- [ ] The "Re-run Analysis" button works on a sample (or is clearly labeled as pre-computed).
- [ ] Slide follows all formatting rules (font 14, anonymous, accessible colours).
- [ ] No personal name appears anywhere in the engine or slide.

---

## By the end of Deliverable 1

You should be able to state, with evidence:

> These are the main reasons wishlisted items do not become purchases, for these users, and this is the problem most worth validating in interviews.

This statement, backed by your engine's ranked opportunities and evidence base, becomes the foundation for everything that follows: metric decomposition (Part 2), interview design (Part 3), problem definition (Part 4), MVP (Part 5), success metrics (Part 6), and risk assessment (Part 7).
