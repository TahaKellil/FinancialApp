import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

# Alpha Vantage API Configuration
ALPHA_VANTAGE_API_KEY = "80ETPCUN6W2VSSQP"
ECONOMIC_CALENDAR_URL = "https://www.alphavantage.co/query?function=ECONOMIC_CALENDAR&apikey={}"

# Function to fetch macroeconomic events
def fetch_macroeconomic_events():
    url = ECONOMIC_CALENDAR_URL.format(ALPHA_VANTAGE_API_KEY)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data.get("results", []))
    return pd.DataFrame()

# Function to analyze event impact on prices
def analyze_event_impact(symbol, event_date, interval='5m'):
    try:
        event_date = pd.to_datetime(event_date)
        start_date = event_date - timedelta(hours=1)
        end_date = event_date + timedelta(hours=1)
        
        data = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False
        )
        
        if data.empty:
            return None
        
        pre_event_price = data.iloc[0]['Close']
        post_5m = data.iloc[1]['Close'] if len(data) > 1 else pre_event_price
        post_10m = data.iloc[2]['Close'] if len(data) > 2 else post_5m
        
        return {
            '5m_change': round(((post_5m - pre_event_price) / pre_event_price) * 100, 2),
            '10m_change': round(((post_10m - pre_event_price) / pre_event_price) * 100, 2),
            'pre_event_price': pre_event_price
        }
    
    except Exception as e:
        st.error(f"Error analyzing event impact: {str(e)}")
        return None

# Enhanced ROI Calculator with TipRanks Forecasts
def calculate_roi(current_price, low_target, avg_target, high_target, initial_investment, leverage, event_impact=0):
    if current_price <= 0:
        raise ValueError("Current price must be positive")
    
    # Adjust targets based on event impact
    adjusted_low = low_target * (1 + event_impact/100)
    adjusted_avg = avg_target * (1 + event_impact/100)
    adjusted_high = high_target * (1 + event_impact/100)
    
    # Calculate ROI for each target
    def _roi(target):
        position_size = initial_investment * leverage
        volume = position_size / current_price
        price_change = target - current_price
        profit = price_change * volume
        roi = (profit / initial_investment) * 100
        return round(roi, 2), round(profit, 2), round(volume, 4)
    
    roi_low, profit_low, volume_low = _roi(adjusted_low)
    roi_avg, profit_avg, volume_avg = _roi(adjusted_avg)
    roi_high, profit_high, volume_high = _roi(adjusted_high)
    
    return {
        "Low Target ROI%": roi_low,
        "Low Target Profit": profit_low,
        "Low Target Volume": volume_low,
        "Avg Target ROI%": roi_avg,
        "Avg Target Profit": profit_avg,
        "Avg Target Volume": volume_avg,
        "High Target ROI%": roi_high,
        "High Target Profit": profit_high,
        "High Target Volume": volume_high,
    }

# Streamlit App
st.title("Advanced Financial Calculator")
st.write("ROI Calculator with TipRanks Forecasts and Macroeconomic Event Impact Analysis")

# Sidebar for navigation
option = st.sidebar.selectbox("Choose an option", ["ROI Calculator", "Macroeconomic Events"])

if option == "ROI Calculator":
    st.header("ROI Calculator with TipRanks Forecasts")
    
    # Inputs for TipRanks Forecasts
    current_price = st.number_input("Current Price ($)", min_value=0.01, value=100.0)
    low_target = st.number_input("Low Target ($)", min_value=0.01, value=90.0)
    avg_target = st.number_input("Average Target ($)", min_value=0.01, value=110.0)
    high_target = st.number_input("High Target ($)", min_value=0.01, value=130.0)
    
    # Investment Parameters
    initial_investment = st.number_input("Initial Investment ($)", min_value=0.01, value=1000.0)
    leverage = st.number_input("Leverage Ratio", min_value=1.0, value=2.0)
    
    # Event Impact (optional)
    event_impact = st.number_input("Event Impact (%)", value=0.0, help="Adjust ROI based on macroeconomic event impact.")
    
    if st.button("Calculate ROI"):
        results = calculate_roi(
            current_price,
            low_target,
            avg_target,
            high_target,
            initial_investment,
            leverage,
            event_impact
        )
        
        st.write("### ROI Calculation Results")
        st.write(f"**Low Target ROI:** {results['Low Target ROI%']}%")
        st.write(f"**Low Target Profit:** ${results['Low Target Profit']}")
        st.write(f"**Low Target Volume:** {results['Low Target Volume']}")
        
        st.write(f"**Average Target ROI:** {results['Avg Target ROI%']}%")
        st.write(f"**Average Target Profit:** ${results['Avg Target Profit']}")
        st.write(f"**Average Target Volume:** {results['Avg Target Volume']}")
        
        st.write(f"**High Target ROI:** {results['High Target ROI%']}%")
        st.write(f"**High Target Profit:** ${results['High Target Profit']}")
        st.write(f"**High Target Volume:** {results['High Target Volume']}")

elif option == "Macroeconomic Events":
    st.header("Macroeconomic Event Calendar")
    events = fetch_macroeconomic_events()
    
    if not events.empty:
        selected_event = st.selectbox("Select Economic Event", events['event'])
        event_data = events[events['event'] == selected_event].iloc[0]
        st.write(f"**{event_data['event']}**")
        st.write(f"Date: {event_data['date']}")streamlit run app.py --server.port $PORT
        st.write(f"Country: {event_data['country']}")
        st.write(f"Impact: {event_data['impact']}")
        
        if st.button("Analyze Historical Impact"):
            symbol = st.text_input("Enter Asset Symbol", "AAPL")
            impact_data = analyze_event_impact(symbol, event_data['date'])
            
            if impact_data:
                st.write("### Price Movement Analysis")
                st.write(f"5-minute Change: {impact_data['5m_change']}%")
                st.write(f"10-minute Change: {impact_data['10m_change']}%")
                event_impact = (impact_data['5m_change'] + impact_data['10m_change']) / 2
                st.session_state.event_impact = event_impact
    else:
        st.warning("No upcoming economic events found")