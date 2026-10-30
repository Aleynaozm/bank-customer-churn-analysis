# Bank Customer Churn Analysis

End-to-end churn analysis of a retail bank customer base: SQL exploration in PostgreSQL,
Python EDA, an explainable XGBoost model (SHAP), and an interactive Streamlit dashboard.

## Problem
Losing an existing customer costs far more than acquiring a new one. The goal is to
(1) understand who leaves and why, and (2) build a model that flags customers at high risk
of churning so retention effort can be targeted instead of sprayed.

## Dataset
Kaggle "Churn Modelling" dataset (shrutimechlearn) — 10,000 customers, 14 columns.
Loaded into PostgreSQL; the same table feeds the Python notebooks.

## Tech Stack
PostgreSQL · Python · pandas · matplotlib/seaborn · scikit-learn · XGBoost · SHAP · Streamlit

## Pipeline
1. **Load** — `sql/01_create_and_load.sql`: schema + bulk `\copy` of the CSV
2. **SQL analysis** — `sql/02_analysis.sql`: churn by geography, age band, product count, gender × activity
3. **EDA** — `notebooks/01_eda.ipynb`: distributions, balance behaviour, correlations
4. **Modeling** — `notebooks/02_modeling.ipynb`: baseline → logistic regression → XGBoost, stratified 80/20 split, 5-fold CV, SHAP explainability
5. **Dashboard** — `dashboard/app.py`: KPI cards, segment filters, single-customer risk predictor

## Key Findings (SQL)
| Segment | Churn rate |
| --- | --- |
| Overall | 20.37% |
| Germany | 32.44% |
| Spain | 16.67% |
| France | 16.15% |
| Age 45–59 | 49.45% |
| Age 60+ | 27.95% |
| Age 30–44 | 14.44% |
| Age under 30 | 7.56% |
| Female, inactive | 32.09% |
| Male, inactive | 22.28% |
| Female, active | 18.13% |
| Male, active | 11.20% |

- German customers churn at roughly twice the rate of French or Spanish ones.
- The 45–59 band is the single riskiest group: 49.45% vs 7.56% for customers under 30.
- Active membership lowers churn by about 10 points for both genders.
- 36.17% of customers hold a zero balance; they churn at 13.82% vs 24.08% for funded accounts.

## Model Results
Stratified 80/20 split (train 8,000 / test 2,000), categoricals one-hot encoded.
A naive "nobody churns" baseline already scores 79.6% accuracy while catching zero
churners — so accuracy is not the target metric here; **recall** is.

| Model | ROC-AUC | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| Logistic regression | 0.782 | 0.399 | 0.708 | 0.510 |
| XGBoost | **0.865** | **0.513** | **0.727** | **0.602** |

XGBoost cross-validation ROC-AUC 0.765 ± 0.014 sits close to the test score, so the model
is not overfitting. At the default threshold it catches ~73% of leavers, and roughly half of
the customers it flags actually leave against a 20% base rate — a retention campaign built
on this list is about 2.5× more efficient than contacting everyone.

## Why the model says what it says (SHAP)
- **age** is by far the strongest driver, and the effect is non-linear, concentrated in 45–59
- **num_of_products** is U-shaped: 1-product and 3–4-product customers are risky, 2-product
  customers are the most loyal — a pattern only a tree model captures
- **is_active_member = 0** pushes risk up; high **balance** and **Germany** add moderate risk
- **credit_score**, **tenure**, **estimated_salary** and **has_cr_card** contribute almost nothing

## Dashboard
`dashboard/app.py` — KPI cards, churn by geography and product count, and a form that returns
a churn probability for any customer profile you type in.

## How to run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
createdb bank
psql -d bank -f sql/01_create_and_load.sql
