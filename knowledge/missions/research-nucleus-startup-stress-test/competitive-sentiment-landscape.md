---
status: completed
milestone: Research
date: 2026-03-24
type: research
model: claude
tags: [#research]
confidence: medium
router_decision: claude
router_reasoning: 'research'
---

## Task Description

Map every existing product, feature, or platform that captures structured public opinion or sentiment on news events. Cover: Twitter/X polls, Community Notes, Polis, AllSides, Ground News, Polymarket, Metaculus, Reddit polls, Instagram Story polls, YouTube Community polls, Blind, and any polling apps (Polly, Mentimeter, Kahoot, Recess, etc.) that have targeted news or current events. For each product, document: (1) what structured input it captures (freeform vs. slider vs. binary vs. prediction market), (2) whether it shows users how their opinion compares to others, (3) its current active user base and engagement metrics if public, (4) how close it gets to Nucleus's value prop of event + 3-slider sentiment + personal percentile ranking, and (5) why users do or don't engage with it. Identify any products in this space that have shut down in the last 5 years and explain why. Note funding history for any VC-backed entrants. Conclude with a whitespace map: what does Nucleus offer that none of these do, and is that gap real or trivially bridgeable?

## Expected Behavior

A detailed competitive matrix with 8-12 products, clear differentiation analysis, shutdown postmortems for failed entrants, and an honest assessment of whether the Nucleus gap is defensible or easily replicated by an incumbent adding a feature.

## Findings / Output

Here is the full competitive landscape report:

---

# Competitive Landscape: Structured Public Opinion & Sentiment Capture on News Events

*Research date: March 23, 2026. All citations included.*

---

## Executive Summary

Nucleus sits at an unusual intersection: it attaches a structured, multi-dimensional sentiment instrument (three sliders) to a specific news event and then delivers a **personal percentile rank** back to the user — telling them not just "X% of people agree," but exactly where they sit in the distribution. No surveyed platform does all three of these things (event-anchored + multi-axis slider + personal percentile feedback) simultaneously for a consumer news audience. The closest competitors each solve one or two dimensions but not all three, and the few that approach the full combination are B2B research tools or academic democracy experiments, not consumer products.

---

## Platform-by-Platform Analysis

---

### 1. Twitter / X Polls

**What structured input it captures**
Binary or up-to-four-option multiple choice. Users vote on one option per poll; no sliders, no numeric scales. Polls can run 5 minutes to 7 days.

**Does it show users how their opinion compares to others?**
Yes — partially and crudely. After voting, results are revealed instantly showing percentage splits. The winning choice appears in bold. There is no individual-level comparison; you see the aggregate but not where you personally sit in any distribution. Votes are anonymous; neither the creator nor other voters can see who voted for what.

**Active user base and engagement metrics**
X has approximately 600 million monthly active users as of early 2026, with roughly 335 million daily active users. Polls average 0.39% engagement rate per post on the platform (up from 0.09% in 2024). Nearly 60% of X users report using the platform to follow news and current events.

**Proximity to Nucleus value prop**
Low. Polls are freeform, creator-defined, and usually one-dimensional. Results show group percentage but never a user's personal percentile. No event framework — any post can be a poll. No multi-axis sentiment capture.

**Why users engage / don't engage**
Engage: low friction (one tap), instant gratification, social visibility of results, sense of participation in real-time events. Don't engage: poll options are creator-designed (often biased framing), no depth of expression beyond the single choice, results are easily gamed by bot activity, no follow-through or context.

**Funding / ownership**: Privately held by Elon Musk (acquired October 2022, ~$44B).

**Sources**: [Twitter/X Benchmarks 2026 — Enrich Labs](https://www.enrichlabs.ai/blog/twitter-x-benchmarks-2025) | [X Polls Help](https://help.x.com/en/using-x/x-polls) | [Twitter Stats 2025 — Social Champ](https://www.socialchamp.com/blog/twitter-stats/) | [Noble Desktop — Creating Polls on Twitter](https://www.nobledesktop.com/learn/social-media-marketing/creating-polls-on-twitter-strategies-for-higher-engagement)

---

### 2. Community Notes (X / Twitter)

**What structured input it captures**
Binary: contributors rate proposed notes as "Helpful," "Somewhat helpful," or "Not helpful." Notes themselves are free-text annotations. The underlying bridging-based algorithm (not a vote count) determines whether a note gets displayed, weighting ratings that come from users across the political spectrum.

**Does it show users how their opinion compares to others?**
No. Contributors see aggregate ratings on notes they've rated after the note reaches a status threshold, but there is no personal percentile or position-in-distribution feedback.

**Active user base and engagement metrics**
X reached 1 million Community Notes contributors worldwide. However, a 2025 NBC News analysis found submissions cratered significantly. The "helpful" note rate fell from 13.1% (peak, March 2024) to 8.2% (May 2025). Contributor retention dropped from 63% (early 2023) to 44% (late 2024). A University of Washington study confirmed posts receiving Community Notes saw reposts drop 46% and likes drop 44%.

**Proximity to Nucleus value prop**
Very low. Community Notes is a fact-checking and contextualization tool, not a sentiment-expression tool.

**Sources**: [Community Notes — Wikipedia](https://en.wikipedia.org/wiki/Community_Notes) | [NBC News: Community Notes use has plummeted](https://www.nbcnews.com/tech/social-media/x-twitter-community-notes-disappear-data-rcna210710) | [UW News: Community Notes reduce virality](https://www.washington.edu/news/2025/09/18/community-notes-x-false-information-viral/)

---

### 3. Polis / pol.is

**What structured input it captures**
Binary agree/disagree (and sometimes "pass") on text statements. Users can also submit their own statements. No sliders, no numeric ratings.

**Does it show users how their opinion compares to others?**
Yes — in aggregate cluster form. Polis uses PCA and k-means clustering to group users and visualizes the result as a 2D opinion map. But it shows you which *cluster* you belong to, not a personal percentile rank on any specific axis.

**Active user base and engagement metrics**
Used with populations ranging from 40 to 40,000 per deployment. Largest deployment was vTaiwan's with 200,000+ participants over multiple years. Polis is a 501(c)(3) nonprofit; not a mass consumer product.

**Proximity to Nucleus value prop**
Moderate in methodology, low in consumer UX. Polis does show how your votes cluster against others (the closest thing to social comparison on this list), but it's a governance/deliberation tool, not a consumer news experience.

**Sources**: [Pol.is — Wikipedia](https://en.wikipedia.org/wiki/Pol.is) | [Computational Democracy Project FAQ](https://compdemocracy.org/faq/) | [vTaiwan — Participedia](https://participedia.net/method/vtaiwan)

---

### 4. AllSides

**What structured input it captures**
Multiple formats: (a) Blind Bias Surveys — users rate news content without knowing the source; (b) Community rating — users vote on whether a source leans Left/Right on a 5-point categorical scale. Input is about *source bias*, not the user's emotional response to a news event.

**Does it show users how their opinion compares to others?**
Partially. When users rate a source, they can see AllSides' prior rating and how other users have voted (aggregate breakdown). No personal percentile or individual rank shown.

**Active user base and engagement metrics**
AllSides has rated 2,400+ media sources. Specific MAU not publicly disclosed. Launched 2012.

**Proximity to Nucleus value prop**
Low. AllSides measures perceived *source* bias rather than user sentiment on a news *event*. No event-anchored rating, no slider instrument, no personal percentile.

**Sources**: [AllSides Media Bias Chart](https://www.allsides.com/media-bias/media-bias-chart) | [AllSides Bias Rating Methods](https://www.allsides.com/about/media-bias-rating-methods)

---

### 5. Ground News

**What structured input it captures**
Does not capture user sentiment on events at all. Aggregates existing news coverage and categorizes sources by political bias, factuality, and ownership.

**Does it show users how their opinion compares to others?**
No. Shows how *media coverage* is distributed, not user opinion.

**Active user base and engagement metrics**
250,000 mindful newsreaders (self-reported). Bootstrapped and subscriber-supported. Founded 2018.

**Proximity to Nucleus value prop**
Very low. A media bias aggregator with no user-sentiment input and no social comparison mechanism.

**Sources**: [Ground News — Wikipedia](https://en.wikipedia.org/wiki/Ground_News) | [Ground News About Us](https://ground.news/about)

---

### 6. Polymarket

**What structured input it captures**
Binary probability markets: users buy and sell shares in binary outcomes (Yes/No). Prices range from $0.01 to $0.99 and reflect implied crowd probability. Financially staked.

**Does it show users how their opinion compares to others?**
Yes — through market price as aggregate crowd signal. No personal percentile rank; you see where the crowd is priced, not where you individually sit in a distribution.

**Active user base and engagement metrics**
450,000+ active traders as of early 2026. $22 billion in notional trading volume in 2025. $110M daily volume.

**Funding history**: $4M seed (2020), $45M Series A (2022, Polychain Capital), $200M Series B (Founders Fund, June 2025, ~$1B valuation), $2B investment from ICE/NYSE at $9B valuation (October 2025). Seeking $15B valuation round as of late 2025.

**Proximity to Nucleus value prop**
Low on UX, high on social comparison mechanism. Gives you a real-time crowd probability but requires financial stakes, covers only binary outcomes, is crypto-native, and captures probability of outcome — not sentiment or emotion.

**Sources**: [Polymarket Volumes — CCN](https://www.ccn.com/news/crypto/polymarket-7-5-billion-2025-prediction-markets/) | [ICE invests $2B in Polymarket — Fortune](https://fortune.com/crypto/2025/10/07/polymarket-2-billion-intercontinental-exchange-new-york-stock-exchange-9-billion/) | [Bloomberg: Polymarket $15B valuation](https://www.bloomberg.com/news/articles/2025-10-23/polymarket-is-seeking-funding-at-a-valuation-of-up-to-15-billion)

---

### 7. Kalshi

**What structured input it captures**
Same binary prediction market structure as Polymarket but operating as a CFTC-regulated exchange (legal in the US). Markets span sports (90%+ of activity), politics, economic indicators, technology, and cultural events.

**Does it show users how their opinion compares to others?**
Same as Polymarket: market price is the crowd signal. No personal percentile rank.

**Active user base and engagement metrics**
Millions of weekly users. 3,500+ active markets. Weekly trading volume surpassed $1B by late 2025, up 1,000%+ from 2024. $11B valuation (Series E, December 2025) led by Paradigm, with Sequoia, a16z, Meritech, IVP, ARK, Anthos, CapitalG, and YC participation. Infrastructure for Robinhood's Prediction Markets Hub. Formal media partnerships with CNN and CNBC.

**Proximity to Nucleus value prop**
Same as Polymarket: low on sentiment nuance, moderate on social comparison, requires financial stakes.

**Sources**: [Kalshi $11B Valuation — BusinessWire](https://www.businesswire.com/news/home/20251202735424/en/Kalshi-Reaches-$11-Billion-Valuation-as-App-Takes-over-America) | [Kalshi — Wikipedia](https://en.wikipedia.org/wiki/Kalshi)

---

### 8. Metaculus

**What structured input it captures**
Numeric probability estimate (0–100%) for a specific forecasting question. A continuous probability slider — but always "what probability do you assign to X happening?" not an emotional/sentiment rating.

**Does it show users how their opinion compares to others?**
Yes — the community median and distribution are shown after submission. Metaculus displays the distribution of all user forecasts for a question, so you can see whether your estimate is above or below the community median. This is the closest of all listed platforms to showing a user where they sit relative to others, though it's for probability forecasts, not sentiment.

**Active user base and engagement metrics**
Non-profit. Expert-level forecasters and rationalist community; not a mass consumer product.

**Proximity to Nucleus value prop**
Moderate on social comparison (shows your estimate vs. the distribution), low on emotional sentiment capture, low on consumer accessibility.

**Sources**: [Metaculus — Wikipedia](https://en.wikipedia.org/wiki/Metaculus) | [TIME: AI Learning to Predict the Future](https://time.com/7318577/ai-model-forecasting-predict-future-metaculus/)

---

### 9. Manifold Markets

**What structured input it captures**
Probability markets using play money ("Mana"). Continuous probability estimates on binary or multiple-outcome questions. Free-form market creation by any user.

**Does it show users how their opinion compares to others?**
Yes — through current market price and historical price charts. Shows crowd probability and your position against it, but not a personal percentile.

**Active user base and engagement metrics**
Peak of 2,000+ daily active users. After sunsetting real-money features in March 2025, DAU dropped to a record low of ~886 daily active traders. Play-money only as of 2025.

**Sources**: [Manifold Markets — Wikipedia](https://en.wikipedia.org/wiki/Manifold_(prediction_market)) | [Manifold Markets Review 2026 — CryptoNews](https://cryptonews.com/cryptocurrency/manifold-markets-review/)

---

### 10. Reddit Polls

**What structured input it captures**
Binary or multiple-choice polls embedded in posts (up to 6 options). Reddit introduced native polls in 2019. Upvotes/downvotes as a one-dimensional popularity signal.

**Does it show users how their opinion compares to others?**
Partially. After voting, poll results are shown as percentages. No personal positioning, no percentile, no individual ranking.

**Active user base and engagement metrics**
Reddit has 73 million daily active users (2025). 67% of Reddit users find it a good source for news (Rasmussen, April 2025).

**Proximity to Nucleus value prop**
Very low. Reddit polls are utilitarian tools for community decisions, not structured sentiment instruments tied to news events.

**Sources**: [Rasmussen: 67% of Reddit Users Find Good Source for News](https://www.rasmussenreports.com/public_content/lifestyle/general_lifestyle/april_2025/67_of_reddit_users_find_it_a_good_source_for_news) | [Reddit Polls — RedditTrends](https://reddittrends.com/reddit-polls-what-they-reveal/)

---

### 11. Instagram Story Polls

**What structured input it captures**
Binary (Yes/No or two custom options). Also: **Emoji Slider** (a continuous scale from 😐 to 😍) — the closest instrument to a true sentiment slider in this entire category. Quiz sticker (multiple choice). Question sticker (open text).

**Does it show users how their opinion compares to others?**
Creator-only. Only the story creator sees poll results; voters see a "Thank you for voting!" confirmation. No public display of aggregate results to voters, and no individual positioning or percentile.

**Active user base and engagement metrics**
70% of Instagram's 2 billion+ MAU watch Stories daily. Interactive Story stickers average 12–18% interaction rate. Adding any interactive element boosts engagement by 50%+.

**Proximity to Nucleus value prop**
Very low for news events. The Emoji Slider is a rare consumer-facing sentiment slider but is used for trivial engagement, not structured news sentiment. Results are entirely private to the creator.

**Sources**: [Instagram Stories Statistics 2025 — Amra & Elma](https://www.amraandelma.com/total-instagram-stories-statistics/) | [Instagram Polls Guide 2025 — Chatfuel](https://chatfuel.com/blog/instagram-polls-guide)

---

### 12. YouTube Community Polls

**What structured input it captures**
Binary or multiple-choice polls posted in the Community tab by creators. Standard percentage-based result display after voting.

**Does it show users how their opinion compares to others?**
Yes, aggregate percentages are publicly visible after voting. No individual positioning or percentile.

**Active user base and engagement metrics**
YouTube has 2.7 billion logged-in monthly users.

**Proximity to Nucleus value prop**
Very low. Community polls are creator engagement tools, not a structured news-sentiment framework.

**Sources**: [Interactive Polls Boost Engagement 2026 — Polling.com Blog](https://blog.polling.com/how-interactive-polls-boost-engagement-and-insights-in-2025/)

---

### 13. Blind (TeamBlind)

**What structured input it captures**
Freeform text posts and comments. Does support upvotes/downvotes and binary/multiple-choice polling within posts. Primarily a Q&A and discussion forum.

**Does it show users how their opinion compares to others?**
Partially: upvote counts and aggregate poll results are visible. No personal percentile. Anonymity and professional verification create a distinct signal (tech industry professionals).

**Active user base and engagement metrics**
9 million+ verified professionals from 300,000+ companies. Significant concentration in US tech companies.

**Proximity to Nucleus value prop**
Very low. Not structured around news events, does not use a slider instrument.

**Sources**: [Blind — Wikipedia](https://en.wikipedia.org/wiki/Blind_(app)) | [Harvard Digital Innovation: Blind](https://d3.harvard.edu/platform-digit/submission/blind-building-and-scaling-anonymous-community/)

---

### 14. Polly (for Slack/Teams)

**What structured input it captures**
Multiple-choice polls, NPS surveys, open-ended text, star ratings, and pulse sentiment scales (1–5 numeric). AI-generated sentiment summaries from open-ended responses. Deployed in Slack, Teams.

**Does it show users how their opinion compares to others?**
Yes, within a team context: aggregate results and AI trend summaries are shared back to the channel. No individual percentile positioning.

**Active user base and engagement metrics**
Used by 40%+ of the Fortune 100. Over 64 million responses and 10 million "pollys" sent. Primarily a B2B tool.

**Proximity to Nucleus value prop**
Very low. Workplace engagement tool; lacks news event anchor and personal percentile feedback.

**Sources**: [Polly.ai](https://www.polly.ai/) | [3 Best Slack Poll Apps 2025 — Geekbot](https://geekbot.com/blog/slack-poll/)

---

### 15. Mentimeter

**What structured input it captures**
Live polling with multiple input types: multiple choice, word cloud, Q&A, ranking, rating scales, and a **scales/slider question type**.

**Does it show users how their opinion compares to others?**
Yes — live aggregate visualization shown to all participants (word clouds, bar charts, scatter plots) during sessions. The most visually sophisticated group comparison on this list. But session-scoped only, not persistent.

**Active user base and engagement metrics**
400 million users worldwide. 80,000 enterprise customers. $38M–$45M revenue in 2024. $43M raised over 8 rounds. $349M valuation (June 2024). Headquartered in Stockholm, founded 2014.

**Proximity to Nucleus value prop**
Low for consumer news, moderate for the mechanics. Mentimeter is the only platform that actually uses a slider input AND shows group comparison results. But it's a live presentation tool, not a persistent consumer news product. No news event framework, no ongoing community, and no concept of personal percentile rank.

**Sources**: [Mentimeter](https://www.mentimeter.com/) | [How Mentimeter hit $38M revenue — Latka](https://getlatka.com/companies/mentimeter)

---

### 16. Kahoot

**What structured input it captures**
Multiple-choice quiz questions (game format). Primarily knowledge-testing, not opinion-expressing. No sliders, no sentiment scales.

**Does it show users how their opinion compares to others?**
Yes — live leaderboards and score comparisons. But the comparison is on quiz performance (right/wrong), not on opinions or sentiment.

**Active user base and engagement metrics**
1 billion+ players per year. 9 billion+ participant sessions cumulative. Revenue ~$46M in 2022; taken private by Goldman Sachs in 2023 at ~$1.5B.

**Proximity to Nucleus value prop**
Very low. A gamified knowledge test, not a sentiment/opinion tool.

**Sources**: [Kahoot Statistics 2025 — Expanded Ramblings](https://expandedramblings.com/index.php/kahoot-statistics-facts/)

---

### 17. YouGov

**What structured input it captures**
Structured survey questions: multiple choice, agree/disagree scales (Likert), and tracking questions. YouGov Today shows users questions they can answer and then reveals aggregate results after answering.

**Does it show users how their opinion compares to others?**
Yes — and this is the closest competitor on this dimension. After answering a YouGov Today question, the platform shows aggregate distribution of how others answered, broken down by demographics (age, gender, party affiliation). However, it shows aggregate % distributions — it does **NOT** show a personal percentile rank.

**Active user base and engagement metrics**
26 million global panelists as of 2025. Public company on London Stock Exchange (YOU). Operates in 55+ countries. Users earn points for completing surveys, redeemable for cash or vouchers.

**Proximity to Nucleus value prop**
Moderate — the highest of all surveyed platforms for structured opinion + comparison. YouGov Today shows aggregate results tied to specific questions about news events after you answer. But: (1) input is multiple-choice or Likert, not a multi-axis slider; (2) comparison shows group distributions, not a personal percentile rank; (3) it's a market research panel with incentive-driven participation; (4) the experience is survey-like rather than news-discovery-driven.

**Sources**: [YouGov Ratings FAQ](https://today.yougov.com/about/ratings-faq) | [YouGov — Wikipedia](https://en.wikipedia.org/wiki/YouGov)

---

### 18. Ranker.com

**What structured input it captures**
Ranked-choice voting: users rank items in lists by voting them up or down. Binary directional voting on individual list items. Primarily entertainment, pop culture, and sports.

**Does it show users how their opinion compares to others?**
Yes — live rankings update based on votes. But no personal percentile, and coverage of hard news/current events is minimal.

**Active user base and engagement metrics**
15 million monthly visitors (late 2025). 1 billion+ cumulative votes. 8 million votes per month. $53.5M revenue in 2024. Founded 2009.

**Proximity to Nucleus value prop**
Very low. Pop culture and entertainment rankings, not structured news event sentiment.

**Sources**: [Ranker — Wikipedia](https://en.wikipedia.org/wiki/Ranker) | [About Ranker's Voting System](https://www.ranker.com/howrankingswork)

---

### 19. Newsvoice

**What structured input it captures**
Community upvoting of news story importance, plus collaborative news summaries. The upvote is a single binary importance signal; sources are tagged with political lean. No sliders, no multi-axis sentiment.

**Does it show users how their opinion compares to others?**
No individual comparison. Upvote counts visible to all.

**Active user base and engagement metrics**
Small; primarily Northern European user base.

**Proximity to Nucleus value prop**
Low. Captures importance signal (upvote) but not emotional/sentiment response and no personal positioning.

**Sources**: [Best Newsvoice Alternatives — Product Hunt](https://www.producthunt.com/products/newsvoice/alternatives)

---

## Platforms That Have Shut Down (Last 5 Years)

### CrowdTangle (Meta) — Shut down August 14, 2024
CrowdTangle was Meta's social analytics tool letting journalists, researchers, and NGOs track trending posts and measure engagement on Facebook and Instagram in real time. Meta began breaking up the team in 2021 and formally started shutdown proceedings in 2022. The stated reason was that it "does not provide a representative picture" of platforms. The real concern, per journalism and tech policy analysts, was that CrowdTangle made Meta's misinformation problem too visible. The replacement (Meta Content Library) is restricted to academic researchers only. This shutdown is widely cited as a warning about the fragility of civic-tech products dependent on platform-controlled data.

**Sources**: [Bloomberg: Meta Shuts Down CrowdTangle](https://www.bloomberg.com/news/articles/2024-08-14/meta-shuts-down-tool-used-for-tracking-online-misinformation) | [NPR: Meta shutters CrowdTangle](https://www.npr.org/2024/08/14/nx-s1-5074143/meta-shutters-tool-used-to-fight-disinformation-despite-outcry) | [TechPolicy.Press: Loss of CrowdTangle](https://www.techpolicy.press/why-the-loss-of-crowdtangle-signals-trouble-for-civic-tech-products/)

### Manifold Markets Sweepcash (Real-Money Features) — March 2025
Manifold Markets shut down its real-money "Sweepcash" betting feature in March 2025, following regulatory pressure on the sweepstakes model. Daily active traders fell to a record low of ~886, down from a peak of 2,000+. Continues as play-money only but with substantial engagement decline.

**Sources**: [Manifold Markets Review 2026 — CryptoNews](https://cryptonews.com/cryptocurrency/manifold-markets-review/)

### Vox Media's Chorus — Wind-down completed 2023
Chorus was Vox Media's proprietary CMS that included embedded audience reaction tools. When Vox pivoted to focus on its core ad/subscription business, Chorus was wound down. Existing customers had 18 months to migrate. Showed the difficulty of sustaining publisher-integrated audience engagement modules.

**Sources**: [Axios: Vox Media stops using Chorus](https://www.axios.com/2023/07/18/vox-media-chorus) | [Nieman Lab: Vox will no longer license Chorus](https://www.niemanlab.org/reading/vox-media-will-no-longer-license-chorus-its-cms-software/)

### Parler — Effectively defunct as a major platform by 2023
Launched as a "free speech" conservative social network. After AWS deplatformed it post-January 6th, 2021, it was briefly resurrected and then backed out of an acquisition by Ye (Kanye West); it was subsequently delisted from major app stores. By 2023, it had lost its main user base. Raised estimated $56M from conservative donors. Relaunched in limited form in 2024 but with minimal traction.

**Sources**: [Parler — Wikipedia](https://en.wikipedia.org/wiki/Parler)

### Hearken — Pivoted away from structured opinion, 2022–2023
Hearken built tools for newsrooms to let the public submit questions that journalists then answered, using community upvoting to surface most-wanted questions tied to news events. Announced it was "evolving" away from its original tech product toward consulting in 2022–2023. Relevant because it shows how hard it is to build a sustainable newsroom-integrated opinion product.

**Sources**: [Hearken: Evolving — Medium](https://medium.com/we-are-hearken/hearken-is-evolving-heres-how-dd21a3d1d872)

---

## Funding Summary for VC-Backed Entrants

| Platform | Total Raised | Key Investors | Latest Valuation |
|---|---|---|---|
| Polymarket | $200M+ | Founders Fund, ICE/NYSE | $9B–$15B (2025) |
| Kalshi | $1.3B+ (cumulative) | Paradigm, Sequoia, a16z, YC | $11B (Dec 2025) |
| Manifold Markets | <$5M (bootstrapped/small rounds) | — | N/A |
| Mentimeter | $43M | Various | $349M (Jun 2024) |
| Kahoot | ~$215M raised; taken private | Goldman Sachs | ~$1.5B (2023) |
| YouGov | Public (LSE: YOU) | — | ~$400M market cap |
| Ground News | $0 (subscriber-funded) | — | N/A |
| AllSides | Undisclosed (private) | — | N/A |
| Polis | ~$1M grants | Nonprofit grants | N/A (nonprofit) |

---

## The Whitespace Map: What Does Nucleus Offer That None of These Do?

### The Three-Part Value Proposition Broken Down

Nucleus's core feature set can be broken into three distinct components:

1. **Event-anchored input**: The sentiment rating is tied to a specific, editor-curated or algorithmically-surfaced news event — not a creator's arbitrary poll question, not a market-defined binary outcome, not a deliberation prompt.

2. **Multi-axis slider sentiment**: Three separate slider dimensions capturing orthogonal facets of sentiment (e.g., anger/hope/surprise, or personal impact/moral judgment/emotional intensity). Not binary, not multiple choice, not a single Likert scale.

3. **Personal percentile rank**: After rating, the user sees their exact percentile position in the distribution of all raters — not "56% agreed with you," but "you are in the 23rd percentile on dimension 1, the 71st percentile on dimension 2, and the 44th percentile on dimension 3."

### The Gap Analysis (Mapped Against All Surveyed Platforms)

| Feature | Nucleus | X Polls | Polis | Metaculus | Mentimeter | YouGov Today | Polymarket |
|---|---|---|---|---|---|---|---|
| News event anchor | Yes | Partial (any topic) | Yes (curated) | Yes (question) | No (presentation) | Partial (surveys) | Yes (binary outcome) |
| Multi-axis slider input | **Yes** | No (binary/MC) | No (binary vote) | No (probability) | Yes (in sessions) | No (Likert) | No (price) |
| Consumer product | Yes | Yes | No | No | No | Partial | Yes |
| Personal percentile rank | **Yes** | No | No | Partial | No | No | No |
| Real-time personal feedback | Yes | Aggregate only | Cluster only | Distribution view | Session only | Aggregate only | Market price only |

The clearest gap: **No consumer-facing product combines all three of these elements.** Every platform that provides a personal-position-in-distribution feedback loop (Metaculus, Polis, YouGov in weak form) either (a) requires expert-level forecasting knowledge, (b) is a B2B/research tool, or (c) uses aggregate group percentages rather than personal percentile ranks. Every product that is consumer-facing and news-oriented (X polls, Reddit polls, Instagram Story polls) shows only aggregate group results with no personal positioning. Mentimeter is the only platform with a slider input AND group comparison visualization, but it's a live presentation tool with no persistent user community or news event framework.

### Is the Gap Real or Trivially Bridgeable?

**Arguments that the gap is real and durable:**

1. **Structural incentives don't reward this.** Social platforms maximize engagement through rage and social validation. A percentile rank showing you are in the 40th percentile on emotional intensity is informationally interesting but not algorithmically viral. Platforms have little incentive to add this feature because it doesn't optimize for time-on-platform.

2. **Prediction markets don't want sentiment; they want probability.** Polymarket and Kalshi are growing explosively ($22B+ in notional volume 2025). They have no reason to add a "how do you feel about this" dimension that doesn't sharpen probability estimates.

3. **Survey platforms don't want the consumer UX problem.** YouGov, Morning Consult, and Pew have the structured data infrastructure but are B2B intelligence companies. Building a consumer product with notification-driven news engagement, real-time percentile feedback, and a discovery feed is a different product with different GTM.

4. **The three-slider architecture is unique.** Multi-dimensional emotional profiling of news reactions is academically established (LIWC, dimensional emotion models) but has never been productized for consumer news. The psychological hook — "where do I sit in the spectrum of how people feel about this?" — exploits social comparison theory in a way that is more nuanced and less toxic than "how many likes did my opinion get?"

**Arguments that the gap is bridgeable:**

1. **X could add it tomorrow.** X already has polls and 600M users consuming news. Adding a slider reaction attached to a news post, plus a percentile display, is technically trivial. The reason they haven't is incentive-alignment, not capability.

2. **Metaculus is one pivot away.** Metaculus already shows users their estimate versus the community distribution. Reformatting questions to capture sentiment rather than probability would bring them within one product iteration of Nucleus's value prop — albeit for a small, expert-leaning user base.

3. **YouGov Today is structurally analogous.** YouGov Today already does event + structured question + show-me-results-after-answering. The gap is (a) slider vs. Likert, (b) percentile vs. aggregate %, and (c) real-time news peg vs. survey panel. These are meaningful but not insurmountable differences.

4. **The data is valuable to third parties, which creates acquisition risk.** If Nucleus demonstrates that multi-axis news sentiment data is a compelling signal (for brands, politicians, newsrooms, or advertisers), a Morning Consult, YouGov, or media company could acquire or replicate it. Morning Consult collects 30,000 structured survey interviews daily across 40+ countries; adding a slider sentiment dimension to news coverage is well within their operational capability.

### What Nucleus Offers That Is Genuinely Distinct (The Real Whitespace)

The specific combination of **consumer-grade news discovery + three-dimensional slider input + personal percentile rank feedback** in a mobile-first product does not exist anywhere in the current landscape as of March 2026. The closest adjacencies are:

- **YouGov Today** (structured input on news events, group comparison, but no slider and no percentile rank)
- **Metaculus** (personal position vs. distribution, but for probability forecasts by experts, not sentiment by general consumers)
- **Mentimeter** (slider input + group visualization, but requires a live presentation session and has no persistent news community)
- **Instagram Emoji Slider** (consumer-facing continuous sentiment input, but entirely private results and trivial use case)

The whitespace is **not trivially bridgeable by the existing players** in the short term because each faces structural disincentives: social platforms optimize for engagement loops that reward extremity over nuance; prediction markets need probability signals not sentiment signals; survey companies are B2B-first and consumer-product-second; civic tech tools (Polis) lack the consumer UX investment and mass-market go-to-market.

**The main risk to Nucleus's differentiation** is not that a competitor bridges the gap technically (trivial) but that one of the large-scale platforms (X, Instagram, YouTube, Reddit) decides this feature is worth bolting on as a stickiness mechanism for their news-following users. That is a platform risk, not a product differentiation problem — and it is the same risk facing every news-adjacent consumer startup in 2026.

---

## Sources (Consolidated)

- [Twitter/X Benchmarks 2026 — Enrich Labs](https://www.enrichlabs.ai/blog/twitter-x-benchmarks-2025)
- [X Polls Help — X](https://help.x.com/en/using-x/x-polls)
- [Community Notes — Wikipedia](https://en.wikipedia.org/wiki/Community_Notes)
- [NBC News: Community Notes use has plummeted 2025](https://www.nbcnews.com/tech/social-media/x-twitter-community-notes-disappear-data-rcna210710)
- [UW News: Community Notes reduce virality of false info](https://www.washington.edu/news/2025/09/18/community-notes-x-false-information-viral/)
- [Pol.is — Wikipedia](https://en.wikipedia.org/wiki/Pol.is)
- [Computational Democracy Project FAQ](https://compdemocracy.org/faq/)
- [AllSides Media Bias Chart](https://www.allsides.com/media-bias/media-bias-chart)
- [Ground News — Wikipedia](https://en.wikipedia.org/wiki/Ground_News)
- [Polymarket Volumes — CCN](https://www.ccn.com/news/crypto/polymarket-7-5-billion-2025-prediction-markets/)
- [ICE invests $2B in Polymarket — Fortune](https://fortune.com/crypto/2025/10/07/polymarket-2-billion-intercontinental-exchange-new-york-stock-exchange-9-billion/)
- [Bloomberg: Polymarket $15B valuation](https://www.bloomberg.com/news/articles/2025-10-23/polymarket-is-seeking-funding-at-a-valuation-of-up-to-15-billion)
- [Kalshi $11B Valuation — BusinessWire](https://www.businesswire.com/news/home/20251202735424/en/Kalshi-Reaches-$11-Billion-Valuation-as-App-Takes-over-America)
- [Kalshi — Wikipedia](https://en.wikipedia.org/wiki/Kalshi)
- [Metaculus — Wikipedia](https://en.wikipedia.org/wiki/Metaculus)
- [TIME: AI Learning to Predict the Future](https://time.com/7318577/ai-model-forecasting-predict-future-metaculus/)
- [Manifold Markets — Wikipedia](https://en.wikipedia.org/wiki/Manifold_(prediction_market))
- [Rasmussen: 67% of Reddit Users Find Good Source for News](https://www.rasmussenreports.com/public_content/lifestyle/general_lifestyle/april_2025/67_of_reddit_users_find_it_a_good_source_for_news)
- [Instagram Stories Statistics 2025 — Amra & Elma](https://www.amraandelma.com/total-instagram-stories-statistics/)
- [Blind — Wikipedia](https://en.wikipedia.org/wiki/Blind_(app))
- [Polly.ai](https://www.polly.ai/)
- [Mentimeter](https://www.mentimeter.com/)
- [How Mentimeter hit $38M revenue — Latka](https://getlatka.com/companies/mentimeter)
- [Kahoot Statistics 2025 — Expanded Ramblings](https://expandedramblings.com/index.php/kahoot-statistics-facts/)
- [YouGov Ratings FAQ](https://today.yougov.com/about/ratings-faq)
- [YouGov — Wikipedia](https://en.wikipedia.org/wiki/YouGov)
- [Ranker — Wikipedia](https://en.wikipedia.org/wiki/Ranker)
- [Bloomberg: Meta Shuts Down CrowdTangle](https://www.bloomberg.com/news/articles/2024-08-14/meta-shuts-down-tool-used-for-tracking-online-misinformation)
- [NPR: Meta shutters CrowdTangle](https://www.npr.org/2024/08/14/nx-s1-5074143/meta-shutters-tool-used-to-fight-disinformation-despite-outcry)
- [TechPolicy.Press: Loss of CrowdTangle](https://www.techpolicy.press/why-the-loss-of-crowdtangle-signals-trouble-for-civic-tech-products/)
- [Axios: Vox Media stops using Chorus](https://www.axios.com/2023/07/18/vox-media-chorus)
- [Parler — Wikipedia](https://en.wikipedia.org/wiki/Parler)
- [Hearken: Evolving — Medium](https://medium.com/we-are-hearken/hearken-is-evolving-heres-how-dd21a3d1d872)
- [Bloomberg: Prediction Markets Polymarket Kalshi 2026](https://www.bloomberg.com/features/2026-prediction-markets-polymarket-kalshi/)
- [Mercury News: Prediction Markets political boom 2026](https://www.mercurynews.com/2026/03/22/prediction-markets-are-seeing-a-political-boom-heres-what-they-might-mean-for-californias-governor-race/)

## Validation Result

Output length: 37426 chars | Verification: needs_revision

## My Notes
<!-- Write below this line. The harness reads this on re-run. Use #redo to re-run this task, #skip to skip it, #pivot:<new direction> to change the approach. -->