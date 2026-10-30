from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent.parent
DATA_PATH = BASE / "data" / "customers.csv"
MODEL_PATH = BASE / "models" / "xgb_churn.joblib"

st.set_page_config(page_title="Banka Müşteri Churn Analizi", page_icon="📊", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


@st.cache_resource
def load_model():
    bundle = joblib.load(MODEL_PATH)
    if isinstance(bundle, dict):
        return bundle["model"], list(bundle["columns"])
    return bundle, list(getattr(bundle, "feature_names_in_", []))


df = load_data()
model, features = load_model()

st.title("Banka Müşteri Churn Analizi")
st.caption("PostgreSQL · Python · XGBoost · SHAP · Streamlit")

st.sidebar.header("Filtreler")
countries = st.sidebar.multiselect(
    "Ülke", sorted(df["geography"].unique()), default=sorted(df["geography"].unique())
)
view = df[df["geography"].isin(countries)] if countries else df

c1, c2, c3 = st.columns(3)
c1.metric("Müşteri sayısı", f"{len(view):,}")
c2.metric("Churn oranı", f"%{view['exited'].mean() * 100:.2f}")
c3.metric("Aktif üye", f"%{view['is_active_member'].mean() * 100:.1f}")

st.subheader("Kırılımlara göre churn")
left, right = st.columns(2)

with left:
    by_geo = df.groupby("geography")["exited"].mean().mul(100).rename("Churn (%)").reset_index()
    st.bar_chart(by_geo.set_index("geography"))

with right:
    by_prod = view.groupby("num_of_products")["exited"].mean().mul(100).rename("Churn (%)").reset_index()
    st.bar_chart(by_prod.set_index("num_of_products"))

bands = pd.cut(view["age"], [0, 29, 44, 59, 200], labels=["30 altı", "30-44", "45-59", "60 üstü"])
by_age = view.groupby(bands, observed=True)["exited"].mean().mul(100).rename("Churn (%)")
by_age = by_age.reset_index()
by_age.columns = ["yaş bandı", "Churn (%)"]
st.bar_chart(by_age.set_index("yaş bandı"))

st.subheader("Müşteri risk tahmini")
with st.form("risk_form"):
    age = st.slider("Yaş", 18, 92, 45)
    credit_score = st.slider("Kredi puanı", 300, 850, 650)
    tenure = st.slider("Bankayla geçen yıl", 0, 10, 5)
    products = st.selectbox("Ürün sayısı", [1, 2, 3, 4], index=1)
    gender = st.selectbox("Cinsiyet", ["Female", "Male"])
    geography = st.selectbox("Ülke", ["France", "Germany", "Spain"], index=2)
    active = st.radio("Aktif üye", ["Hayır", "Evet"], index=1, horizontal=True)
    balance = st.number_input("Bakiye", 0.0, 300000.0, 50000.0, step=1000.0)
    card = st.radio("Kredi kartı", ["Hayır", "Evet"], index=1, horizontal=True)
    salary = st.number_input("Tahmini maaş", 0.0, 250000.0, 100000.0, step=1000.0)
    submitted = st.form_submit_button("Riski hesapla")

if submitted:
    row = pd.DataFrame([{
        "credit_score": credit_score,
        "geography": geography,
        "gender": gender,
        "age": age,
        "tenure": tenure,
        "balance": balance,
        "num_of_products": products,
        "has_cr_card": 1 if card == "Evet" else 0,
        "is_active_member": 1 if active == "Evet" else 0,
        "estimated_salary": salary,
    }])
    encoded = pd.get_dummies(row, columns=["geography", "gender"])
    encoded = encoded.reindex(columns=features, fill_value=0)
    proba = float(model.predict_proba(encoded)[0][1])

    st.progress(proba)
    st.metric("Ayrılma olasılığı", f"%{proba * 100:.1f}")
    if proba >= 0.5:
        st.error("Yüksek risk — retention kampanyasına alınmalı")
    else:
        st.success("Düşük risk")
