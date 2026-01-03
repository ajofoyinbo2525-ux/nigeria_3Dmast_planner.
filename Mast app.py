import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mast Data Dashboard", layout="wide")

st.title("📡 Mast Data Analysis Dashboard")
st.markdown("---")

def load_data(file_path):
    # This block automatically fixes the 'invalid start byte' error
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            return df, enc
        except Exception:
            continue
    return None, None

# File path matches your filename
file_path = 'mast_data_final.csv'
df, used_encoding = load_data(file_path)

if df is not None:
    st.sidebar.success(f"Data loaded via {used_encoding}")
    
    # Metrics
    m1, m2 = st.columns(2)
    m1.metric("Total Records", len(df))
    m2.metric("Total Columns", len(df.columns))
    
    # Data View
    st.subheader("Data Preview")
    st.dataframe(df, use_container_width=True)

    # Automated Visuals
    st.subheader("Visual Analysis")
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        col = st.selectbox("Select column to group by:", cat_cols)
        fig = px.bar(df[col].value_counts(), title=f"Distribution of {col}")
        st.plotly_chart(fig, use_container_width=True)
    
    # Map (Auto-detects Latitude/Longitude)
    lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
    lon_col = next((c for c in df.columns if 'lon' in c.lower()), None)
    if lat_col and lon_col:
        st.subheader("📍 Site Map Locations")
        st.map(df[[lat_col, lon_col]])
else:
    st.error("Error: 'mast_data_final.csv' is missing or corrupted.")
    st.info("Make sure you upload your CSV file to the same folder as this script.")
