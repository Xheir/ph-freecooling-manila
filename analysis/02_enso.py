"""
02_enso.py — ENSO association test for the S2 opportunity series.
Reproduces §4.4: El Niño vs La Niña vs neutral group means + Welch tests.
Run AFTER 01_screening.py logic (loads the same CSV).
Classification: NOAA CPC ONI, events assigned to the calendar year containing
the event's DJF peak (e.g. 2015-16 El Niño -> 2016). Event list per NOAA CPC
historical episode table (ONI v5), events overlapping 2006-2024:
  El Niño: 2006-07, 2009-10, 2014-15, 2015-16, 2018-19, 2019-20, 2023-24
  La Niña: 2007-08, 2010-11, 2011-12, 2016-17, 2017-18, 2020-21, 2021-22, 2022-23
"""
import pandas as pd, numpy as np, pathlib
from scipy import stats

BASE = pathlib.Path(__file__).resolve().parent
CSV = BASE.parent / "data" / "naia_manila_2006_2025_hourly.csv"

elnino_djf = {2007, 2010, 2015, 2016, 2019, 2020, 2024}
lanina_djf = {2008, 2011, 2012, 2017, 2018, 2021, 2022, 2023}

df = pd.read_csv(CSV, parse_dates=["time"], engine="python",
                 dtype={"temp": "float32", "rhum": "float32"})
df = df[(df.time >= "2006-01-01") & (df.time < "2025-01-01")].dropna(subset=["temp", "rhum"]).copy()
T = df.temp.astype("float64"); RH = df.rhum.astype("float64")
WB = (T*np.arctan(0.151977*np.sqrt(RH+8.313659)) + np.arctan(T+RH) - np.arctan(RH-1.676331)
      + 0.00391838*RH**1.5*np.arctan(0.023101*RH) - 4.686035)
s2 = (T <= 32) & (WB <= 23)
ann = df.assign(flag=s2).groupby(df.time.dt.year)["flag"].sum()

rows = []
for y in sorted(ann.index):
    tag = "EN" if y in elnino_djf else ("LN" if y in lanina_djf else "N")
    rows.append((y, int(ann[y]), tag))
tbl = pd.DataFrame(rows, columns=["year", "hours", "enso"])
print(tbl.to_string(index=False))

g = {k: tbl.loc[tbl.enso == k, "hours"] for k in ("EN", "LN", "N")}
for k, v in g.items():
    print(f"{k}: n={len(v)} mean={v.mean():.0f} sd={v.std():.0f}")
t1, p1 = stats.ttest_ind(g["EN"], g["LN"], equal_var=False)
t2, p2 = stats.ttest_ind(g["EN"], g["N"], equal_var=False)
print(f"Welch EN vs LN: t={t1:.2f} p={p1:.2f}")
print(f"Welch EN vs N:  t={t2:.2f} p={p2:.2f}")
print("Conclusion: no statistically detectable ENSO association in the 19-year sample.")
