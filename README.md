# Data Analysis Agent

This repository contains a reusable `data-analysis-agent` skill plus sample data, generated reports, and a script to rebuild those reports.

## Structure

- `AGENTS.md`: Project-level skill registration.
- `data-analysis-agent/`: Main skill folder.
- `data-analysis-agent/assets/sample_growth_data.csv`: Sample dataset for testing.
- `data-analysis-agent/reports/`: Generated regression charts and business reports.
- `data-analysis-agent/scripts/generate_reports.py`: One-command report generator.
- `general-agent/`: Generic fallback agent template.

## Included Outputs

- Regression report: `data-analysis-agent/reports/regression-report.md`
- Chinese business report:
  - `data-analysis-agent/reports/business-report-zh.html`
  - `data-analysis-agent/reports/business-report-zh.txt`
- Regression charts:
  - `reg_orders_vs_sessions.png`
  - `reg_revenue_vs_orders.png`
  - `reg_signups_vs_sessions.png`

## Quick Start

Run the report generator from the repository root:

```powershell
python data-analysis-agent/scripts/generate_reports.py
```

By default it reads:

```text
data-analysis-agent/assets/sample_growth_data.csv
```

and writes outputs into:

```text
data-analysis-agent/reports/
```

## Use The Agent

Inside a Codex/Cursor chat in this project, call it by name:

```text
use data-analysis-agent to analyze d:/project/cursor/data-analysis-agent/assets/sample_growth_data.csv
```

or:

```text
$data-analysis-agent analyze the sample CSV and produce a data quality report, channel conversion summary, revenue trend review, and recommendations.
```

## Notes

- The sample dataset intentionally includes missing values, a duplicate row, a negative value, and an extreme outlier.
- The report generator reads CSV with `keep_default_na=False` so region value `NA` is preserved as a literal region label.
