@echo off
title EzOptions Analytics Pro
echo ============================================================
echo           EzOptions Analytics Pro - Dashboard
echo ============================================================
echo.

cd /d "%~dp0"
python start_dashboard.py

echo.
echo Pressione qualquer tecla para sair...
pause >nul