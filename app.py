import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Dashboard Configuration
st.set_page_config(page_title="Nigeria Telecom GIS", page_icon="📡", layout="wide")

# 2. Network Mapping for Nigeria (MCC 621)
MNC_MAP = {
    30: "MTN Nigeria",
    60: "Airtel Nigeria",
    20: "Airtel Nigeria",
    50: "Globacom (Glo)",
    2: "9mobile",
    1: "9mobile",
    27: "Smile",
    40: "ntel",
    0: "Other/Fixed"
}

# 3. High-Performance Data Loading
@st.cache_data(ttl=3600) # Cache for 1 hour to speed up the site
def load_data():
    file_name = '621_GIS_ready_2G_3G_4G.csv'
    if not os.path.exists(file_name):
        return None
    
    # Reading the specific columns we need to save memory
    df = pd.read_csv(file_name)
    
    # Mapping columns from your specific CSV structure
    df = df.rename(columns={
        '60': 'MNC',
        '50822': 'Cell_ID',
        'Latitude_abs': 'Latitude',
        'Longitude_abs': 'Longitude',
        'Network_Generation': 'Generation'
    })
    
    # Create Operator names
    df['Operator'] = df['MNC'].map(MNC_MAP).fillna("Unknown")
    return df

# 4. Main Application Logic
def main():
    df = load_data()
    
    if df is None:
        st.error("⚠️ Data file not found. Ensure '621_GIS_ready_2G_3G_4G.csv' is in your GitHub folder.")
        st.stop()

    st.title("📡 Nigeria Infrastructure GIS Dashboard")

    # Sidebar Filters
    st.sidebar.subheader("Filter Settings")
    selected_ops = st.sidebar.multiselect("Operators", df['Operator'].unique(), default=df['Operator'].unique())
    selected_gens = st.sidebar.multiselect("Technology", df['Generation'].unique(), default=df['Generation'].unique())

    # Apply Filters
    f_df = df[(df['Operator'].isin(selected_ops)) & (df['Generation'].isin(selected_gens))]

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Sites", f"{len(f_df):,}")
    m2.metric("4G Sites", f"{len(f_df[f_df['Generation'] == '4G']):,}")
    m3.metric("3G Sites", f"{len(f_df[f_df['Generation'] == '3G']):,}")

    # Visualization Tabs
    tab1, tab2 = st.tabs(["🌍 GIS Map", "📊 Analytics"])

    with tab1:
        # Sampling 20,000 points to ensure the map is fast in the web browser
        plot_df = f_df.sample(min(len(f_df), 20000), random_state=42) if len(f_df) > 20000 else f_df
        
        fig = px.scatter_mapbox(
            plot_df, lat="Latitude", lon="Longitude", color="Operator",
            hover_name="Cell_ID", zoom=5, height=650,
            title="Geographical Distribution (Sampled for Performance)"
        )
        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.bar(f_df['Operator'].value_counts(), title="Site Count by Operator"), use_container_width=True)
        c2.plotly_chart(px.pie(f_df, names='Generation', title="Technology Share"), use_container_width=True)

    # Export Feature
    st.sidebar.divider()
    st.sidebar.download_button("📥 Export Filtered Data", f_df.to_csv(index=False), "telecom_data.csv")

if __name__ == "__main__":
    main()
