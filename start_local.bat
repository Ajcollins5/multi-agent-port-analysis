@echo off
REM Multi-Agent Portfolio Analysis - Local Startup Script (Windows)
REM This script sets up and starts the optimized system locally

echo 🚀 Multi-Agent Portfolio Analysis - Optimized Edition
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed
    pause
    exit /b 1
)

REM Function to show usage
if "%1"=="" goto show_usage
if "%1"=="help" goto show_usage

REM Main script logic
if "%1"=="setup" goto setup_system
if "%1"=="test" goto test_system
if "%1"=="sample" goto run_sample
if "%1"=="frontend" goto start_frontend
if "%1"=="backend" goto start_backend
if "%1"=="both" goto start_both
if "%1"=="clean" goto clean_system

echo ❌ Unknown option: %1
echo.
goto show_usage

:show_usage
echo Usage: %0 [option]
echo.
echo Options:
echo   setup     - Full setup (install dependencies, create .env)
echo   test      - Test optimized system components
echo   sample    - Run sample portfolio analysis
echo   frontend  - Start frontend development server
echo   backend   - Start backend API server
echo   both      - Start both frontend and backend
echo   clean     - Clean up generated files
echo.
echo Examples:
echo   %0 setup     # First time setup
echo   %0 test      # Test optimizations
echo   %0 both      # Start full system
pause
exit /b 0

:setup_system
echo 🔧 Setting up optimized multi-agent system...
python local_test_setup.py
if errorlevel 1 (
    echo ❌ Setup failed
    pause
    exit /b 1
)
echo ✅ Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: %0 test (to verify optimizations)
echo 3. Run: %0 both (to start the system)
pause
exit /b 0

:test_system
call :check_env
echo 🧪 Testing optimized system components...
python test_optimizations.py
pause
exit /b 0

:run_sample
call :check_env
echo 📊 Running sample portfolio analysis...
python local_test_setup.py --sample
pause
exit /b 0

:start_frontend
call :check_env
echo 🌐 Starting frontend development server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop
cd frontend
npm run dev
exit /b 0

:start_backend
call :check_env
echo ⚙️ Starting backend API server...
echo API will be available at: http://localhost:8000
echo Press Ctrl+C to stop

REM Set environment for local development
set ENVIRONMENT=development
set DEBUG=true

REM Start the API server
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
exit /b 0

:start_both
call :check_env
echo 🚀 Starting both frontend and backend...
echo.
echo This will start:
echo   - Frontend at http://localhost:3000
echo   - Backend at http://localhost:8000
echo.
echo Press Ctrl+C to stop

REM Start backend in new window
start "Backend API" cmd /k "cd api && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
cd frontend
npm run dev
exit /b 0

:clean_system
echo 🧹 Cleaning up generated files...

REM Remove Python cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

REM Remove Node.js cache
if exist "frontend\node_modules\.cache" rd /s /q "frontend\node_modules\.cache"
if exist "frontend\.next" rd /s /q "frontend\.next"

REM Remove logs
del *.log >nul 2>&1
del api\*.log >nul 2>&1

echo ✅ Cleanup completed
pause
exit /b 0

:check_env
if not exist ".env" (
    echo ⚠️  Warning: .env file not found
    echo    Run '%0 setup' first to create the environment file
    echo    Or manually create .env with your API keys
    echo.
)
exit /b 0
