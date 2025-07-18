import os
import json
import yfinance as yf
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
import asyncio
import logging
from .base_agent import BaseAgent

# Environment variables for configuration (with fallback for build time)
XAI_API_KEY = os.environ.get("XAI_API_KEY")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")

class SupabaseRiskAgent(BaseAgent):
    """
    Enhanced Risk Agent with Supabase integration
    
    This agent analyzes portfolio risk using real-time data and stores
    insights and events in Supabase for real-time frontend updates.
    """
    
    def __init__(self):
        super().__init__("RiskAgent")
        self.risk_threshold = 0.05  # 5% volatility threshold
        self.confidence_threshold = 0.7  # 70% confidence threshold
        
    async def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch stock data with error handling and logging
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dict with stock data or error information
        """
        try:
            # Store fetch attempt metric
            await self.store_system_metric(
                metric_type="stock_data_fetch",
                metric_value=1,
                additional_data={"ticker": ticker, "status": "started"}
            )
            
            stock = yf.Ticker(ticker)
            
            # Get historical data (last 30 days)
            hist = stock.history(period="30d")
            
            if hist.empty:
                error_msg = f"No data available for {ticker}"
                logging.warning(error_msg)
                
                # Store error metric
                await self.store_system_metric(
                    metric_type="stock_data_fetch",
                    metric_value=0,
                    additional_data={"ticker": ticker, "status": "failed", "error": error_msg}
                )
                
                return {"success": False, "error": error_msg}
            
            # Calculate key metrics
            current_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            
            # Calculate volatility (standard deviation of returns)
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
            
            # Calculate price change
            price_change = (current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
            
            # Volume spike detection
            volume_spike = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Store successful fetch metric
            await self.store_system_metric(
                metric_type="stock_data_fetch",
                metric_value=1,
                additional_data={"ticker": ticker, "status": "success", "volatility": volatility}
            )
            
            return {
                "success": True,
                "ticker": ticker,
                "current_price": current_price,
                "price_change": price_change,
                "volatility": volatility,
                "volume_spike": volume_spike,
                "avg_volume": avg_volume,
                "current_volume": current_volume,
                "data_points": len(hist)
            }
            
        except Exception as e:
            error_msg = f"Error fetching data for {ticker}: {str(e)}"
            logging.error(error_msg)
            
            # Store error metric
            await self.store_system_metric(
                metric_type="stock_data_fetch",
                metric_value=0,
                additional_data={"ticker": ticker, "status": "error", "error": error_msg}
            )
            
            return {"success": False, "error": error_msg}
    
    async def analyze_stock_risk(self, ticker: str) -> Dict[str, Any]:
        """
        Analyze individual stock risk with comprehensive metrics
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dict with risk analysis results
        """
        try:
            # Fetch stock data
            stock_data = await self.fetch_stock_data(ticker)
            
            if not stock_data["success"]:
                return stock_data
            
            # Extract metrics
            volatility = stock_data["volatility"]
            price_change = stock_data["price_change"]
            volume_spike = stock_data["volume_spike"]
            
            # Risk assessment logic
            risk_score = 0
            risk_factors = []
            
            # Volatility risk
            if volatility > 0.3:  # 30% annualized volatility
                risk_score += 40
                risk_factors.append(f"High volatility: {volatility:.2%}")
            elif volatility > 0.2:  # 20% annualized volatility
                risk_score += 25
                risk_factors.append(f"Moderate volatility: {volatility:.2%}")
            
            # Price change risk
            if abs(price_change) > 0.05:  # 5% price change
                risk_score += 30
                risk_factors.append(f"Significant price change: {price_change:.2%}")
            
            # Volume spike risk
            if volume_spike > 2:  # 2x average volume
                risk_score += 20
                risk_factors.append(f"High volume spike: {volume_spike:.1f}x")
            elif volume_spike > 1.5:  # 1.5x average volume
                risk_score += 10
                risk_factors.append(f"Moderate volume spike: {volume_spike:.1f}x")
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = "HIGH"
                impact_level = "HIGH"
            elif risk_score >= 40:
                risk_level = "MEDIUM"
                impact_level = "MEDIUM"
            else:
                risk_level = "LOW"
                impact_level = "LOW"
            
            # Calculate confidence based on data quality
            confidence = min(0.95, 0.5 + (stock_data["data_points"] / 60))  # Max 95% confidence
            
            # Create insight
            insight = f"{ticker} risk analysis: {risk_level} risk level (score: {risk_score})"
            if risk_factors:
                insight += f". Factors: {', '.join(risk_factors)}"
            
            # Store insight in Supabase
            await self.store_insight(
                ticker=ticker,
                insight=insight,
                volatility=volatility,
                impact_level=impact_level,
                confidence=confidence,
                metadata={
                    "risk_score": risk_score,
                    "risk_factors": risk_factors,
                    "price_change": price_change,
                    "volume_spike": volume_spike,
                    "analysis_type": "individual_stock_risk"
                }
            )
            
            # Store high-risk events
            if risk_level == "HIGH":
                await self.store_event(
                    event_type="HIGH_RISK_ALERT",
                    ticker=ticker,
                    message=f"High risk detected for {ticker}: {', '.join(risk_factors)}",
                    severity="HIGH",
                    volatility=volatility,
                    volume_spike=volume_spike,
                    metadata={
                        "risk_score": risk_score,
                        "confidence": confidence
                    }
                )
            
            return {
                "success": True,
                "ticker": ticker,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "volatility": volatility,
                "confidence": confidence,
                "high_impact": risk_level == "HIGH",
                "insight": insight
            }
            
        except Exception as e:
            error_msg = f"Error analyzing risk for {ticker}: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def analyze_portfolio_risk(self, portfolio: List[str]) -> Dict[str, Any]:
        """
        Analyze portfolio-wide risk with comprehensive metrics
        
        Args:
            portfolio: List of stock ticker symbols
            
        Returns:
            Dict with portfolio risk analysis results
        """
        try:
            if not portfolio:
                return {"success": False, "error": "Empty portfolio provided"}
            
            # Analyze each stock
            stock_analyses = []
            high_risk_stocks = []
            total_risk_score = 0
            
            for ticker in portfolio:
                analysis = await self.analyze_stock_risk(ticker)
                
                if analysis["success"]:
                    stock_analyses.append(analysis)
                    total_risk_score += analysis["risk_score"]
                    
                    if analysis["risk_level"] == "HIGH":
                        high_risk_stocks.append(ticker)
                else:
                    logging.warning(f"Failed to analyze {ticker}: {analysis.get('error')}")
            
            if not stock_analyses:
                return {"success": False, "error": "No successful stock analyses"}
            
            # Calculate portfolio metrics
            avg_risk_score = total_risk_score / len(stock_analyses)
            high_risk_count = len(high_risk_stocks)
            high_risk_percentage = (high_risk_count / len(portfolio)) * 100
            
            # Determine portfolio risk level
            if avg_risk_score >= 60 or high_risk_percentage >= 30:
                portfolio_risk = "HIGH"
                impact_level = "HIGH"
            elif avg_risk_score >= 35 or high_risk_percentage >= 15:
                portfolio_risk = "MEDIUM"
                impact_level = "MEDIUM"
            else:
                portfolio_risk = "LOW"
                impact_level = "LOW"
            
            # Calculate overall portfolio volatility
            portfolio_volatility = sum(s["volatility"] for s in stock_analyses) / len(stock_analyses)
            
            # Create portfolio insight
            portfolio_insight = f"Portfolio risk analysis: {portfolio_risk} risk level (avg score: {avg_risk_score:.1f})"
            if high_risk_stocks:
                portfolio_insight += f". High risk stocks: {', '.join(high_risk_stocks)}"
            
            # Store portfolio insight
            await self.store_insight(
                ticker="PORTFOLIO",
                insight=portfolio_insight,
                volatility=portfolio_volatility,
                impact_level=impact_level,
                confidence=0.85,
                metadata={
                    "portfolio_size": len(portfolio),
                    "analyzed_stocks": len(stock_analyses),
                    "avg_risk_score": avg_risk_score,
                    "high_risk_count": high_risk_count,
                    "high_risk_percentage": high_risk_percentage,
                    "high_risk_stocks": high_risk_stocks,
                    "analysis_type": "portfolio_risk"
                }
            )
            
            # Store portfolio analysis record
            await self.storage.store_portfolio_analysis(
                portfolio_size=len(portfolio),
                analyzed_stocks=len(stock_analyses),
                high_impact_count=high_risk_count,
                portfolio_risk=portfolio_risk,
                analysis_duration=0,  # Could be calculated if needed
                agents_used=["RiskAgent"],
                synthesis_summary=portfolio_insight,
                metadata={
                    "avg_risk_score": avg_risk_score,
                    "portfolio_volatility": portfolio_volatility
                }
            )
            
            # Store high-risk portfolio events
            if portfolio_risk == "HIGH":
                await self.store_event(
                    event_type="PORTFOLIO_HIGH_RISK",
                    ticker="PORTFOLIO",
                    message=f"High portfolio risk detected: {high_risk_count}/{len(portfolio)} stocks at high risk",
                    severity="HIGH",
                    volatility=portfolio_volatility,
                    portfolio_risk=portfolio_risk,
                    metadata={
                        "high_risk_stocks": high_risk_stocks,
                        "avg_risk_score": avg_risk_score
                    }
                )
            
            return {
                "success": True,
                "portfolio_risk": portfolio_risk,
                "avg_risk_score": avg_risk_score,
                "high_risk_count": high_risk_count,
                "high_risk_percentage": high_risk_percentage,
                "high_risk_stocks": high_risk_stocks,
                "portfolio_volatility": portfolio_volatility,
                "stock_analyses": stock_analyses,
                "insight": portfolio_insight
            }
            
        except Exception as e:
            error_msg = f"Error analyzing portfolio risk: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def send_email_alert(self, subject: str, body: str, to_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email notifications for high impact events
        
        Args:
            subject: Email subject
            body: Email body
            to_email: Recipient email (optional)
            
        Returns:
            Dict with success status
        """
        try:
            # Validate email configuration
            if not SENDER_EMAIL or not SENDER_PASSWORD:
                return {"success": False, "error": "Email configuration incomplete"}
            
            if not to_email:
                to_email = TO_EMAIL
            
            if not to_email:
                return {"success": False, "error": "No recipient email specified"}
            
            message = MIMEMultipart()
            message["From"] = SENDER_EMAIL
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            text = message.as_string()
            server.sendmail(SENDER_EMAIL, to_email, text)
            server.quit()
            
            # Store email notification metric
            await self.store_system_metric(
                metric_type="email_notification",
                metric_value=1,
                additional_data={"subject": subject, "recipient": to_email, "status": "sent"}
            )
            
            return {"success": True, "message": f"Email sent to {to_email}"}
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logging.error(error_msg)
            
            # Store email error metric
            await self.store_system_metric(
                metric_type="email_notification",
                metric_value=0,
                additional_data={"subject": subject, "status": "failed", "error": error_msg}
            )
            
            return {"success": False, "error": error_msg}
    
    async def monitor_portfolio_risk(self, portfolio: List[str]) -> Dict[str, Any]:
        """
        Monitor portfolio risk and send alerts if necessary
        
        Args:
            portfolio: List of stock ticker symbols
            
        Returns:
            Dict with monitoring results
        """
        try:
            # Analyze portfolio risk
            analysis = await self.analyze_portfolio_risk(portfolio)
            
            if not analysis["success"]:
                return analysis
            
            # Check if alert is needed
            if analysis["portfolio_risk"] == "HIGH":
                subject = f"🚨 High Risk Alert: Portfolio Risk Level"
                body = f"""
Portfolio Risk Alert

Risk Level: {analysis['portfolio_risk']}
Average Risk Score: {analysis['avg_risk_score']:.1f}
High Risk Stocks: {analysis['high_risk_count']}/{len(portfolio)} ({analysis['high_risk_percentage']:.1f}%)

High Risk Stocks:
{', '.join(analysis['high_risk_stocks']) if analysis['high_risk_stocks'] else 'None'}

Portfolio Volatility: {analysis['portfolio_volatility']:.2%}

This is an automated alert from the Risk Agent.
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                # Send email alert
                email_result = await self.send_email_alert(subject, body)
                
                # Store alert event
                await self.store_event(
                    event_type="RISK_ALERT_SENT",
                    ticker="PORTFOLIO",
                    message=f"Risk alert sent for portfolio with {analysis['high_risk_count']} high-risk stocks",
                    severity="HIGH",
                    metadata={
                        "email_sent": email_result["success"],
                        "portfolio_analysis": analysis
                    }
                )
                
                return {
                    "success": True,
                    "alert_sent": email_result["success"],
                    "analysis": analysis,
                    "email_result": email_result
                }
            
            return {
                "success": True,
                "alert_sent": False,
                "analysis": analysis,
                "message": "No alert needed - portfolio risk is acceptable"
            }
            
        except Exception as e:
            error_msg = f"Error monitoring portfolio risk: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}


# Wrapper functions for backward compatibility
async def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """Backward compatibility wrapper"""
    agent = SupabaseRiskAgent()
    return await agent.fetch_stock_data(ticker)

async def analyze_portfolio_risk(portfolio: List[str]) -> Dict[str, Any]:
    """Backward compatibility wrapper"""
    agent = SupabaseRiskAgent()
    return await agent.analyze_portfolio_risk(portfolio)

async def send_email(subject: str, body: str, to_email: Optional[str] = None) -> Dict[str, Any]:
    """Backward compatibility wrapper"""
    agent = SupabaseRiskAgent()
    return await agent.send_email_alert(subject, body, to_email)

# Sync wrappers for existing code
def fetch_stock_data_sync(ticker: str) -> Dict[str, Any]:
    """Synchronous wrapper for fetch_stock_data"""
    return asyncio.run(fetch_stock_data(ticker))

def analyze_portfolio_risk_sync(portfolio: List[str]) -> Dict[str, Any]:
    """Synchronous wrapper for analyze_portfolio_risk"""
    return asyncio.run(analyze_portfolio_risk(portfolio))

def send_email_sync(subject: str, body: str, to_email: Optional[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for send_email"""
    return asyncio.run(send_email(subject, body, to_email))

# Test function
async def test_risk_agent():
    """Test the enhanced risk agent"""
    try:
        agent = SupabaseRiskAgent()
        
        # Test single stock analysis
        result = await agent.analyze_stock_risk("AAPL")
        print(f"Single stock analysis: {result}")
        
        # Test portfolio analysis
        portfolio_result = await agent.analyze_portfolio_risk(["AAPL", "GOOGL", "MSFT"])
        print(f"Portfolio analysis: {portfolio_result}")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_risk_agent()) 