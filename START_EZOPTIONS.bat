@echo off
title EzOptions Analytics Pro
cls

echo ============================================================
echo              EzOptions Analytics Pro
echo              SISTEMA AUTOMATICO
echo ============================================================
echo.

REM Ir para o diretório do script
cd /d "%~dp0"

REM Instalar dependências se necessário
echo Instalando dependencias necessarias...
python -m pip install --quiet streamlit pandas plotly numpy python-dotenv MetaTrader5

echo.
echo Iniciando sistema...
echo.
echo Dashboard sera aberto em: http://localhost:8502
echo.

REM Definir encoding
set PYTHONIOENCODING=utf-8

REM Iniciar dashboard
streamlit run dashboard_completo.py --server.port 8502

pause