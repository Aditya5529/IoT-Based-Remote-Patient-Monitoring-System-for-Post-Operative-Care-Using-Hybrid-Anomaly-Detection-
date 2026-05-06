@echo off
echo Starting RPM Vitals Collection System...
start "Backend API" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
start "Frontend UI" cmd /k "cd frontend_new && npm run dev"
echo Both servers are starting up!
echo Backend will be available at http://localhost:8000/docs
echo Frontend will be available at http://localhost:5173
