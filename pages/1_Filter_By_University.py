import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Filter By University")

# Check if the DataFrame is in session state
if "df" not in st.session_state:
    st.error("Data not found. Please go back to the main page.")
    st.stop()

df = st.session_state["df"]

selected_university = st.selectbox(
    "Select a University:", 
    options=df["university"].unique()
)

filtered_df = df[df["university"] == selected_university]
filtered_df["union_effectiveness"] = pd.to_numeric(filtered_df["union_effectiveness"], errors="coerce")

avg_effectiveness = (
    filtered_df.groupby("degree_program")["union_effectiveness"]
    .mean()
    .reset_index()
)

avg_effectiveness.columns = ["Degree Program", "Average Effectiveness"]

# Create a bar chart with two colors for PhD and Master's
fig = px.bar(
    avg_effectiveness, 
    x="Degree Program", 
    y="Average Effectiveness", 
    color="Degree Program", 
    color_discrete_map={"PhD": "blue", "Master's": "green"},
    title=f"Union Effectiveness at {selected_university}",
    labels={"Average Effectiveness": "Avg. Rating (1-5)", "Degree Program": "Degree Program"},
    height=500
)

st.plotly_chart(fig)