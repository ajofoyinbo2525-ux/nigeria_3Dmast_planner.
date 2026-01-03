import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 1. Page Config
st.set_page_config(page_title="Nigeria Telecom Planner", page_icon="📡", layout="wide")

# 2. Hardcoded Sample Data (To bypass file loading errors)
# This data is from your actual 621_GIS dataset structure
csv_data = """MNC,Cell_ID,Latitude,Longitude,Gen
60,50822,9.0117,7.6197,2G
60,7301,6.6567,3.2988,2G
60,2917,6.7018,3.2450,2G
30,24441,4.9401,6.3365,2G
30,24663,4.9487,6.3516,2G
50,1011,6.5244,3.3792,3G
50,1012,6.4531,3.3958,3G
2,2022,6.6018,3.3515,4G
30,3033,9.0765,7.3986,4G
30,3044,7.3775,3.9470,4G
"""

# 3. Data Loader
@st.cache_data
def load_data():
    # Attempt to load the real file first
    try:
        # Check if the file exists and is not empty
        if os.path.exists('621_GIS_ready_2G_3G_4G.csv') and os.path.getsize('621_GIS_ready_2G_3G_4G.csv') > 100:
            df = pd.read_csv('621_GIS_ready_2G_3G_4G.csv', encoding='latin1', on_bad_lines='skip')
            
            # Rename columns if they match your original raw format
            if '60' in df.columns:
                df = df.rename(columns={
                    '60': 'MNC', '50822': 'Cell_ID', 
                    'Latitude_abs': 'Latitude', 'Longitude_abs': 'Longitude', 
                    'Network_Generation': 'Gen'
                })
            return df
    except:
        pass # If file fails, fall back to the internal data below
    
    # Fallback to internal data so the app NEVER crashes
    df = pd.read_csv(io.StringIO(csv_data))
    return df

# 4. Operator Mapping
MNC_MAP = {30: "MTN", 60: "Airtel", 20: "Airtel", 50: "Glo", 2: "9mobile", 1: "9mobile"}

# 5. Main App
def main():
    st.title("📡 Telecom GIS Planner (Live Status)")
    
    df = load_data()
    
    # Process Data
    df['Operator'] = df['MNC'].map(MNC_MAP).fillna("Other")
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Display Warning if using Fallback Data
    if len(df) < 50:
        st.warning("⚠️ Currently running on SAMPLE DATA because the main CSV file could not be loaded. Please re-upload '621_GIS_ready_2G_3G_4G.csv' to GitHub.")

    # Visuals
    c1, c2 = st.columns(2)
    c1.metric("Total Sites", len(df))
    c2.metric("Operators", df['Operator'].nunique())

    st.subheader("Map View")
    fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", color="Operator", zoom=5, height=500)
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    import os # Import here to be safe
    main()
