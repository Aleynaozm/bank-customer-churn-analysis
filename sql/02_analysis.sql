-- 02_analysis.sql: temel churn analizleri

-- 1) Genel churn orani
SELECT
    COUNT(*)                                    AS toplam_musteri,
    SUM(exited)                                 AS ayrılan,
    ROUND(100.0 * SUM(exited) / COUNT(*), 2)    AS churn_orani
FROM customers;

-- 2) Ulkeye gore
SELECT
    geography,
    COUNT(*)                                 AS musteri,
    SUM(exited)                              AS ayrılan,
    ROUND(100.0 * SUM(exited) / COUNT(*), 2) AS churn_orani
FROM customers
GROUP BY geography
ORDER BY churn_orani DESC;

-- 3) Yas bandina gore
SELECT
    CASE
        WHEN age < 30 THEN '30 alti'
        WHEN age BETWEEN 30 AND 44 THEN '30-44'
        WHEN age BETWEEN 45 AND 59 THEN '45-59'
        ELSE '60 ustu'
    END                                      AS yas_bandi,
    COUNT(*)                                 AS musteri,
    ROUND(100.0 * SUM(exited) / COUNT(*), 2) AS churn_orani
FROM customers
GROUP BY 1
ORDER BY churn_orani DESC;

-- 4) Cinsiyet x aktif uyelik
SELECT
    gender,
    is_active_member,
    COUNT(*)                                 AS musteri,
    ROUND(100.0 * SUM(exited) / COUNT(*), 2) AS churn_orani
FROM customers
GROUP BY gender, is_active_member
ORDER BY churn_orani DESC;
