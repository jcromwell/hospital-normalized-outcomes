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
from datetime import datetime
import base64

# Configure Streamlit page
st.set_page_config(
    page_title="Hospital Outcomes Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced aesthetics
st.markdown("""
<style>
/* Main container styling */
.main {
    padding: 0rem 1rem;
}

/* Card styling */
.stMetric {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border: 1px solid #e5e7eb;
    transition: all 0.3s ease;
}

.stMetric:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

/* Metric value styling */
div[data-testid="metric-container"] {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 1px solid #e5e7eb;
    transition: all 0.3s ease;
}

div[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    transform: translateY(-2px);
}

div[data-testid="metric-container"] > div[data-testid="metric-value"] {
    font-size: 2rem;
    font-weight: 600;
    color: #1E88E5;
}

/* Headers styling */
h1 {
    color: #1F2937;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

h2 {
    color: #374151;
    font-weight: 600;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #E5E7EB;
}

h3 {
    color: #4B5563;
    font-weight: 600;
}

/* Selectbox styling */
div[data-baseweb="select"] {
    border-radius: 8px;
}

div[data-baseweb="select"] > div {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    transition: all 0.2s ease;
}

div[data-baseweb="select"] > div:hover {
    border-color: #1E88E5;
    box-shadow: 0 2px 8px rgba(30, 136, 229, 0.1);
}

/* Button styling */
.stButton > button {
    background-color: #1E88E5;
    color: white;
    border: none;
    padding: 0.5rem 1.5rem;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stButton > button:hover {
    background-color: #1976D2;
    box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
    transform: translateY(-1px);
}

/* Download button styling */
.stDownloadButton > button {
    background-color: #059669;
    color: white;
    border: none;
    padding: 0.5rem 1.5rem;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stDownloadButton > button:hover {
    background-color: #047857;
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
    transform: translateY(-1px);
}

/* Radio button styling */
div[role="radiogroup"] {
    background-color: #F9FAFB;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #E5E7EB;
}

/* Checkbox styling */
.stCheckbox {
    padding: 0.5rem;
    border-radius: 6px;
    transition: background-color 0.2s ease;
}

.stCheckbox:hover {
    background-color: #F3F4F6;
}

/* Table styling */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stTable {
    border-radius: 8px;
    overflow: hidden;
}

/* Reduce table font size */
.stTable table {
    font-size: 12px;
}

.stTable th {
    font-size: 12px;
}

.stTable td {
    font-size: 12px;
}

/* Expander styling */
.streamlit-expanderHeader {
    background-color: #F3F4F6;
    border-radius: 8px;
    border: 1px solid #E5E7EB;
    font-weight: 500;
}

.streamlit-expanderHeader:hover {
    background-color: #E5E7EB;
}

/* Info and warning boxes */
.stAlert {
    border-radius: 8px;
    border-left: 4px solid;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #F9FAFB;
    border-right: 1px solid #E5E7EB;
}

section[data-testid="stSidebar"] .stRadio > label {
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
}

/* Plotly chart styling */
.js-plotly-plot {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

/* Column gaps */
.row-widget.stHorizontal {
    gap: 1rem;
}

/* Footer styling */
.footer {
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid #E5E7EB;
}

/* Loading spinner */
.stSpinner > div {
    border-color: #1E88E5;
}

/* Metric label styling */
div[data-testid="metric-container"] label {
    color: #6B7280;
    font-weight: 500;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Success/Error message styling */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 8px;
    padding: 1rem;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: #F3F4F6;
    border-radius: 8px;
    padding: 0.25rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #FFFFFF;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Slider styling */
.stSlider > div > div {
    background-color: #E5E7EB;
}

.stSlider > div > div > div {
    background-color: #1E88E5;
}

/* Caption styling */
.caption {
    color: #6B7280;
    font-size: 0.875rem;
    margin-top: 0.5rem;
}

/* Custom container */
.custom-container {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 1px solid #e5e7eb;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

def get_base64_image(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

@st.cache_data(show_spinner=False)
def load_data():
    """Load and clean the hospital data"""
    data_file = "Readmission CMI-LOS-DRG 329-334 2022.xlsx"
    if os.path.exists(data_file):
        with st.spinner("⏳ Loading hospital data..."):
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
    
    # Create histogram with enhanced styling
    fig = px.histogram(
        x=clean_data,
        nbins=30,
        title=f'<b>{metric} Distribution</b><br><sup style="color: #6B7280">{title_suffix}</sup>',
        labels={'x': metric, 'y': 'Number of Hospitals'},
        color_discrete_sequence=['#60A5FA']  # Light blue color
    )
    
    # Add statistics lines
    mean_val = clean_data.mean()
    median_val = clean_data.median()
    
    fig.add_vline(
        x=mean_val, 
        line_dash="dash", 
        line_color="#EF4444",  # Red
        line_width=2,
        annotation_text=f"Mean: {mean_val:.2f}",
        annotation_position="top right",
        annotation_font_color="#EF4444"
    )
    fig.add_vline(
        x=median_val, 
        line_dash="dash", 
        line_color="#10B981",  # Green
        line_width=2,
        annotation_text=f"Median: {median_val:.2f}",
        annotation_position="top left",
        annotation_font_color="#10B981"
    )
    
    # Update layout with enhanced styling
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="sans-serif", size=12, color="#374151"),
        title_font_size=16,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5E7EB',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5E7EB',
            zeroline=False
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif",
            bordercolor="#E5E7EB"
        )
    )
    
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
    
    # Determine performance color based on metric type and percentile
    if "Readmission" in metric or "ALOS" in metric:
        # Lower is better for these metrics
        if percentile < 25:
            perf_color = "#10B981"  # Green - Good performance
        elif percentile < 75:
            perf_color = "#F59E0B"  # Yellow - Average
        else:
            perf_color = "#EF4444"  # Red - Poor performance
    else:
        # Higher might be better (CMI)
        perf_color = "#1E88E5"  # Blue - Neutral
    
    # Create box plot
    fig = go.Figure()
    
    # Add box plot for comparator with enhanced styling
    fig.add_trace(go.Box(
        y=comp_data,
        name="Comparator Group",
        boxpoints='outliers',
        fillcolor='#E0E7FF',
        line=dict(color='#4F46E5', width=2),
        marker=dict(
            color='#6366F1',
            size=4,
            line=dict(width=1, color='#4F46E5')
        )
    ))
    
    # Add point for index hospital/IDN with dynamic color
    fig.add_trace(go.Scatter(
        x=[0],
        y=[index_value],
        mode='markers+text',
        marker=dict(
            size=20, 
            color=perf_color, 
            symbol='star',
            line=dict(width=2, color='white')
        ),
        text=[f'{percentile:.0f}%ile'],
        textposition='middle right',
        textfont=dict(size=14, color=perf_color, family='sans-serif', weight=600),
        name=f'{index_label}',
        showlegend=True
    ))
    
    # Update layout with enhanced styling
    fig.update_layout(
        title=f'<b>{metric} Comparison</b><br><sup style="color: #6B7280">{index_label} vs Comparator Group</sup>',
        yaxis_title=metric,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="sans-serif", size=12, color="#374151"),
        title_font_size=16,
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5E7EB',
            zeroline=False
        ),
        margin=dict(l=40, r=40, t=80, b=40),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif",
            bordercolor="#E5E7EB"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#E5E7EB',
            borderwidth=1
        )
    )
    
    # Add percentile annotation
    fig.add_annotation(
        x=0,
        y=index_value,
        text=f"<b>{percentile:.0f}th percentile</b>",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor=perf_color,
        ax=50,
        ay=-30,
        bgcolor='white',
        bordercolor=perf_color,
        borderwidth=2,
        borderpad=4,
        font=dict(size=12, color=perf_color)
    )
    
    return fig

def display_summary_stats(index_data, comparator_data):
    """Display summary statistics"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏥 Index Hospital/IDN")
        if not index_data.empty:
            if len(index_data) == 1:
                row = index_data.iloc[0]
                
                # Hospital info table
                info_data = {
                    "Hospital": row['Hospital'],
                    "Provider ID": row['Provider'],
                    "IDN": row['IDN'],
                    "Staffed Beds": row['Number of Staffed Beds']
                }
                
                # Add location
                if 'City/State' in row and pd.notna(row['City/State']):
                    info_data["Location"] = row['City/State']
                elif 'City' in row and 'State' in row:
                    city = row['City'] if pd.notna(row['City']) else ''
                    state = row['State'] if pd.notna(row['State']) else ''
                    if city or state:
                        info_data["Location"] = f"{city}, {state}"
                
                # Display hospital info as table
                info_df = pd.DataFrame([info_data]).T
                info_df.columns = ['']
                st.table(info_df)
                
                # Metrics table
                st.write("**Key Metrics**")
                metrics_data = {}
                if pd.notna(row['Readmission Rate']):
                    metrics_data['Readmission Rate'] = f"{row['Readmission Rate']:.1%}"
                if pd.notna(row['ALOS']):
                    metrics_data['Average LOS'] = f"{row['ALOS']:.1f} days"
                if pd.notna(row['CMI']):
                    metrics_data['CMI'] = f"{row['CMI']:.2f}"
                if pd.notna(row['Normalized Readmission Rate']):
                    metrics_data['Normalized Readmission Rate'] = f"{row['Normalized Readmission Rate']:.1%}"
                if pd.notna(row['Normalized ALOS']):
                    metrics_data['Normalized ALOS'] = f"{row['Normalized ALOS']:.1f} days"
                
                if metrics_data:
                    metrics_df = pd.DataFrame([metrics_data]).T
                    metrics_df.columns = ['Value']
                    st.table(metrics_df)
            else:
                # IDN aggregate data
                st.write(f"**IDN:** {index_data.iloc[0]['IDN']}")
                st.write(f"**Number of Hospitals:** {len(index_data)}")
                
                st.write("**Aggregate Metrics**")
                metrics_data = {}
                for metric in ['Readmission Rate', 'ALOS', 'CMI', 'Normalized Readmission Rate', 'Normalized ALOS']:
                    mean_val = index_data[metric].mean()
                    if pd.notna(mean_val):
                        if 'Readmission Rate' in metric:
                            metrics_data[f"Avg {metric}"] = f"{mean_val:.1%}"
                        else:
                            metrics_data[f"Avg {metric}"] = f"{mean_val:.2f}"
                
                if metrics_data:
                    metrics_df = pd.DataFrame([metrics_data]).T
                    metrics_df.columns = ['Value']
                    st.table(metrics_df)
    
    with col2:
        st.subheader("📈 Comparator Group")
        st.write(f"**Number of Hospitals:** {len(comparator_data)}")
        
        # Create distribution table
        st.write("**Metrics Distribution**")
        dist_data = []
        
        for metric in ['Readmission Rate', 'ALOS', 'CMI', 'Normalized Readmission Rate', 'Normalized ALOS']:
            clean_data = comparator_data[metric].dropna()
            if not clean_data.empty:
                if 'Readmission Rate' in metric:
                    dist_data.append({
                        'Metric': metric,
                        'Mean': f"{clean_data.mean():.1%}",
                        'Median': f"{clean_data.median():.1%}",
                        '25th Percentile': f"{clean_data.quantile(0.25):.1%}",
                        '75th Percentile': f"{clean_data.quantile(0.75):.1%}"
                    })
                else:
                    dist_data.append({
                        'Metric': metric,
                        'Mean': f"{clean_data.mean():.2f}",
                        'Median': f"{clean_data.median():.2f}",
                        '25th Percentile': f"{clean_data.quantile(0.25):.2f}",
                        '75th Percentile': f"{clean_data.quantile(0.75):.2f}"
                    })
        
        if dist_data:
            dist_df = pd.DataFrame(dist_data)
            dist_df = dist_df.set_index('Metric')
            st.table(dist_df)

def main():
    # Add logo in sidebar with centered styling and reduced padding
    logo_html = f"""
    <style>
    .sidebar .sidebar-content {{
        padding-top: 1rem;
    }}
    </style>
    <div style="display: flex; justify-content: center; margin: -1.5rem 0 -1rem 0;">
        <img src="data:image/png;base64,{get_base64_image("tauspan_logo.png")}" width="125">
    </div>
    """
    st.sidebar.markdown(logo_html, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Main title with enhanced styling
    st.markdown("""
    <h1 style='text-align: center; color: #1F2937; margin-bottom: 0;'>
        🏥 Hospital Outcomes Analyzer
    </h1>
    <p style='text-align: center; color: #6B7280; font-size: 1.1rem; margin-top: 0.5rem;'>
        DRG 329-334 Intestinal Resection Procedures • 2022 Analysis
    </p>
    """, unsafe_allow_html=True)
    
    # Add explanation of normalized metrics with enhanced styling
    with st.expander("ℹ️ **About Normalized Metrics** - Click to learn more"):
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
    
    # Show success toast on first load
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = True
        st.toast("✅ Hospital data loaded successfully!", icon='✅')
    
    # Sidebar for selections with icon
    st.sidebar.markdown("### 🏥 Hospital Selection")
    
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
    
    # Comparator selection with icon
    st.sidebar.markdown("### 📊 Comparison Group")
    
    # Adjust comparison options based on selection mode
    if selection_mode == "IDN (Health System)":
        comparison_options = ["All Hospitals", "Same IDN"]
    else:
        comparison_options = ["All Hospitals", "Same IDN", "Same State"]
    
    comparator_type = st.sidebar.radio(
        "Compare to:",
        comparison_options
    )
    
    # Get comparator data
    comparator_data = filter_comparator_data(df, index_data, comparator_type, selected_hospital, selected_idn)
    
    # Main content
    if not index_data.empty:
        # Summary statistics with enhanced header
        st.markdown("""
        <h2 style='color: #1F2937; border-bottom: 3px solid #1E88E5; padding-bottom: 0.5rem; margin-bottom: 1.5rem;'>
            📊 Summary Statistics
        </h2>
        """, unsafe_allow_html=True)
        display_summary_stats(index_data, comparator_data)
        
        # Metric selection with enhanced header
        st.markdown("""
        <h2 style='color: #1F2937; border-bottom: 3px solid #1E88E5; padding-bottom: 0.5rem; margin-bottom: 1.5rem;'>
            📈 Analysis & Charts
        </h2>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_metric = st.selectbox(
                "Select Metric:",
                ["Readmission Rate", "ALOS", "CMI", "Normalized Readmission Rate", "Normalized ALOS"]
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribution")
            with st.spinner("Generating distribution chart..."):
                title_suffix = f"{len(comparator_data)} hospitals"
                chart = create_metric_chart(comparator_data, selected_metric, title_suffix)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
        
        with col2:
            st.subheader("📈 Comparison")
            with st.spinner("Generating comparison chart..."):
                comp_chart = create_comparison_chart(index_data, comparator_data, selected_metric)
                if comp_chart:
                    st.plotly_chart(comp_chart, use_container_width=True)
        
        # Data table with enhanced header
        st.markdown("""
        <h2 style='color: #1F2937; border-bottom: 3px solid #1E88E5; padding-bottom: 0.5rem; margin-bottom: 1.5rem;'>
            📋 Hospital Data
        </h2>
        """, unsafe_allow_html=True)
        
        # Filter options
        col1, col2 = st.columns([1, 2])
        with col1:
            show_all = st.checkbox("Show all comparator hospitals", value=False)
        
        # Initialize display_data
        display_data = comparator_data.copy()
        
        # Show percentage slider when "show all" is unchecked
        if not show_all and not index_data.empty:
            with col2:
                claims_percent = st.slider(
                    "Total procedures similarity (%)",
                    min_value=1,
                    max_value=75,
                    value=5,
                    step=1,
                    help="Show hospitals within this percentage of the index hospital's total procedures (Medicare Total Claims)"
                )
            
            # Get index Medicare Total Claims
            if len(index_data) == 1:
                index_claims = index_data.iloc[0]['Medicare Total Claims']
            else:
                # For IDN, use average Medicare Total Claims
                index_claims = index_data['Medicare Total Claims'].mean()
            
            # Calculate claims range based on percentage
            claims_tolerance = index_claims * (claims_percent / 100)
            min_claims_threshold = index_claims - claims_tolerance
            max_claims_threshold = index_claims + claims_tolerance
            
            # Filter display data to hospitals within claims range
            with st.spinner(f"Filtering hospitals within ±{claims_percent}% total procedures..."):
                display_data = display_data[
                    (display_data['Medicare Total Claims'] >= min_claims_threshold) &
                    (display_data['Medicare Total Claims'] <= max_claims_threshold)
                ]
                
                # Also ensure index hospital(s) are included
                display_data = pd.concat([index_data, display_data]).drop_duplicates()
        
        # Scatter plot - Normalized ALOS vs Normalized Readmission Rate
        st.header("📊 Normalized Performance Comparison")
        
        # Create scatter plot data from display_data (already filtered)
        scatter_data = display_data[['Provider', 'Hospital', 'Normalized ALOS', 'Normalized Readmission Rate']].copy()
        scatter_data = scatter_data.dropna(subset=['Normalized ALOS', 'Normalized Readmission Rate'])
        
        # Add info about what's being displayed
        if not show_all and not index_data.empty:
            st.info(f"📊 Scatter plot and table show hospitals within ±{claims_percent}% of index hospital total procedures "
                   f"({min_claims_threshold:.0f} - {max_claims_threshold:.0f} procedures). "
                   f"Displaying {len(scatter_data)} hospitals with complete normalized data.")
        elif show_all:
            st.info(f"📊 Showing all {len(scatter_data)} comparator hospitals with complete normalized data.")
        
        if not scatter_data.empty:
            # Truncate hospital names for labels
            scatter_data['Label'] = scatter_data['Hospital'].apply(lambda x: x[:20] + '...' if len(str(x)) > 20 else str(x))
            
            # Identify index hospital(s)
            if len(index_data) == 1:
                index_provider = index_data.iloc[0]['Provider']
                scatter_data['Is_Index'] = scatter_data['Provider'] == index_provider
            else:
                # For IDN selection, mark all hospitals in the IDN
                index_providers = index_data['Provider'].tolist()
                scatter_data['Is_Index'] = scatter_data['Provider'].isin(index_providers)
            
            # Create the scatter plot
            fig = go.Figure()
            
            # Add comparator hospitals
            comparator_points = scatter_data[~scatter_data['Is_Index']]
            if not comparator_points.empty:
                fig.add_trace(go.Scatter(
                    x=comparator_points['Normalized ALOS'],
                    y=comparator_points['Normalized Readmission Rate'],
                    mode='markers+text',
                    marker=dict(
                        size=10,
                        color='#60A5FA',  # Light blue
                        line=dict(width=1.5, color='#2563EB'),  # Darker blue border
                        opacity=0.8
                    ),
                    text=comparator_points['Label'],
                    textposition="top center",
                    textfont=dict(size=9, color='#4B5563'),
                    name='Comparator Hospitals',
                    hovertemplate='<b>%{text}</b><br>Normalized ALOS: %{x:.2f}<br>Normalized Readmission Rate: %{y:.1%}<extra></extra>'
                ))
            
            # Add index hospital(s) - highlighted
            index_points = scatter_data[scatter_data['Is_Index']]
            if not index_points.empty:
                fig.add_trace(go.Scatter(
                    x=index_points['Normalized ALOS'],
                    y=index_points['Normalized Readmission Rate'],
                    mode='markers+text',
                    marker=dict(
                        size=20,
                        color='#F59E0B',  # Amber
                        symbol='star',
                        line=dict(width=2, color='white')
                    ),
                    text=index_points['Label'],
                    textposition="top center",
                    textfont=dict(size=12, color='#D97706', weight=600),
                    name='Selected Hospital(s)',
                    hovertemplate='<b>%{text}</b><br>Normalized ALOS: %{x:.2f}<br>Normalized Readmission Rate: %{y:.1%}<extra></extra>'
                ))
            
            # Add reference lines for means
            mean_alos = scatter_data['Normalized ALOS'].mean()
            mean_readmit = scatter_data['Normalized Readmission Rate'].mean()
            
            # Add quadrant shading
            fig.add_hrect(
                y0=0, y1=mean_readmit,
                x0=0, x1=mean_alos,
                fillcolor="#10B981", opacity=0.1,
                layer="below", line_width=0
            )
            
            fig.add_hline(
                y=mean_readmit,
                line_dash="dot",
                line_color="#6B7280",
                opacity=0.7,
                line_width=2,
                annotation_text=f"Mean: {mean_readmit:.1%}",
                annotation_position="right",
                annotation_font=dict(color="#6B7280", size=11)
            )
            fig.add_vline(
                x=mean_alos,
                line_dash="dot",
                line_color="#6B7280",
                opacity=0.7,
                line_width=2,
                annotation_text=f"Mean: {mean_alos:.2f}",
                annotation_position="top",
                annotation_font=dict(color="#6B7280", size=11)
            )
            
            # Update layout with enhanced styling
            fig.update_layout(
                title=dict(
                    text="<b>Normalized ALOS vs Normalized Readmission Rate</b><br><sup style='color: #6B7280'>Lower values indicate better performance when adjusted for case complexity</sup>",
                    font=dict(size=18)
                ),
                xaxis_title="<b>Normalized ALOS</b> (days/CMI)",
                yaxis_title="<b>Normalized Readmission Rate</b> (%/CMI)",
                height=650,
                hovermode='closest',
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="sans-serif", size=12, color="#374151"),
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#E5E7EB',
                    zeroline=False,
                    tickfont=dict(size=11)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#E5E7EB',
                    zeroline=False,
                    tickfont=dict(size=11)
                ),
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='#E5E7EB',
                    borderwidth=1,
                    font=dict(size=12)
                ),
                margin=dict(l=60, r=40, t=80, b=60)
            )
            
            # Format y-axis as percentage
            fig.update_layout(yaxis_tickformat='.1%')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add performance quadrant explanation
            with st.expander("📊 Understanding the Performance Quadrants"):
                st.markdown("""
                The scatter plot is divided into four quadrants by the mean values:
                
                - **Lower-Left (Best)**: Below average normalized readmission rate AND below average normalized length of stay
                - **Lower-Right**: Below average normalized readmission rate BUT above average normalized length of stay
                - **Upper-Left**: Above average normalized readmission rate BUT below average normalized length of stay
                - **Upper-Right (Worst)**: Above average normalized readmission rate AND above average normalized length of stay
                
                **Note**: These are normalized metrics (divided by CMI), so they account for case complexity. 
                Lower values generally indicate better performance.
                """)
        else:
            st.warning("Insufficient data for scatter plot. Both Normalized ALOS and Normalized Readmission Rate data are required.")
        
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
        
        st.table(formatted_data)
        
        # Export functionality with enhanced header
        st.markdown("""
        <h2 style='color: #1F2937; border-bottom: 3px solid #1E88E5; padding-bottom: 0.5rem; margin-bottom: 1.5rem;'>
            💾 Export Data
        </h2>
        """, unsafe_allow_html=True)
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
        # Welcome message with enhanced styling
        st.markdown("""
        <div style='background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%); 
                    padding: 2rem; 
                    border-radius: 12px; 
                    text-align: center;
                    border: 1px solid #C7D2FE;'>
            <h2 style='color: #4338CA; margin-bottom: 1rem;'>👋 Welcome to Hospital Outcomes Analyzer</h2>
            <p style='color: #4B5563; font-size: 1.1rem;'>
                Select a hospital or health system from the sidebar to begin your analysis.
            </p>
            <p style='color: #6B7280; font-size: 0.95rem; margin-top: 0.5rem;'>
                This tool analyzes readmission rates and length of stay for intestinal resection procedures.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show data overview
        st.header("📊 Dataset Overview")
        
        # Create overview container
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Hospitals", 
                value=f"{len(df):,}",
                delta=None,
                help="Total number of hospitals in the dataset"
            )
        with col2:
            st.metric(
                label="Health Systems", 
                value=f"{df['IDN'].nunique():,}",
                delta=None,
                help="Total number of Integrated Delivery Networks (IDNs)"
            )
        with col3:
            if 'State' in df.columns:
                states = df['State'].nunique()
            elif 'City/State' in df.columns:
                states = df['City/State'].str.split(', ').str[-1].nunique()
            else:
                states = "N/A"
            st.metric(
                label="States Covered", 
                value=states,
                delta=None,
                help="Geographic coverage across US states"
            )
        with col4:
            total_discharges = df['Number of Discharges'].sum() if 'Number of Discharges' in df.columns else None
            if total_discharges:
                st.metric(
                    label="Total Procedures", 
                    value=f"{total_discharges:,}",
                    delta=None,
                    help="Total DRG 329-334 procedures in 2022"
                )
            else:
                avg_beds = df['Number of Staffed Beds'].mean()
                st.metric(
                    label="Avg Bed Size", 
                    value=f"{avg_beds:.0f}",
                    delta=None,
                    help="Average hospital bed capacity"
                )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add enhanced footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: linear-gradient(to right, #F3F4F6, #E5E7EB); 
                padding: 2rem 0; 
                margin: 0 -1rem; 
                text-align: center;
                border-top: 2px solid #E5E7EB;'>
        <img src="data:image/png;base64,{}" width="80" style="margin-bottom: 0.5rem;">
        <p style='color: #4B5563; font-size: 0.9rem; margin: 0;'>
            Copyright © {} tauSpan Technologies LLC. All rights reserved.
        </p>
        <p style='color: #6B7280; font-size: 0.8rem; margin-top: 0.5rem;'>
            Built with ❤️ for healthcare analytics
        </p>
    </div>
    """.format(get_base64_image("tauspan_logo.png"), datetime.now().year), unsafe_allow_html=True)

if __name__ == "__main__":
    main()