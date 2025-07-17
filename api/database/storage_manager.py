import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import threading

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
    """Manages data storage with fallback from external DB to in-memory"""
    
    def __init__(self):
        self.use_external_db = bool(DATABASE_URL)
        self.use_redis = bool(REDIS_URL)
        
        if self.use_external_db:
            try:
                self.init_external_db()
            except Exception as e:
                print(f"Failed to initialize external DB: {e}")
                self.use_external_db = False
        
        if self.use_redis:
            try:
                self.init_redis()
            except Exception as e:
                print(f"Failed to initialize Redis: {e}")
                self.use_redis = False
    
    def init_external_db(self):
        """Initialize external database connection"""
        # This would typically be PostgreSQL for production
        # For now, using SQLite as fallback
        self.db_connection = sqlite3.connect(":memory:")
        self.init_tables()
    
    def init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            self.redis_client = redis.from_url(REDIS_URL)
            self.redis_client.ping()
        except ImportError:
            print("Redis library not installed")
            self.use_redis = False
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.use_redis = False
    
    def init_tables(self):
        """Initialize database tables"""
        if self.use_external_db:
            cursor = self.db_connection.cursor()
            
            # Insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    insight TEXT NOT NULL,
                    agent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    ticker TEXT,
                    message TEXT,
                    severity TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Knowledge evolution table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    evolution_type TEXT,
                    previous_insight TEXT,
                    refined_insight TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            self.db_connection.commit()
    
    def store_insight(self, ticker: str, insight: str, agent: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store insight with fallback to in-memory storage"""
        try:
            insight_data = {
                "ticker": ticker,
                "insight": insight,
                "agent": agent,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            if self.use_external_db:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO insights (ticker, insight, agent, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (ticker, insight, agent, json.dumps(metadata or {})))
                self.db_connection.commit()
                insight_data["id"] = cursor.lastrowid
            
            # Always store in memory as backup
            with _storage_lock:
                _insights_storage.append(insight_data)
            
            # Cache in Redis if available
            if self.use_redis:
                cache_key = f"insight:{ticker}:{datetime.now().timestamp()}"
                self.redis_client.setex(cache_key, 3600, json.dumps(insight_data))
            
            return {
                "success": True,
                "insight_id": insight_data.get("id"),
                "stored_in": self._get_storage_method()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_insights(self, ticker: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Retrieve insights with fallback"""
        try:
            insights = []
            
            if self.use_external_db:
                cursor = self.db_connection.cursor()
                if ticker:
                    cursor.execute('''
                        SELECT ticker, insight, agent, timestamp, metadata 
                        FROM insights 
                        WHERE ticker = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (ticker, limit))
                else:
                    cursor.execute('''
                        SELECT ticker, insight, agent, timestamp, metadata 
                        FROM insights 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (limit,))
                
                for row in cursor.fetchall():
                    insights.append({
                        "ticker": row[0],
                        "insight": row[1],
                        "agent": row[2],
                        "timestamp": row[3],
                        "metadata": json.loads(row[4]) if row[4] else {}
                    })
            
            # Fallback to in-memory storage
            if not insights:
                with _storage_lock:
                    filtered_insights = _insights_storage
                    if ticker:
                        filtered_insights = [i for i in _insights_storage if i["ticker"] == ticker]
                    
                    insights = sorted(filtered_insights, key=lambda x: x["timestamp"], reverse=True)[:limit]
            
            return {
                "success": True,
                "insights": insights,
                "total_count": len(insights),
                "source": self._get_storage_method()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def store_event(self, event_type: str, ticker: str, message: str, severity: str = "INFO", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store event with fallback"""
        try:
            event_data = {
                "event_type": event_type,
                "ticker": ticker,
                "message": message,
                "severity": severity,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            if self.use_external_db:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO events (event_type, ticker, message, severity, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (event_type, ticker, message, severity, json.dumps(metadata or {})))
                self.db_connection.commit()
                event_data["id"] = cursor.lastrowid
            
            # Always store in memory as backup
            with _storage_lock:
                _events_storage.append(event_data)
            
            return {
                "success": True,
                "event_id": event_data.get("id"),
                "stored_in": self._get_storage_method()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_events(self, event_type: Optional[str] = None, ticker: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Retrieve events with fallback"""
        try:
            events = []
            
            if self.use_external_db:
                cursor = self.db_connection.cursor()
                query = "SELECT event_type, ticker, message, severity, timestamp, metadata FROM events WHERE 1=1"
                params = []
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                
                if ticker:
                    query += " AND ticker = ?"
                    params.append(ticker)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                for row in cursor.fetchall():
                    events.append({
                        "event_type": row[0],
                        "ticker": row[1],
                        "message": row[2],
                        "severity": row[3],
                        "timestamp": row[4],
                        "metadata": json.loads(row[5]) if row[5] else {}
                    })
            
            # Fallback to in-memory storage
            if not events:
                with _storage_lock:
                    filtered_events = _events_storage
                    if event_type:
                        filtered_events = [e for e in filtered_events if e["event_type"] == event_type]
                    if ticker:
                        filtered_events = [e for e in filtered_events if e["ticker"] == ticker]
                    
                    events = sorted(filtered_events, key=lambda x: x["timestamp"], reverse=True)[:limit]
            
            return {
                "success": True,
                "events": events,
                "total_count": len(events),
                "source": self._get_storage_method()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def store_knowledge_evolution(self, ticker: str, evolution_type: str, previous_insight: str, refined_insight: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store knowledge evolution data"""
        try:
            evolution_data = {
                "ticker": ticker,
                "evolution_type": evolution_type,
                "previous_insight": previous_insight,
                "refined_insight": refined_insight,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            if self.use_external_db:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO knowledge_evolution (ticker, evolution_type, previous_insight, refined_insight, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (ticker, evolution_type, previous_insight, refined_insight, json.dumps(metadata or {})))
                self.db_connection.commit()
                evolution_data["id"] = cursor.lastrowid
            
            # Always store in memory as backup
            with _storage_lock:
                _knowledge_storage.append(evolution_data)
            
            return {
                "success": True,
                "evolution_id": evolution_data.get("id"),
                "stored_in": self._get_storage_method()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_knowledge_evolution(self, ticker: Optional[str] = None, evolution_type: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """Retrieve knowledge evolution data"""
        try:
            evolutions = []
            
            if self.use_external_db:
                cursor = self.db_connection.cursor()
                query = "SELECT ticker, evolution_type, previous_insight, refined_insight, timestamp, metadata FROM knowledge_evolution WHERE 1=1"
                params = []
                
                if ticker:
                    query += " AND ticker = ?"
                    params.append(ticker)
                
                if evolution_type:
                    query += " AND evolution_type = ?"
                    params.append(evolution_type)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                for row in cursor.fetchall():
                    evolutions.append({
                        "ticker": row[0],
                        "evolution_type": row[1],
                        "previous_insight": row[2],
                        "refined_insight": row[3],
                        "timestamp": row[4],
                        "metadata": json.loads(row[5]) if row[5] else {}
                    })
            
            # Fallback to in-memory storage
            if not evolutions:
                with _storage_lock:
                    filtered_evolutions = _knowledge_storage
                    if ticker:
                        filtered_evolutions = [e for e in filtered_evolutions if e["ticker"] == ticker]
                    if evolution_type:
                        filtered_evolutions = [e for e in filtered_evolutions if e["evolution_type"] == evolution_type]
                    
                    evolutions = sorted(filtered_evolutions, key=lambda x: x["timestamp"], reverse=True)[:limit]
            
            return {
                "success": True,
                "evolutions": evolutions,
                "total_count": len(evolutions),
                "source": self._get_storage_method()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Get current storage status and configuration"""
        return {
            "external_db": self.use_external_db,
            "redis": self.use_redis,
            "environment": ENVIRONMENT,
            "primary_storage": self._get_storage_method(),
            "in_memory_counts": {
                "insights": len(_insights_storage),
                "events": len(_events_storage),
                "knowledge_evolutions": len(_knowledge_storage)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_storage_method(self) -> str:
        """Get current storage method"""
        if self.use_external_db:
            return "external_database"
        elif self.use_redis:
            return "redis_cache"
        else:
            return "in_memory"
    
    def clear_storage(self, storage_type: str = "all") -> Dict[str, Any]:
        """Clear storage (for testing/maintenance)"""
        try:
            if storage_type in ["all", "insights"]:
                if self.use_external_db:
                    cursor = self.db_connection.cursor()
                    cursor.execute("DELETE FROM insights")
                    self.db_connection.commit()
                
                with _storage_lock:
                    _insights_storage.clear()
            
            if storage_type in ["all", "events"]:
                if self.use_external_db:
                    cursor = self.db_connection.cursor()
                    cursor.execute("DELETE FROM events")
                    self.db_connection.commit()
                
                with _storage_lock:
                    _events_storage.clear()
            
            if storage_type in ["all", "knowledge"]:
                if self.use_external_db:
                    cursor = self.db_connection.cursor()
                    cursor.execute("DELETE FROM knowledge_evolution")
                    self.db_connection.commit()
                
                with _storage_lock:
                    _knowledge_storage.clear()
            
            return {
                "success": True,
                "message": f"Cleared {storage_type} storage",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global storage manager instance
storage_manager = StorageManager()

def handler(request):
    """Vercel serverless function handler for storage operations"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "status")
            
            if action == "status":
                return json.dumps(storage_manager.get_storage_status())
            
            elif action == "store_insight":
                ticker = body.get("ticker", "")
                insight = body.get("insight", "")
                agent = body.get("agent", "")
                metadata = body.get("metadata", {})
                return json.dumps(storage_manager.store_insight(ticker, insight, agent, metadata))
            
            elif action == "get_insights":
                ticker = body.get("ticker")
                limit = body.get("limit", 10)
                return json.dumps(storage_manager.get_insights(ticker, limit))
            
            elif action == "store_event":
                event_type = body.get("event_type", "")
                ticker = body.get("ticker", "")
                message = body.get("message", "")
                severity = body.get("severity", "INFO")
                metadata = body.get("metadata", {})
                return json.dumps(storage_manager.store_event(event_type, ticker, message, severity, metadata))
            
            elif action == "get_events":
                event_type = body.get("event_type")
                ticker = body.get("ticker")
                limit = body.get("limit", 50)
                return json.dumps(storage_manager.get_events(event_type, ticker, limit))
            
            elif action == "store_knowledge":
                ticker = body.get("ticker", "")
                evolution_type = body.get("evolution_type", "")
                previous_insight = body.get("previous_insight", "")
                refined_insight = body.get("refined_insight", "")
                metadata = body.get("metadata", {})
                return json.dumps(storage_manager.store_knowledge_evolution(ticker, evolution_type, previous_insight, refined_insight, metadata))
            
            elif action == "get_knowledge":
                ticker = body.get("ticker")
                evolution_type = body.get("evolution_type")
                limit = body.get("limit", 20)
                return json.dumps(storage_manager.get_knowledge_evolution(ticker, evolution_type, limit))
            
            elif action == "clear_storage":
                storage_type = body.get("storage_type", "all")
                return json.dumps(storage_manager.clear_storage(storage_type))
            
            else:
                return json.dumps({
                    "error": "Invalid action",
                    "available_actions": [
                        "status", "store_insight", "get_insights", "store_event",
                        "get_events", "store_knowledge", "get_knowledge", "clear_storage"
                    ]
                })
        
        else:
            return json.dumps({
                "service": "StorageManager",
                "description": "Manages data storage with fallback from external DB to in-memory",
                "storage_status": storage_manager.get_storage_status(),
                "endpoints": [
                    "POST - status: Get storage status",
                    "POST - store_insight: Store insight data",
                    "POST - get_insights: Retrieve insights",
                    "POST - store_event: Store event data",
                    "POST - get_events: Retrieve events",
                    "POST - store_knowledge: Store knowledge evolution",
                    "POST - get_knowledge: Retrieve knowledge evolution",
                    "POST - clear_storage: Clear storage (maintenance)"
                ]
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "service": "StorageManager"}) 