"""
News Pipeline Scheduler
Manages automated news monitoring and processing schedules
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict
import os
from automated_news_pipeline import automated_pipeline

logger = logging.getLogger(__name__)

class NewsScheduler:
    """Scheduler for automated news processing"""
    
    def __init__(self):
        self.is_running = False
        self.monitored_tickers = []
        self.monitoring_tasks = {}
        
    def add_ticker(self, ticker: str, interval_minutes: int = 30):
        """Add a ticker to monitoring schedule"""
        if ticker not in self.monitored_tickers:
            self.monitored_tickers.append(ticker)
            
            # Schedule periodic analysis
            schedule.every(interval_minutes).minutes.do(
                self._schedule_ticker_analysis, ticker
            ).tag(f"ticker_{ticker}")
            
            logger.info(f"Added {ticker} to monitoring schedule (every {interval_minutes} minutes)")
    
    def remove_ticker(self, ticker: str):
        """Remove a ticker from monitoring schedule"""
        if ticker in self.monitored_tickers:
            self.monitored_tickers.remove(ticker)
            
            # Cancel scheduled jobs for this ticker
            schedule.clear(f"ticker_{ticker}")
            
            logger.info(f"Removed {ticker} from monitoring schedule")
    
    def _schedule_ticker_analysis(self, ticker: str):
        """Schedule analysis for a specific ticker"""
        asyncio.create_task(self._run_ticker_analysis(ticker))
    
    async def _run_ticker_analysis(self, ticker: str):
        """Run analysis for a specific ticker"""
        try:
            logger.info(f"Running scheduled analysis for {ticker}")
            snapshots = await automated_pipeline.process_ticker_news(ticker)
            
            if snapshots:
                logger.info(f"Processed {len(snapshots)} new articles for {ticker}")
            else:
                logger.debug(f"No new articles found for {ticker}")
                
        except Exception as e:
            logger.error(f"Error in scheduled analysis for {ticker}: {e}")
    
    def start_scheduler(self):
        """Start the scheduler"""
        self.is_running = True
        logger.info("News scheduler started")
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("News scheduler stopped")
    
    def get_status(self) -> Dict:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "monitored_tickers": self.monitored_tickers,
            "scheduled_jobs": len(schedule.jobs),
            "next_run": str(schedule.next_run()) if schedule.jobs else None
        }

class TriggerBasedProcessor:
    """Process news based on trigger events"""
    
    def __init__(self):
        self.price_check_intervals = [1, 24]  # Hours after publication
        
    async def process_news_trigger(self, ticker: str, article_url: str, 
                                 published_time: datetime) -> bool:
        """Process a single news article trigger"""
        try:
            # Wait for price impact window
            await self._wait_for_price_impact(published_time)
            
            # Process the specific article
            snapshots = await automated_pipeline.process_ticker_news(ticker)
            
            # Filter for the specific article
            relevant_snapshots = [
                s for s in snapshots 
                if article_url in getattr(s, 'source_url', '')
            ]
            
            if relevant_snapshots:
                logger.info(f"Processed triggered article for {ticker}: {article_url}")
                return True
            else:
                logger.warning(f"No snapshot created for triggered article: {article_url}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing news trigger for {ticker}: {e}")
            return False
    
    async def _wait_for_price_impact(self, published_time: datetime):
        """Wait for sufficient time to measure price impact"""
        now = datetime.now()
        time_since_publication = (now - published_time).total_seconds() / 3600  # Hours
        
        # Wait at least 1 hour after publication
        if time_since_publication < 1:
            wait_time = (1 - time_since_publication) * 3600  # Convert to seconds
            logger.info(f"Waiting {wait_time/60:.1f} minutes for price impact window")
            await asyncio.sleep(wait_time)

class NewsWebhookHandler:
    """Handle webhook notifications for new articles"""
    
    def __init__(self, scheduler: NewsScheduler, processor: TriggerBasedProcessor):
        self.scheduler = scheduler
        self.processor = processor
        
    async def handle_news_webhook(self, webhook_data: Dict) -> Dict:
        """Handle incoming news webhook"""
        try:
            ticker = webhook_data.get('ticker', '').upper()
            article_url = webhook_data.get('url', '')
            published_time = datetime.fromisoformat(
                webhook_data.get('published_time', datetime.now().isoformat())
            )
            
            if not ticker or not article_url:
                return {"success": False, "error": "Missing ticker or URL"}
            
            # Process immediately if ticker is monitored
            if ticker in self.scheduler.monitored_tickers:
                success = await self.processor.process_news_trigger(
                    ticker, article_url, published_time
                )
                
                return {
                    "success": success,
                    "ticker": ticker,
                    "processed": success,
                    "message": f"Processed article for {ticker}" if success else "Failed to process article"
                }
            else:
                return {
                    "success": False,
                    "ticker": ticker,
                    "processed": False,
                    "message": f"Ticker {ticker} not in monitoring list"
                }
                
        except Exception as e:
            logger.error(f"Error handling news webhook: {e}")
            return {"success": False, "error": str(e)}

class MarketHoursScheduler:
    """Schedule news processing based on market hours"""
    
    def __init__(self, scheduler: NewsScheduler):
        self.scheduler = scheduler
        self.market_open_time = "09:30"  # EST
        self.market_close_time = "16:00"  # EST
        
    def setup_market_hours_schedule(self):
        """Setup schedules based on market hours"""
        
        # More frequent monitoring during market hours
        schedule.every().monday.at(self.market_open_time).do(
            self._start_intensive_monitoring
        ).tag("market_hours")
        
        schedule.every().tuesday.at(self.market_open_time).do(
            self._start_intensive_monitoring
        ).tag("market_hours")
        
        schedule.every().wednesday.at(self.market_open_time).do(
            self._start_intensive_monitoring
        ).tag("market_hours")
        
        schedule.every().thursday.at(self.market_open_time).do(
            self._start_intensive_monitoring
        ).tag("market_hours")
        
        schedule.every().friday.at(self.market_open_time).do(
            self._start_intensive_monitoring
        ).tag("market_hours")
        
        # Reduce monitoring frequency after market close
        schedule.every().monday.at(self.market_close_time).do(
            self._start_light_monitoring
        ).tag("market_hours")
        
        schedule.every().tuesday.at(self.market_close_time).do(
            self._start_light_monitoring
        ).tag("market_hours")
        
        schedule.every().wednesday.at(self.market_close_time).do(
            self._start_light_monitoring
        ).tag("market_hours")
        
        schedule.every().thursday.at(self.market_close_time).do(
            self._start_light_monitoring
        ).tag("market_hours")
        
        schedule.every().friday.at(self.market_close_time).do(
            self._start_light_monitoring
        ).tag("market_hours")
        
        logger.info("Market hours schedule configured")
    
    def _start_intensive_monitoring(self):
        """Start intensive monitoring during market hours"""
        logger.info("Starting intensive monitoring (market hours)")
        # Clear existing schedules and add more frequent ones
        for ticker in self.scheduler.monitored_tickers:
            schedule.clear(f"ticker_{ticker}")
            schedule.every(15).minutes.do(
                self.scheduler._schedule_ticker_analysis, ticker
            ).tag(f"ticker_{ticker}")
    
    def _start_light_monitoring(self):
        """Start light monitoring after market hours"""
        logger.info("Starting light monitoring (after hours)")
        # Clear existing schedules and add less frequent ones
        for ticker in self.scheduler.monitored_tickers:
            schedule.clear(f"ticker_{ticker}")
            schedule.every(60).minutes.do(
                self.scheduler._schedule_ticker_analysis, ticker
            ).tag(f"ticker_{ticker}")

# Global instances
news_scheduler = NewsScheduler()
trigger_processor = TriggerBasedProcessor()
webhook_handler = NewsWebhookHandler(news_scheduler, trigger_processor)
market_scheduler = MarketHoursScheduler(news_scheduler)

def start_news_monitoring(tickers: List[str], interval_minutes: int = 30):
    """Start monitoring for a list of tickers"""
    for ticker in tickers:
        news_scheduler.add_ticker(ticker, interval_minutes)
    
    # Setup market hours scheduling
    market_scheduler.setup_market_hours_schedule()
    
    # Start the scheduler in a separate thread
    import threading
    scheduler_thread = threading.Thread(target=news_scheduler.start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info(f"Started news monitoring for {len(tickers)} tickers")

def stop_news_monitoring():
    """Stop all news monitoring"""
    news_scheduler.stop_scheduler()
    logger.info("Stopped news monitoring")

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        tickers = sys.argv[1].split(',')
        start_news_monitoring(tickers)
        
        try:
            # Keep the script running
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            stop_news_monitoring()
    else:
        print("Usage: python news_scheduler.py AAPL,TSLA,MSFT")
