#!/usr/bin/env python3
"""
Security Definer Views Fix Script
Applies the security fix for SECURITY DEFINER views in Supabase database.
"""

import os
import sys
import psycopg2
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_supabase_connection() -> Optional[psycopg2.extensions.connection]:
    """
    Get connection to Supabase database using environment variables.
    
    Expected environment variables:
    - SUPABASE_URL: Your Supabase project URL
    - SUPABASE_SERVICE_ROLE_KEY: Service role key for database access
    - DATABASE_URL: Direct database connection string (alternative)
    """
    try:
        # Try direct database URL first
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            logger.info("Connecting using DATABASE_URL...")
            return psycopg2.connect(database_url)
        
        # Try Supabase connection parameters
        supabase_url = os.getenv('SUPABASE_URL')
        service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not service_role_key:
            logger.error("Missing required environment variables:")
            logger.error("Need either DATABASE_URL or both SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
            return None
        
        # Extract connection details from Supabase URL
        # Format: https://project-ref.supabase.co
        project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')
        
        # Build connection string
        conn_string = f"postgresql://postgres:{service_role_key}@{project_ref}.supabase.co:5432/postgres"
        
        logger.info(f"Connecting to Supabase project: {project_ref}")
        return psycopg2.connect(conn_string)
        
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def read_sql_file(file_path: str) -> str:
    """Read SQL file content."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Failed to read SQL file {file_path}: {e}")
        return ""

def apply_security_fix(conn: psycopg2.extensions.connection) -> bool:
    """
    Apply the security fix by running the SQL script.
    
    Args:
        conn: Database connection
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the SQL fix file
        sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'api', 'database', 'fix_security_definer_views.sql')
        sql_content = read_sql_file(sql_file_path)
        
        if not sql_content:
            logger.error("Could not read SQL fix file")
            return False
        
        # Execute the SQL script
        cursor = conn.cursor()
        
        logger.info("Applying security fix...")
        cursor.execute(sql_content)
        conn.commit()
        
        logger.info("✅ Security fix applied successfully!")
        
        # Test the views
        logger.info("Testing new views...")
        
        test_queries = [
            "SELECT COUNT(*) FROM public.system_health",
            "SELECT COUNT(*) FROM public.portfolio_summary", 
            "SELECT COUNT(*) FROM public.recent_insights"
        ]
        
        for query in test_queries:
            try:
                cursor.execute(query)
                result = cursor.fetchone()
                view_name = query.split('FROM ')[1].split('.')[1]
                logger.info(f"✅ {view_name} view is working (returned {result[0] if result else 0} rows)")
            except Exception as e:
                logger.error(f"❌ Error testing view: {e}")
                return False
        
        cursor.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply security fix: {e}")
        return False

def main():
    """Main function to run the security fix."""
    logger.info("🔧 Starting Security Definer Views Fix...")
    
    # Get database connection
    conn = get_supabase_connection()
    if not conn:
        logger.error("❌ Could not connect to database")
        sys.exit(1)
    
    try:
        # Apply the fix
        if apply_security_fix(conn):
            logger.info("🎉 Security fix completed successfully!")
            logger.info("📋 Next steps:")
            logger.info("1. Test your application to ensure everything works")
            logger.info("2. Run Supabase linter again to verify warnings are gone")
            logger.info("3. Monitor database performance")
        else:
            logger.error("❌ Security fix failed")
            sys.exit(1)
            
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main() 