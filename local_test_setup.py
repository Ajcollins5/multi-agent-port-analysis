#!/usr/bin/env python3
"""
Local Testing Setup for Optimized Multi-Agent Portfolio Analysis System
Run this script to set up and test the system locally
"""

import os
import sys
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalTestSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.api_dir = self.root_dir / "api"
        self.frontend_dir = self.root_dir / "frontend"
        self.env_file = self.root_dir / ".env"
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        logger.info("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 9):
            logger.error("❌ Python 3.9+ required")
            return False
        logger.info("✅ Python version OK")
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Node.js not found")
                return False
            logger.info(f"✅ Node.js version: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("❌ Node.js not installed")
            return False
        
        # Check if requirements.txt exists
        if not (self.root_dir / "requirements.txt").exists():
            logger.error("❌ requirements.txt not found")
            return False
        logger.info("✅ requirements.txt found")
        
        # Check if frontend package.json exists
        if not (self.frontend_dir / "package.json").exists():
            logger.error("❌ frontend/package.json not found")
            return False
        logger.info("✅ frontend/package.json found")
        
        return True
    
    def setup_environment(self) -> bool:
        """Setup environment variables for local testing"""
        logger.info("🔧 Setting up environment...")
        
        if self.env_file.exists():
            logger.info("✅ .env file already exists")
            return True
        
        # Create basic .env file for local testing
        env_content = """# Local Testing Environment for Multi-Agent Portfolio Analysis
# This is a minimal setup for local testing

# AI Configuration (Required for full functionality)
XAI_API_KEY=your_xai_api_key_here

# Email Configuration (Optional for local testing)
SENDER_EMAIL=test@example.com
SENDER_PASSWORD=test_password
TO_EMAIL=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Local Development Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true

# Performance Optimization Settings
CACHE_ENABLED=true
PARALLEL_EXECUTION=true
CIRCUIT_BREAKER_ENABLED=true
MONITORING_ENABLED=true
MAX_WORKERS=4
CACHE_TTL=300

# Portfolio Configuration
DEFAULT_PORTFOLIO=AAPL,GOOGL,MSFT,AMZN,TSLA
HIGH_VOLATILITY_THRESHOLD=0.05
MEDIUM_VOLATILITY_THRESHOLD=0.02

# Database (Optional - will use SQLite if not configured)
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
# POSTGRES_URL=postgresql://user:password@host:port/database

# Security
API_SECRET_KEY=local_testing_secret_key
CRON_SECRET=local_cron_secret
"""
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            logger.info("✅ Created .env file for local testing")
            logger.warning("⚠️  Please edit .env file with your actual API keys for full functionality")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create .env file: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python and Node.js dependencies"""
        logger.info("📦 Installing dependencies...")
        
        # Install Python dependencies
        try:
            logger.info("Installing Python dependencies...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], cwd=self.root_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Failed to install Python dependencies: {result.stderr}")
                return False
            logger.info("✅ Python dependencies installed")
        except Exception as e:
            logger.error(f"❌ Error installing Python dependencies: {e}")
            return False
        
        # Install Node.js dependencies
        try:
            logger.info("Installing Node.js dependencies...")
            result = subprocess.run([
                "npm", "install"
            ], cwd=self.frontend_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Failed to install Node.js dependencies: {result.stderr}")
                return False
            logger.info("✅ Node.js dependencies installed")
        except Exception as e:
            logger.error(f"❌ Error installing Node.js dependencies: {e}")
            return False
        
        return True
    
    async def test_optimized_system(self) -> bool:
        """Test the optimized multi-agent system"""
        logger.info("🚀 Testing optimized multi-agent system...")
        
        try:
            # Add the root directory to Python path for api imports
            sys.path.insert(0, str(self.root_dir))
            
            # Test basic imports
            logger.info("Testing imports...")
            
            # Test optimized components
            from api.agents.optimized_agent_coordinator import OptimizedAgentCoordinator
            from api.agents.enhanced_risk_agent import EnhancedRiskAgent
            from api.agents.optimized_supervisor import OptimizedSupervisor
            from api.monitoring.agent_performance_monitor import AgentPerformanceMonitor
            from api.utils.cache_manager import default_cache
            from api.utils.circuit_breaker import yfinance_circuit_breaker
            
            logger.info("✅ All optimized components imported successfully")
            
            # Test agent coordinator
            logger.info("Testing OptimizedAgentCoordinator...")
            coordinator = OptimizedAgentCoordinator(max_workers=2)
            
            # Test enhanced risk agent
            logger.info("Testing EnhancedRiskAgent...")
            risk_agent = EnhancedRiskAgent()
            
            # Test performance monitor
            logger.info("Testing AgentPerformanceMonitor...")
            monitor = AgentPerformanceMonitor()
            await monitor.start_monitoring()
            
            # Test cache system
            logger.info("Testing cache system...")
            await default_cache.set("test_key", {"test": "data"}, ttl=60)
            cached_data = await default_cache.get("test_key")
            if cached_data:
                logger.info("✅ Cache system working")
            else:
                logger.warning("⚠️  Cache system may have issues")
            
            # Test circuit breaker
            logger.info("Testing circuit breaker...")
            stats = yfinance_circuit_breaker.get_stats()
            logger.info(f"✅ Circuit breaker initialized: {stats['name']}")
            
            # Test optimized supervisor
            logger.info("Testing OptimizedSupervisor...")
            supervisor = OptimizedSupervisor()
            
            # Stop monitoring
            await monitor.stop_monitoring()
            
            logger.info("🎉 All optimized components tested successfully!")
            return True
            
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            logger.error("Make sure all dependencies are installed")
            return False
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return False
    
    async def run_sample_analysis(self) -> bool:
        """Run a sample portfolio analysis"""
        logger.info("📊 Running sample portfolio analysis...")
        
        try:
            sys.path.insert(0, str(self.root_dir))
            
            from api.agents.optimized_supervisor import OptimizedSupervisor
            from api.monitoring.agent_performance_monitor import agent_performance_monitor
            
            # Start monitoring
            await agent_performance_monitor.start_monitoring()
            
            # Create supervisor
            supervisor = OptimizedSupervisor()
            
            # Run sample analysis
            logger.info("Running optimized analysis for AAPL...")
            result = await supervisor.orchestrate_parallel_analysis(
                ticker="AAPL",
                analysis_type="comprehensive"
            )
            
            if result.get("success"):
                execution_time = result.get("execution_time", 0)
                logger.info(f"✅ Analysis completed successfully in {execution_time:.2f}s")
                
                # Show performance metrics
                perf_metrics = result.get("performance_metrics", {})
                if perf_metrics:
                    logger.info(f"📈 Parallel efficiency: {perf_metrics.get('parallel_efficiency', 0):.1f}x")
                    logger.info(f"📊 Success rate: {perf_metrics.get('success_rate', 0):.1f}%")
                
                # Show agent results
                agent_results = result.get("agent_results", {})
                for agent, agent_result in agent_results.items():
                    if agent_result.get("success"):
                        exec_time = agent_result.get("execution_time", 0)
                        logger.info(f"  ✅ {agent}: {exec_time:.2f}s")
                    else:
                        error = agent_result.get("error", "Unknown error")
                        logger.warning(f"  ⚠️  {agent}: {error}")
                
                return True
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"❌ Analysis failed: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Sample analysis failed: {e}")
            return False
        finally:
            try:
                await agent_performance_monitor.stop_monitoring()
            except:
                pass
    
    def start_frontend(self) -> bool:
        """Start the frontend development server"""
        logger.info("🌐 Starting frontend development server...")
        
        try:
            logger.info("Frontend will start at http://localhost:3000")
            logger.info("Press Ctrl+C to stop the frontend server")
            
            # Start frontend in development mode
            subprocess.run([
                "npm", "run", "dev"
            ], cwd=self.frontend_dir)
            
            return True
        except KeyboardInterrupt:
            logger.info("Frontend server stopped")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            return False
    
    def show_usage_instructions(self):
        """Show usage instructions"""
        logger.info("\n" + "="*60)
        logger.info("🎉 LOCAL TESTING SETUP COMPLETE!")
        logger.info("="*60)
        logger.info("\n📋 NEXT STEPS:")
        logger.info("1. Edit .env file with your API keys (especially XAI_API_KEY)")
        logger.info("2. For Supabase integration, add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        logger.info("3. Run the frontend: cd frontend && npm run dev")
        logger.info("4. Access the application at http://localhost:3000")
        logger.info("\n🚀 TESTING COMMANDS:")
        logger.info("- Test optimizations: python local_test_setup.py --test")
        logger.info("- Run sample analysis: python local_test_setup.py --sample")
        logger.info("- Start frontend: python local_test_setup.py --frontend")
        logger.info("\n📊 MONITORING:")
        logger.info("- Performance metrics will be logged during execution")
        logger.info("- Check console output for optimization results")
        logger.info("- Monitor cache hit rates and parallel efficiency")
        logger.info("\n⚠️  NOTES:")
        logger.info("- Some features require valid API keys (XAI, Supabase)")
        logger.info("- Local testing uses simplified configurations")
        logger.info("- For production deployment, use Vercel with full environment setup")

async def main():
    """Main function to run local testing setup"""
    setup = LocalTestSetup()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Local Testing Setup for Multi-Agent Portfolio Analysis")
    parser.add_argument("--test", action="store_true", help="Test optimized system components")
    parser.add_argument("--sample", action="store_true", help="Run sample portfolio analysis")
    parser.add_argument("--frontend", action="store_true", help="Start frontend development server")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    
    args = parser.parse_args()
    
    # If specific action requested, run it
    if args.test:
        success = await setup.test_optimized_system()
        sys.exit(0 if success else 1)
    
    if args.sample:
        success = await setup.run_sample_analysis()
        sys.exit(0 if success else 1)
    
    if args.frontend:
        success = setup.start_frontend()
        sys.exit(0 if success else 1)
    
    # Full setup process
    logger.info("🚀 Starting Local Testing Setup for Optimized Multi-Agent System")
    
    # Check prerequisites
    if not setup.check_prerequisites():
        logger.error("❌ Prerequisites check failed")
        sys.exit(1)
    
    # Setup environment
    if not setup.setup_environment():
        logger.error("❌ Environment setup failed")
        sys.exit(1)
    
    # Install dependencies
    if not args.skip_deps:
        if not setup.install_dependencies():
            logger.error("❌ Dependency installation failed")
            sys.exit(1)
    
    # Test optimized system
    if not await setup.test_optimized_system():
        logger.error("❌ System testing failed")
        sys.exit(1)
    
    # Show usage instructions
    setup.show_usage_instructions()

if __name__ == "__main__":
    asyncio.run(main())
