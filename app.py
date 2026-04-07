import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set page configuration
st.set_page_config(page_title="PrintIQ | Material Selector", layout="wide")

# File to store our materials permanently
DATA_FILE = "printiq_materials.csv"

# --- 1. Data Management ---
def load_data():
    """Loads material data from CSV, or creates a default one if it doesn't exist."""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Default starter data extracted from your original HTML
        default_data = [
            {"Material": "PLA", "HDT (°C)": 80.0, "Tensile Strength (MPa)": 56.0, "Tensile Modulus (GPa)": 3.46, "Max Price/kg (USD)": 25.0, "Technology": "FDM", "Bed Temp (°C)": 60, "Hotend Temp (°C)": 200, "Flexible": "false", "Link": "https://www.3dxtech.com/product/ecomax-pla/"},
            {"Material": "ABS", "HDT (°C)": 95.0, "Tensile Strength (MPa)": 42.0, "Tensile Modulus (GPa)": 2.34, "Max Price/kg (USD)": 25.0, "Technology": "FDM", "Bed Temp (°C)": 100, "Hotend Temp (°C)": 235, "Flexible": "false", "Link": "https://www.3dxtech.com/product/3dxtech-abs/"},
            {"Material": "PEEK", "HDT (°C)": 182.0, "Tensile Strength (MPa)": 100.0, "Tensile Modulus (GPa)": 3.72, "Max Price/kg (USD)": 588.0, "Technology": "FDM", "Bed Temp (°C)": 140, "Hotend Temp (°C)": 400, "Flexible": "false", "Link": "https://www.3dxtech.com/product/thermax-peek/"},
            {"Material": "ULTEM 1010", "HDT (°C)": 207.0, "Tensile Strength (MPa)": 95.0, "Tensile Modulus (GPa)": 2.3, "Max Price/kg (USD)": 278.0, "Technology": "FDM", "Bed Temp (°C)": 140, "Hotend Temp (°C)": 410, "Flexible": "false", "Link": "https://www.prusa3d.com/product/prusament-pei-1010/"},
            {"Material": "Formlabs Rigid 10K", "HDT (°C)": 163.0, "Tensile Strength (MPa)": 65.0, "Tensile Modulus (GPa)": 10.0, "Max Price/kg (USD)": 299.0, "Technology": "SLA", "Bed Temp (°C)": 0, "Hotend Temp (°C)": 0, "Flexible": "false", "Link": "https://formlabs.com/store/materials/rigid-10k-resin/"},
            {"Material": "Formlabs PA12", "HDT (°C)": 177.0, "Tensile Strength (MPa)": 47.0, "Tensile Modulus (GPa)": 1.95, "Max Price/kg (USD)": 110.0, "Technology": "SLS", "Bed Temp (°C)": 0, "Hotend Temp (°C)": 0, "Flexible": "false", "Link": "https://formlabs.com/store/materials/nylon-12-white-powder/"}
        ]
        df = pd.DataFrame(default_data)
        df.to_csv(DATA_FILE, index=False)
        return df

def save_data(df):
    """Saves the dataframe back to the CSV."""
    df.to_csv(DATA_FILE, index=False)

# Load the data into session state
if 'materials_df' not in st.session_state:
    st.session_state.materials_df = load_data()

df = st.session_state.materials_df

# --- 2. App Layout & Title ---
st.title("PrintIQ: 3D Printing Material Selector")
st.markdown("Find the appropriate 3D printing material for your application.")

# Create tabs for the main interface and the database manager
tab1, tab2 = st.tabs(["🔍 Material Selector & Plots", "⚙️ Manage Materials Database"])

# --- TAB 1: Selector and Plots ---
with tab1:
    # Sidebar Filters
    st.sidebar.header("Filter Criteria")
    
    min_hdt = st.sidebar.number_input("Min Heat Deflection Temp (°C)", value=0.0, step=10.0)
    min_ts = st.sidebar.number_input("Min Tensile Strength (MPa)", value=0.0, step=10.0)
    min_tm = st.sidebar.number_input("Min Tensile Modulus (GPa)", value=0.0, step=0.5)
    max_price = st.sidebar.number_input("Max Price per kg (USD)", value=1500.0, step=50.0)
    
    st.sidebar.markdown("#### Printing Technology")
    techs_available = df["Technology"].dropna().unique().tolist()
    selected_techs = st.sidebar.multiselect("Select Technologies", options=techs_available, default=techs_available)

    # Apply Filters
    filtered_df = df[
        (df["HDT (°C)"] >= min_hdt) &
        (df["Tensile Strength (MPa)"] >= min_ts) &
        (df["Tensile Modulus (GPa)"] >= min_tm) &
        (df["Max Price/kg (USD)"] <= max_price) &
        (df["Technology"].isin(selected_techs))
    ]

    # Display Results
    st.subheader(f"Matching Materials ({len(filtered_df)})")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # Dynamic Plotting
    st.divider()
    st.subheader("📊 Dynamic Material Plots")
    
    numeric_cols = ["HDT (°C)", "Tensile Strength (MPa)", "Tensile Modulus (GPa)", "Max Price/kg (USD)", "Bed Temp (°C)", "Hotend Temp (°C)"]
    
    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("Choose X-Axis:", options=numeric_cols, index=3) # Default to Price
    with col2:
        y_axis = st.selectbox("Choose Y-Axis:", options=numeric_cols, index=0) # Default to HDT

    if not filtered_df.empty:
        # Create Plotly scatter plot
        fig = px.scatter(
            filtered_df, 
            x=x_axis, 
            y=y_axis, 
            color="Technology",
            hover_name="Material",
            hover_data=["Max Price/kg (USD)", "HDT (°C)", "Tensile Strength (MPa)"],
            title=f"{y_axis} vs {x_axis}",
            template="plotly_white"
        )
        fig.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No materials match your current filter criteria. Adjust the sliders in the sidebar.")

# --- TAB 2: Manage Materials ---
with tab2:
    st.header("Database Editor")
    st.markdown("""
    Use the table below to **add, edit, or delete** materials. 
    * **To Add:** Scroll to the bottom and type in the empty row.
    * **To Delete:** Select the checkbox on the left of a row and press the `Delete` key on your keyboard.
    * **To Edit:** Click any cell and type.
    """)

    # The dynamic data editor
    edited_df = st.data_editor(
        st.session_state.materials_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="data_editor"
    )

    # Save button
    if st.button("Save Changes to Database", type="primary"):
        st.session_state.materials_df = edited_df
        save_data(edited_df)
        st.success("Database successfully updated! Changes are saved to 'printiq_materials.csv'.")
