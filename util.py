import streamlit as st 
#from shillelagh.backends.apsw.db import connect
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import logging

UNION_PRESENT_OPTIONS = {
    "Yes, we have a union and an active contract/CBA",
    "We have a union, but initial contract/CBA talks are ongoing",
    "We have a union, but our CBA/contract is up for renewal"
}



def load_data():
    scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    gc = gspread.authorize(credentials)
    spreadsheet_id = "1RUXCN-FO311WKMUA4hSeFd7hQ5v0LWb2UglciGNuUcw"
    sheet_name = "Form Responses 1"
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
        "Does your university have a union and collective bargaining agreement (CBA) for graduate students?": "union_exists",
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
        "If you are willing to validate your responses, please provide contact information in this question.": "contact_info",
        "Please describe the state of CBA negotiations (if any) at your university": "cba_state",
        "If you do have a CBA, what year was it initially established?": "cba_year",
        
        "Validated": "validated"
    }

    # Rename columns
    df = df.rename(columns=column_mapping)
    print("Point 0")
    print(df)
    # --- Filter 1: Universities with more than three respondents ---
    df = df.groupby('university').filter(lambda x: len(x) > 3)
    print("Point 1")
    print(df)
    
    # --- Filter 1: Departments with more than three respondents ---
    df = df.groupby('department').filter(lambda x: len(x) > 3)
    print("Point 2")
    print(df)
    
    # --- Filter 2: (University, Department) pairs with more than three respondents ---
    df = df.groupby(['university', 'department']).filter(lambda x: len(x) > 3)
    print("Point 3")
    print(df)
    # --- Filter 3: Ensure each university has multiple valid union membership responses ---
    # Here we assume that a valid response in "union_member" is non-empty.
    # Adjust the condition if your data uses a different convention.
    #df = df.groupby('university').filter(lambda x: (x['union_member'].str.strip() != '').sum() > 2)
    
    # Adding weightage
    df['weight'] = 1
    df.loc[df['validated'].str.strip().str.lower() == 'yes', 'weight'] = 3
    
    return df

def filterDegreeDepartment(degrees, department, df):
    filtered_df = df[
    (df["department"] == department) &
    (df["degree_program"].isin(degrees))
    ]
    return filtered_df

def plot_union_membership_university(data, university):
    """
    Plot union membership percentage at the university level.
    Only plots if the union exists based on the new union_exists options.
    """
    # Filter data for the specified university.
    uni_data = data[data["university"] == university]
    if uni_data.empty or "union_exists" not in uni_data.columns:
        return None

    # Determine the most common response regarding union existence.
    union_exists_mode = uni_data["union_exists"].mode().iloc[0] if not uni_data["union_exists"].mode().empty else None

    # If the mode response is not in our union-present options, return None.
    if union_exists_mode not in UNION_PRESENT_OPTIONS:
        return None

    # Compute total weight and weight for those who are union members.
    total_weight = uni_data["weight"].sum() if "weight" in uni_data.columns else len(uni_data)
    members_weight = (
        uni_data.loc[uni_data["union_member"] == "Yes", "weight"].sum()
        if "weight" in uni_data.columns else uni_data[uni_data["union_member"] == "Yes"].shape[0]
    )

    percentage = (members_weight / total_weight) * 100 if total_weight > 0 else 0

    # Create the bar plot.
    fig = px.bar(
        x=["Union Membership"],
        y=[percentage],
        labels={"x": "", "y": "Percentage"},
        title=f"Union Membership Percentage at {university}",
        range_y=[0, 100]
    )
    return fig



def plot_union_membership_department(data, university, department):
    """
    Plot union membership percentage for a specific department within a university.
    """
    # Filter data for the specified university and department.
    dept_data = data[(data["university"] == university) & (data["department"] == department)]
    if dept_data.empty or "union_exists" not in dept_data.columns:
        return None

    # Determine the mode of union existence responses for the department.
    union_exists_mode = dept_data["union_exists"].mode().iloc[0] if not dept_data["union_exists"].mode().empty else None

    # Only proceed if a union is present.
    if union_exists_mode not in UNION_PRESENT_OPTIONS:
        return None

    # Compute the weighted union membership percentage.
    total_weight = dept_data["weight"].sum() if "weight" in dept_data.columns else len(dept_data)
    members_weight = (
        dept_data.loc[dept_data["union_member"] == "Yes", "weight"].sum()
        if "weight" in dept_data.columns else dept_data[dept_data["union_member"] == "Yes"].shape[0]
    )

    percentage = (members_weight / total_weight) * 100 if total_weight > 0 else 0

    # Create the bar plot.
    fig = px.bar(
        x=["Union Membership"],
        y=[percentage],
        labels={"x": "", "y": "Percentage"},
        title=f"Union Membership Percentage at {university} - {department}",
        range_y=[0, 100]
    )
    return fig

def get_cba_status(data, university):
    """
    Determine the CBA status for a university based on union_exists responses.
    Returns one of: "active CBA", "negotiating CBA", or "No CBA".
    """
    # Filter data for the given university.
    uni_data = data[data["university"] == university]
    if uni_data.empty or "union_exists" not in uni_data.columns:
        return None

    # Determine the most common union_exists response.
    union_status_mode = uni_data["union_exists"].mode().iloc[0] if not uni_data["union_exists"].mode().empty else None

    if union_status_mode == "Yes, we have a union and an active contract/CBA":
        return "active CBA"
    elif union_status_mode in {
        "We have a union, but initial contract/CBA talks are ongoing",
        "We have a union, but our CBA/contract is up for renewal"
    }:
        return "negotiating CBA"
    elif union_status_mode in {
        "We do not have a union, but unionization efforts are ongoing/imminent",
        "We do not have a union, and unionization efforts are not really happening"
    }:
        return "No CBA"
    else:
        return None
    
def plot_funding_breakdown(data, university):
    """
    Plot a pie chart showing the breakdown of funding sources.
    """
    if "funding_source" not in data.columns:
        return None

    funding_counts = (
        data.groupby("funding_source")["weight"]
            .sum()
            .reset_index()
            .rename(columns={"funding_source": "Funding Source", "weight": "Weighted Count"})
    )
    
    fig = px.pie(
        funding_counts,
        names="Funding Source",
        values="Weighted Count",
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
    
    job_counts = (
        data.groupby("other_job")["weight"]
            .sum()
            .reset_index()
            .rename(columns={"other_job": "Other Job", "weight": "Weighted Count"})
    )
    
    fig = px.pie(
        job_counts,
        names="Other Job",
        values="Weighted Count",
        title=f"Working Another Job at {university}"
    )
    return fig


    


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

