import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Nigeria Telecom GIS Infrastructure",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. OPERATOR MAPPING (MCC 621) ---
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

# --- 3. ROBUST DATA LOADING ---
@st.cache_data(show_spinner="Analyzing Infrastructure Database...")
def load_data():
    file_path = '621_GIS_ready_2G_3G_4G.csv'
    
    # Try multiple encodings to handle special characters or Excel-saved CSVs
    encodings = ['utf-8', 'latin1', 'cp1252']
    
    if not os.path.exists(file_path):
        return None

    for enc in encodings:
        try:
            # Loading data with current encoding
            df = pd.read_csv(file_path, encoding=enc)
            
            # Rename columns based on the specific dataset structure
            df = df.rename(columns={
                '60': 'MNC',
                '50822': 'Cell_ID',
                'Latitude_abs': 'Latitude',
                'Longitude_abs': 'Longitude',
                'Network_Generation': 'Gen'
            })
            
            # Map MNC codes to names and drop invalid coordinates
            df['Operator'] = df['MNC'].map(MNC_MAP).fillna("Other Operator")
            df = df.dropna(subset=['Latitude', 'Longitude'])
            
            return df
        except Exception:
            continue
            
    return None

# --- 4. MAIN APPLICATION LOGIC ---
def main():
    # Load the data
    df = load_data()
    
    if df is None:
        st.error("### ❌ Data Loading Error")
        st.write("Could not decode the CSV file or file is missing. Ensure `621_GIS_ready_2G_3G_4G.csv` is in the repository.")
        st.stop()

    # --- SIDEBAR FILTERS ---
    st.sidebar.image("https://img.icons8.com/fluency/96/antenna.png", width=80)
    st.sidebar.title("Filter Control")
    
    operators = sorted(df['Operator'].unique())
    selected_ops = st.sidebar.multiselect("Network Operators", operators, default=operators)
    
    generations = sorted(df['Gen'].unique())
    selected_gens = st.sidebar.multiselect("Technology Generation", generations, default=generations)

    # Filtering dataframe
    f_df = df[(df['Operator'].isin(selected_ops)) & (df['Gen'].isin(selected_gens))]

    # --- DASHBOARD HEADER & METRICS ---
    st.title("📡 Nigeria Network Infrastructure GIS")
    st.markdown(f"Currently visualizing site data for **{len(f_df):,}** active cell sites.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Cells", f"{len(f_df):,}")
    m2.metric("4G Sites", f"{len(f_df[f_df['Gen'] == '4G']):,}")
    m3.metric("3G Sites", f"{len(f_df[f_df['Gen'] == '3G']):,}")
    m4.metric("Active Operators", f_df['Operator'].nunique())

    # --- VISUALIZATION TABS ---
    tab_map, tab_stats, tab_data = st.tabs(["🌍 GIS Map", "📊 Market Analytics", "📂 Data Explorer"])

    with tab_map:
        st.subheader("Geographical Distribution")
        
        # Optimization: Plotting > 100k points crashes browsers. 
        # We sample up to 25k for the best visual vs performance balance.
        if len(f_df) > 25000:
            st.info("💡 Large dataset detected. Showing a representative sample of 25,000 sites.")
            map_data = f_df.sample(25000, random_state=42)
        else:
            map_data = f_df
        
        fig_map = px.scatter_mapbox(
            map_data, 
            lat="Latitude", 
            lon="Longitude", 
            color="Operator",
            hover_name="Cell_ID",
            hover_data=["Operator", "Gen"],
            zoom=5, 
            height=650,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with tab_stats:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Sites per Operator")
            fig_op = px.bar(f_df['Operator'].value_counts(), color_discrete_sequence=['#2E86C1'])
            st.plotly_chart(fig_op, use_container_width=True)
        with c2:
            st.subheader("Technology Mix")
            fig_pie = px.pie(f_df, names='Gen', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab_data:
        st.subheader("Database Preview")
        st.dataframe(f_df.head(1000), use_container_width=True)
        
        csv_data = f_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Dataset (CSV)",
            data=csv_data,
            file_name="nigeria_telecom_export.csv",
            mime="text/csv"
        )

    st.divider()
    st.caption("Deployment: GitHub / Streamlit Community Cloud | Nigeria GIS Ready Dataset")

if __name__ == "__main__":
    main()
