@echo off
echo Running F1 Calendar Rich Console Display...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Please install Python and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Using system Python.
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import fastf1" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing FastF1 package...
    pip install fastf1
)

python -c "import rich" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Rich package...
    pip install rich
)

python -c "import pandas" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Pandas package...
    pip install pandas
)

REM Run the Rich console display
echo.
echo Running display...
echo.
python rich_display.py

REM Keep the window open
echo.
echo Press any key to exit...
pause >nul 