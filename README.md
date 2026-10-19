# Churn Project - How to run

Folder layout (keep exactly like this):
```
churn project/
├── eda.ipynb              <- notebook (Day 1-3). Put European_Bank.csv in the SAME folder to run it.
├── app.py                 <- Streamlit dashboard
├── requirements.txt
├── data/
│   ├── European_Bank.csv  <- original data
│   └── cleaned_data.csv   <- made by the notebook
├── charts/                <- PNG charts used in the report
└── report/
    ├── Research_Paper.docx
    └── Executive_Summary.docx
```

## 1. Notebook
Copy `data/European_Bank.csv` next to `eda.ipynb`, open it in Jupyter, Kernel -> Restart & Run All.
If a library is missing, run in a cell:  `%pip install pandas numpy plotly`

## 2. Dashboard
Open Command Prompt in the project folder and run:
```
pip install -r requirements.txt
streamlit run app.py
```
Browser opens at http://localhost:8501

## 3. Deploy (free, optional)
Upload the folder to GitHub -> share.streamlit.io -> New app -> pick repo -> main file `app.py`.
