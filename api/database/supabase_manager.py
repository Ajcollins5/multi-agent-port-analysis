import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import logging
from supabase import create_client, Client
from supabase.client import ClientOptions
import asyncpg
from contextlib import asynccontextmanager

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
POSTGRES_URL = os.environ.get("POSTGRES_URL")

class SupabaseManager:
    """Enhanced Supabase manager with real-time capabilities and connection pooling"""
    
    def __init__(self):
        if not SUPABASE_URL:
            raise ValueError("SUPABASE_URL environment variable is required")
        
        if not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is required")
        
        # Initialize Supabase client with service role for backend operations
        self.client: Client = create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_ROLE_KEY,
            options=ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                auto_refresh_token=True,
                persist_session=True,
            )
        )
        
        # Connection pool for high-performance operations
        self.pool: Optional[asyncpg.Pool] = None
        self._pool_lock = asyncio.Lock()
        
    async def _get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool for direct PostgreSQL access"""
        if self.pool is None:
            async with self._pool_lock:
                if self.pool is None:  # Double-check pattern
                    if not POSTGRES_URL:
                        raise ValueError("POSTGRES_URL environment variable is required for connection pooling")
                    
                    self.pool = await asyncpg.create_pool(
                        POSTGRES_URL,
                        min_size=1,  # Minimum for serverless
                        max_size=5,  # Conservative limit for Vercel
                        command_timeout=30,
                        server_settings={
                            'jit': 'off',  # Disable JIT for faster startup
                            'application_name': 'supabase_portfolio_analysis'
                        }
                    )
        return self.pool
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connections"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            yield conn
    
    async def store_insight(self, ticker: str, insight: str, agent: str = None, 
                          metadata: Dict[str, Any] = None, 
                          volatility: float = None,
                          impact_level: str = None,
                          confidence: float = None) -> Dict[str, Any]:
        """Store insight with real-time updates"""
        try:
            data = {
                "ticker": ticker,
                "insight": insight,
                "agent": agent or "Unknown",
                "volatility": volatility,
                "impact_level": impact_level,
                "confidence": confidence,
                "metadata": metadata or {}
            }
            
            result = self.client.table("insights").insert(data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "insight_id": result.data[0]["id"],
                    "message": "Insight stored successfully"
                }
            else:
                return {"success": False, "error": "Failed to store insight"}
                
        except Exception as e:
            logging.error(f"Failed to store insight: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_insights(self, ticker: str = None, limit: int = 10, 
                         agent: str = None, 
                         impact_level: str = None,
                         time_window_hours: int = None) -> Dict[str, Any]:
        """Get insights with advanced filtering"""
        try:
            query = self.client.table("insights").select("*")
            
            if ticker:
                query = query.eq("ticker", ticker)
            if agent:
                query = query.eq("agent", agent)
            if impact_level:
                query = query.eq("impact_level", impact_level)
            if time_window_hours:
                cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
                query = query.gte("timestamp", cutoff_time.isoformat())
            
            result = query.order("timestamp", desc=True).limit(limit).execute()
            
            return {
                "success": True,
                "insights": result.data,
                "total_count": len(result.data)
            }
            
        except Exception as e:
            logging.error(f"Failed to get insights: {e}")
            return {"success": False, "error": str(e), "insights": []}
    
    async def store_event(self, event_type: str, ticker: str, message: str, 
                        severity: str = "INFO", 
                        metadata: Dict[str, Any] = None,
                        volatility: float = None,
                        volume_spike: float = None,
                        portfolio_risk: str = None) -> Dict[str, Any]:
        """Store event with real-time broadcasting"""
        try:
            data = {
                "event_type": event_type,
                "ticker": ticker,
                "message": message,
                "severity": severity,
                "volatility": volatility,
                "volume_spike": volume_spike,
                "portfolio_risk": portfolio_risk,
                "metadata": metadata or {}
            }
            
            result = self.client.table("events").insert(data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "event_id": result.data[0]["id"],
                    "message": "Event stored successfully"
                }
            else:
                return {"success": False, "error": "Failed to store event"}
                
        except Exception as e:
            logging.error(f"Failed to store event: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_events(self, ticker: str = None, 
                       event_type: str = None,
                       severity: str = None,
                       time_window_hours: int = 24,
                       limit: int = 50) -> Dict[str, Any]:
        """Get events with filtering"""
        try:
            query = self.client.table("events").select("*")
            
            if ticker:
                query = query.eq("ticker", ticker)
            if event_type:
                query = query.eq("event_type", event_type)
            if severity:
                query = query.eq("severity", severity)
            if time_window_hours:
                cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
                query = query.gte("timestamp", cutoff_time.isoformat())
            
            result = query.order("timestamp", desc=True).limit(limit).execute()
            
            return {
                "success": True,
                "events": result.data,
                "total_count": len(result.data)
            }
            
        except Exception as e:
            logging.error(f"Failed to get events: {e}")
            return {"success": False, "error": str(e), "events": []}
    
    async def store_knowledge_evolution(self, ticker: str, evolution_type: str, 
                                     previous_insight: str, refined_insight: str,
                                     improvement_score: float, agent: str,
                                     context: str = None,
                                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Store knowledge evolution tracking"""
        try:
            data = {
                "ticker": ticker,
                "evolution_type": evolution_type,
                "previous_insight": previous_insight,
                "refined_insight": refined_insight,
                "improvement_score": improvement_score,
                "agent": agent,
                "context": context,
                "metadata": metadata or {}
            }
            
            result = self.client.table("knowledge_evolution").insert(data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "evolution_id": result.data[0]["id"],
                    "message": "Knowledge evolution stored successfully"
                }
            else:
                return {"success": False, "error": "Failed to store knowledge evolution"}
                
        except Exception as e:
            logging.error(f"Failed to store knowledge evolution: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_knowledge_evolution(self, ticker: str = None,
                                   evolution_type: str = None,
                                   agent: str = None,
                                   limit: int = 20) -> Dict[str, Any]:
        """Get knowledge evolution with trend analysis"""
        try:
            query = self.client.table("knowledge_evolution").select("*")
            
            if ticker:
                query = query.eq("ticker", ticker)
            if evolution_type:
                query = query.eq("evolution_type", evolution_type)
            if agent:
                query = query.eq("agent", agent)
            
            result = query.order("timestamp", desc=True).limit(limit).execute()
            
            # Calculate trend analysis
            evolutions = result.data
            if evolutions:
                avg_improvement = sum(e["improvement_score"] for e in evolutions) / len(evolutions)
                trend_analysis = {
                    "average_improvement": avg_improvement,
                    "total_evolutions": len(evolutions),
                    "agents_involved": list(set(e["agent"] for e in evolutions)),
                    "evolution_types": list(set(e["evolution_type"] for e in evolutions))
                }
            else:
                trend_analysis = {
                    "average_improvement": 0,
                    "total_evolutions": 0,
                    "agents_involved": [],
                    "evolution_types": []
                }
            
            return {
                "success": True,
                "evolutions": evolutions,
                "trend_analysis": trend_analysis
            }
            
        except Exception as e:
            logging.error(f"Failed to get knowledge evolution: {e}")
            return {"success": False, "error": str(e), "evolutions": []}
    
    async def store_portfolio_analysis(self, portfolio_size: int, analyzed_stocks: int,
                                     high_impact_count: int, portfolio_risk: str,
                                     analysis_duration: float = 0,
                                     agents_used: List[str] = None,
                                     synthesis_summary: str = None,
                                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Store portfolio analysis results"""
        try:
            data = {
                "portfolio_size": portfolio_size,
                "analyzed_stocks": analyzed_stocks,
                "high_impact_count": high_impact_count,
                "portfolio_risk": portfolio_risk,
                "analysis_duration": analysis_duration,
                "agents_used": agents_used or [],
                "synthesis_summary": synthesis_summary,
                "metadata": metadata or {}
            }
            
            result = self.client.table("portfolio_analysis").insert(data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "analysis_id": result.data[0]["id"],
                    "message": "Portfolio analysis stored successfully"
                }
            else:
                return {"success": False, "error": "Failed to store portfolio analysis"}
                
        except Exception as e:
            logging.error(f"Failed to store portfolio analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_portfolio_analysis(self, limit: int = 20) -> Dict[str, Any]:
        """Get recent portfolio analysis results"""
        try:
            result = self.client.table("portfolio_analysis").select("*").order("timestamp", desc=True).limit(limit).execute()
            
            return {
                "success": True,
                "analyses": result.data,
                "total_count": len(result.data)
            }
            
        except Exception as e:
            logging.error(f"Failed to get portfolio analysis: {e}")
            return {"success": False, "error": str(e), "analyses": []}
    
    async def store_system_metric(self, metric_type: str, metric_value: float,
                                additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Store system performance metrics"""
        try:
            data = {
                "metric_type": metric_type,
                "metric_value": metric_value,
                "additional_data": additional_data or {}
            }
            
            result = self.client.table("system_metrics").insert(data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "metric_id": result.data[0]["id"],
                    "message": "System metric stored successfully"
                }
            else:
                return {"success": False, "error": "Failed to store system metric"}
                
        except Exception as e:
            logging.error(f"Failed to store system metric: {e}")
            return {"success": False, "error": str(e)}
    
    def subscribe_to_changes(self, table: str, callback):
        """Subscribe to real-time changes"""
        try:
            channel = self.client.channel(f'realtime:{table}')
            channel.on('postgres_changes', {
                'event': '*',
                'schema': 'public',
                'table': table
            }, callback)
            channel.subscribe()
            return channel
        except Exception as e:
            logging.error(f"Failed to subscribe to {table}: {e}")
            return None
    
    async def bulk_insert(self, table: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """High-performance bulk insert using direct PostgreSQL connection"""
        try:
            if not data:
                return {"success": True, "inserted_count": 0}
            
            async with self.get_connection() as conn:
                columns = list(data[0].keys())
                placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
                query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                
                values = [[row[col] for col in columns] for row in data]
                await conn.executemany(query, values)
                
                return {"success": True, "inserted_count": len(data)}
                
        except Exception as e:
            logging.error(f"Bulk insert failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_query(self, query: str, params: List = None) -> Dict[str, Any]:
        """Execute custom SQL query with connection pooling"""
        try:
            async with self.get_connection() as conn:
                result = await conn.fetch(query, *(params or []))
                return {"success": True, "data": [dict(row) for row in result]}
                
        except Exception as e:
            logging.error(f"Query execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_insights_summary(self) -> Dict[str, Any]:
        """Get insights summary using the database view"""
        try:
            result = self.client.table("insights_summary").select("*").execute()
            return {
                "success": True,
                "summary": result.data
            }
        except Exception as e:
            logging.error(f"Failed to get insights summary: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_portfolio_risk_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get portfolio risk trends"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = f"""
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour,
                    portfolio_risk,
                    COUNT(*) as analysis_count,
                    AVG(high_impact_count) as avg_high_impact,
                    AVG(analysis_duration) as avg_duration
                FROM portfolio_analysis
                WHERE timestamp >= '{cutoff_time.isoformat()}'
                GROUP BY DATE_TRUNC('hour', timestamp), portfolio_risk
                ORDER BY hour DESC
            """
            
            result = await self.execute_query(query)
            
            if result["success"]:
                return {
                    "success": True,
                    "trends": result["data"]
                }
            else:
                return result
                
        except Exception as e:
            logging.error(f"Failed to get portfolio risk trends: {e}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """Clean up old data using the database function"""
        try:
            query = f"SELECT cleanup_old_data({days_to_keep})"
            result = await self.execute_query(query)
            
            if result["success"]:
                deleted_count = result["data"][0]["cleanup_old_data"]
                return {
                    "success": True,
                    "deleted_count": deleted_count,
                    "message": f"Cleaned up {deleted_count} old records"
                }
            else:
                return result
                
        except Exception as e:
            logging.error(f"Failed to cleanup old data: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None

# Create global instance
try:
    supabase_manager = SupabaseManager()
except Exception as e:
    logging.error(f"Failed to initialize Supabase manager: {e}")
    supabase_manager = None 