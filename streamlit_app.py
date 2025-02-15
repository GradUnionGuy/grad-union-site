import streamlit as st 
from shillelagh.backends.apsw.db import connect
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import logging

#logging.basicConfig(level=logging.DEBUG)


st.title('Graduate Student Union Data Results')

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)


gc = gspread.authorize(credentials)
spreadsheet_id = "1RUXCN-FO311WKMUA4hSeFd7hQ5v0LWb2UglciGNuUcw"  # Replace with your actual spreadsheet ID
sheet_name = "Form Responses 1"  # Replace with your sheet name if different

worksheet = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)


data = worksheet.get_all_values()

df = pd.DataFrame(data)
df.columns = df.iloc[0]  # First row becomes column names
df = df[1:].reset_index(drop=True)  # Drop first row and reset index


column_mapping = {
    "Timestamp": "timestamp",
    "Which university do you attend?": "university",
    "Which (non-listed) university do you attend?": "other_university",
    "Which department are you a part of?": "department",
    "Which (non-listed) department are you a part of?": "other_department",
    "What year of your program are you in?": "year",
    "What is your degree program?": "degree_program",
    "What will be your primary source of funding during your degree?": "funding_source",
    "Do you work another job while in graduate school?": "other_job",
    "Does your university have a union for graduate students?": "union_exists",
    "Are you a part of the grad student union at your university?": "union_member",
    "Is your university graduate union affiliated with any larger unions or organizations?  If so, which one?": "union_affiliation",
    "How active are you in your union?": "union_activity",
    "How effective has your union been in advocating for graduate student needs?": "union_effectiveness",
    "How responsive is your union to member concerns or feedback?": "union_responsiveness",
    "How informed do you feel about the activities and goals of your union?": "union_awareness",
    "What is the state of unionization at your university?": "union_status",
    "Please rank your satisfaction with the following elements of graduate student life at your university [Stipend And Financial Support]": "satisfaction_stipend",
    "Please rank your satisfaction with the following elements of graduate student life at your university [Work-Life Balance]": "satisfaction_work_life",
    "Please rank your satisfaction with the following elements of graduate student life at your university [Health Insurance and Benefits]": "satisfaction_health",
    "Please rank your satisfaction with the following elements of graduate student life at your university [Employment Security]": "satisfaction_employment",
    "Please rank your satisfaction with the following elements of graduate student life at your university [Grievance Handling and Workplace Issues]": "satisfaction_grievance",
    "Please rank your satisfaction with the following elements of graduate student life at your university [International Student Resources]": "satisfaction_international",
    "Please rank your satisfaction with the following elements of graduate student life at your university [Parental Leave and Family Support]": "satisfaction_parental",
    "Please rank your satisfaction with the following elements of graduate student life at your university [Housing Support]": "satisfaction_housing",
    "Please rank your satisfaction with the following elements of graduate student life at your university [Harassment/Discrimination Support]": "satisfaction_harassment",
    "Please rank your satisfaction with the following elements of graduate student life at your university [Professional Development]": "satisfaction_professional_dev",
    "If you are willing to validate your responses, please provide contact information in this question.": "contact_info"
}

# Rename columns
df = df.rename(columns=column_mapping)

# Display the cleaned DataFrame in Streamlit
import streamlit as st
st.write("Cleaned DataFrame:", df.head())


st.title("Graduate Student Union Effectiveness")

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