# Nucleus — MVP Product & Business Plan

## 1. Executive Summary

**Product:** Nucleus  
**Category:** Consumer Social + News  
**Core Insight:**  
People don’t just want to know what’s happening — they want to know **how others feel about it and where they stand**.

**Positioning:**  
> Nucleus is the fastest way to understand both an event and the world’s reaction to it — including your place within it.

**MVP Goal:**  
Validate that users:
1. Consistently submit structured sentiment (sliders)
2. Find value in **opinion comparison**
3. Return daily for new events and updated distributions

---

## 2. Product Thesis

### The Problem

| Category | Issue |
|--------|------|
| News Apps | Overwhelming, fragmented, no emotional context |
| Social Platforms | Noisy, extreme, unstructured opinions |
| Polling Platforms | Not integrated with real-world events |

### The Gap

No platform currently:
- Aggregates **events + sentiment**
- Structures opinions into **quantifiable distributions**
- Enables **personal positioning vs the crowd**

---

## 3. Core Value Proposition

> “Understand the world — and where you stand in it.”

### User Value

- **Clarity:** Quickly understand important events  
- **Expression:** Share opinion with minimal effort  
- **Insight:** See how others think  
- **Identity:** Discover personal alignment or deviation  

---

## 4. Target User

### Primary Segment
- Age: 18–35  
- Behavior:
  - Light-to-moderate news consumers
  - Active on X, Reddit, Instagram
  - Curious about social consensus

### Core Motivation
> “Do people think like me?”

---

## 5. Product Principles (Non-Negotiable)

1. **Speed > Depth (initially)**  
   Users must reach value in <10 seconds

2. **Input Before Output**  
   Users must submit sentiment to unlock insights

3. **High Signal Only**  
   No feed clutter — strictly curated events

4. **No Chaos Layer**  
   No comments, no threads in MVP

5. **Emotionally Engaging**  
   The product must trigger:
   - surprise
   - validation
   - disagreement

---

## 6. MVP Scope

### 6.1 Core Loop

1. User sees event  
2. User submits sentiment  
3. User sees distribution + positioning  
4. User reacts emotionally (“I’m different / aligned”)  

---

### 6.2 App Structure

**Bottom Navigation:**
- Today
- Discover (placeholder for later)
- Profile

---

## 7. Feature Specification

### 7.1 Today Feed

**Purpose:** Present a small set of high-importance events

**Constraints:**
- 5–10 events per day (strict)
- Updated daily

**Event Card Fields:**
- Category (color-coded)
- Title (clear, neutral)
- Timestamp
- Response count (social proof)

**Design Notes:**
- One “primary” story (larger card)
- Others secondary

---

### 7.2 Event Page

#### Section 1: Summary
- 3–5 sentences
- Multi-source aggregated
- Neutral tone

#### Section 2: Key Takeaways
- Max 3 bullet points
- Clear, non-editorial

#### Section 3: Sentiment Input (MANDATORY)

3 sliders (0–100 scale):

- Concern
- Optimism
- Significance

**Interaction Requirements:**
- Must complete all sliders
- Smooth, tactile UI
- Immediate progression to results

---

### 7.3 Results Screen (CORE PRODUCT)

**Purpose:** Deliver the “aha” moment

**Must Include:**
- Distribution curves (per slider)
- User position marker
- Percentile comparison

**Key Insight Copy Examples:**
- “You are more concerned than 78% of users”
- “You are among the least optimistic 15%”

**Optional (High Impact):**
- Cluster labeling:
  - “Cautious Majority”
  - “Optimistic Minority”

---

### 7.4 Profile (Lightweight)

- Username (pseudonymous)
- Minimal stats:
  - # responses
  - optional: trend over time

---

## 8. Behavioral Design (Critical)

### Emotional Triggers

| Trigger | Effect |
|--------|-------|
| Social comparison | Engagement |
| Percentile ranking | Identity formation |
| Being an outlier | Curiosity |
| Alignment with majority | Validation |

---

### Retention Mechanism

**Primary Driver:**
> New events + desire to compare opinions

**Secondary Driver:**
> Identity over time (“what kind of thinker am I?”)

---

## 9. Data & Backend Design

### 9.1 Event Pipeline (MVP)

- Manual curation (founder-led)
- Sources:
  - Major news aggregators
  - Trending topics

---

### 9.2 Summarization

- LLM-generated summaries
- Prompt constraints:
  - neutral tone
  - multi-source synthesis
  - no speculation

---

### 9.3 Data Model

#### Events Table
- id
- title
- category
- summary
- timestamp

#### Responses Table
- user_id
- event_id
- concern_score
- optimism_score
- significance_score
- timestamp

---

### 9.4 Aggregation

- Histograms per slider
- Percentile ranking
- Mean / median

---

## 10. Success Metrics

### Activation
- % users completing ≥1 response

### Engagement
- Avg responses per session
- Time to first response

### Retention
- Day 1 retention
- Day 7 retention

### Core KPI
> % of users who return within 24h and respond again

---

## 11. Go-To-Market Strategy

### Positioning

NOT:
- “News app”

YES:
> “See how your opinion compares to everyone else.”

---

### Launch Channels

- Reddit (r/technology, r/worldnews)
- X (tech + current events communities)
- College networks

---

### Content Strategy

Post:
- Distribution screenshots
- Polarizing events

Goal:
- Trigger curiosity
- Encourage sharing

---

## 12. Roadmap (Post-MVP)

### Phase 2
- Opinion history
- Trend shifts over time
- Notifications

### Phase 3
- Social graph (follow users)
- Creator-driven events

### Phase 4
- Advanced ML:
  - event clustering
  - bias detection
  - segmentation

---

## 13. Risks & Mitigations

| Risk | Mitigation |
|-----|-----------|
| Low retention | Daily fresh events |
| Low participation | Reduce friction, fast UI |
| Gimmick perception | Improve insights depth |
| Content trust issues | Multi-source summaries |

---

## 14. Technical Stack

- Frontend: SwiftUI (Rork)
- Backend: Node.js / Python
- DB: Postgres / Supabase
- LLM: OpenAI / Anthropic
- Analytics: PostHog

---

## 15. Key Strategic Insight

This is NOT a news company.

This is:

> A structured, scalable system for capturing and visualizing human opinion at scale.

If successful, Nucleus becomes:
- A sentiment engine
- A social layer
- A data platform

---

## 16. MVP Definition of Success

Nucleus succeeds if:

> Users repeatedly return to answer:
> “What do people think about this — and how do I compare?”

---

## Appendix A — MVP Build Checklist

- [ ] Today feed (5–10 events)
- [ ] Event summary + takeaways
- [ ] Slider input system
- [ ] Results visualization (distribution + percentile)
- [ ] Basic profile
- [ ] Manual event ingestion
- [ ] LLM summary pipeline

---

## Appendix B — What to Ignore

- Comments
- Followers
- Real-time data
- Complex ML
- Monetization

---
