# ChurnLab model report

## Decision and scope
Rank historical telecom profiles for possible retention outreach. The demonstration scores profiles instantly in the browser; it has no live data ingestion or telecom integration. Outreach benefits are unmeasured.

Source: [UCI Iranian Churn (2020)](https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset), DOI 10.24432/C5JW3Z, CC BY 4.0. UCI describes inputs from the first nine months and churn status at month 12. This is a three-month prediction gap. The specific cancellation-event definition and exact dates are unavailable.

## Data quality
- 3,150 records; 495 churn labels.
- 0 missing cells.
- 300 repeated full rows, retained because stable customer IDs are absent.
- 365 repeated included-input profiles, grouped so they cannot cross splits.
- Charge amount has a source-documentation discrepancy: described as 0–9, but observed values reach 10. Values are retained; the app displays the observed training range. Operational use would require clarification.
- Generated record IDs are source-row references, not real customer identifiers.

## Features and exclusions
Nine included predictors: call failures, complaint indicator, subscription length, charge band, call seconds, call count, SMS count, distinct called numbers, and tariff plan. Complaint is a binary flag, not a count. Counts summarize the observation window.

Status is excluded pending confirmation of its business meaning; the source does describe non-target fields as observation-window data, so this report does not claim proven temporal leakage. Customer value is excluded because its formula needs verification. Age and age group are excluded; this does not demonstrate fairness or eliminate demographic proxies.

## Reproducible protocol
Use a five-fold stratified group split with seed 42, reserving the first fold as test. Use a four-fold stratified group split with seed 17 on the remaining data, reserving the first fold as validation. Groups are hashes of included inputs, with labels excluded. This is a grouped random evaluation, not a temporal validation; missing customer IDs also prevent definitive customer-identity separation.

Train: 1886 records. Validation: 635. Test: 629.

Fit dummy, logistic-regression, and random-forest candidates using training data. The logistic baseline applies log1p and training-fitted standardization; the forest uses raw inputs. Select the non-dummy model by validation average precision. Select a threshold from 0.05 to 0.95 in steps of 0.01 by validation F2. F2 assigns recall greater weight; this is a stated project objective, not an estimated business cost optimum. Evaluate the selected model and threshold once on test data. No refitting on validation data is performed.

Selected model: **Random forest**. Fixed threshold: **0.14**.

## Fixed test results

| Measure | Result |
|---|---:|
| Test records | 629 |
| Actual churners | 98 |
| Average precision | 0.8987 |
| ROC-AUC | 0.9768 |
| Recall | 96.94% |
| Precision | 54.60% |
| Correctly flagged churners | 95 |
| False alarms | 79 |
| Missed churners | 3 |
| Correctly unflagged | 452 |
| Precision in top 10% (63 records) | 93.65% |
| Recall in top 10% | 60.20% |
| Lift in top 10% over test prevalence | 6.01x |

At this recall-focused operating point, 174 customers are flagged: 95 actual churners and 79 non-churners. These results measure historical classification, not retention impact. Top-budget ranking uses a stable tie-break on dataset order; tied scores near a cutoff can affect exact counts. Average precision is reported using scikit-learn's average_precision_score; it is not trapezoidal PR-AUC.

## Limitations and next steps
The dataset is small, historical, and drawn from one company. The test result is one grouped split, not a population guarantee. Repeated profiles reduce effective independent sample size. No confidence intervals, prospective validation, external validation, probability calibration, or comprehensive fairness audit are provided. Models output uncalibrated scores. No financial savings, reduced churn, or causal effects have been measured. Permutation importance is global predictive association, not an individual explanation.

Before production: confirm field definitions and unique customer IDs, audit timestamp availability, validate on future data, assess calibration and fairness, define the cost of errors, monitor drift, secure access, and test outreach effectiveness with an appropriate experiment. After using test results to redesign the model, obtain a fresh final evaluation set.

## Reproduction
Run `python src/train.py`, then `python -m unittest discover -s tests -p "check_data.py"` and `node tests/check_engine.cjs`. The pipeline recreates the SQLite database, SQL results, model, browser data bundle, and this report. Reload the dashboard after regeneration.

Source SHA-256: `90d5fb6bd1630cd4de4b4d28fcf8b4cb92a8f6ab7484605b0799d47386f7dbe1`.

Runtime versions: {"numpy": "2.5.3", "pandas": "3.0.1", "python": "3.12.14", "sklearn": "1.9.1"}.
