"""
07_load_weighting.py — Load-weighted S2 energy bounds for §5.1.

Applies representative 24-hour data-centre load profiles to the canonical
S2 screen (DB <= 32 °C and Stull wet-bulb <= 23 °C) over 2006–2024.
"""
from pathlib import Path

import sys
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
CSV = BASE.parent / "data" / "naia_manila_2006_2025_hourly.csv"
OUT = BASE / "load_weighting_results.md"
YRS = 19
COMPRESSOR_KW = 220.0
LOW_DISPLACEMENT = 0.30
MID_DISPLACEMENT = 0.50
HIGH_DISPLACEMENT = 0.70
FACILITY_MWH_YR = 1000.0 * 1.5 * 8760 / 1000  # 1 MW IT at PUE 1.5
CENTRAL_PESO_PER_KWH = 12.0

# Representative published/industry load-shape cases, indexed hour 0–23.
PROFILES = {
    "FLAT": np.array([
        1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00,
        1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00,
        1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00,
    ]),
    "ENTERPRISE": np.array([
        0.55, 0.55, 0.55, 0.55, 0.55, 0.60, 0.65, 0.75,
        0.85, 0.85, 0.85, 0.85, 0.80, 0.80, 0.85, 0.85,
        0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.55, 0.55,
    ]),
    "HYPERSCALE": np.array([
        0.80, 0.78, 0.78, 0.78, 0.80, 0.82, 0.85, 0.88,
        0.90, 0.92, 0.92, 0.92, 0.90, 0.90, 0.92, 0.92,
        0.90, 0.88, 0.85, 0.83, 0.82, 0.80, 0.80, 0.80,
    ]),
}


def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV, parse_dates=["time"])
    df["time"] = df["time"] + pd.Timedelta(hours=8)  # UTC -> PST (UTC+8): profiles are local-clock shapes
    df = df[(df.time >= "2006-01-01") & (df.time < "2025-01-01")].copy()
    df = df.dropna(subset=["temp", "rhum"]).reset_index(drop=True)
    t, rh = df["temp"], df["rhum"]
    # Stull (2011) wet-bulb approximation, matching 01_screening.py exactly.
    df["wb"] = (
        t * np.arctan(0.151977 * np.sqrt(rh + 8.313659))
        + np.arctan(t + rh)
        - np.arctan(rh - 1.676331)
        + 0.00391838 * rh**1.5 * np.arctan(0.023101 * rh)
        - 4.686035
    )
    df["s2"] = (t <= 32) & (df["wb"] <= 23)
    return df


def calculate(df: pd.DataFrame) -> list[dict[str, float | str]]:
    # This is the same 19-year mean as total weighted flagged hours / 19.
    results = []
    flat_hours = float((df["s2"]).sum()) / YRS
    for name, profile in PROFILES.items():
        weighted_total = float(
            (df["s2"].to_numpy(dtype=float)
             * profile[df["time"].dt.hour.to_numpy()]).sum()
        )
        hours_yr = weighted_total / YRS
        low_mwh = COMPRESSOR_KW * hours_yr * LOW_DISPLACEMENT / 1000
        mid_mwh = COMPRESSOR_KW * hours_yr * MID_DISPLACEMENT / 1000
        high_mwh = COMPRESSOR_KW * hours_yr * HIGH_DISPLACEMENT / 1000
        mid50_peso_m = mid_mwh * 1000 * CENTRAL_PESO_PER_KWH / 1_000_000  # draft central case (50%, P12/kWh)
        highdisp_peso_m = high_mwh * 1000 * CENTRAL_PESO_PER_KWH / 1_000_000
        results.append({
            "Profile": name,
            "Load-Weighted_h_yr": hours_yr,
            "vs_Flat_%": hours_yr / flat_hours * 100,
            "Low_Displacement_MWh": low_mwh,
            "Mid50_MWh": mid_mwh,
            "High_Displacement_MWh": high_mwh,
            "Mid50_Peso_M": mid50_peso_m,
            "HighDisp_Peso_M": highdisp_peso_m,
        })
    return results


def render(results: list[dict[str, float | str]], df: pd.DataFrame) -> str:
    lines = [
        "# Load-weighted S2 energy bounds",
        "",
        "S2 is defined as DB ≤ 32 °C and Stull (2011) WB ≤ 23 °C, applied to the 19 full calendar years 2006–2024. Compressor power is 220 kW; displacement cases are 30% and 70%; the central electricity rate is ₱12/kWh.",
        "",
        "| Profile | Load-Weighted_h_yr | vs_Flat_% | Low30_MWh | Mid50_MWh | High70_MWh | Mid50_Peso_M | HighDisp_Peso_M |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['Profile']} | {r['Load-Weighted_h_yr']:,.1f} | "
            f"{r['vs_Flat_%']:,.1f}% | {r['Low_Displacement_MWh']:,.1f} | "
            f"{r['Mid50_MWh']:,.1f} | {r['High_Displacement_MWh']:,.1f} | "
            f"₱{r['Mid50_Peso_M']:,.2f}M | ₱{r['HighDisp_Peso_M']:,.2f}M |"
        )
    flat, enterprise, hyperscale = results
    lines += [
        "",
        "## Draft paragraph for §5.1",
        "",
        (
            f"Using the S2 screening hours and representative diurnal data-centre load profiles, the flat-load assumption gives {flat['Load-Weighted_h_yr']:,.0f} load-weighted opportunity hours per year (the upper bound). A typical enterprise/office profile reduces this to {enterprise['Load-Weighted_h_yr']:,.0f} h/yr ({enterprise['vs_Flat_%']:,.1f}% of flat), while a flatter hyperscale profile gives {hyperscale['Load-Weighted_h_yr']:,.0f} h/yr ({hyperscale['vs_Flat_%']:,.1f}% of flat). At 220 kW compressor power, these correspond to {enterprise['Low_Displacement_MWh']:,.1f}–{enterprise['High_Displacement_MWh']:,.1f} MWh/yr for the enterprise case and {hyperscale['Low_Displacement_MWh']:,.1f}–{hyperscale['High_Displacement_MWh']:,.1f} MWh/yr for the hyperscale case, compared with {flat['Low_Displacement_MWh']:,.1f}–{flat['High_Displacement_MWh']:,.1f} MWh/yr under the flat upper bound. Valued at the central ₱12/kWh rate, the central-case (50% displacement) values are ₱{flat['Mid50_Peso_M']:,.2f}M (flat), ₱{enterprise['Mid50_Peso_M']:,.2f}M (enterprise), ₱{hyperscale['Mid50_Peso_M']:,.2f}M (hyperscale); the high-displacement (70%) bounds are ₱{flat['HighDisp_Peso_M']:,.2f}M, ₱{enterprise['HighDisp_Peso_M']:,.2f}M, ₱{hyperscale['HighDisp_Peso_M']:,.2f}M. Facility-electricity shares at central displacement: {enterprise['Mid50_MWh']/FACILITY_MWH_YR*100:.2f}-{flat['Mid50_MWh']/FACILITY_MWH_YR*100:.2f}% (full 30-70% envelope: {enterprise['Low_Displacement_MWh']/FACILITY_MWH_YR*100:.2f}-{flat['High_Displacement_MWh']/FACILITY_MWH_YR*100:.2f}%, facility 1 MW IT at PUE 1.5 = {FACILITY_MWH_YR:,.0f} MWh/yr). At 50 MW IT the flat central case scales to ₱{flat['Mid50_Peso_M']*50:,.0f}M/yr."
        ),
        "",
        f"Source records: {len(df):,} valid hourly observations; S2 flagged hours: {int(df['s2'].sum()):,} total ({int(df['s2'].sum()) / YRS:,.1f} h/yr flat).",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    data = load_data()
    result = calculate(data)
    text = render(result, data)
    OUT.write_text(text, encoding="utf-8")
    print(text, end="")
