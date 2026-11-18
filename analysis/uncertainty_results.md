# Stull wet-bulb uncertainty sensitivity

Dataset: NAIA hourly observations, 2006--2024; rows with missing temperature or RH removed.
S2 criterion: DB <= 32 °C and shifted WB <= 23 °C.
Annual statistics include all 19 calendar years (zero-hour years retained if present).

| WB_shift | total_S2_h | mean_h_yr | std_h_yr | pct_change_from_baseline |
|---:|---:|---:|---:|---:|
| +0.00 °C | 20807 | 1095.11 | 406.43 | +0.00% |
| +0.30 °C | 16683 | 878.05 | 379.32 | -19.82% |
| -0.30 °C | 26097 | 1373.53 | 423.96 | +25.42% |
| +0.65 °C | 12656 | 666.11 | 335.37 | -39.17% |
| -1.00 °C | 38649 | 2034.16 | 452.48 | +85.75% |

Baseline S2 hours with Stull WB in 22.7--23.3 °C: 4124 of 20807 (19.82%).

The threshold-band percentage is calculated among baseline S2 hours and uses the explicitly requested WB interval.
