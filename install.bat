@echo off
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
echo ============================================
echo   Assistive Vision System - Install
echo ============================================
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install -r requirements.txt
echo.
echo Done! Make sure models/cnn_v3_final.h5 exists, then run: run.bat
pause
