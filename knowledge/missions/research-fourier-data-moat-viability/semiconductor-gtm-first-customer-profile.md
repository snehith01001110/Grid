---
status: completed
milestone: Research
date: 2026-03-24
type: research
model: claude
tags: [#research]
confidence: medium
router_decision: claude
router_reasoning: 'research requires web search'
---

## Task Description

The synthesis critique states that hyperscalers are the wrong first customer (18–36 month procurement cycle, SOC 2 Type II required, build-vs-buy default) and recommends targeting well-funded fabless startups or Tier-2 semiconductor companies. Research the following: (1) Which specific companies are in active CXL or PCIe 6.0 bring-up cycles in 2025–2026 that are (a) not hyperscalers and (b) unlikely to build internal tooling? Consider Astera Labs, XConn, Montage, Rambus, Microchip, plus AI-specific interconnect startups. (2) What does the actual procurement process look like at a 200–2000 person fabless semiconductor company for a $100–200K software tool? Who signs, what procurement steps are required, what is the typical sales cycle? (3) What is a realistic first PoC structure — scope, duration, success criteria, and conversion rate to a paid license — based on comparable EDA startup GTM playbooks?

## Expected Behavior

A named short-list of 5–10 realistic first-customer targets with rationale, a realistic procurement timeline and stakeholder map for this customer type, and a structured PoC template with success criteria and typical conversion rates.

## Findings / Output

---

# Research Report: CXL/PCIe 6.0 Bring-Up Targets, Semiconductor Procurement, and EDA PoC Playbooks

**Date:** March 24, 2026 | **Research method:** Web search + primary source fetches across 30+ queries

---

## Question 1: Companies in Active CXL / PCIe 6.0 Bring-Up Cycles (Non-Hyperscaler, Unlikely to Build Internal Tooling)

### 1.1 Astera Labs

**Company profile:** ~600–756 employees; engineering headcount ~310 as of November 2025; San Jose HQ. Publicly traded (ALAB).

**Product roadmap:**
- Aries 6 PCIe/CXL Smart DSP Retimers — third-generation, 64 GT/s (PCIe 6.x/CXL 3.x), in production ramp mid-2025
- Aries PCIe Smart Gearbox — industry-first bridging PCIe 6 ↔ PCIe 5; in production ramp 2025
- Leo CXL Smart Memory Controllers — first cloud service provider deployment on Microsoft Azure M-series VMs (2025); broader CXL revenue expected H2 2026
- Scorpio Smart Fabric Switches — integrated into their Cloud-Scale Interop Lab

**Internal SI/validation tooling:**
Astera ships COSMOS Developer Kit and COSMOS Explorer to customers as managed-intelligence software. COSMOS covers PHY/data link/transaction layer error counters, BER, eye metrics, error injection, RAS testing. Astera *outsources* deep physical-layer SI simulation to Cadence and compliance testing to Teledyne LeCroy/Keysight — not built internally.

**Bring-up pain points (documented):**
- PAM4 signal degradation at 64 GT/s; reduced noise margin vs. NRZ
- Channel topology complexity (add-in cards, cables, risers, backplanes) requiring retimers
- Mixed-generation system deployments (PCIe 6 host + PCIe 5 endpoints)
- Interoperability risk across NVIDIA, AMD, Intel platforms

**Likely to build internal tooling?** Partially. COSMOS covers basic diagnostics, but customers integrating Astera chips into their own boards lack internal PAM4 link bring-up tooling.

**Sources:** [Astera Labs 2025 Milestones](https://www.asteralabs.com/astera-labs-2025-milestones-a-breakthrough-year-of-expansion-innovation-ecosystem-leadership/) | [PCIe 6 Ramp](https://www.asteralabs.com/news/astera-labs-ramps-production-of-pcie-6-connectivity-portfolio-supercharging-advanced-ai-and-cloud-infrastructure-deployments/) | [COSMOS Dev Kit](https://www.asteralabs.com/cosmos-dev-kit-accelerating-ai-infrastructure-time-to-market/)

---

### 1.2 Montage Technology

**Company profile:** ~501 employees; ~75% in R&D; listed on Shanghai STAR Market.

**Product roadmap:**
- M88RT61632 PCIe 6.x/CXL 3.x Retimer — 16-lane, 64 GT/s, proprietary PAM4 SerDes IP; began sampling January 2025
- M88MX6852 CXL 3.1 Memory eXpander Controller — sampling phase September 2025
- PCIe 6.x/CXL 3.x AEC solution — launched February 2026

**Internal SI/validation tooling:**
Montage ships evaluation boards and reference designs. No evidence of a software tooling team beyond silicon R&D. Customer bring-up support model is hardware-kit-plus-reference-design only.

**Bring-up pain points:**
- PCIe 6.x signal integrity challenges (crosstalk, reflections) in AI servers and AECs
- China-based ODM/OEM customers evaluating boards without Keysight-level lab infrastructure

**Likely to build internal tooling?** Very low. Deep hardware R&D focus; predominantly China-based customer base that relies on reference designs rather than software tooling investments.

**Sources:** [Montage PCIe 6.x Retimer — PR Newswire Jan 2025](https://www.prnewswire.com/news-releases/montage-technology-samples-pcie-6xcxl-3x-retimer-chips-302356064.html) | [CXL 3.1 MXC — Yahoo Finance Sep 2025](https://finance.yahoo.com/news/montage-technology-introduces-cxl-3-150000451.html) | [AEC Launch Feb 2026](https://www.prnewswire.com/news-releases/montage-technology-launches-pcie-6xcxl-3x-aec-solution-to-enable-high-efficiency-interconnects-for-next-generation-data-centers-302669836.html)

---

### 1.3 Rambus

**Company profile:** ~712 employees in 2025. Hybrid IP licensing + silicon products company.

**Product roadmap:**
- PCIe 6.0 Controller IP and Retimer Controller — silicon IP for SoC customers
- CXL 3.0 Controller IP — achieved CXL 2.0 compliance April 2025; on CXL Integrators List
- XpressAGENT embedded protocol analyzer — built-in logic analyzer, TL packet tracing, register-level API for silicon bring-up/debug

**Internal SI/validation tooling:**
Rambus *sells* XpressAGENT as an IP-embedded bring-up tool — but this only covers its own IP customers. Rambus's SoC customers integrating its IP into novel designs still face multi-vendor interoperability issues Rambus cannot pre-validate.

**Bring-up pain points:**
- CXL compliance testing requires BIOS enumeration, OS-level validation, golden reference host
- Transition from CXL 2.0 to CXL 3.0/3.1 spec compliance ongoing and demanding

**Likely to build internal tooling?** Medium. XpressAGENT serves its own hardware customers only; no standalone validation software team.

**Sources:** [Rambus PCIe 6.0 Controller IP](https://www.rambus.com/interface-ip/pci-express/pcie6-controller/) | [XpressAGENT Product Page](https://www.rambus.com/interface-ip/pci-express/xpressagent/) | [CXL Compliance Journey](https://www.rambus.com/blogs/rambus-cxl-ip-a-journey-from-spec-to-compliance/)

---

### 1.4 Microchip Technology (Switchtec PCIe Division)

**Company profile:** ~19,400 employees; in restructuring/furloughs as of 2025. PCIe switches are a focused product line.

**Product roadmap:**
- Switchtec Gen 6 PCIe Switch — industry's first PCIe Gen 6 switch in 3 nm process; unveiled October 2025; up to 160 lanes; sampling to qualified customers; 64/48-lane versions Q2 2026
- ChipLink diagnostic GUI — proprietary software for debug, configuration, live signal analysis, eye diagrams; updated for Gen 6

**Internal SI/validation tooling:**
ChipLink is a customer-facing tool bundled with Switchtec hardware. No in-house PAM4 simulation or AI-based link-anomaly-detection capability. Company is in cost-reduction mode; software tooling investment is not a priority.

**Bring-up pain points:**
- Customers (ODMs, storage OEMs) need to integrate 160-lane PCIe 6 switches into dense AI rack topologies
- 3 nm process introduces new thermal/power bring-up challenges alongside electrical ones

**Likely to build internal tooling?** Low. Cost-reduction mode; hardware delivery focused.

**Sources:** [Switchtec Gen 6 Announcement](https://www.microchip.com/en-us/about/news-releases/products/microchip-unveils-first-3-nm-pcie--gen-6-switch-to-power-modern) | [Switchtec Gen 6 Blog](https://www.microchip.com/en-us/about/media-center/blog/2025/introducing-the-first-3nm-gen-6-pcie-switchtec-family)

---

### 1.5 Credo Semiconductor (AI-Specific Interconnect)

**Company profile:** Publicly traded (CRDO). ~300–400 employees. Targets AI infrastructure SerDes, retimers, AECs.

**Product roadmap:**
- Toucan PCIe Gen 6/7 retimers — 40 dB reach, sub-7 ns latency at 11W; in production
- PILOT (Predictive Integrity Link Optimization and Telemetry) — launched May 2025 as a software diagnostic/analytics SDK for PCIe/CXL deployments

**Internal SI/validation tooling:**
Credo built PILOT because its customers needed it during bring-up and fleet-scale monitoring — but PILOT serves Credo's own hardware customers, not the broader market. Early-access customers report "faster deployment and improved consistency in dense rack-scale environments."

**Bring-up pain points:**
- Hundreds of PCIe/CXL links in AI racks require automation; manual per-link bring-up is untenable
- PCIe link state transitions and CXL memory coherence failures during bring-up are hard to diagnose

**Likely to build internal tooling?** Medium — actively building PILOT, which signals they felt the tooling gap acutely. But PILOT is hardware-tied.

**Sources:** [PILOT Launch — Business Wire May 2025](https://www.businesswire.com/news/home/20250520197675/en/Credo-Launches-PILOT-a-Diagnostic-and-Analytics-Software-Platform-Enhancing-Link-Reliability-and-Performance-Across-High-Speed-Connectivity-Solutions) | [PILOT Product Page](https://credosemi.com/products/pilot/)

---

### 1.6 Kandou AI (formerly Kandou Bus)

**Company profile:** Private startup; rebranded "Kandou AI" in 2025. Focus shifted from SerDes IP to PCIe/CXL interconnect chips for AI inference/training.

**Product roadmap:**
- Next-generation PCIe and CXL interconnect chips for AI inference, training, CXL memory platforms, rack connectivity
- Completed Innosuisse-funded project July 2025

**Internal SI/validation tooling:** No evidence whatsoever. In active chip development mode, not tooling mode.

**Likely to build internal tooling?** Very low. **Strongest candidate for third-party AI-based bring-up tooling.**

**Sources:** [Kandou AI Jan 2025](https://www.kandou.com/news/2025-01-30-kandous-foundational-technologies/) | [Leadership Changes — EEHerald Dec 2025](https://www.eeherald.com/section/news/p20251216nwkandou.html)

---

### 1.7 Alphawave Semi

**Company profile:** Publicly traded (AWE.L). ~400–600 employees. PCIe/CXL PHY IP and controller subsystems.

**Product roadmap:**
- PipeCORE PCIe 6.0 PHY and controller subsystem — demonstrated interoperability with Keysight at 64 GT/s
- PCIe 7.0 and optical PCIe — demonstrated at PCI-SIG Developers Conference 2025
- UCIe 1.6T interconnect chiplets for AI data centers

**Internal SI/validation tooling:**
Alphawave *explicitly outsources* compliance validation to Keysight via formal partnership — direct evidence that even a connectivity IP specialist relies entirely on third-party tooling for bring-up and compliance.

**Likely to build internal tooling?** Low. Explicitly partners with Keysight rather than building.

**Sources:** [Alphawave-Keysight PCIe 6.0 Partnership](https://awavesemi.com/press-release/alphawave-semi-partners-with-keysight-to-deliver-industry-leading-expertise-and-interoperability-for-a-complete-pcie-6-0-subsystem-solution/) | [PCIe 7.0 at PCI-SIG 2025](https://awavesemi.com/press-release/alphawave-semi-at-the-forefront-of-pcie-7-0-specification-showcasing-next-gen-chiplet-interoperability-and-optical-pcie-technology-at-pci-sig-developers-conference-2025/)

---

### 1.8 XConn Technologies (Acquired by Marvell, January 2026)

XConn announced Apollo 2 CXL 3.1/PCIe 6.2 hybrid switch chip at FMS 2025, then was acquired by Marvell for $540M (closed February 2026). As an independent entity, XConn was a canonical "active bring-up, no internal tooling team" target. Its team is now inside Marvell.

**Sources:** [XConn Apollo 2 — ServeTheHome](https://www.servethehome.com/xconn-tech-shows-off-new-pcie-gen6-and-cxl-3-switch-chips-at-fms-2025/) | [Marvell Acquires XConn — Business Wire](https://www.businesswire.com/news/home/20260106226715/en/Marvell-to-Acquire-XConn-Technologies-Expanding-Leadership-in-AI-Data-Center-Connectivity)

---

### Summary Table

| Company | Size | PCIe 6/CXL Status | Internal Tooling Team? | Tooling Gap |
|---|---|---|---|---|
| Astera Labs | ~600 | PCIe 6 in prod; CXL ramping H2 2026 | Partial (COSMOS, outsources SI sim) | Medium |
| Montage Technology | ~501 | PCIe 6 retimer + CXL 3.1 sampling | No — ref design only | **High** |
| Rambus | ~712 | PCIe 6 IP; CXL 2.0 compliant | Partial (XpressAGENT, IP-embedded) | Medium |
| Microchip (Switchtec) | ~19,400 | PCIe Gen 6 switch sampling Oct 2025 | No AI/ML validation team | **High** |
| Credo Semiconductor | ~300–400 | PCIe 6/7 retimers in production | Building PILOT, hardware-tied | Medium |
| Kandou AI | <100 est. | PCIe/CXL chips in development | None | **Very High** |
| Alphawave Semi | ~400–600 | PCIe 6 PHY/subsystem | No — partners with Keysight | **High** |

---

## Question 2: Procurement Process for a $100–200K Software Tool at a 200–2,000 Person Fabless Semiconductor Company

### 2.1 Who Signs

At the 200–2,000 person fabless tier:

- **Champion / initiator:** Director of Systems/Validation Engineering or Principal SI Engineer
- **Technical approver:** VP of Engineering (required above ~$50K)
- **Budget holder + executive sign-off:** VP Engineering or CTO (above $100K, CTO typically required)
- **Finance review:** CFO or Finance Director; triggered above $50K–$100K thresholds
- **Legal review:** Required for any multi-year software license agreement; involves MSA review, IP ownership, data security, indemnification, liability caps
- **Security/IT review:** Required when tool processes proprietary design data; involves SOC 2 Type II, ISO 27001, data residency, export control review

### 2.2 Procurement Steps (In Order)

1. Engineering need identified → champion writes internal justification (1–2 weeks)
2. Internal budget check (1 week)
3. Vendor shortlist + demo (2–6 weeks)
4. Technical evaluation / PoC (4–12 weeks; see Question 3)
5. Vendor security questionnaire — SOC 2, data handling, IP protection (1–6 weeks at semi companies handling export-controlled IP)
6. Legal review of MSA/license agreement (2–8 weeks; often the single largest variable)
7. Finance approval (1–2 weeks)
8. Executive sign-off on PO (days to 1 week once docs ready)
9. PO issuance (days)

**Total typical timeline: 6–12 months.** Mid-market firms now average ~9 months for $50K–$100K+ ACV deals due to the "Mid-Market Squeeze" — adoption of enterprise-level procurement processes without enterprise procurement resources.

### 2.3 Key Variables That Lengthen the Cycle

- **IP sensitivity:** Semiconductor companies handle export-controlled design data (ITAR/EAR potentially applicable). Vendor security reviews are substantially more rigorous. A single missing security control can add "10–21 days of drag" between verbal yes and signed contract.
- **Legal contract complexity:** IP ownership clauses for EDA/validation tools are contested territory — who owns insights derived from chip designs? Negotiation alone can take 3–4 months.
- **Buying committee size:** Typically 4–7 stakeholders (champion, VP Eng, CTO, legal, finance, IT security, procurement coordinator).
- **Budget cycles:** EDA/tool budgets planned annually; Q3 requests may wait for Q4 planning.
- **Export control:** For companies with China-based customers (e.g., Montage), OFAC/Commerce review adds further delays.

### 2.4 Security Review Specifics

Typical security review for a $100–200K validation software tool at a semiconductor company:
- SOC 2 Type II report required (5–10 business days to review)
- ISO 27001 certification verification (increasingly standard)
- Data processing agreement review (where is design IP stored? who has access?)
- Export control compliance questionnaire

**Sources:** [ControlHub Semiconductor Procurement](https://www.controlhub.com/industry/semiconductor) | [Average B2B Deal Cycle — Demand Gen Report](https://www.demandgenreport.com/industry-news/the-average-b2b-deal-cycle-lasts-6-months-new-research/47659/) | [Sales Cycle Length Statistics 2025 — SalesSo](https://salesso.com/blog/sales-cycle-length-statistics/) | [Vendor Security Review — UpGuard](https://www.upguard.com/blog/vendor-security-review) | [Heavybit SaaS PoC Best Practices](https://www.heavybit.com/library/article/saas-poc-paid-pilot-program/)

---

## Question 3: Realistic First PoC Structure for an AI/ML-Based Semiconductor Validation Tool

### 3.1 What the EDA Startup Landscape Shows

**ChipAgents** (founded 2023; $74M raised by February 2026): Deployed at 80 leading semiconductor companies by early 2026. Reported 140x ARR growth YoY. Achieved "several multi-year, multi-million-dollar licensing agreements." Claims: 10x verification productivity boost; 240x reduction in formal assertion generation time. GTM: engineering-team-centric, augmenting existing toolchains rather than replacing them, targeting verification/debug workflows where pain is measurable. Strategic investors (Micron, MediaTek) were early customers.

**Advantest SiConic** (February 2025): Joint development with AMD as anchor customer → launch with co-development credibility → expand via Siemens EDA/Synopsys/Cadence channel partnerships. The canonical "anchor customer co-develops, provides social proof" playbook.

**TestFlow**: AI platform for semiconductor validation. Claims: 70% reduction in validation cycle time, 45% increase in test coverage, one CPU manufacturer went from 16-week to 4-week validation cycles. Demo-led sales model.

**Sources:** [ChipAgents $74M — Business Wire Feb 2026](https://www.businesswire.com/news/home/20260217568914/en/ChipAgents-Raises-$74M-to-Scale-an-Agentic-AI-Platform-to-Accelerate-Chip-Design) | [Advantest SiConic — GlobeNewswire Feb 2025](https://www.globenewswire.com/news-release/2025/03/29/3032/0/en/Advantest-Introduces-SiConic-Groundbreaking-Solution-for-Automated-Silicon-Validation.html) | [TestFlow Validation Platform](https://testflowinc.com/blog/semiconductor-time-to-market-critical-success-factor)

---

### 3.2 Recommended PoC Structure

**Phase 0 — Qualification (2–4 weeks before PoC)**
- Identify a specific bring-up milestone the customer faces *right now* (e.g., PCIe 6.0 link training failures on a retimer evaluation board)
- Define **one primary KPI** in advance: e.g., "reduce mean time to root-cause a link training failure from 3 days to 4 hours"
- Agree mutually in writing on go/no-go criteria *before* the PoC begins — enterprise pilots with predefined success criteria are 3.2x more likely to convert
- **Charge a nominal paid pilot fee ($5K–$25K)** to qualify buyer commitment. SaaStr/Lemkin: "if a big enterprise isn't willing to pay something for a pilot, they almost never will." Heavybit data: "A small paid commitment changes behavior overnight."

**Phase 1 — Scoped PoC (60–90 days)**
- Duration: 30 days creates urgency but is unrealistic for semiconductor hardware companies where bring-up cycles have hardware availability dependencies; **60–90 days is appropriate for CXL/PCIe bring-up**
- Scope: Limit to **one** bring-up scenario (one platform, one failure mode)
- Deliverable: Report demonstrating measurable movement on the agreed KPI, with diagnostics log as evidence
- Structure the pilot within a full-year contract template with 90-day opt-out — handles legal/security upfront, makes conversion a commercial formality

**Phase 2 — Conversion**
- Trigger: KPI achieved (or meaningful progress demonstrated)
- Annual license: $100K–$200K for single team/site
- Multi-year/multi-site expansion as adoption grows

---

### 3.3 Success Criteria — Semiconductor-Specific Examples

| Metric | Baseline | Target (PoC success threshold) |
|---|---|---|
| Mean time to root-cause link training failure | 2–5 days (oscilloscope + protocol analyzer) | < 4 hours (AI-assisted log analysis) |
| Bring-up iterations to PCIe 6.0 compliance | 6–10 cycles | < 3 cycles |
| Validation cycle duration | 16–20 weeks | 4–6 weeks (TestFlow benchmark) |
| Simulation cycles in design verification | Baseline | 30–50% reduction (Siemens/Synopsys benchmark) |
| Formal assertion generation time | Baseline | 240x faster (ChipAgents claim) |

**For a PCIe/CXL bring-up tool, the single most credible KPI is: time-to-passing link training on first silicon.** It is unambiguous, measurable, and directly tied to chip program schedule risk — a VP-level concern.

---

### 3.4 Conversion Rate Data

- Properly structured **paid pilots** in B2B enterprise: **40–60% conversion** to annual contracts (Monetizely)
- Well-run paid pilots (SaaStr/Lemkin): **70%+ conversion** when done right
- **Free pilots: <10% conversion** for enterprise software — do not use
- AI pilots in manufacturing broadly: "nearly 90% fail to transition to production" — risk scenario driven by unclear KPIs, siloed teams, and data integration failures. Directly applicable to semiconductor AI tools requiring access to proprietary design data and EDA integrations

**Sources:** [SaaStr: Paid Pilot Conversion](https://www.saastr.com/what-is-the-typical-conversion-from-paid-pilot-to-annual-contract-in-b2b-saas/) | [Heavybit SaaS PoC Best Practices](https://www.heavybit.com/library/article/saas-poc-paid-pilot-program/) | [Scaling AI in Semiconductor Manufacturing — Spotfire May 2025](https://www.spotfire.com/blog/2025/05/06/scaling-ai-in-semiconductor-manufacturing-why-most-pilots-fail-and-how-to-succeed/)

---

### 3.5 GTM Analogies

**Cadence/Synopsys early history:** Both grew from university research tools adopted by National Semiconductor, Harris, GE, and Ericsson — domain experts within target companies became external advocates who pulled the startup vendor in. Pattern: founder network → first 2–3 customers via personal relationships → strategic investors as validators.

**ChipAgents GTM:** Founder-engineer network → seed deployment at 10–20 companies → Series A with strategic investors (Micron, MediaTek as users) → 80 companies and multi-year contracts. 140x ARR growth in one year is consistent with a product proving immediate value (10x productivity) for a universally-felt pain.

**Key implication:** The first 1–3 customers should be: (1) a company the founding team has a personal relationship with, (2) a company actively in a painful bring-up cycle *right now*, (3) a company small enough that the champion can get to "yes" quickly (200–500 person company).

**Best first PoC candidates from the landscape above:**
- **Kandou AI** — startup, PCIe/CXL chips in development, zero tooling team, maximum urgency
- **Companies integrating Alphawave Semi PipeCORE or Rambus CXL Controller IP** into novel SoCs — active integration, no internal tooling
- **Montage Technology's ODM partners** — Chinese AI server ODMs without lab infrastructure

---

## Cross-Cutting Findings

**On tooling gaps:** Every company in this space has built or is building a proprietary bring-up software layer (COSMOS, PILOT, XpressAGENT, ChipLink). None solve the underlying *data analysis* problem — pattern recognition across link training logs, eye diagram data, BER telemetry to predict or classify failures. This is the opportunity space for an AI/ML-native tool.

**On procurement:** The $100–200K price point requires VP Engineering/CTO sign-off with mandatory legal and security review at a 200–2,000-person fabless semi company. Budget exists (EDA tools regularly run $100K–$1M/seat), but a 9–12 month sales cycle is real and must be engineered around via a paid PoC that handles legal/security *upfront*.

**On PoC design:** The most important design decision is not duration (30 vs. 90 days) but **KPI specificity**: one measurable metric the customer's VP Engineering cares about tied to schedule risk, which translates directly to revenue timing — a C-level concern.

**On conversion:** 40–70% conversion from paid pilot to annual contract is achievable with: (1) a paid (not free) pilot, (2) predefined KPIs, (3) a champion in active pain *today*, and (4) legal/security handled *before* the pilot starts so conversion is a commercial formality, not another 3-month process.

## Validation Result

Output length: 22845 chars | Verification: needs_revision

## My Notes
<!-- Write below this line. The harness reads this on re-run. Use #redo to re-run this task, #skip to skip it, #pivot:<new direction> to change the approach. -->