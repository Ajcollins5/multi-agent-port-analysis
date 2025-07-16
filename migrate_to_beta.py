#!/usr/bin/env python3
"""
Migration script for Multi-Agent Portfolio Analysis System
Migrates from single-user to multi-user beta schema with optimizations
"""

import sqlite3
import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handle database migration from single-user to multi-user schema"""
    
    def __init__(self, db_path: str = "knowledge.db"):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_backup(self):
        """Create backup of current database"""
        try:
            if os.path.exists(self.db_path):
                import shutil
                shutil.copy2(self.db_path, self.backup_path)
                logger.info(f"Database backed up to: {self.backup_path}")
                return True
            else:
                logger.warning(f"Database file not found: {self.db_path}")
                return False
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def check_current_schema(self) -> Dict[str, bool]:
        """Check current database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_status = {
            'insights': 'insights' in tables,
            'users': 'users' in tables,
            'portfolios': 'portfolios' in tables,
            'insights_new': 'insights_new' in tables,
            'api_usage': 'api_usage' in tables,
            'query_cache': 'query_cache' in tables
        }
        
        conn.close()
        
        logger.info(f"Current schema status: {schema_status}")
        return schema_status
    
    def create_beta_schema(self):
        """Create beta schema tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                subscription_tier TEXT DEFAULT 'free',
                api_quota_used INTEGER DEFAULT 0,
                api_quota_limit INTEGER DEFAULT 100,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create portfolios table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                portfolio_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                tickers TEXT NOT NULL,
                risk_tolerance TEXT DEFAULT 'moderate',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create enhanced insights table
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
                processing_time REAL DEFAULT 0.0,
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
                ticker TEXT,
                tokens_used INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                response_time REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create query cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_cache (
                cache_key TEXT PRIMARY KEY,
                query_type TEXT NOT NULL,
                parameters TEXT,
                result TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                hit_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id TEXT PRIMARY KEY,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_insights_user_id ON insights_new(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_insights_ticker ON insights_new(ticker)",
            "CREATE INDEX IF NOT EXISTS idx_insights_timestamp ON insights_new(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_expires ON query_cache(expires_at)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        
        logger.info("Beta schema created successfully")
    
    def migrate_existing_data(self):
        """Migrate existing data to new schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if old insights table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='insights'")
        if not cursor.fetchone():
            logger.info("No existing insights table found, skipping migration")
            conn.close()
            return
        
        # Create default user for existing data
        default_user_id = "default_user"
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, email, subscription_tier, api_quota_limit)
            VALUES (?, ?, ?, ?, ?)
        ''', (default_user_id, "default_user", "default@example.com", "legacy", 1000))
        
        # Create default portfolio
        default_portfolio_id = "default_portfolio"
        cursor.execute('''
            INSERT OR IGNORE INTO portfolios (portfolio_id, user_id, name, tickers, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (default_portfolio_id, default_user_id, "Legacy Portfolio", '["AAPL"]', "Migrated from single-user system"))
        
        # Migrate existing insights
        cursor.execute('SELECT ticker, insight, timestamp FROM insights')
        old_insights = cursor.fetchall()
        
        migrated_count = 0
        for ticker, insight, timestamp in old_insights:
            insight_id = f"migrated_{hashlib.md5(f'{ticker}:{insight}:{timestamp}'.encode()).hexdigest()}"
            
            # Estimate tokens used (rough calculation)
            tokens_used = len(insight.split()) + 50  # Base tokens for system message
            
            cursor.execute('''
                INSERT OR IGNORE INTO insights_new 
                (insight_id, user_id, portfolio_id, ticker, insight, source_agent, tokens_used, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (insight_id, default_user_id, default_portfolio_id, ticker, insight, "legacy", tokens_used, timestamp))
            
            migrated_count += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"Migrated {migrated_count} existing insights to new schema")
    
    def add_sample_data(self):
        """Add sample data for testing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add sample users
        sample_users = [
            ("user_sample1", "john_doe", "john@example.com", "premium", 500),
            ("user_sample2", "jane_smith", "jane@example.com", "free", 100),
            ("user_sample3", "bob_wilson", "bob@example.com", "enterprise", 2000)
        ]
        
        for user_id, username, email, tier, quota in sample_users:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, email, subscription_tier, api_quota_limit)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, email, tier, quota))
        
        # Add sample portfolios
        sample_portfolios = [
            ("portfolio_tech", "user_sample1", "Tech Stocks", '["AAPL", "GOOGL", "MSFT"]', "Technology focused portfolio"),
            ("portfolio_div", "user_sample1", "Dividend Stocks", '["KO", "PG", "JNJ"]', "Dividend growth portfolio"),
            ("portfolio_growth", "user_sample2", "Growth Stocks", '["TSLA", "NVDA", "AMZN"]', "High growth potential"),
            ("portfolio_mixed", "user_sample3", "Balanced Portfolio", '["AAPL", "TSLA", "KO", "MSFT"]', "Balanced risk portfolio")
        ]
        
        for portfolio_id, user_id, name, tickers, description in sample_portfolios:
            cursor.execute('''
                INSERT OR IGNORE INTO portfolios (portfolio_id, user_id, name, tickers, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (portfolio_id, user_id, name, tickers, description))
        
        # Add sample API usage data
        sample_usage = [
            ("usage_1", "user_sample1", "analyze_ticker", "AAPL", 150, 0.0015, 1.2),
            ("usage_2", "user_sample1", "portfolio_analysis", None, 300, 0.0030, 2.5),
            ("usage_3", "user_sample2", "analyze_ticker", "TSLA", 120, 0.0012, 0.8),
            ("usage_4", "user_sample3", "batch_analysis", None, 500, 0.0050, 3.1)
        ]
        
        for usage_id, user_id, endpoint, ticker, tokens, cost, response_time in sample_usage:
            cursor.execute('''
                INSERT OR IGNORE INTO api_usage 
                (usage_id, user_id, endpoint, ticker, tokens_used, cost, response_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (usage_id, user_id, endpoint, ticker, tokens, cost, response_time))
        
        conn.commit()
        conn.close()
        
        logger.info("Sample data added successfully")
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify migration was successful"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count records in each table
        verification = {}
        
        tables = ['users', 'portfolios', 'insights_new', 'api_usage', 'query_cache']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            verification[table] = count
        
        # Check if old insights table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='insights'")
        has_old_table = cursor.fetchone() is not None
        
        if has_old_table:
            cursor.execute("SELECT COUNT(*) FROM insights")
            verification['insights_old'] = cursor.fetchone()[0]
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        verification['indexes'] = len([idx for idx in indexes if idx.startswith('idx_')])
        
        conn.close()
        
        logger.info(f"Migration verification: {verification}")
        return verification
    
    def cleanup_old_data(self):
        """Clean up old data after successful migration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Rename old table instead of dropping (safer)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='insights'")
        if cursor.fetchone():
            cursor.execute("ALTER TABLE insights RENAME TO insights_old_backup")
            logger.info("Old insights table renamed to insights_old_backup")
        
        conn.commit()
        conn.close()
    
    def run_migration(self, include_sample_data: bool = True):
        """Run complete migration process"""
        logger.info("Starting database migration to beta schema")
        
        # Step 1: Create backup
        if not self.create_backup():
            logger.error("Backup failed, aborting migration")
            return False
        
        # Step 2: Check current schema
        schema_status = self.check_current_schema()
        
        # Step 3: Create beta schema
        self.create_beta_schema()
        
        # Step 4: Migrate existing data
        self.migrate_existing_data()
        
        # Step 5: Add sample data (optional)
        if include_sample_data:
            self.add_sample_data()
        
        # Step 6: Verify migration
        verification = self.verify_migration()
        
        # Step 7: Cleanup (optional)
        # self.cleanup_old_data()  # Commented out for safety
        
        logger.info("Migration completed successfully")
        logger.info(f"Backup created at: {self.backup_path}")
        logger.info(f"Migration results: {verification}")
        
        return True

def main():
    """Main migration function"""
    print("Multi-Agent Portfolio Analysis System - Database Migration")
    print("=" * 60)
    
    # Initialize migrator
    migrator = DatabaseMigrator()
    
    # Run migration
    success = migrator.run_migration(include_sample_data=True)
    
    if success:
        print("\n✅ Migration completed successfully!")
        print(f"📁 Backup created: {migrator.backup_path}")
        print("\n🔄 Next steps:")
        print("1. Test the new schema with sample data")
        print("2. Update application code to use new tables")
        print("3. Implement user authentication")
        print("4. Deploy optimized caching system")
        print("5. Monitor performance improvements")
        
        print("\n📊 Beta Features Available:")
        print("• Multi-user support with quotas")
        print("• Enhanced portfolio management")
        print("• API usage tracking and cost monitoring")
        print("• Advanced caching and optimization")
        print("• Performance metrics and analytics")
        
    else:
        print("\n❌ Migration failed!")
        print("Check the logs for details")

if __name__ == "__main__":
    main() 