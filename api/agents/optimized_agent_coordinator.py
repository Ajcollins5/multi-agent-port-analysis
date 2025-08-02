import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import json

from .base_agent import BaseAgent
from ..utils.cache_manager import cached, cache_market_data
from ..utils.circuit_breaker import circuit_breaker
from ..database.supabase_manager import supabase_manager

@dataclass
class AgentTask:
    """Represents a task for an agent to execute"""
    agent_name: str
    method_name: str
    args: tuple
    kwargs: dict
    priority: int = 1  # Higher number = higher priority
    timeout: float = 30.0
    retry_count: int = 3
    dependencies: List[str] = None  # List of agent names this task depends on
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class AgentResult:
    """Represents the result of an agent task execution"""
    agent_name: str
    task_id: str
    success: bool
    result: Any
    execution_time: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class OptimizedAgentCoordinator:
    """
    High-performance agent coordinator with parallel execution, caching, and optimization
    """
    
    def __init__(self, max_workers: int = 4):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[AgentTask] = []
        self.results_cache: Dict[str, AgentResult] = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.performance_metrics = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'avg_execution_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
    async def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the coordinator"""
        self.agents[agent.agent_name] = agent
        logging.info(f"Registered agent: {agent.agent_name}")
    
    def _generate_task_id(self, task: AgentTask) -> str:
        """Generate a unique task ID for caching"""
        task_data = {
            'agent': task.agent_name,
            'method': task.method_name,
            'args': task.args,
            'kwargs': task.kwargs
        }
        return f"{task.agent_name}_{task.method_name}_{hash(str(task_data))}"
    
    async def _execute_agent_task(self, task: AgentTask) -> AgentResult:
        """Execute a single agent task with error handling and metrics"""
        task_id = self._generate_task_id(task)
        start_time = time.time()
        
        # Check cache first
        if task_id in self.results_cache:
            cached_result = self.results_cache[task_id]
            # Check if cache is still valid (5 minutes)
            if time.time() - cached_result.metadata.get('timestamp', 0) < 300:
                self.performance_metrics['cache_hits'] += 1
                logging.info(f"Cache hit for task {task_id}")
                return cached_result
        
        self.performance_metrics['cache_misses'] += 1
        
        try:
            # Get the agent
            if task.agent_name not in self.agents:
                raise ValueError(f"Agent {task.agent_name} not registered")
            
            agent = self.agents[task.agent_name]
            
            # Get the method
            if not hasattr(agent, task.method_name):
                raise ValueError(f"Agent {task.agent_name} has no method {task.method_name}")
            
            method = getattr(agent, task.method_name)
            
            # Execute with timeout
            try:
                if asyncio.iscoroutinefunction(method):
                    result = await asyncio.wait_for(
                        method(*task.args, **task.kwargs),
                        timeout=task.timeout
                    )
                else:
                    # Run sync method in executor
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.executor,
                        lambda: method(*task.args, **task.kwargs)
                    )
                
                execution_time = time.time() - start_time
                
                # Create successful result
                agent_result = AgentResult(
                    agent_name=task.agent_name,
                    task_id=task_id,
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    metadata={
                        'timestamp': time.time(),
                        'method': task.method_name,
                        'args_count': len(task.args),
                        'kwargs_count': len(task.kwargs)
                    }
                )
                
                # Cache the result
                self.results_cache[task_id] = agent_result
                
                # Update metrics
                self.performance_metrics['successful_tasks'] += 1
                self._update_avg_execution_time(execution_time)
                
                return agent_result
                
            except asyncio.TimeoutError:
                raise Exception(f"Task timeout after {task.timeout} seconds")
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logging.error(f"Task {task_id} failed: {error_msg}")
            
            # Create error result
            agent_result = AgentResult(
                agent_name=task.agent_name,
                task_id=task_id,
                success=False,
                result=None,
                execution_time=execution_time,
                error=error_msg,
                metadata={
                    'timestamp': time.time(),
                    'method': task.method_name,
                    'retry_count': task.retry_count
                }
            )
            
            # Update metrics
            self.performance_metrics['failed_tasks'] += 1
            self._update_avg_execution_time(execution_time)
            
            return agent_result
        
        finally:
            self.performance_metrics['total_tasks'] += 1
    
    def _update_avg_execution_time(self, execution_time: float) -> None:
        """Update average execution time metric"""
        total_tasks = self.performance_metrics['total_tasks']
        current_avg = self.performance_metrics['avg_execution_time']
        
        # Calculate new average
        new_avg = ((current_avg * (total_tasks - 1)) + execution_time) / total_tasks
        self.performance_metrics['avg_execution_time'] = new_avg
    
    async def execute_parallel_tasks(self, tasks: List[AgentTask]) -> Dict[str, AgentResult]:
        """Execute multiple tasks in parallel with dependency resolution"""
        if not tasks:
            return {}
        
        # Sort tasks by priority and resolve dependencies
        sorted_tasks = self._resolve_task_dependencies(tasks)
        
        # Group tasks by dependency level
        task_groups = self._group_tasks_by_dependencies(sorted_tasks)
        
        results = {}
        
        # Execute task groups sequentially, but tasks within groups in parallel
        for group in task_groups:
            if not group:
                continue
                
            # Execute all tasks in this group in parallel
            group_tasks = [self._execute_agent_task(task) for task in group]
            group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
            
            # Process results
            for task, result in zip(group, group_results):
                task_id = self._generate_task_id(task)
                
                if isinstance(result, Exception):
                    # Handle exception
                    error_result = AgentResult(
                        agent_name=task.agent_name,
                        task_id=task_id,
                        success=False,
                        result=None,
                        execution_time=0.0,
                        error=str(result)
                    )
                    results[task.agent_name] = error_result
                else:
                    results[task.agent_name] = result
        
        return results
    
    def _resolve_task_dependencies(self, tasks: List[AgentTask]) -> List[AgentTask]:
        """Sort tasks based on dependencies and priority"""
        # Simple topological sort for dependencies
        sorted_tasks = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Find tasks with no unresolved dependencies
            ready_tasks = []
            for task in remaining_tasks:
                if not task.dependencies or all(
                    dep in [t.agent_name for t in sorted_tasks] 
                    for dep in task.dependencies
                ):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Circular dependency or missing dependency
                logging.warning("Circular dependency detected, adding remaining tasks")
                ready_tasks = remaining_tasks
            
            # Sort ready tasks by priority
            ready_tasks.sort(key=lambda t: t.priority, reverse=True)
            
            # Add to sorted list and remove from remaining
            sorted_tasks.extend(ready_tasks)
            for task in ready_tasks:
                remaining_tasks.remove(task)
        
        return sorted_tasks
    
    def _group_tasks_by_dependencies(self, tasks: List[AgentTask]) -> List[List[AgentTask]]:
        """Group tasks that can be executed in parallel"""
        groups = []
        current_group = []
        completed_agents = set()
        
        for task in tasks:
            # Check if all dependencies are satisfied
            if all(dep in completed_agents for dep in task.dependencies):
                current_group.append(task)
            else:
                # Start new group
                if current_group:
                    groups.append(current_group)
                    # Mark agents in current group as completed
                    for t in current_group:
                        completed_agents.add(t.agent_name)
                
                current_group = [task]
        
        # Add the last group
        if current_group:
            groups.append(current_group)
        
        return groups
    
    async def execute_portfolio_analysis(self, ticker: str, portfolio: List[str] = None) -> Dict[str, Any]:
        """Execute optimized portfolio analysis with parallel agent execution"""
        start_time = time.time()
        
        # Create optimized task list
        tasks = []
        
        # Risk analysis task (no dependencies)
        tasks.append(AgentTask(
            agent_name="RiskAgent",
            method_name="analyze_stock_risk",
            args=(ticker,),
            kwargs={},
            priority=3,
            timeout=15.0
        ))
        
        # Portfolio risk analysis if portfolio provided
        if portfolio:
            tasks.append(AgentTask(
                agent_name="RiskAgent",
                method_name="analyze_portfolio_risk",
                args=(portfolio,),
                kwargs={},
                priority=2,
                timeout=30.0
            ))
        
        # Knowledge curation (can run in parallel)
        tasks.append(AgentTask(
            agent_name="KnowledgeCurator",
            method_name="curate_knowledge_quality",
            args=(),
            kwargs={},
            priority=1,
            timeout=10.0
        ))
        
        # Execute all tasks
        results = await self.execute_parallel_tasks(tasks)
        
        # Calculate total execution time
        total_time = time.time() - start_time
        
        # Compile final results
        analysis_result = {
            "ticker": ticker,
            "portfolio": portfolio,
            "execution_time": total_time,
            "agent_results": {},
            "performance_metrics": self.get_performance_metrics(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Process agent results
        for agent_name, result in results.items():
            analysis_result["agent_results"][agent_name] = {
                "success": result.success,
                "data": result.result,
                "execution_time": result.execution_time,
                "error": result.error
            }
        
        return analysis_result
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        metrics = self.performance_metrics.copy()
        
        # Calculate additional metrics
        total_tasks = metrics['total_tasks']
        if total_tasks > 0:
            metrics['success_rate'] = (metrics['successful_tasks'] / total_tasks) * 100
            metrics['failure_rate'] = (metrics['failed_tasks'] / total_tasks) * 100
            metrics['cache_hit_rate'] = (metrics['cache_hits'] / (metrics['cache_hits'] + metrics['cache_misses'])) * 100
        else:
            metrics['success_rate'] = 0
            metrics['failure_rate'] = 0
            metrics['cache_hit_rate'] = 0
        
        return metrics
    
    def clear_cache(self) -> None:
        """Clear the results cache"""
        self.results_cache.clear()
        logging.info("Agent coordinator cache cleared")
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
        self.clear_cache()

# Global coordinator instance
agent_coordinator = OptimizedAgentCoordinator()
