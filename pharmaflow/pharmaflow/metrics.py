# PharmaFlow by WaadAlwagdani
# © 2026 Waad Alwagdani, PharmD (وعد الوقداني) · waadnalwagdani@gmail.com
# All rights reserved. Not to be copied, reused or redistributed without written permission.

"""KPIs and grouped summaries (NumPy / pandas)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def kpis(df: pd.DataFrame) -> dict[str, float]:
    delivered = df["delay_days"].notna()
    late = df.loc[delivered & ~df["on_time"], "delay_days"]
    return {
        "shipments": len(df),
        "countries": df["country"].nunique(),
        "vendors": df["vendor"].nunique(),
        "value_usd": df["value_usd"].sum(),
        "freight_usd": df["freight_usd"].sum(),
        "on_time_rate": df.loc[delivered, "on_time"].mean() * 100,
        "median_delay_when_late": float(late.median()) if len(late) else 0.0,
        "median_lead_time": float(df["lead_time_days"].median()),
        "freight_pct_median": float(df["freight_pct_of_value"].median()),
    }


def by(df: pd.DataFrame, col: str, min_shipments: int = 1) -> pd.DataFrame:
    """Delivery and cost performance grouped by any column."""
    g = df.groupby(col, observed=True)
    out = pd.DataFrame({
        "shipments": g.size(),
        "value_usd": g["value_usd"].sum(),
        "on_time_rate": g["on_time"].mean() * 100,
        "mean_delay_days": g["delay_days"].mean(),
        "late_p90_days": g["delay_days"].quantile(0.9),
        "median_lead_time": g["lead_time_days"].median(),
        "median_freight_pct": g["freight_pct_of_value"].median(),
        "median_freight_per_kg": g["freight_per_kg"].median(),
    })
    return out[out["shipments"] >= min_shipments].sort_values("shipments", ascending=False)


def yearly(df: pd.DataFrame) -> pd.DataFrame:
    return by(df, "year").sort_index()


def delay_buckets(df: pd.DataFrame) -> pd.Series:
    bins = [-np.inf, -1, 0, 7, 30, np.inf]
    labels = ["Early", "On the day", "1–7 days late", "8–30 days late", ">30 days late"]
    return pd.cut(df["delay_days"], bins=bins, labels=labels).value_counts().reindex(labels)


def vendor_scorecard(df: pd.DataFrame, min_shipments: int = 50) -> pd.DataFrame:
    """Vendors ranked by on-time rate, with value share."""
    sc = by(df, "vendor", min_shipments)
    sc["value_share_pct"] = sc["value_usd"] / df["value_usd"].sum() * 100
    return sc.sort_values("on_time_rate")


def price_trend(df: pd.DataFrame, molecule_contains: str) -> pd.DataFrame:
    """Median pack price per year for a molecule (e.g. 'Efavirenz/Lamivudine/Tenofovir')."""
    sub = df[df["molecule"].str.contains(molecule_contains, case=False, na=False, regex=False)]
    return sub.groupby("year")["pack_price"].agg(["median", "count"]).rename(columns={"median": "median_pack_price"})


def mode_cost_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Air vs Truck vs Ocean: cost per kg and delay, recorded freight only."""
    rec = df[df["freight_status"] == "recorded"]
    return by(rec[rec["shipment_mode"] != "Unknown"], "shipment_mode")[
        ["shipments", "median_freight_per_kg", "median_freight_pct", "on_time_rate", "mean_delay_days"]]
