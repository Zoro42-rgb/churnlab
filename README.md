# ChurnLab — Customer Churn Analytics and Interactive Scoring

A complete, assisted portfolio starting point: public data, reproducible Python, runnable SQL, measured model evaluation, and an offline-capable D3 dashboard.

**Start with [START-HERE.md](START-HERE.md).** To use the app immediately, open `dist/index.html` in a browser. No model API, server, paid account, or Python installation is needed for the prebuilt demonstration. Keep its adjacent files intact.

## Business question

Which customers should a telecom retention team prioritize for investigation when its capacity is limited? The model estimates churn risk from a nine-month observation window; source labels describe churn status three months later. A high score does not imply that contacting the customer will prevent churn.

## What works

- **Decision lab:** adjust a validation threshold and see precision, recall, workload, missed churners, and a confusion matrix update.
- **D3 chart:** compare precision and recall across thresholds, with the current operating point marked.
- **Priority list:** filter validation profiles by tariff and export currently flagged rows to CSV.
- **Customer scoring:** enter nine validated numeric inputs and run the trained model instantly in the browser.
- **Evidence:** inspect model comparison, split counts, global permutation importance, and a fixed test report.
- **Python pipeline:** checks data, groups repeated inputs, trains three candidates, selects using validation data, and produces the report and app data.
- **SQLite analysis:** eight business and integrity queries, with their executed results saved.

This is instant inference over a static model and historical dataset, not a streaming platform. Production authentication, customer messaging, live ingestion, retraining schedules, monitoring, and intervention experiments are not implemented. The hosted demo starts private and is not automatically a recruiter-accessible link.

## Architecture

```text
Public UCI CSV
  -> normalize names + validate schema and values
  -> group identical included-feature profiles
  -> train / validation / test partitions
  -> dummy + logistic regression + random forest
  -> select by validation average precision
  -> select threshold by validation F2
  -> one fixed test evaluation
  -> SQLite reports + model artifact + browser model export
  -> D3 dashboard and instant browser scoring
```

See [DATA-DICTIONARY.md](DATA-DICTIONARY.md) for definitions and exclusions and [reports/MODEL-REPORT.md](reports/MODEL-REPORT.md) for the full methodology and measured results.

## Measured starting results

The selected random forest achieved **0.899 test average precision**, **96.9% recall**, and **54.6% precision** at threshold **0.14**, on **629 held-out records**. It caught 95 of 98 churners and produced 79 false alarms. These values describe the bundled run, not an expected result on a new company's customers.

There are 3,150 source rows. The pipeline retains 300 repeated full rows and prevents identical model-input profiles from appearing in different splits. Generated source-row IDs do not establish customer identity. Temporal generalization cannot be tested with the available dates.

## Setup and reproduce

Tested on Python 3.12. From this directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/train.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "check_data.py"
node tests/check_engine.cjs
```

The Node command checks parity between exported browser predictions and scikit-learn predictions. Node is optional for using the app or training; it is needed for this check.

To serve locally rather than opening the HTML directly:

```powershell
.\.venv\Scripts\python.exe -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open `http://127.0.0.1:8000` and stop the server with Ctrl+C. The raw CSV is already included; no network is needed after Python dependencies are installed.

## Run SQL directly with Python

```python
import sqlite3
import pandas as pd

with sqlite3.connect('data/processed/churnlab.sqlite') as connection:
    result = pd.read_sql_query('''
        SELECT tariff_plan, COUNT(*) AS customers,
               SUM(churn) AS churners,
               ROUND(100.0 * AVG(churn), 2) AS churn_rate_pct
        FROM customers
        GROUP BY tariff_plan
    ''', connection)
print(result)
```

`notebooks/01_explore_and_query.ipynb` provides a guided starting notebook. It uses pandas and Python's built-in SQLite module; open it in Jupyter or VS Code with a Python kernel from your environment.

## Files

```text
data/raw/                 Original UCI CSV
data/processed/           Normalized rows, split memberships, generated SQLite DB
src/train.py              Reproducible fitting and evaluation pipeline
src/report.py             Measured report generation
sql/analysis.sql          Eight executable queries
reports/                  Metrics, SQL output, split indices, model report
artifacts/model.joblib    Locally generated scikit-learn model (not needed by app)
dist/                     Complete self-contained browser application
notebooks/                Guided analysis and SQL exercises
tests/                    Evaluation integrity and Python/browser parity checks
LEARNING-PLAN.md           Ten-week build, understand, and interview plan
```

## Portfolio handoff

The code was built with AI assistance. Before presenting it as your project, reproduce it, understand the choices, and make documented contributions. The learning plan suggests concrete extensions. Do not claim the assisted implementation was independently written, or claim real customer impact.

## Attribution

[Iranian Churn (2020), UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset), DOI [10.24432/C5JW3Z](https://doi.org/10.24432/C5JW3Z), **CC BY 4.0**. Changes: column normalization, generated record references and splits, feature selection, model fitting, aggregated analysis, and visualizations. UCI describes charge bands as 0–9; the observed dataset contains 10, retained and documented for review.

D3 7.9.0 is redistributed under its ISC license; see `dist/vendor/D3-LICENSE`. The dashboard bundles it locally, so no third-party chart request is required at runtime.
