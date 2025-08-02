"""
Continuous Portfolio Monitoring Service
Handles real-time analysis scheduling and cost tracking
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class MonitoringFrequency(Enum):
    HOURLY = "hourly"
    DAILY = "daily" 
    WEEKLY = "weekly"

@dataclass
class MonitoringSettings:
    frequency: MonitoringFrequency
    enabled: bool
    cost_per_analysis: float
    estimated_monthly_cost: float

@dataclass
class MonitoringStatus:
    is_monitoring: bool
    active_positions: int
    next_analysis: datetime
    total_analyses_today: int
    current_cost_today: float

@dataclass
class PortfolioPosition:
    ticker: str
    shares: int
    cost_basis: float

class ContinuousMonitoringService:
    """Service to manage continuous portfolio monitoring"""
    
    def __init__(self):
        self.monitoring_sessions: Dict[str, Dict] = {}
        self.analysis_history: Dict[str, List] = {}
        self.cost_tracking: Dict[str, Dict] = {}
        
    def calculate_monitoring_costs(self, frequency: MonitoringFrequency, positions_count: int) -> Dict:
        """Calculate monitoring costs based on frequency and position count"""
        base_cost = 0.25  # Base cost per position per analysis
        
        frequency_config = {
            MonitoringFrequency.HOURLY: {"multiplier": 2.0, "analyses_per_day": 24},
            MonitoringFrequency.DAILY: {"multiplier": 1.0, "analyses_per_day": 1},
            MonitoringFrequency.WEEKLY: {"multiplier": 0.7, "analyses_per_day": 1/7}
        }
        
        config = frequency_config[frequency]
        cost_per_analysis = base_cost * config["multiplier"]
        daily_cost = positions_count * cost_per_analysis * config["analyses_per_day"]
        estimated_monthly_cost = daily_cost * 30
        
        return {
            "cost_per_analysis": cost_per_analysis,
            "estimated_monthly_cost": estimated_monthly_cost,
            "daily_cost": daily_cost
        }
    
    def get_next_analysis_time(self, frequency: MonitoringFrequency) -> datetime:
        """Calculate next analysis time based on frequency"""
        now = datetime.now()
        
        if frequency == MonitoringFrequency.HOURLY:
            return now + timedelta(hours=1)
        elif frequency == MonitoringFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == MonitoringFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        
        return now + timedelta(days=1)  # Default to daily
    
    async def start_monitoring(self, user_id: str, positions: List[PortfolioPosition], 
                             settings: MonitoringSettings) -> MonitoringStatus:
        """Start continuous monitoring for a user's portfolio"""
        
        if not settings.enabled or not positions:
            return MonitoringStatus(
                is_monitoring=False,
                active_positions=0,
                next_analysis=datetime.now(),
                total_analyses_today=0,
                current_cost_today=0.0
            )
        
        # Initialize monitoring session
        session_data = {
            "user_id": user_id,
            "positions": [asdict(pos) for pos in positions],
            "settings": asdict(settings),
            "started_at": datetime.now(),
            "last_analysis": None,
            "analysis_count_today": 0,
            "cost_today": 0.0
        }
        
        self.monitoring_sessions[user_id] = session_data
        
        # Schedule first analysis
        next_analysis = self.get_next_analysis_time(settings.frequency)
        
        # Start background monitoring task
        asyncio.create_task(self._monitoring_loop(user_id))
        
        logger.info(f"Started monitoring for user {user_id} with {len(positions)} positions")
        
        return MonitoringStatus(
            is_monitoring=True,
            active_positions=len(positions),
            next_analysis=next_analysis,
            total_analyses_today=session_data["analysis_count_today"],
            current_cost_today=session_data["cost_today"]
        )
    
    async def stop_monitoring(self, user_id: str) -> bool:
        """Stop continuous monitoring for a user"""
        if user_id in self.monitoring_sessions:
            del self.monitoring_sessions[user_id]
            logger.info(f"Stopped monitoring for user {user_id}")
            return True
        return False
    
    async def get_monitoring_status(self, user_id: str) -> Optional[MonitoringStatus]:
        """Get current monitoring status for a user"""
        if user_id not in self.monitoring_sessions:
            return None
            
        session = self.monitoring_sessions[user_id]
        settings = MonitoringSettings(**session["settings"])
        
        return MonitoringStatus(
            is_monitoring=True,
            active_positions=len(session["positions"]),
            next_analysis=self.get_next_analysis_time(settings.frequency),
            total_analyses_today=session["analysis_count_today"],
            current_cost_today=session["cost_today"]
        )
    
    async def _monitoring_loop(self, user_id: str):
        """Background monitoring loop for continuous analysis"""
        while user_id in self.monitoring_sessions:
            try:
                session = self.monitoring_sessions[user_id]
                settings = MonitoringSettings(**session["settings"])
                
                if not settings.enabled:
                    break
                
                # Wait for next analysis time
                interval_seconds = {
                    MonitoringFrequency.HOURLY: 3600,
                    MonitoringFrequency.DAILY: 86400,
                    MonitoringFrequency.WEEKLY: 604800
                }[settings.frequency]
                
                await asyncio.sleep(interval_seconds)
                
                # Perform analysis
                await self._perform_analysis(user_id)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop for user {user_id}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _perform_analysis(self, user_id: str):
        """Perform analysis for a user's portfolio"""
        if user_id not in self.monitoring_sessions:
            return
            
        session = self.monitoring_sessions[user_id]
        settings = MonitoringSettings(**session["settings"])
        positions = session["positions"]
        
        # Calculate cost
        analysis_cost = settings.cost_per_analysis * len(positions)
        
        # Update session tracking
        session["analysis_count_today"] += 1
        session["cost_today"] += analysis_cost
        session["last_analysis"] = datetime.now()
        
        # Store analysis result (simplified for demo)
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "positions_analyzed": len(positions),
            "cost": analysis_cost,
            "user_id": user_id
        }
        
        if user_id not in self.analysis_history:
            self.analysis_history[user_id] = []
        
        self.analysis_history[user_id].append(analysis_result)
        
        logger.info(f"Performed analysis for user {user_id}: {len(positions)} positions, cost: ${analysis_cost:.2f}")
    
    def get_analysis_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent analysis history for a user"""
        if user_id not in self.analysis_history:
            return []
        
        return self.analysis_history[user_id][-limit:]

# Global monitoring service instance
monitoring_service = ContinuousMonitoringService()
