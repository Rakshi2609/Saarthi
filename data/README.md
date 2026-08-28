# Saarthi Applicant Dataset

5,000 synthetic Indian rural/semi-urban loan applicants generated to
train and demo the AI-powered Smart Lending Decision Hub.

**Disclaimer:** This is **demo / synthetic data**. It does NOT represent
real TVS Credit, CIBIL, or any bureau customer. Real production scoring
would use de-identified bureau + LMS data — see the disclaimer banner
in the demo UI.

## Schema (28 columns)

| Column | Type | Description |
|---|---|---|
| `applicant_id` | str | `APP000001` ... `APP005000` |
| `name` | str | Display name only |
| `age` | int | 21-68 |
| `gender` | cat | M / F |
| `state` | cat | 13 Indian states |
| `district` | cat | district within state |
| `lat`, `lng` | float | applicant geolocation (state centroid ± 0.4) |
| `employment` | cat | Salaried, Self Employed Business, Farmer, Daily Wage, Gig Worker, Driver, Homemaker |
| `monthly_income_inr` | int | 5,000 – 80,000 |
| `loan_type` | cat | Two Wheeler, Used Car, Tractor, Used Commercial Vehicle, Three Wheeler, Consumer Durable, Personal Loan, Mobile Loan, Gold Loan |
| `loan_amount_inr` | int | 6,000 – 1,200,000 |
| `loan_tenure_months` | int | 9 – 60 |
| `is_agricultural` | 0/1 | farmer or tractor loan |
| `crop_type` | str | paddy / wheat / cotton / ... |
| `land_acres` | float | 0 – 12 |
| `ndvi_score` | float | 0 – 1 (synthetic satellite proxy) |
| `rainfall_30d_mm` | float | rainfall deficit (negative = surplus) |
| `phone` | str | E.164 mock |
| `email` | str | mix of real + disposable domains |
| `device` | cat | Android-Samsung/Xiaomi/Realme/iPhone/Other-Android/Feature-Phone |
| `browser` | cat | browser/app source |
| `application_timestamp` | ISO | within Aug 2026 |
| `cibil_score` | int | 300 – 900 (synthetic, calibrated to 640 ± 70 mean) |
| `existing_loans` | int | 0 – 5 |
| `default_history` | 0/1 | any prior default |
| `dti` | float | estimated EMI / monthly income |
| `default_probability` | float | 0.005 – 0.95 (synthetic logistic ground truth) |
| `outcome` | 0/1/2 | 0=reject, 1=approve, 2=refer |
| `app_velocity_30d` | int | apps from same phone in 30d |
| `email_age_days` | int | 1 – 4000 |
| `phone_age_days` | int | 30 – 4000 |
| `ip_geo_mismatch` | 0/1 | IP geo != applicant geo |
| `device_shared_count_30d` | int | apps from same device fingerprint |
| `disposable_email` | 0/1 | tempmail / yandex / similar |
| `fraud_score` | float | 0.01 – 0.99 (synthetic, from rules + sigmoid) |

## Outcome distribution (seed=42)

Approx:
- 0 (reject) ≈ 8-10%
- 1 (approve) ≈ 65-70%
- 2 (refer)  ≈ 20-25%

## How to regenerate

```bash
cd /home/appu/saarthi
python3 scripts/generate_data.py
```

Deterministic — seed=42.
