"""
03_rfm_segmentation.py
RFM (Recency, Frequency, Monetary) customer segmentation.

Each customer is scored 1-4 on recency, frequency, and monetary value
(quartile-based), then mapped to a named segment (Champions, Loyal,
At Risk, etc.). Rows without a CustomerID are excluded here since they
can't be attributed to a customer.

Outputs:
  outputs/figures/rfm_segments.png
  outputs/figures/segment_revenue_share.png
  outputs/tables/rfm_customer_scores.csv
  outputs/tables/segment_summary.csv

Usage: python src/03_rfm_segmentation.py  (run 01_data_cleaning.py first)
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

plt.style.use("seaborn-v0_8-whitegrid")
COLOR = "#2b6cb0"

df = pd.read_csv("data/online_retail_clean.csv", parse_dates=["InvoiceDate"])
df = df.dropna(subset=["CustomerID"]).copy()
df["CustomerID"] = df["CustomerID"].astype(int)

snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda s: (snapshot - s.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Revenue", "sum"),
)

# Quartile scores: recency reversed (recent = high score)
rfm["R"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1]).astype(int)
rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["M"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4]).astype(int)


def segment(row) -> str:
    r, f = row["R"], row["F"]
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal Customers"
    if r >= 3 and f <= 2:
        return "Recent / Promising"
    if r == 2 and f >= 3:
        return "Needs Attention"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r == 1 and f <= 2:
        return "Lost"
    return "Hibernating"


rfm["Segment"] = rfm.apply(segment, axis=1)
rfm.to_csv("outputs/tables/rfm_customer_scores.csv")

summary = (
    rfm.groupby("Segment")
    .agg(customers=("Recency", "size"),
         avg_recency_days=("Recency", "mean"),
         avg_frequency=("Frequency", "mean"),
         total_revenue=("Monetary", "sum"),
         avg_revenue=("Monetary", "mean"))
    .round(1)
    .sort_values("total_revenue", ascending=False)
)
summary["revenue_share"] = (summary["total_revenue"] / summary["total_revenue"].sum()).round(3)
summary.to_csv("outputs/tables/segment_summary.csv")
print(summary)

# ------------------------------------------------------------------ charts
order = summary.index.tolist()

fig, ax = plt.subplots(figsize=(10, 6))
counts = rfm["Segment"].value_counts().reindex(order)
counts.sort_values().plot(kind="barh", color=COLOR, ax=ax)
ax.set_title("Customer count by RFM segment", fontsize=13, fontweight="bold")
ax.set_xlabel("Customers")
ax.set_ylabel("")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("outputs/figures/rfm_segments.png", dpi=150, bbox_inches="tight")
plt.close()

fig, ax = plt.subplots(figsize=(10, 6))
rev = summary["total_revenue"].sort_values()
rev.plot(kind="barh", color=COLOR, ax=ax)
top_share = summary["revenue_share"].iloc[0]
ax.set_title(f"Revenue concentration: {summary.index[0]} alone drive {top_share:.0%} of revenue",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue")
ax.set_ylabel("")
ax.xaxis.set_major_formatter(
    mtick.FuncFormatter(lambda x, _: f"\u00a3{x / 1e6:,.1f}M" if x >= 1e6 else f"\u00a3{x / 1000:,.0f}K"))
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("outputs/figures/segment_revenue_share.png", dpi=150, bbox_inches="tight")
plt.close()

print("Figures and tables saved to outputs/")
