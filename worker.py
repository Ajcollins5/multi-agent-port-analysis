#!/usr/bin/env python3
"""
Background Worker for Multi-Agent Portfolio Analysis
Handles scheduled analysis and background processing for Render deployment
"""

import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Import configuration and core modules
from cloud_config import get_config, get_portfolio_config, get_feature_flags, log_config_status
from main import daily_analysis, analyze_ticker, PORTFOLIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('worker.log') if get_config("ENABLE_LOG_FILE") else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackgroundWorker:
    """Background worker for scheduled analysis"""
    
    def __init__(self):
        self.running = False
        self.last_analysis = None
        self.analysis_count = 0
        self.error_count = 0
        
        # Load configuration
        self.config = get_portfolio_config()
        self.features = get_feature_flags()
        
        logger.info("🚀 Background Worker initialized")
        logger.info(f"Analysis interval: {self.config['analysis_interval']} seconds")
        logger.info(f"Features enabled: {self.features}")
    
    def run_scheduled_analysis(self):
        """Run scheduled portfolio analysis"""
        try:
            logger.info("📊 Starting scheduled portfolio analysis")
            start_time = datetime.now()
            
            # Run daily analysis
            daily_analysis()
            
            # Update statistics
            self.last_analysis = start_time
            self.analysis_count += 1
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Scheduled analysis completed in {duration:.2f} seconds")
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Scheduled analysis failed: {str(e)}")
            
            # Send error notification if enabled
            if self.features["enable_error_notifications"]:
                self.send_error_notification(str(e))
    
    def run_individual_analysis(self, ticker: str):
        """Run analysis for individual ticker"""
        try:
            logger.info(f"🔍 Analyzing ticker: {ticker}")
            analyze_ticker(ticker)
            logger.info(f"✅ Analysis completed for {ticker}")
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {ticker}: {str(e)}")
    
    def health_check(self):
        """Perform health check"""
        try:
            # Check if analysis is running
            if self.last_analysis:
                time_since_last = (datetime.now() - self.last_analysis).total_seconds()
                max_interval = self.config['analysis_interval'] * 2  # Allow 2x interval
                
                if time_since_last > max_interval:
                    logger.warning(f"⚠️ Last analysis was {time_since_last:.0f} seconds ago")
                    return False
            
            # Check error rate
            if self.analysis_count > 0:
                error_rate = self.error_count / self.analysis_count
                if error_rate > 0.5:  # More than 50% errors
                    logger.warning(f"⚠️ High error rate: {error_rate:.2%}")
                    return False
            
            logger.info("✅ Health check passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return False
    
    def send_error_notification(self, error_message: str):
        """Send error notification"""
        try:
            from main import send_email
            
            subject = "🚨 Background Worker Error"
            body = f"""Background Worker Error Report

Error: {error_message}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Count: {self.analysis_count}
Error Count: {self.error_count}
Last Analysis: {self.last_analysis or 'Never'}

Worker Statistics:
- Running: {self.running}
- Error Rate: {self.error_count / max(self.analysis_count, 1):.2%}

Please check the application logs for more details.

---
Multi-Agent Portfolio Analysis Background Worker"""
            
            send_email(subject, body)
            logger.info("📧 Error notification sent")
            
        except Exception as e:
            logger.error(f"❌ Failed to send error notification: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get worker status"""
        return {
            "running": self.running,
            "last_analysis": self.last_analysis.isoformat() if self.last_analysis else None,
            "analysis_count": self.analysis_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.analysis_count, 1),
            "uptime": datetime.now().isoformat(),
            "config": self.config,
            "features": self.features
        }
    
    def run(self):
        """Run the background worker"""
        logger.info("🚀 Starting background worker")
        
        # Validate configuration
        log_config_status()
        
        if not self.features["enable_background_analysis"]:
            logger.warning("⚠️ Background analysis is disabled in configuration")
            return
        
        # Schedule analysis
        interval = self.config['analysis_interval']
        schedule.every(interval).seconds.do(self.run_scheduled_analysis)
        
        # Schedule health checks (every 30 minutes)
        schedule.every(1800).seconds.do(self.health_check)
        
        self.running = True
        logger.info(f"✅ Worker started with {interval}s interval")
        
        # Run initial analysis
        self.run_scheduled_analysis()
        
        # Main worker loop
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("🛑 Worker interrupted by user")
        except Exception as e:
            logger.error(f"❌ Worker crashed: {str(e)}")
            raise
        finally:
            self.running = False
            logger.info("🏁 Worker stopped")

def run_worker():
    """Run the background worker"""
    worker = BackgroundWorker()
    worker.run()

def run_single_analysis(ticker: str = None):
    """Run single analysis for testing"""
    worker = BackgroundWorker()
    
    if ticker is not None:
        worker.run_individual_analysis(ticker)
    else:
        worker.run_scheduled_analysis()

def worker_status():
    """Get worker status for monitoring"""
    worker = BackgroundWorker()
    return worker.get_status()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "run":
            run_worker()
        elif command == "test":
            ticker = sys.argv[2] if len(sys.argv) > 2 else None
            run_single_analysis(ticker)
        elif command == "status":
            status = worker_status()
            import json
            print(json.dumps(status, indent=2))
        else:
            print("Usage:")
            print("  python worker.py run         # Run background worker")
            print("  python worker.py test [TICKER] # Run single analysis")
            print("  python worker.py status      # Get worker status")
    else:
        # Default: run worker
        run_worker() 