@echo off
echo 🚀 NoticeWala Local Testing Quick Start
echo =====================================
echo.

echo 📋 Step 1: Setting up environment...
if not exist backend\.env (
    echo Creating environment file...
    copy backend\env.example backend\.env
    echo ✅ Environment file created
) else (
    echo ✅ Environment file already exists
)

echo.
echo 📋 Step 2: Starting Docker services...
cd infrastructure
docker-compose up -d postgres redis elasticsearch
echo ✅ Infrastructure services started

echo.
echo 📋 Step 3: Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo 📋 Step 4: Installing Python dependencies...
cd ..\backend
pip install -r requirements.txt
echo ✅ Python dependencies installed

echo.
echo 📋 Step 5: Running database migrations...
alembic upgrade head
echo ✅ Database migrations completed

echo.
echo 📋 Step 6: Starting backend server...
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
