"""Load Taiwan EPA air quality CSV files (one per station, year 2025).

Raw schema (wide):
    測站, 日期, 測項, 00, 01, ..., 23, [trailing empty col]

Each row = one station × one date × one parameter, with 24 hourly readings.
"""
from __future__ import annotations

import glob
import os
from typing import Iterable

import pandas as pd

RAW_COLS_RENAME = {"測站": "station", "日期": "date", "測項": "parameter"}
HOUR_COLS = [f"{h:02d}" for h in range(24)]


def load_csv(path: str) -> pd.DataFrame:
    """Read a single station CSV in EPA wide format."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    # Drop the trailing unnamed column produced by EPA's trailing comma
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df = df.rename(columns=RAW_COLS_RENAME)
    missing = {"station", "date", "parameter", *HOUR_COLS} - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    return df


def load_all_stations(raw_dir: str, pattern: str = "*_2025.csv") -> pd.DataFrame:
    """Concat every station CSV under raw_dir into a single wide DataFrame."""
    paths = sorted(glob.glob(os.path.join(raw_dir, pattern)))
    if not paths:
        raise FileNotFoundError(f"No files matching {pattern} in {raw_dir}")
    frames: Iterable[pd.DataFrame] = (load_csv(p) for p in paths)
    return pd.concat(frames, ignore_index=True)
