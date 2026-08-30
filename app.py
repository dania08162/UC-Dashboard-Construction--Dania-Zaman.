import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UC Admissions & Poverty Dashboard", layout="wide")

df = pd.read_csv("chart_data.csv")

st.title("Does Poverty Predict UC Admissions Outcomes?")
st.markdown(
    "**Question:** For Bay Area high schools, does a school's poverty rate "
    "(% on free/reduced lunch) predict whether it over- or under-performs its "
    "*expected* UC admit rate — after controlling for GPA, a-g completion, and school size?"
)

# ---- Sidebar controls ----
years = sorted(df.fall_term.unique())
year = st.sidebar.slider("Fall term", int(min(years)), int(max(years)), 2025)

st.sidebar.caption(
    "Note: 2022 has no data — the free/reduced-lunch figures the model relies on "
    "have a documented gap that year."
)

filtered = df[df.fall_term == year].copy()
filtered["frpm_pct_display"] = filtered["frpm_pct"] * 100

# ---- KPI row ----
col1, col2, col3 = st.columns(3)

corr = filtered["frpm_pct"].corr(filtered["admit_rate_residual"])
high_pov = filtered[filtered.frpm_pct >= filtered.frpm_pct.median()]
low_pov = filtered[filtered.frpm_pct < filtered.frpm_pct.median()]

col1.metric("Schools shown", len(filtered))
col2.metric("Poverty ↔ Residual correlation", f"{corr:.2f}")
col3.metric(
    "Avg residual: high- vs low-poverty schools",
    f"{high_pov.admit_rate_residual.mean():+.2f} vs {low_pov.admit_rate_residual.mean():+.2f}"
)

st.divider()

# ---- Main scatter ----
st.subheader(f"Poverty rate vs. admissions outperformance — Fall {year}")
fig = px.scatter(
    filtered,
    x="frpm_pct_display",
    y="admit_rate_residual",
    size="applicants",
    color="county",
    hover_name="high_school",
    labels={"frpm_pct_display": "% Free/Reduced Lunch", "admit_rate_residual": "Admit Rate vs. Expected"},
)
fig.add_hline(y=0, line_dash="dash", line_color="gray")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---- County comparison + school drill-down side by side ----
left, right = st.columns(2)

with left:
    st.subheader(f"Average residual by county — Fall {year}")
    county_avg = (
        filtered.groupby("county")["admit_rate_residual"]
        .mean()
        .sort_values()
        .reset_index()
    )
    bar_fig = px.bar(
        county_avg,
        x="admit_rate_residual",
        y="county",
        orientation="h",
        labels={"admit_rate_residual": "Avg Admit Rate vs. Expected", "county": ""},
    )
    bar_fig.add_vline(x=0, line_dash="dash", line_color="gray")
    st.plotly_chart(bar_fig, use_container_width=True)

with right:
    st.subheader("School trend over time")
    school_list = sorted(df.high_school.unique())
    default_idx = school_list.index("MISSION SAN JOSE HIGH SCHOOL") if "MISSION SAN JOSE HIGH SCHOOL" in school_list else 0
    school = st.selectbox("Pick a school", school_list, index=default_idx)

    school_data = df[df.high_school == school].sort_values("fall_term")
    line_fig = px.line(
        school_data,
        x="fall_term",
        y="admit_rate_residual",
        markers=True,
        labels={"fall_term": "Fall term", "admit_rate_residual": "Admit Rate vs. Expected"},
    )
    line_fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(line_fig, use_container_width=True)

st.caption(
    "Data: UC Information Center & California Dept. of Education, aggregated at the "
    "school level. Bay Area public high schools only (9 counties). No individual "
    "student records. 'Expected admit rate' is a model baseline controlling for "
    "applicant GPA, a-g completion rate, poverty, and cohort size."
)