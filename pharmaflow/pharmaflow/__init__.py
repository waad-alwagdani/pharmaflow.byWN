# PharmaFlow by WaadAlwagdani
# © 2026 Waad Alwagdani, PharmD (وعد الوقداني) · waadnalwagdani@gmail.com
# All rights reserved. Not to be copied, reused or redistributed without written permission.

"""PharmaFlow — analysis of 10,324 USAID global health medicine shipments (2006–2015).

Author: Waad Alwagdani, PharmD (WaadAlwagdani)."""

from .io import load_raw, load_clean
from .cleaning import clean
from . import metrics, viz

__version__ = "1.0.0"
__author__ = "WaadAlwagdani (Waad Alwagdani, PharmD)"
SIGNATURE = "PharmaFlow by WaadAlwagdani"
__all__ = ["load_raw", "load_clean", "clean", "metrics", "viz", "SIGNATURE"]
