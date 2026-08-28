# Saarthi — AI-Powered Smart Lending Decision Hub

> A 4-module AI platform that turns a rural Indian loan application into an underwriter-ready decision in under 60 seconds, with the evidence trail that RBI Digital Lending Directions 2025 require.

**Team:** Saarthi (Hindi for "charioteer / guide")
**Round 2 submission — TVS Credit EPIC 8 Hackathon, Problem C**
**Built by:** Rakshith Ganjimut · B.Tech CSE AI&Robotics · VIT Chennai 2024–28
**Live demo URLs (when started locally):** API `http://localhost:8000` · Frontend `http://localhost:5173`

---

## TL;DR

| What you get | Where it lives |
|---|---|
| 15-slide Round-2 deck (PPTX + PDF) | `docs/Saarthi_Round2_Deck.pptx` / `.pdf` |
| 3-paragraph cover response | `docs/cover_response.md` |
| 5-minute demo script | `docs/cover_response.md` (bottom) |
| Novelty research (RBI / NABARD / IFPRI) | `docs/novelty_research.md` |
| 4 ML models, 1 explainer | `ml/` (XGBoost, Isolation Forest, SHAP) |
| 5,000 synthetic applicants | `data/applicants.csv` |
| FastAPI backend (8 endpoints) | `api/main.py` |
| Static HTML + Tailwind + Chart.js frontend (3 pages) | `frontend/` |
| Browser screenshots | `assets/` |
| One-command local start | `./start.sh` |

---

## Architecture in one minute

```
[Customer / Dealer browser]              [Underwriter dashboard browser]
         (HTML+Tailwind SPA)                    (HTML+Tailwind SPA)
                \                                   /
                 \--------->  FastAPI :8000  <----/
                              (api/main.py)
                  ┌────────────┬────────────┬────────────┐
              [Credit     [Fraud    [Default  [GenAI Loan
               Scorer]    Engine]  Predictor] Assistant]
                  └────────────┴────────────┴────────────┘
                  XGBoost + SHAP + Rule-engine + Gemini/RAG
                              │
        [5000 synthetic applicants CSV  +  4 product docs RAG corpus]
```

Modules:
1. **Credit Scorer** — XGBoost regressor on 59 engineered features (agri, demographic, geo). Returns 300-900 score, decision, top-3 SHAP reasons.
2. **Fraud Engine** — Weighted rule flags (SIM age, geo, velocity) + Isolation Forest anomaly score.
3. **Default Predictor** — XGBoost classifier. AUC 0.98 on held-out 1,000 applicants.
4. **GenAI Loan Assistant** — Hinglish chat. Gemini function-calling when `GEMINI_API_KEY` is set; deterministic fallback otherwise. RAG over `docs/product_docs/`.

---

## Quick start (one command)

```bash
cd /home/appu/saarthi
./start.sh
```

That single script will:
1. Create `/home/appu/saarthi/.venv` if missing, install deps.
2. Start the FastAPI backend on port **8000** in the background (logs in `logs/api.log`).
3. Serve the static frontend on port **5173** in the background (logs in `logs/web.log`).
4. Print both URLs when ready.

Visit `http://localhost:5173`. To stop: `./start.sh stop` (or `kill $(cat /tmp/saarthi_api.pid) $(cat /tmp/saarthi_web.pid)`).

### Manual start (if you prefer)

```bash
cd /home/appu/saarthi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Terminal 1 — backend
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
cd frontend && python3 -m http.server 5173
```

---

## API endpoints (all working right now)

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/api/health` | Liveness + applicant count |
| `GET`  | `/api/products` | List loan products |
| `GET`  | `/api/applicants/random` | Pull a synthetic applicant |
| `GET`  | `/api/applicants/{id}` | Pull applicant by ID (e.g. `APP000011`) |
| `POST` | `/api/score` | Score a single applicant |
| `POST` | `/api/chat` | Hinglish / English loan chat |
| `GET`  | `/api/portfolio/stats` | Portfolio aggregates |
| `GET`  | `/api/portfolio/region-risk` | State-level risk buckets |
| `GET`  | `/docs` | Swagger UI |

### Try in 30 seconds

```bash
# Health
curl -s http://localhost:8000/api/health | python3 -m json.tool
# {"status":"ok","applicants_loaded":5000}

# Score a random applicant
curl -s http://localhost:8000/api/score \
  -H 'content-type: application/json' \
  -d '{"age":34,"gender":"M","state":"Tamil Nadu","annual_income_inr":180000,
       "loan_type":"Tractor","loan_amount_inr":450000,"tenure_months":60,
       "employment":"Farmer","land_size_acres":4.5,"crop_type":"Paddy",
       "monsoon_index":-0.15,"ndvi_proxy":0.7,"cibil_score":608,
       "existing_loans":2,"mfi_member":true,"sim_age_months":18,
       "device_fingerprint":"dev_xyz","ip_state":"Tamil Nadu",
       "phone_reuse_count":1,"application_velocity_30d":0}' | python3 -m json.tool
```

You'll get back a JSON like:
```json
{"credit_score": 653.6, "default_probability": 0.0001, "decision": "REFER",
 "fraud_score": 0.18, "fraud_flags": [], "anomaly_score": -0.07,
 "top_3_reasons": [{"feature": "annual_income_inr", "impact": -28.4},
                   {"feature": "cibil_score", "impact": +19.1},
                   {"feature": "land_size_acres", "impact": +12.7}],
 "loan_recommendation": {"max_eligible_amount_inr": 512000,
                         "suggested_tenure_months": 60,
                         "suggested_interest_rate_pct": 16.5,
                         "monthly_emi_inr": 11063}}
```

### Chat example

```bash
curl -s http://localhost:8000/api/chat \
  -H 'content-type: application/json' \
  -d '{"message":"₹3 lakh tractor loan?", "applicant_id":"APP000011"}' | python3 -m json.tool
```

Returns a Hinglish reply (in fallback mode) that includes the applicant's real credit score, default probability, decision, EMI, documents required, and next steps. With `GEMINI_API_KEY` set in the env, the same endpoint upgrades to Gemini function-calling.

---

## What's in this repo

```
saarthi/
├── README.md                  # this file
├── start.sh                   # one-command local start
├── stop.sh                    # one-command local stop
├── requirements.txt
│
├── data/
│   ├── applicants.csv         # 5000 synthetic applicants
│   └── README.md              # schema + disclaimer
│
├── ml/
│   ├── train.py               # trains all 4 models, writes metrics.json
│   ├── predict.py             # score_applicant(dict) → full JSON
│   ├── credit_model.pkl
│   ├── default_model.pkl
│   ├── outcome_model.pkl
│   ├── isolation_forest.pkl
│   ├── fraud_rules.json
│   ├── feature_columns.json
│   ├── metrics.json           # 5,000-applicant training metrics
│   ├── sample_predictions.json
│   └── shap_summary.png
│
├── api/
│   └── main.py                # FastAPI, 8 endpoints, RAG, Gemini
│
├── frontend/
│   ├── index.html             # Tailwind CDN, hash router, 3 pages
│   └── app.js                 # 1 file, no build step
│
├── docs/
│   ├── product_docs/          # RAG corpus (4 files)
│   │   ├── two_wheeler.md
│   │   ├── tractor.md
│   │   ├── gold_loan.md
│   │   └── digital_lending_rights.md
│   ├── novelty_research.md    # 16KB cited research
│   ├── cover_response.md      # 3-paragraph response + 5-min demo script
│   ├── Saarthi_Round2_Deck.pptx  # 15-slide deck
│   └── Saarthi_Round2_Deck.pdf   # PDF preview
│
├── scripts/
│   ├── generate_data.py       # synthetic 5K applicant generator
│   └── build_ppt.py           # 15-slide deck builder
│
├── assets/
│   ├── screenshot_apply.png
│   ├── screenshot_dashboard.png
│   └── screenshot_assistant.png
│
└── .git/                      # initialized (Rakshith <rakshith@saarthi.dev>)
```

---

## The four modules in detail

### 1. Credit Scorer (`ml/predict.py → score_applicant`)

- XGBoost regressor on a 5,000-applicant synthetic dataset with realistic India distributions (loan mix, geography, agri profiles, CIBIL distribution, employment).
- **Features (59 total):** age, gender, state (one-hot), annual income, loan type, loan amount, tenure, employment type, land size, crop type, monsoon deviation, NDVI proxy, CIBIL score, existing loans, MFI membership, sim age, device fingerprint, ip state, phone reuse, application velocity, plus 3 DTI/employment-stability/crop-yield engineered features.
- **Output:** 300–900 score, approve/refer/reject decision, top-3 SHAP reasons, loan recommendation (max eligible amount, tenure, rate, EMI).
- **Performance on 1,000 held-out:** MAE 55.5, R² 0.19.

### 2. Fraud Engine (`api/main.py`)

- Weighted rule engine (sums to 1.0 across flags like geo-mismatch, SIM-too-new, phone reuse, application velocity > 3 in 30 d).
- Isolation Forest anomaly score on the same 59 features.
- Returns: `fraud_score` (0–1), `fraud_flags` (list of triggered rules), `anomaly_score`.

### 3. Default Predictor (`ml/predict.py → default_probability`)

- XGBoost binary classifier on a 3-class outcome label (0=reject, 1=approve, 2=refer).
- Output: probability of default in next 12 months.
- **Performance on 1,000 held-out:** AUC 0.98, Accuracy 0.98, F1 0.57 (positive class is rare by construction).

### 4. GenAI Loan Assistant (`api/main.py → /api/chat`)

- Hinglish / English chat endpoint.
- **Two modes:**
  - **With `GEMINI_API_KEY` set:** Gemini 2.0 Flash with function-calling. The model decides whether to call `score_applicant(applicant_id)` and the assistant returns the live score in the reply. The function call result is then grounded in a RAG context fetched from `docs/product_docs/` via naive keyword retrieval.
  - **Without the key (default):** Deterministic fallback that injects the live score and pulls the top-3 RAG docs and stitches a Hinglish reply. Same response shape, no network calls.
- **Cited in slide 3-4 of the deck** for DLG 2025 + FREE-AI compliance.

---

## Deploy guide (Vercel + Render free tier)

The current build is a static frontend + Python FastAPI backend, which maps cleanly to:

- **Frontend → Vercel.** Drag the `frontend/` folder into a Vercel project. The 3-page SPA uses a hash router, so no rewrites are needed. Set `API_URL` env var to your backend's public URL.
- **Backend → Render free tier.** Create a new Web Service from the repo root. Build command `pip install -r requirements.txt`. Start command `uvicorn api.main:app --host 0.0.0.0 --port $PORT`. The free tier sleeps after 15 min of inactivity and serves 512 MB RAM — plenty for the demo loadout.
- **Optional upgrades:** Add a managed Postgres (Neon / Supabase) to replace the in-memory CSV load. Add Upstash Redis for the live-feed ticker.

---

## What is **synthetic** in this build

Everything is synthetic to make the submission self-contained and DLG-2025-compliant (no real PII). Specifically:
- 5,000 applicants in `data/applicants.csv` are generated by `scripts/generate_data.py` with realistic India distributions for state, age, income, loan type, CIBIL. The generator code is in the repo and the schema is in `data/README.md`.
- Product docs in `docs/product_docs/` are paraphrased from TVS Credit's public marketing pages and the RBI Digital Lending Directions (Aug 2025) circular.
- The "live feed" on the dashboard streams from the 5,000 synthetic applicants at one per 3 seconds.

To swap to real data, replace `data/applicants.csv` with an export from the production LOS, and update `api/main.py:load_applicants()` to query a database instead.

---

## Reproduce the ML pipeline from scratch

```bash
source .venv/bin/activate
python3 scripts/generate_data.py    # writes data/applicants.csv
python3 ml/train.py                # writes ml/*_model.pkl, metrics.json, shap_summary.png
```

Total time on a 4-core laptop: ~3 minutes.

---

## License & contact

MIT. Built for the TVS Credit EPIC 8 Hackathon (Round 2) — submission by **Rakshith Ganjimut** (rakshithganjimut@gmail.com · github.com/Rakshi2609).
