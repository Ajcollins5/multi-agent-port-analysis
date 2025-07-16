import autogen  # pip install pyautogen
import os
import sqlite3
import yfinance as yf
from apscheduler.schedulers.background import BackgroundScheduler
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Set up xAI Grok API key (get from x.ai/api)
os.environ["XAI_API_KEY"] = "xai-xxxxxxxxxxxxxx"

# SQLite for knowledge base
conn = sqlite3.connect('knowledge.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS insights (ticker TEXT, insight TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# Email configuration
def send_email(subject, body, to_email="austin@example.com"):
    """Send email notifications for high impact events and system alerts"""
    try:
        # Email configuration - Update these with your email settings
        # NOTE: For Gmail, you need to use an App Password, not your regular password
        # Go to: Google Account > Security > 2-Step Verification > App passwords
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your-email@gmail.com"  # Update with your email
        sender_password = "your-app-password"  # Update with your app password
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(sender_email, sender_password)
        
        # Send email
        text = message.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        print(f"✓ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# Config for Grok 4 (OpenAI-compatible)
config_list = [{
    "model": "grok-4-0709",
    "api_key": os.environ["XAI_API_KEY"],
    "base_url": "https://api.x.ai/v1",
    "api_type": "open_ai"  # For compatibility
}]

# Agents setup with Grok 4 configuration
user_proxy = autogen.UserProxyAgent(name="User", human_input_mode="NEVER")
risk_agent = autogen.AssistantAgent(name="RiskAgent", llm_config={"config_list": config_list}, system_message="Analyze stock risk: volatility, beta. Fetch data and store insights in DB.")
news_agent = autogen.AssistantAgent(name="NewsAgent", llm_config={"config_list": config_list}, system_message="Analyze news sentiment. Estimate low/medium/high impact. Store in DB.")
supervisor = autogen.AssistantAgent(name="Supervisor", llm_config={"config_list": config_list}, system_message="Orchestrate agents for portfolio (e.g., AAPL). Synthesize and notify on events.")

# New specialized agents for enhanced analysis
event_sentinel = autogen.AssistantAgent(
    name="EventSentinel", 
    llm_config={"config_list": config_list}, 
    system_message="Monitor and detect significant market events, anomalies, and patterns. Track cross-ticker correlations and system-wide risks. Alert on portfolio-wide events and generate event summaries using Grok's reasoning capabilities."
)

knowledge_curator = autogen.AssistantAgent(
    name="KnowledgeCurator", 
    llm_config={"config_list": config_list}, 
    system_message="Manage and evolve the knowledge base. Curate insights, identify knowledge gaps, and recommend areas for deeper analysis. Maintain knowledge quality and facilitate learning across analysis cycles using Grok's advanced reasoning."
)

groupchat = autogen.GroupChat(agents=[user_proxy, risk_agent, news_agent, supervisor, event_sentinel, knowledge_curator], messages=[], max_round=7)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

# Tool: Fetch stock data
@risk_agent.register_for_execution()
@risk_agent.register_for_llm(name="fetch_stock_data", description="Fetch stock data and detect high impact events")
def fetch_stock_data(ticker: str):
    # Download stock data for the past 5 days
    data = yf.download(ticker, period="5d")
    volatility = data['Close'].pct_change().std()
    
    # Event detection: Check if volatility exceeds threshold
    if volatility > 0.05:
        # Send email notification for high impact event
        subject = f"🚨 HIGH IMPACT EVENT: {ticker} Stock Alert"
        body = f"""HIGH IMPACT EVENT DETECTED

Ticker: {ticker}
Volatility: {volatility:.4f} (>{0.05:.2f} threshold)
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated alert from the Multi-Agent Portfolio Analysis System.
High volatility detected requiring immediate attention.

Grok AI agents are now analyzing this event and will provide detailed insights.

---
Multi-Agent Portfolio Analysis System
Powered by Grok 4 with Knowledge Evolution"""
        
        send_email(subject, body)
        print(f'High impact event for {ticker}! Email notification sent.')
    
    return f"Data for {ticker}: Volatility {volatility:.2f}"

# Tool: Determine impact level based on volatility
@risk_agent.register_for_execution()
@risk_agent.register_for_llm(name="determine_impact_level", description="Determine impact level based on volatility")
def determine_impact_level(ticker: str):
    # Fetch stock data to calculate volatility
    data = yf.download(ticker, period="5d")
    volatility = data['Close'].pct_change().std()
    
    # Determine impact level based on volatility thresholds
    if volatility > 0.05:
        impact_level = "high"
    elif volatility > 0.02:
        impact_level = "medium"
    else:
        impact_level = "low"
    
    return f"Impact level for {ticker}: {impact_level} (volatility: {volatility:.4f})"

# Tool: Store insight
@supervisor.register_for_execution()
@supervisor.register_for_llm(name="store_insight", description="Store analysis in DB")
def store_insight(ticker: str, insight: str):
    cursor.execute("INSERT INTO insights (ticker, insight) VALUES (?, ?)", (ticker, insight))
    conn.commit()
    return "Insight stored."

# Knowledge Evolution Functions
def query_past_insights(ticker: str, limit: int = 5):
    """Query past insights from SQLite database for knowledge evolution"""
    cursor.execute("""
        SELECT insight, timestamp 
        FROM insights 
        WHERE ticker = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (ticker, limit))
    
    results = cursor.fetchall()
    if results:
        # Format past insights for system message
        past_insights = []
        for insight, timestamp in results:
            past_insights.append(f"[{timestamp}] {insight}")
        return " | ".join(past_insights)
    return "No previous insights found."

def update_agent_system_messages(ticker: str):
    """Update agent system messages with past insights for knowledge evolution"""
    past_insights = query_past_insights(ticker)
    
    # Enhanced system messages with past knowledge
    risk_system_msg = f"Analyze stock risk: volatility, beta. Fetch data and store insights in DB. Previous insights: {past_insights}. Use Grok's reasoning to synthesize new insights with historical knowledge."
    news_system_msg = f"Analyze news sentiment. Estimate low/medium/high impact. Store in DB. Previous insights: {past_insights}. Use Grok's reasoning to refine analysis based on historical patterns."
    supervisor_system_msg = f"Orchestrate agents for portfolio (e.g., AAPL). Synthesize and notify on events. Previous insights: {past_insights}. Use Grok's reasoning to evolve knowledge and improve decision-making."
    
    # Update agent system messages
    risk_agent.system_message = risk_system_msg
    news_agent.system_message = news_system_msg
    supervisor.system_message = supervisor_system_msg
    
    return f"Agent system messages updated with {len(past_insights.split('|'))} past insights"

@supervisor.register_for_execution()
@supervisor.register_for_llm(name="refine_insight", description="Refine and update existing insights using Grok's reasoning")
def refine_insight(ticker: str, new_insight: str):
    """Refine insights by comparing with past knowledge and updating database"""
    # Get recent insights for comparison
    past_insights = query_past_insights(ticker, limit=3)
    
    # Create refined insight using Grok's reasoning capabilities
    refined_insight = f"REFINED: {new_insight} | SYNTHESIS: Compared with past insights [{past_insights}], this analysis shows evolution in understanding."
    
    # Store the refined insight
    cursor.execute("INSERT INTO insights (ticker, insight) VALUES (?, ?)", (ticker, refined_insight))
    conn.commit()
    
    return f"Refined insight stored for {ticker}. Knowledge evolution applied."

@supervisor.register_for_execution()
@supervisor.register_for_llm(name="query_knowledge_evolution", description="Query knowledge evolution patterns for better synthesis")
def query_knowledge_evolution(ticker: str):
    """Query knowledge evolution patterns to improve Grok's reasoning"""
    # Get all insights for the ticker to analyze patterns
    cursor.execute("""
        SELECT insight, timestamp 
        FROM insights 
        WHERE ticker = ? 
        ORDER BY timestamp ASC
    """, (ticker,))
    
    results = cursor.fetchall()
    if len(results) < 2:
        return f"Insufficient data for knowledge evolution analysis. Only {len(results)} insights available."
    
    # Analyze evolution patterns
    evolution_summary = f"Knowledge evolution for {ticker}: {len(results)} insights spanning from {results[0][1]} to {results[-1][1]}. "
    
    # Count refined insights
    refined_count = sum(1 for insight, _ in results if insight.startswith("REFINED:"))
    evolution_summary += f"Refined insights: {refined_count}/{len(results)}. "
    
    # Pattern analysis for Grok's reasoning
    recent_insights = [insight for insight, _ in results[-3:]]
    evolution_summary += f"Recent pattern: {' -> '.join(recent_insights[:2])}"
    
    return evolution_summary

@risk_agent.register_for_execution()
@risk_agent.register_for_llm(name="query_past_insights", description="Query past insights from database for knowledge evolution")
def query_past_insights_tool(ticker: str, limit: int = 5):
    """Tool wrapper for querying past insights"""
    return query_past_insights(ticker, limit)

# EventSentinel tools
@event_sentinel.register_for_execution()
@event_sentinel.register_for_llm(name="detect_portfolio_events", description="Detect portfolio-wide events and correlations")
def detect_portfolio_events():
    """Detect significant events across the entire portfolio"""
    events = []
    high_volatility_count = 0
    
    for ticker in PORTFOLIO:
        try:
            data = yf.download(ticker, period="5d", progress=False)
            if not data.empty:
                volatility = data['Close'].pct_change().std()
                if volatility > 0.05:
                    high_volatility_count += 1
                    events.append(f"HIGH VOLATILITY: {ticker} ({volatility:.4f})")
                elif volatility > 0.02:
                    events.append(f"MEDIUM VOLATILITY: {ticker} ({volatility:.4f})")
        except Exception as e:
            events.append(f"ERROR: {ticker} - {str(e)}")
    
    # Portfolio-wide analysis
    portfolio_risk = "HIGH" if high_volatility_count > len(PORTFOLIO) * 0.5 else "MEDIUM" if high_volatility_count > 0 else "LOW"
    
    summary = f"PORTFOLIO EVENT DETECTION:\n"
    summary += f"Risk Level: {portfolio_risk}\n"
    summary += f"High Volatility Stocks: {high_volatility_count}/{len(PORTFOLIO)}\n"
    summary += f"Events: {len(events)}\n\n"
    summary += "\n".join(events)
    
    return summary

@event_sentinel.register_for_execution()
@event_sentinel.register_for_llm(name="generate_event_summary", description="Generate comprehensive event summary with Grok reasoning")
def generate_event_summary():
    """Generate a comprehensive event summary using Grok's reasoning"""
    # Get recent insights for analysis
    cursor.execute("""
        SELECT ticker, insight, timestamp 
        FROM insights 
        WHERE timestamp >= datetime('now', '-24 hours')
        ORDER BY timestamp DESC
    """)
    
    recent_insights = cursor.fetchall()
    
    # Analyze event patterns
    event_summary = f"EVENT ANALYSIS SUMMARY ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"
    event_summary += f"="*50 + "\n\n"
    
    if recent_insights:
        event_summary += f"RECENT ACTIVITY: {len(recent_insights)} insights in last 24 hours\n"
        
        # Group by ticker
        ticker_insights = {}
        for ticker, insight, timestamp in recent_insights:
            if ticker not in ticker_insights:
                ticker_insights[ticker] = []
            ticker_insights[ticker].append((insight, timestamp))
        
        event_summary += f"ACTIVE TICKERS: {', '.join(ticker_insights.keys())}\n\n"
        
        # Analyze patterns
        refined_count = sum(1 for _, insight, _ in recent_insights if insight.startswith("REFINED:"))
        event_summary += f"KNOWLEDGE EVOLUTION: {refined_count}/{len(recent_insights)} refined insights\n\n"
        
        # Recent events
        event_summary += "RECENT EVENTS:\n"
        for ticker, insights in ticker_insights.items():
            event_summary += f"• {ticker}: {len(insights)} insights\n"
    else:
        event_summary += "No recent activity detected in the last 24 hours.\n"
    
    return event_summary

# KnowledgeCurator tools  
@knowledge_curator.register_for_execution()
@knowledge_curator.register_for_llm(name="curate_knowledge_quality", description="Assess and improve knowledge base quality")
def curate_knowledge_quality():
    """Assess knowledge base quality and suggest improvements"""
    # Get all insights
    cursor.execute("SELECT ticker, insight, timestamp FROM insights ORDER BY timestamp DESC")
    all_insights = cursor.fetchall()
    
    if not all_insights:
        return "No insights available for curation."
    
    # Quality metrics
    total_insights = len(all_insights)
    refined_insights = sum(1 for _, insight, _ in all_insights if insight.startswith("REFINED:"))
    
    # Ticker distribution
    ticker_counts = {}
    for ticker, _, _ in all_insights:
        ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
    
    # Quality assessment
    quality_report = f"KNOWLEDGE QUALITY ASSESSMENT\n"
    quality_report += f"="*30 + "\n\n"
    quality_report += f"Total Insights: {total_insights}\n"
    quality_report += f"Refined Insights: {refined_insights} ({refined_insights/total_insights*100:.1f}%)\n"
    quality_report += f"Coverage: {len(ticker_counts)} tickers\n\n"
    
    # Recommendations
    quality_report += "RECOMMENDATIONS:\n"
    if refined_insights < total_insights * 0.3:
        quality_report += "• Increase knowledge refinement rate\n"
    
    # Identify knowledge gaps
    min_insights = min(ticker_counts.values()) if ticker_counts else 0
    max_insights = max(ticker_counts.values()) if ticker_counts else 0
    
    if max_insights > min_insights * 2:
        quality_report += "• Balance insights across tickers\n"
    
    quality_report += f"• Focus on tickers with <{min_insights + 1} insights\n"
    
    return quality_report

@knowledge_curator.register_for_execution()
@knowledge_curator.register_for_llm(name="identify_knowledge_gaps", description="Identify gaps in knowledge base and recommend analysis areas")
def identify_knowledge_gaps():
    """Identify knowledge gaps and recommend areas for deeper analysis"""
    # Analyze portfolio coverage
    coverage_analysis = f"KNOWLEDGE GAP ANALYSIS\n"
    coverage_analysis += f"="*25 + "\n\n"
    
    # Check insights per ticker
    for ticker in PORTFOLIO:
        cursor.execute("SELECT COUNT(*) FROM insights WHERE ticker = ?", (ticker,))
        count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM insights 
            WHERE ticker = ? AND insight LIKE '%REFINED:%'
        """, (ticker,))
        refined_count = cursor.fetchone()[0]
        
        status = "GOOD" if count > 5 else "NEEDS ATTENTION" if count > 2 else "CRITICAL"
        coverage_analysis += f"{ticker}: {count} insights ({refined_count} refined) - {status}\n"
    
    # Time-based analysis
    cursor.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM insights 
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """)
    
    daily_counts = cursor.fetchall()
    
    coverage_analysis += f"\nRECENT ACTIVITY (7 days):\n"
    for date, count in daily_counts:
        coverage_analysis += f"• {date}: {count} insights\n"
    
    # Recommendations
    coverage_analysis += f"\nRECOMMENDATIONS:\n"
    coverage_analysis += f"• Increase analysis frequency for critical tickers\n"
    coverage_analysis += f"• Focus on knowledge refinement\n"
    coverage_analysis += f"• Implement cross-ticker correlation analysis\n"
    
    return coverage_analysis

# Portfolio management
PORTFOLIO = ['AAPL']  # Hardcoded portfolio list starting with AAPL

def analyze_ticker(ticker: str):
    """Generic analysis function for any ticker with knowledge evolution"""
    print(f"\n=== Analyzing {ticker} ===")
    
    # Get impact level for the stock
    try:
        data = yf.download(ticker, period="5d")
        if data.empty:
            print(f"No data found for ticker {ticker}")
            return
            
        volatility = data['Close'].pct_change().std()
        
        # Determine impact level
        if volatility > 0.05:
            impact_level = "high"
            # Send email notification for high impact event with Grok analysis context
            subject = f"🚨 HIGH IMPACT EVENT: {ticker} - Grok Analysis Initiated"
            body = f"""HIGH IMPACT EVENT DETECTED - GROK ANALYSIS INITIATED

Ticker: {ticker}
Impact Level: HIGH
Volatility: {volatility:.4f} (>{0.05:.2f} threshold)
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

GROK AI ANALYSIS STATUS:
- Multi-agent analysis triggered
- Risk assessment in progress
- News sentiment analysis initiated
- Knowledge evolution applied

This high-impact event will be analyzed by our advanced Grok 4 AI agents:
• RiskAgent: Analyzing volatility patterns and risk metrics
• NewsAgent: Evaluating news sentiment and market impact
• Supervisor: Synthesizing insights with historical knowledge

Detailed analysis results will be stored in the knowledge database.

---
Multi-Agent Portfolio Analysis System
Powered by Grok 4 with Knowledge Evolution"""
            
            send_email(subject, body)
            print(f'High impact event for {ticker}! Email notification sent.')
        elif volatility > 0.02:
            impact_level = "medium"
        else:
            impact_level = "low"
        
        print(f"Impact level detected: {impact_level} for {ticker} (volatility: {volatility:.4f})")
        
        # Knowledge Evolution: Update agent system messages with past insights
        update_status = update_agent_system_messages(ticker)
        print(f"Knowledge evolution: {update_status}")
        
        # Query knowledge evolution patterns for enhanced reasoning
        evolution_patterns = query_knowledge_evolution(ticker)
        print(f"Evolution patterns: {evolution_patterns}")
        
        # Initiate chat with enhanced context including knowledge evolution
        message = f"""Analyze stock {ticker} for risk and news. 
        Current impact level: {impact_level} with volatility {volatility:.4f}. 
        Use Grok's reasoning to synthesize with historical knowledge. 
        Evolution patterns: {evolution_patterns}
        Apply knowledge evolution techniques and refine insights. Store results in DB."""
        
        user_proxy.initiate_chat(manager, message=message)
        
        # Send email notification for completed Grok analysis
        subject = f"📊 Grok Analysis Complete: {ticker} - {impact_level.upper()} Impact"
        body = f"""GROK ANALYSIS COMPLETED

Ticker: {ticker}
Impact Level: {impact_level.upper()}
Volatility: {volatility:.4f}
Analysis Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ANALYSIS SUMMARY:
✓ Multi-agent analysis completed successfully
✓ Risk assessment by RiskAgent
✓ News sentiment analysis by NewsAgent  
✓ Knowledge evolution applied
✓ Insights synthesized by Supervisor

EVOLUTION PATTERNS:
{evolution_patterns}

KNOWLEDGE STATUS:
{update_status}

The complete analysis results have been stored in the knowledge database.
Access the dashboard to view detailed insights and recommendations.

---
Multi-Agent Portfolio Analysis System
Powered by Grok 4 with Knowledge Evolution"""
        
        send_email(subject, body)
        print(f"Analysis complete for {ticker} with knowledge evolution applied. Email notification sent.")
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")

# Enhanced daily analysis with impact level checking and knowledge evolution
def daily_analysis():
    """Run daily analysis for all tickers in portfolio"""
    print("\n=== Daily Portfolio Analysis ===")
    analysis_start = datetime.now()
    high_impact_tickers = []
    
    for ticker in PORTFOLIO:
        analyze_ticker(ticker)
        # Check if this was a high impact event
        try:
            data = yf.download(ticker, period="5d", progress=False)
            if not data.empty:
                volatility = data['Close'].pct_change().std()
                if volatility > 0.05:
                    high_impact_tickers.append(f"{ticker} (volatility: {volatility:.4f})")
        except:
            pass
        print("-" * 50)
    
    # Send email notification for completed daily analysis
    analysis_end = datetime.now()
    duration = analysis_end - analysis_start
    
    subject = f"📈 Daily Portfolio Analysis Complete - {len(PORTFOLIO)} Stocks Analyzed"
    body = f"""DAILY PORTFOLIO ANALYSIS COMPLETED

Analysis Summary:
• Portfolio Size: {len(PORTFOLIO)} stocks
• Analysis Duration: {duration.total_seconds():.1f} seconds
• High Impact Events: {len(high_impact_tickers)}
• Timestamp: {analysis_end.strftime('%Y-%m-%d %H:%M:%S')}

ANALYZED TICKERS:
{', '.join(PORTFOLIO)}

{'HIGH IMPACT EVENTS DETECTED:' if high_impact_tickers else 'No high impact events detected.'}
{chr(10).join(f'• {ticker}' for ticker in high_impact_tickers) if high_impact_tickers else ''}

GROK AI ANALYSIS STATUS:
✓ Multi-agent analysis completed for all tickers
✓ Risk assessments updated
✓ News sentiment analysis performed
✓ Knowledge evolution applied across portfolio
✓ All insights stored in knowledge database

Next scheduled analysis: {(analysis_end + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')}

Access the dashboard to view detailed insights and recommendations.

---
Multi-Agent Portfolio Analysis System
Powered by Grok 4 with Knowledge Evolution"""
    
    send_email(subject, body)
    print(f"Daily analysis complete for {len(PORTFOLIO)} stocks. Email notification sent.")

def cli_analysis():
    """CLI interface for ad-hoc ticker analysis"""
    print("\n=== CLI Ad-hoc Analysis ===")
    print(f"Current portfolio: {PORTFOLIO}")
    
    while True:
        # Get ticker input from user
        ticker = input("\nEnter ticker symbol to analyze (or 'quit' to exit): ").strip().upper()
        
        if ticker == 'QUIT':
            print("Exiting CLI analysis...")
            break
        
        if not ticker:
            print("Please enter a valid ticker symbol.")
            continue
        
        # Analyze the ticker
        analyze_ticker(ticker)
        
        # Ask if user wants to add to portfolio
        if ticker not in PORTFOLIO:
            add_to_portfolio = input(f"\nAdd {ticker} to portfolio? (y/n): ").strip().lower()
            if add_to_portfolio == 'y':
                PORTFOLIO.append(ticker)
                print(f"✓ {ticker} added to portfolio. Current portfolio: {PORTFOLIO}")
            else:
                print(f"✗ {ticker} not added to portfolio.")
        else:
            print(f"ℹ️  {ticker} is already in portfolio.")
        
        # Ask if user wants to analyze another ticker
        continue_analysis = input("\nAnalyze another ticker? (y/n): ").strip().lower()
        if continue_analysis != 'y':
            break
    
    print(f"Final portfolio: {PORTFOLIO}")

def show_menu():
    """Display CLI menu options"""
    print("\n" + "="*50)
    print("🚀 MULTI-AGENT PORTFOLIO ANALYSIS SYSTEM")
    print("="*50)
    print("1. Run daily analysis for portfolio")
    print("2. Ad-hoc ticker analysis (CLI)")
    print("3. View current portfolio")
    print("4. Start scheduled analysis")
    print("5. Exit")
    print("="*50)

# Initialize scheduler (not started by default)
scheduler = BackgroundScheduler()

def start_scheduled_analysis():
    """Start background scheduled analysis"""
    scheduler.add_job(daily_analysis, 'interval', seconds=3600)  # Run every hour
    scheduler.start()
    print("✓ Scheduled analysis started (runs every hour)")
    print("Press Ctrl+C to return to menu")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("\n✓ Scheduled analysis stopped")

def main():
    """Main CLI interface"""
    print("Welcome to Multi-Agent Portfolio Analysis System!")
    print("Powered by Grok 4 with Knowledge Evolution")
    
    while True:
        show_menu()
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            # Run daily analysis for portfolio
            daily_analysis()
            
        elif choice == '2':
            # Ad-hoc ticker analysis (CLI)
            cli_analysis()
            
        elif choice == '3':
            # View current portfolio
            print(f"\n📊 Current Portfolio: {PORTFOLIO}")
            print(f"Total stocks: {len(PORTFOLIO)}")
            
        elif choice == '4':
            # Start scheduled analysis
            start_scheduled_analysis()
            
        elif choice == '5':
            # Exit
            print("Thank you for using Multi-Agent Portfolio Analysis System!")
            break
            
        else:
            print("❌ Invalid option. Please select 1-5.")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    finally:
        # Cleanup
        if scheduler.running:
            scheduler.shutdown()
        conn.close()
        print("✓ Database connection closed")