import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Environment variables (validation moved to runtime)
XAI_API_KEY = os.environ.get("XAI_API_KEY")
VERCEL_URL = os.environ.get("VERCEL_URL", "")

class GrokAI:
    """Grok 4 AI integration for intelligent analysis and synthesis"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def synthesize_analysis(self, agent_results: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """Use Grok 4 to synthesize multi-agent analysis results"""
        try:
            # Prepare context for Grok 4
            context = self._prepare_analysis_context(agent_results, ticker)
            
            # Create synthesis prompt
            synthesis_prompt = f"""
            You are an expert financial analyst synthesizing multi-agent portfolio analysis results for {ticker}.
            
            ANALYSIS CONTEXT:
            {context}
            
            TASK: Provide a comprehensive synthesis including:
            1. Overall risk assessment (LOW/MEDIUM/HIGH)
            2. Key insights from each agent
            3. Recommendations for portfolio management
            4. Confidence level in the analysis
            5. Whether immediate action is required
            
            Respond in JSON format with the following structure:
            {{
                "overall_risk": "LOW/MEDIUM/HIGH",
                "key_insights": ["insight1", "insight2", ...],
                "recommendations": ["rec1", "rec2", ...],
                "confidence_level": 0.8,
                "requires_action": false,
                "synthesis_summary": "Brief summary of the analysis"
            }}
            """
            
            # Call Grok 4 API
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "grok-beta",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert financial analyst with deep knowledge of portfolio management and risk assessment. Always respond with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": synthesis_prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                grok_response = response.json()
                content = grok_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                
                try:
                    synthesis = json.loads(content)
                    synthesis["grok_model"] = "grok-beta"
                    synthesis["synthesis_timestamp"] = datetime.now().isoformat()
                    return synthesis
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    return {
                        "overall_risk": "MEDIUM",
                        "key_insights": [content],
                        "recommendations": ["Review analysis manually"],
                        "confidence_level": 0.5,
                        "requires_action": False,
                        "synthesis_summary": "Grok analysis completed but JSON parsing failed",
                        "raw_grok_response": content
                    }
            else:
                logging.error(f"Grok API error: {response.status_code} - {response.text}")
                return {
                    "overall_risk": "MEDIUM",
                    "key_insights": ["Grok 4 API error"],
                    "recommendations": ["Review analysis manually"],
                    "confidence_level": 0.5,
                    "requires_action": False,
                    "synthesis_summary": "Grok 4 API error - manual review required",
                    "error": True
                }
                
        except Exception as e:
            logging.error(f"Grok synthesis failed: {str(e)}")
            return {
                "overall_risk": "MEDIUM",
                "key_insights": ["Grok 4 synthesis failed"],
                "recommendations": ["Review analysis manually"],
                "confidence_level": 0.5,
                "requires_action": False,
                "synthesis_summary": "Grok 4 synthesis failed - manual review required",
                "error": True
            }
    
    def _prepare_analysis_context(self, agent_results: Dict[str, Any], ticker: str) -> str:
        """Prepare context string for Grok 4 analysis"""
        context_parts = []
        
        # Risk Agent Results
        if "risk" in agent_results:
            risk_data = agent_results["risk"]
            context_parts.append(f"RISK ANALYSIS: {ticker} volatility {risk_data.get('volatility', 0):.4f}, impact level {risk_data.get('impact_level', 'UNKNOWN')}")
        
        # News Agent Results
        if "news" in agent_results:
            news_data = agent_results["news"]
            context_parts.append(f"NEWS SENTIMENT: {news_data.get('sentiment', 'NEUTRAL')} sentiment, impact level {news_data.get('impact_level', 'UNKNOWN')}")
        
        # Event Results
        if "events" in agent_results:
            event_data = agent_results["events"]
            context_parts.append(f"EVENTS: {event_data.get('total_events', 0)} events detected, portfolio risk {event_data.get('portfolio_risk', 'UNKNOWN')}")
        
        # Knowledge Results
        if "knowledge" in agent_results:
            knowledge_data = agent_results["knowledge"]
            context_parts.append(f"KNOWLEDGE QUALITY: Score {knowledge_data.get('quality_score', 0)}, gaps identified: {len(knowledge_data.get('gaps', []))}")
        
        return "\n".join(context_parts)
    


    def refine_insight(self, ticker: str, original_insight: str, additional_context: str = "") -> Dict[str, Any]:
        """Use Grok 4 to refine and enhance insights"""
        try:
            refinement_prompt = f"""
            You are an expert financial analyst tasked with refining and enhancing portfolio insights.
            
            ORIGINAL INSIGHT: {original_insight}
            ADDITIONAL CONTEXT: {additional_context}
            TICKER: {ticker}
            
            TASK: Enhance this insight by:
            1. Adding deeper market context
            2. Identifying potential implications
            3. Suggesting specific actions
            4. Providing confidence assessment
            
            Respond in JSON format:
            {{
                "refined_insight": "Enhanced insight with deeper analysis",
                "implications": ["implication1", "implication2"],
                "suggested_actions": ["action1", "action2"],
                "confidence": 0.8,
                "enhancement_quality": "HIGH/MEDIUM/LOW"
            }}
            """
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "grok-beta",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert financial analyst specializing in insight refinement and enhancement."
                        },
                        {
                            "role": "user",
                            "content": refinement_prompt
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 800
                },
                timeout=25
            )
            
            if response.status_code == 200:
                grok_response = response.json()
                content = grok_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                
                try:
                    refined = json.loads(content)
                    refined["original_insight"] = original_insight
                    refined["refinement_timestamp"] = datetime.now().isoformat()
                    return refined
                except json.JSONDecodeError:
                    return {
                        "refined_insight": f"ENHANCED: {original_insight}",
                        "implications": ["Manual review recommended"],
                        "suggested_actions": ["Review with expert analyst"],
                        "confidence": 0.5,
                        "enhancement_quality": "LOW",
                        "raw_grok_response": content
                    }
            else:
                logging.error(f"Grok refinement error: {response.status_code}")
                return self._fallback_refinement(original_insight)
                
        except Exception as e:
            logging.error(f"Grok refinement failed: {str(e)}")
            return self._fallback_refinement(original_insight)
    
    def _fallback_refinement(self, original_insight: str) -> Dict[str, Any]:
        """Fallback refinement when Grok 4 is unavailable"""
        return {
            "refined_insight": f"REFINED: {original_insight} (Enhanced with timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
            "implications": ["Grok 4 unavailable for deep analysis"],
            "suggested_actions": ["Review manually when Grok 4 is available"],
            "confidence": 0.4,
            "enhancement_quality": "LOW",
            "fallback_used": True
        }

class SupervisorAgent:
    """Orchestrates multi-agent analysis with enhanced coordination and Grok 4 integration"""
    
    def __init__(self):
        self.base_url = VERCEL_URL
        if XAI_API_KEY:
            self.grok_ai = GrokAI(XAI_API_KEY)
        else:
            self.grok_ai = None
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
    
    def _fallback_synthesis(self, agent_results: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """Fallback synthesis when Grok 4 is unavailable"""
        # Simple rule-based synthesis
        risk_level = "LOW"
        requires_action = False
        
        # Check risk indicators
        if "risk" in agent_results:
            risk_data = agent_results["risk"]
            if risk_data.get("high_impact") or risk_data.get("volatility", 0) > 0.05:
                risk_level = "HIGH"
                requires_action = True
        
        # Check news sentiment
        if "news" in agent_results:
            news_data = agent_results["news"]
            if news_data.get("impact_level") == "HIGH":
                risk_level = "HIGH" if risk_level != "HIGH" else "HIGH"
                requires_action = True
        
        return {
            "overall_risk": risk_level,
            "key_insights": [f"Fallback analysis for {ticker}"],
            "recommendations": ["Review with Grok 4 when available"],
            "confidence_level": 0.6,
            "requires_action": requires_action,
            "synthesis_summary": f"Rule-based synthesis for {ticker} - Grok 4 unavailable",
            "fallback_used": True
        }
    
    def orchestrate_analysis(self, ticker: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Orchestrate comprehensive analysis across all agents with Grok 4 synthesis"""
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
                
                # Store risk insights with Grok 4 enhancement
                if risk_result.get("high_impact"):
                    original_insight = f"HIGH RISK: {ticker} volatility {risk_result.get('volatility', 0):.4f}"
                    if self.grok_ai:
                        refined = self.grok_ai.refine_insight(ticker, original_insight, "High volatility detected")
                        self._store_insight(ticker, refined.get("refined_insight", original_insight), "RiskAgent")
                    else:
                        self._store_insight(ticker, original_insight, "RiskAgent")
                
            except Exception as e:
                results["errors"].append(f"Risk analysis failed: {str(e)}")
            
            # Step 2: News Sentiment Analysis
            try:
                news_result = self._call_agent("news", "analyze_sentiment", {"ticker": ticker})
                results["agent_results"]["news"] = news_result
                
                # Store news insights with Grok 4 enhancement
                if news_result.get("impact_level") == "HIGH":
                    original_insight = f"NEWS IMPACT: {ticker} {news_result.get('sentiment', 'NEUTRAL')} sentiment"
                    if self.grok_ai:
                        refined = self.grok_ai.refine_insight(ticker, original_insight, "High news impact detected")
                        self._store_insight(ticker, refined.get("refined_insight", original_insight), "NewsAgent")
                    else:
                        self._store_insight(ticker, original_insight, "NewsAgent")
                
            except Exception as e:
                results["errors"].append(f"News analysis failed: {str(e)}")
            
            # Step 3: Event Detection
            try:
                event_result = self._call_agent("events", "detect_events", {"portfolio": [ticker]})
                results["agent_results"]["events"] = event_result
                
                # Store event insights with Grok 4 enhancement
                if event_result.get("total_events", 0) > 0:
                    original_insight = f"EVENTS: {event_result.get('total_events', 0)} events detected"
                    if self.grok_ai:
                        refined = self.grok_ai.refine_insight(ticker, original_insight, "Multiple events detected")
                        self._store_insight(ticker, refined.get("refined_insight", original_insight), "EventSentinel")
                    else:
                        self._store_insight(ticker, original_insight, "EventSentinel")
                
            except Exception as e:
                results["errors"].append(f"Event detection failed: {str(e)}")
            
            # Step 4: Knowledge Curation
            try:
                knowledge_result = self._call_agent("knowledge", "quality_assessment", {})
                results["agent_results"]["knowledge"] = knowledge_result
                
            except Exception as e:
                results["errors"].append(f"Knowledge curation failed: {str(e)}")
            
            # Step 5: Grok 4 Synthesis and Decision Making
            if self.grok_ai:
                synthesis = self.grok_ai.synthesize_analysis(results["agent_results"], ticker)
            else:
                synthesis = self._fallback_synthesis(results["agent_results"], ticker)
            results["synthesis"] = synthesis
            
            # Step 6: Notifications
            if synthesis.get("requires_action"):
                notification_result = self._send_notifications(ticker, synthesis)
                results["notifications"] = notification_result
            
            # Calculate execution time
            end_time = datetime.now()
            results["end_time"] = end_time.isoformat()
            results["execution_time"] = (end_time - start_time).total_seconds()
            
            return results
            
        except Exception as e:
            return {
                "error": f"Orchestration failed: {str(e)}",
                "ticker": ticker,
                "timestamp": datetime.now().isoformat()
            }
    
    def _call_agent(self, agent_type: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call individual agent with error handling"""
        try:
            # DEPRECATED: Direct import calls for legacy agents
            # These have been migrated to Supabase-based agents
            # Use the new SupabaseRiskAgent and BaseAgent classes instead
            
            if agent_type == "risk":
                # Use agents.supabase_risk_agent.SupabaseRiskAgent instead
                return {"success": False, "error": "Legacy risk agent deprecated. Use SupabaseRiskAgent instead."}
                    
            elif agent_type == "news":
                # Use BaseAgent with news analysis capabilities instead
                return {"success": False, "error": "Legacy news agent deprecated. Use BaseAgent with news analysis instead."}
                    
            elif agent_type == "events":
                # Use BaseAgent with event detection capabilities instead
                return {"success": False, "error": "Legacy event agent deprecated. Use BaseAgent with event detection instead."}
                    
            elif agent_type == "knowledge":
                from agents.knowledge_curator import curate_knowledge_quality, identify_knowledge_gaps
                if action == "quality_assessment":
                    return curate_knowledge_quality()
                elif action == "identify_gaps":
                    return identify_knowledge_gaps(data.get("time_window", 24))
            
            return {"error": f"Unknown agent type or action: {agent_type}.{action}"}
            
        except Exception as e:
            return {"error": f"Agent call failed: {str(e)}"}
    
    def _store_insight(self, ticker: str, insight: str, agent: str) -> None:
        """Store insight with error handling"""
        try:
            # In a real implementation, this would store to database
            logging.info(f"Storing insight for {ticker} from {agent}: {insight}")
        except Exception as e:
            logging.error(f"Failed to store insight: {str(e)}")
    
    def _send_notifications(self, ticker: str, synthesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send notifications for high-priority events"""
        try:
            notifications = []
            
            if synthesis.get("overall_risk") == "HIGH":
                # Send high-risk notification
                from notifications.email_handler import send_email
                
                to_email = os.environ.get("TO_EMAIL")
                subject = f"🚨 HIGH RISK ALERT: {ticker}"
                body = f"""
HIGH RISK EVENT DETECTED

Ticker: {ticker}
Overall Risk: {synthesis.get('overall_risk')}
Confidence: {synthesis.get('confidence_level', 0):.2%}

Key Insights:
{chr(10).join(f'• {insight}' for insight in synthesis.get('key_insights', []))}

Recommendations:
{chr(10).join(f'• {rec}' for rec in synthesis.get('recommendations', []))}

Synthesis Summary:
{synthesis.get('synthesis_summary', 'No summary available')}

---
Multi-Agent Portfolio Analysis System
Powered by Grok 4 AI and Vercel Serverless Functions
"""
                
                if to_email:
                    email_result = send_email(to_email, subject, body)
                    notifications.append({
                        "type": "email",
                        "status": "sent" if email_result.get("success") else "failed",
                        "details": email_result
                    })
            
            return notifications
            
        except Exception as e:
            logging.error(f"Notification sending failed: {str(e)}")
            return [{"type": "error", "message": str(e)}]

# Export for Vercel
def handler(request):
    """Vercel serverless function handler for Supervisor"""
    try:
        supervisor = SupervisorAgent()
        
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "orchestrate")
            
            if action == "orchestrate":
                ticker = body.get("ticker", "AAPL")
                analysis_type = body.get("analysis_type", "comprehensive")
                result = supervisor.orchestrate_analysis(ticker, analysis_type)
                return json.dumps(result)
            
            else:
                return json.dumps({"error": "Invalid action", "available_actions": ["orchestrate"]})
        
        else:
            return json.dumps({
                "agent": "SupervisorAgent",
                "description": "Orchestrates multi-agent analysis with Grok 4 integration",
                "endpoints": [
                    "POST - orchestrate: Comprehensive multi-agent analysis"
                ],
                "status": "active"
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "agent": "SupervisorAgent"})

# Export handler for Vercel
app = handler 