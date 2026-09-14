-- Delivery Operations Intelligence | Recruiter-ready SQL pack
-- The application materializes the cleaned order_fact table in SQLite.

-- 1. Monthly service-level trend
SELECT purchase_month,
       COUNT(*) AS orders,
       ROUND(AVG(CASE WHEN is_delivered = 1 THEN 1.0 - is_late ELSE NULL END), 4) AS on_time_rate,
       ROUND(AVG(is_cancelled), 4) AS cancellation_rate
FROM order_fact
GROUP BY purchase_month
ORDER BY purchase_month;

-- 2. Market-level service risk with a minimum-volume guardrail
SELECT customer_state,
       COUNT(*) AS orders,
       ROUND(AVG(is_late), 4) AS late_rate,
       ROUND(AVG(is_cancelled), 4) AS cancellation_rate,
       ROUND(AVG(NULLIF(review_score, 0)), 2) AS avg_rating
FROM order_fact
GROUP BY customer_state
HAVING COUNT(*) >= 100
ORDER BY late_rate DESC;

-- 3. Seller intervention queue
SELECT seller_id, seller_state,
       COUNT(*) AS orders,
       ROUND(AVG(is_late), 4) AS late_rate,
       ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
       ROUND(AVG(NULLIF(review_score, 0)), 2) AS avg_rating,
       ROUND(SUM(order_value), 2) AS order_value
FROM order_fact
GROUP BY seller_id, seller_state
HAVING COUNT(*) >= 30
ORDER BY late_rate DESC, orders DESC;

-- 4. Experience penalty: late vs on-time reviews
SELECT CASE WHEN is_late = 1 THEN 'Late' ELSE 'On time / other' END AS delivery_group,
       COUNT(*) AS reviewed_orders,
       ROUND(AVG(review_score), 2) AS avg_review_score,
       ROUND(AVG(CASE WHEN review_score IN (1,2) THEN 1.0 ELSE 0 END), 4) AS at_risk_review_rate
FROM order_fact
WHERE review_score > 0
GROUP BY delivery_group;

-- 5. Category operating profile
SELECT category, COUNT(*) AS orders,
       ROUND(AVG(is_late), 4) AS late_rate,
       ROUND(AVG(delivery_days), 2) AS median_proxy_delivery_days,
       ROUND(AVG(NULLIF(review_score, 0)), 2) AS avg_rating
FROM order_fact
WHERE is_delivered = 1
GROUP BY category
HAVING COUNT(*) >= 100
ORDER BY late_rate DESC;
