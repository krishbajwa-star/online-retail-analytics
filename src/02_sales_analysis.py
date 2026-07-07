"""
02_sales_analysis.py
Revenue trends, top products, and geographic breakdown.

Outputs:
  outputs/figures/monthly_revenue.png
  outputs/figures/top_products.png
  outputs/figures/revenue_by_country.png
  outputs/figures/orders_by_day_hour.png
  outputs/tables/monthly_summary.csv

Usage: python src/02_sales_analysis.py  (run 01_data_cleaning.py first)
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import seaborn as sns

plt.style.use("seaborn-v0_8-whitegrid")
COLOR = "#2b6cb0"
HIGHLIGHT = "#dd6b20"

df = pd.read_csv("data/online_retail_clean.csv", parse_dates=["InvoiceDate"])


def fmt_k(x, _):
    return f"\u00a3{x / 1000:,.0f}K" if x < 1_000_000 else f"\u00a3{x / 1e6:,.1f}M"


# ---------------------------------------------------------------- monthly revenue
monthly = (
    df.groupby("InvoiceMonth")
    .agg(revenue=("Revenue", "sum"), orders=("InvoiceNo", "nunique"))
    .reset_index()
)
# Dec 2011 is a partial month (data ends Dec 9) -- flag it rather than drop it
monthly["partial"] = monthly["InvoiceMonth"] == "2011-12"
monthly.to_csv("outputs/tables/monthly_summary.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 6))
complete = monthly[~monthly["partial"]]
ax.plot(complete["InvoiceMonth"], complete["revenue"], marker="o",
        color=COLOR, linewidth=2.5, label="Monthly revenue")
ax.plot(monthly["InvoiceMonth"].iloc[-2:], monthly["revenue"].iloc[-2:],
        linestyle="--", color="grey", label="Dec 2011 (partial month)")
peak = complete.loc[complete["revenue"].idxmax()]
ax.scatter([peak["InvoiceMonth"]], [peak["revenue"]], color=HIGHLIGHT, zorder=5, s=80)
ax.annotate(f"Peak: {fmt_k(peak['revenue'], None)}",
            xy=(peak["InvoiceMonth"], peak["revenue"]),
            xytext=(0, 14), textcoords="offset points",
            ha="center", fontweight="bold", color=HIGHLIGHT)
ax.set_title("Revenue climbs through Q4: Sep-Nov 2011 drove a ~50% lift over the summer baseline",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(fmt_k))
ax.tick_params(axis="x", rotation=45)
ax.spines[["top", "right"]].set_visible(False)
ax.legend()
plt.tight_layout()
plt.savefig("outputs/figures/monthly_revenue.png", dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------- top products
top_products = (
    df.groupby("Description")["Revenue"].sum().nlargest(10).sort_values()
)
fig, ax = plt.subplots(figsize=(10, 6))
top_products.plot(kind="barh", color=COLOR, ax=ax)
ax.set_title("Top 10 products by revenue", fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue")
ax.set_ylabel("")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(fmt_k))
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("outputs/figures/top_products.png", dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------- country breakdown
by_country = df.groupby("Country")["Revenue"].sum().sort_values(ascending=False)
uk_share = by_country["United Kingdom"] / by_country.sum()
non_uk = by_country.drop("United Kingdom").head(10).sort_values()
fig, ax = plt.subplots(figsize=(10, 6))
non_uk.plot(kind="barh", color=COLOR, ax=ax)
ax.set_title(f"Top international markets (UK = {uk_share:.0%} of total revenue)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue")
ax.set_ylabel("")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(fmt_k))
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("outputs/figures/revenue_by_country.png", dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------- order timing heatmap
df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()
df["Hour"] = df["InvoiceDate"].dt.hour
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
pivot = (
    df.drop_duplicates("InvoiceNo")
    .pivot_table(index="DayOfWeek", columns="Hour", values="InvoiceNo", aggfunc="count")
    .reindex(day_order)
)
fig, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(pivot, cmap="Blues", ax=ax, cbar_kws={"label": "Orders"})
ax.set_title("Order volume peaks midday, Tuesday-Thursday", fontsize=13, fontweight="bold")
ax.set_xlabel("Hour of day")
ax.set_ylabel("")
plt.tight_layout()
plt.savefig("outputs/figures/orders_by_day_hour.png", dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------- console summary
print(f"Total revenue: \u00a3{df['Revenue'].sum():,.0f}")
print(f"Total orders: {df['InvoiceNo'].nunique():,}")
print(f"Avg order value: \u00a3{df['Revenue'].sum() / df['InvoiceNo'].nunique():,.2f}")
print(f"UK revenue share: {uk_share:.1%}")
print(f"Peak month: {peak['InvoiceMonth']} (\u00a3{peak['revenue']:,.0f})")
print("Figures saved to outputs/figures/")
