"""Generate the readable report from measured pipeline outputs."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def build_report():
    m=json.loads((ROOT/'reports/metrics.json').read_text())
    t=m['test']
    text=f'''# ChurnLab model report

## Decision and scope
Rank historical telecom profiles for possible retention outreach. The demonstration scores profiles instantly in the browser; it has no live data ingestion or telecom integration. Outreach benefits are unmeasured.

Source: [UCI Iranian Churn (2020)]({m['source']}), DOI 10.24432/C5JW3Z, CC BY 4.0. UCI describes inputs from the first nine months and churn status at month 12. This is a three-month prediction gap. The specific cancellation-event definition and exact dates are unavailable.

## Data quality
- {m['rows']:,} records; {m['churners']} churn labels.
- {m['missing_cells']} missing cells.
- {m['raw_duplicate_rows']} repeated full rows, retained because stable customer IDs are absent.
- {m['repeated_feature_rows']} repeated included-input profiles, grouped so they cannot cross splits.
- Charge amount has a source-documentation discrepancy: described as 0–9, but observed values reach 10. Values are retained; the app displays the observed training range. Operational use would require clarification.
- Generated record IDs are source-row references, not real customer identifiers.

## Features and exclusions
Nine included predictors: call failures, complaint indicator, subscription length, charge band, call seconds, call count, SMS count, distinct called numbers, and tariff plan. Complaint is a binary flag, not a count. Counts summarize the observation window.

Status is excluded pending confirmation of its business meaning; the source does describe non-target fields as observation-window data, so this report does not claim proven temporal leakage. Customer value is excluded because its formula needs verification. Age and age group are excluded; this does not demonstrate fairness or eliminate demographic proxies.

## Reproducible protocol
Use a five-fold stratified group split with seed 42, reserving the first fold as test. Use a four-fold stratified group split with seed 17 on the remaining data, reserving the first fold as validation. Groups are hashes of included inputs, with labels excluded. This is a grouped random evaluation, not a temporal validation; missing customer IDs also prevent definitive customer-identity separation.

Train: {m['splits']['train']['n']} records. Validation: {m['splits']['validation']['n']}. Test: {m['splits']['test']['n']}.

Fit dummy, logistic-regression, and random-forest candidates using training data. The logistic baseline applies log1p and training-fitted standardization; the forest uses raw inputs. Select the non-dummy model by validation average precision. Select a threshold from 0.05 to 0.95 in steps of 0.01 by validation F2. F2 assigns recall greater weight; this is a stated project objective, not an estimated business cost optimum. Evaluate the selected model and threshold once on test data. No refitting on validation data is performed.

Selected model: **{m['selected_model']}**. Fixed threshold: **{m['threshold']:.2f}**.

## Fixed test results

| Measure | Result |
|---|---:|
| Test records | {t['n']} |
| Actual churners | {t['tp']+t['fn']} |
| Average precision | {t['average_precision']:.4f} |
| ROC-AUC | {t['roc_auc']:.4f} |
| Recall | {t['recall']:.2%} |
| Precision | {t['precision']:.2%} |
| Correctly flagged churners | {t['tp']} |
| False alarms | {t['fp']} |
| Missed churners | {t['fn']} |
| Correctly unflagged | {t['tn']} |
| Precision in top 10% ({t['top10_k']} records) | {t['top10_precision']:.2%} |
| Recall in top 10% | {t['top10_recall']:.2%} |
| Lift in top 10% over test prevalence | {t['top10_lift']:.2f}x |

At this recall-focused operating point, {t['flagged']} customers are flagged: {t['tp']} actual churners and {t['fp']} non-churners. These results measure historical classification, not retention impact. Top-budget ranking uses a stable tie-break on dataset order; tied scores near a cutoff can affect exact counts. Average precision is reported using scikit-learn's average_precision_score; it is not trapezoidal PR-AUC.

## Limitations and next steps
The dataset is small, historical, and drawn from one company. The test result is one grouped split, not a population guarantee. Repeated profiles reduce effective independent sample size. No confidence intervals, prospective validation, external validation, probability calibration, or comprehensive fairness audit are provided. Models output uncalibrated scores. No financial savings, reduced churn, or causal effects have been measured. Permutation importance is global predictive association, not an individual explanation.

Before production: confirm field definitions and unique customer IDs, audit timestamp availability, validate on future data, assess calibration and fairness, define the cost of errors, monitor drift, secure access, and test outreach effectiveness with an appropriate experiment. After using test results to redesign the model, obtain a fresh final evaluation set.

## Reproduction
Run `python src/train.py`, then `python -m unittest discover -s tests -p "check_data.py"` and `node tests/check_engine.cjs`. The pipeline recreates the SQLite database, SQL results, model, browser data bundle, and this report. Reload the dashboard after regeneration.

Source SHA-256: `{m['dataset_sha256']}`.

Runtime versions: {json.dumps(m['versions'],sort_keys=True)}.
'''
    (ROOT/'reports/MODEL-REPORT.md').write_text(text,encoding='utf-8')
    (ROOT/'dist/model-report.md').write_text(text,encoding='utf-8')

if __name__=='__main__':build_report()
