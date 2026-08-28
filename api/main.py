"""
Saarthi — FastAPI backend.

Endpoints:
  GET  /api/health                  health check
  GET  /api/products                list loan products (for the apply form)
  GET  /api/applicants/random?n=10  random sample applicants (for dashboard seed)
  GET  /api/applicants/{id}         one applicant (for chat demo)
  POST /api/score                   score one applicant (credit + default + fraud + loan rec)
  POST /api/chat                    GenAI loan assistant (Gemini function calling)
  GET  /api/portfolio/stats         dashboard summary (for the underwriter view)
  GET  /api/portfolio/region-risk   per-state risk stats (for the heatmap)

Run:
  cd /home/appu/saarthi
  source .venv/bin/activate
  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
"""
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# allow `from ml.predict import ...`
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import pandas as pd

from ml.predict import score_applicant

ROOT = Path(__file__).parent.parent
DATA_CSV = ROOT / "data" / "applicants.csv"
PRODUCT_DOCS_DIR = ROOT / "docs" / "product_docs"

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Saarthi API",
    description="AI-Powered Smart Lending Decision Hub (TVS Credit EPIC 8, problem c)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache the dataset
_APPLICANTS_DF: Optional[pd.DataFrame] = None

def get_applicants() -> pd.DataFrame:
    global _APPLICANTS_DF
    if _APPLICANTS_DF is None:
        _APPLICANTS_DF = pd.read_csv(DATA_CSV)
    return _APPLICANTS_DF


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ApplicantIn(BaseModel):
    age: int = Field(..., ge=18, le=80)
    monthly_income_inr: int = Field(..., ge=2000, le=500000)
    employment: str
    loan_type: str
    loan_amount_inr: int = Field(..., ge=1000)
    loan_tenure_months: int = Field(..., ge=1, le=120)
    state: str
    district: str = ""
    lat: float = 20.5937
    lng: float = 78.9629
    # optional agri
    land_acres: float = 0.0
    ndvi_score: float = 0.0
    rainfall_30d_mm: float = 0.0
    crop_type: str = "none"
    is_agricultural: int = 0
    # optional fraud
    existing_loans: int = 0
    default_history: int = 0
    dti: float = 0.0
    app_velocity_30d: int = 1
    email_age_days: int = 365
    phone_age_days: int = 365
    ip_geo_mismatch: int = 0
    device_shared_count_30d: int = 0
    disposable_email: int = 0
    device: str = "Android-Samsung"
    browser: str = "Chrome"
    email: str = "demo@example.com"
    phone: str = "+919999999999"
    name: str = "Demo Applicant"


class ChatIn(BaseModel):
    message: str
    applicant_id: Optional[str] = None   # if provided, use that applicant's profile
    applicant: Optional[ApplicantIn] = None  # else use this one
    history: List[Dict[str, str]] = []    # [{"role":"user"|"assistant","content":...}]


class ChatOut(BaseModel):
    reply: str
    tool_calls: List[Dict[str, Any]] = []
    cited_sources: List[str] = []
    fallback: bool = False


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "applicants_loaded": len(get_applicants())}


@app.get("/api/products")
def products():
    return {
        "loan_types": [
            {"type": "Two Wheeler", "min": 35000, "max": 120000, "tenure": 24,
             "rate_range_pct": "12.5-19.5", "description": "New and used two-wheeler financing."},
            {"type": "Used Car", "min": 150000, "max": 600000, "tenure": 48,
             "rate_range_pct": "13.0-19.5", "description": "Pre-owned car financing."},
            {"type": "Tractor", "min": 300000, "max": 1200000, "tenure": 60,
             "rate_range_pct": "12.0-18.0", "description": "New and used tractor loans for farmers."},
            {"type": "Used Commercial Vehicle", "min": 250000, "max": 900000, "tenure": 48,
             "rate_range_pct": "13.5-19.0", "description": "Used commercial vehicle loans."},
            {"type": "Three Wheeler", "min": 120000, "max": 350000, "tenure": 36,
             "rate_range_pct": "13.5-19.0", "description": "Three-wheeler passenger/cargo."},
            {"type": "Consumer Durable", "min": 8000, "max": 60000, "tenure": 12,
             "rate_range_pct": "0-14.0", "description": "Appliance, electronics, furniture."},
            {"type": "Personal Loan", "min": 30000, "max": 200000, "tenure": 24,
             "rate_range_pct": "14.0-22.0", "description": "General-purpose personal loan."},
            {"type": "Mobile Loan", "min": 6000, "max": 30000, "tenure": 9,
             "rate_range_pct": "0-16.0", "description": "Smartphone financing."},
            {"type": "Gold Loan", "min": 20000, "max": 500000, "tenure": 12,
             "rate_range_pct": "10.0-14.0", "description": "Loan against gold jewellery."},
        ],
    }


@app.get("/api/applicants/random")
def random_applicants(n: int = 10):
    df = get_applicants()
    n = min(n, len(df))
    sample = df.sample(n=n, random_state=random.randint(0, 9999))
    cols = ["applicant_id", "name", "state", "district", "loan_type",
            "loan_amount_inr", "monthly_income_inr", "cibil_score",
            "default_probability", "fraud_score", "outcome",
            "application_timestamp", "lat", "lng"]
    return sample[cols].to_dict(orient="records")


@app.get("/api/applicants/{applicant_id}")
def get_one_applicant(applicant_id: str):
    df = get_applicants()
    rows = df[df["applicant_id"] == applicant_id]
    if rows.empty:
        raise HTTPException(404, f"applicant {applicant_id} not found")
    return rows.iloc[0].to_dict()


@app.post("/api/score")
def score(applicant: ApplicantIn):
    payload = applicant.model_dump()
    return score_applicant(payload)


# ---------------------------------------------------------------------------
# Chat (Gemini function calling + RAG over product docs)
# ---------------------------------------------------------------------------

# Load product docs (markdown) for RAG context
def _load_product_docs() -> List[Dict[str, str]]:
    docs = []
    if not PRODUCT_DOCS_DIR.exists():
        PRODUCT_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for p in PRODUCT_DOCS_DIR.glob("*.md"):
        docs.append({"name": p.stem, "content": p.read_text()[:3500]})
    return docs

PRODUCT_DOCS = _load_product_docs()


# Naive keyword-based retrieval (no embeddings needed for demo)
def _retrieve_context(query: str, k: int = 2) -> List[Dict[str, str]]:
    if not PRODUCT_DOCS:
        return []
    q = query.lower()
    scored = []
    for d in PRODUCT_DOCS:
        words = set(q.split())
        overlap = sum(1 for w in words if w in d["content"].lower())
        scored.append((overlap, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored or scored[0][0] == 0:
        return [scored[0][1]] if scored else []
    return [d for score, d in scored[:k] if score > 0]


SYSTEM_PROMPT = """You are Saarthi (सारथी — Hindi for 'charioteer'), the AI loan assistant for TVS Credit.
You help rural and semi-urban Indian customers understand their loan eligibility,
required documents, and the reasoning behind decisions. You speak in simple
Hindi-English (Hinglish) when the user does, otherwise clear English.

RULES:
1. Always be empathetic, never dismissive of small-ticket or first-time borrowers.
2. If a tool returns a result, ALWAYS cite the relevant numbers (score, EMI, rate).
3. For any decision, surface the top reasons in plain language ("Your score is 712 because your income is stable and you have no prior defaults").
4. If you don't know, say so. Don't invent rates or products.
5. Never guarantee approval — only the underwriter can do that.
6. Keep replies under 120 words unless asked for detail.

AVAILABLE PRODUCTS (TVS Credit):
- Two Wheeler, Used Car, Tractor, Used Commercial Vehicle, Three Wheeler,
  Consumer Durable, Personal Loan, Mobile Loan, Gold Loan.

You can call these tools:
- score_applicant: get credit score, default probability, decision, fraud flags, top reasons
- get_loan_recommendation: get max eligible amount, suggested tenure, rate, EMI
- retrieve_product_docs: get product policy / FAQ / rate-card excerpts
"""


def _try_gemini_chat(user_msg: str, history: list, applicant: dict) -> Optional[Dict[str, Any]]:
    """Try Gemini function-calling. Returns None if no API key or on failure."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
            tools=[score_applicant_tool_def(), retrieve_product_docs_tool_def()],
        )
        chat = model.start_chat(history=[
            {"role": "user" if h["role"] == "user" else "model", "parts": [h["content"]]}
            for h in history
        ])
        response = chat.send_message(user_msg)
        # handle function calling
        tool_calls_made = []
        for part in response.parts:
            if fn := part.function_call:
                name = fn.name
                args = dict(fn.args) if fn.args else {}
                if name == "score_applicant":
                    result = score_applicant({**applicant, **args})
                    tool_calls_made.append({"name": name, "args": args, "result": result})
                elif name == "retrieve_product_docs":
                    docs = _retrieve_context(args.get("query", user_msg))
                    result = {"docs": [{"name": d["name"], "excerpt": d["content"][:600]} for d in docs]}
                    tool_calls_made.append({"name": name, "args": args, "result": result})
        # final text
        reply = response.text if response.text else ""
        return {"reply": reply, "tool_calls": tool_calls_made}
    except Exception as e:
        print(f"[gemini] error: {e}")
        return None


def score_applicant_tool_def():
    return {
        "function_declarations": [{
            "name": "score_applicant",
            "description": "Score the current applicant: returns credit_score (300-900), default_probability (0-1), decision (approve/refer/reject), fraud_score, top 3 reasons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "loan_amount_inr": {"type": "integer", "description": "Override loan amount if customer changed mind"},
                    "loan_tenure_months": {"type": "integer", "description": "Override tenure"},
                },
            },
        }],
    }


def retrieve_product_docs_tool_def():
    return {
        "function_declarations": [{
            "name": "retrieve_product_docs",
            "description": "Look up TVS Credit product FAQ, terms, and rate cards.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "User's question or topic"},
                },
                "required": ["query"],
            },
        }],
    }


# ---------------------------------------------------------------------------
# Demo fallback (works without Gemini key) — rule-based, but feels chatty
# ---------------------------------------------------------------------------
def _fallback_reply(user_msg: str, applicant: Dict[str, Any]) -> Dict[str, Any]:
    """Run score + return a templated reply. Used when Gemini is unavailable."""
    result = score_applicant(applicant)
    rec = result["loan_recommendation"]
    decision = result["decision"]
    score = int(result["credit_score"])
    default_pct = int(result["default_probability"] * 100)
    flags = result["fraud_flags"]
    top3 = result["top_3_reasons"]

    q = user_msg.lower()
    if any(w in q for w in ("fraud", "risk", "safe", "verify")):
        if flags:
            reply = (f"Namaste. Aapke application pe {len(flags)} risk signals mile hain: " +
                     ", ".join(flags) +
                     f". Saarthi fraud score: {result['fraud_score']:.2f} (0=safe, 1=high risk). "
                     "Agar yeh galti se trigger hua hai, dealer se contact karein — manual review 24 hrs me ho jayegi.")
        else:
            reply = (f"Aapka fraud score {result['fraud_score']:.2f} hai — bilkul safe zone me. "
                     "Koi risk signal nahi mila. Application normally proceed hogi.")
    elif any(w in q for w in ("emi", "installment", "monthly", "kitna")):
        reply = (f"Aapke ₹{applicant['loan_amount_inr']:,} loan pe, "
                 f"{rec['suggested_tenure_months']} months tenure, "
                 f"{rec['suggested_interest_rate_pct']}% rate se, "
                 f"monthly EMI ≈ ₹{rec['monthly_emi_inr']:,}. "
                 f"Max eligible amount aapke profile pe: ₹{rec['max_eligible_amount']:,}. "
                 "EMI aapki monthly income ke 45% se kam honi chahiye — agar zyada lag rahi ho, "
                 "tenure badha sakte hain.")
    elif any(w in q for w in ("eligible", "approve", "approval", "loan milega", "paisa")):
        if decision == "approve":
            reply = (f"Namaste! Aapka credit score {score} hai aur default risk sirf {default_pct}%. "
                     f"Decision: APPROVE. Aap ₹{applicant['loan_amount_inr']:,} tak ke liye eligible hain. "
                     f"Top reasons: {top3[0]['feature']} (positive), "
                     f"{top3[1]['feature']}, {top3[2]['feature']}. Next step: "
                     "Aadhaar + PAN + bank statement last 3 months upload karein.")
        elif decision == "refer":
            reply = (f"Aapka score {score} hai — borderline case. Default risk {default_pct}%. "
                     "Decision: REFER (manual underwriter review). 24-48 hrs me jawab aayega. "
                     f"Top reason: {top3[0]['feature']}. Agar aapke paas land record ya "
                     "ITR hai toh approval chances badh jayenge.")
        else:
            reply = (f"Maaf kijiye, abhi aapka application reject ho gaya. Credit score {score}, "
                     f"default risk {default_pct}%. Reason: {top3[0]['feature']} (negative impact). "
                     "6 mahine baad reapply karein — score improve karne ke liye: "
                     "kisi bhi small-ticket loan ka EMI time pe pay karein.")
    elif any(w in q for w in ("document", "papers", "kyc", "kagaz")):
        reply = ("Aapko chahiye: 1) Aadhaar card, 2) PAN card, 3) Last 3 months bank statement, "
                 "4) Last 2 months salary slip ya ITR (agar salaried/business), 5) Passport photo. "
                 "Farmer ho toh: 6) Land record (khatauni) ya lease deed, 7) Crop pattern document. "
                 "Sab documents dealer ke through upload ho jayenge.")
    elif any(w in q for w in ("rate", "interest", "byaaj")):
        reply = (f"Aapke profile pe suggested rate {rec['suggested_interest_rate_pct']}% p.a. "
                 f"(reducing balance) hai. Score {score} ke basis pe bracket decide hua hai. "
                 "Final rate loan agreement me confirm hoga.")
    else:
        # generic — show the score
        reply = (f"Namaste! Main Saarthi hoon. Aapka credit score {score} hai, "
                 f"default risk {default_pct}%, decision: {decision.upper()}. "
                 "Poochiye: 'EMI kitni hogi?', 'Documents kya chahiye?', 'Approval milega?', ya 'Fraud check'.")
    return {
        "reply": reply,
        "tool_calls": [{"name": "score_applicant", "args": {}, "result": result}],
        "cited_sources": [],
        "fallback": True,
    }


@app.post("/api/chat", response_model=ChatOut)
def chat(req: ChatIn):
    # resolve applicant
    if req.applicant:
        applicant = req.applicant.model_dump()
    elif req.applicant_id:
        rows = get_applicants()
        match = rows[rows["applicant_id"] == req.applicant_id]
        if match.empty:
            raise HTTPException(404, f"applicant {req.applicant_id} not found")
        applicant = match.iloc[0].to_dict()
        # normalize
        for k, default in [
            ("monthly_income_inr", 20000), ("loan_amount_inr", 100000),
            ("loan_tenure_months", 24), ("age", 35), ("employment", "Salaried"),
            ("loan_type", "Personal Loan"), ("state", "Tamil Nadu"),
        ]:
            applicant.setdefault(k, default)
    else:
        raise HTTPException(400, "Either applicant or applicant_id is required")

    # try Gemini first, fall back to rule-based
    gemini_result = _try_gemini_chat(req.message, req.history, applicant)
    if gemini_result and gemini_result.get("reply"):
        # attach RAG sources
        ctx = _retrieve_context(req.message)
        cited = [d["name"] for d in ctx]
        return ChatOut(
            reply=gemini_result["reply"],
            tool_calls=gemini_result["tool_calls"],
            cited_sources=cited,
            fallback=False,
        )
    # fallback
    result = _fallback_reply(req.message, applicant)
    ctx = _retrieve_context(req.message)
    result["cited_sources"] = [d["name"] for d in ctx]
    return ChatOut(**result)


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------
@app.get("/api/portfolio/stats")
def portfolio_stats():
    df = get_applicants()
    return {
        "total_applicants": int(len(df)),
        "avg_credit_score": int(df["cibil_score"].mean()),
        "avg_default_probability": round(float(df["default_probability"].mean()), 4),
        "approval_rate": round(float((df["outcome"] == 1).mean()), 3),
        "refer_rate": round(float((df["outcome"] == 2).mean()), 3),
        "rejection_rate": round(float((df["outcome"] == 0).mean()), 3),
        "avg_loan_amount_inr": int(df["loan_amount_inr"].mean()),
        "high_fraud_count": int((df["fraud_score"] > 0.5).sum()),
        "loan_type_mix": df["loan_type"].value_counts().to_dict(),
        "top_states_by_volume": df["state"].value_counts().head(5).to_dict(),
    }


@app.get("/api/portfolio/region-risk")
def region_risk():
    """Per-state aggregated risk for the heatmap."""
    df = get_applicants()
    agg = df.groupby("state").agg(
        avg_credit_score=("cibil_score", "mean"),
        avg_default_prob=("default_probability", "mean"),
        avg_fraud_score=("fraud_score", "mean"),
        applications=("applicant_id", "count"),
        high_risk=("default_probability", lambda s: int((s > 0.30).sum())),
    ).reset_index()
    return {
        "states": agg.to_dict(orient="records"),
    }
