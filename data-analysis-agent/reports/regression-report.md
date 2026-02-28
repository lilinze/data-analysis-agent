# Regression Report

Data file: `D:\project\cursor\data-analysis-agent\assets\sample_growth_data.csv`

## Data handling
- Removed 1 exact duplicate row.
- Dropped rows missing core regression fields: `sessions`, `signups`, `orders`, `revenue_usd`.
- Dropped 1 row with negative `sessions`.
- Dropped 1 extreme revenue outlier: `2026-01-20 / U1065 / revenue_usd=9900`.
- Read CSV with `keep_default_na=False` so region value `NA` is not misread as null.
- Final regression sample size: 63 rows.

## Model 1
Formula: `orders ~ sessions + C(channel) + C(region)`

- R^2: 0.9454
- Adjusted R^2: 0.9406
- Sessions coefficient: 0.4961 (p=4.77e-23)

Interpretation:
- Orders rise strongly with sessions.
- Channel and region still explain part of the remaining variation after controlling for sessions.

## Model 2
Formula: `revenue_usd ~ orders + C(channel) + C(region)`

- R^2: 0.9819
- Adjusted R^2: 0.9804
- Orders coefficient: 80.9775 (p=1.002e-34)

Interpretation:
- Revenue is primarily explained by order volume.
- After cleaning the outlier, `paid` remains stronger than the baseline channel.

## Model 3
Formula: `signups ~ sessions + C(channel) + C(region)`

- R^2: 0.8963
- Adjusted R^2: 0.8872
- Sessions coefficient: 0.2369 (p=2.846e-12)

Interpretation:
- Sessions also explain signups well, though slightly less strongly than orders or revenue.

## Output files
- `reg_orders_vs_sessions.png`
- `reg_revenue_vs_orders.png`
- `reg_signups_vs_sessions.png`
