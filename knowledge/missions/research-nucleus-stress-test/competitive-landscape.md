# Nucleus Competitive Audit: Structured Public Opinion on News Events
**Date:** March 23, 2026
**Scope:** All platforms that capture structured public opinion on news events, evaluated against the Nucleus value proposition.

---

## Nucleus Value Proposition (Reference Frame)

Mobile app pairing **5–10 curated daily news events** with **3 sliders** (Concern, Optimism, Significance — 0–100 scale). Users submit before unlocking **aggregate distribution curves + percentile ranking**. No comments. No social graph. Core hook: *"You are more concerned than 78% of users."*

The four defining constraints:
1. **Daily curated news events** (editorial curation, not user-generated)
2. **Structured sentiment sliders** (not binary polls, not free text)
3. **Personal percentile positioning vs. crowd** (the identity hook)
4. **No comments / no social graph** (by design)

---

## Platform-by-Platform Findings

---

### 1. Twitter / X Polls

**What it does:** Twitter/X Polls are native binary or multiple-choice polls embedded in tweets, visible to followers or the public, with results revealed immediately after voting.

**Proximity to Nucleus value prop:**
- No news curation. Polls are user-generated and atomized — there is no editorial layer selecting which events to ask about.
- No sliders. Responses are binary or multiple-choice only (up to 4 options); no continuous sentiment scale.
- Results are shown to all after voting, but there is zero personal percentile positioning. You see aggregate percentages only — never "you voted X, which is higher than Y% of respondents."
- No crowd distribution curve; simple bar-chart percentages.

**Proximity score:** Very Low. Shares the "vote before seeing results" mechanic implicitly (results only update after you vote), but lacks every structural element of Nucleus.

**User engagement patterns:**
- Platform-wide: ~611 million MAU, ~245–259 million DAU (2025). 29 minutes/day average session. 72.6% monthly retention rate; 82% among Premium users. [(Source: Sprout Social)](https://sproutsocial.com/insights/twitter-statistics/)
- Polls specifically: No isolated DAU/MAU data for the poll feature. Polls are a minor feature — used largely by politicians, journalists, and brands as a quick temperature-check tool. They are embedded in the feed, not a destination.
- Engagement with individual polls is highly variable and follower-count dependent. No evidence of poll-driven retention.

**Why users engage / don't:**
- Engage: Fast, zero-friction, one tap. Satisfies curiosity about where others stand.
- Don't retain: Polls are ephemeral. No identity, no progression, no personal data trail. No reason to return to a specific poll. Completion of a poll is a dead end.

**Social comparison hook:** Minimal. You see aggregate % after voting. No "you vs. crowd" framing. No percentile. No demographic breakdown. No ongoing personal context.

**Retention evidence:** None specific to polls. Platform retention is driven by the social graph, content feed, and algorithmic amplification — not by the poll feature.

---

### 2. X Community Notes

**What it does:** A crowdsourced fact-checking system where contributors attach contextual notes to potentially misleading posts; notes become visible when raters with divergent viewpoints collectively mark them "Helpful."

**Proximity to Nucleus value prop:**
- Not a polling or sentiment product. There are no sliders, no news events paired with structured opinion collection, and no percentile feedback.
- Community Notes is a content moderation / epistemic correction tool, not an opinion measurement tool.

**Proximity score:** None. Entirely different product category.

**User engagement patterns:**
- 126,000+ English contributors submitted at least one note in 2024 (more than double 2023). [(Source: DDIA Report)](https://ddia.org/en/a-deep-dive-into-xs-community-notes-report)
- Only ~4.9% of submitted notes were ever published by early 2025 (down from 9.5% in 2023). High contributor frustration.
- After a note is applied: reposts drop 46%, likes drop 44%, views drop 14%. The product reduces engagement rather than driving it.

**Social comparison hook:** None by design. The system is about content judgment, not personal opinion positioning.

**Retention evidence:** Contributor base grew, but the bottleneck (sub-5% publication rate) creates friction that limits retention. Not a consumer retention product.

---

### 3. Polis (pol.is)

**What it does:** An open-source deliberative democracy platform where participants vote agree/disagree/pass on short text statements; machine learning clusters participants by opinion similarity and surfaces consensus and divisive statements.

**Proximity to Nucleus value prop:**
- News events: Polis is deployed issue-by-issue (e.g., ride-sharing regulation in Taiwan), not as a daily news-event stream. It has no editorial curation layer.
- Structured sentiment: Agree/disagree/pass is binary, not a continuous slider. No multi-dimensional sentiment (no separate "Concern" vs. "Optimism" axes).
- Social comparison: Polis shows aggregate cluster data but does not provide personal percentile positioning. You can see which "group" you belong to, but not "you are more X than Y% of participants."
- No social graph, no comments — this does align with Nucleus's no-comments design.

**Proximity score:** Low-Medium. Shares the deliberate anonymity and aggregate results logic, but it is a governance/research tool (B2G/B2B), not a consumer daily-habit app.

**User engagement patterns:**
- Not designed for DAU/MAU. Individual Polis conversations have 900–4,000 active participants. [(Source: vTaiwan/Participedia)](https://participedia.net/method/polis)
- Taiwan's vTaiwan mailing list reached 200,000 by 2020, but only thousands participate in any single conversation.
- Polis has no retention mechanics. It is a one-time or episodic deliberation tool, not a daily habit product.

**Social comparison hook:** Weak. You learn which cluster you're in, but there's no personal score or percentile.

**Retention evidence:** None for consumer use. Polis is used institutionally (governments, think tanks) and has no meaningful consumer MAU.

---

### 4. AllSides

**What it does:** A media bias rating platform that presents news stories from Left, Center, and Right sources side-by-side, allowing users to assess media bias and read across the political spectrum.

**Proximity to Nucleus value prop:**
- News events: AllSides curates stories but pairs them with source perspectives, not user opinion collection.
- Structured sentiment: None. Users can rate whether they agree or disagree with a bias rating ("Blind Bias Survey"), but this is not a continuous slider and not tied to specific news events.
- Social comparison: None. There is no "you vs. crowd" mechanic. Users can see aggregate bias rating votes but not their own positioning vs. others.

**Proximity score:** Very Low. AllSides is a media literacy tool, not an opinion measurement platform.

**User engagement patterns:**
- ~2.8M total monthly visits (November 2024). [(Source: SimilarWeb via search)](https://www.similarweb.com/website/allsides.com/)
- Traffic declined ~11.64% month-over-month in 2025.
- Content consumed passively. No login-required engagement loop.

**Social comparison hook:** None.

**Retention evidence:** Traffic is driven by election cycles and political events. No evidence of daily habit formation or sustained non-election retention.

---

### 5. Ground News

**What it does:** A news aggregation app that rates the political bias of sources and tracks coverage blind spots (stories covered only by Left or Right), helping users diversify their news diet.

**Proximity to Nucleus value prop:**
- News events: Yes — Ground News curates real news stories daily. This is the closest overlap with Nucleus's event curation layer.
- Structured sentiment: No sliders for user emotional response. Users can edit bias ratings (a source-level rating, not a personal sentiment) but cannot rate their emotional reaction to a story.
- Social comparison: Ground News has a "My News Bias" feature (Vantage tier) that shows your reading habits — but this compares your source diet against a political spectrum, not your emotional response vs. the crowd. It does not show "you are more concerned than 78% of readers." [(Source: Ground News Help)](https://help.ground.news/en/articles/3189505)
- Bias Comparison Summary shows how Left/Center/Right outlets cover the same story — a source-level comparison, not a user-vs-user percentile.

**Proximity score:** Low-Medium on event curation; Near-Zero on structured sentiment + percentile comparison. Ground News compares sources; Nucleus would compare people.

**User engagement patterns:**
- Estimated annual revenue: ~$5.7M. [(Source: Growjo)](https://growjo.com/company/Ground_News)
- Staff grew 52% year-over-year. App Store rating: positive, 4+ stars.
- Web traffic: ground.news sees moderate monthly traffic, with ~1% month-over-month growth as of late 2025.
- Subscription model (Pro, Premium, Vantage tiers). Paying subscriber base not disclosed publicly.

**Social comparison hook:** Minimal. "My News Bias" shows your reading pattern vs. an abstract political spectrum — not vs. other users. No percentile. No emotional sentiment layer.

**Retention evidence:** Subscription revenue suggests a retained paying base, but no public DAU/MAU data. Reviews cite appreciation for the bias aggregation tool but fatigue from the subscription paywall.

---

### 6. Polymarket

**What it does:** The world's largest decentralized prediction market, where users trade on the probability of real-world events resolving a certain way, using real money (USDC on blockchain).

**Proximity to Nucleus value prop:**
- News events: Yes — Polymarket creates markets around real news events (elections, geopolitics, sports, macro). Strong overlap here.
- Structured sentiment: No sliders. Users place probabilistic bets (0–100% implied probability), which is mathematically similar to a continuous scale but is a financial transaction, not an emotional rating.
- Social comparison: Polymarket has a leaderboard ranked by PnL, not by emotional insight. There is no "you feel X vs. 78% of participants" — the comparison is about trading accuracy and profit.
- No social graph by default, but a comment section was added and became a core engagement driver.

**Proximity score:** Low. Shares news-event pairing and numerical confidence input, but the mechanism (financial stakes, trading) and the output (profit/loss) are entirely different from emotional sentiment comparison.

**User engagement patterns:**
- Peak: ~300,000 DAU on Election Day, November 5, 2024. [(Source: Polymarket/Fortune)](https://fortune.com/2025/07/24/polymarket-and-kalshi-user-numbers/)
- Post-election collapse: dropped to 5,000–10,000 DAU by mid-2025.
- Recovery: ~72,000 DAU by November 2025 with broader market diversification.
- 1.2M+ unique traders in 2024; $22B total volume in 2025.
- Monthly retention: 35% (2024); another source claims Polymarket outperforms 85% of crypto platforms.

**Social comparison hook:** Leaderboard (PnL-based). No personal emotional positioning vs. crowd. The hook is financial competition, not identity-level self-awareness.

**Retention evidence:** Extreme event-driven volatility. Election-cycle dependency is a severe structural retention problem — 90%+ DAU decline post-election. Not a daily habit outside high-salience events.

---

### 7. Metaculus

**What it does:** A forecasting platform where users submit probabilistic predictions on future events; predictions are scored by accuracy after resolution, with a leaderboard and tournament system.

**Proximity to Nucleus value prop:**
- News events: Yes — Metaculus questions are tied to real-world events (geopolitics, AI, science). Strong event anchoring.
- Structured sentiment: Users submit a probability (0–100%), analogous to a continuous scale, but it represents a predictive belief, not an emotional reaction.
- Social comparison: Metaculus has a robust scoring system comparing you to (a) an impartial baseline and (b) all other forecasters (Peer Score). Leaderboards by accuracy, question authorship, and comment quality. [(Source: Metaculus FAQ)](https://www.metaculus.com/faq/)
- Comments are central to Metaculus. Social graph is implicit. This is the opposite of Nucleus's no-comment design.

**Proximity score:** Medium. Metaculus is the closest existing product to Nucleus's "score yourself vs. crowd on news events" mechanic — but it measures predictive accuracy, not emotional sentiment, and it requires deep intellectual engagement rather than a 30-second slider interaction.

**User engagement patterns:**
- ACX/Metaculus 2025 forecasting contest: 3,000+ forecasters (2x year-over-year). [(Source: Astral Codex Ten)](https://www.astralcodexten.com/p/try-the-2025-acxmetaculus-forecasting)
- Bridgewater x Metaculus contest: 17,000+ competitors (10x year-over-year).
- Total predictions projected to reach 3.49M by October 2025.
- No public DAU/MAU data. User base is engaged but niche (EA community, professional forecasters, rationalists).

**Social comparison hook:** Strong for its audience. Peer Score directly compares you to other forecasters. Leaderboards and medals create competitive identity. But the audience skews highly analytical; the mechanic is not accessible to mainstream users.

**Retention evidence:** Strong within its niche. Tournament participation growing 10x year-over-year suggests sticky engagement, but total user numbers remain small (tens of thousands, not millions).

---

### 8. Reddit Polls

**What it does:** Native polls embedded in Reddit posts, allowing subreddit members to vote on questions with 2–6 options; results visible after voting.

**Proximity to Nucleus value prop:**
- News events: No editorial curation. Polls are user-created within subreddits. No structured daily event pairing.
- Structured sentiment: Binary/multiple-choice only. No sliders.
- Social comparison: You see aggregate % after voting. No personal percentile. No demographic breakdown in standard polls. Reddit added a "Predictions" feature for some subreddits (sports outcomes) but no emotional sentiment layer.
- Comments are core to Reddit — the opposite of Nucleus.

**Proximity score:** Very Low.

**User engagement patterns:**
- Reddit: ~1.2B MAU (2025 estimates), 97.4M DAU. [(Source: Digital Web Solutions)](https://www.digitalwebsolutions.com/blog/reddit-statistics/)
- Polls specifically: A Super Bowl poll in r/NFL received 9,100 votes in 48 hours — ~5x more engagement than average posts. [(Source: Social Media Today)](https://www.socialmediatoday.com/news/reddit-launches-polls-providing-another-way-for-redditors-to-engage-with-c/574643/)
- Polls activate lurkers (98%+ of Reddit users never post), but engagement is concentrated in large subreddits.

**Social comparison hook:** None beyond aggregate %. No personal score, no percentile, no progression.

**Retention evidence:** Polls are not a retention mechanism for Reddit — the social graph and content feed drive retention. Polls are a content type within a retention system, not a retention system themselves.

---

### 9. Instagram Story Polls / Emoji Slider

**What it does:** Instagram Stories offer native poll stickers (binary A/B vote) and emoji slider stickers (drag a sliding emoji on a 0–100 scale) that followers can interact with; creators see results, respondents see current average after voting.

**Proximity to Nucleus value prop:**
- **The emoji slider is structurally the closest mechanic to a Nucleus slider.** It is a continuous 0–100 scale with an emoji anchor. After sliding, users see the current average response — not a distribution curve, not a personal percentile.
- News events: Zero editorial curation. Sliders are creator-defined and tied to creator content (brands, influencers, personal life), not curated news events.
- Social comparison: After sliding, users see the average position. No percentile ("you slid higher than 78% of responders"). No distribution curve.
- No social graph for the poll itself, but deeply embedded in creator follow relationships.

**Proximity score:** Low-Medium on the slider mechanic; Very Low on everything else.

**User engagement patterns:**
- Instagram: ~2B MAU. Stories see billions of daily interactions.
- Story completion rates: average 23.8% exit after slide 1, stabilizing to ~13.3% exit by slide 9. [(Source: SocialInsider)](https://www.socialinsider.io/social-media-benchmarks/instagram-stories-benchmarks)
- Emoji slider adoption: described as "essential engagement boosters" especially among Gen Z. A wellness influencer case study showed Story completion rate doubling (34% → 68%) after consistent slider use.

**Social comparison hook:** Minimal. "Current average" shown after submitting — not a personal percentile. The creator sees breakdowns; respondents do not.

**Retention evidence:** Sliders improve retention *within a Story sequence*, but do not drive app retention. Instagram retention is driven by the social graph, Reels algorithm, and DMs — not polls.

---

### 10. YouTube Community Polls

**What it does:** Creator-posted polls (text, image, or GIF options) in the YouTube Community/Posts tab, visible to subscribers; results shown after voting with simple percentage breakdown.

**Proximity to Nucleus value prop:**
- No news curation. Creator-controlled, not editorially curated current events.
- Binary/multiple choice only. No sliders.
- After voting, subscribers see aggregate %. No percentile, no distribution curve.
- Comments enabled — opposite of Nucleus.

**Proximity score:** Very Low.

**User engagement patterns:**
- YouTube: 2.7B+ MAU. Community polls drive high engagement vs. regular posts — creators report 63%+ participation on poll posts. [(Source: vidIQ)](https://vidiq.com/blog/post/youtube-stats-small-creator-journey/)
- Polls are a creator-to-audience engagement tool, not a peer-comparison tool.

**Social comparison hook:** None. You see aggregate %, which is less than even Instagram's "current average after you vote."

---

### 11. Blind (Workplace App)

**What it does:** An anonymous professional community for verified employees to discuss workplace issues, compensation, company culture, and career topics without revealing their identity; verified via work email.

**Proximity to Nucleus value prop:**
- No news curation. Content is user-generated workplace discussion.
- Structured sentiment: None. Blind has polls occasionally, but the core format is text posts with upvotes — not sliders.
- Social comparison: Blind has salary comparison tools (your comp vs. peers by role/level/location). This is a form of personal positioning vs. crowd, but in the compensation domain, not emotional response to news events.
- No social graph in the traditional sense (no public follower count), but it has company-specific feeds and upvote mechanics.

**Proximity score:** Very Low on product mechanics; Moderate on psychological model (anonymous community + implicit self-positioning).

**User engagement patterns:**
- 12M lifetime users (early 2024). [(Source: Gitnux)](https://gitnux.org/blind-statistics/)
- DAU/MAU ratio: 38% (2023, up from 29% in 2021) — a high stickiness metric for a professional app.
- Churn rate: 11% monthly (2023).
- Premium subscribers: 750,000 at ~$10/month (2023).

**Social comparison hook:** Yes, in compensation. The salary tool creates "you earn more/less than X% of peers" positioning. This is the closest analog to Nucleus's identity hook — but applied to money, not news sentiment. This comparison hook is a primary driver of Blind's retention.

**Retention evidence:** Strong. 38% DAU/MAU is significantly above social app averages. The anonymity + comparison mechanic creates a "safe to check, hard to stop" habit loop.

---

### 12. Yik Yak (Historical)

**What it does:** Hyperlocal anonymous social media app originally for college campuses (2013–2017), relaunched 2021, acquired by Sidechat in 2023. Users post short anonymous messages visible within a 5-mile radius.

**Proximity to Nucleus value prop:**
- No news curation, no structured sliders, no percentile comparison.
- Pure anonymous free-text social posting. Upvote/downvote mechanic.
- The only Nucleus-adjacent quality: anonymity removes social graph pressure.

**Proximity score:** None — different product category entirely.

**User engagement patterns:**
- Peak (2015): ~4M users, $400M valuation.
- Post-relaunch (2021–2023): ~3.5M installs cumulative.
- Acquisition by Sidechat (2023) was poorly received; user exodus due to university email requirement overriding prior anonymity model.
- UNC system banned the app in 2024 over cyberbullying. [(Source: TechCrunch)](https://techcrunch.com/2023/03/16/anonymous-app-sidechat-picks-up-rival-yik-yak-and-users-arent-happy/)

**Social comparison hook:** None by design.

**Retention evidence:** Failed product. Peak novelty failed to sustain engagement after cyberbullying scandals. Anonymity without structured prompts defaults to lowest-common-denominator content, destroying retention.

---

### 13. Agree.com

**What it does (clarification):** Agree.com is a **contract management and e-signature platform**, not an opinion aggregation product. It processes millions of business agreements monthly for photographers, freelancers, and SMBs.

**Proximity to Nucleus value prop:** None. This is a contract SaaS tool.

*Note: There does not appear to be a consumer opinion platform operating under this name as of March 2026.*

---

### 14. Remesh

**What it does:** An AI-native B2B market research platform enabling organizations to conduct live moderated conversations with up to 1,000 simultaneous participants, who vote on each other's open-ended responses in real time to surface consensus.

**Proximity to Nucleus value prop:**
- Remesh does have a real-time consensus-surfacing mechanic where participants vote on responses — this is mechanistically similar to Polis.
- It is entirely B2B/enterprise. No consumer app. No daily news events. No personal percentile positioning.
- Pricing is enterprise-tier (custom quotes, not publicly disclosed). [(Source: Capterra)](https://www.capterra.com/p/173121/Remesh/pricing/)
- In October 2025, launched Remy, an AI agent delivering "grounded, citation-backed insights" from participant data.

**Proximity score:** None for consumers. B2B research tool, not a consumer habit product.

**Social comparison hook:** None for end users. Research clients see aggregate data.

**Retention evidence:** Enterprise SaaS with high switching costs — retention is contract-driven, not engagement-driven.

---

### 15. Swayable

**What it does:** A B2B creative pre-testing platform using randomized control trial (RCT) survey experiments to measure how content (ads, messaging, concepts) changes minds; used by AirBnB, Amazon, Meta, T-Mobile, political campaigns. [(Source: Swayable](https://www.swayable.com/))

**Proximity to Nucleus value prop:** None for consumers. Swayable is a research tool for brands and campaigns — not a consumer-facing daily news opinion product.

**Social comparison hook:** None for end users.

**Retention evidence:** B2B SaaS. Not applicable.

---

### 16. Beehiiv Polls

**What it does:** Native poll and trivia features embedded in Beehiiv newsletter emails, allowing newsletter creators to collect subscriber votes on questions directly within the email; analytics integrated into creator dashboard.

**Proximity to Nucleus value prop:**
- No news curation. Creator-defined questions within newsletters.
- Binary/multiple-choice options; no sliders.
- Creators see response breakdowns; subscribers see aggregate % after voting but no personal percentile.
- No social graph, no comments in the poll itself (comments exist elsewhere).

**Proximity score:** Very Low. Newsletter-embedded polling is a creator tool, not a consumer opinion-on-news product.

**User engagement patterns:**
- Available on Grow ($49/month) and Scale plans.
- Newsletter creators report poll posts improving open rate and engagement metrics.
- No public subscriber-side DAU/MAU data.

**Social comparison hook:** None for subscribers.

---

### 17. Hearken

**What it does:** A journalism audience engagement platform where news organizations invite audiences to submit story questions; other readers vote on which questions they'd most like answered; newsrooms answer the most popular. [(Source: Hearken)](https://wearehearken.com/)

**Proximity to Nucleus value prop:**
- News events: Adjacent — but the direction is reversed. Hearken gathers audience questions *about* news, rather than collecting audience sentiment *on* news events.
- Structured sentiment: None. Binary voting on story ideas.
- Social comparison: None. No personal positioning vs. crowd.

**Proximity score:** Very Low. A journalism tool that involves audience participation in topic selection, not opinion measurement on current events.

**Retention evidence:** B2B tool for ~100 newsroom clients. No consumer retention model.

---

### 18. Perspective API (Google Jigsaw)

**What it does:** A machine learning API that scores the "toxicity" of text comments, used by online platforms to moderate discussions. Processing 500M+ API requests daily. [(Source: PRNewswire)](https://www.prnewswire.com/news-releases/googles-jigsaw-announces-toxicity-reducing-api-perspective-is-processing-500m-requests-daily-301223601.html)

**Proximity to Nucleus value prop:** None. This is an NLP API for content moderation, not a consumer product for opinion collection or social comparison.

---

### 19. Pollitics

**What it does:** An AI-powered opinion polling platform (launched September 2024 on Product Hunt) using synthetic "virtual voter" technology to generate simulated poll results from 40+ countries — not real human responses. Users input a question and receive AI-generated aggregate opinion data. [(Source: Pollitics)](https://pollitics.com/)

**Proximity to Nucleus value prop:**
- Not real human opinions — synthetic AI outputs. Structurally incomparable to Nucleus.
- No news event curation. No sliders. No personal percentile.

**Proximity score:** None.

---

### 20. Hunch (Social Polling App)

**What it does:** A poll-centric social media app (founded 2022, based in India/Dubai) where users create and answer polls on any topic anonymously; the algorithm matches users with others who have similar poll responses. Raised $23M Series A in March 2024. [(Source: YourStory)](https://yourstory.com/2024/03/hunch-anonymous-polls-social-media-app-startup-ai-moderation)

**Proximity to Nucleus value prop:**
- Polls are user-generated, not editorially curated to daily news events.
- Binary/multiple-choice. No sliders. No structured sentiment dimensions (Concern, Optimism, Significance).
- Social comparison: Hunch matches you with like-minded users based on poll similarity — this is a *social graph formation* mechanic, not a "you vs. crowd" percentile. The goal is connection, not self-positioning.
- Has comments. Has a social graph. Opposite of Nucleus's design.
- Pivoted toward dating/social discovery (app is now described as a dating app on Google Play).

**Proximity score:** Low. Shares poll-based opinion collection and some anonymity, but lacks news curation, slider mechanics, crowd distribution curves, and the percentile identity hook. The product is moving toward dating, not news opinion.

**User engagement patterns:**
- 2M+ users in India and the US (March 2024). 220,000 MAU.
- 115,000+ polls created; 10M+ total votes.

**Social comparison hook:** Matching (find similar people), not positioning (where do I stand vs. everyone). Different psychological mechanism.

**Retention evidence:** Small but growing. $23M raise suggests investor belief, but MAU (220,000) is modest relative to funding.

---

### 21. Show of Hands

**What it does:** One of the oldest polling apps on the App Store (14+ years), allowing users to answer daily questions and see results broken down by age, gender, income, political party, religion, and geography. Users can also create their own polls. [(Source: Show of Hands)](https://www.showofhands.com/)

**Proximity to Nucleus value prop:**
- News curation: Partial. Show of Hands does post editorial questions daily (including politics, health, news topics), giving it a curated daily question stream — closer to Nucleus than most platforms.
- Structured sentiment: Binary/multiple-choice only. No sliders, no multi-dimensional sentiment axes.
- Social comparison: After voting, users see aggregate results + demographic breakdowns. The "test if your opinion is in the majority" framing is directionally similar to Nucleus's percentile hook. However, it shows demographic segmentation (you voted X; 60% of Republicans agreed) rather than a personal percentile ("you are more concerned than 78%").
- A daily "guess the result" game is offered — users estimate what % chose each option before seeing results. This is a light social comparison mechanic.
- Comments are enabled — opposite of Nucleus's design.

**Proximity score:** Medium. Of all platforms researched, Show of Hands is closest to Nucleus's daily curated questions + opinion positioning mechanic. But it lacks sliders, lacks personal percentile framing, and has comments.

**User engagement patterns:**
- No public DAU/MAU data. App has been live since ~2011. Hundreds of thousands of questions and answers on the platform.
- User reviews note a politically skewed user base (historically right-leaning, more mixed recently).
- No recent press or funding announcements — appears to be a mature, low-growth product.

**Social comparison hook:** Moderate. Demographic breakdowns after voting create "how I compare to my group" awareness. The daily guess-the-result feature adds a light social comparison ritual. But no personal percentile score.

**Retention evidence:** 14+ years of operation suggests durable retention, but the product appears to have low growth momentum. No recent investment or media coverage.

---

## Additional Consumer Polling Apps (Last 5 Years)

### YouGov (today.yougov.com)

**What it does:** Panel-based polling research platform with a public-facing site showing survey results on news events, culture, and politics. Panel members earn points by completing surveys.

**Proximity to Nucleus:** Partial news-event alignment (YouGov surveys are often tied to news events). But the "results before participation" model is the opposite of Nucleus — YouGov publishes aggregate findings publicly, without requiring participants to submit first. No slider mechanics. No personal percentile positioning. No social comparison hook.

**User engagement:** 26M global panel members. Panel members are motivated by rewards points, not social identity. DAU/MAU not disclosed.

**Retention:** Incentive-driven (points/rewards). Not identity-driven.

---

## Summary Comparison Table

| Platform | Daily News Events | Structured Sliders | Personal Percentile vs. Crowd | No Comments/Social Graph | Consumer Habit App | Evidence of Strong Retention |
|---|---|---|---|---|---|---|
| Twitter/X Polls | No | No | No | No | Yes | Platform yes, polls no |
| X Community Notes | No | No | No | No | No | Partial (contributor growth) |
| Polis | No (episodic) | No | No | Yes | No | No |
| AllSides | Partial | No | No | Yes (read-only) | Partial | Weak |
| Ground News | Yes | No | No | Yes | Yes | Moderate (subscriptions) |
| Polymarket | Yes (events) | No (bets) | No (PnL rank) | No | Partial | Event-driven, volatile |
| Metaculus | Yes (questions) | No (probability) | Yes (peer score) | No | No | Strong in niche |
| Reddit Polls | No | No | No | No | Yes | Platform yes, polls no |
| Instagram Slider | No | Yes (emoji slider) | No | No | Yes | Platform yes, polls no |
| YouTube Polls | No | No | No | No | Yes | Platform yes, polls no |
| Blind | No | No | Salary only | Partial | Yes | Strong (38% DAU/MAU) |
| Yik Yak | No | No | No | Yes | Failed | Failed |
| Agree.com | N/A | N/A | N/A | N/A | No (contract SaaS) | N/A |
| Remesh | No | No | No | No | No (B2B) | B2B contract |
| Swayable | No | No | No | No | No (B2B) | B2B contract |
| Beehiiv Polls | No | No | No | Partial | No (creator tool) | N/A |
| Hearken | No | No | No | No | No (newsroom tool) | N/A |
| Perspective API | N/A | N/A | N/A | N/A | No (API) | N/A |
| Pollitics | No | No | No | No | Partial | N/A (synthetic data) |
| Hunch | No | No | No | No | Yes | Low (220K MAU) |
| Show of Hands | Partial/Yes | No | Partial | No | Yes | Moderate (14yr lifespan) |
| YouGov | Yes | No | No | Yes | Partial | Incentive-driven |

**Nucleus column:** **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | **Unknown (new)**

---

## Conclusions

### (a) Closest Existing Competitor to Nucleus

**Show of Hands** is the closest existing competitor, followed by **Metaculus** (for a different audience).

Show of Hands matches on: daily curated questions tied to news/politics/culture, vote-before-you-see-results flow, and aggregate breakdowns that imply "where do you stand vs. others." It has 14+ years of evidence that the daily question ritual can sustain a loyal user base.

The gaps are significant: Show of Hands uses binary/multiple-choice (not sliders), shows demographic segmentation rather than personal percentile ("you are more concerned than 78%"), and has comments. It does not have Nucleus's three-axis emotional slider design or the distribution curve + percentile revelation mechanic.

Metaculus is closest on the *social comparison* mechanic (Peer Score compares you to all forecasters), but it targets a narrow, analytically sophisticated audience and requires deep engagement (researching, writing rationale, tracking over time) — not Nucleus's frictionless 30-second emotional check-in model.

**Instagram's emoji slider** is structurally the closest to Nucleus's slider UX, but it is embedded in a creator/follower relationship, has no news curation, and shows only the current average rather than a personal percentile distribution.

No single product replicates the full Nucleus stack.

---

### (b) Is the Claimed Gap Real?

**Yes — the gap is real and documented.**

The research confirms that no existing product combines all four elements simultaneously:

1. **Daily curated news events** — Ground News, Polymarket, and Metaculus have this. Most others do not.
2. **Structured sentiment sliders (continuous, multi-axis)** — Instagram's emoji slider has the mechanic in isolation, but no product pairs it with curated news events.
3. **Personal percentile positioning vs. crowd** ("you are more concerned than 78%") — Metaculus has a peer score for predictive accuracy. Blind has salary comparison. No product applies this mechanic to emotional reactions to news events.
4. **No comments / no social graph** — Polis, AllSides, Ground News, and YouGov are all read-only or comment-free in varying degrees. But none of them combine this constraint with the other three elements.

The gap is not just that all four elements are missing from one product — it is that even the closest candidates (Show of Hands, Metaculus, Ground News) are each missing at least two of the four structural pillars.

The specific identity hook — **"you are more X than Y% of people who read the same headline"** — does not exist in any researched consumer product. This is the most defensible and novel element of the Nucleus design.

---

### (c) Biggest Competitive Threat to Nucleus at Launch

**Primary threat: Twitter/X polls + the platform effect.**

Not because X has a better product, but because it has 245M+ DAU and near-zero friction to deploy a poll on any news event, from any publisher or journalist account. If the Nucleus format shows early traction, X can replicate the "vote on a news event before seeing results" loop within its existing feed. X cannot easily replicate the slider mechanics, the distribution curve, or the percentile framing — but it can approximate the ritual at massive scale.

**Secondary threat: Metaculus / prediction market incumbents targeting emotional framing.**

If Polymarket or a competitor introduces a "sentiment layer" (how worried are you about this event, 0–100?) alongside its existing probability markets, it would have the news curation, the crowd distribution data, and an existing engaged user base. The marginal cost of adding this feature is low; the risk to Nucleus is high if a well-capitalized platform moves this direction.

**Third threat: Ground News adding a sentiment slider.**

Ground News already curates daily news events and has a subscriber base habituated to rating sources and tracking their own media diet. If Ground News added even a single emotional slider (e.g., "How concerned are you about this story?") and showed subscribers how they compare to other readers, it would cover ~75% of the Nucleus value proposition overnight with an established distribution channel.

**Fourth threat: Feature commoditization via Instagram / Snapchat.**

If Instagram extended its emoji slider to allow creators to tie it to a trending news event — with aggregate result reveals and a "you responded higher than X% of readers" post-submission screen — it would replicate the core mechanic at 2B MAU scale. Instagram has the infrastructure; it lacks only the editorial curation and the percentile framing decision.

**Lowest threat: Remesh, Swayable, Polis.** These are B2B or governance tools with no consumer distribution ambition. They are not competitive threats to a consumer mobile app.

---

## Strategic Implications for Nucleus

1. **The daily ritual moat is real but time-limited.** Show of Hands demonstrates 14 years of survival on the daily-question-ritual model, but with low growth. The Nucleus percentile hook is the differentiating mechanism that could drive viral growth (sharing your percentile result) beyond what Show of Hands achieved.

2. **The slider UX is unproven at scale for news.** Instagram has validated sliders as engaging in the creator/follower context. Nucleus needs to validate whether 0–100 sentiment sliders create the "just one more" pull in a news context where questions may feel heavier.

3. **No-comment design is a meaningful moat.** Every platform that has added comment sections to news/opinion tools has experienced harassment, political polarization escalation, and content moderation costs. Nucleus's no-comment constraint is not just a philosophical choice — it is a structural defense against the toxicity failure mode that destroyed Yik Yak and limits Blind's crossover appeal.

4. **Polymarket's post-election collapse (90%+ DAU drop) is the cautionary tale.** Even with real-money stakes and 1.2M unique traders in 2024, Polymarket could not retain users without a sustained high-salience event. Nucleus's design of pairing 5–10 *daily* events (including lower-salience stories) is the right counter-strategy — but editorial curation quality becomes the make-or-break variable.

5. **The biggest defensibility risk is Ground News moving upmarket.** If Ground News adds emotional sentiment sliders to its already-curated daily story feed, Nucleus loses its clearest use-case differentiation. Monitor Ground News product announcements closely.

---

*Sources referenced throughout:*
- [Sprout Social — Twitter/X Statistics 2026](https://sproutsocial.com/insights/twitter-statistics/)
- [DDIA — Community Notes Deep Dive 2021–2025](https://ddia.org/en/a-deep-dive-into-xs-community-notes-report)
- [Participedia — Polis Method](https://participedia.net/method/polis)
- [SimilarWeb — AllSides Traffic](https://www.similarweb.com/website/allsides.com/)
- [Ground News Help — Bias Comparison Summary](https://help.ground.news/en/articles/3189505)
- [Ground News — My News Bias](https://ground.news/my-news-bias-vantage)
- [Growjo — Ground News Revenue](https://growjo.com/company/Ground_News)
- [Fortune — Polymarket and Kalshi User Drop](https://fortune.com/2025/07/24/polymarket-and-kalshi-user-numbers/)
- [CryptoSlate — Polymarket Post-Election Drop](https://cryptoslate.com/polymarket-survives-post-election-drop-off-though-volume-drops-60/)
- [Metaculus FAQ](https://www.metaculus.com/faq/)
- [Astral Codex Ten — ACX/Metaculus 2025 Contest](https://www.astralcodexten.com/p/try-the-2025-acxmetaculus-forecasting)
- [Social Media Today — Reddit Polls Launch](https://www.socialmediatoday.com/news/reddit-launches-polls-providing-another-way-for-redditors-to-engage-with-c/574643/)
- [Digital Web Solutions — Reddit Statistics](https://www.digitalwebsolutions.com/blog/reddit-statistics/)
- [SocialInsider — Instagram Stories Benchmarks 2025](https://www.socialinsider.io/social-media-benchmarks/instagram-stories-benchmarks)
- [Instagram Blog — Emoji Slider Announcement](https://about.instagram.com/blog/announcements/introducing-the-emoji-slider-sticker)
- [Gitnux — Blind Statistics](https://gitnux.org/blind-statistics/)
- [TechCrunch — Sidechat / Yik Yak Acquisition](https://techcrunch.com/2023/03/16/anonymous-app-sidechat-picks-up-rival-yik-yak-and-users-arent-happy/)
- [Remesh — Platform Overview](https://www.remesh.ai/)
- [Swayable — About](https://www.swayable.com/)
- [Beehiiv — Polls Feature](https://www.beehiiv.com/features/polls)
- [Hearken — About](https://wearehearken.com/)
- [YourStory — Hunch $23M Series A](https://yourstory.com/2024/03/hunch-anonymous-polls-social-media-app-startup-ai-moderation)
- [Show of Hands — Homepage](https://www.showofhands.com/)
- [Pollitics — Homepage](https://pollitics.com/)
- [PRNewswire — Perspective API 500M daily requests](https://www.prnewswire.com/news-releases/googles-jigsaw-announces-toxicity-reducing-api-perspective-is-processing-500m-requests-daily-301223601.html)
- [YouGov — About](https://today.yougov.com/)
