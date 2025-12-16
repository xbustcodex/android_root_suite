@echo off
echo Setting up Android Root Suite development environment...
echo.

REM Check Python version
python --version
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Install development requirements if requested
set /p dev="Install development tools? (y/n): "
if /i "%dev%"=="y" (
    echo Installing development tools...
    pip install -r requirements-dev.txt
    pre-commit install
)

echo.
echo Setup complete!
echo.
echo To activate the virtual environment:
echo   venv\Scripts\activate.bat
echo.
echo To run the application:
echo   python main.py
pause
