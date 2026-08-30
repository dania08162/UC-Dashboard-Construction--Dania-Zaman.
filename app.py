import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("chart_data.csv")

year = st.slider("Fall term", int(df.fall_term.min()), int(df.fall_term.max()), 2025)
filtered = df[df.fall_term == year].copy()
filtered["frpm_pct_display"] = filtered["frpm_pct"] * 100

fig = px.scatter(
    filtered,
    x="frpm_pct_display",
    y="admit_rate_residual",
    size="applicants",
    color="county",
    hover_name="high_school",
    labels={"frpm_pct_display": "% Free/Reduced Lunch", "admit_rate_residual": "Admit Rate vs. Expected"}
)
st.plotly_chart(fig, use_container_width=True)