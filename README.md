# Free-Cooling Availability in Philippine Data Centers

Companion repository for the paper: **"Free-Cooling Availability in Philippine Data Centers: A Weather-Data Analysis of Economizer Opportunity in a Tropical Climate"** (Provido, 2026 — preprint, SSRN; DOI to be added on posting).

**The finding in one sentence:** Direct air-side free cooling is essentially impossible in Manila (1 qualifying hour in 19 years), but a measurable wet-bulb-bounded window — **~1,095 hours/year (12.6%)** at WB ≤ 23 °C — exists for water-side and indirect economization, concentrated in December–March and in evening hours, worth an estimated **₱0.65–2.53M/year** in chiller-energy displacement for a 1 MW IT-load facility.

## Why this repo exists

Every number and figure in the paper regenerates from **public weather data** with these scripts, in under a minute. Reproducibility is the paper's credibility claim — run it yourself.

## Repository contents

```
analysis/
  01_screening.py   — canonical screening: 4 economizer screens (S1–S4),
                      WB sensitivity ladder (21–25 °C), monthly/diurnal/annual stats
  02_enso.py        — ENSO classification (NOAA ONI) + Welch t-tests (reproduces p-values)
  04_figures.py     — regenerates all 3 figures (PNG + PDF, 300 dpi)
data/
  (see Data section below — CSV not committed due to size)
```

## Data

Hourly dry-bulb temperature and relative humidity, **NAIA synoptic station (Ninoy Aquino International Airport), WMO 98429, Metro Manila**, 2006–2025, from [Meteostat](https://dev.meteostat.net/) (which aggregates national weather-provider observations, including PAGASA).

Fetch it yourself (Python ≥ 3.9):

```bash
pip install meteostat pandas numpy matplotlib
```

```python
from meteostat import Point, Hourly  # or Stations().nearby for exact station
from datetime import datetime

# station 98429 via Stations API is the canonical reference used in the paper
from meteostat import Stations
stations = Stations()
station = stations.fetch('98429')
df = Hourly(station, datetime(2005,1,1), datetime(2025,1,1),
            parameters={'temperature','humidity'}).fetch()
df.to_csv('naia_manila_2006_2025_hourly.csv')
```

Or download via the Meteostat bulk interface. Place the CSV as `data/naia_manila_2006_2025_hourly.csv`.

## Reproduce everything

```bash
cd analysis
python 01_screening.py   # ~30 s: prints all headline numbers (S1–S4, WB ladder, monthly/diurnal/annual)
python 02_enso.py        # ~5 s:  ENSO classification + Welch tests (El Niño vs La Niña p-values)
python 04_figures.py     # ~30 s: regenerates fig1_monthly, fig2_diurnal, fig3_annual_wb
```

Expected headline output (2006–2024, 165,754 valid hourly records, 99.8% coverage):

| Screen | Definition | Hours/yr |
|---|---|---|
| S1 direct supply-air | DB ≤ 18 °C & WB ≤ 14 °C | ≈ 0 (1 h in 19 yr) |
| **S2 water-side/indirect (headline)** | **DB ≤ 32 °C & WB ≤ 23 °C** | **1,095 (12.6%)** |
| S3 hot-hall mixed-air | DB 15–27 °C & RH ≤ 80% | 1,028 (overlaps S2) |
| S4 A1-like context (NOT free cooling) | DB 15–32 °C & RH 20–80% | 4,439 (50.9%) |

Wet-bulb is computed with the Stull (2011) closed-form approximation (doi:10.1175/JAMC-D-11-0143.1).

## Requirements

```
pandas
numpy
matplotlib
meteostat (data fetch only)
```

## Citation

If you use this analysis or the screening approach, cite the paper:

> Provido, G.A.C. (2026). *Free-Cooling Availability in Philippine Data Centers: A Weather-Data Analysis of Economizer Opportunity in a Tropical Climate.* Preprint. DOI: 10.2139/ssrn.XXXXXXX (to be assigned).

## License & AI disclosure

Code: MIT. The paper discloses that the data pipeline, statistical analysis, and manuscript drafting were prepared with AI assistance (Hermes Agent, Nous Research) under the direction and verification of the author, who is responsible for the integrity of the analysis.

## Contact

Giuseppe Arlo C. Provido — De La Salle University – Dasmariñas, Dept. of Mechanical Engineering.
