"""
04_cohort_retention.py
Monthly cohort retention analysis.

Customers are grouped by the month of their first purchase (cohort).
For each cohort, retention = % of customers who purchased again N months
later. Produces the classic retention heatmap.

Outputs:
  outputs/figures/cohort_retention.png
  outputs/tables/cohort_retention_matrix.csv

Usage: python src/04_cohort_retention.py  (run 01_data_cleaning.py first)
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

plt.style.use("seaborn-v0_8-whitegrid")

df = pd.read_csv("data/online_retail_clean.csv", parse_dates=["InvoiceDate"])
df = df.dropna(subset=["CustomerID"]).copy()
df["CustomerID"] = df["CustomerID"].astype(int)

df["OrderMonth"] = df["InvoiceDate"].dt.to_period("M")
df["CohortMonth"] = df.groupby("CustomerID")["OrderMonth"].transform("min")
df["CohortIndex"] = (
    (df["OrderMonth"].dt.year - df["CohortMonth"].dt.year) * 12
    + (df["OrderMonth"].dt.month - df["CohortMonth"].dt.month)
)

cohort_counts = (
    df.groupby(["CohortMonth", "CohortIndex"])["CustomerID"]
    .nunique()
    .unstack()
)
cohort_size = cohort_counts.iloc[:, 0]
retention = cohort_counts.divide(cohort_size, axis=0)
retention.index = retention.index.astype(str)
retention.to_csv("outputs/tables/cohort_retention_matrix.csv")

avg_m1 = retention[1].mean()

fig, ax = plt.subplots(figsize=(13, 7))
sns.heatmap(retention, annot=True, fmt=".0%", cmap="Blues",
            vmin=0, vmax=0.6, ax=ax,
            cbar_kws={"label": "Retention rate"})
ax.set_title(f"Monthly cohort retention (avg month-1 retention: {avg_m1:.0%})",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Months since first purchase")
ax.set_ylabel("Cohort (first purchase month)")
plt.tight_layout()
plt.savefig("outputs/figures/cohort_retention.png", dpi=150, bbox_inches="tight")
plt.close()

print(f"Cohorts: {len(retention)}")
print(f"Average month-1 retention: {avg_m1:.1%}")
print(f"Average month-3 retention: {retention[3].mean():.1%}")
print("Saved heatmap and matrix to outputs/")
