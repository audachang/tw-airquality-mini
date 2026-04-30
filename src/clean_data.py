"""Clean and reshape EPA air quality data: wide → long → tidy hourly wide-by-parameter."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .load_data import HOUR_COLS

# EPA invalid-data codes — all map to NaN. NR (No Rain) is handled separately below.
INVALID_CODES = {"x", "X", "#", "*", "A", "", "ND"}

# Parameters kept after filtering (per project requirements):
#   WD_HR     — wind direction, vector hourly mean (deg)
#   PM2.5     — fine particulate (µg/m³)
#   PM10      — coarse particulate (µg/m³)
#   THC       — total hydrocarbons (ppm)
#   AMB_TEMP  — ambient temperature (°C)
KEEP_PARAMETERS = ["WD_HR", "PM2.5", "PM10", "THC", "AMB_TEMP"]


def to_long(df_wide: pd.DataFrame) -> pd.DataFrame:
    """Melt 24 hour columns into one row per (station, date, parameter, hour)."""
    long = df_wide.melt(
        id_vars=["station", "date", "parameter"],
        value_vars=HOUR_COLS,
        var_name="hour",
        value_name="value_raw",
    )
    long["hour"] = long["hour"].astype(int)
    long["date"] = pd.to_datetime(long["date"], format="%Y/%m/%d %H:%M:%S").dt.normalize()
    long["datetime"] = long["date"] + pd.to_timedelta(long["hour"], unit="h")
    return long[["station", "datetime", "parameter", "value_raw"]]


def clean_values(df_long: pd.DataFrame) -> pd.DataFrame:
    """Convert value_raw → numeric float `value`. EPA codes → NaN; NR (RAINFALL only) → 0."""
    s = df_long["value_raw"].astype("string").str.strip()

    # NR is 'No Rain' and only valid for RAINFALL — any other parameter with NR is invalid.
    is_rainfall = df_long["parameter"].eq("RAINFALL")
    s = s.mask(s.eq("NR") & is_rainfall, "0")
    s = s.mask(s.isin(INVALID_CODES), pd.NA)

    df = df_long.copy()
    df["value"] = pd.to_numeric(s, errors="coerce")
    return df.drop(columns="value_raw")


def to_hourly(
    df_long_clean: pd.DataFrame, parameters: list[str] | None = None
) -> pd.DataFrame:
    """Pivot to (station, datetime) × parameters and reindex to the full hourly grid.

    Reindexing guarantees every station has one row per hour across the full date span,
    so all-NaN hours stay visible (pivot_table would otherwise drop them).
    """
    df = df_long_clean
    if parameters is not None:
        df = df[df["parameter"].isin(parameters)]

    pivot = df.pivot_table(
        index=["station", "datetime"],
        columns="parameter",
        values="value",
        aggfunc="first",
    )

    stations = sorted(df_long_clean["station"].unique())
    full_range = pd.date_range(
        df_long_clean["datetime"].min(),
        df_long_clean["datetime"].max(),
        freq="h",
    )
    full_idx = pd.MultiIndex.from_product([stations, full_range], names=["station", "datetime"])
    pivot = pivot.reindex(full_idx)

    wide = pivot.reset_index().rename_axis(columns=None)
    if parameters is not None:
        for p in parameters:
            if p not in wide.columns:
                wide[p] = np.nan
        wide = wide[["station", "datetime", *parameters]]
    return wide.sort_values(["station", "datetime"]).reset_index(drop=True)


def clean(df_wide: pd.DataFrame, parameters: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """End-to-end: wide → long-clean + hourly-wide. Returns both for downstream use."""
    long_clean = clean_values(to_long(df_wide))
    if parameters is not None:
        long_clean = long_clean[long_clean["parameter"].isin(parameters)].reset_index(drop=True)
    hourly = to_hourly(long_clean, parameters=parameters)
    return {"long": long_clean, "hourly": hourly}
