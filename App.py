import streamlit as st
import pandas as pd

st.set_page_config(page_title="Nigeria Mast Planner")

st.title("Nigeria Mast Planner")

df = pd.read_csv("mast_data_final.csv")

st.write("Preview of data:")
st.dataframe(df.head())
