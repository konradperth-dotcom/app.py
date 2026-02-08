import streamlit as st
import pandas as pd
import plotly.express as px
from garminconnect import Garmin
import datetime

# --- SETUP & LOGIN ---
st.set_page_config(page_title="Cape to Cape Training Tracker", layout="wide")
st.title("🚵‍♂️ Cape to Cape Prep Dashboard")

# You would set these in Streamlit "Secrets" for security
GARMIN_EMAIL = st.sidebar.text_input("Garmin Email")
GARMIN_PWD = st.sidebar.text_input("Garmin Password", type="password")

if st.sidebar.button("Sync Garmin Data"):
    try:
        client = Garmin(GARMIN_EMAIL, GARMIN_PWD)
        client.login()
        
        # Pull activities (last 30 days)
        activities = client.get_activities(0, 50) 
        df = pd.DataFrame(activities)
        
        # Filter for Cycling only
        df = df[df['activityType'].apply(lambda x: x['typeKey'] == 'cycling')]
        
        # Convert units (Garmin uses meters and seconds)
        df['Date'] = pd.to_datetime(df['startTimeLocal'])
        df['Distance (km)'] = df['distance'] / 1000
        df['Elevation Gain (m)'] = df['totalElevationGain']
        
        # --- GOAL TRACKING ---
        st.header("Progress vs. Goal")
        col1, col2 = st.columns(2)
        
        # Graph 1: Distance over time
        fig_dist = px.line(df, x='Date', y='Distance (km)', title="Ride Distances", markers=True)
        # Add a target line for your Cape to Cape long ride (e.g., 60km)
        fig_dist.add_hline(y=60, line_dash="dot", annotation_text="Race Stage Target", line_color="green")
        col1.plotly_chart(fig_dist)
        
        # Graph 2: Elevation Progress
        fig_elev = px.bar(df, x='Date', y='Elevation Gain (m)', title="Elevation per Ride")
        col2.plotly_chart(fig_elev)

        st.success("Synchronized with Garmin!")
        
    except Exception as e:
        st.error(f"Login failed: {e}")
else:
    st.info("Enter your Garmin credentials and hit 'Sync' to load your progress.")

# --- MANUAL GOALS TRACKING ---
st.sidebar.markdown("---")
st.sidebar.subheader("Race Countdown")
days_left = (datetime.date(2026, 10, 15) - datetime.date.today()).days
st.sidebar.metric("Days to Cape to Cape", days_left)
