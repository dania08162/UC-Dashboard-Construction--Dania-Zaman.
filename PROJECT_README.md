# Does Poverty Predict UC Admissions Outcomes?

An interactive Streamlit dashboard exploring whether a Bay Area high school's
poverty level explains how it performs against its *expected* UC admit rate.

**Live app:** [add your Streamlit Cloud URL here]

## The Question

For Bay Area public high schools, after a baseline model already accounts for
applicant GPA, a-g course completion, poverty, and school size, is there
anything left over in how schools out- or under-perform their expected UC
admit rate — and does that leftover gap track with poverty, or vary by county?

## Data

All data comes from the provided `dashboard_data.csv`, itself sourced from the
UC Information Center and the California Department of Education. Each row is
one high school, in one year, aggregated at the school level — there are no
individual student records. The dashboard uses only the `Universitywide` rows
(one school = one row per year) to avoid double-counting schools across the
nine UC campuses.

**Poverty proxy:** we use `frpm_pct` — the share of students at a school
eligible for Free or Reduced-Price Meals — as a standard, widely-used proxy
for school-level poverty. It is not household income, but eligibility is
tied to federal poverty thresholds, and it is the only economic indicator
available in this dataset.

**Outcome measure:** `admit_rate_residual`, provided in the source data, is
the gap between a school's actual UC admit rate and its *expected* admit
rate from a baseline model that already controls for GPA, a-g completion,
poverty, and cohort size. A positive residual means a school admitted more
students than the model predicted; negative means fewer. Because poverty is
already one of the model's inputs, this dashboard is not testing a raw
poverty effect — it shows what's left over *after* that adjustment, which is
a more conservative and more interesting question.

## Known Limitations

- **Bay Area only** (9 counties) — not a statewide sample, no private or
  out-of-state schools.
- **2022 is excluded** — that year's `frpm_pct` records have a documented gap
  in the source data, so the residual could not be computed.
- **Small samples create noise.** Any school-level result based on fewer than
  ~10 applicants is flagged in the dashboard and should be read with caution.
- **Correlation, not causation.** Any relationship shown here is
  observational; it does not establish that poverty causes admissions
  outcomes to differ.

## Dashboard Features

- Year and county filters
- Poverty vs. outcome scatter plot, with school search-and-highlight
- Animated year-by-year time-lapse (2017–2025)
- County-level comparison and single-school trend lines
- "Matched pairs" tool comparing similar-poverty schools with different outcomes
- "Hidden gems" leaderboard of high-poverty schools most beating expectations
- Auto-generated year-over-year narrative summary
- CSV export of the currently filtered view

## Tech Stack

Python, Streamlit, Plotly, pandas.

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
