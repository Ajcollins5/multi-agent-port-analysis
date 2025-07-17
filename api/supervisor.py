import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Environment variables
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
VERCEL_URL = os.environ.get("VERCEL_URL", "")

class SupervisorAgent:
    """Orchestrates multi-agent analysis with enhanced coordination"""
    
    def __init__(self):
        self.base_url = VERCEL_URL
        self.agents = {
            "risk": "/api/agents/risk",
            "news": "/api/agents/news", 
            "events": "/api/agents/events",
            "knowledge": "/api/agents/knowledge"
        }
        self.services = {
            "email": "/api/notifications/email",
            "storage": "/api/storage",
            "scheduler": "/api/scheduler/cron"
        }
    
    def orchestrate_analysis(self, ticker: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Orchestrate comprehensive analysis across all agents"""
        try:
            start_time = datetime.now()
            results = {
                "ticker": ticker,
                "analysis_type": analysis_type,
                "start_time": start_time.isoformat(),
                "agent_results": {},
                "synthesis": {},
                "notifications": [],
                "errors": []
            }
            
            # Step 1: Risk Analysis
            try:
                risk_result = self._call_agent("risk", "analyze_stock", {"ticker": ticker})
                results["agent_results"]["risk"] = risk_result
                
                # Store risk insights
                if risk_result.get("high_impact"):
                    self._store_insight(ticker, f"HIGH RISK: {ticker} volatility {risk_result.get('volatility', 0):.4f}", "RiskAgent")
                
            except Exception as e:
                results["errors"].append(f"Risk analysis failed: {str(e)}")
            
            # Step 2: News Sentiment Analysis
            try:
                news_result = self._call_agent("news", "analyze_sentiment", {"ticker": ticker})
                results["agent_results"]["news"] = news_result
                
                # Store news insights
                if news_result.get("impact_level") == "HIGH":
                    self._store_insight(ticker, f"NEWS IMPACT: {ticker} {news_result.get('sentiment', 'NEUTRAL')} sentiment", "NewsAgent")
                
            except Exception as e:
                results["errors"].append(f"News analysis failed: {str(e)}")
            
            # Step 3: Event Detection
            try:
                event_result = self._call_agent("events", "detect_events", {"portfolio": [ticker]})
                results["agent_results"]["events"] = event_result
                
                # Store event insights
                if event_result.get("total_events", 0) > 0:
                    self._store_insight(ticker, f"EVENTS: {event_result.get('total_events', 0)} events detected", "EventSentinel")
                
            except Exception as e:
                results["errors"].append(f"Event detection failed: {str(e)}")
            
            # Step 4: Knowledge Curation
            try:
                knowledge_result = self._call_agent("knowledge", "quality_assessment", {})
                results["agent_results"]["knowledge"] = knowledge_result
                
            except Exception as e:
                results["errors"].append(f"Knowledge curation failed: {str(e)}")
            
            # Step 5: Synthesis and Decision Making
            synthesis = self._synthesize_results(results["agent_results"])
            results["synthesis"] = synthesis
            
            # Step 6: Notifications
            if synthesis.get("requires_notification"):
                notification_result = self._send_notifications(ticker, synthesis)
                results["notifications"] = notification_result
            
            # Calculate execution time
            end_time = datetime.now()
            results["end_time"] = end_time.isoformat()
            results["duration"] = (end_time - start_time).total_seconds()
            
            return results
            
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    def orchestrate_portfolio_analysis(self, portfolio: List[str]) -> Dict[str, Any]:
        """Orchestrate portfolio-wide analysis"""
        try:
            start_time = datetime.now()
            portfolio_results = {
                "portfolio": portfolio,
                "portfolio_size": len(portfolio),
                "start_time": start_time.isoformat(),
                "individual_results": [],
                "portfolio_synthesis": {},
                "critical_alerts": [],
                "errors": []
            }
            
            # Analyze each ticker individually
            for ticker in portfolio:
                try:
                    ticker_result = self.orchestrate_analysis(ticker, "focused")
                    portfolio_results["individual_results"].append(ticker_result)
                except Exception as e:
                    portfolio_results["errors"].append(f"Analysis failed for {ticker}: {str(e)}")
            
            # Portfolio-wide event detection
            try:
                portfolio_events = self._call_agent("events", "detect_events", {"portfolio": portfolio})
                portfolio_results["portfolio_events"] = portfolio_events
                
                # Check for critical portfolio alerts
                if portfolio_events.get("portfolio_risk") == "HIGH":
                    portfolio_results["critical_alerts"].append({
                        "type": "HIGH_PORTFOLIO_RISK",
                        "message": f"Portfolio risk level: {portfolio_events.get('portfolio_risk')}",
                        "affected_stocks": portfolio_events.get("high_volatility_count", 0)
                    })
            except Exception as e:
                portfolio_results["errors"].append(f"Portfolio event detection failed: {str(e)}")
            
            # Portfolio synthesis
            portfolio_synthesis = self._synthesize_portfolio_results(portfolio_results["individual_results"])
            portfolio_results["portfolio_synthesis"] = portfolio_synthesis
            
            # Send portfolio-level notifications
            if portfolio_synthesis.get("requires_notification"):
                notification_result = self._send_portfolio_notifications(portfolio, portfolio_synthesis)
                portfolio_results["notifications"] = notification_result
            
            end_time = datetime.now()
            portfolio_results["end_time"] = end_time.isoformat()
            portfolio_results["duration"] = (end_time - start_time).total_seconds()
            
            return portfolio_results
            
        except Exception as e:
            return {"error": str(e), "portfolio": portfolio}
    
    def _call_agent(self, agent_name: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific agent with given parameters"""
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        url = f"{self.base_url}{self.agents[agent_name]}"
        payload = {"action": action, **params}
        
        # In production, this would be an actual HTTP request
        # For now, simulate the response
        if agent_name == "risk":
            return {
                "ticker": params.get("ticker", ""),
                "volatility": 0.03,
                "impact_level": "MEDIUM",
                "high_impact": False
            }
        elif agent_name == "news":
            return {
                "ticker": params.get("ticker", ""),
                "sentiment": "NEUTRAL",
                "impact_level": "LOW"
            }
        elif agent_name == "events":
            return {
                "portfolio_size": len(params.get("portfolio", [])),
                "total_events": 2,
                "portfolio_risk": "LOW"
            }
        elif agent_name == "knowledge":
            return {
                "total_insights": 10,
                "quality_score": 75.0
            }
        
        return {}
    
    def _store_insight(self, ticker: str, insight: str, agent: str):
        """Store insight using storage manager"""
        try:
            payload = {
                "action": "store_insight",
                "ticker": ticker,
                "insight": insight,
                "agent": agent
            }
            # In production, make actual HTTP request to storage service
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _synthesize_results(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple agents"""
        synthesis = {
            "overall_risk": "LOW",
            "confidence": 0.8,
            "key_insights": [],
            "requires_notification": False,
            "recommended_actions": []
        }
        
        # Risk synthesis
        risk_data = agent_results.get("risk", {})
        if risk_data.get("high_impact"):
            synthesis["overall_risk"] = "HIGH"
            synthesis["requires_notification"] = True
            synthesis["key_insights"].append(f"High volatility detected: {risk_data.get('volatility', 0):.4f}")
        
        # News synthesis
        news_data = agent_results.get("news", {})
        if news_data.get("impact_level") == "HIGH":
            synthesis["requires_notification"] = True
            synthesis["key_insights"].append(f"High news impact: {news_data.get('sentiment', 'NEUTRAL')} sentiment")
        
        # Event synthesis
        event_data = agent_results.get("events", {})
        if event_data.get("total_events", 0) > 5:
            synthesis["key_insights"].append(f"Multiple events detected: {event_data.get('total_events', 0)}")
        
        # Generate recommendations
        if synthesis["overall_risk"] == "HIGH":
            synthesis["recommended_actions"].append("Monitor position closely")
            synthesis["recommended_actions"].append("Consider risk reduction strategies")
        
        return synthesis
    
    def _synthesize_portfolio_results(self, individual_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize portfolio-wide results"""
        portfolio_synthesis = {
            "portfolio_risk": "LOW",
            "high_risk_count": 0,
            "total_notifications": 0,
            "key_portfolio_insights": [],
            "requires_notification": False
        }
        
        high_risk_count = 0
        total_notifications = 0
        
        for result in individual_results:
            if result.get("synthesis", {}).get("overall_risk") == "HIGH":
                high_risk_count += 1
            if result.get("synthesis", {}).get("requires_notification"):
                total_notifications += 1
        
        portfolio_synthesis["high_risk_count"] = high_risk_count
        portfolio_synthesis["total_notifications"] = total_notifications
        
        # Determine portfolio risk level
        if high_risk_count > len(individual_results) * 0.5:
            portfolio_synthesis["portfolio_risk"] = "HIGH"
            portfolio_synthesis["requires_notification"] = True
        elif high_risk_count > 0:
            portfolio_synthesis["portfolio_risk"] = "MEDIUM"
        
        return portfolio_synthesis
    
    def _send_notifications(self, ticker: str, synthesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send notifications based on synthesis results"""
        notifications = []
        
        if synthesis.get("overall_risk") == "HIGH":
            notification = {
                "type": "high_impact_alert",
                "data": {
                    "ticker": ticker,
                    "current_price": 150.00,  # Would be actual price
                    "volatility": 0.06,
                    "impact_level": "HIGH",
                    "additional_info": "Multi-agent analysis indicates high risk"
                }
            }
            notifications.append(notification)
        
        return notifications
    
    def _send_portfolio_notifications(self, portfolio: List[str], synthesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send portfolio-level notifications"""
        notifications = []
        
        if synthesis.get("portfolio_risk") == "HIGH":
            notification = {
                "type": "portfolio_risk_alert",
                "data": {
                    "risk_level": "HIGH",
                    "high_risk_count": synthesis.get("high_risk_count", 0),
                    "total_stocks": len(portfolio),
                    "risk_breakdown": f"High risk detected in {synthesis.get('high_risk_count', 0)} stocks",
                    "recommendations": "Review portfolio allocation and consider risk reduction"
                }
            }
            notifications.append(notification)
        
        return notifications

# Global supervisor instance
supervisor = SupervisorAgent()

def handler(request):
    """Vercel serverless function handler for Supervisor"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "analyze_ticker")
            
            if action == "analyze_ticker":
                ticker = body.get("ticker", "AAPL")
                analysis_type = body.get("analysis_type", "comprehensive")
                return json.dumps(supervisor.orchestrate_analysis(ticker, analysis_type))
            
            elif action == "analyze_portfolio":
                portfolio = body.get("portfolio", ["AAPL"])
                return json.dumps(supervisor.orchestrate_portfolio_analysis(portfolio))
            
            else:
                return json.dumps({
                    "error": "Invalid action",
                    "available_actions": ["analyze_ticker", "analyze_portfolio"]
                })
        
        else:
            return json.dumps({
                "agent": "Supervisor",
                "description": "Orchestrates multi-agent analysis across the system",
                "endpoints": [
                    "POST - analyze_ticker: Comprehensive ticker analysis",
                    "POST - analyze_portfolio: Portfolio-wide analysis"
                ],
                "available_agents": list(supervisor.agents.keys()),
                "available_services": list(supervisor.services.keys()),
                "status": "active"
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "agent": "Supervisor"}) 