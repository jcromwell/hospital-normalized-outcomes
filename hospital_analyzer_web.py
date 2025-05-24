#!/usr/bin/env python3
"""
Hospital Outcomes Analyzer - Web Interface
A web-based application for analyzing hospital readmission data
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
import os

# Configure Streamlit page
st.set_page_config(
    page_title="Hospital Outcomes Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Load and clean the hospital data"""
    data_file = "Readmission CMI-LOS-DRG 329-334 2022.xlsx"
    if os.path.exists(data_file):
        df = pd.read_excel(data_file)
        
        # Clean the data
        df['CMI'] = pd.to_numeric(df['CMI'], errors='coerce')
        df = df.dropna(axis=1, how='all')
        df['IDN'] = df['IDN'].fillna('Independent')
        
        # Create City/State column if it doesn't exist
        if 'City/State' not in df.columns and 'City' in df.columns and 'State' in df.columns:
            df['City/State'] = df['City'].astype(str) + ', ' + df['State'].astype(str)
            df['City/State'] = df['City/State'].replace('nan, nan', '')
        
        # Calculate normalized metrics (divide by CMI to adjust for case complexity)
        df['Normalized ALOS'] = df['ALOS'] / df['CMI']
        df['Normalized Readmission Rate'] = df['Readmission Rate'] / df['CMI']
        
        return df
    else:
        st.error(f"Data file '{data_file}' not found in current directory")
        return None

def get_hospital_display_name(row):
    """Create a display name for hospitals"""
    return f"{row['Provider']} - {row['Hospital']}"

def filter_comparator_data(df, index_data, comparator_type, selected_hospital, selected_idn):
    """Filter data based on comparator selection"""
    if comparator_type == "All Hospitals":
        return df
    elif comparator_type == "Same IDN":
        if selected_hospital and not index_data.empty:
            idn = index_data.iloc[0]['IDN']
            return df[df['IDN'] == idn]
        elif selected_idn:
            return df[df['IDN'] == selected_idn]
        else:
            return df
    elif comparator_type == "Same State":
        if selected_hospital and not index_data.empty:
            # Try City/State column first, then State column
            if 'City/State' in index_data.columns:
                location = index_data.iloc[0]['City/State']
                if pd.notna(location) and ', ' in str(location):
                    state = location.split(', ')[-1]
                    return df[df['City/State'].str.contains(state, na=False)]
            elif 'State' in index_data.columns:
                state = index_data.iloc[0]['State']
                if pd.notna(state):
                    return df[df['State'] == state]
        return df
    return df

def create_metric_chart(data, metric, title_suffix=""):
    """Create a histogram chart for the selected metric"""
    clean_data = data[metric].dropna()
    
    if clean_data.empty:
        st.warning(f"No data available for {metric}")
        return None
    
    # Create histogram
    fig = px.histogram(
        x=clean_data,
        nbins=30,
        title=f'{metric} Distribution - {title_suffix}',
        labels={'x': metric, 'y': 'Number of Hospitals'}
    )
    
    # Add statistics lines
    mean_val = clean_data.mean()
    median_val = clean_data.median()
    
    fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                  annotation_text=f"Mean: {mean_val:.2f}")
    fig.add_vline(x=median_val, line_dash="dash", line_color="blue", 
                  annotation_text=f"Median: {median_val:.2f}")
    
    fig.update_layout(height=400)
    return fig

def create_comparison_chart(index_data, comparator_data, metric):
    """Create a comparison chart showing index vs comparator"""
    if index_data.empty or comparator_data.empty:
        return None
        
    # Get index value
    if len(index_data) == 1:
        index_value = index_data.iloc[0][metric]
        index_label = "Selected Hospital"
    else:
        index_value = index_data[metric].mean()
        index_label = "Selected IDN (Average)"
    
    if pd.isna(index_value):
        st.warning(f"No {metric} data available for selected hospital/IDN")
        return None
    
    # Get comparator distribution
    comp_data = comparator_data[metric].dropna()
    if comp_data.empty:
        return None
    
    # Calculate percentile
    percentile = (comp_data < index_value).mean() * 100
    
    # Create box plot
    fig = go.Figure()
    
    # Add box plot for comparator
    fig.add_trace(go.Box(
        y=comp_data,
        name="Comparator Group",
        boxpoints='outliers'
    ))
    
    # Add point for index hospital/IDN
    fig.add_trace(go.Scatter(
        x=[0],
        y=[index_value],
        mode='markers',
        marker=dict(size=15, color='red', symbol='star'),
        name=f'{index_label} ({percentile:.1f}th percentile)'
    ))
    
    fig.update_layout(
        title=f'{metric} Comparison',
        yaxis_title=metric,
        height=400
    )
    
    return fig

def display_summary_stats(index_data, comparator_data):
    """Display summary statistics"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Index Hospital/IDN")
        if not index_data.empty:
            if len(index_data) == 1:
                row = index_data.iloc[0]
                st.write(f"**Hospital:** {row['Hospital']}")
                st.write(f"**Provider ID:** {row['Provider']}")
                st.write(f"**IDN:** {row['IDN']}")
                if 'City/State' in row and pd.notna(row['City/State']):
                    st.write(f"**Location:** {row['City/State']}")
                elif 'City' in row and 'State' in row:
                    city = row['City'] if pd.notna(row['City']) else ''
                    state = row['State'] if pd.notna(row['State']) else ''
                    if city or state:
                        st.write(f"**Location:** {city}, {state}")
                st.write(f"**Staffed Beds:** {row['Number of Staffed Beds']}")
                
                st.write("**Key Metrics:**")
                if pd.notna(row['Readmission Rate']):
                    st.write(f"Readmission Rate: {row['Readmission Rate']:.1%}")
                if pd.notna(row['ALOS']):
                    st.write(f"Average LOS: {row['ALOS']:.1f} days")
                if pd.notna(row['CMI']):
                    st.write(f"CMI: {row['CMI']:.2f}")
                if pd.notna(row['Normalized Readmission Rate']):
                    st.write(f"Normalized Readmission Rate: {row['Normalized Readmission Rate']:.1%}")
                if pd.notna(row['Normalized ALOS']):
                    st.write(f"Normalized ALOS: {row['Normalized ALOS']:.1f} days")
            else:
                st.write(f"**IDN:** {index_data.iloc[0]['IDN']}")
                st.write(f"**Number of Hospitals:** {len(index_data)}")
                
                st.write("**Aggregate Metrics:**")
                for metric in ['Readmission Rate', 'ALOS', 'CMI', 'Normalized Readmission Rate', 'Normalized ALOS']:
                    mean_val = index_data[metric].mean()
                    if pd.notna(mean_val):
                        if 'Readmission Rate' in metric:
                            st.write(f"Avg {metric}: {mean_val:.1%}")
                        else:
                            st.write(f"Avg {metric}: {mean_val:.2f}")
    
    with col2:
        st.subheader("Comparator Group")
        st.write(f"**Number of Hospitals:** {len(comparator_data)}")
        
        for metric in ['Readmission Rate', 'ALOS', 'CMI', 'Normalized Readmission Rate', 'Normalized ALOS']:
            clean_data = comparator_data[metric].dropna()
            if not clean_data.empty:
                st.write(f"**{metric} Distribution:**")
                if 'Readmission Rate' in metric:
                    st.write(f"  Mean: {clean_data.mean():.1%}")
                    st.write(f"  Median: {clean_data.median():.1%}")
                    st.write(f"  25th-75th Percentile: {clean_data.quantile(0.25):.1%} - {clean_data.quantile(0.75):.1%}")
                else:
                    st.write(f"  Mean: {clean_data.mean():.2f}")
                    st.write(f"  Median: {clean_data.median():.2f}")
                    st.write(f"  25th-75th Percentile: {clean_data.quantile(0.25):.2f} - {clean_data.quantile(0.75):.2f}")

def main():
    st.title("🏥 Hospital Outcomes Analyzer")
    st.markdown("### DRG 329-334 Readmission Analysis")
    
    # Add explanation of normalized metrics
    with st.expander("ℹ️ About Normalized Metrics"):
        st.markdown("""
        **Normalized metrics adjust for case complexity using Case Mix Index (CMI):**
        
        - **Normalized Readmission Rate** = Readmission Rate ÷ CMI
        - **Normalized ALOS** = Average Length of Stay ÷ CMI
        
        These metrics provide fairer comparisons between hospitals by accounting for differences in patient complexity. 
        A hospital with higher CMI (more complex cases) would be expected to have higher raw readmission rates and length of stay, 
        so normalizing helps identify true performance differences.
        
        **Lower normalized values typically indicate better performance** when adjusted for case complexity.
        """)
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Sidebar for selections
    st.sidebar.header("Hospital Selection")
    
    # Selection mode
    selection_mode = st.sidebar.radio(
        "Select by:",
        ["Individual Hospital", "IDN (Health System)"]
    )
    
    selected_hospital = None
    selected_idn = None
    index_data = pd.DataFrame()
    
    if selection_mode == "Individual Hospital":
        # Hospital selection
        hospital_options = [get_hospital_display_name(row) for _, row in df.iterrows() if pd.notna(row['Hospital'])]
        selected_hospital = st.sidebar.selectbox(
            "Choose Hospital:",
            [""] + sorted(hospital_options)
        )
        
        if selected_hospital:
            provider_id = selected_hospital.split(' - ')[0]
            index_data = df[df['Provider'].astype(str) == provider_id]
    
    else:
        # IDN selection
        idn_options = df['IDN'].dropna().unique()
        selected_idn = st.sidebar.selectbox(
            "Choose IDN:",
            [""] + sorted(idn_options)
        )
        
        if selected_idn:
            index_data = df[df['IDN'] == selected_idn]
    
    # Comparator selection
    st.sidebar.header("Comparison Group")
    comparator_type = st.sidebar.radio(
        "Compare to:",
        ["All Hospitals", "Same IDN", "Same State"]
    )
    
    # Get comparator data
    comparator_data = filter_comparator_data(df, index_data, comparator_type, selected_hospital, selected_idn)
    
    # Main content
    if not index_data.empty:
        # Summary statistics
        st.header("Summary Statistics")
        display_summary_stats(index_data, comparator_data)
        
        # Metric selection
        st.header("Analysis & Charts")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_metric = st.selectbox(
                "Select Metric:",
                ["Readmission Rate", "ALOS", "CMI", "Normalized Readmission Rate", "Normalized ALOS"]
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribution")
            title_suffix = f"{len(comparator_data)} hospitals"
            chart = create_metric_chart(comparator_data, selected_metric, title_suffix)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        with col2:
            st.subheader("Comparison")
            comp_chart = create_comparison_chart(index_data, comparator_data, selected_metric)
            if comp_chart:
                st.plotly_chart(comp_chart, use_container_width=True)
        
        # Data table
        st.header("Hospital Data")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            show_all = st.checkbox("Show all comparator hospitals", value=False)
        with col2:
            min_beds = st.number_input("Minimum beds:", min_value=0, value=0)
        with col3:
            max_beds = st.number_input("Maximum beds:", min_value=0, value=3000)
        
        # Filter data for table
        display_data = comparator_data.copy()
        if not show_all and not index_data.empty:
            # Show index hospitals plus top/bottom performers
            n_show = min(20, len(comparator_data))
            if selected_metric in comparator_data.columns:
                sorted_data = comparator_data.sort_values(selected_metric, na_position='last')
                top_performers = sorted_data.head(n_show//2)
                bottom_performers = sorted_data.tail(n_show//2)
                display_data = pd.concat([index_data, top_performers, bottom_performers]).drop_duplicates()
        
        # Apply bed filters
        if min_beds > 0:
            display_data = display_data[display_data['Number of Staffed Beds'] >= min_beds]
        if max_beds < 3000:
            display_data = display_data[display_data['Number of Staffed Beds'] <= max_beds]
        
        # Format data for display
        available_columns = ['Provider', 'Hospital', 'IDN', 'Number of Staffed Beds', 
                           'Readmission Rate', 'ALOS', 'CMI', 'Normalized Readmission Rate', 'Normalized ALOS']
        
        # Add location columns if available
        if 'City/State' in display_data.columns:
            available_columns.insert(3, 'City/State')
        elif 'City' in display_data.columns and 'State' in display_data.columns:
            available_columns.insert(3, 'City')
            available_columns.insert(4, 'State')
        
        # Only include columns that exist in the data
        display_columns = [col for col in available_columns if col in display_data.columns]
        
        formatted_data = display_data[display_columns].copy()
        
        # Format percentages and numbers
        for col in ['Readmission Rate', 'Normalized Readmission Rate']:
            if col in formatted_data.columns:
                formatted_data[col] = formatted_data[col].apply(
                    lambda x: f"{x:.1%}" if pd.notna(x) else "N/A"
                )
        
        for col in ['ALOS', 'CMI', 'Normalized ALOS']:
            if col in formatted_data.columns:
                formatted_data[col] = formatted_data[col].apply(
                    lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
                )
        
        st.dataframe(formatted_data, use_container_width=True, height=400)
        
        # Export functionality
        st.header("Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download Filtered Data as CSV"):
                csv = display_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="hospital_analysis.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Download All Data as CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download All Data CSV",
                    data=csv,
                    file_name="hospital_data_complete.csv",
                    mime="text/csv"
                )
    
    else:
        st.info("👈 Please select a hospital or IDN from the sidebar to begin analysis")
        
        # Show data overview
        st.header("Dataset Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Hospitals", len(df))
        with col2:
            st.metric("Total IDNs", df['IDN'].nunique())
        with col3:
            if 'State' in df.columns:
                st.metric("States Covered", df['State'].nunique())
            elif 'City/State' in df.columns:
                st.metric("States Covered", df['City/State'].str.split(', ').str[-1].nunique())
            else:
                st.metric("States Covered", "N/A")

if __name__ == "__main__":
    main()