@echo off
REM Bananriti Project Setup Script for Windows
REM Sets up the complete development environment

echo ==================================================
echo বানানরীতি (Bananriti) - Project Setup
echo Bangla Spelling Error Correction System
echo ==================================================
echo.

REM Check Python version
echo [1/5] Checking Python version...
python --version
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created at: .\venv
) else (
    echo Virtual environment already exists at: .\venv
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
echo.

REM Install requirements
echo [5/5] Installing dependencies...
pip install -r requirements.txt
echo.

echo ==================================================
echo Setup Complete!
echo ==================================================
echo.
echo To activate the virtual environment:
echo   venv\Scripts\activate
echo.
echo To deactivate:
echo   deactivate
echo.
echo Project structure is ready at:
echo   .\1_Data_Preprocessing\
echo   .\2_Error_Generation\
echo   .\3_Noisy_Channel_Model\
echo   .\4_BanglaT5_Model\
echo   .\5_Evaluation\
echo   .\resources\
echo   .\utils\
echo.
pause
