"""
04_figures.py — Regenerates fig1-3 from the canonical S2 screen (DB<=32 & WB<=23).
Run after 01_screening.py. Outputs 300dpi PNG+PDF into analysis/.
"""
import pandas as pd, numpy as np, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = pathlib.Path(__file__).resolve().parent
CSV = BASE.parent / "data" / "naia_manila_2006_2025_hourly.csv"

df = pd.read_csv(CSV, parse_dates=["time"], engine="python")
df = df[(df.time >= "2006-01-01") & (df.time < "2025-01-01")].dropna(subset=["temp", "rhum"]).copy()
T, RH = df.temp, df.rhum
WB = (T * np.arctan(0.151977 * np.sqrt(RH + 8.313659))
      + np.arctan(T + RH) - np.arctan(RH - 1.676331)
      + 0.00391838 * RH**1.5 * np.arctan(0.023101 * RH) - 4.686035)
df["wb"] = WB
YRS = 19
s2 = (df.temp <= 32) & (df.wb <= 23)   # canonical headline screen
LBL = "DB $\\leq$32°C & WB $\\leq$23°C"

# ---- fig 1: monthly
m = df[s2].groupby(df.time.dt.month).size() / YRS
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.bar(m.index, m.values, color="#2c6fbb")
ax.set_xticks(range(1, 13), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
ax.set_ylabel("hours / year")
ax.set_title(f"Free-cooling opportunity hours by month — {LBL}, NAIA 2006–2024 mean")
for i, v in enumerate(m.values):
    ax.text(i + 1, v + 3, f"{v:.0f}", ha="center", fontsize=7)
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(BASE / f"fig1_monthly.{ext}", dpi=300, bbox_inches="tight", pad_inches=0.15)
plt.close(fig)

# ---- fig 2: diurnal
h = df[s2].groupby(df.time.dt.hour).size() / YRS
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.bar(h.index, h.values, color="#2c6fbb")
ax.set_xticks(range(0, 24, 2))
ax.set_xlabel("hour of day (station-local standard time, UTC+8)")
ax.set_ylabel("hours / year")
ax.set_title(f"Diurnal distribution of free-cooling opportunity — {LBL}")
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(BASE / f"fig2_diurnal.{ext}", dpi=300, bbox_inches="tight", pad_inches=0.15)
plt.close(fig)

# ---- fig 3: annual
ann = df.assign(flag=s2).groupby(df.time.dt.year)["flag"].sum()
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.bar(ann.index, ann.values, color="#2c6fbb")
ax.axhline(ann.mean(), ls="--", c="k", lw=1, label=f"mean {ann.mean():.0f} h")
ax.set_ylabel("hours / year")
ax.set_xlabel("year")
ax.set_title(f"Inter-annual variability — {LBL}")
ax.legend()
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(BASE / f"fig3_annual_wb.{ext}", dpi=300, bbox_inches="tight", pad_inches=0.15)
plt.close(fig)

print("figures regenerated:", sorted(p.name for p in BASE.glob('fig*')))
