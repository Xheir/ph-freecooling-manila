"""
01_screening.py — Canonical economizer-screening analysis for the NAIA paper.
Single source of truth for every number in draft.md. Run:
    C:/Users/gacpr/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe 01_screening.py
Outputs: analysis/summary_stats.txt (overwrites), and figures fig1-3 via 04_figures logic.
"""
import pandas as pd, numpy as np, pathlib

BASE = pathlib.Path(__file__).resolve().parent
CSV = BASE / "data" / "naia_manila_2006_2025_hourly.csv"
if not CSV.exists():
    CSV = BASE.parent / "data" / "naia_manila_2006_2025_hourly.csv"

# ---------------------------------------------------------------- data
df = pd.read_csv(CSV, parse_dates=["time"])
# Meteostat hourly timestamps are UTC (verified 2026-11-04 by diurnal-physics check:
# raw-hour DB max 05h == 13h local, raw-hour DB min 22h == 06h local for Manila).
# Convert to Philippine Standard Time (UTC+8, no DST) before any calendar aggregation.
df["time"] = df["time"] + pd.Timedelta(hours=8)
# Restrict to 19 full calendar years 2006-2024 (local calendar).
df = df[(df.time >= "2006-01-01") & (df.time < "2025-01-01")].copy()
n_archived = len(df)
n_missing = n_archived - df[["temp", "rhum"]].dropna().shape[0]
n_calendar = len(pd.date_range("2006-01-01", "2024-12-31 23:00", freq="h"))
n_absent = n_calendar - n_archived
df = df.dropna(subset=["temp", "rhum"]).reset_index(drop=True)

T, RH = df.temp, df.rhum
# Stull (2011) wet-bulb approximation, valid 5-99 RH%, -20..50 C
WB = (T * np.arctan(0.151977 * np.sqrt(RH + 8.313659))
      + np.arctan(T + RH) - np.arctan(RH - 1.676331)
      + 0.00391838 * RH**1.5 * np.arctan(0.023101 * RH) - 4.686035)
df["wb"] = WB
YRS = 19

# ---------------------------------------------------------------- screens (exact Boolean conditions, stated in paper Sec 3.3)
screens = {
    # S1: direct supply-air (cool-supply) economization
    "S1_direct_coolsupply (DB<=18 & WB<=14)":            (T <= 18) & (WB <= 14),
    # S2: water-side / evaporative opportunity screen (THE headline).
    # NOTE: this WB screen bounds water-side/evaporative economization only.
    # Indirect air-to-air applicability is NOT quantified here (paper Sec. 3.4 / 5.3).
    "S2_waterside_WB23 (DB<=32 & WB<=23)":               (T <= 32) & (WB <= 23),
    "S2b_waterside_WB20 (WB<=20)":                       (WB <= 20),
    "S2c_waterside_WB18 (WB<=18)":                       (WB <= 18),
    # S3: hot-hall direct/mixed air-side potential (SS697-style 26C+ hall, supply ~18-26)
    "S3_hothall_mixed (DB 15-27 & RH<=80)":              (T >= 15) & (T <= 27) & (RH <= 80),
    # S4: outdoor air within A1-allowable-like meteorological window (context only,
    #     NOT free-cooling availability - see paper Sec 3.4 limitations)
    "S4_A1like_meteo (DB 15-32 & RH 20-80)":             (T >= 15) & (T <= 32) & (RH >= 20) & (RH <= 80),
}
s2 = screens["S2_waterside_WB23 (DB<=32 & WB<=23)"]

# ---------------------------------------------------------------- summary
lines = []
A = lines.append
A(f"CANONICAL SCREENING SUMMARY (NAIA 98429, 2006-2024, {YRS} full years)")
A(f"Input: {len(df):,} valid hourly records from {n_archived:,} archived rows in the study window.")
A(f"Accounting: calendar {n_calendar:,} h (19 yrs incl. 5 leap days); absent rows {n_absent}; "
  f"rows w/ missing TEMP/RHUM {n_missing}; valid paired {len(df):,}.")
A(f"Coverage: {len(df)/n_calendar*100:.1f}% of calendar hours; {len(df)/n_archived*100:.1f}% of archived rows. "
  f"Screen percentages use valid-obs denominator.")
A(f"WB: Stull (2011) approx from DB+RH; timestamps station-local standard time (PST, UTC+8).")
A("")
for name, mask in screens.items():
    tot = int(mask.sum())
    A(f"{name}: {tot:,} h total = {tot/YRS:,.0f} h/yr = {tot/len(df)*100:.1f}% of valid obs")
A("")
A("S2 (headline) detail:")
m = df[s2].groupby(df.time.dt.month).size() / YRS
A("  monthly h/yr: " + ", ".join(f"{int(k)}:{v:.0f}" for k, v in m.items()))
ann = df.assign(flag=s2).groupby(df.time.dt.year)["flag"].sum()
A(f"  annual range: {ann.min()} h ({ann.idxmin()}) to {ann.max()} h ({ann.idxmax()})")
A(f"  mean: {ann.mean():.0f} h/yr, std: {ann.std():.0f} h")
A("")
A("Diurnal split (S2):")
night = df[s2 & ((df.time.dt.hour >= 22) | (df.time.dt.hour <= 6))]
A(f"  22:00-06:59 share: {len(night)/max(s2.sum(),1)*100:.0f}% of eligible hours")
A("")
A("VERDICT (relabeled 2026-10-15 after Opus review):")
A("- Direct cool-supply air-side economization: NOT feasible (~0 h/yr).")
A("- Water-side/evaporative WB<=23C opportunity window: ~1,100 h/yr (12.6%) - the headline.")
A("- Indirect air-to-air applicability is NOT quantified by this screen; it needs separate")
A("  temperature/enthalpy and exchanger-effectiveness modeling.")
A("- Hot-hall mixed air-side (15-27C, RH<=80): additional direct-use window, see S3 above.")
A("- A1-like meteo window (S4) is CONTEXT ONLY: outdoor air is within allowable-like")
A("  conditions ~half the year, but that is not free-cooling availability because supply")
A("  air must be cooler than the hall return. Do NOT equate S4 with economizer hours.")
out = BASE.parent / "analysis" / "summary_stats.txt"
if not out.parent.exists():
    out = BASE / "analysis" / "summary_stats.txt"
out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
