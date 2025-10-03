@echo off
title Dashboard EzOptions - Sistema de Agentes em Tempo Real

echo ============================================================
echo 🚀 DASHBOARD EZOPTIONS - SISTEMA DE AGENTES EM TEMPO REAL
echo ============================================================
echo Autor: EzOptions Team
echo Data: %DATE% %TIME%
echo ============================================================

:: Verificar se Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado!
    echo Por favor, instale o Node.js em https://nodejs.org/
    pause
    exit /b 1
)

:: Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo Por favor, instale o Python em https://python.org/
    pause
    exit /b 1
)

echo ✅ Dependências verificadas com sucesso!

:: Criar diretórios se não existirem
if not exist "logs" mkdir logs
if not exist "data" mkdir data

echo 📁 Diretórios criados com sucesso!

:: Instalar dependências do backend
echo 📦 Instalando dependências do backend...
cd /d "%~dp0"
npm install > logs\backend-install.log 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências do backend
    type logs\backend-install.log
    pause
    exit /b 1
)
echo ✅ Backend instalado com sucesso!

:: Instalar dependências do frontend
echo 📦 Instalando dependências do frontend...
cd client
npm install > ..\logs\frontend-install.log 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências do frontend
    type ..\logs\frontend-install.log
    pause
    exit /b 1
)
cd ..

echo ✅ Frontend instalado com sucesso!

:: Construir frontend
echo 🏗️  Construindo frontend...
cd client
npm run build > ..\logs\frontend-build.log 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro ao construir frontend
    type ..\logs\frontend-build.log
    pause
    exit /b 1
)
cd ..

echo ✅ Frontend construído com sucesso!

:: Copiar build para pasta pública
echo 📂 Copiando build para pasta pública...
xcopy /E /I /Y client\build public > logs\copy-build.log 2>&1

echo ✅ Build copiado para pasta pública!

:: Iniciar servidores
echo 🚀 Iniciando servidores...

:: Iniciar servidor backend em segundo plano
start "Backend Server" /MIN cmd /c "node server.js > logs\backend-server.log 2>&1"
echo ✅ Servidor backend iniciado na porta 3001 (WebSocket na porta 3002)

:: Aguardar um momento para o servidor iniciar
timeout /t 3 /nobreak >nul

:: Abrir navegador
echo 🌐 Abrindo dashboard no navegador...
start "" "http://localhost:3001"

echo ============================================================
echo 🎉 DASHBOARD INICIADO COM SUCESSO!
echo ============================================================
echo 📊 Acesse: http://localhost:3001
echo 📡 WebSocket: ws://localhost:3002
echo 📝 Logs: Pasta "logs"
echo ============================================================

:: Manter janela aberta
echo.
echo Pressione qualquer tecla para encerrar...
pause >nul

:: Encerrar processos
echo 🛑 Encerrando servidores...
taskkill /FI "WINDOWTITLE eq Backend Server*" /F >nul 2>&1

echo ✅ Servidores encerrados com sucesso!
echo 👋 Até a próxima!