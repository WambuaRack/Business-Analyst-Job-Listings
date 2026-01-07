import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Business Analyst Job Market Dashboard",
    layout="wide"
)

st.title("📊 Business Analyst Job Market Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/business_analyst_jobs.csv")

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Clean company name (remove ratings)
    df["company_name"] = df["company_name"].str.replace(r"\n.*", "", regex=True)

    # Fix founded year
    df["founded"] = df["founded"].replace(-1, np.nan)

    # Easy apply to boolean
    df["easy_apply"] = df["easy_apply"].replace(-1, False)

    # Parse salary
    def parse_salary(s):
        if pd.isna(s):
            return np.nan
        nums = re.findall(r"\d+", s)
        nums = [int(n) for n in nums]
        return np.mean(nums) if nums else np.nan

    df["avg_salary_k"] = df["salary_estimate"].apply(parse_salary)

    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

location = st.sidebar.multiselect(
    "Location",
    sorted(df["location"].dropna().unique())
)

industry = st.sidebar.multiselect(
    "Industry",
    sorted(df["industry"].dropna().unique())
)

ownership = st.sidebar.multiselect(
    "Ownership Type",
    sorted(df["type_of_ownership"].dropna().unique())
)

filtered_df = df.copy()

if location:
    filtered_df = filtered_df[filtered_df["location"].isin(location)]

if industry:
    filtered_df = filtered_df[filtered_df["industry"].isin(industry)]

if ownership:
    filtered_df = filtered_df[filtered_df["type_of_ownership"].isin(ownership)]

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("📌 Total Jobs", len(filtered_df))
col2.metric("🏢 Companies", filtered_df["company_name"].nunique())
col3.metric("🌍 Locations", filtered_df["location"].nunique())
col4.metric("⭐ Avg Rating", round(filtered_df["rating"].mean(), 2))

# ---------------- JOBS BY LOCATION ----------------
st.subheader("📍 Jobs by Location")

loc_df = filtered_df["location"].value_counts().reset_index()
loc_df.columns = ["Location", "Jobs"]

fig_loc = px.bar(
    loc_df,
    x="Location",
    y="Jobs",
    title="Business Analyst Jobs by Location"
)

st.plotly_chart(fig_loc, use_container_width=True)

# ---------------- TOP COMPANIES ----------------
st.subheader("🏢 Top Hiring Companies")

comp_df = filtered_df["company_name"].value_counts().head(10).reset_index()
comp_df.columns = ["Company", "Jobs"]

fig_comp = px.bar(
    comp_df,
    x="Company",
    y="Jobs",
    title="Top 10 Hiring Companies"
)

st.plotly_chart(fig_comp, use_container_width=True)

# ---------------- JOB TITLES ----------------
st.subheader("💼 Job Title Distribution")

title_df = filtered_df["job_title"].value_counts().head(10).reset_index()
title_df.columns = ["Job Title", "Count"]

fig_title = px.bar(
    title_df,
    x="Job Title",
    y="Count",
    title="Most Common Job Titles"
)

st.plotly_chart(fig_title, use_container_width=True)

# ---------------- INDUSTRY & SECTOR ----------------
col1, col2 = st.columns(2)

with col1:
    fig_ind = px.pie(
        filtered_df,
        names="industry",
        title="Jobs by Industry"
    )
    st.plotly_chart(fig_ind, use_container_width=True)

with col2:
    fig_sec = px.pie(
        filtered_df,
        names="sector",
        title="Jobs by Sector"
    )
    st.plotly_chart(fig_sec, use_container_width=True)

# ---------------- SALARY ANALYSIS ----------------
st.subheader("💰 Salary Distribution (Average Estimate)")

salary_df = filtered_df.dropna(subset=["avg_salary_k"])

fig_salary = px.histogram(
    salary_df,
    x="avg_salary_k",
    nbins=25,
    title="Average Salary Estimate ($K)"
)

st.plotly_chart(fig_salary, use_container_width=True)

# ---------------- EASY APPLY ----------------
st.subheader("⚡ Easy Apply Availability")

easy_df = filtered_df["easy_apply"].value_counts().reset_index()
easy_df.columns = ["Easy Apply", "Jobs"]

fig_easy = px.pie(
    easy_df,
    names="Easy Apply",
    values="Jobs",
    title="Easy Apply vs Standard Applications"
)

st.plotly_chart(fig_easy, use_container_width=True)
