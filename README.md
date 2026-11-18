# Free-Cooling Availability for Metro Manila Data Centers
### A Weather-Data Analysis of Economizer Opportunity in a Tropical Climate

**Giuseppe Arlo C. Provido** and **Gian Carlo M. Bongcales**
Department of Mechanical Engineering, De La Salle University - Dasmarinas, Cavite, Philippines

Preprint: SSRN, posted 18 November 2026
DOI: [10.2139/ssrn.7695618](https://doi.org/10.2139/ssrn.7695618)

**The finding in one sentence.** Direct air-side free cooling is effectively absent in Metro Manila - one qualifying hour in nineteen years of hourly records - but a wet-bulb-bounded **water-side / evaporative** window does exist, averaging **1,095 hours per year (12.6%)**, concentrated in December-March and in the pre-dawn hours of the diurnal cycle.

## What this repository is

The companion code for the preprint. Every computed number in the paper and all three figures regenerate from these six scripts against the public Meteostat record for NAIA station WMO 98429.

Reproducibility is the paper's credibility claim. Run it yourself.

## Repository contents

```
analysis/
  01_screening.py         canonical screening: S1-S4 screens, WB sensitivity ladder
                          (21-25 C), monthly / diurnal / annual statistics
  02_enso.py              NOAA ONI-based ENSO classification + Welch t-tests
  04_figures.py           regenerates fig1_monthly, fig2_diurnal, fig3_annual_wb
  06_uncertainty.py       sensitivity of S2 hours to Stull (2011) WB error bands
  07_load_weighting.py    load-weighted energy and cost bounds for Section 5.1
  08_extended_checks.py   WB ladder, S2/S3 overlap, diurnal peak, RH>=100 subset,
                          top/bottom years
CITATION.cff              citation metadata
data/                     place the CSV here (not committed, see below)
```

Generated outputs are committed so the expected results are visible without fetching data: `summary_stats.txt`, `extended_checks.txt`, `uncertainty_results.md`, `load_weighting_results.md`, and `fig1-3` (PNG + PDF, 300 dpi).

## Data

Hourly dry-bulb temperature and relative humidity for the **NAIA synoptic station (Ninoy Aquino International Airport), WMO 98429, Metro Manila**, 2006-2025, from [Meteostat](https://dev.meteostat.net/), which aggregates national weather-provider observations including PAGASA.

**Timestamps are UTC.** The Meteostat hourly archive stores timestamps in UTC, and this was verified against station physics rather than assumed: in the raw record the dry-bulb maximum falls at hour 05 and the minimum at hour 22, which correspond to 13:00 and 06:00 local. Every script therefore applies a fixed `+8 h` shift to Philippine Standard Time (no DST) before any hourly, daily, or annual aggregation. Skipping that shift does not change the headline annual total, but it does distort the diurnal curve and the per-year buckets by eight hours.

Fetch the CSV yourself (Python >= 3.9):

```bash
pip install meteostat pandas numpy
```

```python
from datetime import datetime
from meteostat import Stations, Hourly

station = Stations().fetch('98429')
df = Hourly(station, datetime(2005, 1, 1), datetime(2025, 1, 1),
            parameters={'temperature', 'humidity'}).fetch()
df.to_csv('naia_manila_2006_2025_hourly.csv')
```

Place it at `data/naia_manila_2006_2025_hourly.csv`. Rename the columns to `time,temp,rhum` if your export differs.

## Reproduce everything

```bash
pip install -r requirements.txt
cd analysis
python 01_screening.py        # ~5 s   all headline screens and statistics
python 02_enso.py             # ~10 s  ENSO groups and Welch tests
python 04_figures.py          # ~15 s  fig1-3, PNG + PDF at 300 dpi
python 06_uncertainty.py      # ~10 s  WB error-band sensitivity
python 07_load_weighting.py   # ~5 s   load-weighted energy and cost bounds
python 08_extended_checks.py  # ~5 s   ladder, overlap, diurnal, year rankings
```

## Expected output

Dataset accounting, 2006-2024: 166,560 calendar hours (five leap days), 166,006 rows archived by the provider, 554 calendar hours with no archived row, 260 archived rows missing temperature or humidity, leaving **165,746 valid paired observations** (99.5% of calendar hours, 99.8% of archived rows). No imputation.

| Screen | Definition | Hours | Hours/yr | % of valid |
|---|---|---:|---:|---:|
| S1 direct supply-air | DB <= 18 C and WB <= 14 C | 1 | 0 | 0.0% |
| **S2 water-side / evaporative (headline)** | **DB <= 32 C and WB <= 23 C** | **20,807** | **1,095** | **12.6%** |
| S3 hot-hall mixed-air | DB 15-27 C and RH <= 80% | 19,526 | 1,028 | 11.8% |
| S4 A1-like meteorological (context only) | DB 15-32 C and RH 20-80% | 84,340 | 4,439 | 50.9% |

S2 detail: annual range 672 h (2010) to 1,857 h (2015), mean 1,095 h/yr, sample SD 406 h. The 22:00-06:59 block carries 53% of eligible hours; the diurnal peak is 05:00 (77.2 h/yr) and the trough is 14:00 (15.6 h/yr).

WB ladder, DB <= 32 C: 21 C 3,705 h (195/yr), 22 C 9,554 h (503/yr), 23 C 20,807 h (1,095/yr), 24 C 38,649 h (2,034/yr), 25 C 67,606 h (3,558/yr).

S2 and S3 overlap for 12,729 hours (669.9/yr); S3 contributes 6,797 hours (357.7/yr) beyond S2.

Load-weighted, at the assumed 220 kW compressor input: enterprise profile 714 h/yr (65.2% of flat), hyperscale 916 h/yr (83.6% of flat), flat 1,095 h/yr. Central 50% displacement gives ₱0.94M (enterprise), ₱1.21M (hyperscale), ₱1.45M (flat) per year at the central ₱12/kWh rate.

ENSO: El Nino n=7 mean 1,148 h (SD 463), La Nina n=8 mean 1,061 h (SD 347), neutral n=4 mean 1,070 h (SD 520); Welch EN vs LN p=0.69, EN vs neutral p=0.81. No statistically detectable association in a 19-year sample.

## What this analysis does not claim

- **S4 is context, not free cooling.** Outdoor air sits within A1-like conditions about half the year, but supply air must be cooler than the hall return, so this is not economizer availability.
- **Indirect air-to-air applicability is not quantified.** The WB screen bounds water-side / evaporative economization only; indirect air-to-air needs separate temperature, enthalpy, and exchanger-effectiveness modelling.
- **The 220 kW compressor input is an independent illustrative assumption**, not derived from PUE or COP and not a plant measurement. The MWh and peso figures are scenario bounds, not simulated savings.
- **One station.** NAIA is a deliberate synoptic reference for the Metro Manila-Cavite corridor, not a stand-in for every facility or urban microclimate.

## Citation

If you use this code or the screening approach, cite the preprint:

```bibtex
@misc{provido2026freecooling,
  title  = {Free-Cooling Availability for Metro Manila Data Centers:
            A Weather-Data Analysis of Economizer Opportunity in a Tropical Climate},
  author = {Provido, Giuseppe Arlo C. and Bongcales, Gian Carlo M.},
  year   = {2026},
  month  = {nov},
  note   = {Preprint, SSRN},
  doi    = {10.2139/ssrn.7695618},
  url    = {https://doi.org/10.2139/ssrn.7695618}
}
```

Machine-readable metadata is in `CITATION.cff`.

## License and AI disclosure

Code released under the MIT License (see `LICENSE`). The paper itself is licensed CC BY-NC-ND 4.0.

The manuscript discloses that the data pipeline, statistical analysis, and drafting were prepared with AI assistance under the direction and verification of the authors, who are responsible for the integrity of the analysis.

## Contact

Giuseppe Arlo C. Provido - Department of Mechanical Engineering, De La Salle University - Dasmarinas
gac.provido@gmail.com
