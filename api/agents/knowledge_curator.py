import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Environment variables with defensive checks
XAI_API_KEY = os.environ.get("XAI_API_KEY")
# Environment validation moved to runtime functions

# In-memory storage for knowledge base (Vercel ephemeral environment)
INSIGHTS_STORAGE = []
KNOWLEDGE_GAPS = []
QUALITY_METRICS = {}

def curate_knowledge_quality() -> Dict[str, Any]:
    """Assess and improve knowledge base quality"""
    try:
        if not INSIGHTS_STORAGE:
            return {
                "message": "No insights available for curation",
                "total_insights": 0,
                "quality_score": 0,
                "timestamp": datetime.now().isoformat(),
                "agent": "KnowledgeCurator"
            }
        
        # Quality metrics
        total_insights = len(INSIGHTS_STORAGE)
        refined_insights = sum(1 for insight in INSIGHTS_STORAGE if insight.get("insight", "").startswith("REFINED:"))
        
        # Ticker distribution analysis
        ticker_counts = defaultdict(int)
        agent_contributions = defaultdict(int)
        
        for insight in INSIGHTS_STORAGE:
            ticker = insight.get("ticker", "UNKNOWN")
            agent = insight.get("agent", "UNKNOWN")
            ticker_counts[ticker] += 1
            agent_contributions[agent] += 1
        
        # Calculate quality score
        refinement_ratio = refined_insights / total_insights if total_insights > 0 else 0
        coverage_score = len(ticker_counts) / 10  # Assuming 10 is ideal coverage
        balance_score = 1 - (max(ticker_counts.values()) - min(ticker_counts.values())) / total_insights if ticker_counts else 0
        
        quality_score = (refinement_ratio * 0.4 + coverage_score * 0.3 + balance_score * 0.3) * 100
        
        # Generate recommendations
        recommendations = []
        
        if refinement_ratio < 0.3:
            recommendations.append("Increase knowledge refinement rate - target 30%+ refined insights")
        
        if len(ticker_counts) < 5:
            recommendations.append("Expand ticker coverage - analyze more diverse stocks")
        
        if ticker_counts:
            min_insights = min(ticker_counts.values())
            max_insights = max(ticker_counts.values())
            if max_insights > min_insights * 2:
                recommendations.append("Balance insights across tickers - some are under-analyzed")
        
        # Identify knowledge gaps
        gaps = identify_knowledge_gaps_internal()
        
        quality_report = {
            "total_insights": total_insights,
            "refined_insights": refined_insights,
            "refinement_ratio": refinement_ratio,
            "ticker_coverage": len(ticker_counts),
            "quality_score": round(quality_score, 1),
            "ticker_distribution": dict(ticker_counts),
            "agent_contributions": dict(agent_contributions),
            "recommendations": recommendations,
            "knowledge_gaps": gaps,
            "timestamp": datetime.now().isoformat(),
            "agent": "KnowledgeCurator"
        }
        
        # Store quality metrics
        QUALITY_METRICS[datetime.now().isoformat()] = quality_report
        
        return quality_report
        
    except Exception as e:
        return {"error": str(e), "agent": "KnowledgeCurator"}

def identify_knowledge_gaps_internal() -> List[Dict[str, Any]]:
    """Internal function to identify knowledge gaps"""
    gaps = []
    
    if not INSIGHTS_STORAGE:
        return [{"type": "NO_DATA", "description": "No insights available for analysis"}]
    
    # Analyze temporal gaps
    now = datetime.now()
    recent_cutoff = now - timedelta(hours=24)
    
    recent_insights = [
        insight for insight in INSIGHTS_STORAGE 
        if datetime.fromisoformat(insight.get("timestamp", "")) > recent_cutoff
    ]
    
    if len(recent_insights) < 3:
        gaps.append({
            "type": "TEMPORAL_GAP",
            "description": "Insufficient recent insights - less than 3 in last 24 hours",
            "severity": "HIGH"
        })
    
    # Analyze agent coverage gaps
    agent_coverage = defaultdict(int)
    for insight in INSIGHTS_STORAGE:
        agent = insight.get("agent", "UNKNOWN")
        agent_coverage[agent] += 1
    
    expected_agents = ["RiskAgent", "NewsAgent", "EventSentinel"]
    for agent in expected_agents:
        if agent not in agent_coverage:
            gaps.append({
                "type": "AGENT_GAP",
                "description": f"No insights from {agent}",
                "agent": agent,
                "severity": "MEDIUM"
            })
    
    # Analyze content quality gaps
    low_quality_count = 0
    for insight in INSIGHTS_STORAGE:
        insight_text = insight.get("insight", "")
        if len(insight_text) < 50:  # Too short
            low_quality_count += 1
    
    if low_quality_count > len(INSIGHTS_STORAGE) * 0.3:
        gaps.append({
            "type": "QUALITY_GAP",
            "description": "High percentage of low-quality insights",
            "severity": "HIGH"
        })
    
    return gaps

def identify_knowledge_gaps(time_window_hours: int = 24) -> Dict[str, Any]:
    """Identify knowledge gaps and recommend areas for deeper analysis"""
    try:
        gaps = identify_knowledge_gaps_internal()
        
        # Additional analysis for specific time window
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        recent_insights = [
            insight for insight in INSIGHTS_STORAGE 
            if datetime.fromisoformat(insight.get("timestamp", "")) > cutoff_time
        ]
        
        # Analyze missing analysis types
        analysis_types = set()
        for insight in recent_insights:
            analysis_types.add(insight.get("analysis_type", "unknown"))
        
        expected_types = {"risk_assessment", "news_sentiment", "event_detection"}
        missing_types = expected_types - analysis_types
        
        for missing_type in missing_types:
            gaps.append({
                "type": "ANALYSIS_GAP",
                "description": f"Missing {missing_type} analysis in last {time_window_hours} hours",
                "analysis_type": missing_type,
                "severity": "MEDIUM"
            })
        
        # Generate recommendations
        recommendations = []
        
        high_severity_gaps = [gap for gap in gaps if gap.get("severity") == "HIGH"]
        if high_severity_gaps:
            recommendations.append("Address high-severity gaps immediately")
        
        if len(recent_insights) < 5:
            recommendations.append("Increase analysis frequency for better knowledge coverage")
        
        return {
            "time_window_hours": time_window_hours,
            "total_gaps": len(gaps),
            "high_severity_gaps": len(high_severity_gaps),
            "gaps": gaps,
            "recommendations": recommendations,
            "recent_insights_count": len(recent_insights),
            "timestamp": datetime.now().isoformat(),
            "agent": "KnowledgeCurator"
        }
        
    except Exception as e:
        return {"error": str(e), "agent": "KnowledgeCurator"}

def refine_insight(ticker: str, original_insight: str, additional_context: str = "") -> Dict[str, Any]:
    """Refine an existing insight with additional context and analysis"""
    try:
        # Find the original insight
        original_found = False
        for insight in INSIGHTS_STORAGE:
            if insight.get("ticker") == ticker and insight.get("insight") == original_insight:
                original_found = True
                break
        
        if not original_found and not additional_context:
            return {
                "error": "Original insight not found and no additional context provided",
                "ticker": ticker
            }
        
        # Create refined insight
        refined_insight = f"REFINED: {original_insight}"
        if additional_context:
            refined_insight += f" | Enhanced with: {additional_context}"
        
        # Add evolution context
        refined_insight += f" | Refined at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Store refined insight
        refined_entry = {
            "ticker": ticker,
            "insight": refined_insight,
            "original_insight": original_insight,
            "additional_context": additional_context,
            "timestamp": datetime.now().isoformat(),
            "agent": "KnowledgeCurator",
            "refined": True
        }
        
        INSIGHTS_STORAGE.append(refined_entry)
        
        return {
            "ticker": ticker,
            "refined_insight": refined_insight,
            "original_insight": original_insight,
            "refinement_successful": True,
            "timestamp": datetime.now().isoformat(),
            "agent": "KnowledgeCurator"
        }
        
    except Exception as e:
        return {"error": str(e), "ticker": ticker, "agent": "KnowledgeCurator"}

def get_quality_evolution() -> Dict[str, Any]:
    """Track quality evolution over time"""
    try:
        if not QUALITY_METRICS:
            return {
                "message": "No quality metrics available",
                "timestamp": datetime.now().isoformat(),
                "agent": "KnowledgeCurator"
            }
        
        # Sort quality metrics by timestamp
        sorted_metrics = sorted(QUALITY_METRICS.items(), key=lambda x: x[0])
        
        # Calculate evolution trends
        quality_scores = [metric[1]["quality_score"] for metric in sorted_metrics]
        insight_counts = [metric[1]["total_insights"] for metric in sorted_metrics]
        
        if len(quality_scores) > 1:
            quality_trend = "IMPROVING" if quality_scores[-1] > quality_scores[0] else "DECLINING"
            insight_trend = "GROWING" if insight_counts[-1] > insight_counts[0] else "STABLE"
        else:
            quality_trend = "STABLE"
            insight_trend = "STABLE"
        
        return {
            "quality_evolution": sorted_metrics,
            "quality_trend": quality_trend,
            "insight_trend": insight_trend,
            "current_quality_score": quality_scores[-1] if quality_scores else 0,
            "total_assessments": len(sorted_metrics),
            "timestamp": datetime.now().isoformat(),
            "agent": "KnowledgeCurator"
        }
        
    except Exception as e:
        return {"error": str(e), "agent": "KnowledgeCurator"}

def handler(request):
    """Vercel serverless function handler for KnowledgeCurator"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "quality_assessment")
            
            if action == "quality_assessment":
                return json.dumps(curate_knowledge_quality())
            
            elif action == "identify_gaps":
                time_window = body.get("time_window_hours", 24)
                return json.dumps(identify_knowledge_gaps(time_window))
            
            elif action == "refine_insight":
                ticker = body.get("ticker", "")
                original_insight = body.get("original_insight", "")
                additional_context = body.get("additional_context", "")
                return json.dumps(refine_insight(ticker, original_insight, additional_context))
            
            elif action == "quality_evolution":
                return json.dumps(get_quality_evolution())
            
            else:
                return json.dumps({"error": "Invalid action", "available_actions": ["quality_assessment", "identify_gaps", "refine_insight", "quality_evolution"]})
        
        else:
            return json.dumps({
                "agent": "KnowledgeCurator",
                "description": "Manages knowledge base quality and identifies analysis gaps",
                "endpoints": [
                    "POST - quality_assessment: Assess knowledge base quality",
                    "POST - identify_gaps: Identify knowledge gaps",
                    "POST - refine_insight: Refine existing insights",
                    "POST - quality_evolution: Track quality evolution over time"
                ],
                "status": "active"
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "agent": "KnowledgeCurator"}) 