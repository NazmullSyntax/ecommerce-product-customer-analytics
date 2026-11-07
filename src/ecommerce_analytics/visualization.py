"""Plotting helpers for analytics outputs."""

import matplotlib.pyplot as plt
import pandas as pd


def plot_monthly_sales(monthly: pd.DataFrame) -> plt.Axes:
    """Plot monthly revenue from a monthly_sales result."""
    required = {"month", "revenue"}
    missing = required - set(monthly.columns)
    if missing:
        raise ValueError(f"Monthly sales data is missing columns: {', '.join(sorted(missing))}")
    ax = monthly.plot(x="month", y="revenue", kind="line", marker="o", legend=False)
    ax.set(title="Monthly revenue", xlabel="Month", ylabel="Revenue")
    ax.tick_params(axis="x", labelrotation=45)
    ax.figure.tight_layout()
    return ax
