import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Function to calculate ROI
def calculate_roi(current_price, forecasted_price, initial_investment, leverage):
    if current_price <= 0:
        raise ValueError("Current price must be positive")
    if leverage < 1:
        raise ValueError("Leverage must be at least 1")
    
    position_size = initial_investment * leverage
    volume = position_size / current_price
    price_change = forecasted_price - current_price
    profit = price_change * volume
    roi = (profit / initial_investment) * 100  # ROI in percentage
    
    return {
        "ROI%": round(roi, 2),
        "Profit": round(profit, 2),
        "Volume": round(volume, 4),
        "Position Size": round(position_size, 2)
    }

# Function to analyze historical data
def analyze_historical(symbol, start_date, end_date):
    try:
        data = yf.download(symbol, start=start_date, end=end_date)
        if data.empty:
            return {"error": "No data found for the given symbol and date range"}
        
        prices = data['Adj Close']
        returns = prices.pct_change().dropna()
        
        analysis = {
            "Symbol": symbol,
            "Start Price": round(prices[0], 2),
            "End Price": round(prices[-1], 2),
            "Total Change%": round(((prices[-1] - prices[0]) / prices[0]) * 100, 2),
            "Average Daily Return%": round(returns.mean() * 100, 2),
            "Volatility (Std Dev)%": round(returns.std() * 100, 2),
            "Max Daily Gain%": round(returns.max() * 100, 2),
            "Max Daily Loss%": round(returns.min() * 100, 2)
        }
        
        return analysis
    
    except Exception as e:
        return {"error": str(e)}

# Streamlit App
st.title("Financial Calculator App")
st.write("Calculate ROI and analyze historical price movements for assets.")

# Sidebar for navigation
option = st.sidebar.selectbox("Choose an option", ["ROI Calculator", "Historical Analysis"])

if option == "ROI Calculator":
    st.header("ROI Calculator")
    current = st.number_input("Current Price", min_value=0.01, value=100.0)
    forecast = st.number_input("Forecasted Price", min_value=0.01, value=120.0)
    investment = st.number_input("Initial Investment", min_value=0.01, value=1000.0)
    leverage = st.number_input("Leverage", min_value=1.0, value=2.0)
    
    if st.button("Calculate ROI"):
        result = calculate_roi(current, forecast, investment, leverage)
        st.write("### ROI Calculation Results:")
        for k, v in result.items():
            st.write(f"{k}: {v}")

elif option == "Historical Analysis":
    st.header("Historical Price Analysis")
    symbol = st.text_input("Enter Asset Symbol (e.g., BTC-USD, AAPL)", "AAPL")
    start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
    end_date = st.date_input("End Date", pd.to_datetime("2023-01-01"))
    
    if st.button("Analyze"):
        result = analyze_historical(symbol, start_date, end_date)
        if 'error' in result:
            st.error(result['error'])
        else:
            st.write("### Historical Analysis Results:")
            for k, v in result.items():
                st.write(f"{k}: {v}")