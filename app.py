import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from scipy import stats

# Custom CSS Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    
    :root {
        --primary: #2A9D8F;
        --secondary: #264653;
        --accent: #E9C46A;
        --dark: #2F3E46;
        --light: #F8F9FA;
        --highlight: #F4A261;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Space Grotesk', sans-serif;
    }

    body {
        background: linear-gradient(135deg, var(--dark), #333333);
        color: var(--light);
    }

    .main {
        padding: 3rem;
        background: radial-gradient(circle at center, var(--dark), #2f2f2f);
        color: var(--light);
    }

    h1 {
        color: var(--primary);
        text-align: center;
        font-weight: 700;
        font-size: 3rem;
        padding: 1.5rem 0;
        background: linear-gradient(45deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        letter-spacing: 2px;
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from {
            text-shadow: 0 0 10px rgba(42,157,143,0.3), 0 0 20px rgba(233,196,106,0.5);
        }
        to {
            text-shadow: 0 0 20px rgba(42,157,143,0.5), 0 0 30px rgba(233,196,106,0.7);
        }
    }

    .executive-summary {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid var(--primary);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.25);
    }

    .stButton button {
        background-color: var(--primary);
        color: var(--light);
        border-radius: 5px;
        border: none;
        padding: 0.8rem 1.5rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(42, 157, 143, 0.25);
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
    }

    .stButton button:hover {
        background-color: var(--accent);
        box-shadow: 0 8px 20px rgba(233, 196, 106, 0.5);
    }

    .stSelectbox, .stSlider, .stRadio {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 0.8rem;
        border: 1px solid var(--primary);
        margin-bottom: 1rem;
        transition: background-color 0.3s ease, transform 0.2s ease;
        color: var(--light);
    }

    .stSelectbox:hover, .stSlider:hover, .stRadio:hover {
        background-color: rgba(255, 255, 255, 0.3);
        transform: scale(1.02);
    }

    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        border: 1px solid var(--primary);
        color: var(--light);
        padding: 0.8rem;
        font-size: 1rem;
    }

    .stTextInput input:focus {
        border-color: var(--accent);
        outline: none;
    }

    .loading-spinner {
        animation: spin 1s linear infinite;
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid var(--primary);
        border-radius: 50%;
        margin: 20px auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .sidebar {
        background-color: rgba(31, 38, 135, 0.9);
        color: var(--light);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(31, 38, 135, 0.3);
        transition: all 0.3s ease;
    }

    .sidebar:hover {
        background-color: var(--secondary);
    }

    .expander-header {
        font-weight: bold;
        color: var(--primary);
        font-size: 1.2rem;
        cursor: pointer;
    }

    .expander-content {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 8px;
    }
    
    .stPlotlyChart {
        border-radius: 15px;
        margin-top: 2rem;
        background-color: rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)



def handle_geolocation(df):
    """Process geolocation data if available"""
    geo_available = 'GeoLocation' in df.columns
    latlon_available = all(col in df.columns for col in ['Latitude', 'Longitude'])
    
    if geo_available and not latlon_available:
        try:
            df[['Latitude', 'Longitude']] = df['GeoLocation'].str.strip('()').str.split(',', expand=True).astype(float)
            df = df.drop(columns=['GeoLocation'])
            st.session_state.geo_warning = False
        except:
            st.session_state.geo_warning = True
    elif not latlon_available:
        st.session_state.geo_warning = True
    else:
        st.session_state.geo_warning = False
        
    return df

def generate_executive_summary(filtered_df, confidence_level):
    """Generate automated insights and recommendations"""
    summary = {
        'start_year': filtered_df['YearStart'].min(),
        'end_year': filtered_df['YearStart'].max(),
        'num_states': filtered_df['LocationDesc'].nunique(),
        'num_diseases': filtered_df['Topic'].nunique(),
        'avg_prevalence': filtered_df['DataValue'].mean(),
        'max_prevalence_state': filtered_df.groupby('LocationDesc')['DataValue'].mean().idxmax(),
        'min_prevalence_state': filtered_df.groupby('LocationDesc')['DataValue'].mean().idxmin(),
        'most_common_disease': filtered_df['Topic'].value_counts().idxmax(),
        'trend_direction': 'increasing' if filtered_df.groupby('YearStart')['DataValue'].mean().pct_change().mean() > 0 else 'decreasing',
        'ci_low': stats.norm.interval(confidence_level/100, 
                                    loc=filtered_df['DataValue'].mean(),
                                    scale=filtered_df['DataValue'].std())[0],
        'ci_high': stats.norm.interval(confidence_level/100, 
                                     loc=filtered_df['DataValue'].mean(),
                                     scale=filtered_df['DataValue'].std())[1]
    }
    
    insights = f"""
    <div class="executive-summary">
        <h3>Executive Summary</h3>
        <ul style="list-style-type:none; padding-left:0;">
            <li>📅 <strong>Analysis Period:</strong> {summary['start_year']} - {summary['end_year']}</li>
            <li>🌍 <strong>Geographic Coverage:</strong> {summary['num_states']} states analyzed</li>
            <li>🦠 <strong>Disease Focus:</strong> {summary['num_diseases']} chronic conditions tracked</li>
            <li>📈 <strong>Prevalence Trend:</strong> {summary['trend_direction'].capitalize()} trend observed</li>
            <li>🏆 <strong>High Prevalence Area:</strong> {summary['max_prevalence_state']} shows highest rates</li>
            <li>🩺 <strong>Most Common Condition:</strong> {summary['most_common_disease']}</li>
            <li>📉 <strong>Confidence Range:</strong> {confidence_level}% CI ({summary['ci_low']:.1f}% - {summary['ci_high']:.1f}%)</li>
        </ul>
        <div style="margin-top:1.5rem; border-top:1px solid var(--primary); padding-top:1rem;">
            <h4>Key Recommendations</h4>
            <ul style="list-style-type:none; padding-left:0;">
                <li>🔍 Focus interventions in {summary['max_prevalence_state']} for maximum impact</li>
                <li>📊 Prioritize research on {summary['most_common_disease']} prevalence drivers</li>
                <li>🌡️ Monitor {summary['min_prevalence_state']} for best practice identification</li>
                <li>📈 Allocate resources for {summary['trend_direction']} trend management</li>
            </ul>
        </div>
    </div>
    """
    return insights

def main():
    st.title("Chronic Disease Prevalence Analysis")
    
    # File Upload
    uploaded_file = st.sidebar.file_uploader("📤 Upload Dataset", type="csv", 
                         help="Upload CDC Chronic Disease CSV data")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # ========== Data Preparation Section ==========
        st.sidebar.header("🔧 Data Preparation")
        with st.sidebar.expander("Column Management"):
            cols_to_drop = st.multiselect("Select columns to remove", df.columns)
            if st.button("Confirm Removal"):
                df = df.drop(columns=cols_to_drop, errors='ignore')
                st.session_state.cleaned_df = df.copy()
        
        if 'cleaned_df' in st.session_state:
            df = st.session_state.cleaned_df
        
        # Data Cleaning
        with st.expander("Data Cleaning Console", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write("Missing Values Summary:")
                missing = df.isnull().sum()
                st.write(missing)
            
            with col2:
                st.write("Data Types Summary:")
                dtypes = df.dtypes
                st.write(dtypes)
            
            if st.button("Clean Data Automatically"):
                required_cols = ['DataValue']
                if 'GeoLocation' in df.columns:
                    required_cols.append('GeoLocation')
                
                # Clean core data
                df = df.dropna(subset=required_cols)
                df['DataValue'] = pd.to_numeric(df['DataValue'], errors='coerce')
                df = df.dropna(subset=['DataValue'])
                
                # Handle geolocation
                df = handle_geolocation(df)
                
                st.session_state.cleaned_df = df.copy()
                st.success("Automatic cleaning completed!")

        # ========== Advanced Filters ==========
        st.sidebar.header("🔮 Analysis Parameters")
        with st.sidebar.expander("Core Filters"):
            selected_years = st.slider('Select Years', 
                                     min_value=int(df['YearStart'].min()),
                                     max_value=int(df['YearStart'].max()),
                                     value=(int(df['YearStart'].min()), int(df['YearStart'].max())))

            selected_states = st.multiselect('Select States', 
                                           options=df['LocationDesc'].unique(),
                                           default=df['LocationDesc'].unique()[:3])

            selected_diseases = st.multiselect('Select Diseases',
                                              options=df['Topic'].unique(),
                                              default=df['Topic'].unique()[:2])

        with st.sidebar.expander("Advanced Controls"):
            confidence_level = st.slider("Confidence Level", 80, 99, 95)
            show_confidence = st.checkbox("Show Confidence Intervals")
            analysis_type = st.selectbox("Analysis Type", 
                                       ["Trend Analysis", "Comparative Analysis", "Geospatial Analysis"])

        # Apply Filters
        filtered_df = df[
            (df['YearStart'].between(*selected_years)) & 
            (df['LocationDesc'].isin(selected_states)) & 
            (df['Topic'].isin(selected_diseases))
        ]

        # ========== Executive Summary ==========
        st.markdown(generate_executive_summary(filtered_df, confidence_level), unsafe_allow_html=True)

        # ========== Main Dashboard ==========
        st.header("📊 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>Avg Prevalence</h3>
                    <span style="font-size:1.5em; color:#2A9D8F">
                        {filtered_df['DataValue'].mean():.1f}%
                    </span>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>States</h3>
                    <span style="font-size:1.5em; color:#E9C46A">
                        {filtered_df['LocationDesc'].nunique()}
                    </span>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>Diseases</h3>
                    <span style="font-size:1.5em; color:#F4A261">
                        {filtered_df['Topic'].nunique()}
                    </span>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            ci_low, ci_high = stats.norm.interval(confidence_level/100, 
                                                loc=filtered_df['DataValue'].mean(),
                                                scale=filtered_df['DataValue'].std())
            st.markdown(f"""
                <div class="metric-card">
                    <h3>{confidence_level}% CI</h3>
                    <span style="font-size:1.2em; color:#2A9D8F">
                        {ci_low:.1f}% - {ci_high:.1f}%
                    </span>
                </div>
            """, unsafe_allow_html=True)

        # ========== Advanced Visualizations ==========
        st.header("🔍 Analytical Insights")
        
        # Trend Analysis
        with st.expander("Temporal Trends Analysis", expanded=True):
            col1, col2 = st.columns([3,1])
            with col1:
                trend_fig = px.line(filtered_df, x="YearStart", y="DataValue", 
                                  color="Topic", facet_col="LocationDesc",
                                  title="Disease Prevalence Trends by State",
                                  template="plotly_dark")
                st.plotly_chart(trend_fig, use_container_width=True)
            
            with col2:
                st.subheader("Top Diseases")
                top_diseases = filtered_df.groupby('Topic')['DataValue'].mean().nlargest(5)
                st.write(top_diseases)

        # Comparative Analysis
        with st.expander("State-wise Comparison"):
            col1, col2 = st.columns(2)
            with col1:
                state_comparison = filtered_df.groupby('LocationDesc')['DataValue'].agg(['mean', 'std'])
                state_comparison['ci_low'] = state_comparison['mean'] - 1.96*state_comparison['std']
                state_comparison['ci_high'] = state_comparison['mean'] + 1.96*state_comparison['std']
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=state_comparison.index,
                    y=state_comparison['mean'],
                    error_y=dict(
                        type='data',
                        array=state_comparison['std'],
                        visible=True)
                ))
                fig.update_layout(title="State-wise Prevalence with Confidence Range",
                                template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Statistical Summary")
                st.write(state_comparison.describe())

        # Geospatial Analysis
        with st.expander("Geospatial Distribution"):
            if all(col in filtered_df.columns for col in ['Latitude', 'Longitude']):
                geospatial_fig = px.density_mapbox(filtered_df, lat='Latitude', lon='Longitude', 
                                                 z='DataValue', radius=20,
                                                 mapbox_style="carto-darkmatter",
                                                 zoom=3, height=600,
                                                 title="Disease Prevalence Heatmap")
                st.plotly_chart(geospatial_fig, use_container_width=True)
            else:
                st.warning("Geospatial data not available in the dataset")

        # Frequency Analysis
        with st.expander("Disease Frequency Analysis"):
            col1, col2 = st.columns(2)
            with col1:
                disease_freq = filtered_df['Topic'].value_counts().nlargest(10)
                freq_fig = px.bar(disease_freq, orientation='h', 
                                title="Most Frequent Diseases",
                                template="plotly_dark")
                st.plotly_chart(freq_fig, use_container_width=True)
            
            with col2:
                st.subheader("Prevalence Distribution")
                dist_fig = px.violin(filtered_df, y="DataValue", box=True,
                                   title="Prevalence Distribution",
                                   template="plotly_dark")
                st.plotly_chart(dist_fig, use_container_width=True)

    else:
        st.markdown("""
            <div style="text-align:center; padding:5rem;">
                <h2 style="color:#2A9D8F;">📁 Upload Data to Begin Analysis</h2>
                <p style="color:#264653;">Use the left sidebar to upload your CDC Chronic Disease dataset</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
