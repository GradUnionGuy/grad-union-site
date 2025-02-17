import streamlit as st 
#from shillelagh.backends.apsw.db import connect
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import logging
import util

#logging.basicConfig(level=logging.DEBUG)

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.title('Graduate Student Unions - A Survey (Results)')

@st.cache_data
def initialize():
    df = util.load_data()
    

# Load data and store in session state
if "df" not in st.session_state:
    st.session_state["df"] = util.load_data()


st.write("Navigate to **Page 1** in the sidebar to explore the data!")







