import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from .communication_protocol import (
    message_bus, AgentCommunicationInterface, MessageType, MessagePriority,
    coordinate_parallel_analysis, share_analysis_result
)
from .optimized_agent_coordinator import OptimizedAgentCoordinator, AgentTask
from ..utils.cache_manager import cached, cache_long_term
from ..utils.circuit_breaker import circuit_breaker

class OptimizedSupervisor:
    """
    High-performance supervisor with parallel agent execution and intelligent workflow optimization
    """
    
    def __init__(self):
        self.agent_coordinator = OptimizedAgentCoordinator(max_workers=6)
        self.communication = AgentCommunicationInterface("OptimizedSupervisor", message_bus)
        self.execution_history: List[Dict[str, Any]] = []
        self.performance_baselines: Dict[str, float] = {}
        
        # Workflow optimization settings
        self.parallel_execution_enabled = True
        self.adaptive_timeout_enabled = True
        self.result_caching_enabled = True
        
        # Register message handlers
        self._register_message_handlers()
    
    def _register_message_handlers(self):
        """Register handlers for different message types"""
        self.communication.register_handler(
            MessageType.ANALYSIS_RESULT, 
            self._handle_analysis_result
        )
        self.communication.register_handler(
            MessageType.ERROR_NOTIFICATION, 
            self._handle_error_notification
        )
    
    async def _handle_analysis_result(self, message) -> Dict[str, Any]:
        """Handle analysis results from agents"""
        logging.info(f"Received analysis result from {message.sender}")
        return {"status": "acknowledged", "timestamp": time.time()}
    
    async def _handle_error_notification(self, message) -> Dict[str, Any]:
        """Handle error notifications from agents"""
        logging.error(f"Error from {message.sender}: {message.payload}")
        return {"status": "error_logged", "timestamp": time.time()}
    
    @cache_long_term(ttl=1800)  # Cache for 30 minutes
    async def orchestrate_parallel_analysis(self, ticker: str, analysis_type: str = "comprehensive",
                                           portfolio: List[str] = None) -> Dict[str, Any]:
        """
        Orchestrate comprehensive analysis with parallel agent execution
        """
        start_time = time.time()
        analysis_id = f"analysis_{ticker}_{int(start_time)}"
        
        try:
            # Create execution plan
            execution_plan = await self._create_execution_plan(ticker, analysis_type, portfolio)
            
            # Execute agents in parallel based on dependencies
            agent_results = await self._execute_parallel_workflow(execution_plan)
            
            # Synthesize results
            synthesis = await self._synthesize_results(agent_results, ticker, analysis_type)
            
            # Handle notifications if needed
            notifications = await self._handle_notifications(synthesis, ticker)
            
            # Calculate performance metrics
            execution_time = time.time() - start_time
            performance_metrics = await self._calculate_performance_metrics(
                execution_plan, agent_results, execution_time
            )
            
            # Compile final results
            final_results = {
                "analysis_id": analysis_id,
                "ticker": ticker,
                "analysis_type": analysis_type,
                "portfolio": portfolio,
                "execution_time": execution_time,
                "agent_results": agent_results,
                "synthesis": synthesis,
                "notifications": notifications,
                "performance_metrics": performance_metrics,
                "execution_plan": execution_plan,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            # Store execution history for learning
            self.execution_history.append({
                "analysis_id": analysis_id,
                "execution_time": execution_time,
                "success": True,
                "agent_count": len(execution_plan.get("tasks", [])),
                "parallel_efficiency": performance_metrics.get("parallel_efficiency", 0)
            })
            
            # Share results with interested agents
            await share_analysis_result("OptimizedSupervisor", final_results)
            
            return final_results
            
        except Exception as e:
            error_msg = f"Orchestration failed for {ticker}: {str(e)}"
            logging.error(error_msg)
            
            return {
                "analysis_id": analysis_id,
                "ticker": ticker,
                "success": False,
                "error": error_msg,
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _create_execution_plan(self, ticker: str, analysis_type: str, 
                                   portfolio: List[str] = None) -> Dict[str, Any]:
        """Create optimized execution plan for agents"""
        plan = {
            "analysis_id": f"plan_{ticker}_{int(time.time())}",
            "tasks": [],
            "dependencies": {},
            "estimated_duration": 0.0,
            "parallel_groups": []
        }
        
        # Define base tasks that can run in parallel
        base_tasks = []
        
        # Risk analysis task (independent)
        if analysis_type in ["comprehensive", "risk"]:
            base_tasks.append(AgentTask(
                agent_name="EnhancedRiskAgent",
                method_name="analyze_stock_risk_enhanced",
                args=(ticker,),
                kwargs={},
                priority=3,
                timeout=self._get_adaptive_timeout("risk_analysis", 20.0),
                dependencies=[]
            ))
        
        # Portfolio risk analysis (depends on individual stock analysis)
        if portfolio and analysis_type in ["comprehensive", "portfolio"]:
            base_tasks.append(AgentTask(
                agent_name="EnhancedRiskAgent",
                method_name="analyze_portfolio_risk",
                args=(portfolio,),
                kwargs={},
                priority=2,
                timeout=self._get_adaptive_timeout("portfolio_analysis", 45.0),
                dependencies=["EnhancedRiskAgent"] if len(base_tasks) > 0 else []
            ))
        
        # Knowledge curation (independent)
        if analysis_type in ["comprehensive", "knowledge"]:
            base_tasks.append(AgentTask(
                agent_name="KnowledgeCurator",
                method_name="curate_knowledge_quality",
                args=(),
                kwargs={},
                priority=1,
                timeout=self._get_adaptive_timeout("knowledge_curation", 15.0),
                dependencies=[]
            ))
        
        plan["tasks"] = base_tasks
        
        # Group tasks by dependencies for parallel execution
        plan["parallel_groups"] = self._group_tasks_for_parallel_execution(base_tasks)
        
        # Estimate total duration
        plan["estimated_duration"] = self._estimate_execution_duration(plan["parallel_groups"])
        
        return plan
    
    def _get_adaptive_timeout(self, operation_type: str, default_timeout: float) -> float:
        """Get adaptive timeout based on historical performance"""
        if not self.adaptive_timeout_enabled:
            return default_timeout
        
        # Use historical data to adjust timeouts
        baseline = self.performance_baselines.get(operation_type, default_timeout)
        
        # Add 50% buffer to baseline
        adaptive_timeout = baseline * 1.5
        
        # Ensure minimum and maximum bounds
        return max(10.0, min(120.0, adaptive_timeout))
    
    def _group_tasks_for_parallel_execution(self, tasks: List[AgentTask]) -> List[List[AgentTask]]:
        """Group tasks that can be executed in parallel"""
        groups = []
        remaining_tasks = tasks.copy()
        completed_agents = set()
        
        while remaining_tasks:
            current_group = []
            
            # Find tasks with satisfied dependencies
            for task in remaining_tasks[:]:
                if all(dep in completed_agents for dep in task.dependencies):
                    current_group.append(task)
                    remaining_tasks.remove(task)
            
            if not current_group:
                # Handle circular dependencies by taking the first task
                current_group.append(remaining_tasks.pop(0))
            
            groups.append(current_group)
            
            # Mark agents in current group as completed for dependency resolution
            for task in current_group:
                completed_agents.add(task.agent_name)
        
        return groups
    
    def _estimate_execution_duration(self, parallel_groups: List[List[AgentTask]]) -> float:
        """Estimate total execution duration for parallel groups"""
        total_duration = 0.0
        
        for group in parallel_groups:
            # For parallel execution, duration is the maximum timeout in the group
            group_duration = max(task.timeout for task in group) if group else 0.0
            total_duration += group_duration
        
        return total_duration
    
    async def _execute_parallel_workflow(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with parallel agent execution"""
        parallel_groups = execution_plan["parallel_groups"]
        all_results = {}
        
        for group_index, task_group in enumerate(parallel_groups):
            if not task_group:
                continue
            
            logging.info(f"Executing parallel group {group_index + 1}/{len(parallel_groups)} with {len(task_group)} tasks")
            
            # Execute all tasks in this group in parallel
            group_start_time = time.time()
            
            try:
                # Use the agent coordinator for parallel execution
                group_results = await self.agent_coordinator.execute_parallel_tasks(task_group)
                
                # Process results
                for agent_name, result in group_results.items():
                    if result.success:
                        all_results[agent_name] = result.result
                        
                        # Update performance baselines
                        operation_type = f"{agent_name}_{result.metadata.get('method', 'unknown')}"
                        self.performance_baselines[operation_type] = result.execution_time
                    else:
                        logging.error(f"Task failed for {agent_name}: {result.error}")
                        all_results[agent_name] = {"success": False, "error": result.error}
                
                group_duration = time.time() - group_start_time
                logging.info(f"Group {group_index + 1} completed in {group_duration:.2f}s")
                
            except Exception as e:
                logging.error(f"Parallel group {group_index + 1} execution failed: {e}")
                
                # Add error results for failed group
                for task in task_group:
                    all_results[task.agent_name] = {
                        "success": False, 
                        "error": f"Group execution failed: {str(e)}"
                    }
        
        return all_results
    
    @circuit_breaker(failure_threshold=3, timeout=60, name="grok_synthesis")
    async def _synthesize_results(self, agent_results: Dict[str, Any], ticker: str, 
                                 analysis_type: str) -> Dict[str, Any]:
        """Synthesize agent results with circuit breaker protection"""
        try:
            # Extract successful results
            successful_results = {
                agent: result for agent, result in agent_results.items()
                if isinstance(result, dict) and result.get("success", True)
            }
            
            if not successful_results:
                return {
                    "overall_risk": "UNKNOWN",
                    "confidence": 0.3,
                    "synthesis_summary": "No successful agent results to synthesize",
                    "requires_action": False,
                    "fallback_used": True
                }
            
            # Simple rule-based synthesis (can be enhanced with Grok 4 later)
            risk_levels = []
            confidence_scores = []
            key_insights = []
            
            for agent, result in successful_results.items():
                if "risk_level" in result:
                    risk_levels.append(result["risk_level"])
                if "confidence" in result:
                    confidence_scores.append(result["confidence"])
                if "insight" in result:
                    key_insights.append(f"{agent}: {result['insight']}")
            
            # Determine overall risk
            if "HIGH" in risk_levels:
                overall_risk = "HIGH"
            elif "MEDIUM" in risk_levels:
                overall_risk = "MEDIUM"
            else:
                overall_risk = "LOW"
            
            # Calculate average confidence
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            
            synthesis = {
                "overall_risk": overall_risk,
                "confidence": avg_confidence,
                "key_insights": key_insights,
                "recommendations": self._generate_recommendations(overall_risk, successful_results),
                "requires_action": overall_risk == "HIGH",
                "synthesis_summary": f"Multi-agent analysis for {ticker}: {overall_risk} risk level",
                "agent_count": len(successful_results),
                "synthesis_method": "rule_based"
            }
            
            return synthesis
            
        except Exception as e:
            logging.error(f"Synthesis failed: {e}")
            return {
                "overall_risk": "MEDIUM",
                "confidence": 0.4,
                "synthesis_summary": f"Synthesis failed: {str(e)}",
                "requires_action": False,
                "error": True
            }
    
    def _generate_recommendations(self, risk_level: str, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on risk level and agent results"""
        recommendations = []
        
        if risk_level == "HIGH":
            recommendations.extend([
                "Consider reducing position size",
                "Implement stop-loss orders",
                "Monitor closely for exit opportunities",
                "Review portfolio diversification"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "Maintain current position with caution",
                "Set alerts for volatility changes",
                "Consider partial profit-taking if in profit"
            ])
        else:
            recommendations.extend([
                "Position appears suitable for current risk tolerance",
                "Consider increasing position if strategy allows"
            ])
        
        # Add specific recommendations based on agent results
        for agent, result in results.items():
            if isinstance(result, dict) and "recommendations" in result:
                agent_recs = result["recommendations"]
                if isinstance(agent_recs, list):
                    recommendations.extend([f"{agent}: {rec}" for rec in agent_recs[:2]])
        
        return recommendations[:6]  # Limit to 6 recommendations
    
    async def _handle_notifications(self, synthesis: Dict[str, Any], ticker: str) -> List[Dict[str, Any]]:
        """Handle notifications based on synthesis results"""
        notifications = []
        
        try:
            if synthesis.get("requires_action") and synthesis.get("overall_risk") == "HIGH":
                # Send high-priority notification
                notification_payload = {
                    "type": "high_risk_alert",
                    "ticker": ticker,
                    "risk_level": synthesis.get("overall_risk"),
                    "confidence": synthesis.get("confidence"),
                    "summary": synthesis.get("synthesis_summary"),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Broadcast notification to all agents
                sent_count = await self.communication.broadcast(
                    MessageType.PRIORITY_ALERT, 
                    notification_payload, 
                    MessagePriority.CRITICAL
                )
                
                notifications.append({
                    "type": "broadcast_alert",
                    "recipients": sent_count,
                    "status": "sent",
                    "payload": notification_payload
                })
            
        except Exception as e:
            logging.error(f"Notification handling failed: {e}")
            notifications.append({
                "type": "error",
                "message": f"Notification failed: {str(e)}"
            })
        
        return notifications
    
    async def _calculate_performance_metrics(self, execution_plan: Dict[str, Any], 
                                           agent_results: Dict[str, Any], 
                                           total_execution_time: float) -> Dict[str, Any]:
        """Calculate performance metrics for the execution"""
        try:
            # Basic metrics
            total_tasks = len(execution_plan.get("tasks", []))
            successful_tasks = len([r for r in agent_results.values() if isinstance(r, dict) and r.get("success", True)])
            
            # Parallel efficiency calculation
            estimated_sequential_time = sum(task.timeout for task in execution_plan.get("tasks", []))
            parallel_efficiency = (estimated_sequential_time / total_execution_time) if total_execution_time > 0 else 1.0
            
            # Agent coordinator metrics
            coordinator_metrics = self.agent_coordinator.get_performance_metrics()
            
            return {
                "total_execution_time": total_execution_time,
                "estimated_sequential_time": estimated_sequential_time,
                "parallel_efficiency": min(parallel_efficiency, total_tasks),  # Cap at number of tasks
                "success_rate": (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0,
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "coordinator_metrics": coordinator_metrics,
                "parallel_groups": len(execution_plan.get("parallel_groups", [])),
                "avg_group_size": total_tasks / len(execution_plan.get("parallel_groups", [1]))
            }
            
        except Exception as e:
            logging.error(f"Performance metrics calculation failed: {e}")
            return {
                "total_execution_time": total_execution_time,
                "error": str(e)
            }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history for analysis"""
        return self.execution_history.copy()
    
    def get_performance_baselines(self) -> Dict[str, float]:
        """Get current performance baselines"""
        return self.performance_baselines.copy()
    
    async def cleanup(self):
        """Cleanup resources"""
        self.agent_coordinator.cleanup()
        await message_bus.stop()

# Global optimized supervisor instance
optimized_supervisor = OptimizedSupervisor()
