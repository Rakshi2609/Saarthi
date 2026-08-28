# Saarthi — Novelty Research for TVS Credit Hackathon Round 2

For Round-2 PPT, problem statement 'c'. Bias rule: prefer RBI / NABARD / IFPRI / World Bank / press with bylines.

---

## 1. Regulatory Tailwinds (RBI 2024-2026)

- **RBI Digital Lending Directions, 2025.** Issued **May 8, 2025** as `RBI/2025-26/36`. Replaces 2022 + 2023 frameworks. Adds: CIMS DLA registration (Jun 15, 2025); mandatory Key Fact Statement; 1-day cooling-off; 5% DLG cap; data-localisation; DPDPA consent. **Pitch use:** Saarthi is "born-DLG-2025-compliant" — KFS auto-flow, decision-logging, no biometric overreach, India-only data. Source: RBI PR 2025-2026/288 — https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60403

- **RBI FREE-AI Committee Report.** Constituted Dec 26, 2024; released **Aug 13, 2025** (PR 2025-2026/902). Sets **7 Sutras** (Trust, People First, Innovation over Restraint, Fairness/Equity, Accountability, Understandable by Design, Safety/Resilience) and **26 recommendations**. Flags "bias and lack of explainability" as material risks; recommends XAI for material decisions, fairness assessments, indigenous-language models. **Pitch use:** the Sutras map to Saarthi's pillars (Trust = audit trail, Fairness = bias-tested scores, Understandable = SHAP reason codes). Source: https://www.rbi.org.in/scripts/bs_pressreleasedisplay.aspx/BS_PressReleaseDisplay.aspx?prid=61018

- **RBI FLDG/DLG cap of 5% (codified into 2025 Directions).** "DLG shall not act as a substitute for credit appraisal." **Pitch use:** LSPs can no longer hide behind default-loss guarantees — real underwriting is now a regulatory minimum. Saarthi's satellite+weather score IS the substitute for missing CIBIL history. Source: https://www.rbi.org.in/scripts/FS_Notification.aspx?Id=12514

- **RBI Regulatory Sandbox — Theme-Neutral "On Tap" window (Apr 9, 2025).** Continuous application window after 4 completed cohorts. Enabling Framework requires DPDPA 2023 compliance. **Pitch use:** Saarthi is built sandbox-ready. Source: https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60190

- **Collateral-free agri-loan limit raised to ₹2 lakh (RBI FIDD, Dec 6, 2024).** `FIDD.CO.FSD.BC.No.10/05.05.010/2024-25`. **Pitch use:** regulator is pushing unsecured, small-ticket agri-credit — where bureau data is weakest and Saarthi is most valuable. Source: https://sansad.in/getFile/loksabhaquestions/annex/183/AU3316_lcs1Fe.pdf?source=pqals

---

## 2. Competitive Landscape — What Indian NBFCs Are Actually Doing with AI

- **Bajaj Finance — "BFL 3.0: A FinAI Company" (Investor Day, Dec 10, 2024).** 300+ GenAI projects; 29 use cases live targeting **₹150 crore FY26 cost save**; **10,000 loans/month end-to-end via GenAI**; voice-to-text pipeline enabling **₹2,400 crore/yr disbursal**. **Solves:** urban/salaried & consumer-durable credit at scale. **Does NOT solve:** **no satellite/agri/rural credit play at all.** Source: https://www.bajajfinserv.in/finserv-digital-annual-report-fy25/transformation-through-technology.html ; https://money.rediff.com/news/market/ai-drives-bajaj-fin-x27-x27-s-loan-growth-10-000-loans-month/23756820250319

- **Jio Financial Services — "AI-native financial marketplace" (JioFinance App, AGM Aug 26, 2026).** **~130 AI agents**; Jio Credit gross AUM **+163% YoY to ~₹30,000 crore** in Q1 FY27; Bank of America investing up to **₹18,268 crore for 49.9%** of Jio Credit. **Solves:** consumer credit via mobile-data signals. **Does NOT solve:** **no agri/rural vertical** — Jio Credit is a smartphone + UPI play; the data signal dies where Saarthi's satellite+weather+field-agent layer is the only signal. Source: https://www.business-standard.com/companies/news/jio-financial-bets-on-ai-global-partnerships-to-drive-next-phase-of-growth-126082601161_1.html

- **Airtel Finance — "100% digital, 30-min loan" marketplace.** Airtel Flexi Credit (personal loan up to ₹10L), Axis credit card, gold loan (no CIBIL), business loan up to ₹75L; 10L+ users. **Solves:** thin-file urban personal loans using *telco data* (recharge, handset) as credit proxy. **Does NOT solve:** **no agri-credit vertical, no landless-farmer play.** **Pitch use:** Airtel proves NBFCs *can* underwrite thin-file with alternative data — Saarthi is the rural equivalent, where satellite+weather is the "recharge history" of a farmer. Source: https://www.airtel.in/finance/

- **HDFC Credila — education-loan NBFC.** 2.26L+ students, 64 countries, 5,200+ universities. Won "Innovation in Digital Lending Award" 2024. **Solves:** education loans, urban/aspirational. **Does NOT solve:** **zero rural / agri / income-generation lending.** Source: https://www.credila.com/

- **NBFC market tailwind (CRISIL/ICRA + TransUnion CIBIL Q2 2025).** NBFC AUM expected to **exceed ₹48 lakh crore by end-FY25**. CMI Sep 2025: **double-digit growth in personal loans in semi-urban/rural; faster growth in gold & consumer-durable loans outside metros.** **Pitch use:** market is shifting to Tier 3-4 but incumbents are still pushing collateralised/salaried proxies. **No major NBFC has yet integrated satellite-NDVI + weather into a production credit decision.** This is Saarthi's white space. Source: https://www.linkedin.com/posts/credit-information-bureau-india-limited_cmi-creditmarketindicator-creditinsights-activity-7376974756891316225-bQSm

---

## 3. Rural India Credit Gap (NABARD / Government Data)

- **NABARD NAFIS 2021-22 (released Oct 9, 2024) — 1 lakh rural households, 28 states + 2 UTs.** The single most important primary dataset:
  - **Only 44% of agricultural households hold a valid KCC.**
  - **Only 30.1% of farmers with up to 0.40 hectares** (the majority of India's cultivators) have a KCC.
  - **Only 9.5% of households with <0.01 hectare** (functionally landless) have a KCC.
  - **75.5% of agri-households now borrow from institutional sources only** (up from 60.5% in 2016-17), but **23.4% still borrow from non-institutional sources.**
  - **Average landholding shrank from 1.08 ha to 0.74 ha.**
  **Pitch use:** the 9.5% / 30.1% KCC numbers are *the* problem slide. Demand exists (institutional share up 15pp in 5 yrs) but supply still excludes 9 in 10 landless and 7 in 10 marginal farmers. Source: https://static.pib.gov.in/WriteReadData/specificdocs/documents/2024/oct/doc20241010414001.pdf ; full report https://www.nabard.org/auth/writereaddata/tender/2102255939NAFIS%202021-22%20Report%20Final.pdf ; KCC skew https://thehindubusinessline.com/data-stories/data-focus/skewed-access-marks-kisan-credit-card-growth-story/article69900550.ece

- **Scale of the agri-credit market (Economic Survey 2024-25).** **7.75 crore KCCs** as of Mar 2024, **₹9.81 lakh crore** outstanding. Ground-level agri-credit grew from **₹8.45 lakh crore (2014-15) to ₹25.48 lakh crore (2023-24)**, CAGR 12.98%. Share of small & marginal farmers within GLC rose from 41% to 57%. **Pitch use:** per-farmer ticket is tiny (avg KCC ~₹12,700) — manual underwriting at ₹50K tickets is uneconomic. Saarthi's <30-min target is the only viable answer. Source: https://pib.gov.in/PressReleasePage.aspx?PRID=2097959

- **Rural credit TAT today: 2–4 weeks traditional underwriting.** Per IMPRI India analysis of RBI's Unified Lending Interface (ULI) rollout, "the digitized end-to-end credit delivery architecture has compressed the traditional rural credit underwriting cycle from 2–4 weeks down to less than 30 minutes." Industry data: **40–60% of loan applicants abandon** if TAT exceeds 3 days. **Pitch use:** cite the 2–4 week status-quo as the baseline. Source: https://www.impriindia.com/insights/policy-update/transforming-indias-credit-ecosystem-through-the-unified-lending-interface-uli2025/

- **Fintech NBFC scale: ~10.9 crore personal loans worth ₹1,06,548 crore in FY25; 80% of microfinance NBFC book is rural** (SIDBI/ET). **Pitch use:** validates NBFC + rural + digital is a real, fast-growing segment. Source: https://www.agriwise.com/the-role-of-nbfcs-in-shaping-rural-credit-access/

---

## 4. Tech Novelty — Has Satellite + Weather + ML + GenAI Been Done End-to-End?

- **KhetScore (Dvara E-Registry + IFPRI, Odisha) — the only published end-to-end pilot with RCT evidence.** Cluster-randomised trial across **58 villages (29 treatment, 29 control)**. Pipeline = (1) digitised farmer profiles via georeferenced smartphone pics; (2) satellite imagery for cultivated area, soil moisture, historical NDVI; (3) picture-based crop insurance; (4) credit score → formal loan. **Results (IFPRI Discussion Paper 2288, Kramer/Pattnaik/Ward/Xu 2024):**
  - **Formal-credit uptake rose ~20 percentage points** in treatment villages.
  - Treated households were **less likely** to report repayment difficulty despite borrowing more — **better risk selection, not just more credit.**
  - **Agri profits up ~$102 in Kharif, +$145 in Rabi** (~₹2,000/season extra).
  - Scaled from 50 → **15,000 farmers** across states.
  **Pitch use:** headline stat = "+20pp formal-credit uptake, with better repayment." The only RCT-grade proof in the world that "satellite + ML credit score" works for smallholders. **What Saarthi adds that KhetScore doesn't have:** continuous weather-feed re-scoring during loan life, GenAI loan assistant in Hindi/regional languages, fraud signals, real-time risk dashboard, NBFC-grade explainability + audit trail, loan recommendations, default prediction. Source: https://www.ifpri.org/blog/the-emerging-role-of-ai-tools-in-smallholder-finance ; https://ideas.repec.org/p/fpr/ifprid/2288.html ; https://doi.org/10.22004/ag.econ.339080

- **SatSure / CropIn — commercial satellite+weather stacks used by FSPs in rural India.** World Bank documents SatSure working with an Indian bank to tailor "satellite-based crop and weather forecasts to incorporate their impact on lending portfolios." CropIn's **SmartRisk** does climate-risk-to-yield-to-financial-impact projections. **Pitch use:** these are the *data-layer* precedents; neither ships a full-stack credit + GenAI + dashboard product. Saarthi's "one platform, one workflow" is the integration novelty. Source: https://documents1.worldbank.org/curated/en/099120003132457854/txt/IDU1c6d3dbe812a4a14f19189151f1868459e5eb.txt

- **ICRISAT "STARS" project — the caveat we already handle.** ICRISAT's foundational work showed that at landscape scale, fertilization explains **<35% of NDVI variation** — management practice, soil, and catena position dominate. **Pitch use:** "NDVI alone is not enough — Saarthi combines NDVI with weather, soil, agronomic management flags, and behavioural signals, exactly as ICRISAT's STARS work warned is required." Source: https://www.slideshare.net/slideshow/icrisat-research-program-west-and-central-africa-2016-highlightssmallholders-in-mali-adjust-crop-management-decisions-thanks-to-satellite-monitoring/86615322

---

## 5. Risk — Known Failure Modes & Regulatory Pushback

- **RBI's FREE-AI report explicitly names the risks Saarthi must address.** "Increased adoption of AI could lead to new risks like bias and lack of explainability." Recommends fairness assessments, XAI for material decisions, board-approved AI policies, third-party risk assessments. **Pitch use:** "We mapped our architecture to the 7 Sutras" — judges from banking/regulatory backgrounds will ask "where's your bias audit?" The RBI has already given the answer. Source: https://www.mondaq.com/india/new-technology/1670830/rbi-releases-report-on-responsible-and-ethical-enablement-of-ai-in-the-financial-sector

- **Algorithm bias in smallholder credit scoring is peer-reviewed.** *IJCTT* Vol 71 (2023), "Alternative Risk Scoring Data for Small-Scale Farmers": of 23 data types lenders request, 14 are deemed important but **7 are commonly unavailable**, creating missing-data bias; plus inherent algorithm-bias. The paper proposes 14 alternative data types — *exactly the categories Saarthi uses.* **Pitch use:** "Bias risk is real and published — alternative data is the published mitigation, and Saarthi ships it." Source: https://www.ijcttjournal.org/archives/ijctt-v71i1p101

- **DLG 2025 forbids underwriting-by-guarantee.** "Any DLG arrangement shall not act as a substitute for credit appraisal requirements and robust credit underwriting standards need to be put in place irrespective of DLG cover." **Pitch use:** macro tailwind for Saarthi — every digital-lending partner of an NBFC now has to demonstrate real underwriting rigour. A satellite+weather+ML score with explainability is exactly what the regulator has been demanding. Source: https://www.rbi.org.in/scripts/FS_Notification.aspx?Id=12514

---

## Suggested PPT Line-Up

1. **Problem** → NAFIS 9.5% KCC (landless) + 30.1% (marginal) farmers.
2. **Regulatory tailwind** → FREE-AI 7 Sutras + DLG 2025 + ₹2L collateral-free.
3. **White space** → Competitor matrix: Bajaj=urban GenAI, Jio=mobile-data, Airtel=telco-data, Credila=education — none in rural-satellite-credit.
4. **Evidence** → KhetScore IFPRI RCT (+20pp credit uptake, better repayment, +₹2,000/season profit).
5. **Risk** → Address bias + explainability with the Sutra mapping.

---

## Honest Gaps (do NOT make these claims without verification)

- **Muthoot Fincorp / Manappuram AI initiatives 2024-25** — no recent citable AI product announcements found. Don't claim a competitive gap against them unless verified.
- **"Stanford SAT-GIS" pilot** — no published paper with that exact framing found. Closest academic evidence is IFPRI/Dvara KhetScore (Odisha) and World Bank docs on SatSure/CropIn. Don't claim a "Stanford pilot."
- **Single canonical "average rural NBFC loan approval time"** — not found in RBI/NABARD. Best available is 2–4 week ULI baseline and 5–7 day urban NBFC TAT (industry-typical).
