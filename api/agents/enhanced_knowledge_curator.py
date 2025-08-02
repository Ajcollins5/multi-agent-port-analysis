import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from dataclasses import dataclass
import json

from .base_agent import BaseAgent
from ..utils.cache_manager import cached, cache_short_term
from .communication_protocol import AgentCommunicationInterface, message_bus, MessageType

@dataclass
class InsightQuality:
    """Represents the quality metrics of an insight"""
    relevance_score: float  # 0-1
    confidence_score: float  # 0-1
    novelty_score: float  # 0-1
    consistency_score: float  # 0-1
    actionability_score: float  # 0-1
    overall_score: float  # 0-1
    
    def __post_init__(self):
        # Calculate overall score as weighted average
        weights = {
            'relevance': 0.25,
            'confidence': 0.20,
            'novelty': 0.15,
            'consistency': 0.20,
            'actionability': 0.20
        }
        
        self.overall_score = (
            self.relevance_score * weights['relevance'] +
            self.confidence_score * weights['confidence'] +
            self.novelty_score * weights['novelty'] +
            self.consistency_score * weights['consistency'] +
            self.actionability_score * weights['actionability']
        )

@dataclass
class ConflictResolution:
    """Represents a resolved conflict between agent recommendations"""
    conflicting_agents: List[str]
    conflict_type: str
    original_recommendations: List[str]
    resolved_recommendation: str
    confidence: float
    resolution_method: str

class EnhancedKnowledgeCurator(BaseAgent):
    """
    Enhanced Knowledge Curator with advanced quality assessment and conflict resolution
    """
    
    def __init__(self):
        super().__init__("EnhancedKnowledgeCurator")
        self.communication = AgentCommunicationInterface("EnhancedKnowledgeCurator", message_bus)
        
        # Quality thresholds
        self.quality_thresholds = {
            'minimum_acceptable': 0.6,
            'good_quality': 0.75,
            'excellent_quality': 0.9
        }
        
        # Conflict detection patterns
        self.conflict_patterns = {
            'risk_level': ['HIGH', 'MEDIUM', 'LOW'],
            'action_words': ['buy', 'sell', 'hold', 'reduce', 'increase'],
            'sentiment': ['positive', 'negative', 'neutral', 'bullish', 'bearish']
        }
        
        # Agent specialization profiles
        self.agent_specializations = {
            'RiskAgent': {
                'expertise': ['volatility', 'risk_assessment', 'portfolio_risk'],
                'weight': 0.8,
                'reliability': 0.85
            },
            'EnhancedRiskAgent': {
                'expertise': ['advanced_risk', 'tail_risk', 'var_analysis'],
                'weight': 0.9,
                'reliability': 0.9
            },
            'NewsAgent': {
                'expertise': ['sentiment', 'news_impact', 'market_events'],
                'weight': 0.7,
                'reliability': 0.75
            },
            'EventSentinel': {
                'expertise': ['event_detection', 'correlation_analysis'],
                'weight': 0.75,
                'reliability': 0.8
            }
        }
    
    async def assess_insight_quality(self, insight: Dict[str, Any]) -> InsightQuality:
        """
        Comprehensive quality assessment of an insight
        """
        try:
            # Extract insight components
            insight_text = insight.get('insight', '')
            agent_name = insight.get('agent', 'Unknown')
            confidence = insight.get('confidence', 0.5)
            metadata = insight.get('metadata', {})
            
            # Calculate individual quality scores
            relevance_score = await self._calculate_relevance_score(insight)
            confidence_score = self._normalize_confidence_score(confidence)
            novelty_score = await self._calculate_novelty_score(insight)
            consistency_score = await self._calculate_consistency_score(insight)
            actionability_score = self._calculate_actionability_score(insight_text)
            
            quality = InsightQuality(
                relevance_score=relevance_score,
                confidence_score=confidence_score,
                novelty_score=novelty_score,
                consistency_score=consistency_score,
                actionability_score=actionability_score,
                overall_score=0.0  # Will be calculated in __post_init__
            )
            
            # Store quality assessment
            await self.store_insight(
                ticker=insight.get('ticker', 'UNKNOWN'),
                insight=f"Quality assessment: {quality.overall_score:.2f} overall score",
                confidence=quality.overall_score,
                impact_level=self._quality_to_impact_level(quality.overall_score),
                metadata={
                    'assessment_type': 'quality_evaluation',
                    'original_insight_id': insight.get('id'),
                    'quality_breakdown': {
                        'relevance': quality.relevance_score,
                        'confidence': quality.confidence_score,
                        'novelty': quality.novelty_score,
                        'consistency': quality.consistency_score,
                        'actionability': quality.actionability_score
                    },
                    'agent_evaluated': agent_name
                }
            )
            
            return quality
            
        except Exception as e:
            logging.error(f"Quality assessment failed: {e}")
            return InsightQuality(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
    
    async def _calculate_relevance_score(self, insight: Dict[str, Any]) -> float:
        """Calculate how relevant the insight is to current market conditions"""
        try:
            # Check if insight addresses current market concerns
            insight_text = insight.get('insight', '').lower()
            metadata = insight.get('metadata', {})
            
            # Time relevance (more recent = more relevant)
            timestamp = insight.get('timestamp')
            if timestamp:
                try:
                    insight_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_diff = datetime.now() - insight_time.replace(tzinfo=None)
                    time_relevance = max(0, 1 - (time_diff.total_seconds() / (24 * 3600)))  # Decay over 24 hours
                except:
                    time_relevance = 0.5
            else:
                time_relevance = 0.5
            
            # Content relevance (check for key financial terms)
            relevant_terms = [
                'volatility', 'risk', 'price', 'volume', 'trend', 'momentum',
                'support', 'resistance', 'breakout', 'earnings', 'revenue'
            ]
            
            term_matches = sum(1 for term in relevant_terms if term in insight_text)
            content_relevance = min(1.0, term_matches / 5)  # Normalize to 0-1
            
            # Market context relevance
            market_relevance = 0.7  # Default, could be enhanced with market data
            
            # Weighted combination
            relevance_score = (
                time_relevance * 0.3 +
                content_relevance * 0.4 +
                market_relevance * 0.3
            )
            
            return min(1.0, max(0.0, relevance_score))
            
        except Exception as e:
            logging.error(f"Relevance calculation failed: {e}")
            return 0.5
    
    def _normalize_confidence_score(self, confidence: float) -> float:
        """Normalize confidence score to 0-1 range"""
        try:
            if isinstance(confidence, (int, float)):
                return min(1.0, max(0.0, float(confidence)))
            return 0.5
        except:
            return 0.5
    
    async def _calculate_novelty_score(self, insight: Dict[str, Any]) -> float:
        """Calculate how novel/unique the insight is compared to recent insights"""
        try:
            ticker = insight.get('ticker', '')
            insight_text = insight.get('insight', '')
            
            # Get recent insights for the same ticker
            recent_insights = await self.get_insights(
                ticker=ticker,
                limit=20,
                time_window_hours=24
            )
            
            if not recent_insights.get('success') or not recent_insights.get('insights'):
                return 0.8  # High novelty if no recent insights
            
            # Simple similarity check (could be enhanced with NLP)
            similar_count = 0
            for existing_insight in recent_insights['insights']:
                existing_text = existing_insight.get('insight', '')
                
                # Basic similarity check using common words
                insight_words = set(insight_text.lower().split())
                existing_words = set(existing_text.lower().split())
                
                if len(insight_words) > 0 and len(existing_words) > 0:
                    similarity = len(insight_words & existing_words) / len(insight_words | existing_words)
                    if similarity > 0.6:  # 60% similarity threshold
                        similar_count += 1
            
            # Calculate novelty (inverse of similarity)
            total_insights = len(recent_insights['insights'])
            novelty_score = 1.0 - (similar_count / total_insights) if total_insights > 0 else 1.0
            
            return min(1.0, max(0.0, novelty_score))
            
        except Exception as e:
            logging.error(f"Novelty calculation failed: {e}")
            return 0.5
    
    async def _calculate_consistency_score(self, insight: Dict[str, Any]) -> float:
        """Calculate consistency with agent's historical insights"""
        try:
            agent_name = insight.get('agent', '')
            ticker = insight.get('ticker', '')
            
            # Get recent insights from the same agent
            agent_insights = await self.get_insights(
                ticker=ticker,
                limit=10,
                time_window_hours=72  # 3 days
            )
            
            if not agent_insights.get('success'):
                return 0.7  # Default consistency
            
            # Filter insights from the same agent
            same_agent_insights = [
                i for i in agent_insights.get('insights', [])
                if i.get('agent') == agent_name
            ]
            
            if len(same_agent_insights) < 2:
                return 0.8  # High consistency if limited history
            
            # Check for consistency in risk levels, sentiment, etc.
            current_risk = self._extract_risk_level(insight.get('insight', ''))
            historical_risks = [
                self._extract_risk_level(i.get('insight', ''))
                for i in same_agent_insights
            ]
            
            # Calculate consistency based on risk level stability
            if current_risk and historical_risks:
                consistent_risks = sum(1 for r in historical_risks if r == current_risk)
                consistency_score = consistent_risks / len(historical_risks)
            else:
                consistency_score = 0.7
            
            return min(1.0, max(0.0, consistency_score))
            
        except Exception as e:
            logging.error(f"Consistency calculation failed: {e}")
            return 0.7
    
    def _calculate_actionability_score(self, insight_text: str) -> float:
        """Calculate how actionable the insight is"""
        try:
            text_lower = insight_text.lower()
            
            # Check for actionable language
            action_indicators = [
                'recommend', 'suggest', 'should', 'consider', 'avoid',
                'buy', 'sell', 'hold', 'reduce', 'increase', 'monitor',
                'exit', 'enter', 'stop-loss', 'take-profit'
            ]
            
            action_count = sum(1 for indicator in action_indicators if indicator in text_lower)
            
            # Check for specific metrics or thresholds
            metric_indicators = ['%', 'price', 'target', 'level', 'threshold']
            metric_count = sum(1 for indicator in metric_indicators if indicator in text_lower)
            
            # Calculate actionability score
            actionability_score = min(1.0, (action_count * 0.3 + metric_count * 0.2) / 2)
            
            # Boost score if insight contains specific recommendations
            if any(word in text_lower for word in ['recommend', 'suggest', 'should']):
                actionability_score += 0.2
            
            return min(1.0, max(0.1, actionability_score))
            
        except Exception as e:
            logging.error(f"Actionability calculation failed: {e}")
            return 0.5
    
    def _extract_risk_level(self, insight_text: str) -> Optional[str]:
        """Extract risk level from insight text"""
        text_lower = insight_text.lower()
        
        if 'high risk' in text_lower or 'high volatility' in text_lower:
            return 'HIGH'
        elif 'medium risk' in text_lower or 'moderate risk' in text_lower:
            return 'MEDIUM'
        elif 'low risk' in text_lower:
            return 'LOW'
        
        return None
    
    def _quality_to_impact_level(self, quality_score: float) -> str:
        """Convert quality score to impact level"""
        if quality_score >= self.quality_thresholds['excellent_quality']:
            return 'HIGH'
        elif quality_score >= self.quality_thresholds['good_quality']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    async def detect_and_resolve_conflicts(self, agent_results: Dict[str, Any]) -> List[ConflictResolution]:
        """
        Detect conflicts between agent recommendations and resolve them
        """
        conflicts = []
        
        try:
            # Extract recommendations from all agents
            agent_recommendations = {}
            
            for agent_name, result in agent_results.items():
                if isinstance(result, dict) and result.get('success', True):
                    recommendations = result.get('recommendations', [])
                    if recommendations:
                        agent_recommendations[agent_name] = recommendations
            
            if len(agent_recommendations) < 2:
                return conflicts  # Need at least 2 agents to have conflicts
            
            # Detect conflicts
            risk_level_conflicts = self._detect_risk_level_conflicts(agent_results)
            action_conflicts = self._detect_action_conflicts(agent_recommendations)
            
            # Resolve conflicts
            for conflict in risk_level_conflicts + action_conflicts:
                resolution = await self._resolve_conflict(conflict, agent_results)
                conflicts.append(resolution)
            
            # Store conflict resolution results
            if conflicts:
                await self.store_insight(
                    ticker="PORTFOLIO",
                    insight=f"Resolved {len(conflicts)} conflicts between agent recommendations",
                    confidence=0.8,
                    impact_level="MEDIUM",
                    metadata={
                        'conflict_resolution': True,
                        'conflicts_resolved': len(conflicts),
                        'resolution_methods': [c.resolution_method for c in conflicts]
                    }
                )
            
            return conflicts
            
        except Exception as e:
            logging.error(f"Conflict detection failed: {e}")
            return []
    
    def _detect_risk_level_conflicts(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts in risk level assessments"""
        conflicts = []
        risk_levels = {}
        
        for agent_name, result in agent_results.items():
            if isinstance(result, dict) and 'risk_level' in result:
                risk_levels[agent_name] = result['risk_level']
        
        if len(set(risk_levels.values())) > 1:  # Different risk levels
            conflicts.append({
                'type': 'risk_level_conflict',
                'agents': list(risk_levels.keys()),
                'values': risk_levels,
                'severity': 'high' if 'HIGH' in risk_levels.values() and 'LOW' in risk_levels.values() else 'medium'
            })
        
        return conflicts
    
    def _detect_action_conflicts(self, agent_recommendations: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Detect conflicts in action recommendations"""
        conflicts = []
        
        # Extract action words from recommendations
        agent_actions = {}
        for agent_name, recommendations in agent_recommendations.items():
            actions = []
            for rec in recommendations:
                rec_lower = rec.lower()
                for action in self.conflict_patterns['action_words']:
                    if action in rec_lower:
                        actions.append(action)
            agent_actions[agent_name] = actions
        
        # Check for conflicting actions
        all_actions = set()
        for actions in agent_actions.values():
            all_actions.update(actions)
        
        conflicting_pairs = [
            ('buy', 'sell'), ('increase', 'reduce'), ('hold', 'sell')
        ]
        
        for action1, action2 in conflicting_pairs:
            if action1 in all_actions and action2 in all_actions:
                conflicting_agents = []
                for agent, actions in agent_actions.items():
                    if action1 in actions or action2 in actions:
                        conflicting_agents.append(agent)
                
                conflicts.append({
                    'type': 'action_conflict',
                    'agents': conflicting_agents,
                    'conflicting_actions': [action1, action2],
                    'severity': 'high'
                })
        
        return conflicts
    
    async def _resolve_conflict(self, conflict: Dict[str, Any], agent_results: Dict[str, Any]) -> ConflictResolution:
        """Resolve a specific conflict using agent specialization and confidence"""
        try:
            conflicting_agents = conflict['agents']
            conflict_type = conflict['type']
            
            if conflict_type == 'risk_level_conflict':
                # Weight by agent specialization in risk assessment
                weighted_votes = {}
                for agent in conflicting_agents:
                    if agent in agent_results:
                        risk_level = agent_results[agent].get('risk_level', 'MEDIUM')
                        confidence = agent_results[agent].get('confidence', 0.5)
                        agent_weight = self.agent_specializations.get(agent, {}).get('weight', 0.5)
                        
                        vote_weight = confidence * agent_weight
                        if risk_level not in weighted_votes:
                            weighted_votes[risk_level] = 0
                        weighted_votes[risk_level] += vote_weight
                
                # Choose the risk level with highest weighted vote
                resolved_risk = max(weighted_votes.items(), key=lambda x: x[1])[0]
                resolution_confidence = max(weighted_votes.values()) / sum(weighted_votes.values())
                
                return ConflictResolution(
                    conflicting_agents=conflicting_agents,
                    conflict_type=conflict_type,
                    original_recommendations=[f"{agent}: {agent_results[agent].get('risk_level')}" for agent in conflicting_agents],
                    resolved_recommendation=f"Resolved risk level: {resolved_risk}",
                    confidence=resolution_confidence,
                    resolution_method="weighted_voting"
                )
            
            elif conflict_type == 'action_conflict':
                # For action conflicts, prefer more conservative recommendations
                conservative_actions = ['hold', 'monitor', 'reduce']
                aggressive_actions = ['buy', 'sell', 'increase']
                
                # Default to conservative approach
                resolved_action = "hold"
                resolution_method = "conservative_default"
                
                return ConflictResolution(
                    conflicting_agents=conflicting_agents,
                    conflict_type=conflict_type,
                    original_recommendations=conflict.get('conflicting_actions', []),
                    resolved_recommendation=f"Resolved action: {resolved_action}",
                    confidence=0.7,
                    resolution_method=resolution_method
                )
            
            else:
                # Generic conflict resolution
                return ConflictResolution(
                    conflicting_agents=conflicting_agents,
                    conflict_type=conflict_type,
                    original_recommendations=["Unknown conflict"],
                    resolved_recommendation="Manual review required",
                    confidence=0.5,
                    resolution_method="manual_review"
                )
                
        except Exception as e:
            logging.error(f"Conflict resolution failed: {e}")
            return ConflictResolution(
                conflicting_agents=conflict.get('agents', []),
                conflict_type=conflict.get('type', 'unknown'),
                original_recommendations=["Resolution failed"],
                resolved_recommendation="Error in resolution",
                confidence=0.3,
                resolution_method="error_fallback"
            )
    
    @cache_short_term(ttl=300)
    async def generate_quality_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive quality report for recent insights"""
        try:
            # Get recent insights
            insights_result = await self.get_insights(
                limit=100,
                time_window_hours=time_window_hours
            )
            
            if not insights_result.get('success'):
                return {"error": "Failed to retrieve insights"}
            
            insights = insights_result.get('insights', [])
            
            if not insights:
                return {
                    "message": "No insights available for quality analysis",
                    "time_window_hours": time_window_hours
                }
            
            # Assess quality for each insight
            quality_assessments = []
            for insight in insights:
                quality = await self.assess_insight_quality(insight)
                quality_assessments.append({
                    'insight_id': insight.get('id'),
                    'agent': insight.get('agent'),
                    'ticker': insight.get('ticker'),
                    'quality': quality
                })
            
            # Calculate aggregate metrics
            overall_scores = [qa['quality'].overall_score for qa in quality_assessments]
            avg_quality = np.mean(overall_scores) if overall_scores else 0
            
            # Quality distribution
            excellent_count = sum(1 for score in overall_scores if score >= self.quality_thresholds['excellent_quality'])
            good_count = sum(1 for score in overall_scores if score >= self.quality_thresholds['good_quality'])
            acceptable_count = sum(1 for score in overall_scores if score >= self.quality_thresholds['minimum_acceptable'])
            
            # Agent performance
            agent_performance = defaultdict(list)
            for qa in quality_assessments:
                agent_performance[qa['agent']].append(qa['quality'].overall_score)
            
            agent_avg_quality = {
                agent: np.mean(scores) for agent, scores in agent_performance.items()
            }
            
            quality_report = {
                "time_window_hours": time_window_hours,
                "total_insights": len(insights),
                "average_quality": avg_quality,
                "quality_distribution": {
                    "excellent": excellent_count,
                    "good": good_count,
                    "acceptable": acceptable_count,
                    "below_threshold": len(overall_scores) - acceptable_count
                },
                "agent_performance": agent_avg_quality,
                "quality_trend": "improving" if avg_quality > 0.7 else "needs_attention",
                "recommendations": self._generate_quality_recommendations(avg_quality, agent_avg_quality),
                "timestamp": datetime.now().isoformat()
            }
            
            return quality_report
            
        except Exception as e:
            logging.error(f"Quality report generation failed: {e}")
            return {"error": str(e)}
    
    def _generate_quality_recommendations(self, avg_quality: float, agent_performance: Dict[str, float]) -> List[str]:
        """Generate recommendations based on quality analysis"""
        recommendations = []
        
        if avg_quality < self.quality_thresholds['minimum_acceptable']:
            recommendations.append("Overall insight quality is below acceptable threshold - review agent configurations")
        
        if avg_quality < self.quality_thresholds['good_quality']:
            recommendations.append("Consider implementing additional quality filters")
        
        # Agent-specific recommendations
        for agent, performance in agent_performance.items():
            if performance < self.quality_thresholds['minimum_acceptable']:
                recommendations.append(f"{agent} performance is below threshold - review agent logic")
        
        if not recommendations:
            recommendations.append("Quality metrics are satisfactory - continue current approach")
        
        return recommendations

# Global enhanced knowledge curator instance
enhanced_knowledge_curator = EnhancedKnowledgeCurator()
