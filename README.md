# Banka Müşteri Churn Analizi

**Canlı demo:** https://bank-customer-churn-analysis-ssvpufssnxyhsygyscgvaa.streamlit.app

Perakende banka müşteri kitlesinin uçtan uca churn (müşteri terk) analizi: PostgreSQL'de SQL keşfi, Python ile EDA, açıklanabilir bir XGBoost modeli (SHAP) ve interaktif Streamlit paneli.

## Problem
Mevcut bir müşteriyi kaybetmek, yeni müşteri kazanmaktan çok daha pahalıya mal olur. Amaç: (1) kimin, neden ayrıldığını anlamak ve (2) ayrılma riski yüksek müşterileri işaretleyen bir model kurarak elinde tutma (retention) eforunu rastgele değil, hedefli harcamak.

## Veri Seti
Kaggle "Churn Modelling" veri seti (shrutimechlearn) — 10.000 müşteri, 14 kolon.
PostgreSQL'e yüklendi; Python notebook'ları da aynı tabloyu kullanıyor.

## Teknoloji
PostgreSQL · Python · pandas · matplotlib/seaborn · scikit-learn · XGBoost · SHAP · Streamlit

## İş Akışı
1. **Yükleme** — `sql/01_create_and_load.sql`: tablo şeması + CSV'nin toplu `\copy` ile yüklenmesi
2. **SQL analizi** — `sql/02_analysis.sql`: ülkeye, yaş bandına, ürün sayısına ve cinsiyet × aktivite durumuna göre churn
3. **EDA** — `notebooks/01_eda.ipynb`: dağılımlar, bakiye davranışı, korelasyonlar
4. **Modelleme** — `notebooks/02_modeling.ipynb`: baseline → lojistik regresyon → XGBoost, tabakalı %80/%20 bölme, 5 katlı çapraz doğrulama, SHAP ile açıklanabilirlik
5. **Panel** — `dashboard/app.py`: KPI kartları, segment filtreleri, tek müşteri risk tahmini

## Temel Bulgular (SQL)
| Segment | Churn oranı |
| --- | --- |
| Genel | %20.37 |
| Almanya | %32.44 |
| İspanya | %16.67 |
| Fransa | %16.15 |
| Yaş 45–59 | %49.45 |
| Yaş 60+ | %27.95 |
| Yaş 30–44 | %14.44 |
| Yaş 30 altı | %7.56 |
| Kadın, pasif üye | %32.09 |
| Erkek, pasif üye | %22.28 |
| Kadın, aktif üye | %18.13 |
| Erkek, aktif üye | %11.20 |

- Alman müşteriler Fransız veya İspanyol müşterilerin yaklaşık iki katı oranda ayrılıyor.
- 45–59 bandı tek başına en riskli grup: %49.45'e karşılık 30 yaş altı müşterilerde %7.56.
- Aktif üyelik, her iki cinsiyette de churn oranını yaklaşık 10 puan düşürüyor.
- Müşterilerin %36.17'si sıfır bakiye tutuyor; bunların %13.82'si ayrılırken, bakiyeli hesaplarda oran %24.08.

## Model Sonuçları
Tabakalı %80/%20 bölme (eğitim 8.000 / test 2.000), kategorik değişkenler one-hot kodlandı.
"Hiç kimse ayrılmaz" şeklindeki basit bir baseline bile %79.6 doğruluk verirken tek bir ayrılan müşteriyi bile yakalamıyor — bu yüzden burada hedef metrik doğruluk değil, **recall**.

| Model | ROC-AUC | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| Lojistik regresyon | 0.782 | 0.399 | 0.708 | 0.510 |
| XGBoost | **0.865** | **0.513** | **0.727** | **0.602** |

XGBoost'un çapraz doğrulama ROC-AUC değeri 0.765 ± 0.014, test skoruna çok yakın; yani model overfit etmiyor. Varsayılan eşikte ayrılan müşterilerin ~%73'ünü yakalıyor ve işaretlediği müşterilerin yaklaşık yarısı gerçekten ayrılıyor (temel oran %20). Bu listeye kurulan bir retention kampanyası, herkesi aramaya kıyasla yaklaşık 2.5 kat daha verimli.

## Model Neden Böyle Diyor? (SHAP)
- **age** açık ara en güçlü etken; etkisi doğrusal değil ve 45–59 bandında yoğunlaşıyor
- **num_of_products** U şeklinde: 1 ürünli ve 3–4 ürünli müşteriler riskli, 2 ürünli müşteriler en sadık — bu deseni yalnızca ağaç tabanlı bir model yakalayabilir
- **is_active_member = 0** riski yukarı itiyor; yüksek **balance** ve **Almanya** makul düzeyde risk ekliyor
- **credit_score**, **tenure**, **estimated_salary** ve **has_cr_card** neredeyse hiç katkı sağlamıyor

## Panel
`dashboard/app.py` — KPI kartları, ülkeye ve ürün sayısına göre churn grafikleri, girilen bir müşteri profili için ayrılma olasılığı döndüren form.

## Nasıl Çalıştırılır
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
createdb bank
psql -d bank -f sql/01_create_and_load.sql
```
Ardından etkileşimli bir psql oturumunda (`psql -d bank`):
```sql
\copy customers FROM 'data/Churn_Modelling.csv' WITH (FORMAT csv, HEADER true)
```
Son olarak:
```bash
streamlit run dashboard/app.py
```

## Veri Kaynağı
Kaggle — Churn Modelling (shrutimechlearn): https://www.kaggle.com/shrutimechlearn/churn-modelling

## Lisans
MIT
