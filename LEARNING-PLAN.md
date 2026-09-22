# Learn by extending ChurnLab

This is a working starting point. Resume readiness means being able to reproduce, change, and explain it. Keep a dated learning log of changes you personally make.

## Week 1: Own the problem and data
- Run the dashboard and explain precision and recall using its confusion matrix.
- Explain why the prediction window is three months here, not the 30-day teaching example from our conversation.
- Inspect five rows in the CSV and distinguish inputs, target, and generated record ID.
- Explain why `complains` is binary.
- Deliverable: a one-page problem statement in your own words.

## Week 2: Own the SQL
- Run all eight supplied queries against the SQLite database.
- Add subscription-length bands with counts and churn rates.
- Write a LEFT JOIN that retains customers without model scores. Explain why training customers have no model_scores record.
- Deliverable: three new SQL queries and comments explaining their business purpose.

## Week 3: Own data quality
- Reproduce missing-value counts and full-row repetition counts.
- Explain why blindly deleting repeated rows might be wrong.
- Inspect the check that prevents identical feature groups from crossing splits.
- Deliverable: a quality report with checks, findings, and decisions.

## Week 4: Understand baselines
- Explain the dummy baseline and the logistic regression pipeline.
- Reproduce train/validation/test counts and inspect the fixed seeds.
- Explain why preprocessing must learn from training data only.
- Deliverable: a two-minute walkthrough of the model-building workflow.

## Week 5: Understand model selection
- Compare validation average precision across the three models.
- Explain why the best model was selected using validation results.
- Explain the chosen F2 objective and how recall was prioritized.
- Deliverable: a model-comparison explanation, including why accuracy alone is insufficient.

## Week 6: Understand threshold decisions
- Explore threshold changes on validation data only.
- Describe false positives and false negatives in business terms.
- Add a validation contact-budget analysis for top 5%, 10%, and 20%.
- Deliverable: a small table explaining what each contact budget captures.

## Week 7: Strengthen evaluation
- Inspect errors by tariff and complaint indicator; include group sizes.
- Describe how repeated profiles affect uncertainty.
- Propose a group-aware confidence interval or grouped cross-validation on development data as an extension.
- Do not repeatedly tune against the existing final test results. They are now known; use fresh external data for a new final assessment after substantial redesign.
- Deliverable: an error-analysis report and limitations section.

## Week 8: Make one visible improvement
- Choose one useful change: a new SQL-backed chart, better input explanation, or additional validation segmentation.
- Modify the app and explain the connection between your code and the user-facing result.
- Keep the source attribution and distinction between offline data and instant scoring.
- Deliverable: a recorded before/after demo.

## Week 9: Prepare your portfolio
- Review your GitHub repository's visibility and make it accessible to recruiters when ready.
- Include setup instructions, source license, screenshots, metrics, and limitations.
- Write resume bullets only for work you can explain and reproduce.
- Deliverable: a five-minute demonstration and two accurate resume bullets.

## Week 10: Interview practice
Explain: the business decision, target, observation window, exclusions, repeated profiles, baseline, selection metric, threshold, test results, and missing production capabilities.

Practice these questions:
1. Why not use accuracy as the headline metric?
2. Why was status excluded if UCI says it is an observation-window field?
3. Does removing age establish model fairness? Why not?
4. Why is a risk score not proof that a discount prevents churn?
5. What is the difference between model selection and threshold selection?
6. What would you change before connecting this to real customer data?
7. Which parts did you implement or modify yourself, and what assistance did you use?

## Example resume wording after you can defend the work

Customer Churn Analytics and Interactive Scoring | Python, SQL, scikit-learn, D3

- Developed a reproducible analysis of 3,150 public telecom records with SQL reporting, input-profile grouping across data splits, and validation-based model selection.
- Evaluated a random-forest classifier on 629 held-out records, obtaining 0.899 average precision and 96.9% recall at 54.6% precision; built an interactive threshold dashboard and browser scoring demonstration.

Use these statements only after reproducing the work and making the project your own. Describe it as assisted work when discussing how it was developed. Do not claim real-time data ingestion, company deployment, revenue gains, or reduced churn.
