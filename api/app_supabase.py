import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import asyncio

# Import the new Supabase-enabled agents
from agents.supabase_risk_agent import SupabaseRiskAgent
from database.supabase_manager import supabase_manager
# Migration utilities removed - migration is complete
from supervisor import SupervisorAgent

# Configure logging for serverless environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupabaseAPIHandler:
    """
    Enhanced API handler with Supabase integration
    
    This handler provides all the endpoints for the multi-agent portfolio analysis system
    with real-time database operations and comprehensive error handling.
    """
    
    def __init__(self):
        self.storage = supabase_manager
        self.risk_agent = None
        self.supervisor = None
        
        # Initialize agents lazily to avoid startup issues
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agents with proper error handling"""
        try:
            if self.storage:
                self.risk_agent = SupabaseRiskAgent()
                self.supervisor = SupervisorAgent()
                logger.info("Successfully initialized Supabase agents")
            else:
                logger.warning("Supabase manager not available, using fallback mode")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        try:
            # Check database connectivity
            db_status = "connected" if self.storage else "disconnected"
            
            # Check agent availability
            agents_status = {
                "risk_agent": self.risk_agent is not None,
                "supervisor": self.supervisor is not None
            }
            
            return {
                "success": True,
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database_status": db_status,
                "agents_status": agents_status,
                "environment": "production" if self.storage else "development"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def analyze_portfolio(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio risk with Supabase integration"""
        try:
            portfolio = request_data.get("portfolio", [])
            
            if not portfolio:
                return {"success": False, "error": "Portfolio is required"}
            
            if not isinstance(portfolio, list):
                return {"success": False, "error": "Portfolio must be a list of ticker symbols"}
            
            # Validate portfolio
            if len(portfolio) > 50:
                return {"success": False, "error": "Portfolio size cannot exceed 50 stocks"}
            
            # Use the new Supabase-enabled risk agent
            if self.risk_agent:
                result = await self.risk_agent.analyze_portfolio_risk(portfolio)
                
                if result["success"]:
                    # Add additional metadata
                    result["analysis_timestamp"] = datetime.now().isoformat()
                    result["agent_type"] = "supabase_risk_agent"
                    
                    logger.info(f"Portfolio analysis completed for {len(portfolio)} stocks")
                    return result
                else:
                    logger.error(f"Portfolio analysis failed: {result.get('error')}")
                    return result
            else:
                return {"success": False, "error": "Risk agent not available"}
                
        except Exception as e:
            logger.error(f"Portfolio analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_ticker(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual ticker risk"""
        try:
            ticker = request_data.get("ticker", "").upper()
            
            if not ticker:
                return {"success": False, "error": "Ticker is required"}
            
            # Use the new Supabase-enabled risk agent
            if self.risk_agent:
                result = await self.risk_agent.analyze_stock_risk(ticker)
                
                if result["success"]:
                    result["analysis_timestamp"] = datetime.now().isoformat()
                    result["agent_type"] = "supabase_risk_agent"
                    
                    logger.info(f"Ticker analysis completed for {ticker}")
                    return result
                else:
                    logger.error(f"Ticker analysis failed: {result.get('error')}")
                    return result
            else:
                return {"success": False, "error": "Risk agent not available"}
                
        except Exception as e:
            logger.error(f"Ticker analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_insights(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights from Supabase"""
        try:
            ticker = request_data.get("ticker")
            agent = request_data.get("agent")
            impact_level = request_data.get("impact_level")
            limit = min(request_data.get("limit", 20), 100)  # Cap at 100
            time_window_hours = request_data.get("time_window_hours")
            
            if not self.storage:
                return {"success": False, "error": "Database not available"}
            
            result = await self.storage.get_insights(
                ticker=ticker,
                agent=agent,
                impact_level=impact_level,
                limit=limit,
                time_window_hours=time_window_hours
            )
            
            if result["success"]:
                logger.info(f"Retrieved {len(result['insights'])} insights")
            
            return result
            
        except Exception as e:
            logger.error(f"Get insights error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_events(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get events from Supabase"""
        try:
            ticker = request_data.get("ticker")
            event_type = request_data.get("event_type")
            severity = request_data.get("severity")
            limit = min(request_data.get("limit", 50), 200)  # Cap at 200
            time_window_hours = request_data.get("time_window_hours", 24)
            
            if not self.storage:
                return {"success": False, "error": "Database not available"}
            
            result = await self.storage.get_events(
                ticker=ticker,
                event_type=event_type,
                severity=severity,
                limit=limit,
                time_window_hours=time_window_hours
            )
            
            if result["success"]:
                logger.info(f"Retrieved {len(result['events'])} events")
            
            return result
            
        except Exception as e:
            logger.error(f"Get events error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_knowledge_evolution(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get knowledge evolution from Supabase"""
        try:
            ticker = request_data.get("ticker")
            evolution_type = request_data.get("evolution_type")
            agent = request_data.get("agent")
            limit = min(request_data.get("limit", 20), 100)  # Cap at 100
            
            if not self.storage:
                return {"success": False, "error": "Database not available"}
            
            result = await self.storage.get_knowledge_evolution(
                ticker=ticker,
                evolution_type=evolution_type,
                agent=agent,
                limit=limit
            )
            
            if result["success"]:
                logger.info(f"Retrieved {len(result['evolutions'])} knowledge evolutions")
            
            return result
            
        except Exception as e:
            logger.error(f"Get knowledge evolution error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_portfolio_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get portfolio analysis from Supabase"""
        try:
            limit = min(request_data.get("limit", 20), 100)  # Cap at 100
            
            if not self.storage:
                return {"success": False, "error": "Database not available"}
            
            result = await self.storage.get_portfolio_analysis(limit=limit)
            
            if result["success"]:
                logger.info(f"Retrieved {len(result['analyses'])} portfolio analyses")
            
            return result
            
        except Exception as e:
            logger.error(f"Get portfolio analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_system_status(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            if not self.storage:
                return {"success": False, "error": "Database not available"}
            
            # Get recent insights summary
            insights_result = await self.storage.get_insights_summary()
            
            # Get recent portfolio analysis
            portfolio_result = await self.storage.get_portfolio_analysis(limit=5)
            
            # Get system metrics
            metrics_query = """
                SELECT 
                    metric_type,
                    AVG(metric_value) as avg_value,
                    COUNT(*) as count,
                    MAX(created_at) as last_updated
                FROM system_metrics 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY metric_type
                ORDER BY last_updated DESC
            """
            
            metrics_result = await self.storage.execute_query(metrics_query)
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "insights_summary": insights_result.get("summary", []),
                "recent_portfolio_analyses": portfolio_result.get("analyses", []),
                "system_metrics": metrics_result.get("data", []),
                "database_status": "connected",
                "agents_status": {
                    "risk_agent": self.risk_agent is not None,
                    "supervisor": self.supervisor is not None
                }
            }
            
        except Exception as e:
            logger.error(f"System status error: {e}")
            return {"success": False, "error": str(e)}
    
    # Migration methods removed - migration is complete


# Global API handler instance
api_handler = SupabaseAPIHandler()


async def api(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main API function for Supabase-enabled portfolio analysis
    
    This function handles all API requests with proper routing and error handling.
    """
    try:
        action = request_data.get("action", "health")
        
        # Route to appropriate handler
        if action == "health":
            return await api_handler.health_check()
        elif action == "analyze_portfolio":
            return await api_handler.analyze_portfolio(request_data)
        elif action == "analyze_ticker":
            return await api_handler.analyze_ticker(request_data)
        elif action == "get_insights":
            return await api_handler.get_insights(request_data)
        elif action == "get_events":
            return await api_handler.get_events(request_data)
        elif action == "get_knowledge_evolution":
            return await api_handler.get_knowledge_evolution(request_data)
        elif action == "get_portfolio_analysis":
            return await api_handler.get_portfolio_analysis(request_data)
        elif action == "get_system_status":
            return await api_handler.get_system_status(request_data)
        # Migration actions removed - migration is complete
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
            
    except Exception as e:
        logger.error(f"API error: {e}")
        return {"success": False, "error": str(e)}


def handler(event, context):
    """
    Vercel serverless function handler for Supabase-enabled portfolio analysis
    
    This handler processes HTTP requests and returns JSON responses.
    """
    try:
        # Extract request data
        http_method = event.get("httpMethod", "GET")
        query_params = event.get("queryStringParameters") or {}
        body = event.get("body", "{}")
        
        # Parse request data
        if http_method == "POST":
            try:
                request_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"success": False, "error": "Invalid JSON in request body"})
                }
        else:
            request_data = dict(query_params)
        
        # Set default action if not provided
        if "action" not in request_data:
            request_data["action"] = "health"
        
        # Process the request
        result = asyncio.run(api(request_data))
        
        # Return response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"success": False, "error": str(e)})
        }


# For local testing
if __name__ == "__main__":
    # Test the API locally
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({"action": "health"})
    }
    
    result = handler(test_event, {})
    print(json.dumps(result, indent=2)) 