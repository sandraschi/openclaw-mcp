@echo off
REM openclaw-mcp start - webapp API (5181) and webapp dev server (5180)
REM Run from repo root. Kills existing processes on 5181/5180, then opens two windows.

cd /d "%~dp0\.."
set PYTHONPATH=%CD%\src

REM Kill zombies on 5181 and 5180 so we don't port-hop. Wait after kill so OS releases ports.
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5181"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5180"') do taskkill /PID %%a /F 2>nul
timeout /t 2 /nobreak >nul

echo Starting webapp API (port 5181)...
start "openclaw-mcp API" cmd /k "set PYTHONPATH=%PYTHONPATH% & uvicorn webapp_api.main:app --reload --port 5181 & pause"

timeout /t 2 /nobreak >nul
echo Starting webapp dev server (port 5180)...
start "openclaw-mcp Webapp" cmd /k "cd webapp & npm run dev & pause"

echo API: http://127.0.0.1:5181  Webapp: http://localhost:5180
