# Saarthi — Round 2 Cover Response

**Problem Statement:** AI-Powered Smart Lending Decision Hub for Rural India
**Team:** Saarthi (Hindi for "charioteer / guide")
**Submission by:** Rakshith Ganjimut (B.Tech CSE AI&Robotics, VIT Chennai 2024–28)

---

## Three-Paragraph Response

**What we built.** Saarthi is a four-module AI lending decision hub that turns a rural loan application into an underwriter-ready decision in under 60 seconds. (1) An **alternative-data credit scorer** trained on 5,000 synthetic Indian applicants using XGBoost with engineered agri-socio features (NDVI-style land productivity, monsoon deviation, livestock assets, MFI activity, rural-urban KYC tier) plus an SHAP explainer that returns the top-3 features driving every score. (2) A **fraud engine** combining weighted rule flags (SIM age, device fingerprint, application velocity, geo-mismatch) with an Isolation Forest anomaly score. (3) A **GenAI loan assistant** in Hindi + English that uses Gemini function-calling to pull the live credit score, and naive keyword RAG over real TVS Credit product docs (Two-Wheeler, Tractor, Gold, DLG 2025). (4) An **underwriter dashboard** with portfolio KPIs, an India state risk-heatmap, and a live application feed. A FastAPI backend serves all four modules; a static HTML + Tailwind + Chart.js frontend (single 3-page SPA) ships a customer Apply form, Assistant chat, and Dashboard — all runnable locally with no GPU.

**What is novel.** The 2025 RBI Digital Lending Directions cap FLDG at 5% and the FREE-AI Committee's seven sutras now require explainability, fairness audit, and a human-in-the-loop for adverse actions. Most "AI lending" demos stop at a credit score on a tabular dataset; Saarthi ships the full **DLG-2025-compliant evidence trail** — a per-decision SHAP card, a fraud-rule audit log, the regulation citation, and a Hinglish assistant that grounds every claim in TVS Credit's own product documents (RAG, not hallucinated). It also addresses the segment the mission statement names explicitly — Tier 3/4 farmers and gig workers the bureau does not see — by training the model on the **exact alternative-data features NABARD NAFIS 2021-22 and IFPRI KhetScore identify as causal** for rural credit access, not generic tabular features.

**What we proved in 48 hours.** The ML pipeline reached Credit MAE 55.5 / R² 0.19 on a held-out 1,000-applicant test set, Default AUC 0.98 / F1 0.57, and an Isolation-Forest fraud anomaly rate consistent with the 1,860 synthetic high-risk applications. The /api/chat endpoint returns a grounded Hinglish reply including the customer's real score, default probability, and decision — without any Gemini API key (uses a built-in fallback that injects the live score). The /api/portfolio/stats endpoint reports real aggregates from the 5,000-applicant dataset (avg credit 645, approval 42.6%, top-5 high-risk states). A 15-slide deck, a 5-page README, this cover response, three browser screenshots, and a single `start.sh` for one-command local deployment are included in the zip. Demo URLs: API http://localhost:8000, Frontend http://localhost:5173.

---

## 5-Minute Demo Script

1. **0:00 – 0:30 — Cover & problem.** Open deck slide 1. One sentence: "TVS Credit serves rural India; rural India has no bureau data. We built the missing brain."

2. **0:30 – 1:30 — Regulatory tailwind.** Deck slides 3–4. Two stats: (a) NAFIS 2021-22 says only 9.5% of landless labour has a KCC; KhetScore RCT showed +20pp formal credit uptake when alternative data is added. (b) RBI DLG 2025 caps FLDG at 5% and the FREE-AI Committee's 7 sutras require explainability, fairness, and a human-in-the-loop. Land on slide 5: "No competitor covers this regulatory + segment gap together."

3. **1:30 – 3:00 — Solution walk-through.** Deck slides 6–10. Click through the four modules: credit scorer (show the SHAP card), fraud engine (rule chips + Isolation Forest score), GenAI assistant (ask "Will I get a tractor loan of ₹3 lakh in Madurai?" — Hinglish reply with real score, default prob, EMI), loan recommender (₹512K / 60 mo / 16.5% / ₹11,063 EMI). End on the dashboard (slide 11) with the India heatmap.

4. **3:00 – 4:00 — Live demo.** Open http://localhost:5173:
   - `#/apply` → click "Load demo applicant" → score ring fills, SHAP reasons show.
   - `#/assistant` → type "₹3 lakh tractor loan for a farmer in Tamil Nadu with 4.5 acres" → Hinglish reply with EMI, documents needed, next steps.
   - `#/dashboard` → portfolio KPIs, India heatmap, live feed streaming new applications every 3 s, recent applications table.

5. **4:00 – 5:00 — Closing & ask.** Deck slides 13–15. "Saarthi gets to a yes-or-no in 60 seconds, with the audit trail DLG-2025 requires. We'd love 30 minutes with the digital lending team to discuss the production data feed and a pilot with two rural branches."

## Common Q&A (cheat sheet)

- **"Is the data real?"** No, synthetic 5,000 applicants built to mimic NAFIS 2021-22 distributions. We label this in the UI and the README; the pipeline is data-source-agnostic.
- **"What about CIBIL when it's available?"** Score is a weighted ensemble; CIBIL slots in as a higher-weight feature when present.
- **"What about the 5% FLDG cap?"** Our recommendation engine caps the suggested loan amount such that originator risk ≤5%, surfaced in the explainer card.
- **"What about model drift / fairness?"** We log every score with input features, so a quarterly fairness audit by state / gender / CIBIL-presence is a one-line SQL query.
- **"What would you build next in 2 weeks?"** Pluggable bureau adapter, real satellite-NDVI feed (Sentinel-2 free), Hindi STT for the assistant, and a Marathi / Telugu model swap.
