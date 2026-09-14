# Delivery Operations Intelligence

**A recruiter-ready Streamlit operations analytics product for diagnosing late delivery, cancellations and customer-experience leakage.**

> This is an independent analytical prototype built on the anonymized [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). It is not an internal analysis of Swiggy, Zomato, Blinkit, Zepto or any other delivery company.

## Executive brief

Delivery performance is not a single KPI. It is a chain of operational moments: a customer places an order, a seller prepares it, the carrier handles the parcel, the customer receives it and the experience is reflected in a review. This project turns that chain into a decision interface.

The application is designed to answer four management questions:

1. **Where is service risk concentrated?** The dashboard ranks markets, categories and sellers with volume guardrails so that small samples do not dominate the decision.
2. **What is the customer impact?** It connects delivery outcome to review health and surfaces categories that require an intervention queue.
3. **What should operations do next?** It provides a seller and market prioritization view rather than a generic chart gallery.
4. **Is an intervention directionally worthwhile?** The Decision Lab tests an explicit scenario with visible assumptions and does not present correlation as causation.

## Product capabilities

| Workspace | Decision supported | Core analytical techniques |
|---|---|---|
| Executive Overview | Monitor service health and exposure | KPI design, time series, market benchmarking |
| Delivery Performance | Diagnose promise variance | Date arithmetic, segmentation, long-tail analysis |
| Customer Experience | Link operations to satisfaction | Review segmentation, distribution analysis |
| Seller & Zone Operations | Prioritize intervention candidates | Volume guardrails, risk scoring, Pareto-style triage |
| Decision Lab | Stress-test an improvement scenario | Assumption-driven scenario modelling |

## Data model

The pipeline joins six public tables into an order-level analytical fact table:

| Source | Role |
|---|---|
| `olist_orders_dataset.csv` | Order lifecycle timestamps and status |
| `olist_order_items_dataset.csv` | Item, price, freight and seller detail |
| `olist_order_reviews_dataset.csv` | Customer review score |
| `olist_customers_dataset.csv` | Customer geography |
| `olist_sellers_dataset.csv` | Seller geography |
| `product_category_name_translation.csv` | English category labels |

The derived fact table adds `delivery_days`, `promised_days`, `late_days`, `is_late`, `is_cancelled`, `delivery_status`, purchase calendar fields, review health and a cross-state distance proxy. Because the public dataset does not contain rider-level telemetry, weather or restaurant preparation timestamps, the project does **not** claim those variables caused delay. It makes the data limitation explicit instead of fabricating precision.

## Getting started

```bash
git clone <your-repository-url>
cd delivery_operations_intelligence
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python download_data.py
python prepare_data.py
python validate_data.py
streamlit run app.py
```

Open the local URL printed by Streamlit. The public CSV files and generated SQLite/processed artifacts are intentionally excluded from GitHub because they are large. `download_data.py` retrieves the anonymized Olist source files locally, and `prepare_data.py` rebuilds the data mart reproducibly.

### Streamlit Community Cloud

Set the repository to `khushitamre/delivery-operations-intelligence`, choose `app.py` as the main file, and click **Deploy**. On the first run, the app automatically executes `download_data.py` and `prepare_data.py` because the large data artifacts are intentionally not committed to GitHub. A first deployment may take a few minutes while the public CSV files are downloaded and the SQLite data mart is built. Subsequent runs reuse the generated files while the app instance remains available.

### Why the data files are not committed

The raw source files and generated artifacts are approximately 176 MB combined, while GitHub rejects individual files above its 100 MB limit and discourages large repository uploads. The repository therefore contains the code, documentation and reproducible download/build scripts rather than duplicating the dataset. The source and attribution remain documented in this README.

### Publish or repair the GitHub repository

From the project root, run `bash publish_github.sh`. The script verifies required files, resets the remote to `https://github.com/khushitamre/delivery-operations-intelligence.git`, removes any accidentally staged large data artifacts, safely merges an existing remote `main` commit, and pushes the lightweight project. It deliberately does not force-push or overwrite remote history.

## Portfolio evidence

A strong interview walkthrough should follow this sequence: show the executive KPI strip; filter to a high-risk market; move to Delivery Performance to validate the issue; open Customer Experience to show why the issue matters; then use Seller & Zone Operations to select an intervention queue. Finish in Decision Lab and explain that the output is a scenario, not a causal forecast.

Suggested resume bullet:

> Built a Streamlit delivery-operations intelligence product using Python, Pandas, SQL and Plotly; joined 100K anonymized e-commerce orders to identify late-delivery concentration, customer-review risk and seller intervention priorities, with an assumption-led ROI simulator for operational pilots.

## Quality and governance choices

The data is anonymized. No customer names or direct identifiers are displayed in the UI. The analysis uses minimum-volume thresholds for seller and category comparisons. Missing timestamps are preserved as missing rather than imputed as successful deliveries. Scenario outputs are labelled as directional estimates. These choices are intentionally included because professional analytics requires knowing where the data can and cannot support a conclusion.

## Validation and handover assets

Run `python validate_data.py` after rebuilding the data mart. The validation script checks the order grain, required fields, row-count sanity, non-negative order value, review-score range and boolean-like operational flags. `DATA_DICTIONARY.md` documents every derived field and denominator policy. `METHODOLOGY.md` records the analytical workflow, interview narrative, future instrumentation requirements and governance choices.

## Repository structure

```text
delivery_operations_intelligence/
├── app.py                    # Streamlit application
├── publish_github.sh         # Safe one-command GitHub sync and push
├── download_data.py          # Downloads the public Olist source files locally
├── prepare_data.py           # Reproducible ETL and SQLite data mart build
├── sql_queries.sql           # Interview-ready SQL analysis pack
├── DATA_DICTIONARY.md        # Field definitions and denominator policy
├── METHODOLOGY.md            # Analytical workflow and interview guide
├── validate_data.py          # Reproducible data quality checks
├── requirements.txt
├── README.md
└── data/
    ├── raw/                  # Public Olist source files
    └── processed/            # Generated order_fact.csv
```

## References

[1]: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce "Brazilian E-Commerce Public Dataset by Olist"
[2]: https://github.com/olist/work-at-olist-data "Olist public dataset repository"
