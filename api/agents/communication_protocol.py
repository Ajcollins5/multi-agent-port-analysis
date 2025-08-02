import asyncio
import json
import time
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid
from collections import defaultdict, deque

class MessageType(Enum):
    """Types of messages that can be passed between agents"""
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    ANALYSIS_RESULT = "analysis_result"
    COORDINATION_SIGNAL = "coordination_signal"
    ERROR_NOTIFICATION = "error_notification"
    PERFORMANCE_METRIC = "performance_metric"
    CACHE_INVALIDATION = "cache_invalidation"
    PRIORITY_ALERT = "priority_alert"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AgentMessage:
    """Standardized message format for inter-agent communication"""
    id: str
    sender: str
    recipient: str
    message_type: MessageType
    priority: MessagePriority
    payload: Dict[str, Any]
    timestamp: float
    expires_at: Optional[float] = None
    correlation_id: Optional[str] = None  # For request-response tracking
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.expires_at is None:
            # Default expiration: 5 minutes for most messages, 30 seconds for critical
            ttl = 30 if self.priority == MessagePriority.CRITICAL else 300
            self.expires_at = self.timestamp + ttl
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        return time.time() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type.value,
            'priority': self.priority.value,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'expires_at': self.expires_at,
            'correlation_id': self.correlation_id,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary"""
        return cls(
            id=data['id'],
            sender=data['sender'],
            recipient=data['recipient'],
            message_type=MessageType(data['message_type']),
            priority=MessagePriority(data['priority']),
            payload=data['payload'],
            timestamp=data['timestamp'],
            expires_at=data.get('expires_at'),
            correlation_id=data.get('correlation_id'),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3)
        )

class MessageBus:
    """
    High-performance message bus for inter-agent communication
    
    Features:
    - Priority-based message queuing
    - Message deduplication
    - Automatic retry with exponential backoff
    - Message expiration and cleanup
    - Performance monitoring
    - Broadcast and multicast support
    """
    
    def __init__(self, max_queue_size: int = 1000):
        self.agents: Dict[str, 'AgentCommunicationInterface'] = {}
        self.message_queues: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_queue_size))
        self.message_handlers: Dict[str, Dict[MessageType, Callable]] = defaultdict(dict)
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.message_history: deque = deque(maxlen=10000)  # Keep last 10k messages for debugging
        
        # Performance metrics
        self.metrics = {
            'messages_sent': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'messages_expired': 0,
            'avg_delivery_time': 0.0,
            'queue_sizes': defaultdict(int)
        }
        
        # Background tasks
        self._cleanup_task = None
        self._delivery_task = None
        self._running = False
    
    async def start(self):
        """Start the message bus background tasks"""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_messages())
        self._delivery_task = asyncio.create_task(self._process_message_queues())
        logging.info("Message bus started")
    
    async def stop(self):
        """Stop the message bus and cleanup"""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._delivery_task:
            self._delivery_task.cancel()
        
        # Cancel pending responses
        for future in self.pending_responses.values():
            if not future.done():
                future.cancel()
        
        logging.info("Message bus stopped")
    
    def register_agent(self, agent_name: str, communication_interface: 'AgentCommunicationInterface'):
        """Register an agent with the message bus"""
        self.agents[agent_name] = communication_interface
        logging.info(f"Agent {agent_name} registered with message bus")
    
    def register_handler(self, agent_name: str, message_type: MessageType, handler: Callable):
        """Register a message handler for an agent"""
        self.message_handlers[agent_name][message_type] = handler
        logging.debug(f"Handler registered for {agent_name}: {message_type}")
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message to an agent"""
        try:
            if message.recipient not in self.agents:
                logging.warning(f"Recipient {message.recipient} not registered")
                return False
            
            # Check for message deduplication
            if self._is_duplicate_message(message):
                logging.debug(f"Duplicate message detected: {message.id}")
                return True
            
            # Add to queue based on priority
            queue = self.message_queues[message.recipient]
            
            # Insert based on priority (higher priority first)
            inserted = False
            for i, existing_msg in enumerate(queue):
                if message.priority.value > existing_msg.priority.value:
                    queue.insert(i, message)
                    inserted = True
                    break
            
            if not inserted:
                queue.append(message)
            
            # Update metrics
            self.metrics['messages_sent'] += 1
            self.metrics['queue_sizes'][message.recipient] = len(queue)
            
            # Add to history
            self.message_history.append(message)
            
            logging.debug(f"Message queued: {message.id} -> {message.recipient}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send message {message.id}: {e}")
            self.metrics['messages_failed'] += 1
            return False
    
    async def send_request(self, sender: str, recipient: str, message_type: MessageType, 
                          payload: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Send a request message and wait for response"""
        correlation_id = str(uuid.uuid4())
        
        # Create request message
        request = AgentMessage(
            id=str(uuid.uuid4()),
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            priority=MessagePriority.MEDIUM,
            payload=payload,
            timestamp=time.time(),
            correlation_id=correlation_id
        )
        
        # Create future for response
        response_future = asyncio.Future()
        self.pending_responses[correlation_id] = response_future
        
        try:
            # Send request
            if await self.send_message(request):
                # Wait for response with timeout
                response = await asyncio.wait_for(response_future, timeout=timeout)
                return response
            else:
                return None
                
        except asyncio.TimeoutError:
            logging.warning(f"Request {correlation_id} timed out")
            return None
        except Exception as e:
            logging.error(f"Request {correlation_id} failed: {e}")
            return None
        finally:
            # Cleanup
            self.pending_responses.pop(correlation_id, None)
    
    async def broadcast_message(self, sender: str, message_type: MessageType, 
                               payload: Dict[str, Any], priority: MessagePriority = MessagePriority.MEDIUM) -> int:
        """Broadcast a message to all registered agents"""
        sent_count = 0
        
        for agent_name in self.agents.keys():
            if agent_name != sender:  # Don't send to self
                message = AgentMessage(
                    id=str(uuid.uuid4()),
                    sender=sender,
                    recipient=agent_name,
                    message_type=message_type,
                    priority=priority,
                    payload=payload,
                    timestamp=time.time()
                )
                
                if await self.send_message(message):
                    sent_count += 1
        
        logging.info(f"Broadcast message sent to {sent_count} agents")
        return sent_count
    
    def _is_duplicate_message(self, message: AgentMessage) -> bool:
        """Check if message is a duplicate based on recent history"""
        # Simple deduplication based on sender, recipient, type, and payload hash
        message_signature = f"{message.sender}:{message.recipient}:{message.message_type.value}:{hash(str(message.payload))}"
        
        # Check last 100 messages for duplicates within 60 seconds
        current_time = time.time()
        for hist_msg in list(self.message_history)[-100:]:
            if current_time - hist_msg.timestamp > 60:
                continue
            
            hist_signature = f"{hist_msg.sender}:{hist_msg.recipient}:{hist_msg.message_type.value}:{hash(str(hist_msg.payload))}"
            if message_signature == hist_signature:
                return True
        
        return False
    
    async def _process_message_queues(self):
        """Background task to process message queues"""
        while self._running:
            try:
                for agent_name, queue in self.message_queues.items():
                    if not queue:
                        continue
                    
                    # Process messages in priority order
                    message = queue.popleft()
                    
                    if message.is_expired():
                        self.metrics['messages_expired'] += 1
                        logging.debug(f"Message {message.id} expired")
                        continue
                    
                    # Deliver message
                    delivery_start = time.time()
                    success = await self._deliver_message(message)
                    delivery_time = time.time() - delivery_start
                    
                    if success:
                        self.metrics['messages_delivered'] += 1
                        self._update_avg_delivery_time(delivery_time)
                    else:
                        # Retry logic
                        if message.retry_count < message.max_retries:
                            message.retry_count += 1
                            # Exponential backoff
                            await asyncio.sleep(2 ** message.retry_count)
                            queue.append(message)
                        else:
                            self.metrics['messages_failed'] += 1
                            logging.warning(f"Message {message.id} failed after {message.max_retries} retries")
                    
                    # Update queue size metric
                    self.metrics['queue_sizes'][agent_name] = len(queue)
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logging.error(f"Error in message queue processing: {e}")
                await asyncio.sleep(1)
    
    async def _deliver_message(self, message: AgentMessage) -> bool:
        """Deliver a message to its recipient"""
        try:
            agent = self.agents.get(message.recipient)
            if not agent:
                logging.warning(f"Agent {message.recipient} not found")
                return False
            
            # Check if there's a specific handler for this message type
            handler = self.message_handlers[message.recipient].get(message.message_type)
            
            if handler:
                # Use specific handler
                result = await handler(message)
                
                # If this is a response to a request, resolve the future
                if message.correlation_id and message.correlation_id in self.pending_responses:
                    future = self.pending_responses[message.correlation_id]
                    if not future.done():
                        future.set_result(result)
                
                return True
            else:
                # Use generic message handler
                return await agent.handle_message(message)
                
        except Exception as e:
            logging.error(f"Failed to deliver message {message.id}: {e}")
            return False
    
    def _update_avg_delivery_time(self, delivery_time: float):
        """Update average delivery time metric"""
        current_avg = self.metrics['avg_delivery_time']
        delivered_count = self.metrics['messages_delivered']
        
        # Calculate new average
        new_avg = ((current_avg * (delivered_count - 1)) + delivery_time) / delivered_count
        self.metrics['avg_delivery_time'] = new_avg
    
    async def _cleanup_expired_messages(self):
        """Background task to cleanup expired messages"""
        while self._running:
            try:
                current_time = time.time()
                
                # Cleanup message queues
                for agent_name, queue in self.message_queues.items():
                    expired_count = 0
                    # Create new deque with non-expired messages
                    new_queue = deque(maxlen=queue.maxlen)
                    
                    while queue:
                        message = queue.popleft()
                        if not message.is_expired():
                            new_queue.append(message)
                        else:
                            expired_count += 1
                    
                    self.message_queues[agent_name] = new_queue
                    
                    if expired_count > 0:
                        self.metrics['messages_expired'] += expired_count
                        logging.debug(f"Cleaned up {expired_count} expired messages for {agent_name}")
                
                # Cleanup pending responses
                expired_responses = []
                for correlation_id, future in self.pending_responses.items():
                    if future.done() or current_time - future._creation_time > 300:  # 5 minutes
                        expired_responses.append(correlation_id)
                
                for correlation_id in expired_responses:
                    future = self.pending_responses.pop(correlation_id, None)
                    if future and not future.done():
                        future.cancel()
                
                # Sleep for 30 seconds before next cleanup
                await asyncio.sleep(30)
                
            except Exception as e:
                logging.error(f"Error in message cleanup: {e}")
                await asyncio.sleep(60)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get message bus performance metrics"""
        return {
            **self.metrics,
            'registered_agents': len(self.agents),
            'total_queue_size': sum(len(q) for q in self.message_queues.values()),
            'pending_responses': len(self.pending_responses),
            'message_history_size': len(self.message_history)
        }

class AgentCommunicationInterface:
    """
    Communication interface for agents to interact with the message bus
    """
    
    def __init__(self, agent_name: str, message_bus: MessageBus):
        self.agent_name = agent_name
        self.message_bus = message_bus
        self.message_bus.register_agent(agent_name, self)
    
    async def send_message(self, recipient: str, message_type: MessageType, 
                          payload: Dict[str, Any], priority: MessagePriority = MessagePriority.MEDIUM) -> bool:
        """Send a message to another agent"""
        message = AgentMessage(
            id=str(uuid.uuid4()),
            sender=self.agent_name,
            recipient=recipient,
            message_type=message_type,
            priority=priority,
            payload=payload,
            timestamp=time.time()
        )
        
        return await self.message_bus.send_message(message)
    
    async def send_request(self, recipient: str, message_type: MessageType, 
                          payload: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Send a request and wait for response"""
        return await self.message_bus.send_request(
            self.agent_name, recipient, message_type, payload, timeout
        )
    
    async def broadcast(self, message_type: MessageType, payload: Dict[str, Any], 
                       priority: MessagePriority = MessagePriority.MEDIUM) -> int:
        """Broadcast a message to all agents"""
        return await self.message_bus.broadcast_message(
            self.agent_name, message_type, payload, priority
        )
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_bus.register_handler(self.agent_name, message_type, handler)
    
    async def handle_message(self, message: AgentMessage) -> Any:
        """Default message handler - should be overridden by specific agents"""
        logging.info(f"Agent {self.agent_name} received message: {message.message_type}")
        return {"status": "received", "message_id": message.id}

# Global message bus instance
message_bus = MessageBus()

class DataSharingOptimizer:
    """
    Optimizes data sharing between agents to reduce redundant computations
    """

    def __init__(self):
        self.shared_data_cache: Dict[str, Dict[str, Any]] = {}
        self.data_dependencies: Dict[str, List[str]] = {}
        self.computation_costs: Dict[str, float] = {}
        self.access_patterns: Dict[str, List[float]] = defaultdict(list)

    def register_data_dependency(self, consumer: str, provider: str, data_type: str):
        """Register that one agent depends on data from another"""
        key = f"{consumer}:{data_type}"
        if key not in self.data_dependencies:
            self.data_dependencies[key] = []
        if provider not in self.data_dependencies[key]:
            self.data_dependencies[key].append(provider)

    def cache_shared_data(self, data_key: str, data: Dict[str, Any], ttl: float = 300):
        """Cache data that can be shared between agents"""
        self.shared_data_cache[data_key] = {
            "data": data,
            "timestamp": time.time(),
            "ttl": ttl,
            "access_count": 0
        }

    def get_shared_data(self, data_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve shared data if available and not expired"""
        if data_key not in self.shared_data_cache:
            return None

        cached_item = self.shared_data_cache[data_key]
        if time.time() - cached_item["timestamp"] > cached_item["ttl"]:
            del self.shared_data_cache[data_key]
            return None

        cached_item["access_count"] += 1
        self.access_patterns[data_key].append(time.time())
        return cached_item["data"]

    def optimize_data_flow(self, analysis_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize the data flow for a multi-agent analysis"""
        optimized_plan = {
            "execution_order": [],
            "data_sharing_plan": {},
            "estimated_savings": 0.0
        }

        # Analyze dependencies and create optimal execution order
        agents = analysis_plan.get("agents", [])

        # Simple optimization: group agents that can share data
        data_producers = []
        data_consumers = []

        for agent in agents:
            if agent.get("produces_data"):
                data_producers.append(agent)
            if agent.get("consumes_data"):
                data_consumers.append(agent)

        # Prioritize data producers first
        optimized_plan["execution_order"] = data_producers + [a for a in agents if a not in data_producers]

        return optimized_plan

# Global data sharing optimizer
data_sharing_optimizer = DataSharingOptimizer()

# Utility functions for common communication patterns
async def request_data_from_agent(requester: str, provider: str, data_type: str,
                                 parameters: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """Helper function to request data from another agent with caching"""
    # Check if data is available in shared cache first
    cache_key = f"{provider}:{data_type}:{hash(str(parameters))}"
    cached_data = data_sharing_optimizer.get_shared_data(cache_key)

    if cached_data:
        logging.debug(f"Cache hit for data request: {cache_key}")
        return cached_data

    # Request from agent
    payload = {
        "data_type": data_type,
        "parameters": parameters or {}
    }

    result = await message_bus.send_request(
        requester, provider, MessageType.DATA_REQUEST, payload
    )

    # Cache the result for future use
    if result:
        data_sharing_optimizer.cache_shared_data(cache_key, result)

    return result

async def share_analysis_result(sender: str, result: Dict[str, Any],
                               recipients: List[str] = None, cache_result: bool = True) -> int:
    """Helper function to share analysis results with optional caching"""
    # Cache the result if requested
    if cache_result:
        cache_key = f"{sender}:analysis:{hash(str(result))}"
        data_sharing_optimizer.cache_shared_data(cache_key, result)

    if recipients:
        sent_count = 0
        for recipient in recipients:
            message = AgentMessage(
                id=str(uuid.uuid4()),
                sender=sender,
                recipient=recipient,
                message_type=MessageType.ANALYSIS_RESULT,
                priority=MessagePriority.MEDIUM,
                payload=result,
                timestamp=time.time()
            )
            if await message_bus.send_message(message):
                sent_count += 1
        return sent_count
    else:
        # Broadcast to all agents
        return await message_bus.broadcast_message(
            sender, MessageType.ANALYSIS_RESULT, result
        )

async def coordinate_parallel_analysis(coordinator: str, agents: List[str],
                                     analysis_tasks: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Coordinate parallel analysis across multiple agents"""
    start_time = time.time()

    # Send coordination signals to all agents
    coordination_payload = {
        "analysis_id": str(uuid.uuid4()),
        "participating_agents": agents,
        "tasks": analysis_tasks,
        "coordinator": coordinator
    }

    # Broadcast coordination signal
    await message_bus.broadcast_message(
        coordinator, MessageType.COORDINATION_SIGNAL, coordination_payload, MessagePriority.HIGH
    )

    # Collect results from all agents
    results = {}
    timeout = 60.0  # 1 minute timeout

    for agent in agents:
        if agent in analysis_tasks:
            task = analysis_tasks[agent]
            result = await message_bus.send_request(
                coordinator, agent, MessageType.DATA_REQUEST, task, timeout
            )
            results[agent] = result

    coordination_time = time.time() - start_time

    return {
        "results": results,
        "coordination_time": coordination_time,
        "participating_agents": agents,
        "success_count": len([r for r in results.values() if r is not None])
    }
