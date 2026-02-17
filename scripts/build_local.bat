@echo off
setlocal

set VENV_DIR=.venv
set SCRIPT_PATH=kicad-presence.py

if not exist "%SCRIPT_PATH%" (
  echo ERROR: Could not find %SCRIPT_PATH%
  exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
  py -m venv "%VENV_DIR%"
  if errorlevel 1 exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 exit /b 1

python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

pip install -r requirements.txt
if errorlevel 1 exit /b 1

pyinstaller --onefile --noconsole --name KiCadPresence "%SCRIPT_PATH%"
if errorlevel 1 exit /b 1

echo Build complete: dist\KiCadPresence.exe
