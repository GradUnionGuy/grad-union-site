import streamlit as st
import pandas as pd
import plotly.express as px
import util

st.title("Graduate Program Comparison")

# Check if the DataFrame is in session state
if "df" not in st.session_state:
    st.error("Data not found. Please go back to the main page.")
    st.stop()

df = st.session_state["df"]

print(df)


# Convert satisfaction columns to numeric if needed
for col in util.satisfaction_cols:
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
filtered_df = util.filterDegreeDepartment(selected_degrees, selected_department, df)

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


st.header("University-Specific Visualizations")

col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    st.subheader(f"{uni1}")
    # Check CBA status and display appropriate message
    cba_status1 = util.get_cba_status(df_uni1, uni1)
    if cba_status1 == "No CBA":
        st.error(f"{uni1} does not have a graduate union.")
    elif cba_status1 == "negotiating CBA":
        st.warning(f"{uni1} does not have an active CBA; contract negotiations are in progress.")
    
    st.markdown("**University-Wide Union Membership**")
    fig_union_uni1 = util.plot_union_membership_university(df_uni1, uni1)
    if fig_union_uni1:
         st.plotly_chart(fig_union_uni1)
    else:
         st.info(f"No union membership data available at the university level for {uni1}.")
    
    st.markdown("**Department-Specific Union Membership**")
    fig_union_dept1 = util.plot_union_membership_department(df_uni1, uni1, selected_department)
    if fig_union_dept1:
         st.plotly_chart(fig_union_dept1)
    else:
         st.info(f"No union membership data available at the department level for {uni1} in {selected_department}.")
    
    fig_funding1 = util.plot_funding_breakdown(df_uni1, uni1)
    if fig_funding1:
         st.plotly_chart(fig_funding1)
    
    fig_job1 = util.plot_other_job_percentage(df_uni1, uni1)
    if fig_job1:
         st.plotly_chart(fig_job1)

with col_viz2:
    st.subheader(f"{uni2}")
    # Check CBA status and display appropriate message
    cba_status2 = util.get_cba_status(df_uni2, uni2)
    if cba_status2 == "No CBA":
        st.error(f"{uni2} does not have a graduate union.")
    elif cba_status2 == "negotiating CBA":
        st.warning(f"{uni2} does not have an active CBA; contract negotiations are in progress.")
    
    st.markdown("**University-Wide Union Membership**")
    fig_union_uni2 = util.plot_union_membership_university(df_uni2, uni2)
    if fig_union_uni2:
         st.plotly_chart(fig_union_uni2)
    else:
         st.info(f"No union membership data available at the university level for {uni2}.")
    
    st.markdown("**Department-Specific Union Membership**")
    fig_union_dept2 = util.plot_union_membership_department(df_uni2, uni2, selected_department)
    if fig_union_dept2:
         st.plotly_chart(fig_union_dept2)
    else:
         st.info(f"No union membership data available at the department level for {uni2} in {selected_department}.")
    
    fig_funding2 = util.plot_funding_breakdown(df_uni2, uni2)
    if fig_funding2:
         st.plotly_chart(fig_funding2)
    
    fig_job2 = util.plot_other_job_percentage(df_uni2, uni2)
    if fig_job2:
         st.plotly_chart(fig_job2)

# --- Step 5: Heatmap Comparison of Satisfaction Areas ---

st.header("Satisfaction Areas Comparison (Heatmap)")

def compute_avg_satisfaction(data):
    """Compute the average satisfaction score for each satisfaction area."""
    return data[util.satisfaction_cols].mean()

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