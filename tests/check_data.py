"""Checks relationships that protect the evaluation, not a target performance score."""
from pathlib import Path
import json
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parents[1]

class DataIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.conn=sqlite3.connect(ROOT/'data/processed/churnlab.sqlite')
        self.metrics=json.loads((ROOT/'reports/metrics.json').read_text())
    def tearDown(self):
        self.conn.close()
    def test_all_source_records_accounted_for(self):
        count=self.conn.execute('SELECT COUNT(*), COUNT(DISTINCT record_id) FROM customers').fetchone()
        self.assertEqual(count,(3150,3150))
        self.assertEqual(sum(v['n'] for v in self.metrics['splits'].values()),3150)
    def test_no_profile_overlap_between_splits(self):
        overlaps=self.conn.execute('SELECT feature_group FROM customers GROUP BY feature_group HAVING COUNT(DISTINCT split)>1').fetchall()
        self.assertEqual(overlaps,[])
    def test_sql_confusion_matrix_agrees(self):
        rows=json.loads((ROOT/'reports/sql_results.json').read_text())
        result=rows[6]['rows'][0]
        for sql_key,key in [('true_positives','tp'),('false_positives','fp'),('false_negatives','fn'),('true_negatives','tn')]:
            self.assertEqual(result[sql_key],self.metrics['test'][key])
    def test_only_held_out_records_scored(self):
        rows=self.conn.execute("SELECT COUNT(*) FROM model_scores s JOIN customers c USING(record_id) WHERE c.split='train'").fetchone()[0]
        self.assertEqual(rows,0)
    def test_excluded_features_not_used(self):
        features=set(self.metrics['bounds'])
        self.assertTrue(features.isdisjoint({'churn','age','age_group','status','customer_value','record_id','split'}))

if __name__=='__main__':unittest.main()
