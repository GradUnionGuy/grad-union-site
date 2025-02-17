import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Graduate Program Comparison")

# Check if the DataFrame is in session state
if "df" not in st.session_state:
    st.error("Data not found. Please go back to the main page.")
    st.stop()

df = st.session_state["df"]

# Define satisfaction columns (ensure these column names match your data)
satisfaction_cols = [
    "satisfaction_stipend",
    "satisfaction_work_life",
    "satisfaction_health",
    "satisfaction_employment",
    "satisfaction_grievance",
    "satisfaction_international",
    "satisfaction_parental",
    "satisfaction_housing",
    "satisfaction_harassment",
    "satisfaction_professional_dev"
]

# Convert satisfaction columns to numeric if needed
for col in satisfaction_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    
# --- Step 1: Select Program/Department and Degree(s) ---
selected_department = st.selectbox(
    "Select Program/Department:",
    options=sorted(df["department"].dropna().unique())
)

selected_degrees = st.multiselect(
    "Select Degree(s):",
    options=sorted(df["degree_program"].dropna().unique()),
    
)

# Filter the data by selected department and degree type
filtered_df = df[
    (df["department"] == selected_department) &
    (df["degree_program"].isin(selected_degrees))
]

if filtered_df.empty:
    st.warning("No data available for the selected program/department and degree type(s).")
    st.stop()

# --- Step 2: Select Two Universities for Comparison ---
universities = sorted(filtered_df["university"].dropna().unique())

col_uni_select1, col_uni_select2 = st.columns(2)
with col_uni_select1:
    uni1 = st.selectbox("Select University 1", options=universities, key="uni1")
with col_uni_select2:
    uni2 = st.selectbox("Select University 2", options=universities, key="uni2")

if uni1 == uni2:
    st.warning("Please select two different universities for a meaningful comparison.")

# Create separate DataFrames for each university
df_uni1 = filtered_df[filtered_df["university"] == uni1]
df_uni2 = filtered_df[filtered_df["university"] == uni2]

# --- Step 3: Define Visualization Functions ---

def plot_union_membership(data, university):
    """
    Plot union membership percentage if a union exists.
    Assumes the columns 'union_exists' and 'union_member' are coded as "Yes"/"No".
    """
    # Determine if a union exists (using mode to get the most common response)
    if "union_exists" not in data.columns:
        return None

    union_exists_mode = data["union_exists"].mode().iloc[0] if not data["union_exists"].mode().empty else None
    if union_exists_mode != "Yes":
        st.warning(f"{university} does not have a graduate union.")
        return None
    else:
        total = len(data)
        members = data[data["union_member"] == "Yes"].shape[0]
        percentage = (members / total) * 100 if total > 0 else 0
        fig = px.bar(
            x=["Union Membership"],
            y=[percentage],
            labels={"x": "", "y": "Percentage"},
            title=f"Union Membership Percentage at {university}",
            range_y=[0, 100]
        )
        return fig

def plot_funding_breakdown(data, university):
    """
    Plot a pie chart showing the breakdown of funding sources.
    """
    if "funding_source" not in data.columns:
        return None
    funding_counts = data["funding_source"].value_counts().reset_index()
    funding_counts.columns = ["Funding Source", "Count"]
    fig = px.pie(
        funding_counts,
        names="Funding Source",
        values="Count",
        title=f"Funding Source Breakdown at {university}"
    )
    return fig

def plot_other_job_percentage(data, university):
    """
    Plot a pie chart showing the percentage of students working another job.
    Assumes 'other_job' is coded as "Yes"/"No".
    """
    if "other_job" not in data.columns:
        return None
    job_counts = data["other_job"].value_counts().reset_index()
    job_counts.columns = ["Other Job", "Count"]
    fig = px.pie(
        job_counts,
        names="Other Job",
        values="Count",
        title=f"Working Another Job at {university}"
    )
    return fig

# --- Step 4: Display Visualizations for Each University Side-by-Side ---

st.header("University-Specific Visualizations")

col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    st.subheader(f"{uni1}")
    fig_union1 = plot_union_membership(df_uni1, uni1)
    if fig_union1:
        st.plotly_chart(fig_union1)
    fig_funding1 = plot_funding_breakdown(df_uni1, uni1)
    if fig_funding1:
        st.plotly_chart(fig_funding1)
    fig_job1 = plot_other_job_percentage(df_uni1, uni1)
    if fig_job1:
        st.plotly_chart(fig_job1)

with col_viz2:
    st.subheader(f"{uni2}")
    fig_union2 = plot_union_membership(df_uni2, uni2)
    if fig_union2:
        st.plotly_chart(fig_union2)
    fig_funding2 = plot_funding_breakdown(df_uni2, uni2)
    if fig_funding2:
        st.plotly_chart(fig_funding2)
    fig_job2 = plot_other_job_percentage(df_uni2, uni2)
    if fig_job2:
        st.plotly_chart(fig_job2)

# --- Step 5: Heatmap Comparison of Satisfaction Areas ---

st.header("Satisfaction Areas Comparison (Heatmap)")

def compute_avg_satisfaction(data):
    """Compute the average satisfaction score for each satisfaction area."""
    return data[satisfaction_cols].mean()

avg_uni1 = compute_avg_satisfaction(df_uni1)
avg_uni2 = compute_avg_satisfaction(df_uni2)

# Build a DataFrame where rows are satisfaction categories and columns are universities
satisfaction_df = pd.DataFrame({
    uni1: avg_uni1,
    uni2: avg_uni2
})
satisfaction_df.index.name = "Satisfaction Category"
satisfaction_df.reset_index(inplace=True)

# Create a heatmap using Plotly Express
fig_heatmap = px.imshow(
    satisfaction_df.set_index("Satisfaction Category"),
    color_continuous_scale='Viridis',
    labels=dict(x="University", y="Satisfaction Category", color="Avg Rating"),
    aspect="auto",
    title="Comparison of Satisfaction Areas"
)
st.plotly_chart(fig_heatmap)