"""Build cleaned long + hourly-wide CSVs from raw EPA station files.

Usage:
    python -m scripts.build_processed
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `python scripts/build_processed.py` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.load_data import load_all_stations
from src.clean_data import clean, KEEP_PARAMETERS

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"


def main() -> None:
    print(f"[1/4] Loading raw CSVs from {RAW_DIR} ...")
    wide = load_all_stations(str(RAW_DIR))
    print(f"      raw concat shape: {wide.shape}, stations: {wide['station'].nunique()}")

    print(f"[2/4] Cleaning + reshaping (keep: {KEEP_PARAMETERS}) ...")
    out = clean(wide, parameters=KEEP_PARAMETERS)
    long_df, hourly_df = out["long"], out["hourly"]
    print(f"      long shape:   {long_df.shape}")
    print(f"      hourly shape: {hourly_df.shape}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long_path = OUT_DIR / "aq_long.csv"
    hourly_path = OUT_DIR / "aq_hourly.csv"

    print(f"[3/4] Writing {long_path} ...")
    long_df.to_csv(long_path, index=False, encoding="utf-8-sig")
    print(f"[3/4] Writing {hourly_path} ...")
    hourly_df.to_csv(hourly_path, index=False, encoding="utf-8-sig")

    print("[4/4] Sanity check:")
    print(f"      stations in hourly: {hourly_df['station'].nunique()}")
    print(f"      datetime range: {hourly_df['datetime'].min()} → {hourly_df['datetime'].max()}")
    miss = hourly_df[KEEP_PARAMETERS].isna().mean().mul(100).round(2)
    print(f"      missing rate (%):\n{miss.to_string()}")
    no_thc = (
        hourly_df.groupby("station")["THC"].apply(lambda s: s.isna().all())
    )
    no_thc_stations = no_thc[no_thc].index.tolist()
    print(f"      stations with NO THC at all ({len(no_thc_stations)}): {no_thc_stations}")

    print("Done.")


if __name__ == "__main__":
    main()
