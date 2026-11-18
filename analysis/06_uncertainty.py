"""Sensitivity of NAIA S2 economizer hours to Stull wet-bulb error bands."""

from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
DATA_PATH = BASE.parent / "data" / "naia_manila_2006_2025_hourly.csv"
OUTPUT_PATH = BASE / "uncertainty_results.md"

# Stull (2011) approximation error scenarios, in degrees Celsius.
SHIFTS = [0.0, 0.3, -0.3, 0.65, -1.0]


def stull_wet_bulb(temp_c: pd.Series, rh_pct: pd.Series) -> pd.Series:
    """Calculate wet-bulb temperature using Stull's (2011) approximation."""
    return (
        temp_c * np.arctan(0.151977 * np.sqrt(rh_pct + 8.313659))
        + np.arctan(temp_c + rh_pct)
        - np.arctan(rh_pct - 1.676331)
        + 0.00391838 * rh_pct**1.5 * np.arctan(0.023101 * rh_pct)
        - 4.686035
    )


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["time"])
    df["time"] = df["time"] + pd.Timedelta(hours=8)  # UTC -> PST (UTC+8)
    df = df[df["time"].dt.year.between(2006, 2024)].copy()
    df = df.dropna(subset=["temp", "rhum"])
    df["year"] = df["time"].dt.year
    df["wb"] = stull_wet_bulb(df["temp"], df["rhum"])

    # S2 is dry-bulb <= 32 C and wet-bulb <= 23 C.
    baseline_s2 = (df["temp"] <= 32) & (df["wb"] <= 23)
    baseline_total = int(baseline_s2.sum())
    near_threshold = baseline_s2 & df["wb"].between(22.7, 23.3, inclusive="both")
    near_threshold_pct = 100 * near_threshold.sum() / baseline_total if baseline_total else np.nan

    rows = []
    for shift in SHIFTS:
        s2 = (df["temp"] <= 32) & ((df["wb"] + shift) <= 23)
        annual = s2.groupby(df["year"]).sum().reindex(range(2006, 2025), fill_value=0)
        total = int(s2.sum())
        mean_h = float(annual.mean())
        std_h = float(annual.std(ddof=1))  # sample SD, matches paper (406.4 h)
        pct_change = 100 * (total - baseline_total) / baseline_total if baseline_total else np.nan
        rows.append(
            {
                "WB_shift": shift,
                "total_S2_h": total,
                "mean_h_yr": mean_h,
                "std_h_yr": std_h,
                "pct_change_from_baseline": pct_change,
            }
        )

    results = pd.DataFrame(rows)
    lines = [
        "# Stull wet-bulb uncertainty sensitivity",
        "",
        "Dataset: NAIA hourly observations, 2006--2024; rows with missing temperature or RH removed.",
        "S2 criterion: DB <= 32 °C and shifted WB <= 23 °C.",
        "Annual statistics include all 19 calendar years (zero-hour years retained if present).",
        "",
        "| WB_shift | total_S2_h | mean_h_yr | std_h_yr | pct_change_from_baseline |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in results.itertuples(index=False):
        lines.append(
            f"| {row.WB_shift:+.2f} °C | {row.total_S2_h:d} | "
            f"{row.mean_h_yr:.2f} | {row.std_h_yr:.2f} | {row.pct_change_from_baseline:+.2f}% |"
        )
    lines += [
        "",
        f"Baseline S2 hours with Stull WB in 22.7--23.3 °C: {int(near_threshold.sum())} "
        f"of {baseline_total} ({near_threshold_pct:.2f}%).",
        "",
        "The threshold-band percentage is calculated among baseline S2 hours and uses the explicitly requested WB interval.",
        "",
    ]
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Rows analyzed: {len(df)}")
    print(f"Baseline S2 hours: {baseline_total}")
    print(f"Baseline S2 hours with WB 22.7--23.3 C: {int(near_threshold.sum())} ({near_threshold_pct:.2f}%)")
    print(results.to_string(index=False, formatters={
        "WB_shift": "{:+.2f}".format,
        "mean_h_yr": "{:.2f}".format,
        "std_h_yr": "{:.2f}".format,
        "pct_change_from_baseline": "{:+.2f}%".format,
    }))
    print(f"Wrote: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
