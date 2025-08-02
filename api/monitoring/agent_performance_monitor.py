import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import numpy as np
import json

@dataclass
class AgentPerformanceMetric:
    """Individual agent performance metric"""
    agent_name: str
    metric_type: str
    value: float
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent_name': self.agent_name,
            'metric_type': self.metric_type,
            'value': self.value,
            'timestamp': self.timestamp,
            'metadata': self.metadata or {}
        }

@dataclass
class InteractionMetric:
    """Agent interaction performance metric"""
    sender: str
    receiver: str
    interaction_type: str
    duration: float
    success: bool
    timestamp: float
    payload_size: int = 0
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'interaction_type': self.interaction_type,
            'duration': self.duration,
            'success': self.success,
            'timestamp': self.timestamp,
            'payload_size': self.payload_size,
            'retry_count': self.retry_count
        }

@dataclass
class QualityMetric:
    """Output quality metric"""
    agent_name: str
    output_type: str
    quality_score: float
    relevance: float
    accuracy: float
    timeliness: float
    timestamp: float
    ticker: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent_name': self.agent_name,
            'output_type': self.output_type,
            'quality_score': self.quality_score,
            'relevance': self.relevance,
            'accuracy': self.accuracy,
            'timeliness': self.timeliness,
            'timestamp': self.timestamp,
            'ticker': self.ticker
        }

class AgentPerformanceMonitor:
    """
    Comprehensive performance monitoring system for multi-agent interactions
    """
    
    def __init__(self, max_history_size: int = 10000):
        # Performance data storage
        self.agent_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_size))
        self.interaction_metrics: deque = deque(maxlen=max_history_size)
        self.quality_metrics: deque = deque(maxlen=max_history_size)
        
        # Real-time aggregated metrics
        self.current_metrics = {
            'agent_performance': defaultdict(dict),
            'interaction_efficiency': {},
            'quality_scores': defaultdict(dict),
            'system_health': {}
        }
        
        # Performance baselines and thresholds
        self.performance_baselines = {
            'response_time': {'excellent': 1.0, 'good': 3.0, 'poor': 10.0},
            'success_rate': {'excellent': 0.95, 'good': 0.85, 'poor': 0.70},
            'quality_score': {'excellent': 0.9, 'good': 0.75, 'poor': 0.6},
            'throughput': {'excellent': 10.0, 'good': 5.0, 'poor': 2.0}  # requests per minute
        }
        
        # Monitoring configuration
        self.monitoring_enabled = True
        self.alert_thresholds = {
            'response_time_spike': 5.0,  # seconds
            'success_rate_drop': 0.8,   # 80%
            'quality_degradation': 0.7  # 70%
        }
        
        # Background tasks
        self._aggregation_task = None
        self._cleanup_task = None
        self._running = False
    
    async def start_monitoring(self):
        """Start background monitoring tasks"""
        if self._running:
            return
        
        self._running = True
        self._aggregation_task = asyncio.create_task(self._aggregate_metrics_periodically())
        self._cleanup_task = asyncio.create_task(self._cleanup_old_metrics())
        logging.info("Agent performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring and cleanup"""
        self._running = False
        
        if self._aggregation_task:
            self._aggregation_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        logging.info("Agent performance monitoring stopped")
    
    def record_agent_performance(self, agent_name: str, metric_type: str, 
                                value: float, metadata: Dict[str, Any] = None):
        """Record individual agent performance metric"""
        if not self.monitoring_enabled:
            return
        
        metric = AgentPerformanceMetric(
            agent_name=agent_name,
            metric_type=metric_type,
            value=value,
            timestamp=time.time(),
            metadata=metadata
        )
        
        self.agent_metrics[agent_name].append(metric)
        
        # Update real-time metrics
        self._update_agent_metrics(agent_name, metric_type, value)
    
    def record_interaction(self, sender: str, receiver: str, interaction_type: str,
                          duration: float, success: bool, payload_size: int = 0,
                          retry_count: int = 0):
        """Record agent interaction metric"""
        if not self.monitoring_enabled:
            return
        
        metric = InteractionMetric(
            sender=sender,
            receiver=receiver,
            interaction_type=interaction_type,
            duration=duration,
            success=success,
            timestamp=time.time(),
            payload_size=payload_size,
            retry_count=retry_count
        )
        
        self.interaction_metrics.append(metric)
        
        # Update real-time metrics
        self._update_interaction_metrics(metric)
    
    def record_quality_metric(self, agent_name: str, output_type: str,
                             quality_score: float, relevance: float = None,
                             accuracy: float = None, timeliness: float = None,
                             ticker: str = None):
        """Record output quality metric"""
        if not self.monitoring_enabled:
            return
        
        metric = QualityMetric(
            agent_name=agent_name,
            output_type=output_type,
            quality_score=quality_score,
            relevance=relevance or quality_score,
            accuracy=accuracy or quality_score,
            timeliness=timeliness or quality_score,
            timestamp=time.time(),
            ticker=ticker
        )
        
        self.quality_metrics.append(metric)
        
        # Update real-time metrics
        self._update_quality_metrics(agent_name, metric)
    
    def _update_agent_metrics(self, agent_name: str, metric_type: str, value: float):
        """Update real-time agent metrics"""
        if agent_name not in self.current_metrics['agent_performance']:
            self.current_metrics['agent_performance'][agent_name] = {}
        
        agent_metrics = self.current_metrics['agent_performance'][agent_name]
        
        if metric_type not in agent_metrics:
            agent_metrics[metric_type] = {
                'current': value,
                'average': value,
                'count': 1,
                'min': value,
                'max': value
            }
        else:
            metrics = agent_metrics[metric_type]
            metrics['current'] = value
            metrics['count'] += 1
            metrics['average'] = ((metrics['average'] * (metrics['count'] - 1)) + value) / metrics['count']
            metrics['min'] = min(metrics['min'], value)
            metrics['max'] = max(metrics['max'], value)
    
    def _update_interaction_metrics(self, metric: InteractionMetric):
        """Update real-time interaction metrics"""
        interaction_key = f"{metric.sender}->{metric.receiver}"
        
        if interaction_key not in self.current_metrics['interaction_efficiency']:
            self.current_metrics['interaction_efficiency'][interaction_key] = {
                'total_interactions': 0,
                'successful_interactions': 0,
                'average_duration': 0.0,
                'total_payload_size': 0,
                'total_retries': 0
            }
        
        metrics = self.current_metrics['interaction_efficiency'][interaction_key]
        metrics['total_interactions'] += 1
        
        if metric.success:
            metrics['successful_interactions'] += 1
        
        # Update average duration
        total_interactions = metrics['total_interactions']
        current_avg = metrics['average_duration']
        metrics['average_duration'] = ((current_avg * (total_interactions - 1)) + metric.duration) / total_interactions
        
        metrics['total_payload_size'] += metric.payload_size
        metrics['total_retries'] += metric.retry_count
    
    def _update_quality_metrics(self, agent_name: str, metric: QualityMetric):
        """Update real-time quality metrics"""
        if agent_name not in self.current_metrics['quality_scores']:
            self.current_metrics['quality_scores'][agent_name] = {
                'overall_quality': 0.0,
                'relevance': 0.0,
                'accuracy': 0.0,
                'timeliness': 0.0,
                'count': 0
            }
        
        quality_metrics = self.current_metrics['quality_scores'][agent_name]
        count = quality_metrics['count']
        
        # Update running averages
        quality_metrics['overall_quality'] = ((quality_metrics['overall_quality'] * count) + metric.quality_score) / (count + 1)
        quality_metrics['relevance'] = ((quality_metrics['relevance'] * count) + metric.relevance) / (count + 1)
        quality_metrics['accuracy'] = ((quality_metrics['accuracy'] * count) + metric.accuracy) / (count + 1)
        quality_metrics['timeliness'] = ((quality_metrics['timeliness'] * count) + metric.timeliness) / (count + 1)
        quality_metrics['count'] = count + 1
    
    async def get_performance_dashboard(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance dashboard"""
        try:
            cutoff_time = time.time() - (time_window_hours * 3600)
            
            # Agent performance summary
            agent_summary = await self._generate_agent_performance_summary(cutoff_time)
            
            # Interaction efficiency summary
            interaction_summary = await self._generate_interaction_summary(cutoff_time)
            
            # Quality analysis
            quality_summary = await self._generate_quality_summary(cutoff_time)
            
            # System health indicators
            system_health = await self._calculate_system_health()
            
            # Performance trends
            trends = await self._calculate_performance_trends(cutoff_time)
            
            # Alerts and recommendations
            alerts = await self._generate_performance_alerts()
            
            dashboard = {
                'timestamp': datetime.now().isoformat(),
                'time_window_hours': time_window_hours,
                'agent_performance': agent_summary,
                'interaction_efficiency': interaction_summary,
                'quality_analysis': quality_summary,
                'system_health': system_health,
                'performance_trends': trends,
                'alerts': alerts,
                'recommendations': self._generate_recommendations(agent_summary, interaction_summary, quality_summary)
            }
            
            return dashboard
            
        except Exception as e:
            logging.error(f"Performance dashboard generation failed: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    async def _generate_agent_performance_summary(self, cutoff_time: float) -> Dict[str, Any]:
        """Generate agent performance summary"""
        summary = {}
        
        for agent_name, metrics_deque in self.agent_metrics.items():
            recent_metrics = [m for m in metrics_deque if m.timestamp > cutoff_time]
            
            if not recent_metrics:
                continue
            
            # Group by metric type
            metric_groups = defaultdict(list)
            for metric in recent_metrics:
                metric_groups[metric.metric_type].append(metric.value)
            
            agent_summary = {}
            for metric_type, values in metric_groups.items():
                agent_summary[metric_type] = {
                    'average': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'count': len(values),
                    'trend': self._calculate_trend(values)
                }
            
            summary[agent_name] = agent_summary
        
        return summary
    
    async def _generate_interaction_summary(self, cutoff_time: float) -> Dict[str, Any]:
        """Generate interaction efficiency summary"""
        recent_interactions = [m for m in self.interaction_metrics if m.timestamp > cutoff_time]
        
        if not recent_interactions:
            return {'message': 'No recent interactions'}
        
        # Overall statistics
        total_interactions = len(recent_interactions)
        successful_interactions = sum(1 for i in recent_interactions if i.success)
        success_rate = successful_interactions / total_interactions if total_interactions > 0 else 0
        
        # Duration statistics
        durations = [i.duration for i in recent_interactions]
        avg_duration = np.mean(durations)
        
        # Payload statistics
        payload_sizes = [i.payload_size for i in recent_interactions]
        avg_payload_size = np.mean(payload_sizes) if payload_sizes else 0
        
        # Retry statistics
        total_retries = sum(i.retry_count for i in recent_interactions)
        
        # Per-interaction-type breakdown
        type_breakdown = defaultdict(lambda: {'count': 0, 'success_count': 0, 'avg_duration': 0})
        for interaction in recent_interactions:
            breakdown = type_breakdown[interaction.interaction_type]
            breakdown['count'] += 1
            if interaction.success:
                breakdown['success_count'] += 1
            breakdown['avg_duration'] = ((breakdown['avg_duration'] * (breakdown['count'] - 1)) + interaction.duration) / breakdown['count']
        
        # Calculate success rates for each type
        for type_name, breakdown in type_breakdown.items():
            breakdown['success_rate'] = breakdown['success_count'] / breakdown['count'] if breakdown['count'] > 0 else 0
        
        return {
            'total_interactions': total_interactions,
            'success_rate': success_rate,
            'average_duration': avg_duration,
            'average_payload_size': avg_payload_size,
            'total_retries': total_retries,
            'interaction_types': dict(type_breakdown)
        }
    
    async def _generate_quality_summary(self, cutoff_time: float) -> Dict[str, Any]:
        """Generate quality analysis summary"""
        recent_quality = [m for m in self.quality_metrics if m.timestamp > cutoff_time]
        
        if not recent_quality:
            return {'message': 'No recent quality metrics'}
        
        # Overall quality statistics
        quality_scores = [m.quality_score for m in recent_quality]
        avg_quality = np.mean(quality_scores)
        
        # Per-agent quality breakdown
        agent_quality = defaultdict(list)
        for metric in recent_quality:
            agent_quality[metric.agent_name].append(metric.quality_score)
        
        agent_quality_summary = {}
        for agent, scores in agent_quality.items():
            agent_quality_summary[agent] = {
                'average_quality': np.mean(scores),
                'quality_consistency': 1 - np.std(scores),  # Higher consistency = lower std
                'sample_count': len(scores),
                'trend': self._calculate_trend(scores)
            }
        
        # Quality distribution
        excellent_count = sum(1 for score in quality_scores if score >= self.performance_baselines['quality_score']['excellent'])
        good_count = sum(1 for score in quality_scores if score >= self.performance_baselines['quality_score']['good'])
        poor_count = sum(1 for score in quality_scores if score < self.performance_baselines['quality_score']['poor'])
        
        return {
            'overall_average_quality': avg_quality,
            'quality_distribution': {
                'excellent': excellent_count,
                'good': good_count,
                'poor': poor_count,
                'total': len(quality_scores)
            },
            'agent_quality_breakdown': agent_quality_summary
        }
    
    async def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health indicators"""
        try:
            # Get recent metrics (last hour)
            cutoff_time = time.time() - 3600
            
            # Calculate health indicators
            recent_interactions = [m for m in self.interaction_metrics if m.timestamp > cutoff_time]
            recent_quality = [m for m in self.quality_metrics if m.timestamp > cutoff_time]
            
            # Interaction health
            if recent_interactions:
                success_rate = sum(1 for i in recent_interactions if i.success) / len(recent_interactions)
                avg_response_time = np.mean([i.duration for i in recent_interactions])
                
                interaction_health = "healthy"
                if success_rate < self.alert_thresholds['success_rate_drop']:
                    interaction_health = "degraded"
                if avg_response_time > self.alert_thresholds['response_time_spike']:
                    interaction_health = "poor"
            else:
                interaction_health = "unknown"
                success_rate = 0
                avg_response_time = 0
            
            # Quality health
            if recent_quality:
                avg_quality = np.mean([m.quality_score for m in recent_quality])
                quality_health = "healthy"
                if avg_quality < self.alert_thresholds['quality_degradation']:
                    quality_health = "degraded"
            else:
                quality_health = "unknown"
                avg_quality = 0
            
            # Overall system health
            if interaction_health == "healthy" and quality_health == "healthy":
                overall_health = "healthy"
            elif interaction_health == "poor" or quality_health == "degraded":
                overall_health = "degraded"
            else:
                overall_health = "unknown"
            
            return {
                'overall_health': overall_health,
                'interaction_health': interaction_health,
                'quality_health': quality_health,
                'success_rate': success_rate,
                'average_response_time': avg_response_time,
                'average_quality': avg_quality,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"System health calculation failed: {e}")
            return {'overall_health': 'error', 'error': str(e)}
    
    async def _calculate_performance_trends(self, cutoff_time: float) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        try:
            # Split time window into buckets for trend analysis
            time_window = time.time() - cutoff_time
            bucket_size = time_window / 10  # 10 time buckets
            
            trends = {
                'response_time_trend': [],
                'success_rate_trend': [],
                'quality_trend': [],
                'throughput_trend': []
            }
            
            for i in range(10):
                bucket_start = cutoff_time + (i * bucket_size)
                bucket_end = bucket_start + bucket_size
                
                # Get metrics in this time bucket
                bucket_interactions = [
                    m for m in self.interaction_metrics 
                    if bucket_start <= m.timestamp < bucket_end
                ]
                bucket_quality = [
                    m for m in self.quality_metrics 
                    if bucket_start <= m.timestamp < bucket_end
                ]
                
                # Calculate bucket metrics
                if bucket_interactions:
                    avg_response_time = np.mean([i.duration for i in bucket_interactions])
                    success_rate = sum(1 for i in bucket_interactions if i.success) / len(bucket_interactions)
                    throughput = len(bucket_interactions) / (bucket_size / 60)  # per minute
                else:
                    avg_response_time = 0
                    success_rate = 0
                    throughput = 0
                
                if bucket_quality:
                    avg_quality = np.mean([m.quality_score for m in bucket_quality])
                else:
                    avg_quality = 0
                
                trends['response_time_trend'].append(avg_response_time)
                trends['success_rate_trend'].append(success_rate)
                trends['quality_trend'].append(avg_quality)
                trends['throughput_trend'].append(throughput)
            
            # Calculate trend directions
            for trend_name, values in trends.items():
                if len(values) >= 2:
                    trend_direction = "improving" if values[-1] > values[0] else "declining"
                    if trend_name == 'response_time_trend':
                        trend_direction = "improving" if values[-1] < values[0] else "declining"  # Lower is better
                    trends[f"{trend_name}_direction"] = trend_direction
            
            return trends
            
        except Exception as e:
            logging.error(f"Trend calculation failed: {e}")
            return {'error': str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"
    
    async def _generate_performance_alerts(self) -> List[Dict[str, Any]]:
        """Generate performance alerts based on thresholds"""
        alerts = []
        
        try:
            # Check recent metrics for threshold violations
            recent_time = time.time() - 3600  # Last hour
            
            # Response time alerts
            recent_interactions = [m for m in self.interaction_metrics if m.timestamp > recent_time]
            if recent_interactions:
                avg_response_time = np.mean([i.duration for i in recent_interactions])
                if avg_response_time > self.alert_thresholds['response_time_spike']:
                    alerts.append({
                        'type': 'response_time_alert',
                        'severity': 'high',
                        'message': f"Average response time ({avg_response_time:.2f}s) exceeds threshold",
                        'threshold': self.alert_thresholds['response_time_spike'],
                        'current_value': avg_response_time
                    })
            
            # Success rate alerts
            if recent_interactions:
                success_rate = sum(1 for i in recent_interactions if i.success) / len(recent_interactions)
                if success_rate < self.alert_thresholds['success_rate_drop']:
                    alerts.append({
                        'type': 'success_rate_alert',
                        'severity': 'high',
                        'message': f"Success rate ({success_rate:.1%}) below threshold",
                        'threshold': self.alert_thresholds['success_rate_drop'],
                        'current_value': success_rate
                    })
            
            # Quality alerts
            recent_quality = [m for m in self.quality_metrics if m.timestamp > recent_time]
            if recent_quality:
                avg_quality = np.mean([m.quality_score for m in recent_quality])
                if avg_quality < self.alert_thresholds['quality_degradation']:
                    alerts.append({
                        'type': 'quality_alert',
                        'severity': 'medium',
                        'message': f"Average quality ({avg_quality:.2f}) below threshold",
                        'threshold': self.alert_thresholds['quality_degradation'],
                        'current_value': avg_quality
                    })
            
        except Exception as e:
            logging.error(f"Alert generation failed: {e}")
            alerts.append({
                'type': 'system_error',
                'severity': 'high',
                'message': f"Alert generation failed: {str(e)}"
            })
        
        return alerts
    
    def _generate_recommendations(self, agent_summary: Dict[str, Any], 
                                 interaction_summary: Dict[str, Any], 
                                 quality_summary: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        try:
            # Agent performance recommendations
            for agent_name, metrics in agent_summary.items():
                for metric_type, stats in metrics.items():
                    if metric_type == 'response_time' and stats['average'] > 5.0:
                        recommendations.append(f"Optimize {agent_name} response time (current: {stats['average']:.2f}s)")
                    
                    if metric_type == 'error_rate' and stats['average'] > 0.1:
                        recommendations.append(f"Investigate {agent_name} error rate (current: {stats['average']:.1%})")
            
            # Interaction recommendations
            if interaction_summary.get('success_rate', 1.0) < 0.9:
                recommendations.append("Improve inter-agent communication reliability")
            
            if interaction_summary.get('average_duration', 0) > 3.0:
                recommendations.append("Optimize message passing efficiency")
            
            # Quality recommendations
            if quality_summary.get('overall_average_quality', 1.0) < 0.8:
                recommendations.append("Review and enhance output quality standards")
            
            # Default recommendation if no issues found
            if not recommendations:
                recommendations.append("System performance is within acceptable parameters")
        
        except Exception as e:
            logging.error(f"Recommendation generation failed: {e}")
            recommendations.append("Unable to generate recommendations due to analysis error")
        
        return recommendations
    
    async def _aggregate_metrics_periodically(self):
        """Background task to aggregate metrics periodically"""
        while self._running:
            try:
                # Update system health
                self.current_metrics['system_health'] = await self._calculate_system_health()
                
                # Sleep for 60 seconds before next aggregation
                await asyncio.sleep(60)
                
            except Exception as e:
                logging.error(f"Metric aggregation failed: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_metrics(self):
        """Background task to cleanup old metrics"""
        while self._running:
            try:
                cutoff_time = time.time() - (7 * 24 * 3600)  # Keep 7 days of data
                
                # Cleanup would be handled by deque maxlen, but we can do additional cleanup here
                # For now, just log the cleanup
                logging.debug("Metric cleanup completed")
                
                # Sleep for 1 hour before next cleanup
                await asyncio.sleep(3600)
                
            except Exception as e:
                logging.error(f"Metric cleanup failed: {e}")
                await asyncio.sleep(3600)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        return {
            'agent_performance': dict(self.current_metrics['agent_performance']),
            'interaction_efficiency': dict(self.current_metrics['interaction_efficiency']),
            'quality_scores': dict(self.current_metrics['quality_scores']),
            'system_health': self.current_metrics['system_health'],
            'timestamp': datetime.now().isoformat()
        }

# Global performance monitor instance
agent_performance_monitor = AgentPerformanceMonitor()

# Integration utilities for easy monitoring
async def monitor_agent_execution(agent_name: str, operation: str, func, *args, **kwargs):
    """Decorator-like function to monitor agent execution"""
    start_time = time.time()
    success = False
    error = None

    try:
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        success = True
        return result
    except Exception as e:
        error = str(e)
        raise e
    finally:
        execution_time = time.time() - start_time

        # Record performance metrics
        agent_performance_monitor.record_agent_performance(
            agent_name=agent_name,
            metric_type='execution_time',
            value=execution_time,
            metadata={'operation': operation, 'success': success, 'error': error}
        )

        if not success:
            agent_performance_monitor.record_agent_performance(
                agent_name=agent_name,
                metric_type='error_rate',
                value=1.0,
                metadata={'operation': operation, 'error': error}
            )

def monitor_interaction(sender: str, receiver: str, interaction_type: str):
    """Decorator to monitor agent interactions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            payload_size = 0
            retry_count = 0

            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                success = True

                # Estimate payload size
                if isinstance(result, dict):
                    payload_size = len(str(result))

                return result
            except Exception as e:
                raise e
            finally:
                duration = time.time() - start_time

                agent_performance_monitor.record_interaction(
                    sender=sender,
                    receiver=receiver,
                    interaction_type=interaction_type,
                    duration=duration,
                    success=success,
                    payload_size=payload_size,
                    retry_count=retry_count
                )

        return wrapper
    return decorator
