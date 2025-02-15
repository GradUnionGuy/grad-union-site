import streamlit as st
from shillelagh.backends.apsw.db import connect
import pandas as pd
import numpy as np

st.title('Uber pickups in NYCAA')



connection = connect(":memory:",
                     adapter_kwargs = {
                            "gsheetsapi": { 
                            "service_account_info":  st.secrets["gcp_service_account"] 
                                    }
                                        }
                        )