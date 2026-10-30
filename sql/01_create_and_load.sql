-- 01_create_and_load.sql
-- Churn_Modelling veri seti icin tablo olusturma

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    row_number        INT,
    customer_id       INT PRIMARY KEY,
    surname           VARCHAR(50),
    credit_score      INT,
    geography         VARCHAR(20),
    gender            VARCHAR(10),
    age               INT,
    tenure            INT,
    balance           NUMERIC(12,2),
    num_of_products   INT,
    has_cr_card       SMALLINT,
    is_active_member  SMALLINT,
    estimated_salary  NUMERIC(12,2),
    exited            SMALLINT
);
