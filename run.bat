@echo off
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
py -3.12 main.py
pause
