import json
import logging
import os
import sys
from typing import Dict, Any, Optional, List
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import asyncio

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Configure logging for serverless environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variable validation
REQUIRED_ENV_VARS = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
MISSING_ENV_VARS = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]

# Import with error handling
try:
    # Try to import the Supabase-enabled agents
    from agents.supabase_risk_agent import SupabaseRiskAgent
    SUPABASE_RISK_AGENT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"SupabaseRiskAgent import failed: {e}")
    SUPABASE_RISK_AGENT_AVAILABLE = False

try:
    from database.supabase_manager import supabase_manager
    SUPABASE_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"supabase_manager import failed: {e}")
    SUPABASE_MANAGER_AVAILABLE = False
    supabase_manager = None

try:
    from supervisor import SupervisorAgent
    SUPERVISOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"SupervisorAgent import failed: {e}")
    SUPERVISOR_AVAILABLE = False

# Import monitoring service
try:
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
    sys.path.insert(0, backend_path)
    from monitoring_service import monitoring_service, MonitoringSettings, MonitoringFrequency, PortfolioPosition
    MONITORING_SERVICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"monitoring_service import failed: {e}")
    MONITORING_SERVICE_AVAILABLE = False

# Import news intelligence service
try:
    from news_intelligence_service import news_intelligence, NewsSnapshot, StockPersonality, NewsCategory, NewsImpact
    NEWS_INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"news_intelligence_service import failed: {e}")
    NEWS_INTELLIGENCE_AVAILABLE = False

# Import automated news pipeline
try:
    from automated_news_pipeline import automated_pipeline, AutomatedNewsPipeline
    AUTOMATED_PIPELINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"automated_news_pipeline import failed: {e}")
    AUTOMATED_PIPELINE_AVAILABLE = False

class SupabaseAPIHandler:
    """
    Enhanced API handler with Supabase integration
    
    This handler provides all the endpoints for the multi-agent portfolio analysis system
    with real-time database operations and comprehensive error handling.
    """
    
    def __init__(self):
        self.storage = supabase_manager if SUPABASE_MANAGER_AVAILABLE else None
        self.risk_agent = None
        self.supervisor = None
        
        # Initialize agents lazily to avoid startup issues
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agents with proper error handling"""
        try:
            if MISSING_ENV_VARS:
                logger.error(f"Missing required environment variables: {MISSING_ENV_VARS}")
                return
                
            if self.storage and SUPABASE_RISK_AGENT_AVAILABLE:
                self.risk_agent = SupabaseRiskAgent()
                logger.info("Successfully initialized SupabaseRiskAgent")
            else:
                logger.warning("SupabaseRiskAgent not available")
                
            if SUPERVISOR_AVAILABLE:
                self.supervisor = SupervisorAgent()
                logger.info("Successfully initialized SupervisorAgent")
            else:
                logger.warning("SupervisorAgent not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint with comprehensive status"""
        try:
            status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "supabase_manager": SUPABASE_MANAGER_AVAILABLE,
                    "supabase_risk_agent": SUPABASE_RISK_AGENT_AVAILABLE,
                    "supervisor": SUPERVISOR_AVAILABLE
                },
                "environment": {
                    "required_vars_present": len(MISSING_ENV_VARS) == 0,
                    "missing_vars": MISSING_ENV_VARS
                }
            }
            
            # Test database connection if available
            if self.storage:
                try:
                    # Simple connection test - just check if client is available
                    if hasattr(self.storage, 'client') and self.storage.client:
                        status["database"] = "connected"
                    else:
                        status["database"] = "client_unavailable"
                        status["status"] = "degraded"
                except Exception as db_e:
                    status["database"] = f"error: {str(db_e)}"
                    status["status"] = "degraded"
            else:
                status["database"] = "not_available"
                status["status"] = "degraded"
            
            return {
                "success": True,
                "data": status
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "unhealthy"
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

    async def start_monitoring(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start continuous portfolio monitoring"""
        try:
            if not MONITORING_SERVICE_AVAILABLE:
                return {"success": False, "error": "Monitoring service not available"}

            user_id = request_data.get("user_id", "default_user")
            portfolio = request_data.get("portfolio", [])
            frequency = request_data.get("frequency", "daily")
            enabled = request_data.get("enabled", True)

            if not portfolio:
                return {"success": False, "error": "Portfolio is required"}

            # Convert portfolio to PortfolioPosition objects
            positions = []
            for pos in portfolio:
                positions.append(PortfolioPosition(
                    ticker=pos.get("ticker", ""),
                    shares=pos.get("shares", 0),
                    cost_basis=pos.get("cost_basis", 0.0)
                ))

            # Calculate costs
            costs = monitoring_service.calculate_monitoring_costs(
                MonitoringFrequency(frequency),
                len(positions)
            )

            # Create monitoring settings
            settings = MonitoringSettings(
                frequency=MonitoringFrequency(frequency),
                enabled=enabled,
                cost_per_analysis=costs["cost_per_analysis"],
                estimated_monthly_cost=costs["estimated_monthly_cost"]
            )

            # Start monitoring
            status = await monitoring_service.start_monitoring(user_id, positions, settings)

            return {
                "success": True,
                "monitoring_status": {
                    "is_monitoring": status.is_monitoring,
                    "active_positions": status.active_positions,
                    "next_analysis": status.next_analysis.isoformat(),
                    "total_analyses_today": status.total_analyses_today,
                    "current_cost_today": status.current_cost_today
                },
                "settings": {
                    "frequency": settings.frequency.value,
                    "enabled": settings.enabled,
                    "cost_per_analysis": settings.cost_per_analysis,
                    "estimated_monthly_cost": settings.estimated_monthly_cost
                }
            }

        except Exception as e:
            logger.error(f"Start monitoring error: {e}")
            return {"success": False, "error": str(e)}

    async def stop_monitoring(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop continuous portfolio monitoring"""
        try:
            if not MONITORING_SERVICE_AVAILABLE:
                return {"success": False, "error": "Monitoring service not available"}

            user_id = request_data.get("user_id", "default_user")
            success = await monitoring_service.stop_monitoring(user_id)

            return {
                "success": success,
                "message": "Monitoring stopped" if success else "No active monitoring found"
            }

        except Exception as e:
            logger.error(f"Stop monitoring error: {e}")
            return {"success": False, "error": str(e)}

    async def get_monitoring_status(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current monitoring status"""
        try:
            if not MONITORING_SERVICE_AVAILABLE:
                return {"success": False, "error": "Monitoring service not available"}

            user_id = request_data.get("user_id", "default_user")
            status = await monitoring_service.get_monitoring_status(user_id)

            if not status:
                return {
                    "success": True,
                    "monitoring_status": {
                        "is_monitoring": False,
                        "active_positions": 0,
                        "next_analysis": None,
                        "total_analyses_today": 0,
                        "current_cost_today": 0.0
                    }
                }

            return {
                "success": True,
                "monitoring_status": {
                    "is_monitoring": status.is_monitoring,
                    "active_positions": status.active_positions,
                    "next_analysis": status.next_analysis.isoformat(),
                    "total_analyses_today": status.total_analyses_today,
                    "current_cost_today": status.current_cost_today
                }
            }

        except Exception as e:
            logger.error(f"Get monitoring status error: {e}")
            return {"success": False, "error": str(e)}

    async def ingest_news_article(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest and compress a news article"""
        try:
            if not NEWS_INTELLIGENCE_AVAILABLE:
                return {"success": False, "error": "News intelligence service not available"}

            ticker = request_data.get("ticker", "").upper()
            article_text = request_data.get("article_text", "")
            source_url = request_data.get("source_url", "")
            price_before = request_data.get("price_before", 0.0)
            price_1h_after = request_data.get("price_1h_after", 0.0)
            price_24h_after = request_data.get("price_24h_after", 0.0)

            if not all([ticker, article_text, price_before, price_1h_after, price_24h_after]):
                return {"success": False, "error": "Missing required fields"}

            # Ingest article and create snapshot
            snapshot = await news_intelligence.ingest_article(
                ticker=ticker,
                article_text=article_text,
                source_url=source_url,
                price_before=price_before,
                price_1h_after=price_1h_after,
                price_24h_after=price_24h_after
            )

            return {
                "success": True,
                "snapshot": {
                    "ticker": snapshot.ticker,
                    "timestamp": snapshot.timestamp.isoformat(),
                    "category": snapshot.category.value,
                    "impact": snapshot.impact.value,
                    "price_change_1h": snapshot.price_change_1h,
                    "price_change_24h": snapshot.price_change_24h,
                    "summary_line_1": snapshot.summary_line_1,
                    "summary_line_2": snapshot.summary_line_2,
                    "confidence_score": snapshot.confidence_score
                }
            }

        except Exception as e:
            logger.error(f"Ingest news article error: {e}")
            return {"success": False, "error": str(e)}

    async def get_stock_personality(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get stock personality profile"""
        try:
            if not NEWS_INTELLIGENCE_AVAILABLE:
                return {"success": False, "error": "News intelligence service not available"}

            ticker = request_data.get("ticker", "").upper()
            if not ticker:
                return {"success": False, "error": "Ticker is required"}

            personality = news_intelligence.get_stock_personality(ticker)

            if not personality:
                return {"success": False, "error": f"No personality data found for {ticker}"}

            return {
                "success": True,
                "personality": {
                    "ticker": personality.ticker,
                    "total_events": personality.total_events,
                    "avg_volatility": personality.avg_volatility,
                    "reaction_patterns": personality.reaction_patterns,
                    "sentiment_sensitivity": personality.sentiment_sensitivity,
                    "news_momentum": personality.news_momentum,
                    "last_updated": personality.last_updated.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Get stock personality error: {e}")
            return {"success": False, "error": str(e)}

    async def get_news_history(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get news history for a ticker"""
        try:
            if not NEWS_INTELLIGENCE_AVAILABLE:
                return {"success": False, "error": "News intelligence service not available"}

            ticker = request_data.get("ticker", "").upper()
            days = request_data.get("days", 365)

            if not ticker:
                return {"success": False, "error": "Ticker is required"}

            history = news_intelligence.get_news_history(ticker, days)

            return {
                "success": True,
                "history": [
                    {
                        "ticker": snapshot.ticker,
                        "timestamp": snapshot.timestamp.isoformat(),
                        "category": snapshot.category.value,
                        "impact": snapshot.impact.value,
                        "price_change_1h": snapshot.price_change_1h,
                        "price_change_24h": snapshot.price_change_24h,
                        "summary_line_1": snapshot.summary_line_1,
                        "summary_line_2": snapshot.summary_line_2,
                        "source_url": snapshot.source_url,
                        "confidence_score": snapshot.confidence_score
                    }
                    for snapshot in history
                ]
            }

        except Exception as e:
            logger.error(f"Get news history error: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_news_trends(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze news trends for a ticker"""
        try:
            if not NEWS_INTELLIGENCE_AVAILABLE:
                return {"success": False, "error": "News intelligence service not available"}

            ticker = request_data.get("ticker", "").upper()
            if not ticker:
                return {"success": False, "error": "Ticker is required"}

            trends = news_intelligence.analyze_news_trends(ticker)

            return {
                "success": True,
                "trends": trends
            }

        except Exception as e:
            logger.error(f"Analyze news trends error: {e}")
            return {"success": False, "error": str(e)}

    async def trigger_automated_news_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger automated news analysis for a ticker"""
        try:
            if not AUTOMATED_PIPELINE_AVAILABLE:
                return {"success": False, "error": "Automated pipeline not available"}

            ticker = request_data.get("ticker", "").upper()
            if not ticker:
                return {"success": False, "error": "Ticker is required"}

            # Process news for the ticker
            snapshots = await automated_pipeline.process_ticker_news(ticker)

            return {
                "success": True,
                "ticker": ticker,
                "snapshots_created": len(snapshots),
                "snapshots": [
                    {
                        "ticker": snapshot.ticker,
                        "timestamp": snapshot.timestamp.isoformat(),
                        "category": snapshot.category.value,
                        "impact": snapshot.impact.value,
                        "price_change_1h": snapshot.price_change_1h,
                        "price_change_24h": snapshot.price_change_24h,
                        "summary_line_1": snapshot.summary_line_1,
                        "summary_line_2": snapshot.summary_line_2,
                        "confidence_score": snapshot.confidence_score
                    }
                    for snapshot in snapshots
                ]
            }

        except Exception as e:
            logger.error(f"Trigger automated news analysis error: {e}")
            return {"success": False, "error": str(e)}

    async def start_continuous_monitoring(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start continuous news monitoring for multiple tickers"""
        try:
            if not AUTOMATED_PIPELINE_AVAILABLE:
                return {"success": False, "error": "Automated pipeline not available"}

            tickers = request_data.get("tickers", [])
            interval_minutes = request_data.get("interval_minutes", 30)

            if not tickers:
                return {"success": False, "error": "At least one ticker is required"}

            # Start continuous monitoring in background
            import asyncio
            asyncio.create_task(
                automated_pipeline.run_continuous_monitoring(tickers, interval_minutes)
            )

            return {
                "success": True,
                "message": f"Started continuous monitoring for {len(tickers)} tickers",
                "tickers": tickers,
                "interval_minutes": interval_minutes
            }

        except Exception as e:
            logger.error(f"Start continuous monitoring error: {e}")
            return {"success": False, "error": str(e)}

    async def get_pipeline_status(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get status of the automated news pipeline"""
        try:
            if not AUTOMATED_PIPELINE_AVAILABLE:
                return {"success": False, "error": "Automated pipeline not available"}

            return {
                "success": True,
                "pipeline_status": {
                    "available": True,
                    "processed_articles": len(automated_pipeline.processed_articles),
                    "fmp_api_configured": bool(automated_pipeline.fmp_api_key),
                    "grok_api_configured": bool(automated_pipeline.grok_api_key)
                }
            }

        except Exception as e:
            logger.error(f"Get pipeline status error: {e}")
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
        elif action == "start_monitoring":
            return await api_handler.start_monitoring(request_data)
        elif action == "stop_monitoring":
            return await api_handler.stop_monitoring(request_data)
        elif action == "get_monitoring_status":
            return await api_handler.get_monitoring_status(request_data)
        elif action == "ingest_news_article":
            return await api_handler.ingest_news_article(request_data)
        elif action == "get_stock_personality":
            return await api_handler.get_stock_personality(request_data)
        elif action == "get_news_history":
            return await api_handler.get_news_history(request_data)
        elif action == "analyze_news_trends":
            return await api_handler.analyze_news_trends(request_data)
        elif action == "trigger_automated_news_analysis":
            return await api_handler.trigger_automated_news_analysis(request_data)
        elif action == "start_continuous_monitoring":
            return await api_handler.start_continuous_monitoring(request_data)
        elif action == "get_pipeline_status":
            return await api_handler.get_pipeline_status(request_data)
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
        # Handle OPTIONS requests for CORS
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                },
                "body": ""
            }
        
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
        
        # Process the request - use asyncio.run with proper error handling
        try:
            # Create new event loop for serverless environment
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(api(request_data))
            finally:
                loop.close()
        except Exception as async_e:
            logger.error(f"Async processing error: {async_e}")
            # Fallback to synchronous processing for critical errors
            result = {"success": False, "error": f"Async processing failed: {str(async_e)}"}
        
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
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
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