import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("Urban Gas Company Dashboard")
st.markdown("---")

# Load data
facility_df = pd.read_csv('data/facility_management.csv')
labor_df = pd.read_csv('data/labor_management.csv')
energy_df = pd.read_csv('data/energy_management.csv')

st.subheader("Data Preview")

tab1, tab2, tab3 = st.tabs(["Facility", "Labor", "Energy"])

with tab1:
    st.write("**Facility Management Data**")
    st.dataframe(facility_df.head(10))
    st.write(f"Total records: {len(facility_df)}")

with tab2:
    st.write("**Labor Management Data**")
    st.dataframe(labor_df.head(10))
    st.write(f"Total records: {len(labor_df)}")

with tab3:
    st.write("**Energy Management Data**")
    st.dataframe(energy_df.head(10))
    st.write(f"Total records: {len(energy_df)}")

st.markdown("---")
st.success("Dashboard loaded successfully!")
