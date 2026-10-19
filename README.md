# Customer Segmentation & Churn Analytics: European Banking

Analysis of 10,000 bank customers (France, Spain, Germany) to find who churns, where, and how much balance the bank loses.

**Live dashboard:** https://churn-analytics-european-banking-t434x33uas4kx3x4xueorz.streamlit.app/

## Key findings
- Overall churn rate: **20.37%** (2,037 of 10,000 customers)
- Germany churns at **32.4%** vs 16.2% in France and 16.7% in Spain
- Customers aged 46-60 churn at **51.1%**
- Inactive members churn at 26.9% vs 14.3% for active members
- Churned customers held **EUR 185.6M**, 24.3% of all balances
- Credit score, tenure and salary have almost no effect on churn

## What is in this repository
| File | Purpose |
|---|---|
| `eda.ipynb` | Data validation, cleaning, segmentation, churn analysis, KPIs |
| `app.py` | Streamlit dashboard with filters, dynamic KPIs and drill-downs |
| `data/` | Original and cleaned datasets |
| `charts/` | Charts used in the report |
| `report/` | Research paper and executive summary |

## Tools
Python, Pandas, NumPy, Plotly, Matplotlib, Seaborn, Streamlit

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
