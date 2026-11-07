"""
Data Visualization Engine Module
--------------------------------
Generates styled, standardized plots for executive presentation
and saves output graphics into reports/figures/.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from ecommerce_analytics.config import ConfigManager


class EDAVisualizer:
    """Manages consistent styling, color palettes, and plotting routines."""

    def __init__(self, config: ConfigManager = None) -> None:
        self.config = config or ConfigManager()
        self.figures_path = self.config.get_path("reports") / "figures"
        self.figures_path.mkdir(parents=True, exist_ok=True)
        self._apply_global_styles()

    def _apply_global_styles(self) -> None:
        """Sets clean corporate visual styles using Seaborn and Matplotlib defaults."""
        sns.set_theme(style="whitegrid", palette="muted")
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 12,
            "axes.labelweight": "bold",
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "figure.titlesize": 16
        })

    def plot_monthly_revenue_trend(self, df: pd.DataFrame, filename: str = "monthly_revenue_trend.png") -> Path:
        """Generates a line plot showing monthly GMV trends over time."""
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Filter out incomplete partial trailing months if present
        df_plot = df[df["purchase_year_month"] < "2018-09"].copy()

        color = "#1f77b4"
        ax1.plot(df_plot["purchase_year_month"], df_plot["total_revenue"] / 1e3, marker="o", linewidth=2.5, color=color)
        ax1.set_title("Monthly Revenue Performance (GMV in Thousands BRL)", pad=15)
        ax1.set_xlabel("Purchase Month (YYYY-MM)")
        ax1.set_ylabel("Total Revenue (k BRL)", color=color)
        ax1.tick_params(axis="y", labelcolor=color)
        plt.xticks(rotation=45)

        # Annotate Peak Revenue Month
        max_row = df_plot.loc[df_plot["total_revenue"].idxmax()]
        ax1.annotate(
            f"Peak: R${max_row['total_revenue']/1e3:,.1f}k",
            xy=(max_row["purchase_year_month"], max_row["total_revenue"] / 1e3),
            xytext=(10, 15),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
            weight="bold"
        )

        plt.tight_layout()
        save_path = self.figures_path / filename
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_top_categories(self, df: pd.DataFrame, filename: str = "top_product_categories.png") -> Path:
        """Generates a horizontal bar chart displaying top product categories by revenue."""
        fig, ax = plt.subplots(figsize=(10, 6))

        sns.barplot(
            data=df,
            x="total_revenue",
            y="product_category_name_english",
            palette="Blues_r",
            ax=ax
        )

        ax.set_title("Top 10 Product Categories by Gross Revenue", pad=15)
        ax.set_xlabel("Total Revenue (BRL)")
        ax.set_ylabel("Product Category")

        # Format X-axis labels to currency standard
        ax.xaxis.set_major_formatter("${x:,.0f}")

        plt.tight_layout()
        save_path = self.figures_path / filename
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_review_vs_delivery(self, df: pd.DataFrame, filename: str = "review_vs_delivery.png") -> Path:
        """Generates a bar plot showing average customer review score by delivery timeliness category."""
        fig, ax = plt.subplots(figsize=(8, 5))

        sns.barplot(
            data=df,
            x="delivery_category",
            y="average_review_score",
            palette="RdYlGn_r",
            ax=ax
        )

        ax.set_title("Impact of Delivery Timeliness on Customer Review Scores", pad=15)
        ax.set_xlabel("Delivery Status Category")
        ax.set_ylabel("Average Review Score (1 - 5 Stars)")
        ax.set_ylim(1, 5)

        # Value labels on top of bars
        for p in ax.patches:
            height = p.get_height()
            ax.annotate(
                f"{height:.2f} ⭐",
                (p.get_x() + p.get_width() / 2., height / 2),
                ha="center", va="center",
                color="white", weight="bold", fontsize=11
            )

        plt.tight_layout()
        save_path = self.figures_path / filename
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path


if __name__ == "__main__":
    from ecommerce_analytics.analysis import EDAAnalyzer

    analyzer = EDAAnalyzer()
    visualizer = EDAVisualizer()

    path1 = visualizer.plot_monthly_revenue_trend(analyzer.get_monthly_revenue_trend())
    print(f"Exported chart: {path1}")

    path2 = visualizer.plot_top_categories(analyzer.get_top_categories_by_revenue())
    print(f"Exported chart: {path2}")

    path3 = visualizer.plot_review_vs_delivery(analyzer.get_delivery_vs_review_score())
    print(f"Exported chart: {path3}")