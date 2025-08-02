#!/bin/bash

# Multi-Agent Portfolio Analysis - Local Startup Script
# This script sets up and starts the optimized system locally

echo "🚀 Multi-Agent Portfolio Analysis - Optimized Edition"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  setup     - Full setup (install dependencies, create .env)"
    echo "  test      - Test optimized system components"
    echo "  sample    - Run sample portfolio analysis"
    echo "  frontend  - Start frontend development server"
    echo "  backend   - Start backend API server"
    echo "  both      - Start both frontend and backend"
    echo "  clean     - Clean up generated files"
    echo ""
    echo "Examples:"
    echo "  $0 setup     # First time setup"
    echo "  $0 test      # Test optimizations"
    echo "  $0 both      # Start full system"
}

# Setup function
setup_system() {
    echo "🔧 Setting up optimized multi-agent system..."
    
    # Run the setup script
    python3 local_test_setup.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Setup completed successfully!"
        echo ""
        echo "📋 Next steps:"
        echo "1. Edit .env file with your API keys"
        echo "2. Run: $0 test (to verify optimizations)"
        echo "3. Run: $0 both (to start the system)"
    else
        echo "❌ Setup failed"
        exit 1
    fi
}

# Test function
test_system() {
    echo "🧪 Testing optimized system components..."
    python3 test_optimizations.py
}

# Sample analysis function
run_sample() {
    echo "📊 Running sample portfolio analysis..."
    python3 local_test_setup.py --sample
}

# Start frontend function
start_frontend() {
    echo "🌐 Starting frontend development server..."
    echo "Frontend will be available at: http://localhost:3000"
    echo "Press Ctrl+C to stop"
    
    cd frontend
    npm run dev
}

# Start backend function
start_backend() {
    echo "⚙️ Starting backend API server..."
    echo "API will be available at: http://localhost:8000"
    echo "Press Ctrl+C to stop"
    
    # Set environment for local development
    export ENVIRONMENT=development
    export DEBUG=true
    
    # Start the API server
    cd api
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# Start both frontend and backend
start_both() {
    echo "🚀 Starting both frontend and backend..."
    echo ""
    echo "This will start:"
    echo "  - Frontend at http://localhost:3000"
    echo "  - Backend at http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop both servers"
    
    # Start backend in background
    start_backend &
    BACKEND_PID=$!
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start frontend in foreground
    start_frontend
    
    # Kill backend when frontend stops
    kill $BACKEND_PID 2>/dev/null
}

# Clean function
clean_system() {
    echo "🧹 Cleaning up generated files..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -name "*.pyc" -delete 2>/dev/null
    
    # Remove Node.js cache
    rm -rf frontend/node_modules/.cache 2>/dev/null
    rm -rf frontend/.next 2>/dev/null
    
    # Remove logs
    rm -f *.log 2>/dev/null
    rm -f api/*.log 2>/dev/null
    
    echo "✅ Cleanup completed"
}

# Check if .env file exists and warn if not
check_env() {
    if [ ! -f ".env" ]; then
        echo "⚠️  Warning: .env file not found"
        echo "   Run '$0 setup' first to create the environment file"
        echo "   Or manually create .env with your API keys"
        echo ""
    fi
}

# Main script logic
case "$1" in
    "setup")
        setup_system
        ;;
    "test")
        check_env
        test_system
        ;;
    "sample")
        check_env
        run_sample
        ;;
    "frontend")
        check_env
        start_frontend
        ;;
    "backend")
        check_env
        start_backend
        ;;
    "both")
        check_env
        start_both
        ;;
    "clean")
        clean_system
        ;;
    "")
        echo "❌ No option provided"
        echo ""
        show_usage
        exit 1
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
