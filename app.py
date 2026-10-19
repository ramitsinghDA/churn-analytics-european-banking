# Streamlit dashboard - Customer Segmentation & Churn Analytics (European Banking)
# Run with:  streamlit run app.py
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Churn Analytics - European Banking", layout="wide")

AGE_ORDER = ["<30", "30-45", "46-60", "60+"]
CREDIT_ORDER = ["Low", "Medium", "High"]
TENURE_ORDER = ["New", "Mid-term", "Long-term"]
BAL_ORDER = ["Zero-balance", "Low-balance", "High-balance"]


@st.cache_data
def load_data():
    # Reads the cleaned file made in the notebook (Day 1). Falls back to the raw file.
    try:
        d = pd.read_csv("data/cleaned_data.csv")
    except FileNotFoundError:
        d = pd.read_csv("data/European_Bank.csv").drop(columns=["Year", "Surname", "CustomerId"], errors="ignore")
        d["AgeGroup"] = pd.cut(d.Age, [0, 29, 45, 60, 120], labels=AGE_ORDER)
        d["CreditBand"] = pd.cut(d.CreditScore, [0, 579, 669, 900], labels=CREDIT_ORDER)
        d["TenureGroup"] = pd.cut(d.Tenure, [-1, 2, 6, 10], labels=TENURE_ORDER)
        med = d.loc[d.Balance > 0, "Balance"].median()
        d["BalanceSegment"] = np.where(d.Balance == 0, "Zero-balance",
                                       np.where(d.Balance < med, "Low-balance", "High-balance"))
    return d


df = load_data()
OVERALL = df.Exited.mean() * 100  # churn of the FULL dataset, used as the benchmark

# ---------------- Sidebar filters ----------------
st.sidebar.header("Segment Filters")
geo = st.sidebar.multiselect("Geography", sorted(df.Geography.unique()), sorted(df.Geography.unique()))
gen = st.sidebar.multiselect("Gender", sorted(df.Gender.unique()), sorted(df.Gender.unique()))
age = st.sidebar.multiselect("Age Group", AGE_ORDER, AGE_ORDER)
cb = st.sidebar.multiselect("Credit Band", CREDIT_ORDER, CREDIT_ORDER)
tg = st.sidebar.multiselect("Tenure Group", TENURE_ORDER, TENURE_ORDER)
bs = st.sidebar.multiselect("Balance Segment", BAL_ORDER, BAL_ORDER)
act = st.sidebar.radio("Member status", ["All", "Active only", "Inactive only"])

f = df[df.Geography.isin(geo) & df.Gender.isin(gen) & df.AgeGroup.isin(age)
       & df.CreditBand.isin(cb) & df.TenureGroup.isin(tg) & df.BalanceSegment.isin(bs)]
if act == "Active only":
    f = f[f.IsActiveMember == 1]
elif act == "Inactive only":
    f = f[f.IsActiveMember == 0]

st.title("Customer Segmentation & Churn Analytics - European Banking")
st.caption("All numbers below update automatically when you change the filters on the left.")

if f.empty:
    st.warning("No customers match these filters. Please widen your selection.")
    st.stop()

# ---------------- Dynamic KPIs ----------------
churn = f.Exited.mean() * 100
lost = f.loc[f.Exited == 1, "Balance"].sum()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Customers", f"{len(f):,}")
c2.metric("Churn Rate", f"{churn:.1f}%", f"{churn - OVERALL:+.1f} pts vs overall", delta_color="inverse")
c3.metric("Churned Customers", f"{int(f.Exited.sum()):,}")
c4.metric("Balance at Risk", f"EUR {lost/1e6:,.1f}M")
a0 = f[f.IsActiveMember == 0].Exited.mean() * 100 if (f.IsActiveMember == 0).any() else np.nan
a1 = f[f.IsActiveMember == 1].Exited.mean() * 100 if (f.IsActiveMember == 1).any() else np.nan
c5.metric("Engagement Drop Indicator", f"{a0 / a1:.2f}x" if a0 == a0 and a1 == a1 and a1 > 0 else "n/a",
          help="Churn of inactive members divided by churn of active members")


def rate(data, col, order=None):
    g = data.groupby(col, observed=True).Exited.agg(Customers="count", Churned="sum", ChurnRate="mean").reset_index()
    g["ChurnRate"] *= 100
    if order:
        g[col] = pd.Categorical(g[col], order, ordered=True)
        g = g.sort_values(col)
    return g


tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Geography", "Age & Tenure", "High-Value Customers"])

# ---------------- Tab 1 ----------------
with tab1:
    l, r = st.columns(2)
    pie = px.pie(f, names=f.Exited.map({0: "Retained", 1: "Churned"}), hole=0.5,
                 color_discrete_sequence=["#1F3A5F", "#C0392B"], title="Retained vs Churned")
    l.plotly_chart(pie, width="stretch")
    dim = r.selectbox("Compare churn by:", ["Gender", "CreditBand", "BalanceSegment", "NumOfProducts", "IsActiveMember", "HasCrCard"])
    g = rate(f, dim)
    g[dim] = g[dim].astype(str)
    r.plotly_chart(px.bar(g, x=dim, y="ChurnRate", text_auto=".1f", title=f"Churn rate by {dim}",
                          color_discrete_sequence=["#1F3A5F"]), width="stretch")
    st.subheader("Churned vs Retained - average profile")
    prof = f.groupby("Exited")[["Age", "CreditScore", "Balance", "EstimatedSalary", "Tenure", "NumOfProducts"]].mean().round(1)
    prof.index = prof.index.map({0: "Retained", 1: "Churned"})
    st.dataframe(prof, width="stretch")

# ---------------- Tab 2 ----------------
with tab2:
    g = rate(f, "Geography")
    g["Geographic Risk Index"] = (g.ChurnRate / OVERALL).round(2)
    l, r = st.columns(2)
    l.plotly_chart(px.bar(g, x="Geography", y="ChurnRate", text_auto=".1f", title="Churn rate by country",
                          color="ChurnRate", color_continuous_scale="Reds"), width="stretch")
    r.plotly_chart(px.bar(g, x="Geography", y="Churned", text_auto=True, title="Number of churned customers",
                          color_discrete_sequence=["#C0392B"]), width="stretch")
    st.caption("Geographic Risk Index = country churn / overall churn of the whole bank. Above 1.0 = riskier than average.")
    st.dataframe(g.round(2), width="stretch", hide_index=True)
    st.subheader("Drill-down: Geography x Age Group")
    heat = f.pivot_table(index="Geography", columns="AgeGroup", values="Exited", aggfunc="mean", observed=True) * 100
    st.plotly_chart(px.imshow(heat.round(1), text_auto=True, color_continuous_scale="Reds",
                              title="Churn % by Geography and Age Group"), width="stretch")

# ---------------- Tab 3 ----------------
with tab3:
    l, r = st.columns(2)
    ga = rate(f, "AgeGroup", AGE_ORDER)
    gt = rate(f, "TenureGroup", TENURE_ORDER)
    l.plotly_chart(px.bar(ga, x="AgeGroup", y="ChurnRate", text_auto=".1f", title="Churn rate by age group",
                          color_discrete_sequence=["#C0392B"]), width="stretch")
    r.plotly_chart(px.bar(gt, x="TenureGroup", y="ChurnRate", text_auto=".1f", title="Churn rate by tenure group",
                          color_discrete_sequence=["#1F3A5F"]), width="stretch")
    st.subheader("Drill-down: Age x Tenure")
    h2 = f.pivot_table(index="AgeGroup", columns="TenureGroup", values="Exited", aggfunc="mean", observed=True) * 100
    st.plotly_chart(px.imshow(h2.round(1), text_auto=True, color_continuous_scale="Reds",
                              title="Churn % by Age Group and Tenure Group"), width="stretch")

# ---------------- Tab 4 ----------------
with tab4:
    pct = st.slider("High-value = customers in the top X% by balance", 5, 50, 25, 5)
    thr = df.Balance.quantile(1 - pct / 100)
    hv = f[f.Balance > thr]
    other = f[f.Balance <= thr]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Balance threshold", f"EUR {thr:,.0f}")
    k2.metric("High-Value Churn Ratio", f"{hv.Exited.mean() * 100:.1f}%" if len(hv) else "n/a")
    k3.metric("Other customers churn", f"{other.Exited.mean() * 100:.1f}%" if len(other) else "n/a")
    k4.metric("High-value balance lost", f"EUR {hv.loc[hv.Exited == 1, 'Balance'].sum() / 1e6:,.1f}M")
    if len(hv):
        sample = hv.sample(min(len(hv), 3000), random_state=1).copy()
        sample["Status"] = sample.Exited.map({0: "Retained", 1: "Churned"})
        st.plotly_chart(px.scatter(sample, x="EstimatedSalary", y="Balance", color="Status", opacity=0.55,
                                   color_discrete_map={"Retained": "#1F3A5F", "Churned": "#C0392B"},
                                   title="Salary vs Balance - high-value customers"), width="stretch")
        l, r = st.columns(2)
        gh = rate(hv, "Geography")
        l.plotly_chart(px.bar(gh, x="Geography", y="ChurnRate", text_auto=".1f", title="High-value churn by country",
                              color_discrete_sequence=["#C0392B"]), width="stretch")
        gp = rate(hv, "NumOfProducts")
        gp["NumOfProducts"] = gp["NumOfProducts"].astype(str)
        r.plotly_chart(px.bar(gp, x="NumOfProducts", y="ChurnRate", text_auto=".1f", title="High-value churn by products",
                              color_discrete_sequence=["#1F3A5F"]), width="stretch")
        st.subheader("Explorer: high-value customers who churned")
        cols = ["Geography", "Gender", "Age", "CreditScore", "Balance", "EstimatedSalary", "NumOfProducts", "IsActiveMember"]
        st.dataframe(hv[hv.Exited == 1][cols].sort_values("Balance", ascending=False).head(200), width="stretch", hide_index=True)
    else:
        st.info("No high-value customers in the current filter selection.")
