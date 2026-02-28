import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_FILE = ROOT / "data-analysis-agent" / "assets" / "sample_growth_data.csv"
DEFAULT_REPORT_DIR = ROOT / "data-analysis-agent" / "reports"


BUSINESS_REPORT_TEXT = """样例数据业务分析汇报

数据文件：{data_file}

一、管理层摘要

本次对 2026 年 1 月样例增长数据进行检查后，结论如下：

1. 数据可用于演示分析流程，但当前不适合直接作为正式经营报表依据。
2. 在现有样本中，paid 渠道转化效率最高，是最值得优先优化与扩量的渠道。
3. 整体收入呈上升趋势，月末相较月初明显改善。
4. referral 渠道存在单点极端异常收入，若不清洗会严重误导业务判断。

二、核心业务发现

1. 渠道转化效率

按 sessions -> signups -> orders 口径看：
- paid 渠道转化效率最高
- referral 渠道处于中间水平
- organic 渠道整体偏弱

这意味着如果当前目标是短期提升订单量，优先关注 paid 的投放效率和成本控制会更直接；如果目标是改善自然流量质量，则需要重点排查 organic 的流量来源与落地页表现。

2. 收入趋势

从周度汇总看：
- 首周收入：1210
- 末周收入：1657
- 增长幅度：+36.94%

这说明在剔除明显异常点影响后，收入总体呈上行趋势，业务表现有改善迹象。

3. 收入驱动关系

回归结果显示：
- sessions 与 orders 呈显著正相关
- orders 与 revenue_usd 呈显著正相关
- sessions 与 signups 也存在稳定正相关关系

业务上可以理解为：
- 流量提升会带动订单提升
- 订单提升会直接带动收入增长
- 因此增长工作的关键仍然是提升有效流量与转化质量，而不是只看表面曝光量

三、风险提示

1. 数据质量风险

当前数据中发现以下问题：
- 1 条完全重复记录
- 2 个缺失字段
- 1 条负数 sessions
- 1 条极端异常收入记录

这些问题会直接影响渠道收入、ROI、趋势判断和回归结果稳定性。

2. 异常值风险

最关键异常为：
2026-01-20 / referral / APAC / U1065 / revenue_usd = 9900

该条记录使 referral 渠道总收入被明显放大。若不剔除，业务层很容易错误判断该渠道为高价值来源。

四、建议动作

短期建议
1. 先建立数据清洗口径后再出正式报表。
2. 对 referral 渠道异常记录做来源回查。
3. 继续观察并优化 paid 渠道效率，补充成本完整性后评估 ROI。
4. 对 organic 渠道做专项排查，重点看流量质量、用户意图和转化链路。

中期建议
1. 建立数据质量校验规则：缺失、重复、负值、异常值自动告警。
2. 固化周报口径，统一趋势分析口径与异常处理规则。
3. 将回归分析纳入月度复盘，用于识别对订单和收入最敏感的指标。

五、结论

如果按可直接支持业务决策的标准看，这份样例数据目前最大的工作不是继续深挖，而是先完成数据清洗。

在完成清洗后，当前最明确的方向是：
- 以 paid 为主要增长抓手
- 对 organic 做转化优化
- 对 referral 先完成异常核查，再决定是否扩量
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate demo data analysis reports.")
    parser.add_argument(
        "--input",
        dest="input_file",
        default=str(DEFAULT_DATA_FILE),
        help="Path to input CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory to write generated reports into.",
    )
    return parser.parse_args()


def load_clean_data(data_file: Path) -> pd.DataFrame:
    df = pd.read_csv(data_file, keep_default_na=False)
    for col in ["sessions", "signups", "orders", "revenue_usd", "cost_usd"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    clean = df.drop_duplicates().copy()
    clean = clean.dropna(subset=["sessions", "signups", "orders", "revenue_usd"])
    clean = clean[clean["sessions"] >= 0].copy()
    clean = clean[~((clean["date"] == "2026-01-20") & (clean["user_id"] == "U1065"))].copy()
    return clean


def build_regression_report(clean: pd.DataFrame, data_file: Path) -> str:
    m1 = smf.ols("orders ~ sessions + C(channel) + C(region)", data=clean).fit()
    m2 = smf.ols("revenue_usd ~ orders + C(channel) + C(region)", data=clean).fit()
    m3 = smf.ols("signups ~ sessions + C(channel) + C(region)", data=clean).fit()

    return f"""# Regression Report

Data file: `{data_file}`

## Data handling
- Removed 1 exact duplicate row.
- Dropped rows missing core regression fields: `sessions`, `signups`, `orders`, `revenue_usd`.
- Dropped 1 row with negative `sessions`.
- Dropped 1 extreme revenue outlier: `2026-01-20 / U1065 / revenue_usd=9900`.
- Read CSV with `keep_default_na=False` so region value `NA` is not misread as null.
- Final regression sample size: {len(clean)} rows.

## Model 1
Formula: `orders ~ sessions + C(channel) + C(region)`

- R^2: {m1.rsquared:.4f}
- Adjusted R^2: {m1.rsquared_adj:.4f}
- Sessions coefficient: {m1.params["sessions"]:.4f} (p={m1.pvalues["sessions"]:.4g})

Interpretation:
- Orders rise strongly with sessions.
- Channel and region still explain part of the remaining variation after controlling for sessions.

## Model 2
Formula: `revenue_usd ~ orders + C(channel) + C(region)`

- R^2: {m2.rsquared:.4f}
- Adjusted R^2: {m2.rsquared_adj:.4f}
- Orders coefficient: {m2.params["orders"]:.4f} (p={m2.pvalues["orders"]:.4g})

Interpretation:
- Revenue is primarily explained by order volume.
- After cleaning the outlier, `paid` remains stronger than the baseline channel.

## Model 3
Formula: `signups ~ sessions + C(channel) + C(region)`

- R^2: {m3.rsquared:.4f}
- Adjusted R^2: {m3.rsquared_adj:.4f}
- Sessions coefficient: {m3.params["sessions"]:.4f} (p={m3.pvalues["sessions"]:.4g})

Interpretation:
- Sessions also explain signups well, though slightly less strongly than orders or revenue.

## Output files
- `reg_orders_vs_sessions.png`
- `reg_revenue_vs_orders.png`
- `reg_signups_vs_sessions.png`
"""


def write_business_reports(report_dir: Path, data_file: Path) -> None:
    business_report_text = BUSINESS_REPORT_TEXT.format(data_file=data_file.as_posix())
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>样例数据业务分析汇报</title>
<style>
:root {{ --bg:#f6f1e8; --card:#fffdf8; --ink:#1f2328; --muted:#5b6470; --line:#d8cdbd; --accent:#9a3412; }}
body {{ margin:0; font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif; background:linear-gradient(180deg,#efe4d2 0%, #f8f4ec 100%); color:var(--ink); }}
main {{ max-width:900px; margin:40px auto; background:var(--card); border:1px solid var(--line); border-radius:18px; padding:40px; box-shadow:0 12px 40px rgba(0,0,0,.08); }}
h1 {{ font-size:34px; margin-top:0; }} p {{ line-height:1.75; font-size:16px; white-space:pre-wrap; }}
code {{ background:#f2eadf; padding:2px 6px; border-radius:6px; }} .muted {{ color:var(--muted); }}
</style>
</head>
<body>
<main>
<h1>样例数据业务分析汇报</h1>
<p class="muted">数据文件：<code>{data_file.as_posix()}</code></p>
<p>{business_report_text}</p>
</main>
</body>
</html>"""
    report_dir.joinpath("business-report-zh.txt").write_text(business_report_text, encoding="utf-8-sig")
    report_dir.joinpath("business-report-zh.html").write_text(html, encoding="utf-8")
    report_dir.joinpath("business-report-zh.md").write_text(
        "# 样例数据业务分析汇报\n\n" + business_report_text,
        encoding="utf-8-sig",
    )


def plot_regression(
    clean: pd.DataFrame,
    report_dir: Path,
    x: str,
    y: str,
    title: str,
    filename: str,
    color: str,
) -> None:
    plt.figure(figsize=(7, 5))
    sns.regplot(
        data=clean,
        x=x,
        y=y,
        scatter_kws={"alpha": 0.75, "s": 45},
        line_kws={"color": color, "lw": 2},
    )
    plt.title(title)
    plt.xlabel(x.replace("_", " ").title())
    plt.ylabel(y.replace("_", " ").title())
    plt.tight_layout()
    plt.savefig(report_dir / filename, dpi=160)
    plt.close()


def write_showcase_page(report_dir: Path, data_file: Path, raw_rows: int, clean_rows: int) -> None:
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>数据分析 Agent 报告展示页</title>
  <style>
    :root {{
      --bg: #f4efe6;
      --card: #fffaf2;
      --ink: #1e2329;
      --muted: #5f6b76;
      --line: #d8c9b7;
      --accent: #a4491d;
      --accent-2: #155e75;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Microsoft YaHei", Georgia, serif;
      background:
        radial-gradient(circle at top left, #efe3cf 0, transparent 28%),
        radial-gradient(circle at bottom right, #e7d9c1 0, transparent 24%),
        linear-gradient(180deg, #f0e7da 0%, var(--bg) 100%);
    }}
    .wrap {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 40px 20px 80px;
    }}
    .hero {{
      padding: 28px;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: linear-gradient(135deg, #fffaf2 0%, #f7f0e4 100%);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
    }}
    .eyebrow {{
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--accent);
      font-size: 12px;
      margin: 0 0 10px;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(36px, 6vw, 68px);
      line-height: 0.95;
    }}
    .sub {{
      max-width: 760px;
      margin: 16px 0 0;
      color: var(--muted);
      font-size: 18px;
      line-height: 1.6;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 18px;
      margin-top: 24px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
    }}
    .metric {{
      font-size: 34px;
      color: var(--accent-2);
      margin: 0;
    }}
    .label {{
      margin-top: 6px;
      color: var(--muted);
    }}
    .section {{
      margin-top: 28px;
      padding: 22px;
      border-radius: 20px;
      background: rgba(255, 250, 242, 0.82);
      border: 1px solid var(--line);
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 24px;
    }}
    .links a {{
      display: inline-block;
      margin: 6px 12px 6px 0;
      color: var(--accent-2);
      text-decoration: none;
      border-bottom: 1px solid transparent;
    }}
    .links a:hover {{ border-color: var(--accent-2); }}
    .charts {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }}
    .charts img {{
      width: 100%;
      display: block;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: white;
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
      line-height: 1.7;
    }}
    code {{
      background: #efe5d6;
      padding: 2px 6px;
      border-radius: 6px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <p class="eyebrow">Data Analysis Agent</p>
      <h1>报告展示页</h1>
      <p class="sub">
        这个页面聚合了样例数据的关键输出，包括数据质量检查、回归分析图、业务汇报以及可复用的生成入口。
      </p>
      <div class="grid">
        <div class="card">
          <p class="metric">{raw_rows}</p>
          <div class="label">原始数据行数</div>
        </div>
        <div class="card">
          <p class="metric">{clean_rows}</p>
          <div class="label">清洗后回归样本数</div>
        </div>
        <div class="card">
          <p class="metric">36.94%</p>
          <div class="label">末周收入相较首周提升</div>
        </div>
        <div class="card">
          <p class="metric">1</p>
          <div class="label">识别出的极端异常收入点</div>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>业务摘要</h2>
      <ul>
        <li>`paid` 渠道转化效率最高，是当前最直接的增长抓手。</li>
        <li>`organic` 偏弱，更适合做流量质量和落地页转化排查。</li>
        <li>`referral` 收入被单条异常值放大，必须先清洗再做渠道判断。</li>
      </ul>
    </section>

    <section class="section">
      <h2>报告入口</h2>
      <div class="links">
        <a href="./regression-report.md">回归报告</a>
        <a href="./business-report-zh.html">中文业务汇报</a>
        <a href="./business-report-zh.txt">中文业务汇报 TXT</a>
      </div>
      <p>当前数据文件：<code>{data_file.as_posix()}</code></p>
    </section>

    <section class="section">
      <h2>回归图表</h2>
      <div class="charts">
        <figure>
          <img src="./reg_orders_vs_sessions.png" alt="Orders vs Sessions chart">
        </figure>
        <figure>
          <img src="./reg_revenue_vs_orders.png" alt="Revenue vs Orders chart">
        </figure>
        <figure>
          <img src="./reg_signups_vs_sessions.png" alt="Signups vs Sessions chart">
        </figure>
      </div>
    </section>

    <section class="section">
      <h2>一键重建</h2>
      <ul>
        <li>默认运行：<code>python data-analysis-agent/scripts/generate_reports.py</code></li>
        <li>自定义输入：<code>python data-analysis-agent/scripts/generate_reports.py --input your.csv</code></li>
        <li>自定义输出：<code>python data-analysis-agent/scripts/generate_reports.py --output-dir custom-reports</code></li>
      </ul>
    </section>
  </div>
</body>
</html>"""
    report_dir.joinpath("index.html").write_text(html, encoding="utf-8")


def main() -> None:
    args = parse_args()
    data_file = Path(args.input_file).resolve()
    report_dir = Path(args.output_dir).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    raw = pd.read_csv(data_file, keep_default_na=False)
    clean = load_clean_data(data_file)
    (report_dir / "regression-report.md").write_text(build_regression_report(clean, data_file), encoding="utf-8")
    write_business_reports(report_dir, data_file)
    write_showcase_page(report_dir, data_file, len(raw), len(clean))

    plot_regression(clean, report_dir, "sessions", "orders", "Orders vs Sessions", "reg_orders_vs_sessions.png", "#d9480f")
    plot_regression(clean, report_dir, "orders", "revenue_usd", "Revenue vs Orders", "reg_revenue_vs_orders.png", "#0b7285")
    plot_regression(clean, report_dir, "sessions", "signups", "Signups vs Sessions", "reg_signups_vs_sessions.png", "#2b8a3e")

    print(f"Wrote reports to: {report_dir}")


if __name__ == "__main__":
    main()
