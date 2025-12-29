@echo off
REM AI Idea to Reality POC - Streamlit Startup Script for Windows

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   I2POC Streamlit - Startup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [+] Python found
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [+] Virtual environment created
) else (
    echo [+] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo [+] Virtual environment activated

REM Check if requirements are installed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo.
    echo [*] Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo [+] Dependencies installed successfully
) else (
    echo [+] Dependencies already installed
)

REM Check if .env file exists
echo.
if not exist ".env" (
    echo WARNING: .env file not found
    if exist ".env.example" (
        echo [*] Creating .env from .env.example...
        copy .env.example .env
        echo [+] .env created from .env.example
        echo [!] Please update .env with your credentials
    ) else (
        echo ERROR: .env.example not found
        pause
        exit /b 1
    )
) else (
    echo [+] .env file found
)

REM Start Streamlit app
echo.
echo ========================================
echo   Starting Streamlit Application...
echo ========================================
echo.
echo Application will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py --logger.level=info

endlocal
pause
