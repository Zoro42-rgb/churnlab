"""Rebuild ChurnLab: public data -> grouped splits -> validation -> one test report.

Run from the project root: python src/train.py
No network or paid service is required when the included raw CSV is present.
"""
from pathlib import Path
import hashlib
import json
import sqlite3
import sys

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix, fbeta_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['call_failure', 'complains', 'subscription_length', 'charge_amount',
            'seconds_of_use', 'frequency_of_use', 'frequency_of_sms',
            'distinct_called_numbers', 'tariff_plan']
LABELS = ['Call failures', 'Any complaint (0/1)', 'Subscription months', 'Charge band',
          'Call duration (seconds)', 'Number of calls', 'Number of SMS',
          'Distinct called numbers', 'Tariff (1=pay-as-you-go, 2=contract)']
SOURCE = 'https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset'


def metrics(y, p, threshold):
    pred = p >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    k = max(1, int(np.ceil(len(y) * .1)))
    order = np.argsort(-p, kind='stable')[:k]
    top = np.asarray(y)[order]
    base = float(np.mean(y))
    return dict(n=len(y), prevalence=base, average_precision=float(average_precision_score(y, p)),
                roc_auc=float(roc_auc_score(y, p)), precision=float(precision_score(y, pred, zero_division=0)),
                recall=float(recall_score(y, pred, zero_division=0)),
                f2=float(fbeta_score(y, pred, beta=2, zero_division=0)),
                threshold=float(threshold), tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp),
                flagged=int(pred.sum()), top10_k=k, top10_precision=float(top.mean()),
                top10_recall=float(top.sum() / np.sum(y)), top10_lift=float(top.mean()/base))


def export_model(pipe):
    estimator = pipe.steps[-1][1]
    if isinstance(estimator, LogisticRegression):
        scaler = pipe.steps[-2][1]
        return dict(kind='logistic', features=FEATURES, mean=scaler.mean_.tolist(),
                    scale=scaler.scale_.tolist(), coefficients=estimator.coef_[0].tolist(),
                    intercept=float(estimator.intercept_[0]))
    trees = []
    for tree in estimator.estimators_:
        t = tree.tree_
        counts = t.value[:, 0, :]
        probs = counts[:, 1] / counts.sum(axis=1)
        trees.append(dict(left=t.children_left.tolist(), right=t.children_right.tolist(),
                          feature=t.feature.tolist(), threshold=t.threshold.tolist(), p=probs.tolist()))
    return dict(kind='forest', features=FEATURES, trees=trees)


def main():
    for name in ['reports', 'artifacts', 'data/processed', 'dist']:
        (ROOT/name).mkdir(parents=True, exist_ok=True)
    raw_path = ROOT/'data/raw/customer_churn.csv'
    df = pd.read_csv(raw_path)
    df.columns = ['_'.join(c.strip().lower().split()) for c in df.columns]
    assert len(df) == 3150, 'Unexpected source dataset: inspect before training.'
    assert set(FEATURES+['churn']).issubset(df.columns)
    assert df.isna().sum().sum() == 0
    assert set(df.churn.unique()) == {0, 1}
    assert (df[FEATURES] >= 0).all().all()
    assert set(df.complains.unique()) <= {0, 1}
    assert set(df.tariff_plan.unique()) <= {1, 2}
    # Keep repeated records: no stable customer ID proves that they are errors.
    # Group identical MODEL INPUTS across all splits, ignoring label and excluded fields.
    groups = pd.util.hash_pandas_object(df[FEATURES], index=False).astype(str)
    X, y = df[FEATURES], df.churn
    outer = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    dev_idx, test_idx = next(outer.split(X, y, groups))
    inner = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=17)
    tr, va = next(inner.split(X.iloc[dev_idx], y.iloc[dev_idx], groups.iloc[dev_idx]))
    train_idx, val_idx = dev_idx[tr], dev_idx[va]
    partitions = {'train':train_idx, 'validation':val_idx, 'test':test_idx}
    for a, b in [('train','validation'), ('train','test'), ('validation','test')]:
        assert set(groups.iloc[partitions[a]]).isdisjoint(set(groups.iloc[partitions[b]]))
    Xtr, ytr = X.iloc[train_idx], y.iloc[train_idx]
    Xva, yva = X.iloc[val_idx], y.iloc[val_idx]
    candidates = {
        'Dummy baseline': make_pipeline(DummyClassifier(strategy='prior')),
        'Logistic regression': make_pipeline(FunctionTransformer(np.log1p, feature_names_out='one-to-one'),
                                            StandardScaler(), LogisticRegression(max_iter=2000, random_state=42)),
        'Random forest': make_pipeline(RandomForestClassifier(n_estimators=120, max_depth=8,
                                         min_samples_leaf=4, random_state=42, n_jobs=-1))}
    comparisons = []
    for name, model in candidates.items():
        model.fit(Xtr, ytr)
        p = model.predict_proba(Xva)[:,1]
        comparisons.append(dict(name=name, **metrics(yva, p, .5)))
    # Pick algorithm by validation average precision, excluding the dummy benchmark.
    winner = max(comparisons[1:], key=lambda row:row['average_precision'])['name']
    selected = candidates[winner]
    pv = selected.predict_proba(Xva)[:,1]
    # F2 weights recall more than precision. Preset grid; no test-based tuning.
    thresholds = np.arange(.05, .951, .01)
    threshold = float(max(thresholds, key=lambda t:fbeta_score(yva, pv>=t, beta=2, zero_division=0)))
    pt = selected.predict_proba(X.iloc[test_idx])[:,1]
    final = metrics(y.iloc[test_idx], pt, threshold)
    validation = metrics(yva, pv, threshold)
    importance = permutation_importance(selected, Xva, yva, scoring='average_precision',
                                        n_repeats=5, random_state=42, n_jobs=1)
    signal_rows = sorted([dict(feature=f, label=l, importance=float(v), std=float(s))
                  for f,l,v,s in zip(FEATURES,LABELS,importance.importances_mean,importance.importances_std)],
                  key=lambda row:row['importance'], reverse=True)
    frame = df.copy()
    frame.insert(0, 'record_id', [f'R{i+1:04d}' for i in range(len(df))])
    frame['split'] = ''
    for split, indices in partitions.items(): frame.loc[indices,'split'] = split
    frame['feature_group'] = groups
    frame.to_csv(ROOT/'data/processed/customers.csv', index=False)
    with sqlite3.connect(ROOT/'data/processed/churnlab.sqlite') as conn:
        frame.to_sql('customers',conn,index=False,if_exists='replace')
        score_frames=[]
        for split,idx,p in [('validation',val_idx,pv),('test',test_idx,pt)]:
            score_frames.append(pd.DataFrame(dict(record_id=frame.iloc[idx].record_id.to_list(),
                                  risk_score=p, model=winner, threshold=threshold)))
        pd.concat(score_frames).to_sql('model_scores',conn,index=False,if_exists='replace')
        sql_path=ROOT/'sql/analysis.sql'
        if sql_path.exists():
            query_results=[]
            sql_text = '\n'.join(line for line in sql_path.read_text(encoding='utf-8').splitlines()
                                 if not line.lstrip().startswith('--'))
            for statement in sql_text.split(';'):
                if statement.strip():
                    rows=pd.read_sql_query(statement,conn)
                    query_results.append(dict(query=statement.strip(), rows=rows.to_dict(orient='records')))
            (ROOT/'reports/sql_results.json').write_text(json.dumps(query_results,indent=2),encoding='utf-8')
    pd.DataFrame(comparisons).to_csv(ROOT/'reports/model_comparison.csv', index=False, lineterminator='\n')
    payload = dict(source=SOURCE, source_doi='10.24432/C5JW3Z', rows=len(df), churners=int(y.sum()),
        dataset_sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        raw_duplicate_rows=int(df.duplicated().sum()), repeated_feature_rows=int(groups.duplicated().sum()),
        missing_cells=int(df.isna().sum().sum()), selected_model=winner, threshold=threshold,
        splits={k:dict(n=len(v),churners=int(y.iloc[v].sum()),groups=int(groups.iloc[v].nunique())) for k,v in partitions.items()},
        comparison=comparisons, validation=validation, test=final, importance=signal_rows,
        model=export_model(selected), labels=LABELS,
        bounds={f:dict(min=float(Xtr[f].min()), max=float(Xtr[f].max()), median=float(Xtr[f].median())) for f in FEATURES},
        validation_rows=[dict(id=frame.iloc[int(i)].record_id, y=int(y.iloc[i]), score=float(p),
                             tariff=int(df.iloc[i].tariff_plan), complains=int(df.iloc[i].complains),
                             values=X.iloc[i].astype(float).tolist()) for i,p in zip(val_idx,pv)],
        examples=[dict(id=frame.iloc[int(i)].record_id,values=X.iloc[i].astype(float).tolist(), expected=float(p))
                  for i,p in list(zip(test_idx,pt))[:30]],
        versions=dict(python=sys.version.split()[0],pandas=pd.__version__,numpy=np.__version__,sklearn=sklearn.__version__))
    (ROOT/'dist/data.js').write_text('window.CHURNLAB = '+json.dumps(payload,separators=(',',':'))+';\n',encoding='utf-8')
    report={k:v for k,v in payload.items() if k not in ['model','validation_rows','examples']}
    (ROOT/'reports/metrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    joblib.dump(selected,ROOT/'artifacts/model.joblib')
    (ROOT/'reports/splits.json').write_text(json.dumps({k:v.tolist() for k,v in partitions.items()}),encoding='utf-8')
    from report import build_report
    build_report()
    print(json.dumps(dict(selected_model=winner,threshold=threshold,test=final,splits=payload['splits'],
                         duplicate_rows=payload['raw_duplicate_rows'],versions=payload['versions']),indent=2))


if __name__ == '__main__':
    main()
