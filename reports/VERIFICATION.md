# Verification record

The delivered build passed these checks:

- Five Python integrity tests: complete record accounting, no included-input groups crossing splits, SQL/test confusion-matrix agreement, no training records in the held-out scores table, and excluded fields absent from model inputs.
- 665 browser-engine prediction comparisons against Python outputs (635 validation profiles and 30 test examples), with absolute tolerance 1e-10.
- Validation metric reconciliation and engine invalid-input checks.
- JavaScript syntax check and local asset/link resolution.
- Local app HTTP response: 200.
- Browser inspection at the available narrow viewport: readable responsive layout, populated cards and tables.
- Browser threshold action at 0.50: 59 flags, 52 true positives, 7 false positives, 50 false negatives, 526 true negatives.
- Browser profile scoring action returned a numeric score and updated the displayed result.
- Invalid threshold and negative profile input rejected without changing the decision state.
- Tariff filter updated the table to 51 contractual validation profiles; at threshold 0.14, one was flagged.
- Model evidence view displayed fixed test AP 0.899, recall 96.9%, and precision 54.6% after validation threshold changes.

Hosted deployment did not complete: the installed Sites publishing helper became unavailable during the session. The local static application is complete. A Site registration ID remains in the local hosting manifest for future continuation; no live remote URL is claimed.
