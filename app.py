import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UC Admissions & Poverty Dashboard", layout="wide")

df = pd.read_csv("chart_data.csv")

# ---------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------
st.title("📊 Does Poverty Predict UC Admissions Outcomes?")

st.markdown(
    """
    Every Bay Area high school has an **expected UC admit rate** — a prediction based on
    the school's grades, course completion, and size. This tool compares that prediction
    to what **actually** happened, and asks: *does a school's poverty level explain the gap?*

    Use the year slider on the left to explore different years, then scroll down to compare
    real schools side by side.
    """
)

st.divider()

# ---------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------
st.sidebar.header("⚙️ Controls")
years = sorted(df.fall_term.unique())
year = st.sidebar.slider(
    "Choose a year",
    int(min(years)), int(max(years)), 2025,
    help="2022 is skipped — that year's poverty data has a known gap in the source records."
)

filtered = df[df.fall_term == year].copy()
filtered["frpm_pct_display"] = (filtered["frpm_pct"] * 100).round(1)
filtered["admit_rate_residual"] = filtered["admit_rate_residual"].round(3)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **How to read "residual":**

    - 🟢 **Positive** = school admitted *more* students than expected
    - 🔴 **Negative** = school admitted *fewer* students than expected

    "Expected" already accounts for GPA, course completion, poverty, and school size —
    so this measures what's left over *after* those factors are considered.
    """
)

# ---------------------------------------------------------------
# KPI ROW — plain language framing
# ---------------------------------------------------------------
st.subheader(f"Quick summary — Fall {year}")

corr = filtered["frpm_pct"].corr(filtered["admit_rate_residual"])
high_pov = filtered[filtered.frpm_pct >= filtered.frpm_pct.median()]
low_pov = filtered[filtered.frpm_pct < filtered.frpm_pct.median()]

col1, col2, col3 = st.columns(3)
col1.metric("Schools in this view", len(filtered))
col2.metric(
    "Poverty ↔ Outcome link",
    f"{corr:+.2f}",
    help="Ranges from -1 to +1. Near 0 means poverty barely explains the gap. "
         "Positive means higher-poverty schools tend to outperform expectations."
)
col3.metric(
    "Higher-poverty schools' avg. outcome",
    f"{high_pov.admit_rate_residual.mean():+.1%}",
    delta=f"{(high_pov.admit_rate_residual.mean() - low_pov.admit_rate_residual.mean()):+.1%} vs. lower-poverty schools"
)

st.caption(
    "💡 In plain terms: a correlation near 0 means a school's poverty level tells you "
    "almost nothing about whether it beats or misses its predicted admit rate."
)

st.divider()

# ---------------------------------------------------------------
# MAIN SCATTER
# ---------------------------------------------------------------
st.subheader("Every school, plotted")
st.markdown(
    "Each dot is one high school. **Further right** = more students in poverty. "
    "**Above the dashed line** = beat expectations. **Bigger dot** = more applicants "
    "(so it's a more reliable data point)."
)

fig = px.scatter(
    filtered,
    x="frpm_pct_display",
    y="admit_rate_residual",
    size="applicants",
    color="county",
    hover_name="high_school",
    labels={
        "frpm_pct_display": "% of Students in Poverty (Free/Reduced Lunch)",
        "admit_rate_residual": "Admissions Outcome vs. Expected",
    },
)
fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.6,
              annotation_text="Exactly as expected", annotation_position="bottom right")
fig.update_layout(
    yaxis_tickformat=".0%",
    legend_title_text="County",
    font=dict(size=13),
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------------------
# COUNTY COMPARISON + SCHOOL DRILL-DOWN
# ---------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Which counties beat expectations?")
    st.markdown("Average outcome for all schools in each county, this year.")

    county_avg = (
        filtered.groupby("county")["admit_rate_residual"]
        .mean()
        .sort_values()
        .reset_index()
    )
    county_avg["color"] = county_avg["admit_rate_residual"].apply(
        lambda x: "Above expected" if x >= 0 else "Below expected"
    )

    bar_fig = px.bar(
        county_avg,
        x="admit_rate_residual",
        y="county",
        orientation="h",
        color="color",
        color_discrete_map={"Above expected": "#2ca02c", "Below expected": "#d62728"},
        labels={"admit_rate_residual": "Avg. Outcome vs. Expected", "county": ""},
    )
    bar_fig.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.6)
    bar_fig.update_layout(xaxis_tickformat=".0%", showlegend=False, font=dict(size=13))
    st.plotly_chart(bar_fig, use_container_width=True)

with right:
    st.subheader("Track one school over time")
    st.markdown("Pick a school to see whether it's consistently over- or under-performing.")

    school_list = sorted(df.high_school.unique())
    default_idx = school_list.index("MISSION SAN JOSE HIGH SCHOOL") if "MISSION SAN JOSE HIGH SCHOOL" in school_list else 0
    school = st.selectbox("School", school_list, index=default_idx, label_visibility="collapsed")

    school_data = df[df.high_school == school].sort_values("fall_term").copy()
    school_data["admit_rate_residual"] = school_data["admit_rate_residual"]

    line_fig = px.line(
        school_data,
        x="fall_term",
        y="admit_rate_residual",
        markers=True,
        labels={"fall_term": "Year", "admit_rate_residual": "Outcome vs. Expected"},
    )
    line_fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.6)
    line_fig.update_layout(yaxis_tickformat=".0%", font=dict(size=13))
    st.plotly_chart(line_fig, use_container_width=True)

st.divider()

# ---------------------------------------------------------------
# MATCHED PAIRS FINDER
# ---------------------------------------------------------------
st.subheader("🔍 Find two similar schools with different outcomes")
st.markdown(
    """
    Two schools can have **the exact same poverty level** and still land on opposite
    ends of the outcome scale. Pick a poverty level below to see real examples from
    the selected year.
    """
)

with st.expander("Adjust search settings", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        target_pct = st.slider("Poverty level to search near", 0, 100, 50, step=5, format="%d%%") / 100
    with c2:
        tolerance = st.slider("How close counts as 'similar'?", 1, 20, 5, step=1, format="±%d pts") / 100

matched = filtered[
    (filtered.frpm_pct >= target_pct - tolerance) &
    (filtered.frpm_pct <= target_pct + tolerance)
].dropna(subset=["admit_rate_residual"])

if len(matched) < 2:
    st.warning(
        f"Only {len(matched)} school(s) found that close to {target_pct:.0%} poverty in {year}. "
        "Try a wider search range or a different year."
    )
else:
    n_show = min(3, max(1, len(matched) // 2))
    best = matched.nlargest(n_show, "admit_rate_residual")
    worst = matched.nsmallest(n_show, "admit_rate_residual")

    display_cols = {
        "high_school": "School",
        "county": "County",
        "frpm_pct_display": "% in Poverty",
        "admit_rate_residual": "Outcome vs. Expected",
        "applicants": "# Applicants",
    }

    pair_left, pair_right = st.columns(2)

    with pair_left:
        st.markdown(f"### 🟢 Beat expectations")
        show = best.rename(columns=display_cols)[list(display_cols.values())]
        st.dataframe(
            show.style.format({"% in Poverty": "{:.0f}%", "Outcome vs. Expected": "{:+.1%}"}),
            hide_index=True, use_container_width=True
        )

    with pair_right:
        st.markdown(f"### 🔴 Missed expectations")
        show = worst.rename(columns=display_cols)[list(display_cols.values())]
        st.dataframe(
            show.style.format({"% in Poverty": "{:.0f}%", "Outcome vs. Expected": "{:+.1%}"}),
            hide_index=True, use_container_width=True
        )

    gap = best.admit_rate_residual.mean() - worst.admit_rate_residual.mean()
    st.success(
        f"**Takeaway:** at around {target_pct:.0%} poverty, the best and worst performers "
        f"differ by **{gap:.1%}** in admissions outcome — real schools with nearly identical "
        f"poverty levels, landing in very different places. ({len(matched)} schools matched "
        f"this search overall.)"
    )

st.divider()

with st.expander("📋 About this data"):
    st.markdown(
        """
        - **Source:** UC Information Center + California Dept. of Education, joined at the school level.
        - **Coverage:** Bay Area public high schools only (9 counties) — not statewide, no private schools.
        - **No individual students:** every number here is a school-level aggregate.
        - **"Expected admit rate"** comes from a baseline model that already accounts for
          applicant GPA, course completion (a-g rate), poverty, and cohort size — so this
          dashboard shows what's *left over* after those factors, not a raw poverty effect.
        - **2022 is missing** because that year's poverty (free/reduced lunch) records have a
          documented gap in the source data.
        """
    )