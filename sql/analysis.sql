-- 1. Overall observed churn. This is historical description, not model performance.
SELECT COUNT(*) AS customers, SUM(churn) AS churners,
       ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct
FROM customers;

-- 2. Tariff segments: 1=pay-as-you-go, 2=contractual.
SELECT tariff_plan, COUNT(*) AS customers, SUM(churn) AS churners,
       ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct
FROM customers GROUP BY tariff_plan;

-- 3. Complains is a BINARY indicator, not a support-ticket count.
SELECT complains, COUNT(*) AS customers, SUM(churn) AS churners,
       ROUND(100.0 * SUM(churn) / COUNT(*), 2) AS churn_rate_pct
FROM customers GROUP BY complains;

-- 4. WHERE filters customers; HAVING filters the resulting groups.
SELECT tariff_plan, COUNT(*) AS customers, SUM(churn) AS churners
FROM customers WHERE complains = 1
GROUP BY tariff_plan HAVING COUNT(*) >= 20;

-- 5. Exploratory usage bands. These thresholds are descriptive choices.
SELECT CASE WHEN frequency_of_use < 20 THEN 'Under 20 calls'
            WHEN frequency_of_use < 100 THEN '20-99 calls'
            ELSE '100+ calls' END AS usage_band,
       COUNT(*) AS customers, ROUND(100.0 * AVG(churn), 2) AS churn_rate_pct
FROM customers GROUP BY usage_band;

-- 6. Join customers to scores, then rank validation candidates within tariff.
WITH ranked AS (
 SELECT c.record_id, c.tariff_plan, s.risk_score,
        ROW_NUMBER() OVER (PARTITION BY c.tariff_plan ORDER BY s.risk_score DESC, c.record_id) AS priority
 FROM customers c JOIN model_scores s ON c.record_id = s.record_id
 WHERE c.split = 'validation'
)
SELECT * FROM ranked WHERE priority <= 5 ORDER BY tariff_plan, priority;

-- 7. Locked test confusion matrix at the validation-selected threshold.
SELECT SUM(CASE WHEN s.risk_score >= s.threshold AND c.churn=1 THEN 1 ELSE 0 END) AS true_positives,
       SUM(CASE WHEN s.risk_score >= s.threshold AND c.churn=0 THEN 1 ELSE 0 END) AS false_positives,
       SUM(CASE WHEN s.risk_score < s.threshold AND c.churn=1 THEN 1 ELSE 0 END) AS false_negatives,
       SUM(CASE WHEN s.risk_score < s.threshold AND c.churn=0 THEN 1 ELSE 0 END) AS true_negatives
FROM customers c JOIN model_scores s ON c.record_id = s.record_id WHERE c.split='test';

-- 8. Quality check: must return zero rows (no identical input groups cross splits).
SELECT feature_group, COUNT(DISTINCT split) AS partitions
FROM customers GROUP BY feature_group HAVING COUNT(DISTINCT split) > 1;
