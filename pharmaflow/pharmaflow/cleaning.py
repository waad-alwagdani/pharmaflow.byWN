# PharmaFlow by WaadAlwagdani
# © 2026 Waad Alwagdani, PharmD (وعد الوقداني) · waadnalwagdani@gmail.com
# All rights reserved. Not to be copied, reused or redistributed without written permission.

"""Cleaning pipeline: every step is a small, testable function.

Raw issues handled
------------------
* Latin-1 encoding and long, inconsistent column names
* Dates in two formats ("2-Jun-06" and "9/11/2014") mixed with text such as
  "Pre-PQ Process", "Date Not Captured", "N/A - From RDC"
* Weight and freight stored as text, with sentinels ("Weight Captured Separately",
  "Freight Included in Commodity Cost", "Invoiced Separately") and cross-references
  to another line ("See DN-304 (ID#:10589)")
* Missing shipment mode
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

RENAME = {
    "ID": "id", "Project Code": "project_code", "PQ #": "pq", "PO / SO #": "po_so", "ASN/DN #": "asn_dn",
    "Country": "country", "Managed By": "managed_by", "Fulfill Via": "fulfill_via",
    "Vendor INCO Term": "inco_term", "Shipment Mode": "shipment_mode",
    "PQ First Sent to Client Date": "pq_sent_date", "PO Sent to Vendor Date": "po_sent_date",
    "Scheduled Delivery Date": "scheduled_date", "Delivered to Client Date": "delivered_date",
    "Delivery Recorded Date": "recorded_date", "Product Group": "product_group",
    "Sub Classification": "sub_class", "Vendor": "vendor", "Item Description": "item",
    "Molecule/Test Type": "molecule", "Brand": "brand", "Dosage": "dosage", "Dosage Form": "dosage_form",
    "Unit of Measure (Per Pack)": "units_per_pack", "Line Item Quantity": "quantity",
    "Line Item Value": "value_usd", "Pack Price": "pack_price", "Unit Price": "unit_price",
    "Manufacturing Site": "mfg_site", "First Line Designation": "first_line",
    "Weight (Kilograms)": "weight_raw", "Freight Cost (USD)": "freight_raw",
    "Line Item Insurance (USD)": "insurance_usd",
}
DATE_COLS = ["pq_sent_date", "po_sent_date", "scheduled_date", "delivered_date", "recorded_date"]
PRODUCT_NAMES = {"ARV": "Antiretroviral (ARV)", "HRDT": "HIV rapid test", "ANTM": "Antimalarial",
                 "ACT": "Artemisinin combination", "MRDT": "Malaria rapid test"}
REF = re.compile(r"ID#:(\d+)")


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=RENAME)


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse both date formats; any text sentinel becomes NaT."""
    out = df.copy()
    for col in DATE_COLS:
        s = out[col].astype("string")
        a = pd.to_datetime(s, format="%d-%b-%y", errors="coerce")
        b = pd.to_datetime(s, format="%m/%d/%Y", errors="coerce")
        out[col] = a.fillna(b)
    return out


def _resolve(raw: pd.Series, ids: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Turn a text column into numbers, following "See ... (ID#:123)" references.

    Returns (numeric value, status) where status is one of
    'recorded', 'reference', or the original sentinel text."""
    numeric = pd.to_numeric(raw, errors="coerce")
    status = pd.Series(np.where(numeric.notna(), "recorded", raw), index=raw.index, dtype="object")
    ref_ids = raw.astype("string").str.extract(REF, expand=False).astype("Int64")
    lookup = pd.Series(numeric.values, index=ids.values)
    is_ref = ref_ids.notna()
    status[is_ref] = "reference"
    resolved = numeric.copy()
    resolved[is_ref] = ref_ids[is_ref].map(lookup).astype(float).values
    return resolved, status


def parse_weight_and_freight(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["weight_kg"], out["weight_status"] = _resolve(out["weight_raw"], out["id"])
    freight, out["freight_status"] = _resolve(out["freight_raw"], out["id"])
    # A referenced freight cost belongs to a shared shipment already billed on another line:
    # keep it once (on the original line) so totals are not double counted.
    freight[out["freight_status"] == "reference"] = np.nan
    freight[out["freight_status"] == "Freight Included in Commodity Cost"] = 0.0
    out["freight_usd"] = freight
    return out.drop(columns=["weight_raw", "freight_raw"])


def fill_categories(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["shipment_mode"] = out["shipment_mode"].fillna("Unknown")
    out["product_name"] = out["product_group"].map(PRODUCT_NAMES).fillna(out["product_group"])
    out["first_line"] = out["first_line"].eq("Yes")
    return out


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Delivery performance, lead time and cost features."""
    out = df.copy()
    out["delay_days"] = (out["delivered_date"] - out["scheduled_date"]).dt.days
    out["on_time"] = out["delay_days"] <= 0
    out["lead_time_days"] = (out["delivered_date"] - out["po_sent_date"]).dt.days
    out["year"] = out["scheduled_date"].dt.year
    out["freight_pct_of_value"] = np.where(out["value_usd"] > 0, out["freight_usd"] / out["value_usd"] * 100, np.nan)
    out["freight_per_kg"] = np.where(out["weight_kg"] > 0, out["freight_usd"] / out["weight_kg"], np.nan)
    out.loc[out["lead_time_days"] < 0, "lead_time_days"] = np.nan  # PO recorded after delivery
    return out


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Full pipeline: raw SCMS export → analysis-ready table."""
    return (raw.pipe(rename_columns)
               .pipe(parse_dates)
               .pipe(parse_weight_and_freight)
               .pipe(fill_categories)
               .pipe(add_features))


def quality_report(raw: pd.DataFrame, clean_df: pd.DataFrame) -> pd.DataFrame:
    """Before/after summary of the cleaning, for the notebook and README."""
    rows = [
        ("Rows", len(raw), len(clean_df)),
        ("Duplicate IDs", int(raw["ID"].duplicated().sum()), int(clean_df["id"].duplicated().sum())),
        ("Missing shipment mode", int(raw["Shipment Mode"].isna().sum()), int((clean_df["shipment_mode"] == "Unknown").sum())),
        ("Weight not numeric", int(pd.to_numeric(raw["Weight (Kilograms)"], errors="coerce").isna().sum()), int(clean_df["weight_kg"].isna().sum())),
        ("Freight not numeric", int(pd.to_numeric(raw["Freight Cost (USD)"], errors="coerce").isna().sum()), int(clean_df["freight_usd"].isna().sum())),
        ("PO date missing", None, int(clean_df["po_sent_date"].isna().sum())),
    ]
    return pd.DataFrame(rows, columns=["check", "raw", "clean"])
