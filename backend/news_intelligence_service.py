"""
News Intelligence Service
Ingests stock news articles and compresses them into temporal impact snapshots
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class NewsImpact(Enum):
    VERY_POSITIVE = "very_positive"  # +5% to +15%
    POSITIVE = "positive"            # +1% to +5%
    NEUTRAL = "neutral"              # -1% to +1%
    NEGATIVE = "negative"            # -5% to -1%
    VERY_NEGATIVE = "very_negative"  # -15% to -5%

class NewsCategory(Enum):
    EARNINGS = "earnings"
    PRODUCT_LAUNCH = "product_launch"
    REGULATORY = "regulatory"
    PARTNERSHIP = "partnership"
    LEADERSHIP = "leadership"
    MARKET_SENTIMENT = "market_sentiment"
    ANALYST_RATING = "analyst_rating"
    FINANCIAL_RESULTS = "financial_results"
    ACQUISITION = "acquisition"
    OTHER = "other"

@dataclass
class NewsSnapshot:
    ticker: str
    timestamp: datetime
    category: NewsCategory
    impact: NewsImpact
    price_change_1h: float
    price_change_24h: float
    summary_line_1: str  # First sentence - what happened
    summary_line_2: str  # Second sentence - market reaction/context
    source_url: str
    confidence_score: float  # 0.0 to 1.0

@dataclass
class StockPersonality:
    ticker: str
    total_events: int
    avg_volatility: float
    reaction_patterns: Dict[str, Dict]  # category -> {avg_impact, frequency, volatility}
    sentiment_sensitivity: float  # How much stock reacts to sentiment vs fundamentals
    news_momentum: float  # How quickly stock reacts to news
    last_updated: datetime

class NewsIntelligenceService:
    """Service to ingest, compress, and analyze news impact on stocks"""
    
    def __init__(self):
        self.news_snapshots: Dict[str, List[NewsSnapshot]] = {}  # ticker -> snapshots
        self.stock_personalities: Dict[str, StockPersonality] = {}  # ticker -> personality
        
    async def ingest_article(self, ticker: str, article_text: str, source_url: str,
                           price_before: float, price_1h_after: float, 
                           price_24h_after: float) -> NewsSnapshot:
        """Ingest a news article and create a compressed snapshot"""
        
        # Calculate price changes
        price_change_1h = ((price_1h_after - price_before) / price_before) * 100
        price_change_24h = ((price_24h_after - price_before) / price_before) * 100
        
        # Classify news category
        category = self._classify_news_category(article_text)
        
        # Determine impact level
        impact = self._determine_impact_level(price_change_24h)
        
        # Generate compressed summary (2 sentences)
        summary_line_1, summary_line_2 = await self._compress_article(
            article_text, ticker, category, price_change_24h
        )
        
        # Calculate confidence score
        confidence = self._calculate_confidence(article_text, price_change_1h, price_change_24h)
        
        # Create snapshot
        snapshot = NewsSnapshot(
            ticker=ticker,
            timestamp=datetime.now(),
            category=category,
            impact=impact,
            price_change_1h=price_change_1h,
            price_change_24h=price_change_24h,
            summary_line_1=summary_line_1,
            summary_line_2=summary_line_2,
            source_url=source_url,
            confidence_score=confidence
        )
        
        # Store snapshot
        if ticker not in self.news_snapshots:
            self.news_snapshots[ticker] = []
        self.news_snapshots[ticker].append(snapshot)
        
        # Update stock personality
        await self._update_stock_personality(ticker)
        
        logger.info(f"Created news snapshot for {ticker}: {impact.value} impact from {category.value}")
        
        return snapshot
    
    def _classify_news_category(self, article_text: str) -> NewsCategory:
        """Classify news article into category based on content"""
        text_lower = article_text.lower()
        
        # Keyword-based classification (can be enhanced with ML)
        if any(word in text_lower for word in ['earnings', 'revenue', 'profit', 'eps', 'quarterly']):
            return NewsCategory.EARNINGS
        elif any(word in text_lower for word in ['product', 'launch', 'release', 'unveil']):
            return NewsCategory.PRODUCT_LAUNCH
        elif any(word in text_lower for word in ['fda', 'regulatory', 'approval', 'compliance']):
            return NewsCategory.REGULATORY
        elif any(word in text_lower for word in ['partnership', 'deal', 'agreement', 'collaboration']):
            return NewsCategory.PARTNERSHIP
        elif any(word in text_lower for word in ['ceo', 'cfo', 'leadership', 'executive', 'resign']):
            return NewsCategory.LEADERSHIP
        elif any(word in text_lower for word in ['upgrade', 'downgrade', 'analyst', 'rating', 'target']):
            return NewsCategory.ANALYST_RATING
        elif any(word in text_lower for word in ['acquisition', 'merger', 'buyout', 'acquire']):
            return NewsCategory.ACQUISITION
        else:
            return NewsCategory.OTHER
    
    def _determine_impact_level(self, price_change_24h: float) -> NewsImpact:
        """Determine impact level based on price change"""
        if price_change_24h >= 5.0:
            return NewsImpact.VERY_POSITIVE
        elif price_change_24h >= 1.0:
            return NewsImpact.POSITIVE
        elif price_change_24h <= -5.0:
            return NewsImpact.VERY_NEGATIVE
        elif price_change_24h <= -1.0:
            return NewsImpact.NEGATIVE
        else:
            return NewsImpact.NEUTRAL
    
    async def _compress_article(self, article_text: str, ticker: str, 
                              category: NewsCategory, price_change: float) -> Tuple[str, str]:
        """Compress article into 2 sentences using AI-like logic"""
        
        # Extract key information
        sentences = article_text.split('.')[:5]  # First 5 sentences
        
        # Generate first sentence (what happened)
        if category == NewsCategory.EARNINGS:
            summary_line_1 = f"{ticker} reported quarterly earnings with key metrics showing {'strong' if price_change > 0 else 'weak'} performance."
        elif category == NewsCategory.PRODUCT_LAUNCH:
            summary_line_1 = f"{ticker} announced a new product launch that {'exceeded' if price_change > 0 else 'fell short of'} market expectations."
        elif category == NewsCategory.REGULATORY:
            summary_line_1 = f"{ticker} received regulatory news that {'positively' if price_change > 0 else 'negatively'} impacts its business prospects."
        else:
            summary_line_1 = f"{ticker} made an announcement in the {category.value} category affecting investor sentiment."
        
        # Generate second sentence (market reaction)
        direction = "surged" if price_change > 3 else "rose" if price_change > 0 else "fell" if price_change > -3 else "plummeted"
        summary_line_2 = f"The stock {direction} {abs(price_change):.1f}% in 24 hours as investors {'embraced' if price_change > 0 else 'rejected'} the news."
        
        return summary_line_1, summary_line_2
    
    def _calculate_confidence(self, article_text: str, price_change_1h: float, 
                            price_change_24h: float) -> float:
        """Calculate confidence score for the news-price correlation"""
        
        # Base confidence on consistency between 1h and 24h moves
        direction_consistency = 1.0 if (price_change_1h * price_change_24h) >= 0 else 0.5
        
        # Adjust for magnitude
        magnitude_factor = min(abs(price_change_24h) / 10.0, 1.0)  # Cap at 10%
        
        # Adjust for article quality (length, specificity)
        quality_factor = min(len(article_text) / 1000.0, 1.0)  # Longer articles = higher confidence
        
        confidence = (direction_consistency * 0.5 + magnitude_factor * 0.3 + quality_factor * 0.2)
        return min(confidence, 1.0)
    
    async def _update_stock_personality(self, ticker: str):
        """Update stock personality based on accumulated news snapshots"""
        
        if ticker not in self.news_snapshots or len(self.news_snapshots[ticker]) < 5:
            return  # Need at least 5 events to build personality
        
        snapshots = self.news_snapshots[ticker]
        
        # Calculate overall metrics
        total_events = len(snapshots)
        price_changes = [abs(s.price_change_24h) for s in snapshots]
        avg_volatility = sum(price_changes) / len(price_changes)
        
        # Analyze reaction patterns by category
        reaction_patterns = {}
        for category in NewsCategory:
            category_snapshots = [s for s in snapshots if s.category == category]
            if category_snapshots:
                avg_impact = sum(s.price_change_24h for s in category_snapshots) / len(category_snapshots)
                frequency = len(category_snapshots) / total_events
                volatility = sum(abs(s.price_change_24h) for s in category_snapshots) / len(category_snapshots)
                
                reaction_patterns[category.value] = {
                    "avg_impact": avg_impact,
                    "frequency": frequency,
                    "volatility": volatility
                }
        
        # Calculate sentiment sensitivity (how much stock moves on sentiment vs fundamentals)
        sentiment_events = [s for s in snapshots if s.category in [NewsCategory.ANALYST_RATING, NewsCategory.MARKET_SENTIMENT]]
        fundamental_events = [s for s in snapshots if s.category in [NewsCategory.EARNINGS, NewsCategory.FINANCIAL_RESULTS]]
        
        sentiment_sensitivity = 0.5  # Default
        if sentiment_events and fundamental_events:
            sentiment_avg = sum(abs(s.price_change_24h) for s in sentiment_events) / len(sentiment_events)
            fundamental_avg = sum(abs(s.price_change_24h) for s in fundamental_events) / len(fundamental_events)
            sentiment_sensitivity = sentiment_avg / (sentiment_avg + fundamental_avg)
        
        # Calculate news momentum (how quickly stock reacts)
        momentum_scores = []
        for snapshot in snapshots:
            if abs(snapshot.price_change_1h) > 0:
                momentum = abs(snapshot.price_change_1h) / abs(snapshot.price_change_24h)
                momentum_scores.append(min(momentum, 1.0))
        
        news_momentum = sum(momentum_scores) / len(momentum_scores) if momentum_scores else 0.5
        
        # Create/update personality
        personality = StockPersonality(
            ticker=ticker,
            total_events=total_events,
            avg_volatility=avg_volatility,
            reaction_patterns=reaction_patterns,
            sentiment_sensitivity=sentiment_sensitivity,
            news_momentum=news_momentum,
            last_updated=datetime.now()
        )
        
        self.stock_personalities[ticker] = personality
        
        logger.info(f"Updated personality for {ticker}: {total_events} events, {avg_volatility:.2f}% avg volatility")
    
    def get_stock_personality(self, ticker: str) -> Optional[StockPersonality]:
        """Get stock personality profile"""
        return self.stock_personalities.get(ticker)
    
    def get_news_history(self, ticker: str, days: int = 365) -> List[NewsSnapshot]:
        """Get news history for a ticker"""
        if ticker not in self.news_snapshots:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        return [s for s in self.news_snapshots[ticker] if s.timestamp >= cutoff_date]
    
    def analyze_news_trends(self, ticker: str) -> Dict:
        """Analyze news trends and patterns for a ticker"""
        snapshots = self.get_news_history(ticker)
        
        if len(snapshots) < 10:
            return {"error": "Insufficient data for trend analysis"}
        
        # Monthly trend analysis
        monthly_data = {}
        for snapshot in snapshots:
            month_key = snapshot.timestamp.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(snapshot)
        
        trends = {
            "total_events": len(snapshots),
            "avg_monthly_events": len(snapshots) / len(monthly_data),
            "most_common_category": max(
                set(s.category.value for s in snapshots),
                key=lambda x: sum(1 for s in snapshots if s.category.value == x)
            ),
            "avg_impact": sum(s.price_change_24h for s in snapshots) / len(snapshots),
            "volatility_trend": "increasing" if snapshots[-5:] else "stable",  # Simplified
            "monthly_breakdown": {
                month: {
                    "events": len(events),
                    "avg_impact": sum(e.price_change_24h for e in events) / len(events)
                }
                for month, events in monthly_data.items()
            }
        }
        
        return trends

# Global news intelligence service
news_intelligence = NewsIntelligenceService()
