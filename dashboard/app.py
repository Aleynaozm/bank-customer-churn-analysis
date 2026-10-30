import getpass
import joblib
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Bank Churn Dashboard", layout="wide")

@st.cache_data
def load_data():
    engine = create_engine(f"postgresql+psycopg2://{getpass.getuser()}@localhost:5432/bank")
    return pd.read_sql("SELECT * FROM customers", engine)

@st.cache_resource
def load_model():
    return joblib.load("models/xgb_churn.joblib")

df = load_data()
bundle = load_model()

st.title("🏦 Bank Customer Churn Dashboard")

# --- KPI'lar ---
c1, c2, c3 = st.columns(3)
c1.metric("Müşteri", f"{len(df):,}")
c2.metric("Churn oranı", f"%{df.exited.mean()*100:.2f}")
c3.metric("Aktif üye oranı", f"%{df.is_active_member.mean()*100:.1f}")

# --- Filtre + grafikler ---
country = st.sidebar.multiselect("Ülke", df.geography.unique(), default=list(df.geography.unique()))
f = df[df.geography.isin(country)]

col1, col2 = st.columns(2)
col1.subheader("Ülkeye göre churn (%)")
col1.bar_chart(f.groupby("geography").exited.mean() * 100)
col2.subheader("Ürün sayısına göre churn (%)")
col2.bar_chart(f.groupby("num_of_products").exited.mean() * 100)

# --- Tek müşteri tahmini ---
st.header("🔮 Müşteri risk tahmini")
a, b, c = st.columns(3)
age = a.slider("Yaş", 18, 92, 40)
products = a.selectbox("Ürün sayısı", [1, 2, 3, 4], index=1)
active = a.radio("Aktif üye mi?", [1, 0], format_func=lambda x: "Evet" if x else "Hayır")
geo = b.selectbox("Ülke", ["France", "Germany", "Spain"])
gender = b.selectbox("Cinsiyet", ["Female", "Male"])
balance = b.number_input("Bakiye", 0.0, 260000.0, 50000.0)
credit = c.slider("Kredi skoru", 350, 850, 650)
tenure = c.slider("Müşteri süresi (yıl)", 0, 10, 5)
card = c.radio("Kredi kartı var mı?", [1, 0], format_func=lambda x: "Evet" if x else "Hayır")
salary = c.number_input("Tahmini maaş", 0.0, 200000.0, 100000.0)

row = {
    "credit_score": credit, "age": age, "tenure": tenure, "balance": balance,
    "num_of_products": products, "has_cr_card": card, "is_active_member": active,
    "estimated_salary": salary,
    "geography_Germany": int(geo == "Germany"), "geography_Spain": int(geo == "Spain"),
    "gender_Male": int(gender == "Male"),
}
X = pd.DataFrame([row]).reindex(columns=bundle["columns"], fill_value=0)
p = bundle["model"].predict_proba(X)[0, 1]

st.metric("Ayrılma olasılığı", f"%{p*100:.1f}")
st.progress(float(p))
if p > 0.5:
    st.error("Yüksek risk — elde tutma kampanyasına aday")
else:
    st.success("Düşük risk")
