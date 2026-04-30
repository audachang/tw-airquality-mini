# tw-airquality-mini

2025 年台灣 EPA 空氣品質測站資料的小型分析專案。原始資料為各測站逐日逐時的 wide-format CSV（測站 × 日期 × 測項 × 24 小時）；本專案提供載入、清理、彙整為長格式與每站每日的下游表格，並產出範例圖表。

## Status

- 資料覆蓋：`data/raw/` 已放入 **77 個測站** × 2025 年的原始 CSV（範圍涵蓋 AMB_TEMP、CH4、CO、PM2.5、PM10、THC、WD_HR…等多個測項）。
- 已完成 pipeline：
  - `src/load_data.py` — 讀單站 CSV / 合併所有站。
  - `src/clean_data.py` — wide→long 展開、EPA 無效碼（`x`、`#`、`*`、`A`、`ND`、空值，及非 RAINFALL 的 `NR`）轉 NaN、依測項 pivot 為 hourly wide。
  - `scripts/build_processed.py` — 一鍵把 `data/raw/` 全部站台展開、清理，輸出 `data/processed/aq_long.csv` 與 `aq_hourly.csv`（保留 `WD_HR`、`PM2.5`、`PM10`、`THC`、`AMB_TEMP`）。
- 已完成分析：4 站（中山 / 古亭 / 新店 / 板橋）PM2.5 日均趨勢，輸出於 `reports/`。

### 4-station PM2.5 摘要（2025）

| 測站 | mean (µg/m³) | p95 | days > 35 |
|---|---|---|---|
| 中山 | 12.61 | 24.97 | 2 |
| 古亭 | 10.60 | 23.77 | 1 |
| 新店 |  9.68 | 21.61 | 0 |
| 板橋 | 10.73 | 23.55 | 1 |

圖：`reports/pm25_compare.png`。

## Layout

```
data/
  raw/         # EPA wide-format CSV（gitignored；只追蹤 .gitkeep）
  processed/   # 由 scripts 產生的長/寬表（gitignored）
notebooks/
  01_explore.ipynb
src/
  load_data.py
  clean_data.py
scripts/
  build_processed.py
reports/       # 圖表 / 摘要 CSV
```

## How to run

1. 啟用虛擬環境：`.venv\Scripts\activate`（Windows）或 `source .venv/bin/activate`（Unix）。
2. 安裝套件：`pip install -r requirements.txt`。
3. 把各測站 CSV 放進 `data/raw/`，命名規則 `<測站>_2025.csv`（UTF-8-SIG，schema 為 `測站, 日期, 測項, 00..23`）。
4. 建立清理過的下游表（一次性，輸出到 `data/processed/`）：
   ```
   python -m scripts.build_processed
   ```
5. 互動式探索：`jupyter lab` 開啟 `notebooks/01_explore.ipynb`。
6. 重現 4 站 PM2.5 報告：
   ```python
   from src.load_data import load_csv
   from src.clean_data import to_long, clean_values
   import pandas as pd

   stations = ["中山", "古亭", "新店", "板橋"]
   wide = pd.concat([load_csv(f"data/raw/{s}_2025.csv") for s in stations])
   wide = wide[wide["parameter"] == "PM2.5"]
   long = clean_values(to_long(wide))
   daily = (long.assign(date=long["datetime"].dt.normalize())
                 .groupby(["station", "date"], as_index=False)["value"].mean())
   ```

## Data conventions

- 編碼：raw 為 `utf-8-sig`，輸出沿用 `utf-8-sig` 以利 Excel 直接開啟。
- 時間：`datetime = 日期 + 小時`，已 normalize 至每日 00:00；hourly wide 以 `(station, datetime)` 為 key。
- 缺值：EPA 原始失效碼一律轉為 NaN；只有 RAINFALL 的 `NR` 視為 0。
- 參考閾值：PM2.5 24 小時標準 35 µg/m³（`reports/pm25_compare.png` 中的紅色虛線）。

## Constraints

- 僅用 `pandas` + `matplotlib`（不使用 seaborn）。
- 任何合成資料以 `np.random.seed(42)`。
