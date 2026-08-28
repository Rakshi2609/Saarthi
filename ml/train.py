"""
Saarthi — Train credit scoring, default prediction, and fraud models.

Outputs (all in /home/appu/saarthi/ml/):
  - credit_model.pkl        XGBoost regressor (score 300-900)
  - default_model.pkl       XGBoost classifier (prob 0-1)
  - fraud_rules.json        Rule weights used for the fraud engine
  - isolation_forest.pkl    Anomaly detector
  - feature_columns.json    Canonical feature list (same for all)
  - metrics.json            Train/test metrics for the report slide
  - sample_predictions.json 5 sample applicants with all 3 model outputs + SHAP
  - shap_summary.png        SHAP feature importance chart

Run:
  cd /home/appu/saarthi
  source .venv/bin/activate
  python3 ml/train.py
"""
import json
import pickle
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, classification_report,
    mean_absolute_error, r2_score,
)
from sklearn.ensemble import IsolationForest
import xgboost as xgb
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = Path("/home/appu/saarthi/data/applicants.csv")
OUT  = Path("/home/appu/saarthi/ml")
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Features used for ALL three models
# ---------------------------------------------------------------------------
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
FEATURE_COLS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

def load_and_encode():
    df = pd.read_csv(DATA)
    # fill na categoricals with "none"
    for c in CATEGORICAL_FEATURES:
        df[c] = df[c].fillna("none").astype(str)
    # one-hot
    df_enc = pd.get_dummies(df[FEATURE_COLS], columns=CATEGORICAL_FEATURES, drop_first=True)
    feature_columns = list(df_enc.columns)
    return df, df_enc, feature_columns


def train_credit_model(X_train, y_train, X_test, y_test, feature_columns):
    """Predict cibil_score (300-900) for the explainability card."""
    model = xgb.XGBRegressor(
        n_estimators=300, max_depth=6, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.8, random_state=42, n_jobs=-1,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    preds = np.clip(model.predict(X_test), 300, 900)
    metrics = {
        "mae": float(mean_absolute_error(y_test, preds)),
        "r2": float(r2_score(y_test, preds)),
    }
    return model, metrics


def train_default_model(X_train, y_train, X_test, y_test):
    """Predict default probability (binary)."""
    model = xgb.XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.8, random_state=42, n_jobs=-1,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)
    metrics = {
        "auc": float(roc_auc_score(y_test, probs)),
        "accuracy": float(accuracy_score(y_test, preds)),
        "f1": float(f1_score(y_test, preds)),
    }
    return model, metrics


def train_fraud_models(X):
    """Isolation forest for anomaly + a hand-tuned rules engine (we ship the rules as JSON)."""
    iso = IsolationForest(
        n_estimators=200, contamination=0.08, random_state=42, n_jobs=-1,
    )
    iso.fit(X)
    # simple score based on decision_function (higher = more normal, lower = more anomalous)
    return iso

# fraud rules used at predict time
FRAUD_RULES = {
    "app_velocity_high":     {"weight": 0.20, "trigger": "app_velocity_30d >= 4"},
    "email_too_young":       {"weight": 0.18, "trigger": "email_age_days < 30"},
    "phone_too_young":       {"weight": 0.10, "trigger": "phone_age_days < 90"},
    "ip_geo_mismatch":       {"weight": 0.22, "trigger": "ip_geo_mismatch == 1"},
    "shared_device":         {"weight": 0.15, "trigger": "device_shared_count_30d >= 2"},
    "disposable_email":      {"weight": 0.20, "trigger": "disposable_email == 1"},
}

def fraud_rules_score(row):
    flags = []
    score = 0.0
    if row["app_velocity_30d"] >= 4:
        flags.append("High application velocity (4+ apps/30d)")
        score += 0.20
    if row["email_age_days"] < 30:
        flags.append("Email created < 30 days ago")
        score += 0.18
    if row["phone_age_days"] < 90:
        flags.append("Phone number < 90 days old")
        score += 0.10
    if row["ip_geo_mismatch"] == 1:
        flags.append("IP geo mismatch with applicant address")
        score += 0.22
    if row["device_shared_count_30d"] >= 2:
        flags.append("Device shared with 2+ other recent applications")
        score += 0.15
    if row["disposable_email"] == 1:
        flags.append("Disposable email domain")
        score += 0.20
    return min(0.99, score), flags


def main():
    print("Loading + encoding data…")
    df, X_all, feature_columns = load_and_encode()
    print(f"  rows: {len(df)}, features after one-hot: {len(feature_columns)}")

    # ---------------- Credit model: regress cibil_score ----------------
    print("\nTraining credit score regressor…")
    X_train, X_test, idx_train, idx_test = train_test_split(
        X_all, df.index, test_size=0.2, random_state=42,
    )
    y_cibil_train = df.loc[idx_train, "cibil_score"].values
    y_cibil_test  = df.loc[idx_test,  "cibil_score"].values
    credit_model, credit_metrics = train_credit_model(
        X_train, y_cibil_train, X_test, y_cibil_test, feature_columns,
    )
    print(f"  MAE: {credit_metrics['mae']:.1f}  R²: {credit_metrics['r2']:.3f}")

    # ---------------- Default model: binary classifier ----------------
    # ground truth: default_probability > 0.10 (synthetic, gives a usable positive rate)
    print("\nTraining default classifier…")
    y_default = (df["default_probability"] > 0.10).astype(int).values
    pos_rate = y_default.mean()
    print(f"  positive rate (default_prob > 0.10): {pos_rate:.1%}")
    y_def_train = y_default[idx_train]
    y_def_test  = y_default[idx_test]
    default_model, default_metrics = train_default_model(
        X_train, y_def_train, X_test, y_def_test,
    )
    print(f"  AUC: {default_metrics['auc']:.3f}  Acc: {default_metrics['accuracy']:.3f}  F1: {default_metrics['f1']:.3f}")

    # ---------------- Fraud: rules + isolation forest ----------------
    print("\nTraining fraud isolation forest + writing rules…")
    iso = train_fraud_models(X_all)

    # ---------------- Outcome classifier (for the score card "decision") ----------------
    # train a 3-class classifier on outcome (0/1/2)
    print("\nTraining outcome classifier (0=reject, 1=approve, 2=refer)…")
    y_outcome = df["outcome"].values
    y_out_train = y_outcome[idx_train]
    y_out_test  = y_outcome[idx_test]
    outcome_model = xgb.XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.8, random_state=42, n_jobs=-1,
        objective="multi:softprob", num_class=3, eval_metric="mlogloss",
    )
    outcome_model.fit(X_train, y_out_train, eval_set=[(X_test, y_out_test)], verbose=False)
    out_preds = outcome_model.predict(X_test)
    outcome_metrics = {
        "accuracy": float(accuracy_score(y_out_test, out_preds)),
        "f1_macro": float(f1_score(y_out_test, out_preds, average="macro")),
    }
    print(f"  Acc: {outcome_metrics['accuracy']:.3f}  F1-macro: {outcome_metrics['f1_macro']:.3f}")

    # ---------------- Save models ----------------
    pickle.dump(credit_model,   open(OUT / "credit_model.pkl", "wb"))
    pickle.dump(default_model,  open(OUT / "default_model.pkl", "wb"))
    pickle.dump(outcome_model,  open(OUT / "outcome_model.pkl", "wb"))
    pickle.dump(iso,            open(OUT / "isolation_forest.pkl", "wb"))
    with open(OUT / "feature_columns.json", "w") as f:
        json.dump(feature_columns, f)
    with open(OUT / "fraud_rules.json", "w") as f:
        json.dump(FRAUD_RULES, f, indent=2)

    metrics = {
        "credit_model":   credit_metrics,
        "default_model":  default_metrics,
        "outcome_model":  outcome_metrics,
        "n_train": int(len(X_train)),
        "n_test":  int(len(X_test)),
        "n_features": len(feature_columns),
    }
    with open(OUT / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nWrote metrics: {metrics}")

    # ---------------- SHAP on credit model ----------------
    print("\nComputing SHAP for credit model + saving summary plot…")
    explainer = shap.TreeExplainer(credit_model)
    shap_values = explainer.shap_values(X_test.iloc[:500])
    plt.figure(figsize=(10, 7))
    shap.summary_plot(shap_values, X_test.iloc[:500], show=False, max_display=15)
    plt.tight_layout()
    plt.savefig(OUT / "shap_summary.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {OUT/'shap_summary.png'}")

    # ---------------- Sample predictions ----------------
    print("\nGenerating 5 sample applicant predictions…")
    sample_idx = [10, 100, 500, 1000, 2500]
    samples = []
    explainer_def = shap.TreeExplainer(credit_model)
    for sid in sample_idx:
        row = df.iloc[[sid]]
        x = X_all.iloc[[sid]]
        cibil_pred = float(np.clip(credit_model.predict(x)[0], 300, 900))
        def_prob = float(default_model.predict_proba(x)[0, 1])
        out_proba = outcome_model.predict_proba(x)[0]
        decision = ["reject", "approve", "refer"][int(out_proba.argmax())]
        f_score, f_flags = fraud_rules_score(row.iloc[0])
        iso_score = float(iso.decision_function(x)[0])
        # top 3 reasons via SHAP
        sv = explainer_def.shap_values(x)
        abs_sv = np.abs(sv[0])
        top3_idx = abs_sv.argsort()[-3:][::-1]
        top3 = [
            {"feature": feature_columns[i], "contribution": float(sv[0, i])}
            for i in top3_idx
        ]
        samples.append({
            "applicant_id": row.iloc[0]["applicant_id"],
            "loan_type": row.iloc[0]["loan_type"],
            "monthly_income_inr": int(row.iloc[0]["monthly_income_inr"]),
            "loan_amount_inr": int(row.iloc[0]["loan_amount_inr"]),
            "cibil_actual": int(row.iloc[0]["cibil_score"]),
            "cibil_predicted": round(cibil_pred, 1),
            "default_probability": round(def_prob, 4),
            "decision": decision,
            "decision_probabilities": {
                "reject": round(float(out_proba[0]), 3),
                "approve": round(float(out_proba[1]), 3),
                "refer": round(float(out_proba[2]), 3),
            },
            "fraud_score": round(f_score, 3),
            "fraud_flags": f_flags,
            "anomaly_score": round(iso_score, 3),
            "top_3_reasons": top3,
        })
    with open(OUT / "sample_predictions.json", "w") as f:
        json.dump(samples, f, indent=2)
    print(f"  Saved {len(samples)} samples to {OUT/'sample_predictions.json'}")
    print("\nALL DONE. Models, metrics, SHAP, samples saved.")


if __name__ == "__main__":
    main()
