# Load-weighted S2 energy bounds

S2 is defined as DB ≤ 32 °C and Stull (2011) WB ≤ 23 °C, applied to the 19 full calendar years 2006–2024. Compressor power is 220 kW; displacement cases are 30% and 70%; the central electricity rate is ₱12/kWh.

| Profile | Load-Weighted_h_yr | vs_Flat_% | Low30_MWh | Mid50_MWh | High70_MWh | Mid50_Peso_M | HighDisp_Peso_M |
|---|---:|---:|---:|---:|---:|---:|---:|
| FLAT | 1,095.1 | 100.0% | 72.3 | 120.5 | 168.6 | ₱1.45M | ₱2.02M |
| ENTERPRISE | 714.5 | 65.2% | 47.2 | 78.6 | 110.0 | ₱0.94M | ₱1.32M |
| HYPERSCALE | 916.0 | 83.6% | 60.5 | 100.8 | 141.1 | ₱1.21M | ₱1.69M |

## Draft paragraph for §5.1

Using the S2 screening hours and representative diurnal data-centre load profiles, the flat-load assumption gives 1,095 load-weighted opportunity hours per year (the upper bound). A typical enterprise/office profile reduces this to 714 h/yr (65.2% of flat), while a flatter hyperscale profile gives 916 h/yr (83.6% of flat). At 220 kW compressor power, these correspond to 47.2–110.0 MWh/yr for the enterprise case and 60.5–141.1 MWh/yr for the hyperscale case, compared with 72.3–168.6 MWh/yr under the flat upper bound. Valued at the central ₱12/kWh rate, the central-case (50% displacement) values are ₱1.45M (flat), ₱0.94M (enterprise), ₱1.21M (hyperscale); the high-displacement (70%) bounds are ₱2.02M, ₱1.32M, ₱1.69M. Facility-electricity shares at central displacement: 0.60-0.92% (full 30-70% envelope: 0.36-1.28%, facility 1 MW IT at PUE 1.5 = 13,140 MWh/yr). At 50 MW IT the flat central case scales to ₱72M/yr.

Source records: 165,746 valid hourly observations; S2 flagged hours: 20,807 total (1,095.1 h/yr flat).
