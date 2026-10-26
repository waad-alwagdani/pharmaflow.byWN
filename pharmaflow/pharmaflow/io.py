# PharmaFlow by WaadAlwagdani
# © 2026 Waad Alwagdani, PharmD (وعد الوقداني) · waadnalwagdani@gmail.com
# All rights reserved. Not to be copied, reused or redistributed without written permission.

"""Loading the raw and cleaned datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "SCMS_Delivery_History_Dataset_20150929.csv"
CLEAN_FILE = ROOT / "data" / "processed" / "shipments_clean.csv"


def load_raw(path: Path = RAW_FILE) -> pd.DataFrame:
    """The source file is Latin-1 encoded (e.g. "Côte d'Ivoire")."""
    return pd.read_csv(path, encoding="latin-1")


def load_clean(path: Path = CLEAN_FILE) -> pd.DataFrame:
    """Load the processed file, building it from the raw data the first time."""
    if not path.exists():
        from .cleaning import clean
        df = clean(load_raw())
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return df
    date_cols = ["pq_sent_date", "po_sent_date", "scheduled_date", "delivered_date", "recorded_date"]
    return pd.read_csv(path, parse_dates=date_cols)
