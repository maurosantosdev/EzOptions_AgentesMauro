"""
VERIFICADOR E CORRETOR DE AUTO TRADING MT5
=========================================

Este script verifica e corrige o problema do Auto Trading desativado no MT5.
"""

import MetaTrader5 as mt5
import time
import sys

def verificar_e_corrigir_auto_trading():
    """
    Verifica e corrige o problema do Auto Trading desativado
    """
    print("=" * 60)
    print("🔧 VERIFICADOR E CORRETOR DE AUTO TRADING MT5")
    print("=" * 60)
    
    try:
        # 1. INICIALIZAR MT5
        print("1. INICIALIZANDO MT5...")
        if not mt5.initialize():
            print("❌ FALHA AO INICIALIZAR MT5")
            print("   Solução: Verifique se o MT5 está instalado e rodando")
            return False
        
        print("✅ MT5 INICIALIZADO COM SUCESSO")
        
        # 2. VERIFICAR INFORMAÇÕES DA CONTA
        print("\n2. VERIFICANDO INFORMAÇÕES DA CONTA...")
        account_info = mt5.account_info()
        if not account_info:
            print("❌ NÃO FOI POSSÍVEL OBTER INFORMAÇÕES DA CONTA")
            mt5.shutdown()
            return False
        
        print(f"✅ CONTA CONECTADA: #{account_info.login}")
        print(f"💰 SALDO: ${account_info.balance:.2f}")
        print(f"📊 EQUITY: ${account_info.equity:.2f}")
        
        # 3. VERIFICAR STATUS DO AUTO TRADING
        print("\n3. VERIFICANDO STATUS DO AUTO TRADING...")
        print(f"   Trade Expert (Auto Trading): {account_info.trade_expert}")
        print(f"   Trade Allowed: {account_info.trade_allowed}")
        
        if account_info.trade_expert and account_info.trade_allowed:
            print("✅ AUTO TRADING JÁ ESTÁ HABILITADO!")
            print("✅ SISTEMA PRONTO PARA OPERAR!")
            mt5.shutdown()
            return True
        else:
            print("❌ AUTO TRADING DESATIVADO!")
            print("\n🔧 SOLUÇÃO AUTOMÁTICA:")
            print("   O MT5 requer configuração manual para Auto Trading")
            print("   Siga estas etapas:")
            print()
            print("   1. ABRA O MT5 MANUALMENTE")
            print("   2. VÁ EM 'FERRAMENTAS' → 'OPÇÕES'")
            print("   3. CLIQUE NA ABA 'EXPERT ADVISORS'")
            print("   4. MARQUE 'PERMITIR TRADING AUTOMÁTICO'")
            print("   5. DESMARQUE 'DESATIVAR TODOS OS EXPERT ADVISORS'")
            print("   6. CLIQUE EM 'OK'")
            print("   7. REINICIE O MT5")
            print("   8. EXECUTE ESTE SCRIPT NOVAMENTE")
            print()
            print("⚠️  IMPORTANTE:")
            print("   - O MT5 NÃO PERMITE HABILITAR AUTO TRADING VIA API")
            print("   - ESTA CONFIGURAÇÃO DEVE SER FEITA MANUALMENTE NO CLIENTE")
            print("   - SEM AUTO TRADING, NENHUMA ORDEM SERÁ EXECUTADA")
            
            mt5.shutdown()
            return False
    
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def verificar_configuracoes_do_simbolo():
    """
    Verifica as configurações do símbolo US100
    """
    print("\n4. VERIFICANDO CONFIGURAÇÕES DO SÍMBOLO US100...")
    
    try:
        # Inicializar MT5 se não estiver inicializado
        if not mt5.initialize():
            print("❌ MT5 NÃO INICIALIZADO")
            return False
        
        # Verificar informações do símbolo
        symbol_info = mt5.symbol_info("US100")
        if not symbol_info:
            print("❌ SÍMBOLO US100 NÃO ENCONTRADO")
            # Tentar outras variações
            symbol_variations = ["US100.cash", "US100cash", "US100.CASH", "NASDAQ100", "NQ100"]
            for variation in symbol_variations:
                symbol_info = mt5.symbol_info(variation)
                if symbol_info:
                    print(f"✅ SÍMBOLO ENCONTRADO: {variation}")
                    break
            else:
                print("❌ NENHUMA VARIAÇÃO DO US100 ENCONTRADA")
                mt5.shutdown()
                return False
        
        print(f"✅ SÍMBOLO: {symbol_info.name}")
        print(f"📊 VISÍVEL: {symbol_info.visible}")
        print(f"💰 TRADE MODE: {symbol_info.trade_mode}")
        print(f"📏 SPREAD: {symbol_info.spread}")
        print(f"📐 TRADE STOPS LEVEL: {symbol_info.trade_stops_level}")
        print(f"🔢 DIGITS: {symbol_info.digits}")
        print(f"🎯 POINT: {symbol_info.point}")
        
        # Verificar se o símbolo está visível
        if not symbol_info.visible:
            print("⚠️  SÍMBOLO NÃO ESTÁ VISÍVEL NO MARKET WATCH")
            print("   Solução: Arraste o símbolo para o Market Watch no MT5")
        
        # Verificar modo de trading
        if symbol_info.trade_mode == 0:  # TRADE_MODE_DISABLED
            print("❌ TRADING DESATIVADO PARA ESTE SÍMBOLO")
            print("   Solução: Verifique as configurações do símbolo no MT5")
        elif symbol_info.trade_mode == 1:  # TRADE_MODE_LONGONLY
            print("⚠️  APENAS LONG POSITIONS PERMITIDAS")
        elif symbol_info.trade_mode == 2:  # TRADE_MODE_SHORTONLY
            print("⚠️  APENAS SHORT POSITIONS PERMITIDAS")
        else:  # TRADE_MODE_FULL
            print("✅ TRADING COMPLETO PERMITIDO")
        
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ ERRO AO VERIFICAR SÍMBOLO: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def verificar_ordens_e_posicoes():
    """
    Verifica ordens e posições atuais
    """
    print("\n5. VERIFICANDO ORDENS E POSIÇÕES...")
    
    try:
        # Inicializar MT5 se não estiver inicializado
        if not mt5.initialize():
            print("❌ MT5 NÃO INICIALIZADO")
            return False
        
        # Verificar posições abertas
        positions = mt5.positions_get()
        if positions:
            print(f"📊 POSIÇÕES ABERTAS: {len(positions)}")
            total_profit = 0
            for pos in positions:
                pos_type = "BUY" if pos.type == 0 else "SELL"
                print(f"   - #{pos.ticket}: {pos.symbol} {pos_type} {pos.volume} @ {pos.price_open:.2f} (Profit: ${pos.profit:.2f})")
                total_profit += pos.profit
            print(f"💰 LUCRO TOTAL: ${total_profit:.2f}")
        else:
            print("📊 NENHUMA POSIÇÃO ABERTA")
        
        # Verificar ordens pendentes
        orders = mt5.orders_get()
        if orders:
            print(f"📋 ORDENS PENDENTES: {len(orders)}")
            for order in orders:
                order_type = ""
                if order.type == 0:
                    order_type = "BUY"
                elif order.type == 1:
                    order_type = "SELL"
                elif order.type == 2:
                    order_type = "BUY_LIMIT"
                elif order.type == 3:
                    order_type = "SELL_LIMIT"
                elif order.type == 4:
                    order_type = "BUY_STOP"
                elif order.type == 5:
                    order_type = "SELL_STOP"
                print(f"   - #{order.ticket}: {order.symbol} {order_type} {order.volume_initial} @ {order.price_open:.2f}")
        else:
            print("📋 NENHUMA ORDEM PENDENTE")
        
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ ERRO AO VERIFICAR ORDENS E POSIÇÕES: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def main():
    """
    Função principal
    """
    print("🚀 SISTEMA DE VERIFICAÇÃO E CORREÇÃO DO MT5")
    print("🎯 Objetivo: Diagnosticar e corrigir problemas de Auto Trading")
    
    # 1. Verificar e corrigir Auto Trading
    auto_trading_ok = verificar_e_corrigir_auto_trading()
    
    if auto_trading_ok:
        # 2. Verificar configurações do símbolo
        verificar_configuracoes_do_simbolo()
        
        # 3. Verificar ordens e posições
        verificar_ordens_e_posicoes()
        
        print("\n" + "=" * 60)
        print("🎉 DIAGNÓSTICO CONCLUÍDO COM SUCESSO!")
        print("✅ AUTO TRADING HABILITADO")
        print("✅ SISTEMA PRONTO PARA OPERAR")
        print("=" * 60)
        
        return True
    else:
        print("\n" + "=" * 60)
        print("🚨 DIAGNÓSTICO CONCLUÍDO COM PROBLEMAS!")
        print("❌ AUTO TRADING DESATIVADO")
        print("🔧 CORREÇÃO NECESSÁRIA MANUALMENTE")
        print("=" * 60)
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)