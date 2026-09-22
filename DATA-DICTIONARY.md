# Data dictionary

Source: [UCI Iranian Churn](https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset), 2020, DOI [10.24432/C5JW3Z](https://doi.org/10.24432/C5JW3Z), CC BY 4.0. The raw download is preserved. Column names are normalized in the processed data.

UCI describes predictors aggregated over the first nine months and churn status at the end of month 12. One row represents a customer. Stable customer identifiers and exact observation dates are not present in the supplied CSV.

| Processed column | Definition | Model use |
|---|---|---|
| call_failure | Number of call failures | Included |
| complains | Whether a complaint occurred: 0=no, 1=yes. **Not a ticket count.** | Included |
| subscription_length | Subscription duration in months | Included |
| charge_amount | Ordinal charge band; source documentation describes 0–9 | Included; app uses observed training bounds |
| seconds_of_use | Total call duration in seconds | Included |
| frequency_of_use | Number of calls | Included |
| frequency_of_sms | Number of text messages | Included |
| distinct_called_numbers | Number of distinct called numbers | Included |
| tariff_plan | 1=pay-as-you-go, 2=contractual | Included |
| status | 1=active, 2=non-active | Excluded pending operational-definition verification; UCI describes all non-target fields as observation-window inputs |
| age | Age | Excluded from this demonstration model |
| age_group | Ordinal age category | Excluded from this demonstration model |
| customer_value | Derived customer-value field, formula not supplied here | Excluded pending derivation verification |
| churn | 1=churn, 0=no churn at end of month 12 | Target only |
| record_id | Project-generated source-row reference, e.g. R0001 | Never a feature or a real customer identifier |
| split | train, validation, or test | Never a feature |
| feature_group | Hash of all included model inputs | Splitting only; never a feature |

## Input treatment

No source values are missing. Raw full-row repetitions are preserved because there is no reliable ID that establishes whether they are erroneous duplicate records or different customers with identical attributes. All identical included-input profiles are assigned to the same split, even if their targets differ.

The logistic regression baseline applies `log1p` to non-negative inputs and fits its scaler using training rows only. The random forest uses the raw included inputs. Tariff is treated as its two numeric codes, a documented simplifying choice for the baselines. There is no imputation or oversampling. If future source data contains missing or invalid inputs, the pipeline stops for inspection instead of silently filling them.
