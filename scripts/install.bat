@echo off
REM clawd-mcp install - pip install from source, npm install in webapp
REM Run from repo root. One-time after clone.

cd /d "%~dp0\.."
echo Installing Python deps (pip install -e .[dev])...
pip install -e ".[dev]"
if errorlevel 1 exit /b 1

echo Installing webapp deps (npm install in webapp/)...
cd webapp
npm install
cd ..
if errorlevel 1 exit /b 1

echo Done. Run scripts\start.bat to start API and webapp.
