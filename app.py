import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="Telecom GIS Planner", page_icon="📡", layout="wide")

# 2. Operator Mapping (Nigeria MCC 621)
MNC_MAP = {
    30: "MTN Nigeria",
    60: "Airtel Nigeria",
    20: "Airtel Nigeria",
    50: "Globacom (Glo)",
    2: "9mobile",
    1: "9mobile",
    0: "Fixed/Other"
}

@st.cache_data
def load_data():
    # MANDATORY: Ensure this filename matches exactly what you uploaded to GitHub
    file_path = '621_GIS_ready_2G_3G_4G.csv'
    
    if not os.path.exists(file_path):
        st.error(f"File '{file_path}' not found in GitHub repository.")
        return None

    try:
        # Using latin1 and engine='python' to bypass any "bad" characters
        df = pd.read_csv(file_path, encoding='latin1', engine='python', on_bad_lines='skip')
        
        # Checking if it's actually a webpage/HTML file by mistake
        if 'html' in str(df.columns[0]).lower() or '<!doctype' in str(df.columns[0]).lower():
            st.error("Error: The file uploaded is a Webpage (HTML), not a real CSV. Please upload the raw data file.")
            return None

        # Standardizing columns
        df = df.rename(columns={
            '60': 'MNC',
            '50822': 'Cell_ID',
            'Latitude_abs': 'Latitude',
            'Longitude_abs': 'Longitude',
            'Network_Generation': 'Gen'
        })

        # Data Cleanup
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df['Operator'] = df['MNC'].map(MNC_MAP).fillna("Other")
        
        return df.dropna(subset=['Latitude', 'Longitude'])
    except Exception as e:
        st.error(f"Loading Error: {e}")
        return None

# 3. Application UI
def main():
    st.title("📡 Nigeria Telecom Infrastructure Planner")
    
    df = load_data()
    if df is None:
        st.info("💡 Tip: Ensure you are using '621_GIS_ready_2G_3G_4G.csv' and not a saved webpage.")
        st.stop()

    # Sidebar
    st.sidebar.header("Navigation")
    ops = st.sidebar.multiselect("Network Operator", sorted(df['Operator'].unique()), default=df['Operator'].unique())
    gens = st.sidebar.multiselect("Technology", sorted(df['Gen'].unique()), default=df['Gen'].unique())

    # Filtering
    f_df = df[(df['Operator'].isin(ops)) & (df['Gen'].isin(gens))]

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sites", f"{len(f_df):,}")
    c2.metric("4G Sites", f"{len(f_df[f_df['Gen'] == '4G']):,}")
    c3.metric("3G Sites", f"{len(f_df[f_df['Gen'] == '3G']):,}")

    # Map Display
    st.subheader("🌍 Geographical Site Distribution")
    # Sample data to 25k points to keep the live web domain fast
    map_df = f_df.sample(min(len(f_df), 25000)) if len(f_df) > 25000 else f_df
    
    fig = px.scatter_mapbox(
        map_df, lat="Latitude", lon="Longitude", color="Operator",
        hover_name="Cell_ID", zoom=5, height=700,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
