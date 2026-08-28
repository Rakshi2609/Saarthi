"""
Saarthi — Synthetic Applicant Dataset Generator
Generates 5,000 realistic Indian rural/semi-urban loan applicants with
realistic distributions for credit scoring, default, and fraud modeling.

Output: /home/appu/saarthi/data/applicants.csv
Schema is documented in /home/appu/saarthi/data/README.md
"""
import csv
import random
import math
from pathlib import Path

random.seed(42)  # reproducible

# ---------------------------------------------------------------------------
# Reference data — realistic India distributions
# ---------------------------------------------------------------------------

# States with their weight, avg rural income (Rs/month), loan product mix
STATES = [
    # (state, district, lat, lng, weight, avg_income, agri_share)
    ("Tamil Nadu", "Madurai",       9.9252, 78.1198, 0.08, 22000, 0.45),
    ("Tamil Nadu", "Salem",        11.6643, 78.1460, 0.06, 21000, 0.50),
    ("Tamil Nadu", "Tirunelveli",   8.7139, 77.7567, 0.05, 19000, 0.55),
    ("Karnataka",  "Mysuru",        12.2958, 76.6394, 0.07, 24000, 0.45),
    ("Karnataka",  "Belagavi",      15.8497, 74.4977, 0.05, 20000, 0.60),
    ("Karnataka",  "Tumakuru",      13.3392, 77.1003, 0.04, 19500, 0.55),
    ("Maharashtra","Nashik",        19.9975, 73.7898, 0.07, 25000, 0.50),
    ("Maharashtra","Aurangabad",    19.8762, 75.3433, 0.05, 22000, 0.55),
    ("Maharashtra","Latur",         18.4088, 76.5604, 0.04, 18000, 0.70),
    ("UP",         "Lucknow",       26.8467, 80.9462, 0.08, 23000, 0.50),
    ("UP",         "Varanasi",      25.3176, 82.9739, 0.06, 21000, 0.55),
    ("UP",         "Gorakhpur",     26.7606, 83.3732, 0.04, 18000, 0.65),
    ("Bihar",      "Patna",         25.5941, 85.1376, 0.06, 19000, 0.60),
    ("Bihar",      "Muzaffarpur",   26.1209, 85.3647, 0.04, 17000, 0.70),
    ("Rajasthan",  "Jaipur",        26.9124, 75.7873, 0.07, 24000, 0.45),
    ("Rajasthan",  "Jodhpur",       26.2389, 73.0243, 0.05, 21000, 0.50),
    ("Rajasthan",  "Udaipur",       24.5854, 73.7125, 0.04, 20000, 0.55),
    ("Gujarat",    "Surat",         21.1702, 72.8311, 0.05, 26000, 0.35),
    ("Gujarat",    "Rajkot",        22.3039, 70.8022, 0.04, 23000, 0.45),
    ("MP",         "Indore",        22.7196, 75.8577, 0.05, 24000, 0.45),
    ("MP",         "Bhopal",        23.2599, 77.4126, 0.04, 22000, 0.50),
    ("West Bengal","Murshidabad",   24.1750, 88.2800, 0.04, 19000, 0.65),
    ("Andhra",     "Guntur",        16.3067, 80.4365, 0.04, 22000, 0.55),
    ("Telangana",  "Warangal",      17.9689, 79.5941, 0.04, 21000, 0.55),
]

LOAN_TYPES = [
    # (loan_type, weight, min_amt, max_amt, avg_tenure_months)
    ("Two Wheeler",      0.30, 35000,   120000, 24),
    ("Used Car",         0.12, 150000,  600000, 48),
    ("Tractor",          0.15, 300000,  1200000, 60),
    ("Used Commercial Vehicle", 0.08, 250000, 900000, 48),
    ("Three Wheeler",    0.06, 120000,  350000, 36),
    ("Consumer Durable", 0.10, 8000,    60000, 12),
    ("Personal Loan",    0.08, 30000,   200000, 24),
    ("Mobile Loan",      0.06, 6000,    30000, 9),
    ("Gold Loan",        0.05, 20000,   500000, 12),
]

CROPS = [
    ("Paddy", 0.30, 0.6, 0.95),   # name, share, min NDVI, max NDVI
    ("Wheat", 0.20, 0.4, 0.85),
    ("Sugarcane", 0.10, 0.6, 0.95),
    ("Cotton", 0.10, 0.35, 0.75),
    ("Maize", 0.08, 0.4, 0.85),
    ("Groundnut", 0.07, 0.35, 0.7),
    ("Soybean", 0.07, 0.35, 0.75),
    ("Vegetables", 0.05, 0.5, 0.9),
    ("Pulses", 0.03, 0.3, 0.65),
]

# Employment types
EMPLOYMENT = [
    ("Salaried", 0.25, 1.0),       # higher income stability multiplier
    ("Self Employed Business", 0.20, 0.85),
    ("Farmer", 0.30, 0.60),         # lower stability but agri
    ("Daily Wage", 0.10, 0.55),
    ("Gig Worker", 0.08, 0.60),
    ("Driver", 0.05, 0.70),
    ("Homemaker", 0.02, 0.50),      # low income but co-applicant eligible
]

DEVICES = ["Android-Samsung", "Android-Xiaomi", "Android-Realme", "iPhone", "Other-Android", "Feature-Phone"]
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com", "yandex.com", "tempmail.com"]
BROWSERS = ["Chrome", "Safari", "Firefox", "Edge", "Opera", "InApp"]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def weighted_choice(items, weight_index=1):
    """items: list of tuples; weight is at `weight_index` (default 1)."""
    weights = [it[weight_index] for it in items]
    return random.choices(items, weights=weights, k=1)[0]


def gauss_clamp(mean, std, lo, hi):
    return max(lo, min(hi, random.gauss(mean, std)))


def pick_employment():
    return weighted_choice(EMPLOYMENT)  # (name, weight, stability_mult)


def pick_state():
    return weighted_choice(STATES, weight_index=4)  # weight is at index 4


def pick_loan_type():
    return weighted_choice(LOAN_TYPES, weight_index=1)


def pick_crop():
    return weighted_choice(CROPS, weight_index=1)


def compute_risk_features(applicant, is_agri, state, loan_type, income):
    """Return (cibil_score, default_prob, fraud_score, top_signals_dict)."""
    # CIBIL 300-900 distribution
    # Salaried + urban -> mean ~720; farmer rural -> mean ~640
    base = 640
    if applicant["employment"] == "Salaried":
        base += 60
    elif applicant["employment"] == "Farmer":
        base -= 10
    elif applicant["employment"] in ("Daily Wage", "Homemaker"):
        base -= 40
    if state[5] < 0.50:  # agri_share
        base -= 10
    cibil = int(gauss_clamp(base, 70, 300, 850))
    applicant["cibil_score"] = cibil

    # Existing loans — 0 to 5
    existing_loans = max(0, int(gauss_clamp(1.0, 1.2, 0, 5)))
    applicant["existing_loans"] = existing_loans

    # Default history: lower if cibil good
    p_default_hist = max(0, (650 - cibil) / 800)
    default_history = 1 if random.random() < p_default_hist else 0
    applicant["default_history"] = default_history

    # Loan amount vs income ratio (debt-to-income, higher = riskier)
    monthly_income = max(8000, income)
    loan_amt = applicant["loan_amount_inr"]
    emi = loan_amt / max(12, applicant["loan_tenure_months"]) * 0.022  # rough EMI factor
    dti = emi / monthly_income
    applicant["dti"] = round(dti, 3)

    # Default probability — logistic
    z = (
        -3.5
        + 0.0035 * (700 - cibil)
        + 1.8 * dti
        + 0.7 * default_history
        + 0.4 * (existing_loans - 1)
        + 0.3 * (1 if applicant["employment"] in ("Daily Wage", "Homemaker") else 0)
        - 0.5 * (1 if applicant["employment"] == "Salaried" else 0)
        - 0.001 * (monthly_income - 25000) / 1000
        - 0.2 * (1 if is_agri and random.random() < 0.6 else 0)  # some agri customers perform well
    )
    default_prob = 1 / (1 + math.exp(-z))
    default_prob = max(0.005, min(0.95, default_prob))
    applicant["default_probability"] = round(default_prob, 4)

    # Outcome: 0=reject, 1=approve, 2=refer
    if default_prob > 0.55 or cibil < 580 or dti > 0.65:
        outcome = 0
    elif default_prob > 0.30 or dti > 0.45 or cibil < 660:
        outcome = 2
    else:
        outcome = 1
    applicant["outcome"] = outcome

    # Fraud signals
    # application velocity: apps from same phone in 30 days
    applicant["app_velocity_30d"] = max(1, int(gauss_clamp(1.4, 1.5, 1, 12)))
    # email age days
    applicant["email_age_days"] = max(0, int(gauss_clamp(900, 800, 1, 4000)))
    # phone account age days
    applicant["phone_age_days"] = max(30, int(gauss_clamp(900, 700, 30, 4000)))
    # ip geo mismatch
    applicant["ip_geo_mismatch"] = 1 if random.random() < 0.07 else 0
    # device fingerprint shared with other apps
    applicant["device_shared_count_30d"] = max(0, int(gauss_clamp(0.5, 0.8, 0, 5)))
    # disposable email domain
    applicant["disposable_email"] = 1 if applicant["email"].split("@")[1] in ("tempmail.com", "yandex.com") else 0

    # fraud score: weighted sum + anomaly
    fraud_z = (
        0.25 * (applicant["app_velocity_30d"] - 1)
        + 0.001 * max(0, 30 - applicant["email_age_days"]) / 10
        + 0.0008 * max(0, 90 - applicant["phone_age_days"]) / 10
        + 1.5 * applicant["ip_geo_mismatch"]
        + 0.5 * applicant["device_shared_count_30d"]
        + 2.0 * applicant["disposable_email"]
    )
    fraud_score = 1 / (1 + math.exp(-fraud_z + 1.5))  # sigmoid shifted
    fraud_score = max(0.01, min(0.99, fraud_score))
    applicant["fraud_score"] = round(fraud_score, 4)


def make_applicant(idx):
    state = pick_state()
    state_name, district, lat, lng, _, base_income, agri_share = state
    employment = pick_employment()[0]

    # Income: noise around base, plus employment adjustment
    income_mult = {
        "Salaried": 1.15, "Self Employed Business": 1.1, "Farmer": 0.85,
        "Daily Wage": 0.65, "Gig Worker": 0.75, "Driver": 0.80, "Homemaker": 0.50
    }[employment]
    monthly_income = int(gauss_clamp(base_income * income_mult, base_income * 0.25, 5000, 80000))

    # Age: 21-65
    age = int(gauss_clamp(38, 10, 21, 68))

    # Loan
    loan_type, _, min_amt, max_amt, tenure = pick_loan_type()
    loan_amount = int(gauss_clamp((min_amt + max_amt) / 2, (max_amt - min_amt) / 4, min_amt, max_amt))
    loan_amount = round(loan_amount / 1000) * 1000  # round to nearest 1k

    # Agri signals (only if farmer in agri-heavy state, or loan is Tractor)
    is_agri = (employment == "Farmer" and random.random() < agri_share) or loan_type == "Tractor"
    crop_name, _, ndvi_min, ndvi_max = pick_crop() if is_agri else (None, None, None, None)
    ndvi = round(random.uniform(ndvi_min, ndvi_max), 3) if is_agri else 0.0
    land_acres = round(random.uniform(0.5, 12.0), 2) if is_agri else 0.0
    # weather: rainfall deficit in last 30 days (mm, negative = surplus)
    rainfall_30d = round(random.gauss(-10, 40), 1) if is_agri else 0.0

    # Phone + email
    phone = f"+91{random.randint(7000000000, 9999999999)}"
    email_local = f"{['ramesh', 'suresh', 'priya', 'anita', 'arjun', 'kavita', 'manoj', 'deepa', 'rahul', 'pooja'][random.randint(0,9)]}{random.randint(10,99)}"
    email = f"{email_local}@{random.choice(EMAIL_DOMAINS)}"

    applicant = {
        "applicant_id": f"APP{idx:06d}",
        "name": f"Applicant {idx}",
        "age": age,
        "gender": random.choice(["M", "F"]),
        "state": state_name,
        "district": district,
        "lat": round(lat + random.uniform(-0.4, 0.4), 4),
        "lng": round(lng + random.uniform(-0.4, 0.4), 4),
        "employment": employment,
        "monthly_income_inr": monthly_income,
        "loan_type": loan_type,
        "loan_amount_inr": loan_amount,
        "loan_tenure_months": tenure,
        "is_agricultural": int(is_agri),
        "crop_type": crop_name or "",
        "land_acres": land_acres,
        "ndvi_score": ndvi,
        "rainfall_30d_mm": rainfall_30d,
        "phone": phone,
        "email": email,
        "device": random.choice(DEVICES),
        "browser": random.choice(BROWSERS),
        "application_timestamp": f"2026-08-{random.randint(1,28):02d}T{random.randint(8,21):02d}:{random.randint(0,59):02d}:00",
    }

    compute_risk_features(applicant, is_agri, state, loan_type, monthly_income)
    return applicant


def main():
    out_path = Path("/home/appu/saarthi/data/applicants.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n = 5000
    rows = [make_applicant(i + 1) for i in range(n)]

    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # Print summary
    from collections import Counter
    print(f"Wrote {n} applicants to {out_path}")
    print(f"Outcome distribution: {Counter(r['outcome'] for r in rows)}")
    print(f"Loan type share: {Counter(r['loan_type'] for r in rows).most_common(5)}")
    print(f"Avg cibil: {sum(r['cibil_score'] for r in rows) / n:.0f}")
    print(f"Avg default_prob: {sum(r['default_probability'] for r in rows) / n:.3f}")
    print(f"Avg fraud_score: {sum(r['fraud_score'] for r in rows) / n:.3f}")


if __name__ == "__main__":
    main()
