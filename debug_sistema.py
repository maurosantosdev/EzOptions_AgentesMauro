#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de depuração para entender por que os agentes não estão negociando
"""

import sys
import os
import MetaTrader5 as mt5
from datetime import datetime
import pytz
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def testar_conexao_basica():
    """Testar conexão básica com o MT5"""
    print("=== TESTE DE CONEXÃO BÁSICA ===")
    
    # Verificar credenciais
    login = os.getenv("MT5_LOGIN")
    server = os.getenv("MT5_SERVER")
    password = os.getenv("MT5_PASSWORD")
    
    print(f"Login: {login}")
    print(f"Server: {server}")
    print(f"Senha configurada: {'Sim' if password else 'Não'}")
    
    if not all([login, server, password]):
        print("❌ Credenciais não configuradas corretamente!")
        return False
    
    # Tentar conexão
    try:
        # Fechar conexão anterior se existir
        mt5.shutdown()
    except:
        pass
    
    if not mt5.initialize():
        print("❌ Falha na inicialização do MT5")
        return False
    
    print("✅ MT5 inicializado")
    
    if not mt5.login(int(login), password, server):
        print("❌ Falha no login")
        return False
    
    print("✅ Login realizado com sucesso")
    
    # Testar informações da conta
    account_info = mt5.account_info()
    if not account_info:
        print("❌ Não foi possível obter informações da conta")
        return False
    
    print(f"✅ Conta: {account_info.login} - Saldo: ${account_info.balance:.2f}")
    print(f"✅ Servidor: {account_info.server}")
    
    return True

def testar_simbolo():
    """Testar símbolo US100"""
    print("\n=== TESTE DE SÍMBOLO ===")
    
    symbol = "US100"
    
    # Verificar informações do símbolo
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"❌ Símbolo {symbol} não encontrado")
        print("Tentando outros nomes...")
        
        # Tentar variações comuns
        symbols_to_try = [
            "US100", "US100.cash", "US100cash", "US100.CASH", 
            "NASDAQ100", "NQ100", "USTEC", "USATECH", "US-100"
        ]
        
        for sym in symbols_to_try:
            sym_info = mt5.symbol_info(sym)
            if sym_info:
                print(f"✅ Símbolo encontrado: {sym}")
                symbol = sym
                symbol_info = sym_info
                break
        else:
            print("❌ Nenhum símbolo relacionado encontrado")
            return False
    
    print(f"✅ Símbolo: {symbol_info.name}")
    print(f"✅ Visível: {symbol_info.visible}")
    print(f"✅ Trade mode: {symbol_info.trade_mode}")
    print(f"✅ Point: {symbol_info.point}")
    print(f"✅ Stops level: {symbol_info.trade_stops_level}")
    
    if not symbol_info.visible:
        print("⚠️  Aviso: Símbolo não está visível no Market Watch")
        print("   Adicione o símbolo ao Market Watch no MT5")
    
    return symbol_info

def testar_preco_atual():
    """Testar obtenção de preço atual"""
    print("\n=== TESTE DE PREÇO ATUAL ===")
    
    symbol = "US100"  # ou o símbolo encontrado no teste anterior
    
    # Tentar obter tick
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print(f"❌ Não foi possível obter tick para {symbol}")
        return None
    
    print(f"✅ Preço atual: {tick.last}")
    print(f"✅ Bid: {tick.bid}")
    print(f"✅ Ask: {tick.ask}")
    print(f"✅ Volume: {tick.volume}")
    
    return tick

def testar_hora_trading():
    """Verificar se é horário de trading"""
    print("\n=== VERIFICAÇÃO DE HORÁRIO DE TRADING ===")
    
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz)
    current_time = now_ny.time()
    
    print(f"Horário atual (NY): {current_time}")
    print(f"Dia da semana (NY): {now_ny.weekday()} (0=Segunda, 6=Domingo)")
    
    # Verificar se é fim de semana
    if now_ny.weekday() > 4:  # 5=Sábado, 6=Domingo
        print("❌ Fim de semana - mercado fechado")
        return False
    
    # Horário de negociação (ajustado para horário NY)
    market_open = datetime.time(9, 30)   # 9:30 AM NY
    market_close = datetime.time(16, 0)  # 4:00 PM NY
    
    if market_open <= current_time <= market_close:
        print("✅ Horário de trading - mercado aberto")
        return True
    else:
        print("❌ Fora do horário de trading")
        return False

def testar_ordem_simulada():
    """Testar execução de ordem simulada"""
    print("\n=== TESTE DE ORDEM SIMULADA ===")
    
    symbol = "US100"
    
    # Obter informações atuais
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print("❌ Não foi possível obter preço para teste de ordem")
        return False
    
    # Testar modo de preenchimento
    filling_modes = [
        mt5.ORDER_FILLING_RETURN,
        mt5.ORDER_FILLING_IOC,
        mt5.ORDER_FILLING_FOK,
        mt5.ORDER_FILLING_BOC
    ]
    
    for mode in filling_modes:
        try:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": 0.01,
                "type": mt5.ORDER_TYPE_BUY,
                "price": tick.ask,
                "deviation": 20,
                "magic": 888888,
                "comment": "Teste",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mode,
            }
            
            # Testar apenas a verificação, não executar
            check_result = mt5.order_check(request)
            if check_result:
                print(f"✅ Modo {mode}: Retcode {check_result.retcode} - {check_result.comment}")
                if check_result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"   - Ordem seria aceita com este modo: {mode}")
            else:
                print(f"❌ Modo {mode}: Resultado None - possível problema de conexão")
                
        except Exception as e:
            print(f"❌ Modo {mode}: Erro - {e}")
    
    return True

def main():
    """Função principal de depuração"""
    print("[DEBUG] INICIANDO SCRIPT DE DEPURACAO")
    print("[DEBUG] Identificando por que os agentes nao estao negociando")
    
    try:
        # 1. Testar conexão básica
        if not testar_conexao_basica():
            print("\n💥 Falha crítica na conexão - verifique credenciais e MT5")
            return
        
        # 2. Testar símbolo
        symbol_info = testar_simbolo()
        if not symbol_info:
            print("\n💥 Símbolo não encontrado - verifique nome e disponibilidade")
            return
        
        # 3. Testar preço
        tick = testar_preco_atual()
        if not tick:
            print("\n💥 Não foi possível obter preço - verifique conexão")
            return
        
        # 4. Verificar horário
        trading_hour = testar_hora_trading()
        print(f"   Horário de trading: {trading_hour}")
        
        # 5. Testar ordens
        testar_ordem_simulada()
        
        print("\n[RESULTADO] TESTES CONCLUIDOS")
        print("\n[RESUMO]:")
        print(f"   - Conexao: OK")
        print(f"   - Simbolo: {'OK' if symbol_info else 'NOK'}")
        print(f"   - Preco: {'OK' if tick else 'NOK'}")
        print(f"   - Horario: {'OK' if trading_hour else 'NOK'}")
        
        print("\n[ANALISE] POSSIVEIS CAUSAS DO PROBLEMA:")
        
        if not trading_hour:
            print("   1. Fora do horario de trading")
        
        if not symbol_info.visible:
            print("   2. Simbolo nao esta visivel no Market Watch (adicione no MT5)")
        
        if symbol_info.trade_stops_level == 0:
            print("   3. Stops level e 0 - verifique configuracoes do simbolo")
        
        print("   4. Configuracoes de confianca muito altas nos agentes")
        print("   5. Sistema de protecao de circuit breaker ativado")
        print("   6. Modo de preenchimento incompativel")
        print("   7. Analise de mercado nao esta gerando sinais suficientes")
        
        print("\n[SOLUCOES] SOLUCOES SUGERIDAS:")
        print("   - Verifique se o simbolo esta no Market Watch do MT5")
        print("   - Confirme que esta dentro do horario de trading")
        print("   - Verifique as configuracoes de confianca (min_confidence)")
        print("   - Execute os sistemas em ordem: emergency_stop_loss.py, sistema_lucro_final.py")
        
    except Exception as e:
        print(f"\n💥 Erro durante depuração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()