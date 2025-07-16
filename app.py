import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import threading
import time
import yfinance as yf
from apscheduler.schedulers.background import BackgroundScheduler

# Import main.py logic
from main import (
    analyze_ticker, 
    PORTFOLIO,
    query_past_insights,
    update_agent_system_messages,
    query_knowledge_evolution,
    conn, cursor,
    daily_analysis
)

# Streamlit page configuration
st.set_page_config(
    page_title="Multi-Agent Portfolio Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = BackgroundScheduler()
if 'analysis_running' not in st.session_state:
    st.session_state.analysis_running = False
if 'events' not in st.session_state:
    st.session_state.events = []
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = PORTFOLIO.copy()

# Database functions for dashboard
def get_all_insights():
    """Get all insights from database for dashboard display"""
    cursor.execute("""
        SELECT ticker, insight, timestamp 
        FROM insights 
        ORDER BY timestamp DESC
    """)
    return cursor.fetchall()

def get_insights_by_ticker(ticker):
    """Get insights for specific ticker"""
    cursor.execute("""
        SELECT insight, timestamp 
        FROM insights 
        WHERE ticker = ? 
        ORDER BY timestamp DESC
    """, (ticker,))
    return cursor.fetchall()

def get_portfolio_summary():
    """Get portfolio summary statistics"""
    portfolio_data = []
    for ticker in st.session_state.portfolio:
        try:
            # Get stock data
            data = yf.download(ticker, period="5d", progress=False)
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                volatility = data['Close'].pct_change().std()
                
                # Get insight count
                cursor.execute("SELECT COUNT(*) FROM insights WHERE ticker = ?", (ticker,))
                insight_count = cursor.fetchone()[0]
                
                portfolio_data.append({
                    'Ticker': ticker,
                    'Current Price': f"${current_price:.2f}",
                    'Volatility': f"{volatility:.4f}",
                    'Impact Level': 'High' if volatility > 0.05 else 'Medium' if volatility > 0.02 else 'Low',
                    'Insights': insight_count
                })
        except Exception as e:
            st.error(f"Error loading data for {ticker}: {e}")
    
    return pd.DataFrame(portfolio_data)

def add_event(event_type, ticker, message):
    """Add event to session state for display"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.events.append({
        'timestamp': timestamp,
        'type': event_type,
        'ticker': ticker,
        'message': message
    })
    # Keep only last 50 events
    st.session_state.events = st.session_state.events[-50:]

def background_analysis():
    """Background analysis function for scheduler"""
    try:
        add_event('INFO', 'SYSTEM', 'Starting scheduled portfolio analysis')
        daily_analysis()
        add_event('SUCCESS', 'SYSTEM', 'Scheduled portfolio analysis completed')
    except Exception as e:
        add_event('ERROR', 'SYSTEM', f'Scheduled analysis failed: {str(e)}')

# Main app
def main():
    st.title("🚀 Multi-Agent Portfolio Analysis System")
    st.markdown("*Powered by Grok 4 with Knowledge Evolution*")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard", "Ad-hoc Analysis", "Knowledge Evolution", "Events", "Settings"]
    )
    
    # Background scheduling controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("Background Scheduling")
    
    if st.sidebar.button("Start Scheduled Analysis"):
        if not st.session_state.scheduler.running:
            st.session_state.scheduler.add_job(
                background_analysis, 
                'interval', 
                seconds=3600,  # Run every hour
                id='portfolio_analysis'
            )
            st.session_state.scheduler.start()
            st.session_state.analysis_running = True
            st.sidebar.success("✓ Scheduled analysis started (hourly)")
            add_event('INFO', 'SYSTEM', 'Background scheduling started')
        else:
            st.sidebar.warning("Scheduler already running")
    
    if st.sidebar.button("Stop Scheduled Analysis"):
        if st.session_state.scheduler.running:
            st.session_state.scheduler.shutdown()
            st.session_state.analysis_running = False
            st.sidebar.success("✓ Scheduled analysis stopped")
            add_event('INFO', 'SYSTEM', 'Background scheduling stopped')
        else:
            st.sidebar.warning("Scheduler not running")
    
    # Display scheduler status
    status = "🟢 Running" if st.session_state.analysis_running else "🔴 Stopped"
    st.sidebar.markdown(f"**Status:** {status}")
    
    # Page routing
    if page == "Dashboard":
        dashboard_page()
    elif page == "Ad-hoc Analysis":
        adhoc_analysis_page()
    elif page == "Knowledge Evolution":
        knowledge_evolution_page()
    elif page == "Events":
        events_page()
    elif page == "Settings":
        settings_page()

def dashboard_page():
    """Main dashboard page"""
    st.header("📊 Portfolio Dashboard")
    
    # Portfolio summary
    st.subheader("Portfolio Overview")
    portfolio_df = get_portfolio_summary()
    
    if not portfolio_df.empty:
        # Display portfolio table
        st.dataframe(portfolio_df, use_container_width=True)
        
        # Portfolio metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Stocks", len(st.session_state.portfolio))
        with col2:
            high_impact = len(portfolio_df[portfolio_df['Impact Level'] == 'High'])
            st.metric("High Impact", high_impact)
        with col3:
            total_insights = portfolio_df['Insights'].sum()
            st.metric("Total Insights", total_insights)
        with col4:
            avg_volatility = portfolio_df['Volatility'].str.replace('', '').astype(float).mean()
            st.metric("Avg Volatility", f"{avg_volatility:.4f}")
    else:
        st.info("No portfolio data available")
    
    # Recent insights
    st.subheader("Recent Insights")
    insights = get_all_insights()
    
    if insights:
        insights_df = pd.DataFrame(insights, columns=['Ticker', 'Insight', 'Timestamp'])
        
        # Display recent insights
        for _, row in insights_df.head(10).iterrows():
            # Format timestamp string directly from the raw timestamp
            timestamp_str = str(row['Timestamp'])[:16]  # Get YYYY-MM-DD HH:MM format
            with st.expander(f"{row['Ticker']} - {timestamp_str}"):
                st.write(row['Insight'])
    else:
        st.info("No insights available")
    
    # Insights by ticker chart
    if insights:
        st.subheader("Insights Distribution")
        ticker_counts = insights_df['Ticker'].value_counts()
        fig = px.bar(
            x=ticker_counts.index, 
            y=ticker_counts.values,
            labels={'x': 'Ticker', 'y': 'Number of Insights'},
            title="Insights by Ticker"
        )
        st.plotly_chart(fig, use_container_width=True)

def adhoc_analysis_page():
    """Ad-hoc analysis page"""
    st.header("🔍 Ad-hoc Analysis")
    
    # Analysis form
    with st.form("analysis_form"):
        st.subheader("Analyze New Ticker")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            ticker = st.text_input("Enter Ticker Symbol", placeholder="e.g., TSLA, GOOGL, MSFT").upper()
        with col2:
            st.write("")  # Spacer
            submitted = st.form_submit_button("Analyze", type="primary")
        
        add_to_portfolio = st.checkbox("Add to portfolio after analysis")
    
    if submitted and ticker:
        if ticker.strip():
            with st.spinner(f"Analyzing {ticker}... This may take a moment."):
                try:
                    # Run analysis
                    analyze_ticker(ticker)
                    
                    # Add to portfolio if requested
                    if add_to_portfolio and ticker not in st.session_state.portfolio:
                        st.session_state.portfolio.append(ticker)
                        PORTFOLIO.append(ticker)
                        st.success(f"✓ {ticker} added to portfolio")
                    
                    # Add event
                    add_event('SUCCESS', ticker, f'Ad-hoc analysis completed for {ticker}')
                    
                    st.success(f"✓ Analysis completed for {ticker}")
                    
                    # Display recent insights for this ticker
                    st.subheader(f"Recent Insights for {ticker}")
                    ticker_insights = get_insights_by_ticker(ticker)
                    
                    if ticker_insights:
                        for insight, timestamp in ticker_insights[:5]:
                            with st.expander(f"Insight - {timestamp}"):
                                st.write(insight)
                    else:
                        st.info(f"No insights found for {ticker}")
                        
                except Exception as e:
                    st.error(f"Error analyzing {ticker}: {str(e)}")
                    add_event('ERROR', ticker, f'Analysis failed: {str(e)}')
        else:
            st.warning("Please enter a valid ticker symbol")
    
    # Quick analysis buttons
    st.subheader("Quick Analysis")
    st.markdown("Click to analyze popular stocks:")
    
    quick_tickers = ['TSLA', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA']
    cols = st.columns(len(quick_tickers))
    
    for i, qticker in enumerate(quick_tickers):
        with cols[i]:
            if st.button(qticker):
                with st.spinner(f"Analyzing {qticker}..."):
                    try:
                        analyze_ticker(qticker)
                        st.success(f"✓ {qticker} analyzed")
                        add_event('SUCCESS', qticker, f'Quick analysis completed for {qticker}')
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        add_event('ERROR', qticker, f'Quick analysis failed: {str(e)}')

def knowledge_evolution_page():
    """Knowledge evolution page"""
    st.header("🧠 Knowledge Evolution")
    
    # Select ticker for evolution analysis
    if st.session_state.portfolio:
        selected_ticker = st.selectbox("Select Ticker", st.session_state.portfolio)
        
        if selected_ticker:
            # Evolution patterns
            st.subheader(f"Evolution Patterns for {selected_ticker}")
            evolution_info = query_knowledge_evolution(selected_ticker)
            st.info(evolution_info)
            
            # Past insights
            st.subheader("Historical Insights")
            past_insights = query_past_insights(selected_ticker, limit=10)
            
            if past_insights != "No previous insights found.":
                insights_list = past_insights.split(" | ")
                for insight in insights_list:
                    st.write(f"• {insight}")
            else:
                st.info("No historical insights found")
            
            # Knowledge evolution timeline
            st.subheader("Knowledge Timeline")
            ticker_insights = get_insights_by_ticker(selected_ticker)
            
            if ticker_insights:
                timeline_data = []
                for insight, timestamp in ticker_insights:
                    timeline_data.append({
                        'timestamp': timestamp,
                        'insight': insight[:100] + "..." if len(insight) > 100 else insight,
                        'type': 'Refined' if insight.startswith('REFINED:') else 'Original'
                    })
                
                timeline_df = pd.DataFrame(timeline_data)
                # Keep timestamp as string for plotting
                
                # Create timeline chart
                fig = px.scatter(
                    timeline_df, 
                    x='timestamp', 
                    y='type',
                    hover_data=['insight'],
                    title=f"Knowledge Evolution Timeline for {selected_ticker}"
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tickers in portfolio for evolution analysis")

def events_page():
    """Events and alerts page"""
    st.header("⚡ Events & Alerts")
    
    # Event controls
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Clear Events"):
            st.session_state.events = []
            st.success("Events cleared")
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=False)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Display events
    if st.session_state.events:
        st.subheader("Recent Events")
        
        for event in reversed(st.session_state.events[-20:]):  # Show last 20 events
            # Event styling based on type
            if event['type'] == 'ERROR':
                st.error(f"🔴 **{event['timestamp']}** | {event['ticker']} | {event['message']}")
            elif event['type'] == 'SUCCESS':
                st.success(f"🟢 **{event['timestamp']}** | {event['ticker']} | {event['message']}")
            elif event['type'] == 'WARNING':
                st.warning(f"🟡 **{event['timestamp']}** | {event['ticker']} | {event['message']}")
            else:
                st.info(f"🔵 **{event['timestamp']}** | {event['ticker']} | {event['message']}")
    else:
        st.info("No events to display")

def settings_page():
    """Settings page"""
    st.header("⚙️ Settings")
    
    # Portfolio management
    st.subheader("Portfolio Management")
    
    # Display current portfolio
    st.write("**Current Portfolio:**")
    for ticker in st.session_state.portfolio:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"• {ticker}")
        with col2:
            if st.button(f"Remove", key=f"remove_{ticker}"):
                st.session_state.portfolio.remove(ticker)
                PORTFOLIO.remove(ticker)
                st.success(f"Removed {ticker}")
                st.rerun()
    
    # Add new ticker to portfolio
    st.subheader("Add Ticker to Portfolio")
    new_ticker = st.text_input("New Ticker Symbol").upper()
    if st.button("Add to Portfolio"):
        if new_ticker and new_ticker not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_ticker)
            PORTFOLIO.append(new_ticker)
            st.success(f"Added {new_ticker} to portfolio")
            st.rerun()
        elif new_ticker in st.session_state.portfolio:
            st.warning(f"{new_ticker} already in portfolio")
    
    # Database management
    st.subheader("Database Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Insights"):
            insights = get_all_insights()
            if insights:
                df = pd.DataFrame(insights, columns=['Ticker', 'Insight', 'Timestamp'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with col2:
        if st.button("Clear Database", type="secondary"):
            if st.button("Confirm Clear", type="secondary"):
                cursor.execute("DELETE FROM insights")
                conn.commit()
                st.success("Database cleared")
    
    # System info
    st.subheader("System Information")
    st.write(f"**Total Insights:** {len(get_all_insights())}")
    st.write(f"**Portfolio Size:** {len(st.session_state.portfolio)}")
    st.write(f"**Scheduler Status:** {'Running' if st.session_state.analysis_running else 'Stopped'}")

if __name__ == "__main__":
    main() 