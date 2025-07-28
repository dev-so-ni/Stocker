# app.py (Updated, more stable version)

import streamlit as st
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- Page Configuration ---
st.set_page_config(
    page_title="Personal Stock Analyzer",
    page_icon="chart_with_upwards_trend",
    layout="wide"
)

# --- VADER Sentiment Analyzer ---
analyzer = SentimentIntensityAnalyzer()

# --- Helper Functions with Caching ---

@st.cache_data(ttl="1h")  # Cache data for 1 hour
def get_stock_data(ticker_symbol):
    """Fetches all necessary stock data from yfinance."""
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    hist = stock.history(period="3mo") # Get 3 months of history
    news = stock.news
    return info, hist, news

def get_sentiment(text):
    """Performs VADER sentiment analysis and returns score and emoji."""
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05:
        return "Positive", "😊", score
    elif score <= -0.05:
        return "Negative", "😟", score
    else:
        return "Neutral", "😐", score

# --- Main Application ---

st.title("🇮🇳 Personal Stock Analyzer")
st.caption("A personalized tool to analyze price drops and market sentiment.")

ticker = st.text_input("Enter Stock Ticker (e.g., RELIANCE.NS, TCS.BO)", "RELIANCE.NS").upper()

if ticker:
    try:
        # --- Fetch Data ---
        info, hist, news = get_stock_data(ticker)

        # Check if the ticker is valid
        if not info or info.get('longName') is None:
            st.error(f"Invalid Ticker: '{ticker}'. Please check the symbol and exchange (e.g., use .NS for NSE).")
        else:
            # --- Header and Price Metrics ---
            st.header(f"{info.get('longName', 'N/A')} ({info.get('symbol', 'N/A')})")

            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = info.get('previousClose', 0)
            price_change = current_price - previous_close
            percent_change = (price_change / previous_close) * 100 if previous_close else 0

            # Calculate drop from recent high
            high_60d = hist['High'].max()
            drop_from_high = ((current_price - high_60d) / high_60d) * 100

            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"₹{current_price:,.2f}", f"{price_change:,.2f} ({percent_change:.2f}%)")
            col2.metric("60-Day High", f"₹{high_60d:,.2f}", f"{drop_from_high:.2f}% Drop")
            col3.metric("Market Cap", f"₹{info.get('marketCap', 0)/1e7:,.0f} Cr")

            st.divider()

            # --- Core Competence & Sentiment Analysis ---
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🏢 Core Competence")
                st.info(info.get('longBusinessSummary', 'No business summary available.'))

            with col2:
                st.subheader("📰 Recent News & Sentiment")
                if news:
                    with st.expander("Click to see news analysis", expanded=True):
                        for item in news[:5]: # Show top 5 news items
                            title = item['title']
                            publisher = item['publisher']
                            sentiment_label, sentiment_emoji, score = get_sentiment(title)
                            st.markdown(f"**{title}** ({publisher})")
                            st.write(f"Sentiment: {sentiment_label} {sentiment_emoji} (Score: {score:.2f})")
                            st.markdown("---")
                else:
                    st.write("No recent news found.")
            
            st.divider()
            
            # --- Bulk & Block Deals Section ---
            st.subheader("💼 Top Investor Activity (Bulk & Block Deals)")
            st.info("Please check the official NSE website for the most accurate data.")
            plain_symbol = ticker.split('.')[0]
            st.markdown(f'''
                * [**Check for Bulk Deals on NSE**](https://www.nseindia.com/get-quotes/equity?symbol={plain_symbol}#security-information-bulk-deals)
                * [**Check for Block Deals on NSE**](https://www.nseindia.com/get-quotes/equity?symbol={plain_symbol}#security-information-block-deals)
            ''', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.warning("This could be due to an invalid ticker or a network issue. Please try again.")

st.divider()
st.caption("Disclaimer: This is an informational tool, not financial advice. Always do your own research (DYOR).")
