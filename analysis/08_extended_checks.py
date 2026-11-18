"""
08_extended_checks.py — canonical outputs for every remaining narrative number:
WB ladder (21-25 C), S2/S3 overlap, diurnal peak/trough + block shares,
RH=100 saturation subset, top/bottom years. Run:
    C:/Users/gacpr/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -E 08_extended_checks.py
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
CSV = BASE.parent / "data" / "naia_manila_2006_2025_hourly.csv"
YRS = 19

df = pd.read_csv(CSV, parse_dates=["time"])
# Meteostat hourly timestamps are UTC (verified 2026-11-04 by diurnal-physics check:
# raw-hour DB max 05h == 13h local, raw-hour DB min 22h == 06h local for Manila).
# Convert to Philippine Standard Time (UTC+8, no DST) before any calendar aggregation.
df["time"] = df["time"] + pd.Timedelta(hours=8)
df = df[(df.time >= "2006-01-01") & (df.time < "2025-01-01")].copy()
n_sat_rh = int((df.rhum >= 100).sum())
n_low_rh = int((df.rhum < 5).sum())
df = df.dropna(subset=["temp", "rhum"]).reset_index(drop=True)
T, RH = df.temp, df.rhum
WB = (T * np.arctan(0.151977 * np.sqrt(RH + 8.313659))
      + np.arctan(T + RH) - np.arctan(RH - 1.676331)
      + 0.00391838 * RH**1.5 * np.arctan(0.023101 * RH) - 4.686035)

out = []
A = out.append
A(f"08 EXTENDED CHECKS (NAIA 98429, 2006-2024, {len(df):,} valid rows)")

# 1) WB ladder: (T<=32) & (WB<=x)
A("WB ladder (DB<=32 & WB<=x):")
for x in range(21, 26):
    tot = int(((T <= 32) & (WB <= x)).sum())
    A(f"  WB<={x}C: {tot:,} h total = {tot/YRS:,.0f} h/yr = {tot/len(df)*100:.1f}% of valid obs")

# 2) S2/S3 overlap
s2 = (T <= 32) & (WB <= 23)
s3 = (T >= 15) & (T <= 27) & (RH <= 80)
ov = int((s2 & s3).sum())
s3_only = int((s3 & ~s2).sum())
A(f"S2 total: {int(s2.sum()):,} h; S3 total: {int(s3.sum()):,} h")
A(f"S2&S3 overlap: {ov:,} h = {ov/YRS:,.1f} h/yr")
A(f"S3-only beyond S2: {s3_only:,} h = {s3_only/YRS:,.1f} h/yr")

# 3) diurnal
hh = df[s2].groupby(df[s2].time.dt.hour).size() / YRS
peak_h, peak_v = int(hh.idxmax()), hh.max()
trough_h, trough_v = int(hh.idxmin()), hh.min()
A(f"Diurnal peak: {peak_h:02d}:00 = {peak_v:,.1f} h/yr; trough: {trough_h:02d}:00 = {trough_v:,.1f} h/yr")
tot = int(s2.sum())
blk_1723 = int(df[s2 & (df.time.dt.hour >= 17) & (df.time.dt.hour <= 23)].shape[0])
blk_0916 = int(df[s2 & (df.time.dt.hour >= 9) & (df.time.dt.hour <= 16)].shape[0])
blk_2206 = int(df[s2 & ((df.time.dt.hour >= 22) | (df.time.dt.hour <= 6))].shape[0])
A(f"Block shares of S2: 17-23h {blk_1723/tot*100:.0f}% ({blk_1723:,} h); "
  f"09-16h {blk_0916/tot*100:.0f}% ({blk_0916:,} h); 22-06h {blk_2206/tot*100:.0f}% ({blk_2206:,} h)")

# 4) saturation subset (RH>=100 in raw window; recompute on valid set too)
sat_mask = df.rhum >= 100
sat_s2 = int((s2 & sat_mask).sum())
A(f"RH>=100 rows (valid set): {int(sat_mask.sum()):,} ({int(sat_mask.sum())/len(df)*100:.1f}%); "
  f"S2 hours among them: {sat_s2} = {sat_s2/YRS:.1f} h/yr = {sat_s2/tot*100:.1f}% of S2")
A(f"RH>=100 rows incl. missing-value rows (raw window): {n_sat_rh}; RH<5 rows: {n_low_rh}")

# 5) top/bottom years
ann = df.assign(flag=s2).groupby(df.time.dt.year)["flag"].sum().sort_values()
A(f"Bottom-3 years: {[(int(y), int(v)) for y, v in ann.head(3).items()]}")
A(f"Top-3 years: {[(int(y), int(v)) for y, v in ann.tail(3).items()]}")

print("\n".join(out))
(BASE / "extended_checks.txt").write_text("\n".join(out), encoding="utf-8")
