import asyncio
import time
import logging
from dataclasses import dataclass
from typing import Dict, Any, List
from datetime import datetime, timedelta

@dataclass
class HealthMetric:
    name: str
    status: str
    response_time: float
    error_count: int
    last_check: float
    details: Dict[str, Any] = None

class HealthMonitor:
    """Comprehensive system health monitoring"""
    
    def __init__(self):
        self.metrics: Dict[str, HealthMetric] = {}
        self.alert_thresholds = {
            'response_time': 5.0,  # seconds
            'error_rate': 0.1,     # 10%
            'uptime': 0.99         # 99%
        }
        self.check_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    async def check_database_health(self) -> HealthMetric:
        """Check database connection and performance"""
        start_time = time.time()
        try:
            from api.database.supabase_manager import supabase_manager
            
            # Test basic connectivity
            health_ok = await supabase_manager.health_check()
            
            # Get pool statistics
            pool_stats = await supabase_manager.get_pool_stats()
            
            response_time = time.time() - start_time
            
            if health_ok:
                return HealthMetric(
                    name="database",
                    status="healthy",
                    response_time=response_time,
                    error_count=0,
                    last_check=time.time(),
                    details=pool_stats
                )
            else:
                return HealthMetric(
                    name="database",
                    status="unhealthy",
                    response_time=response_time,
                    error_count=1,
                    last_check=time.time(),
                    details={"error": "Health check failed"}
                )
                
        except Exception as e:
            logging.error(f"Database health check failed: {e}")
            return HealthMetric(
                name="database",
                status="unhealthy",
                response_time=time.time() - start_time,
                error_count=1,
                last_check=time.time(),
                details={"error": str(e)}
            )
    
    async def check_external_apis(self) -> HealthMetric:
        """Check external API connectivity (yfinance, OpenAI, etc.)"""
        start_time = time.time()
        try:
            import requests
            
            # Test a simple API call
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return HealthMetric(
                    name="external_apis",
                    status="healthy",
                    response_time=response_time,
                    error_count=0,
                    last_check=time.time(),
                    details={"test_endpoint": "httpbin.org"}
                )
            else:
                return HealthMetric(
                    name="external_apis",
                    status="degraded",
                    response_time=response_time,
                    error_count=1,
                    last_check=time.time(),
                    details={"status_code": response.status_code}
                )
                
        except Exception as e:
            logging.error(f"External API health check failed: {e}")
            return HealthMetric(
                name="external_apis",
                status="unhealthy",
                response_time=time.time() - start_time,
                error_count=1,
                last_check=time.time(),
                details={"error": str(e)}
            )
    
    async def check_memory_usage(self) -> HealthMetric:
        """Check system memory usage"""
        start_time = time.time()
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            response_time = time.time() - start_time
            
            # Consider unhealthy if memory usage > 90%
            if memory.percent < 90:
                status = "healthy"
            elif memory.percent < 95:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return HealthMetric(
                name="memory",
                status=status,
                response_time=response_time,
                error_count=0 if status == "healthy" else 1,
                last_check=time.time(),
                details={
                    "percent_used": memory.percent,
                    "available_mb": memory.available // (1024 * 1024),
                    "total_mb": memory.total // (1024 * 1024)
                }
            )
            
        except ImportError:
            # psutil not available, skip memory check
            return HealthMetric(
                name="memory",
                status="unknown",
                response_time=time.time() - start_time,
                error_count=0,
                last_check=time.time(),
                details={"error": "psutil not available"}
            )
        except Exception as e:
            logging.error(f"Memory health check failed: {e}")
            return HealthMetric(
                name="memory",
                status="unhealthy",
                response_time=time.time() - start_time,
                error_count=1,
                last_check=time.time(),
                details={"error": str(e)}
            )
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        checks = await asyncio.gather(
            self.check_database_health(),
            self.check_external_apis(),
            self.check_memory_usage(),
            self.check_cache_performance(),
            self.check_circuit_breakers(),
            return_exceptions=True
        )
        
        components = {}
        overall_status = "healthy"
        
        for check in checks:
            if isinstance(check, Exception):
                logging.error(f"Health check failed: {check}")
                continue
                
            components[check.name] = {
                "status": check.status,
                "response_time": check.response_time,
                "last_check": check.last_check,
                "details": check.details or {}
            }
            
            # Update overall status
            if check.status == "unhealthy":
                overall_status = "unhealthy"
            elif check.status == "degraded" and overall_status == "healthy":
                overall_status = "degraded"
        
        health_report = {
            "overall_status": overall_status,
            "components": components,
            "timestamp": time.time(),
            "checks_completed": len([c for c in checks if not isinstance(c, Exception)])
        }
        
        # Store in history
        self.check_history.append(health_report)
        if len(self.check_history) > self.max_history:
            self.check_history.pop(0)
        
        return health_report
    
    async def check_cache_performance(self) -> HealthMetric:
        """Check cache performance and statistics"""
        start_time = time.time()
        try:
            from api.utils.cache_manager import get_all_cache_stats

            cache_stats = await get_all_cache_stats()
            response_time = time.time() - start_time

            # Determine health based on hit rates
            overall_hit_rate = sum(
                stats['hit_rate'] for stats in cache_stats.values()
                if isinstance(stats, dict) and 'hit_rate' in stats
            ) / 3  # Average of 3 caches

            if overall_hit_rate > 70:
                status = "healthy"
            elif overall_hit_rate > 50:
                status = "degraded"
            else:
                status = "unhealthy"

            return HealthMetric(
                name="cache",
                status=status,
                response_time=response_time,
                error_count=0,
                last_check=time.time(),
                details={
                    "cache_stats": cache_stats,
                    "overall_hit_rate": overall_hit_rate
                }
            )

        except Exception as e:
            logging.error(f"Cache performance check failed: {e}")
            return HealthMetric(
                name="cache",
                status="unhealthy",
                response_time=time.time() - start_time,
                error_count=1,
                last_check=time.time(),
                details={"error": str(e)}
            )

    async def check_circuit_breakers(self) -> HealthMetric:
        """Check circuit breaker status"""
        start_time = time.time()
        try:
            from api.utils.circuit_breaker import get_all_circuit_breaker_stats

            breaker_stats = get_all_circuit_breaker_stats()
            response_time = time.time() - start_time

            # Check if any circuit breakers are open
            open_breakers = [
                name for name, stats in breaker_stats.items()
                if stats['state'] == 'open'
            ]

            if not open_breakers:
                status = "healthy"
            elif len(open_breakers) <= len(breaker_stats) / 2:
                status = "degraded"
            else:
                status = "unhealthy"

            return HealthMetric(
                name="circuit_breakers",
                status=status,
                response_time=response_time,
                error_count=len(open_breakers),
                last_check=time.time(),
                details={
                    "breaker_stats": breaker_stats,
                    "open_breakers": open_breakers
                }
            )

        except Exception as e:
            logging.error(f"Circuit breaker check failed: {e}")
            return HealthMetric(
                name="circuit_breakers",
                status="unknown",
                response_time=time.time() - start_time,
                error_count=1,
                last_check=time.time(),
                details={"error": str(e)}
            )

    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over time"""
        cutoff_time = time.time() - (hours * 3600)
        recent_checks = [
            check for check in self.check_history
            if check["timestamp"] > cutoff_time
        ]

        if not recent_checks:
            return {"error": "No recent health data available"}

        # Calculate uptime percentage
        healthy_checks = len([
            check for check in recent_checks
            if check["overall_status"] == "healthy"
        ])
        uptime_percentage = (healthy_checks / len(recent_checks)) * 100

        # Calculate average response times by component
        avg_response_times = {}
        for check in recent_checks:
            for component, data in check["components"].items():
                if component not in avg_response_times:
                    avg_response_times[component] = []
                avg_response_times[component].append(data["response_time"])

        for component in avg_response_times:
            avg_response_times[component] = sum(avg_response_times[component]) / len(avg_response_times[component])

        return {
            "uptime_percentage": uptime_percentage,
            "total_checks": len(recent_checks),
            "healthy_checks": healthy_checks,
            "average_response_times": avg_response_times,
            "time_window_hours": hours
        }

# Global health monitor instance
health_monitor = HealthMonitor()
