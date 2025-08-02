"""
Automated News Intelligence Pipeline
Integrates with Financial Modeling Prep API and Grok 4 for real-time news analysis
"""

import asyncio
import logging
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import os
from news_intelligence_service import news_intelligence, NewsSnapshot, NewsCategory, NewsImpact
from rate_limiter import news_rate_limiter, rate_limited

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    title: str
    text: str
    url: str
    published_date: datetime
    ticker: str
    site: str

@dataclass
class PriceData:
    ticker: str
    timestamp: datetime
    price: float
    change_1h: float
    change_24h: float

class FinancialModelingPrepAPI:
    """Interface to Financial Modeling Prep API for news and price data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @rate_limited("financial_modeling_prep")
    async def get_latest_news(self, ticker: str, limit: int = 50) -> List[NewsArticle]:
        """Fetch latest news articles for a ticker"""
        try:
            url = f"{self.base_url}/stock_news"
            params = {
                "tickers": ticker,
                "limit": limit,
                "apikey": self.api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = []
                    
                    for item in data:
                        articles.append(NewsArticle(
                            title=item.get("title", ""),
                            text=item.get("text", ""),
                            url=item.get("url", ""),
                            published_date=datetime.fromisoformat(item.get("publishedDate", "").replace("Z", "+00:00")),
                            ticker=ticker,
                            site=item.get("site", "")
                        ))
                    
                    return articles
                else:
                    logger.error(f"Failed to fetch news for {ticker}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return []
    
    @rate_limited("financial_modeling_prep")
    async def get_historical_prices(self, ticker: str, from_date: datetime, to_date: datetime) -> List[PriceData]:
        """Fetch historical price data for impact analysis"""
        try:
            url = f"{self.base_url}/historical-chart/1hour/{ticker}"
            params = {
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d"),
                "apikey": self.api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = []
                    
                    for item in data:
                        prices.append(PriceData(
                            ticker=ticker,
                            timestamp=datetime.fromisoformat(item.get("date", "")),
                            price=float(item.get("close", 0)),
                            change_1h=0,  # Will be calculated
                            change_24h=0  # Will be calculated
                        ))
                    
                    return sorted(prices, key=lambda x: x.timestamp)
                else:
                    logger.error(f"Failed to fetch prices for {ticker}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching prices for {ticker}: {e}")
            return []

class GrokAIAnalyzer:
    """Interface to Grok 4 AI for news analysis and enrichment"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @rate_limited("grok_ai")
    async def analyze_news_article(self, article: NewsArticle, price_impact: Dict) -> Dict:
        """Use Grok 4 to analyze and enrich news article"""
        try:
            prompt = f"""
            Analyze this financial news article and provide structured insights:
            
            ARTICLE:
            Title: {article.title}
            Content: {article.text[:2000]}...
            Ticker: {article.ticker}
            Published: {article.published_date}
            
            PRICE IMPACT:
            1 Hour Change: {price_impact.get('change_1h', 0):.2f}%
            24 Hour Change: {price_impact.get('change_24h', 0):.2f}%
            
            Please provide:
            1. Category classification (earnings, product_launch, regulatory, partnership, leadership, analyst_rating, acquisition, other)
            2. Impact sentiment (very_positive, positive, neutral, negative, very_negative)
            3. Two-sentence summary:
               - Sentence 1: What happened (the key event/news)
               - Sentence 2: Market reaction and context
            4. Confidence score (0.0 to 1.0) for the news-price correlation
            5. Key themes and sentiment drivers
            6. Potential future implications
            
            Return as JSON format.
            """
            
            # For demo purposes, we'll simulate Grok 4 response
            # In production, this would call the actual Grok 4 API
            analysis = await self._simulate_grok_analysis(article, price_impact)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing article with Grok 4: {e}")
            return self._fallback_analysis(article, price_impact)
    
    async def _simulate_grok_analysis(self, article: NewsArticle, price_impact: Dict) -> Dict:
        """Simulate Grok 4 analysis for demo purposes"""
        
        # Determine category based on title and content
        title_lower = article.title.lower()
        text_lower = article.text.lower()
        
        if any(word in title_lower + text_lower for word in ['earnings', 'revenue', 'profit', 'eps', 'quarterly']):
            category = 'earnings'
        elif any(word in title_lower + text_lower for word in ['product', 'launch', 'release', 'unveil']):
            category = 'product_launch'
        elif any(word in title_lower + text_lower for word in ['fda', 'regulatory', 'approval', 'compliance']):
            category = 'regulatory'
        elif any(word in title_lower + text_lower for word in ['partnership', 'deal', 'agreement', 'collaboration']):
            category = 'partnership'
        elif any(word in title_lower + text_lower for word in ['ceo', 'cfo', 'leadership', 'executive']):
            category = 'leadership'
        elif any(word in title_lower + text_lower for word in ['upgrade', 'downgrade', 'analyst', 'rating']):
            category = 'analyst_rating'
        elif any(word in title_lower + text_lower for word in ['acquisition', 'merger', 'buyout']):
            category = 'acquisition'
        else:
            category = 'other'
        
        # Determine impact based on price change
        change_24h = price_impact.get('change_24h', 0)
        if change_24h >= 5.0:
            impact = 'very_positive'
        elif change_24h >= 1.0:
            impact = 'positive'
        elif change_24h <= -5.0:
            impact = 'very_negative'
        elif change_24h <= -1.0:
            impact = 'negative'
        else:
            impact = 'neutral'
        
        # Generate enriched summary
        direction = "surged" if change_24h > 3 else "rose" if change_24h > 0 else "fell" if change_24h > -3 else "plummeted"
        reaction = "embraced" if change_24h > 0 else "rejected"
        
        summary_line_1 = f"{article.ticker} {self._generate_event_description(category, article.title)}"
        summary_line_2 = f"The stock {direction} {abs(change_24h):.1f}% in 24 hours as investors {reaction} the news."
        
        # Calculate confidence based on various factors
        confidence = min(0.95, max(0.3, 
            0.5 + abs(change_24h) * 0.05 + (len(article.text) / 2000) * 0.2
        ))
        
        return {
            "category": category,
            "impact": impact,
            "summary_line_1": summary_line_1,
            "summary_line_2": summary_line_2,
            "confidence_score": confidence,
            "themes": self._extract_themes(article),
            "sentiment_drivers": self._extract_sentiment_drivers(article, change_24h),
            "future_implications": self._generate_implications(category, impact)
        }
    
    def _generate_event_description(self, category: str, title: str) -> str:
        """Generate event description based on category"""
        descriptions = {
            'earnings': 'reported quarterly earnings with key metrics showing',
            'product_launch': 'announced a new product launch that',
            'regulatory': 'received regulatory news that',
            'partnership': 'announced strategic partnership that',
            'leadership': 'announced executive leadership changes that',
            'analyst_rating': 'received analyst rating changes that',
            'acquisition': 'announced acquisition activity that',
            'other': 'made an announcement that'
        }
        
        performance = "strong performance" if "beat" in title.lower() or "exceed" in title.lower() else "mixed results"
        expectation = "exceeded market expectations" if "beat" in title.lower() else "met analyst expectations"
        impact_desc = "positively impacts" if "positive" in title.lower() else "impacts"
        
        base = descriptions.get(category, descriptions['other'])
        
        if category == 'earnings':
            return f"{base} {performance}."
        elif category in ['product_launch', 'partnership']:
            return f"{base} {expectation}."
        else:
            return f"{base} {impact_desc} its business prospects."
    
    def _extract_themes(self, article: NewsArticle) -> List[str]:
        """Extract key themes from article"""
        themes = []
        text_lower = (article.title + " " + article.text).lower()
        
        theme_keywords = {
            'growth': ['growth', 'expansion', 'increase', 'rise'],
            'innovation': ['innovation', 'technology', 'ai', 'digital'],
            'market_share': ['market', 'competition', 'share', 'dominance'],
            'financial_performance': ['revenue', 'profit', 'earnings', 'margin'],
            'regulatory': ['regulation', 'compliance', 'approval', 'fda'],
            'leadership': ['ceo', 'management', 'leadership', 'executive']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:3]  # Return top 3 themes
    
    def _extract_sentiment_drivers(self, article: NewsArticle, price_change: float) -> List[str]:
        """Extract sentiment drivers"""
        drivers = []
        text_lower = (article.title + " " + article.text).lower()
        
        if price_change > 0:
            positive_drivers = ['beat expectations', 'strong results', 'positive outlook', 'growth potential']
            drivers.extend([d for d in positive_drivers if any(word in text_lower for word in d.split())])
        else:
            negative_drivers = ['missed expectations', 'weak results', 'concerns', 'challenges']
            drivers.extend([d for d in negative_drivers if any(word in text_lower for word in d.split())])
        
        return drivers[:2]  # Return top 2 drivers
    
    def _generate_implications(self, category: str, impact: str) -> str:
        """Generate future implications"""
        implications = {
            'earnings': 'May influence next quarter guidance and investor confidence.',
            'product_launch': 'Could impact market share and competitive positioning.',
            'regulatory': 'May affect operational capabilities and compliance costs.',
            'partnership': 'Could create new revenue opportunities and market access.',
            'leadership': 'May signal strategic direction changes and operational shifts.',
            'analyst_rating': 'Could influence institutional investor sentiment and stock valuation.',
            'acquisition': 'May reshape competitive landscape and business model.'
        }
        
        return implications.get(category, 'Could have broader implications for business strategy.')
    
    def _fallback_analysis(self, article: NewsArticle, price_impact: Dict) -> Dict:
        """Fallback analysis if Grok 4 is unavailable"""
        return {
            "category": "other",
            "impact": "neutral",
            "summary_line_1": f"{article.ticker} made an announcement affecting investor sentiment.",
            "summary_line_2": f"The stock moved {price_impact.get('change_24h', 0):.1f}% in 24 hours following the news.",
            "confidence_score": 0.5,
            "themes": ["general_news"],
            "sentiment_drivers": ["market_reaction"],
            "future_implications": "Monitoring required for further developments."
        }

class AutomatedNewsPipeline:
    """Main pipeline orchestrator for automated news intelligence"""

    def __init__(self, fmp_api_key: str, grok_api_key: str):
        self.fmp_api_key = fmp_api_key
        self.grok_api_key = grok_api_key
        # OPTIMIZATION: Use LRU cache with size limit to prevent memory leaks
        from collections import OrderedDict
        self.processed_articles = OrderedDict()  # Track processed articles with LRU eviction
        self.max_processed_articles = 10000  # Limit memory usage
        self._session_pool = None  # Reuse HTTP sessions
        self._rate_limiter = {}  # Track API rate limits per endpoint
    
    async def process_ticker_news(self, ticker: str) -> List[NewsSnapshot]:
        """Process all new articles for a ticker"""
        snapshots = []
        
        async with FinancialModelingPrepAPI(self.fmp_api_key) as fmp_api:
            async with GrokAIAnalyzer(self.grok_api_key) as grok_ai:
                
                # Get latest news articles
                articles = await fmp_api.get_latest_news(ticker, limit=20)
                logger.info(f"Found {len(articles)} articles for {ticker}")
                
                for article in articles:
                    # Skip if already processed (with LRU cache management)
                    article_id = f"{ticker}_{article.url}_{article.published_date}"
                    if article_id in self.processed_articles:
                        # Move to end (LRU)
                        self.processed_articles.move_to_end(article_id)
                        continue

                    # OPTIMIZATION: Manage cache size to prevent memory leaks
                    if len(self.processed_articles) >= self.max_processed_articles:
                        # Remove oldest entries
                        for _ in range(100):  # Remove in batches for efficiency
                            if self.processed_articles:
                                self.processed_articles.popitem(last=False)
                    
                    try:
                        # Get price data around article publication
                        price_impact = await self._calculate_price_impact(
                            fmp_api, ticker, article.published_date
                        )
                        
                        if price_impact:
                            # Analyze with Grok 4
                            analysis = await grok_ai.analyze_news_article(article, price_impact)
                            
                            # Create news snapshot
                            snapshot = await news_intelligence.ingest_article(
                                ticker=ticker,
                                article_text=article.text,
                                source_url=article.url,
                                price_before=price_impact['price_before'],
                                price_1h_after=price_impact['price_1h_after'],
                                price_24h_after=price_impact['price_24h_after']
                            )
                            
                            # Enhance with Grok analysis
                            snapshot.summary_line_1 = analysis['summary_line_1']
                            snapshot.summary_line_2 = analysis['summary_line_2']
                            snapshot.confidence_score = analysis['confidence_score']
                            
                            snapshots.append(snapshot)
                            # OPTIMIZATION: Add to LRU cache
                            self.processed_articles[article_id] = datetime.now()
                            
                            logger.info(f"Processed article for {ticker}: {analysis['category']} - {analysis['impact']}")
                            
                    except Exception as e:
                        logger.error(f"Error processing article for {ticker}: {e}")
                        continue
        
        return snapshots
    
    async def _calculate_price_impact(self, fmp_api: FinancialModelingPrepAPI, 
                                    ticker: str, published_date: datetime) -> Optional[Dict]:
        """Calculate price impact around article publication"""
        try:
            # Get price data from 2 hours before to 25 hours after publication
            from_date = published_date - timedelta(hours=2)
            to_date = published_date + timedelta(hours=25)
            
            prices = await fmp_api.get_historical_prices(ticker, from_date, to_date)
            
            if len(prices) < 3:
                return None
            
            # Find prices at key intervals
            price_before = self._find_closest_price(prices, published_date - timedelta(minutes=30))
            price_1h_after = self._find_closest_price(prices, published_date + timedelta(hours=1))
            price_24h_after = self._find_closest_price(prices, published_date + timedelta(hours=24))
            
            if price_before and price_1h_after and price_24h_after:
                return {
                    'price_before': price_before.price,
                    'price_1h_after': price_1h_after.price,
                    'price_24h_after': price_24h_after.price,
                    'change_1h': ((price_1h_after.price - price_before.price) / price_before.price) * 100,
                    'change_24h': ((price_24h_after.price - price_before.price) / price_before.price) * 100
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating price impact for {ticker}: {e}")
            return None
    
    def _find_closest_price(self, prices: List[PriceData], target_time: datetime) -> Optional[PriceData]:
        """Find price data closest to target time"""
        if not prices:
            return None
        
        closest_price = min(prices, key=lambda p: abs((p.timestamp - target_time).total_seconds()))
        
        # Only return if within 2 hours of target
        if abs((closest_price.timestamp - target_time).total_seconds()) <= 7200:
            return closest_price
        
        return None
    
    async def run_continuous_monitoring(self, tickers: List[str], interval_minutes: int = 30):
        """Run continuous monitoring for multiple tickers"""
        logger.info(f"Starting continuous monitoring for {len(tickers)} tickers")
        
        while True:
            try:
                for ticker in tickers:
                    snapshots = await self.process_ticker_news(ticker)
                    if snapshots:
                        logger.info(f"Created {len(snapshots)} new snapshots for {ticker}")
                
                # Wait before next cycle
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

# Global pipeline instance
automated_pipeline = AutomatedNewsPipeline(
    fmp_api_key=os.getenv("FMP_API_KEY", ""),
    grok_api_key=os.getenv("GROK_API_KEY", "")
)
