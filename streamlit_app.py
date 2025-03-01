import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import logging
import util

# Set the page configuration
st.set_page_config(
    page_title="Graduate Student Unions - Survey Results",
    page_icon="📊",
    layout="wide"
)

# Page title
st.title("Graduate Student Unions - Survey Results")

# Introduction section
st.write(
    """
    Welcome to the results of the Graduate Student Union survey! This dashboard presents key insights 
    from the survey data, providing an overview of graduate student experiences with unionization.
    
    You can explore the data through the visualizations available in the sidebar, which offer 
    interactive charts and insights into various aspects of the survey results.
    
    **Interested in participating?** [https://forms.gle/BsuyBrG4s1k4PLcc6](#)
    
    **Want to contribute?** Email gradunionguy@gmail.com or [Contribute via GitHub](https://github.com/gradunionguy/grad-union-site/)
    
    We’re continuously updating this dashboard. Be sure to check back periodically for the latest 
    insights and features.
    
    Have questions or suggestions? Feel free to reach out via email at gradunionguy@gmail.com.
    """
)

# Caching data loading
@st.cache_data
def initialize():
    df = util.load_data()

# Load data and store in session state
if "df" not in st.session_state:
    st.session_state["df"] = util.load_data()

# Additional sections for more context
st.write(
    """
    ---
    ### Explore the Data
    Use the tabs on the left sidebar to interact with visualizations, filter data, and uncover 
    interesting patterns from the survey. You can explore various dimensions such as student 
    demographics, university characteristics, and unionization efforts.
    
    This project is a work in progress, and we're continuously refining it. Stay tuned for updates, 
    and if you're interested in contributing, we'd love to collaborate!
    
    [Contribute on GitHub](https://github.com/your-repo-link)
    """
)
