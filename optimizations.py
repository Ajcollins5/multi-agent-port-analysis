#!/usr/bin/env python3
"""
Optimizations for Multi-Agent Portfolio Analysis System
Includes Grok pricing optimization, caching, and beta features
"""

import sqlite3
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
import logging

try:
    import yfinance as yf
except ImportError:
    yf = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrokOptimizer:
    """Optimize Grok API usage for cost efficiency"""
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self.response_cache = {}
        self.token_usage = {}
        
    def cache_key(self, prompt: str, model: str = "grok-4-0709") -> str:
        """Generate cache key for API requests"""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_response(self, prompt: str, model: str = "grok-4-0709") -> Optional[Dict]:
        """Get cached response if available and not expired"""
        key = self.cache_key(prompt, model)
        
        if key in self.response_cache:
            cached_data = self.response_cache[key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                logger.info(f"Cache hit for prompt: {prompt[:50]}...")
                return cached_data['response']
            else:
                # Remove expired cache entry
                del self.response_cache[key]
        
        return None
    
    def cache_response(self, prompt: str, response: Dict, model: str = "grok-4-0709"):
        """Cache API response"""
        key = self.cache_key(prompt, model)
        self.response_cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        logger.info(f"Cached response for prompt: {prompt[:50]}...")
    
    def optimize_prompt(self, prompt: str, max_tokens: int = 1000) -> str:
        """Optimize prompt to reduce token usage"""
        # Remove excessive whitespace
        optimized = ' '.join(prompt.split())
        
        # Truncate if too long (rough estimation: 1 token ≈ 4 characters)
        if len(optimized) > max_tokens * 4:
            optimized = optimized[:max_tokens * 4] + "..."
            logger.warning(f"Prompt truncated to {max_tokens * 4} characters")
        
        return optimized
    
    def track_usage(self, model: str, tokens_used: int, cost: float = 0.0):
        """Track API usage for cost monitoring"""
        date_key = datetime.now().strftime('%Y-%m-%d')
        
        if date_key not in self.token_usage:
            self.token_usage[date_key] = {
                'tokens': 0,
                'requests': 0,
                'estimated_cost': 0.0
            }
        
        self.token_usage[date_key]['tokens'] += tokens_used
        self.token_usage[date_key]['requests'] += 1
        self.token_usage[date_key]['estimated_cost'] += cost
        
        logger.info(f"Usage tracked: {tokens_used} tokens, ${cost:.4f}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total_tokens = sum(day['tokens'] for day in self.token_usage.values())
        total_requests = sum(day['requests'] for day in self.token_usage.values())
        total_cost = sum(day['estimated_cost'] for day in self.token_usage.values())
        
        return {
            'daily_usage': self.token_usage,
            'total_tokens': total_tokens,
            'total_requests': total_requests,
            'estimated_total_cost': total_cost
        }

class StockDataCache:
    """Cache stock data to reduce API calls"""
    
    def __init__(self, cache_ttl: int = 300):  # 5 minutes default
        self.cache_ttl = cache_ttl
        self.stock_cache = {}
    
    def get_cached_data(self, ticker: str, period: str = "5d") -> Optional[Dict]:
        """Get cached stock data"""
        cache_key = f"{ticker}:{period}"
        
        if cache_key in self.stock_cache:
            cached_data = self.stock_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                logger.info(f"Cache hit for stock data: {ticker}")
                return cached_data['data']
            else:
                del self.stock_cache[cache_key]
        
        return None
    
    def cache_data(self, ticker: str, data: Dict, period: str = "5d"):
        """Cache stock data"""
        cache_key = f"{ticker}:{period}"
        self.stock_cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.info(f"Cached stock data for: {ticker}")

class DatabaseOptimizer:
    """Database optimizations and beta features"""
    
    def __init__(self, db_path: str = "knowledge.db"):
        self.db_path = db_path
        self.init_beta_schema()
    
    def init_beta_schema(self):
        """Initialize beta database schema with user support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table for beta multi-user support
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                subscription_tier TEXT DEFAULT 'free',
                api_quota_used INTEGER DEFAULT 0,
                api_quota_limit INTEGER DEFAULT 100
            )
        ''')
        
        # Create portfolios table for user-specific portfolios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                portfolio_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                tickers TEXT NOT NULL,  -- JSON array of tickers
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Update insights table to include user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights_new (
                insight_id TEXT PRIMARY KEY,
                user_id TEXT,
                portfolio_id TEXT,
                ticker TEXT NOT NULL,
                insight TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.0,
                source_agent TEXT,
                tokens_used INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (portfolio_id)
            )
        ''')
        
        # Create API usage tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                usage_id TEXT PRIMARY KEY,
                user_id TEXT,
                endpoint TEXT NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create cache table for query results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_cache (
                cache_key TEXT PRIMARY KEY,
                query_type TEXT NOT NULL,
                result TEXT NOT NULL,  -- JSON result
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Beta database schema initialized")
    
    def migrate_existing_data(self):
        """Migrate existing insights to new schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if old insights table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='insights'
        ''')
        
        if cursor.fetchone():
            # Create default user for existing data
            default_user_id = "default_user"
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, email)
                VALUES (?, ?, ?)
            ''', (default_user_id, "default", "default@example.com"))
            
            # Create default portfolio
            default_portfolio_id = "default_portfolio"
            cursor.execute('''
                INSERT OR IGNORE INTO portfolios (portfolio_id, user_id, name, tickers)
                VALUES (?, ?, ?, ?)
            ''', (default_portfolio_id, default_user_id, "Default Portfolio", '["AAPL"]'))
            
            # Migrate existing insights
            cursor.execute('SELECT ticker, insight, timestamp FROM insights')
            old_insights = cursor.fetchall()
            
            for ticker, insight, timestamp in old_insights:
                insight_id = f"migrated_{hashlib.md5(f'{ticker}:{insight}:{timestamp}'.encode()).hexdigest()}"
                cursor.execute('''
                    INSERT OR IGNORE INTO insights_new 
                    (insight_id, user_id, portfolio_id, ticker, insight, source_agent, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (insight_id, default_user_id, default_portfolio_id, ticker, insight, "legacy", timestamp))
            
            logger.info(f"Migrated {len(old_insights)} existing insights")
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, email: str) -> Optional[str]:
        """Create a new user (beta feature)"""
        user_id = f"user_{hashlib.md5(f'{username}:{email}'.encode()).hexdigest()[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, username, email)
                VALUES (?, ?, ?)
            ''', (user_id, username, email))
            conn.commit()
            logger.info(f"Created user: {username} ({user_id})")
            return user_id
        except sqlite3.IntegrityError:
            logger.error(f"User already exists: {username}")
            return None
        finally:
            conn.close()
    
    def create_portfolio(self, user_id: str, name: str, tickers: List[str]) -> str:
        """Create a new portfolio for user"""
        portfolio_id = f"portfolio_{hashlib.md5(f'{user_id}:{name}'.encode()).hexdigest()[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO portfolios (portfolio_id, user_id, name, tickers)
            VALUES (?, ?, ?, ?)
        ''', (portfolio_id, user_id, name, json.dumps(tickers)))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created portfolio: {name} ({portfolio_id}) for user {user_id}")
        return portfolio_id
    
    def get_user_portfolios(self, user_id: str) -> List[Dict]:
        """Get all portfolios for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT portfolio_id, name, description, tickers, created_at, updated_at
            FROM portfolios
            WHERE user_id = ?
        ''', (user_id,))
        
        portfolios = []
        for row in cursor.fetchall():
            portfolios.append({
                'portfolio_id': row[0],
                'name': row[1],
                'description': row[2],
                'tickers': json.loads(row[3]),
                'created_at': row[4],
                'updated_at': row[5]
            })
        
        conn.close()
        return portfolios
    
    def track_api_usage(self, user_id: str, endpoint: str, tokens_used: int, cost: float):
        """Track API usage for cost monitoring"""
        usage_id = f"usage_{int(time.time())}_{hashlib.md5(f'{user_id}:{endpoint}'.encode()).hexdigest()[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_usage (usage_id, user_id, endpoint, tokens_used, cost)
            VALUES (?, ?, ?, ?, ?)
        ''', (usage_id, user_id, endpoint, tokens_used, cost))
        
        # Update user quota
        cursor.execute('''
            UPDATE users 
            SET api_quota_used = api_quota_used + ?
            WHERE user_id = ?
        ''', (tokens_used, user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_usage_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get usage statistics for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('''
            SELECT api_quota_used, api_quota_limit, subscription_tier
            FROM users
            WHERE user_id = ?
        ''', (user_id,))
        
        user_info = cursor.fetchone()
        if not user_info:
            return None
        
        # Get usage by day
        cursor.execute('''
            SELECT DATE(timestamp) as date, 
                   SUM(tokens_used) as tokens,
                   SUM(cost) as cost,
                   COUNT(*) as requests
            FROM api_usage
            WHERE user_id = ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
        ''', (user_id,))
        
        daily_usage = []
        for row in cursor.fetchall():
            daily_usage.append({
                'date': row[0],
                'tokens': row[1],
                'cost': row[2],
                'requests': row[3]
            })
        
        conn.close()
        
        return {
            'quota_used': user_info[0],
            'quota_limit': user_info[1],
            'subscription_tier': user_info[2],
            'daily_usage': daily_usage
        }

def cache_decorator(cache_ttl: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Check cache
            if cache_key in cache:
                cached_data = cache[cache_key]
                if time.time() - cached_data['timestamp'] < cache_ttl:
                    logger.info(f"Cache hit for {func.__name__}")
                    return cached_data['result']
                else:
                    del cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
            
            logger.info(f"Cached result for {func.__name__}")
            return result
        
        return wrapper
    return decorator

class BatchProcessor:
    """Process multiple requests in batches to optimize API usage"""
    
    def __init__(self, batch_size: int = 5, delay: float = 1.0):
        self.batch_size = batch_size
        self.delay = delay
        self.pending_requests = []
    
    def add_request(self, request_data: Dict):
        """Add request to batch"""
        self.pending_requests.append(request_data)
        
        if len(self.pending_requests) >= self.batch_size:
            return self.process_batch()
        
        return None
    
    def process_batch(self) -> List[Dict]:
        """Process accumulated requests as a batch"""
        if not self.pending_requests:
            return []
        
        batch = self.pending_requests[:self.batch_size]
        self.pending_requests = self.pending_requests[self.batch_size:]
        
        logger.info(f"Processing batch of {len(batch)} requests")
        
        # Add delay to respect rate limits
        time.sleep(self.delay)
        
        # Process each request in the batch
        results = []
        for request in batch:
            # This would be replaced with actual processing logic
            results.append({
                'request_id': request.get('id'),
                'status': 'processed',
                'timestamp': datetime.now().isoformat()
            })
        
        return results
    
    def flush(self) -> List[Dict]:
        """Process all remaining requests"""
        if not self.pending_requests:
            return []
        
        results = []
        while self.pending_requests:
            batch_results = self.process_batch()
            results.extend(batch_results)
        
        return results

# Global instances
grok_optimizer = GrokOptimizer()
stock_cache = StockDataCache()
db_optimizer = DatabaseOptimizer()
batch_processor = BatchProcessor()

# Example usage functions
def optimized_stock_analysis(ticker: str) -> Dict[str, Any]:
    """Optimized stock analysis with caching"""
    # Check cache first
    cached_data = stock_cache.get_cached_data(ticker)
    if cached_data:
        return cached_data
    
    # Fetch new data (this would be replaced with actual yfinance call)
    import yfinance as yf
    data = yf.download(ticker, period="5d", progress=False)
    
    if data.empty:
        return {"error": f"No data for {ticker}"}
    
    volatility = data['Close'].pct_change().std()
    
    result = {
        'ticker': ticker,
        'volatility': float(volatility),
        'timestamp': datetime.now().isoformat(),
        'cached': False
    }
    
    # Cache the result
    stock_cache.cache_data(ticker, result)
    
    return result

def optimized_grok_query(prompt: str, user_id: str = None) -> Dict[str, Any]:
    """Optimized Grok query with caching and usage tracking"""
    # Check cache first
    cached_response = grok_optimizer.get_cached_response(prompt)
    if cached_response:
        return cached_response
    
    # Optimize prompt
    optimized_prompt = grok_optimizer.optimize_prompt(prompt)
    
    # This would be replaced with actual Grok API call
    response = {
        'response': f"Optimized analysis for: {optimized_prompt[:100]}...",
        'tokens_used': len(optimized_prompt.split()),
        'timestamp': datetime.now().isoformat()
    }
    
    # Cache response
    grok_optimizer.cache_response(prompt, response)
    
    # Track usage
    tokens_used = response['tokens_used']
    estimated_cost = tokens_used * 0.0001  # Example pricing
    grok_optimizer.track_usage("grok-4-0709", tokens_used, estimated_cost)
    
    if user_id:
        db_optimizer.track_api_usage(user_id, "grok_query", tokens_used, estimated_cost)
    
    return response

if __name__ == "__main__":
    # Example usage
    print("Multi-Agent Portfolio Analysis - Optimizations Module")
    print("=" * 50)
    
    # Test optimizations
    result = optimized_stock_analysis("AAPL")
    print(f"Stock analysis result: {result}")
    
    # Test Grok optimization
    grok_result = optimized_grok_query("Analyze AAPL stock performance")
    print(f"Grok analysis result: {grok_result}")
    
    # Show usage stats
    stats = grok_optimizer.get_usage_stats()
    print(f"Usage stats: {stats}") 