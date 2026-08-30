# UC Admissions Data

Everything here is public data from the University of California Information
Center and the California Department of Education, cleaned and joined so you can
start analyzing immediately.

Download it before the event. The zip is 7 MB and unzips to about 25 MB.

---

## Load it

```python
import pandas as pd

df = pd.read_csv("bay_area_modeling_table.csv", low_memory=False)
print(df.shape)          # (34311, 65)
df.head()
```

Plain CSV files. You can also double-click them, or open them in Excel or Google
Sheets, though the two big ones are 34,000 rows so a spreadsheet will be slow.

---

## What one row is

**One high school, in one year, at one UC campus.**

So a single school in a single year has ten rows: the nine UC campuses, plus a
tenth row where `campus == "Universitywide"`.

```python
df[(df.high_school == "LYNBROOK HIGH SCHOOL") & (df.fall_term == 2025)][
    ["campus", "applicants", "admits", "admit_rate"]]
```

This is aggregated school-level data. There are **no individual student records**
anywhere in here, so nothing can tell you whether a particular student would get
in. What it can tell you is a great deal about schools, places and pipelines.

---

## Three things that will make your numbers wrong

### 1. "Universitywide" is not the sum of the campuses

It counts **students**, not applications. One person who applied to six campuses
counts once. It means *"admitted to at least one UC."*

Adding the nine campuses together does not give you a systemwide number. It
gives you one about 2.6x too big.

```python
y = df[df.fall_term == 2025]

y[y.campus != "Universitywide"].admits.sum()    # WRONG: 54,991
y[y.campus == "Universitywide"].admits.sum()    # RIGHT: 21,070
```

### 2. Blank counts are redacted, not zero

UC hides any cell with fewer than 5 applicants, or fewer than 3 admits or
enrollees. A blank means *"hidden, or none"* and you cannot tell which.

`.fillna(0)` invents students who do not exist. At Berkeley in 2025, 88% of the
school-level race/ethnicity cells are blank, and 16% of admitted students are
inside them.

### 3. Fall 2021 changed the rules

A court order stopped UC from looking at SAT and ACT scores starting with the
fall 2021 cycle, and a settlement kept it that way through 2025. If you compare
2019 to 2023, you are comparing two different admissions systems. Fall 2020 is
also distorted by COVID.

Two smaller ones: UC's GPA is capped-weighted and **maxes out at 4.40**, so it is
squashed at the top. And California banned race-conscious admissions in 1996
(Prop 209), so race is in this data as a reported outcome, never as an input.

---

## Which file do I open?

| File | Rows | Use it for |
|---|---|---|
| **`bay_area_modeling_table.csv`** | 34,311 | **Start here.** Bay Area high schools x year x campus, with school characteristics attached. |
| `dashboard_data.csv` | 34,311 | Same table plus `expected_admit_rate`, `admit_rate_residual` and `peer_*` comparison columns. Use this if you want a model baseline without fitting one. |
| `uc_admissions_summary_by_ethnicity.csv` | 4,239 | **Anything about race/ethnicity.** UC's own campus totals, 2017-2025. |
| `uc_freshman_admission_by_discipline.csv` | 101 | Admit and yield rates by major area, 9 campuses. Fall 2025 only. |
| `uc_transfer_admission_by_major.csv` | 49 | Named majors (Computer Science vs Data Science, etc). Berkeley transfers, fall 2025 only. |
| `gemini_benchmark_*.csv` | 1,124 / 243 / 2,595 | A school name-matching problem with known answers. See the challenge description. |

> **For race and ethnicity, do not add up the school-level columns.** Redaction
> wipes out small groups. Summing school rows gives about 13 American Indian
> admits in a year when UC's published total is 561. Use the ethnicity file.

---

## Columns

**Who and when**
`fall_term` (2005-2025), `campus`, `high_school`, `city`, `county`,
`cde_district`, `cds_code`, `zip`, `lat`, `lon`, `charter`

**UC outcomes**
`applicants`, `admits`, `enrollees`, `admit_rate`, `yield_rate`,
`applicant_gpa`, `admit_gpa`, `enrollee_gpa`

**Race/ethnicity at school level** (see the warning above)
`app_*`, `adm_*`, `enr_*` for 8 groups, 24 columns total

**What the high school is like**
`cohort_students`, `graduates`, `grad_rate`, `ag_completers`,
`ag_completion_rate`, `frpm_pct` (share on free/reduced lunch),
`caaspp_ela_pct_met`, `caaspp_mathematics_pct_met`

`ag_completion_rate` is the share of graduates who finished the "a-g" courses
UC and CSU require. It is the best single measure of how many students a school
makes UC-eligible in the first place.

**Where the graduates actually went**
`enrolled_uc`, `enrolled_csu`, `enrolled_ccc`, `enrolled_in_state_private`,
`enrolled_out_of_state`, `college_going_rate`, `hs_completers`

**Only in `dashboard_data.csv`**
`expected_admit_rate`, `admit_rate_residual`, `peer_*`

---

## Coverage is not even

Check `.notna()` before you trust a join.

| Columns | Years available |
|---|---|
| UC applicants / admits / enrollees | 2005-2025 |
| Graduation and a-g completion | 2017-2025 |
| Where graduates enrolled | 2015-2023 |
| Free/reduced lunch | 2012-2025, no 2021-22 |
| CAASPP test scores | 2015-2025, no 2020 |

A few other gaps worth knowing:

- **California public high schools only.** No private, out-of-state or
  international source schools.
- The **discipline** and **named-major** files are fall 2025 only. There is no
  trend data for majors, so do not build a question about how a major's admit
  rate has changed.
- About 6% of schools could not be matched to state records and have a blank
  `cds_code`, so they have no school characteristics.

---

## One useful habit

Sum the counts, then divide. Do not average the rates.

```python
# WRONG: a school with 12 applicants counts as much as one with 400
df[df.fall_term == 2025].groupby("campus").admit_rate.mean()

# RIGHT
(df[df.fall_term == 2025].groupby("campus")
   .apply(lambda g: g.admits.sum() / g.applicants.sum()))
```

---

## Where it came from

- [UC Information Center](https://www.universityofcalifornia.edu/about-uc/information-center) — applicants, admits, enrollees, GPA, by school and campus
- [CDE Downloadable Data Files](https://www.cde.ca.gov/ds/ad/downloadabledata.asp) — graduation, a-g completion, poverty, college-going
- [CAASPP Research Files](https://caaspp-elpac.ets.org/caaspp/ResearchFileListSB) — grade 11 test results
