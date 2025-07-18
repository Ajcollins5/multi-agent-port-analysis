import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import threading
import logging

# Environment variables for database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "")
REDIS_URL = os.environ.get("REDIS_URL", "")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# Thread-safe in-memory storage for Vercel ephemeral environment
_storage_lock = threading.Lock()
_insights_storage = []
_events_storage = []
_knowledge_storage = []

class StorageManager:
    """Enhanced storage manager with SQLite persistence for insights, events, and knowledge evolution"""
    
    def __init__(self, db_path: str = "portfolio_analysis.db"):
        self.db_path = db_path
        self.use_external_db = bool(DATABASE_URL)
        self.use_redis = bool(REDIS_URL)
        
        # Initialize database
        self._init_database()
        
        if self.use_external_db:
            try:
                self.init_external_db()
            except Exception as e:
                logging.error(f"Failed to initialize external DB: {e}")
                self.use_external_db = False
        
        if self.use_redis:
            try:
                self.init_redis()
            except Exception as e:
                logging.error(f"Failed to initialize Redis: {e}")
                self.use_redis = False
    
    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create insights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    insight TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    volatility REAL,
                    impact_level TEXT,
                    confidence REAL,
                    metadata TEXT,
                    refined BOOLEAN DEFAULT FALSE,
                    original_insight TEXT
                )
            """)
            
            # Create indexes for insights table
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_insights_ticker ON insights(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_insights_agent ON insights(agent)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_insights_timestamp ON insights(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_insights_impact_level ON insights(impact_level)")
            
            # Create events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT DEFAULT 'INFO',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    volatility REAL,
                    volume_spike REAL,
                    portfolio_risk TEXT,
                    correlation_data TEXT,
                    metadata TEXT
                )
            """)
            
            # Create indexes for events table
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_ticker ON events(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
            
            # Create knowledge_evolution table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    evolution_type TEXT NOT NULL,
                    previous_insight TEXT,
                    refined_insight TEXT NOT NULL,
                    improvement_score REAL,
                    agent TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    context TEXT,
                    metadata TEXT
                )
            """)
            
            # Create indexes for knowledge_evolution table
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_ticker ON knowledge_evolution(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_evolution(evolution_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_agent ON knowledge_evolution(agent)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_timestamp ON knowledge_evolution(timestamp)")
            
            # Create portfolio_analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_size INTEGER NOT NULL,
                    analyzed_stocks INTEGER NOT NULL,
                    high_impact_count INTEGER NOT NULL,
                    portfolio_risk TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    analysis_duration REAL,
                    agents_used TEXT,
                    synthesis_summary TEXT,
                    metadata TEXT
                )
            """)
            
            # Create indexes for portfolio_analysis table
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_timestamp ON portfolio_analysis(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_risk ON portfolio_analysis(portfolio_risk)")
            
            # Create system_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    additional_data TEXT
                )
            """)
            
            # Create indexes for system_metrics table
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_type ON system_metrics(metric_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)")
            
            conn.commit()
            conn.close()
            logging.info("Database initialized successfully")
            
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise
    
    def init_external_db(self):
        """Initialize external database connection"""
        # For production, this would connect to PostgreSQL
        # For now, fallback to enhanced SQLite
        pass
    
    def init_redis(self):
        """Initialize Redis connection for caching"""
        try:
            import redis
            self.redis_client = redis.Redis.from_url(REDIS_URL)
            self.redis_client.ping()
            logging.info("Redis connection established")
        except ImportError:
            logging.error("Redis library not available")
            self.use_redis = False
            raise
        except Exception as e:
            logging.error(f"Redis connection failed: {e}")
            raise
    
    def store_insight(self, ticker: str, insight: str, agent: Optional[str] = None, 
                     metadata: Optional[Dict[str, Any]] = None, 
                     volatility: Optional[float] = None,
                     impact_level: Optional[str] = None,
                     confidence: Optional[float] = None) -> Dict[str, Any]:
        """Store insight with enhanced metadata"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare metadata
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO insights (ticker, insight, agent, volatility, impact_level, confidence, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ticker, insight, agent or "Unknown", volatility, impact_level, confidence, metadata_json))
            
            insight_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Cache in Redis if available
            if self.use_redis:
                try:
                    cache_key = f"insight:{ticker}:{insight_id}"
                    cache_data = {
                        "id": insight_id,
                        "ticker": ticker,
                        "insight": insight,
                        "agent": agent,
                        "timestamp": datetime.now().isoformat(),
                        "volatility": volatility,
                        "impact_level": impact_level,
                        "confidence": confidence
                    }
                    self.redis_client.setex(cache_key, 3600, json.dumps(cache_data))
                except Exception as e:
                    logging.warning(f"Redis caching failed: {e}")
            
            return {
                "success": True,
                "insight_id": insight_id,
                "message": "Insight stored successfully"
            }
            
        except Exception as e:
            logging.error(f"Failed to store insight: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_insights(self, ticker: Optional[str] = None, limit: int = 10, 
                    agent: Optional[str] = None, 
                    impact_level: Optional[str] = None,
                    time_window_hours: Optional[int] = None) -> Dict[str, Any]:
        """Get insights with filtering and pagination"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query dynamically
            query = "SELECT * FROM insights WHERE 1=1"
            params = []
            
            if ticker:
                query += " AND ticker = ?"
                params.append(ticker)
            
            if agent:
                query += " AND agent = ?"
                params.append(agent)
            
            if impact_level:
                query += " AND impact_level = ?"
                params.append(impact_level)
            
            if time_window_hours:
                cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
                query += " AND timestamp > ?"
                params.append(cutoff_time.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to dictionaries
            insights = []
            for row in rows:
                insight = {
                    "id": row[0],
                    "ticker": row[1],
                    "insight": row[2],
                    "agent": row[3],
                    "timestamp": row[4],
                    "volatility": row[5],
                    "impact_level": row[6],
                    "confidence": row[7],
                    "metadata": json.loads(row[8]) if row[8] else None,
                    "refined": bool(row[9]),
                    "original_insight": row[10]
                }
                insights.append(insight)
            
            conn.close()
            
            return {
                "success": True,
                "insights": insights,
                "total_count": len(insights)
            }
            
        except Exception as e:
            logging.error(f"Failed to get insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "insights": []
            }
    
    def store_event(self, event_type: str, ticker: str, message: str, 
                   severity: str = "INFO", 
                   metadata: Optional[Dict[str, Any]] = None,
                   volatility: Optional[float] = None,
                   volume_spike: Optional[float] = None,
                   portfolio_risk: Optional[str] = None) -> Dict[str, Any]:
        """Store event with enhanced tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO events (event_type, ticker, message, severity, volatility, 
                                   volume_spike, portfolio_risk, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_type, ticker, message, severity, volatility, volume_spike, 
                  portfolio_risk, metadata_json))
            
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "event_id": event_id,
                "message": "Event stored successfully"
            }
            
        except Exception as e:
            logging.error(f"Failed to store event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_events(self, ticker: Optional[str] = None, 
                  event_type: Optional[str] = None,
                  severity: Optional[str] = None,
                  time_window_hours: int = 24,
                  limit: int = 50) -> Dict[str, Any]:
        """Get events with filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if ticker:
                query += " AND ticker = ?"
                params.append(ticker)
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            if time_window_hours:
                cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
                query += " AND timestamp > ?"
                params.append(cutoff_time.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to dictionaries
            events = []
            for row in rows:
                event = {
                    "id": row[0],
                    "event_type": row[1],
                    "ticker": row[2],
                    "message": row[3],
                    "severity": row[4],
                    "timestamp": row[5],
                    "volatility": row[6],
                    "volume_spike": row[7],
                    "portfolio_risk": row[8],
                    "metadata": json.loads(row[10]) if row[10] else None
                }
                events.append(event)
            
            conn.close()
            
            return {
                "success": True,
                "events": events,
                "total_count": len(events)
            }
            
        except Exception as e:
            logging.error(f"Failed to get events: {e}")
            return {
                "success": False,
                "error": str(e),
                "events": []
            }
    
    def store_knowledge_evolution(self, ticker: str, evolution_type: str, 
                                 previous_insight: str, refined_insight: str,
                                 improvement_score: float, agent: str,
                                 context: Optional[str] = None,
                                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store knowledge evolution tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO knowledge_evolution (ticker, evolution_type, previous_insight, 
                                               refined_insight, improvement_score, agent, context, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticker, evolution_type, previous_insight, refined_insight, 
                  improvement_score, agent, context, metadata_json))
            
            evolution_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "evolution_id": evolution_id,
                "message": "Knowledge evolution stored successfully"
            }
            
        except Exception as e:
            logging.error(f"Failed to store knowledge evolution: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_knowledge_evolution(self, ticker: Optional[str] = None,
                               evolution_type: Optional[str] = None,
                               agent: Optional[str] = None,
                               limit: int = 20) -> Dict[str, Any]:
        """Get knowledge evolution with trend analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM knowledge_evolution WHERE 1=1"
            params = []
            
            if ticker:
                query += " AND ticker = ?"
                params.append(ticker)
            
            if evolution_type:
                query += " AND evolution_type = ?"
                params.append(evolution_type)
            
            if agent:
                query += " AND agent = ?"
                params.append(agent)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to dictionaries and analyze trends
            evolutions = []
            for row in rows:
                evolution = {
                    "id": row[0],
                    "ticker": row[1],
                    "evolution_type": row[2],
                    "previous_insight": row[3],
                    "refined_insight": row[4],
                    "improvement_score": row[5],
                    "agent": row[6],
                    "timestamp": row[7],
                    "context": row[8],
                    "metadata": json.loads(row[9]) if row[9] else None
                }
                evolutions.append(evolution)
            
            # Calculate trend metrics
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
            
            conn.close()
            
            return {
                "success": True,
                "evolutions": evolutions,
                "trend_analysis": trend_analysis
            }
            
        except Exception as e:
            logging.error(f"Failed to get knowledge evolution: {e}")
            return {
                "success": False,
                "error": str(e),
                "evolutions": []
            }
    
    def store_portfolio_analysis(self, portfolio_size: int, analyzed_stocks: int,
                               high_impact_count: int, portfolio_risk: str,
                               analysis_duration: float, agents_used: List[str],
                               synthesis_summary: str,
                               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store portfolio analysis results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            agents_json = json.dumps(agents_used)
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO portfolio_analysis (portfolio_size, analyzed_stocks, high_impact_count,
                                              portfolio_risk, analysis_duration, agents_used, 
                                              synthesis_summary, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (portfolio_size, analyzed_stocks, high_impact_count, portfolio_risk,
                  analysis_duration, agents_json, synthesis_summary, metadata_json))
            
            analysis_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "message": "Portfolio analysis stored successfully"
            }
            
        except Exception as e:
            logging.error(f"Failed to store portfolio analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_portfolio_metrics(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get portfolio metrics and trends"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            
            # Get recent analyses
            cursor.execute("""
                SELECT * FROM portfolio_analysis 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            """, (cutoff_time.isoformat(),))
            
            rows = cursor.fetchall()
            
            if not rows:
                return {
                    "success": True,
                    "metrics": {
                        "total_analyses": 0,
                        "average_portfolio_size": 0,
                        "average_high_impact": 0,
                        "risk_distribution": {},
                        "trend": "stable"
                    }
                }
            
            # Calculate metrics
            total_analyses = len(rows)
            avg_portfolio_size = sum(row[1] for row in rows) / total_analyses
            avg_high_impact = sum(row[3] for row in rows) / total_analyses
            
            # Risk distribution
            risk_distribution = {}
            for row in rows:
                risk = row[4]
                risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
            
            # Trend analysis (simple)
            if len(rows) >= 2:
                recent_risk = rows[0][4]
                older_risk = rows[-1][4]
                risk_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
                trend = "improving" if risk_levels.get(recent_risk, 2) < risk_levels.get(older_risk, 2) else "deteriorating"
            else:
                trend = "stable"
            
            conn.close()
            
            return {
                "success": True,
                "metrics": {
                    "total_analyses": total_analyses,
                    "average_portfolio_size": avg_portfolio_size,
                    "average_high_impact": avg_high_impact,
                    "risk_distribution": risk_distribution,
                    "trend": trend
                }
            }
            
        except Exception as e:
            logging.error(f"Failed to get portfolio metrics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_insights_csv(self, ticker: Optional[str] = None, 
                           time_window_hours: Optional[int] = None) -> Dict[str, Any]:
        """Export insights to CSV format"""
        try:
            import csv
            import io
            
            insights_data = self.get_insights(ticker=ticker, time_window_hours=time_window_hours, limit=1000)
            
            if not insights_data["success"]:
                return insights_data
            
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Ticker", "Insight", "Agent", "Timestamp", 
                "Volatility", "Impact Level", "Confidence", "Refined"
            ])
            
            # Write data
            for insight in insights_data["insights"]:
                writer.writerow([
                    insight["id"],
                    insight["ticker"],
                    insight["insight"],
                    insight["agent"],
                    insight["timestamp"],
                    insight["volatility"],
                    insight["impact_level"],
                    insight["confidence"],
                    insight["refined"]
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                "success": True,
                "csv_content": csv_content,
                "filename": f"insights_{ticker or 'all'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
            
        except Exception as e:
            logging.error(f"Failed to export CSV: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_storage(self, confirm: bool = False) -> Dict[str, Any]:
        """Clear storage (for testing/maintenance)"""
        if not confirm:
            return {
                "success": False,
                "error": "Must confirm clearing storage"
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear all tables
            cursor.execute("DELETE FROM insights")
            cursor.execute("DELETE FROM events")
            cursor.execute("DELETE FROM knowledge_evolution")
            cursor.execute("DELETE FROM portfolio_analysis")
            cursor.execute("DELETE FROM system_metrics")
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "Storage cleared successfully"
            }
            
        except Exception as e:
            logging.error(f"Failed to clear storage: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global storage instance
storage_manager = StorageManager()

# Export functions for backward compatibility
def get_insights(ticker: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Get insights using global storage manager"""
    return storage_manager.get_insights(ticker=ticker, limit=limit)

def store_insight(ticker: str, insight: str, agent: Optional[str] = None, 
                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Store insight using global storage manager"""
    return storage_manager.store_insight(ticker=ticker, insight=insight, agent=agent, metadata=metadata)

# Export for Vercel
def handler(request):
    """Vercel serverless function handler for StorageManager"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action")
            
            if action == "store_insight":
                ticker = body.get("ticker")
                insight = body.get("insight")
                if not ticker or not insight:
                    return json.dumps({"error": "ticker and insight are required"})
                result = storage_manager.store_insight(
                    ticker=ticker,
                    insight=insight,
                    agent=body.get("agent"),
                    metadata=body.get("metadata"),
                    volatility=body.get("volatility"),
                    impact_level=body.get("impact_level"),
                    confidence=body.get("confidence")
                )
                return json.dumps(result)
            
            elif action == "get_insights":
                result = storage_manager.get_insights(
                    ticker=body.get("ticker"),
                    limit=body.get("limit", 10),
                    agent=body.get("agent"),
                    impact_level=body.get("impact_level"),
                    time_window_hours=body.get("time_window_hours")
                )
                return json.dumps(result)
            
            elif action == "store_event":
                event_type = body.get("event_type")
                ticker = body.get("ticker")
                message = body.get("message")
                if not event_type or not ticker or not message:
                    return json.dumps({"error": "event_type, ticker, and message are required"})
                result = storage_manager.store_event(
                    event_type=event_type,
                    ticker=ticker,
                    message=message,
                    severity=body.get("severity", "INFO"),
                    metadata=body.get("metadata"),
                    volatility=body.get("volatility"),
                    volume_spike=body.get("volume_spike"),
                    portfolio_risk=body.get("portfolio_risk")
                )
                return json.dumps(result)
            
            elif action == "get_events":
                result = storage_manager.get_events(
                    ticker=body.get("ticker"),
                    event_type=body.get("event_type"),
                    severity=body.get("severity"),
                    time_window_hours=body.get("time_window_hours", 24),
                    limit=body.get("limit", 50)
                )
                return json.dumps(result)
            
            elif action == "store_knowledge_evolution":
                ticker = body.get("ticker")
                evolution_type = body.get("evolution_type")
                previous_insight = body.get("previous_insight")
                refined_insight = body.get("refined_insight")
                improvement_score = body.get("improvement_score")
                agent = body.get("agent")
                if not all([ticker, evolution_type, previous_insight, refined_insight, improvement_score, agent]):
                    return json.dumps({"error": "ticker, evolution_type, previous_insight, refined_insight, improvement_score, and agent are required"})
                result = storage_manager.store_knowledge_evolution(
                    ticker=ticker,
                    evolution_type=evolution_type,
                    previous_insight=previous_insight,
                    refined_insight=refined_insight,
                    improvement_score=improvement_score,
                    agent=agent,
                    context=body.get("context"),
                    metadata=body.get("metadata")
                )
                return json.dumps(result)
            
            elif action == "get_knowledge_evolution":
                result = storage_manager.get_knowledge_evolution(
                    ticker=body.get("ticker"),
                    evolution_type=body.get("evolution_type"),
                    agent=body.get("agent"),
                    limit=body.get("limit", 20)
                )
                return json.dumps(result)
            
            elif action == "export_csv":
                result = storage_manager.export_insights_csv(
                    ticker=body.get("ticker"),
                    time_window_hours=body.get("time_window_hours")
                )
                return json.dumps(result)
            
            elif action == "portfolio_metrics":
                result = storage_manager.get_portfolio_metrics(
                    time_window_hours=body.get("time_window_hours", 24)
                )
                return json.dumps(result)
            
            else:
                return json.dumps({
                    "error": "Invalid action",
                    "available_actions": [
                        "store_insight", "get_insights", "store_event", "get_events",
                        "store_knowledge_evolution", "get_knowledge_evolution", 
                        "export_csv", "portfolio_metrics"
                    ]
                })
        
        else:
            return json.dumps({
                "service": "StorageManager",
                "description": "Enhanced SQLite storage with insights, events, and knowledge evolution",
                "endpoints": [
                    "POST - store_insight: Store portfolio insights",
                    "POST - get_insights: Retrieve insights with filtering",
                    "POST - store_event: Store portfolio events",
                    "POST - get_events: Retrieve events",
                    "POST - store_knowledge_evolution: Track knowledge evolution",
                    "POST - get_knowledge_evolution: Get evolution trends",
                    "POST - export_csv: Export insights to CSV",
                    "POST - portfolio_metrics: Get portfolio metrics"
                ],
                "features": [
                    "SQLite persistence",
                    "Redis caching",
                    "Knowledge evolution tracking",
                    "CSV export",
                    "Portfolio metrics",
                    "Event monitoring"
                ],
                "status": "active"
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "service": "StorageManager"})

# Export handler for Vercel
app = handler 