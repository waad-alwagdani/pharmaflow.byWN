# PharmaFlow by WaadAlwagdani
# © 2026 Waad Alwagdani, PharmD (وعد الوقداني) · waadnalwagdani@gmail.com
# All rights reserved. Not to be copied, reused or redistributed without written permission.

"""Matplotlib / Seaborn charts in the PharmaFlow style."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from . import metrics

INK, INK2, INK3, HAIR = "#16131f", "#575366", "#9893a8", "#ebe8f2"
VIOLET, GREEN, AMBER, RED = "#6b4fe0", "#1e9e6e", "#c58a0b", "#c8443a"
PALETTE = [VIOLET, GREEN, AMBER, "#3a8fd6", RED, "#8e75f0"]
SIGNATURE = "PharmaFlow by WaadAlwagdani"


def set_theme() -> None:
    sns.set_theme(style="white", palette=PALETTE)
    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 160, "savefig.bbox": "tight",
        "axes.edgecolor": HAIR, "axes.labelcolor": INK2, "axes.titlecolor": INK,
        "axes.titlesize": 13, "axes.titleweight": "medium", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.grid.axis": "y",
        "grid.color": HAIR, "grid.linewidth": 0.8, "xtick.color": INK3, "ytick.color": INK3,
        "font.family": "DejaVu Sans", "legend.frameon": False,
    })


def _sign(fig) -> None:
    fig.text(0.995, 0.005, SIGNATURE, ha="right", va="bottom", fontsize=7, color=INK3)


def on_time_by_year(df: pd.DataFrame):
    y = metrics.yearly(df)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(y.index, y["on_time_rate"], color=VIOLET, lw=2.4, marker="o", ms=5)
    ax.fill_between(y.index, y["on_time_rate"], y["on_time_rate"].min() - 5, color=VIOLET, alpha=.08)
    last = y.index[-1]
    ax.annotate(f"{y['on_time_rate'].iloc[-1]:.0f}%", (last, y["on_time_rate"].iloc[-1]),
                xytext=(6, 0), textcoords="offset points", color=VIOLET, va="center", fontweight="bold")
    ax.set(title="On-time delivery rate by scheduled year", ylabel="% delivered on or before schedule", xlabel="")
    ax.set_ylim(max(0, y["on_time_rate"].min() - 10), 100)
    _sign(fig)
    return fig


def delay_distribution(df: pd.DataFrame):
    b = metrics.delay_buckets(df)
    colors = [GREEN, GREEN, AMBER, AMBER, RED]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    bars = ax.barh(b.index[::-1], b.values[::-1], color=colors[::-1])
    for bar, v in zip(bars, b.values[::-1]):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f"  {v:,} ({v / b.sum():.0%})", va="center", color=INK2, fontsize=9)
    ax.set(title="How late are shipments?", xlabel="Shipments")
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    _sign(fig)
    return fig


def mode_cost(df: pd.DataFrame):
    m = metrics.mode_cost_comparison(df).sort_values("median_freight_per_kg")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].bar(m.index, m["median_freight_per_kg"], color=VIOLET)
    axes[0].set(title="Median freight cost per kg", ylabel="USD / kg")
    axes[1].bar(m.index, m["on_time_rate"], color=GREEN)
    axes[1].set(title="On-time rate", ylabel="%")
    axes[1].set_ylim(0, 100)
    for ax in axes:
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.1f}", (p.get_x() + p.get_width() / 2, p.get_height()), ha="center", va="bottom", fontsize=9, color=INK2)
    _sign(fig)
    return fig


def country_heat(df: pd.DataFrame, top: int = 12):
    top_c = df["country"].value_counts().head(top).index
    sub = df[df["country"].isin(top_c)]
    piv = sub.pivot_table(index="country", columns="year", values="on_time", aggfunc="mean") * 100
    n = sub.pivot_table(index="country", columns="year", values="id", aggfunc="count")
    piv = piv.where(n >= 10)  # hide cells with fewer than 10 shipments
    piv = piv.loc[sub["country"].value_counts().index]
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(piv, cmap=sns.blend_palette([RED, "#f5e9c8", GREEN], as_cmap=True), vmin=40, vmax=100,
                annot=True, fmt=".0f", annot_kws={"size": 7}, linewidths=.5, linecolor="white", cbar_kws={"label": "% on time"}, ax=ax)
    ax.set(title=f"On-time rate by country and year (top {top} countries; blank = fewer than 10 shipments)", xlabel="", ylabel="")
    _sign(fig)
    return fig


def value_by_product(df: pd.DataFrame):
    s = df.groupby("product_name")["value_usd"].sum().sort_values() / 1e6
    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.barh(s.index, s.values, color=[VIOLET if i == len(s) - 1 else "#cfc6f6" for i in range(len(s))])
    for i, v in enumerate(s.values):
        ax.text(v, i, f"  ${v:,.0f}M" if v >= 1 else f"  ${v * 1000:,.0f}K", va="center", fontsize=9, color=INK2)
    ax.set(title="Commodity value by product group", xlabel="USD (millions)")
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    _sign(fig)
    return fig


def freight_vs_value(df: pd.DataFrame):
    rec = df[(df["freight_status"] == "recorded") & (df["value_usd"] > 0) & (df["freight_usd"] > 0)]
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=rec, x="value_usd", y="freight_usd", hue="shipment_mode", alpha=.45, s=14, ax=ax,
                    palette={"Air": VIOLET, "Truck": GREEN, "Air Charter": AMBER, "Ocean": "#3a8fd6", "Unknown": INK3})
    ax.legend(title="Shipment mode", loc="upper left")
    ax.set(xscale="log", yscale="log", title="Freight cost vs commodity value (log scale)", xlabel="Line item value (USD)", ylabel="Freight (USD)")
    ax.grid(True, which="major")
    _sign(fig)
    return fig
