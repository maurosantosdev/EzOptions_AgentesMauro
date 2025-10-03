@echo off
echo ========================================
echo    DIAGNOSTICO MT5 - EzOptions
echo ========================================
echo.
echo Este arquivo executa um diagnostico completo
echo do MT5 para identificar problemas antes de operar.
echo.
echo Verificando:
echo - Conexao MT5
echo - Informacoes da conta
echo - Simbolo US100
echo - Dados de preco em tempo real
echo - Validacao de ordens
echo - Posicoes e ordens existentes
echo.
pause

python diagnostico_mt5.py

echo.
echo ========================================
echo        DIAGNOSTICO FINALIZADO
echo ========================================
echo.
echo Se todos os testes passaram (✅), o sistema esta OK.
echo Se houver falhas (❌), verifique as recomendacoes acima.
echo.
pause