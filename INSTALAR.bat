@echo off
title EzOptions Analytics Pro - Instalacao
echo ============================================================
echo           EzOptions Analytics Pro - Instalacao
echo ============================================================
echo.

echo Instalando dependencias necessarias...
echo.

echo [1/3] Instalando Streamlit...
pip install streamlit --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar Streamlit
    pause
    exit /b 1
)

echo [2/3] Instalando Plotly...
pip install plotly --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar Plotly
    pause
    exit /b 1
)

echo [3/3] Instalando Pandas...
pip install pandas --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar Pandas
    pause
    exit /b 1
)

echo.
echo ============================================================
echo               INSTALACAO CONCLUIDA!
echo ============================================================
echo.
echo Agora voce pode executar:
echo   * Clique duplo em START.bat
echo   * Ou execute: python start_dashboard.py
echo.
echo O dashboard abrira automaticamente no navegador!
echo URL: http://localhost:8501
echo.
pause