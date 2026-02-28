"""
visualisation.py
----------------
Publication-quality plotting utilities for the tennis racket
virtual prototyping framework.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

_PALETTE = {
    "primary":   "#1B6CA8",
    "secondary": "#E8572A",
    "accent":    "#2EAA5E",
    "light":     "#B0C4DE",
    "dark":      "#1A1A2E",
}


def _apply_style(ax, title: str = "", xlabel: str = "", ylabel: str = ""):
    """Apply consistent styling to a matplotlib Axes object."""
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)
    return ax


# ---------------------------------------------------------------------------
# Individual plot functions
# ---------------------------------------------------------------------------

def plot_exit_speed_distribution(df: pd.DataFrame, ax=None, save_path: str = None):
    """Histogram of ball exit speed across all designs."""
    fig, ax = (None, ax) if ax else plt.subplots(figsize=(7, 4))

    ax.hist(df["v_exit"], bins=40, color=_PALETTE["primary"], edgecolor="white", linewidth=0.4)
    _apply_style(ax, "Ball Exit Speed Distribution", "Exit Speed (m/s)", "Count")
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))

    if save_path:
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
    return ax


def plot_shock_distribution(df: pd.DataFrame, ax=None, save_path: str = None):
    """Histogram of handle shock proxy across all designs."""
    fig, ax = (None, ax) if ax else plt.subplots(figsize=(7, 4))

    ax.hist(df["shock_proxy"], bins=40, color=_PALETTE["secondary"], edgecolor="white", linewidth=0.4)
    _apply_style(ax, "Handle Shock Proxy Distribution", "Shock Proxy (lower = better)", "Count")

    if save_path:
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
    return ax


def plot_sweet_spot_map(df: pd.DataFrame, ax=None, save_path: str = None):
    """
    Average exit speed and shock proxy binned by impact location.

    Shows the classic sweet-spot profile along the racket length.
    """
    bins = np.linspace(df["x_norm"].min(), df["x_norm"].max(), 25)
    df_copy = df.copy()
    df_copy["x_bin"] = pd.cut(df_copy["x_norm"], bins=bins, include_lowest=True)

    g = df_copy.groupby("x_bin", observed=False).agg(
        v_exit_mean=("v_exit", "mean"),
        shock_mean=("shock_proxy", "mean"),
    ).reset_index()
    x_mid = np.array([(i.left + i.right) / 2 for i in g["x_bin"]])

    fig, axes = (None, (ax, ax)) if ax else plt.subplots(1, 2, figsize=(13, 4))
    ax1, ax2 = axes if hasattr(axes, "__len__") else (ax, ax)

    ax1.plot(x_mid, g["v_exit_mean"], marker="o", color=_PALETTE["primary"], linewidth=2, markersize=5)
    _apply_style(ax1, "Exit Speed vs Impact Location", "Impact Location (0=handle, 1=tip)", "Avg Exit Speed (m/s)")

    ax2.plot(x_mid, g["shock_mean"], marker="s", color=_PALETTE["secondary"], linewidth=2, markersize=5)
    _apply_style(ax2, "Shock Proxy vs Impact Location", "Impact Location (0=handle, 1=tip)", "Avg Shock Proxy")

    if save_path:
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
    return axes


def plot_sweet_score_scatter(df: pd.DataFrame, best: pd.DataFrame, ax=None, save_path: str = None):
    """
    Scatter of sweet_score vs impact location, highlighting the top designs.
    """
    fig, ax = (None, ax) if ax else plt.subplots(figsize=(8, 5))

    ax.scatter(df["x_norm"], df["sweet_score"],
               s=6, alpha=0.25, color=_PALETTE["light"], label="All designs")
    ax.scatter(best["x_norm"], best["sweet_score"],
               s=55, color=_PALETTE["secondary"], zorder=5, label=f"Top {len(best)}")

    _apply_style(ax, "Sweet Spot Region", "Impact Location (0=handle, 1=tip)", "Sweet Score (higher = better)")
    ax.legend(fontsize=9)

    if save_path:
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
    return ax


def plot_pareto_tradeoff(df: pd.DataFrame, best: pd.DataFrame, ax=None, save_path: str = None):
    """
    Pareto-style scatter: exit speed vs shock proxy, highlighting top designs.
    """
    fig, ax = (None, ax) if ax else plt.subplots(figsize=(8, 5))

    ax.scatter(df["shock_proxy"], df["v_exit"],
               s=6, alpha=0.25, color=_PALETTE["light"], label="All designs")
    ax.scatter(best["shock_proxy"], best["v_exit"],
               s=55, color=_PALETTE["secondary"], zorder=5, label=f"Top {len(best)}")

    _apply_style(ax, "Performance vs Comfort Tradeoff",
                 "Shock Proxy (lower = better)", "Exit Speed (m/s)")
    ax.legend(fontsize=9)

    if save_path:
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
    return ax


def plot_correlation_heatmap(df: pd.DataFrame, ax=None, save_path: str = None):
    """
    Correlation matrix heatmap across design inputs and performance outputs.
    """
    cols = ["m_racket", "k_string", "damping", "x_norm", "v_exit", "shock_proxy", "sweet_score"]
    available = [c for c in cols if c in df.columns]
    corr = df[available].corr(numeric_only=True)

    fig, ax = (None, ax) if ax else plt.subplots(figsize=(9, 5))

    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(available)))
    ax.set_yticks(range(len(available)))
    ax.set_xticklabels(available, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(available, fontsize=9)
    ax.set_title("Correlation Matrix — Inputs vs Outputs", fontsize=13, fontweight="bold", pad=10)

    # Annotate cells
    for i in range(len(available)):
        for j in range(len(available)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}",
                    ha="center", va="center", fontsize=7,
                    color="white" if abs(corr.values[i, j]) > 0.5 else "black")

    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)

    if save_path:
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
    return ax


def plot_full_dashboard(df: pd.DataFrame, best: pd.DataFrame, save_path: str = None):
    """
    Render a 2×3 dashboard of all key plots in a single figure.

    Parameters
    ----------
    df : pd.DataFrame
        Full simulation results (must include sweet_score).
    best : pd.DataFrame
        Top-n designs subset.
    save_path : str, optional
        If provided, saves the figure to this path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig = plt.figure(figsize=(18, 10))
    fig.suptitle("Tennis Racket Virtual Prototyping — Performance Dashboard",
                 fontsize=15, fontweight="bold", y=1.01)

    ax1 = fig.add_subplot(2, 3, 1)
    ax2 = fig.add_subplot(2, 3, 2)
    ax3 = fig.add_subplot(2, 3, 3)
    ax4 = fig.add_subplot(2, 3, 4)
    ax5 = fig.add_subplot(2, 3, 5)
    ax6 = fig.add_subplot(2, 3, 6)

    plot_exit_speed_distribution(df, ax=ax1)
    plot_shock_distribution(df, ax=ax2)

    # Sweet spot line plots share ax3 area — use twinx approach
    bins = np.linspace(df["x_norm"].min(), df["x_norm"].max(), 25)
    df_c = df.copy()
    df_c["x_bin"] = pd.cut(df_c["x_norm"], bins=bins, include_lowest=True)
    g = df_c.groupby("x_bin", observed=False).agg(
        v_exit_mean=("v_exit", "mean"),
        shock_mean=("shock_proxy", "mean"),
    ).reset_index()
    x_mid = np.array([(i.left + i.right) / 2 for i in g["x_bin"]])

    ax3.plot(x_mid, g["v_exit_mean"], color=_PALETTE["primary"], linewidth=2, label="Exit speed")
    ax3_twin = ax3.twinx()
    ax3_twin.plot(x_mid, g["shock_mean"], color=_PALETTE["secondary"], linewidth=2, linestyle="--", label="Shock")
    ax3.set_xlabel("Impact Location", fontsize=10)
    ax3.set_ylabel("Avg Exit Speed (m/s)", fontsize=9, color=_PALETTE["primary"])
    ax3_twin.set_ylabel("Avg Shock Proxy", fontsize=9, color=_PALETTE["secondary"])
    ax3.set_title("Sweet Spot Profile", fontsize=12, fontweight="bold")
    ax3.spines["top"].set_visible(False)

    plot_sweet_score_scatter(df, best, ax=ax4)
    plot_pareto_tradeoff(df, best, ax=ax5)
    plot_correlation_heatmap(df, ax=ax6)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Dashboard saved to: {save_path}")

    return fig
