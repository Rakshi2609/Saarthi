"""
Saarthi — Predict service. Single import path used by the FastAPI backend
and the demo scripts.

Public API:
    from ml.predict import score_applicant
    result = score_applicant(applicant_dict)

Returns:
    {
        "credit_score": int 300-900,         # from credit_model.pkl
        "default_probability": float 0-1,     # from default_model.pkl
        "decision": "approve" | "refer" | "reject",  # from outcome_model.pkl
        "decision_probabilities": {...},
        "fraud_score": float 0-1,
        "fraud_flags": [str, ...],
        "anomaly_score": float,               # higher = more normal
        "top_3_reasons": [ {feature, contribution}, ... ],
        "loan_recommendation": {
            "max_eligible_amount": int,
            "suggested_tenure_months": int,
            "suggested_interest_rate_pct": float,
            "monthly_emi_inr": int,
        }
    }
"""
import json
import pickle
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import shap

ML_DIR = Path(__file__).parent
FEATURE_COLS = json.loads((ML_DIR / "feature_columns.json").read_text())
CREDIT_MODEL   = pickle.loads((ML_DIR / "credit_model.pkl").read_bytes())
DEFAULT_MODEL  = pickle.loads((ML_DIR / "default_model.pkl").read_bytes())
OUTCOME_MODEL  = pickle.loads((ML_DIR / "outcome_model.pkl").read_bytes())
ISO_MODEL      = pickle.loads((ML_DIR / "isolation_forest.pkl").read_bytes())

# Build SHAP explainer once
EXPLAINER = shap.TreeExplainer(CREDIT_MODEL)

NUMERIC_FEATURES = [
    "age", "monthly_income_inr", "loan_amount_inr", "loan_tenure_months",
    "land_acres", "ndvi_score", "rainfall_30d_mm",
    "existing_loans", "default_history", "dti",
    "app_velocity_30d", "email_age_days", "phone_age_days",
    "ip_geo_mismatch", "device_shared_count_30d", "disposable_email",
]
CATEGORICAL_FEATURES = [
    "employment", "loan_type", "crop_type", "state", "device", "browser",
]


def _to_dataframe(applicant: Dict[str, Any]) -> pd.DataFrame:
    """Apply the same encoding as training."""
    row = {}
    for f in NUMERIC_FEATURES:
        row[f] = applicant.get(f, 0)
    for f in CATEGORICAL_FEATURES:
        row[f] = str(applicant.get(f, "none"))
    df = pd.DataFrame([row])
    df_enc = pd.get_dummies(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES],
                            columns=CATEGORICAL_FEATURES, drop_first=True)
    # align with training feature columns: add missing as 0
    for c in FEATURE_COLS:
        if c not in df_enc.columns:
            df_enc[c] = 0
    df_enc = df_enc[FEATURE_COLS]
    return df_enc


def _fraud_rules_score(row: Dict[str, Any]):
    flags = []
    score = 0.0
    if row.get("app_velocity_30d", 0) >= 4:
        flags.append("High application velocity (4+ apps/30d)")
        score += 0.20
    if row.get("email_age_days", 999) < 30:
        flags.append("Email created < 30 days ago")
        score += 0.18
    if row.get("phone_age_days", 999) < 90:
        flags.append("Phone number < 90 days old")
        score += 0.10
    if row.get("ip_geo_mismatch", 0) == 1:
        flags.append("IP geo mismatch with applicant address")
        score += 0.22
    if row.get("device_shared_count_30d", 0) >= 2:
        flags.append("Device shared with 2+ other recent applications")
        score += 0.15
    if row.get("disposable_email", 0) == 1:
        flags.append("Disposable email domain")
        score += 0.20
    return min(0.99, score), flags


def _loan_recommendation(applicant: Dict[str, Any], credit_score: int, default_prob: float):
    income = max(8000, int(applicant.get("monthly_income_inr", 20000)))
    loan_type = applicant.get("loan_type", "Personal Loan")
    # suggested tenure by loan type
    tenure_map = {
        "Two Wheeler": 24, "Used Car": 48, "Tractor": 60,
        "Used Commercial Vehicle": 48, "Three Wheeler": 36,
        "Consumer Durable": 12, "Personal Loan": 24, "Mobile Loan": 9, "Gold Loan": 12,
    }
    tenure = tenure_map.get(loan_type, 24)
    # rate by credit bucket
    if credit_score >= 750:
        rate = 12.5
    elif credit_score >= 700:
        rate = 14.0
    elif credit_score >= 650:
        rate = 16.5
    else:
        rate = 19.5
    # max eligible: cap EMI at 45% of income, adjust by risk
    max_emi = income * 0.45
    monthly_rate = rate / 12 / 100
    if monthly_rate == 0:
        max_principal = max_emi * tenure
    else:
        max_principal = max_emi * (1 - (1 + monthly_rate) ** (-tenure)) / monthly_rate
    risk_factor = max(0.4, 1.0 - default_prob * 0.8)
    eligible = int(max_principal * risk_factor / 1000) * 1000
    # EMI for the requested loan
    P = int(applicant.get("loan_amount_inr", eligible))
    if monthly_rate == 0:
        emi = P / tenure
    else:
        emi = P * monthly_rate * (1 + monthly_rate) ** tenure / ((1 + monthly_rate) ** tenure - 1)
    return {
        "max_eligible_amount": eligible,
        "suggested_tenure_months": tenure,
        "suggested_interest_rate_pct": rate,
        "monthly_emi_inr": int(emi),
    }


def score_applicant(applicant: Dict[str, Any]) -> Dict[str, Any]:
    x = _to_dataframe(applicant)

    credit_score = float(np.clip(CREDIT_MODEL.predict(x)[0], 300, 900))
    default_prob = float(DEFAULT_MODEL.predict_proba(x)[0, 1])
    out_proba = OUTCOME_MODEL.predict_proba(x)[0]
    decision = ["reject", "approve", "refer"][int(out_proba.argmax())]

    # SHAP top-3 reasons
    sv = EXPLAINER.shap_values(x)
    abs_sv = np.abs(sv[0])
    top3_idx = abs_sv.argsort()[-3:][::-1]
    top3 = [
        {"feature": FEATURE_COLS[i], "contribution": float(sv[0, i])}
        for i in top3_idx
    ]

    # Fraud
    f_score, f_flags = _fraud_rules_score(applicant)
    iso_score = float(ISO_MODEL.decision_function(x)[0])

    # Loan recommendation
    loan_rec = _loan_recommendation(applicant, int(credit_score), default_prob)

    return {
        "credit_score": round(credit_score, 1),
        "default_probability": round(default_prob, 4),
        "decision": decision,
        "decision_probabilities": {
            "reject":  round(float(out_proba[0]), 3),
            "approve": round(float(out_proba[1]), 3),
            "refer":   round(float(out_proba[2]), 3),
        },
        "fraud_score": round(f_score, 3),
        "fraud_flags": f_flags,
        "anomaly_score": round(iso_score, 3),
        "top_3_reasons": top3,
        "loan_recommendation": loan_rec,
    }


if __name__ == "__main__":
    # smoke test
    sample = {
        "age": 35, "monthly_income_inr": 28000, "loan_amount_inr": 350000,
        "loan_tenure_months": 48, "land_acres": 0, "ndvi_score": 0,
        "rainfall_30d_mm": 0, "existing_loans": 1, "default_history": 0,
        "dti": 0.35, "app_velocity_30d": 1, "email_age_days": 1200,
        "phone_age_days": 800, "ip_geo_mismatch": 0,
        "device_shared_count_30d": 0, "disposable_email": 0,
        "employment": "Farmer", "loan_type": "Tractor",
        "crop_type": "Paddy", "state": "Tamil Nadu",
        "device": "Android-Samsung", "browser": "Chrome",
    }
    import pprint
    pprint.pprint(score_applicant(sample))
