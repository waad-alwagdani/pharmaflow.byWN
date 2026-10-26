# PharmaFlow by WaadAlwagdani
# © 2026 Waad Alwagdani, PharmD (وعد الوقداني) · waadnalwagdani@gmail.com
# All rights reserved. Not to be copied, reused or redistributed without written permission.

import unittest

import numpy as np
import pandas as pd

from pharmaflow import cleaning, load_raw, metrics


def tiny():
    """Three rows covering every messy case in the source file."""
    return pd.DataFrame({
        "ID": [1, 2, 3], "Country": ["Nigeria", "Haiti", "Nigeria"], "Shipment Mode": ["Air", None, "Truck"],
        "PQ First Sent to Client Date": ["Pre-PQ Process", "9/11/2014", "Date Not Captured"],
        "PO Sent to Vendor Date": ["1-Jan-10", "N/A - From RDC", "8/27/2014"],
        "Scheduled Delivery Date": ["10-Mar-10", "20-Sep-14", "1-Oct-14"],
        "Delivered to Client Date": ["15-Mar-10", "18-Sep-14", "1-Oct-14"],
        "Delivery Recorded Date": ["15-Mar-10", "18-Sep-14", "1-Oct-14"],
        "Product Group": ["ARV", "HRDT", "ARV"], "Vendor": ["A", "B", "A"], "Molecule/Test Type": ["X", "Y", "X"],
        "Line Item Value": [1000.0, 500.0, 0.0], "Pack Price": [10.0, 5.0, 1.0], "First Line Designation": ["Yes", "No", "Yes"],
        "Weight (Kilograms)": ["100", "See DN-1 (ID#:1)", "Weight Captured Separately"],
        "Freight Cost (USD)": ["250", "See DN-1 (ID#:1)", "Freight Included in Commodity Cost"],
    })


class Cleaning(unittest.TestCase):
    def setUp(self):
        self.df = cleaning.clean(tiny())

    def test_both_date_formats(self):
        self.assertEqual(self.df.loc[1, "pq_sent_date"], pd.Timestamp("2014-09-11"))
        self.assertEqual(self.df.loc[0, "po_sent_date"], pd.Timestamp("2010-01-01"))
        self.assertTrue(pd.isna(self.df.loc[0, "pq_sent_date"]))  # "Pre-PQ Process"
        self.assertTrue(pd.isna(self.df.loc[1, "po_sent_date"]))  # "N/A - From RDC"

    def test_weight_reference_is_followed(self):
        self.assertEqual(self.df.loc[1, "weight_kg"], 100)
        self.assertEqual(self.df.loc[1, "weight_status"], "reference")
        self.assertTrue(np.isnan(self.df.loc[2, "weight_kg"]))

    def test_shared_freight_not_double_counted(self):
        self.assertEqual(self.df["freight_usd"].sum(), 250)
        self.assertEqual(self.df.loc[2, "freight_usd"], 0)  # included in commodity cost

    def test_features(self):
        self.assertEqual(self.df.loc[0, "delay_days"], 5)
        self.assertFalse(self.df.loc[0, "on_time"])
        self.assertTrue(self.df.loc[1, "on_time"])
        self.assertEqual(self.df.loc[1, "shipment_mode"], "Unknown")
        self.assertAlmostEqual(self.df.loc[0, "freight_pct_of_value"], 25)
        self.assertTrue(np.isnan(self.df.loc[2, "freight_pct_of_value"]))  # zero value


class RealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_raw()
        cls.df = cleaning.clean(cls.raw)

    def test_shape_and_ids(self):
        self.assertEqual(len(self.df), 10324)
        self.assertFalse(self.df["id"].duplicated().any())

    def test_all_delivery_dates_parsed(self):
        self.assertEqual(self.df["scheduled_date"].isna().sum(), 0)
        self.assertEqual(self.df["delivered_date"].isna().sum(), 0)

    def test_kpis(self):
        k = metrics.kpis(self.df)
        self.assertEqual((k["countries"], k["vendors"]), (43, 73))
        self.assertAlmostEqual(k["on_time_rate"], 88.5, delta=0.1)

    def test_delay_buckets_cover_everything(self):
        self.assertEqual(metrics.delay_buckets(self.df).sum(), len(self.df))

    def test_air_costs_more_than_ocean(self):
        m = metrics.mode_cost_comparison(self.df)
        self.assertGreater(m.loc["Air", "median_freight_per_kg"], m.loc["Ocean", "median_freight_per_kg"])


if __name__ == "__main__":
    unittest.main()
