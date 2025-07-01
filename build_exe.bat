@echo off

REM The Script should take about 7 Minutes to run
REM This script is designed to build the Bar Loader application for Windows.

REM Author: JonesCKevin
REM Simple Windows batch script to build Bar Loader

echo === Bar Loader Windows Build Script ===
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8 or later.
    pause
    exit /b 1
)

echo Python found.

REM Check if main script exists
if not exist "run-gui_Qt6.py" (
    echo Error: run-gui_Qt6.py not found in current directory.
    echo Please run this script from the Bar Loader directory.
    pause
    exit /b 1
)

echo Main script found.

REM Install/upgrade required packages
echo Installing required packages...
pip install --upgrade pyinstaller PyQt6 Pillow

REM You could also just do a requirements.txt install if it's nearby
REM pip install -r requirements.txt

REM Check if PyInstaller, pillow, and PyQt6 are installed
python -c "import PyInstaller, PyQt6, PIL" >nul 2>&1
if errorlevel 1 (
    echo Error: Required packages not found. Please ensure PyInstaller, PyQt6, and Pillow are installed.
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "BarLoader.spec" del "BarLoader.spec"

REM Build the application

echo Building application...
python -m PyInstaller --onefile --windowed ^
    --name "BarLoader" ^
    --clean ^
    --noconfirm ^
    --icon "resources/Galaxy.ico" ^
    --add-data "data;data" ^
    --add-data "resources;resources" ^
    --add-data "BarBellWeights;BarBellWeights" ^
    "run-gui_Qt6.py"

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo === Build Complete ===
echo Your application has been built in the 'dist' folder.
echo Run 'dist\BarLoader\BarLoader.exe' to test it.
echo.
pause
