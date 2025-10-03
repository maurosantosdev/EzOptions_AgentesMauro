@echo off
echo ================================================
echo 🚀 INICIANDO SISTEMA LUCRATIVO OTIMIZADO
echo ================================================
echo.
echo ✨ Sistema com 14 agentes + IA avançada
echo 📊 Configurações ultra-conservadoras
echo 🛡️ Proteção máxima contra perdas
echo 💰 Foco em lucros consistentes
echo.
echo ================================================
echo.

REM Verificar se o Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não encontrado!
    echo 📦 Instale o Python 3.8 ou superior
    pause
    exit /b 1
)

REM Verificar se o arquivo principal existe
if not exist "sistema_completo_14_agentes.py" (
    echo ❌ ERRO: Arquivo sistema_completo_14_agentes.py não encontrado!
    pause
    exit /b 1
)

echo ✅ Arquivos verificados com sucesso!
echo.
echo 🚀 Iniciando sistema lucrativo...
echo 📈 Aguardando operações de alta qualidade...
echo 🛡️ Sistema de proteção ativado...
echo.

REM Iniciar o sistema
python sistema_completo_14_agentes.py

echo.
echo ================================================
echo ✅ Sistema encerrado
echo ================================================
pause