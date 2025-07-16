#!/usr/bin/env python3
"""
Run script for Multi-Agent Portfolio Analysis System
Starts the Streamlit web application with proper configuration
"""

import subprocess
import sys
import os

def main():
    """Main function to run the Streamlit app"""
    print("🚀 Starting Multi-Agent Portfolio Analysis System")
    print("=" * 50)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✓ Streamlit found")
    except ImportError:
        print("❌ Streamlit not found. Please install requirements:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ main.py not found. Please ensure you're in the correct directory.")
        sys.exit(1)
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("❌ app.py not found. Please ensure you're in the correct directory.")
        sys.exit(1)
    
    print("✓ All required files found")
    print("🌐 Starting Streamlit server...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("=" * 50)
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 