import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Setup
st.set_page_config(layout="wide", page_title="Quant Portfolio Dashboard")
DATA_DIR = Path(r"C:\Users\arjju\OneDrive\Documents\code\yfinance_html")

st.title("📈 Multi-Horizon Asset Performance")

# 1. Sidebar Controls
st.sidebar.header("Settings")
window = st.sidebar.selectbox("Select Timeframe", [84, 72, 60, 36, 24, 12, 6, 3], index=2)
metric_y = st.sidebar.radio("Scatter Plot Y-Axis", ["Sharpe Ratio", "Sortino Ratio"])

# 2. Load Data based on selection
price_file = DATA_DIR / f"price_combined_{window}m.csv"
metrics_file = DATA_DIR / f"metrics_{window}m.csv"

if price_file.exists() and metrics_file.exists():
    df_price = pd.read_csv(price_file, index_col='Date')
    df_metrics = pd.read_csv(metrics_file)

    # 3. Line Chart (Price Growth)
    st.subheader(f"Normalized Growth ({window} Months)")
    fig_line = px.line(df_price, x=df_price.index, y=df_price.columns, 
                        labels={'value': 'Normalized Price', 'Date': ''})
    fig_line.update_layout(hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

    # 4. Scatter Plot (Risk vs Reward)
    st.subheader(f"Risk-Adjusted Return: {metric_y} vs Annualized Return")
    fig_scatter = px.scatter(
        df_metrics, 
        x="Ann. Return %", 
        y=metric_y, 
        text="Asset",
        hover_name="Asset",
        color="Ann. Return %",
        size=df_metrics[metric_y].clip(lower=0.1), # Size points by ratio
        labels={"Ann. Return %": "Annualized Return (%)"}
    )
    fig_scatter.update_traces(textposition='top center')
    st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.error("Data files not found. Please run your processing script first.")