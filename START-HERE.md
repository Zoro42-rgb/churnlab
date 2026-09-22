# ChurnLab: your working data science project

**Start with the app:** open `dist/index.html` in your browser. Keep the complete `dist` folder together. The included dashboard runs without installing Python, without internet access, and without an API key.

This project predicts customer churn from public telecom records. It combines data checks, SQL analysis, three model baselines, validation-based selection, a held-out test report, and an interactive D3 dashboard. Customer profiles can be scored instantly. There is no live telecom data feed.

## First 20 minutes

1. Open **Decision lab** and select **Reset to selected threshold**.
2. Read the four cards. The data is the validation set, not the final test set.
3. Move the threshold higher. Observe how the flagged list changes. Recall cannot increase as the threshold increases; precision does not have to change monotonically.
4. Open **Score a customer**. Choose the higher-scoring example, change one input, and calculate again. Treat this as a model sensitivity demonstration, not an intervention recommendation.
5. Open **Model evidence**. Read the fixed test results and the limitations.

## What you should say honestly

This is an assisted portfolio project using historical public data. Instant browser scoring is implemented. Production streaming, live integrations, A/B-tested retention impact, and actual revenue savings are not implemented. Do not describe the project as deployed at a real telecom company or claim business savings.

## Your first hands-on contribution

Open `sql/analysis.sql`. Run and understand the first three queries. Then add a query that calculates churn rate by subscription-length bands: under 12 months, 12–35 months, and 36+ months. State why you chose those bands, keep the denominators visible, and write two sentences about the results without claiming causation.

The goal is to make and explain a real change. You do not need to master all the code before making this first contribution.

## Rebuild the analysis on your computer

Tested with Python 3.12. Create an environment inside this folder, install the requirements, then run the pipeline:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/train.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "check_data.py"
```

To test that browser predictions match Python, install Node.js if needed and run:

```powershell
node tests/check_engine.cjs
```

If you prefer a local web address, start a server from this project folder:

```powershell
.\.venv\Scripts\python.exe -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Then visit `http://127.0.0.1:8000`. Press Ctrl+C in that terminal to stop it.

## Files to learn in order

1. `data/raw/customer_churn.csv`: original dataset, preserved unchanged.
2. `DATA-DICTIONARY.md`: definitions and input exclusions.
3. `sql/analysis.sql`: eight runnable business and quality queries.
4. `src/train.py`: preparation, grouping, model fitting, validation, and evaluation.
5. `reports/metrics.json` and `reports/model_comparison.csv`: measured outputs.
6. `dist/engine.js`: the exported model's scoring logic.
7. `LEARNING-PLAN.md`: your build-and-explain practice plan.

See `README.md` for the architecture, reproduction notes, and portfolio checklist.
