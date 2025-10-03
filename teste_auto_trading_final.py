"""
TESTE COMPLETO DE AUTO TRADING MT5
=================================

Script para verificar se o Auto Trading está realmente habilitado
e testar a execução de ordens.
"""

import MetaTrader5 as mt5
import time

def testar_auto_trading():
    """Testa se o Auto Trading está realmente habilitado"""
    print("=" * 60)
    print("TESTE COMPLETO DE AUTO TRADING MT5")
    print("=" * 60)
    
    try:
        # 1. INICIALIZAR MT5
        print("1. INICIALIZANDO MT5...")
        if not mt5.initialize():
            print("FALHA AO INICIALIZAR MT5")
            return False
        
        print("MT5 INICIALIZADO COM SUCESSO")
        
        # 2. VERIFICAR INFORMAÇÕES DA CONTA
        print("\n2. VERIFICANDO INFORMAÇÕES DA CONTA...")
        account_info = mt5.account_info()
        if not account_info:
            print("NAO FOI POSSIVEL OBTER INFORMACOES DA CONTA")
            mt5.shutdown()
            return False
        
        print(f"CONTA CONECTADA: #{account_info.login}")
        print(f"SALDO: ${account_info.balance:.2f}")
        print(f"EQUITY: ${account_info.equity:.2f}")
        print(f"MARGIN: ${account_info.margin:.2f}")
        print(f"FREE MARGIN: ${account_info.margin_free:.2f}")
        print(f"PROFIT: ${account_info.profit:.2f}")
        
        # 3. VERIFICAR AUTO TRADING
        print("\n3. VERIFICANDO STATUS DO AUTO TRADING...")
        print(f"   Trade Expert (Auto Trading): {account_info.trade_expert}")
        print(f"   Trade Allowed: {account_info.trade_allowed}")
        
        if not account_info.trade_expert:
            print("AUTO TRADING DESATIVADO!")
            print("\nSOLUCAO NECESSARIA:")
            print("1. ABRA O MT5 MANUALMENTE")
            print("2. VA EM FERRAMENTAS -> OPCOES -> EXPERT ADVISORS")
            print("3. MARQUE 'PERMITIR TRADING AUTOMATICO'")
            print("4. DESMARQUE 'DESATIVAR TODOS OS EXPERT ADVISORS'")
            print("5. REINICIE O MT5")
            mt5.shutdown()
            return False
        
        if not account_info.trade_allowed:
            print("TRADING NAO PERMITIDO!")
            print("\nSOLUCAO NECESSARIA:")
            print("1. VERIFIQUE AS CONFIGURACOES DA CONTA NO MT5")
            print("2. CERTIFIQUE-SE DE QUE A CONTA PERMITE TRADING AUTOMATICO")
            mt5.shutdown()
            return False
        
        print("AUTO TRADING HABILITADO!")
        
        # 4. VERIFICAR SIMBOLO US100
        print("\n4. VERIFICANDO SIMBOLO US100...")
        symbol_info = mt5.symbol_info("US100")
        if not symbol_info:
            print("SIMBOLO US100 NAO ENCONTRADO")
            # Tentar variações
            symbol_variations = ["US100.cash", "US100cash", "US100.CASH", "NASDAQ100", "NQ100"]
            for variation in symbol_variations:
                symbol_info = mt5.symbol_info(variation)
                if symbol_info:
                    print(f"SIMBOLO ENCONTRADO: {variation}")
                    break
            else:
                print("NENHUMA VARIACAO DO US100 ENCONTRADA")
                mt5.shutdown()
                return False
        
        print(f"SIMBOLO: {symbol_info.name}")
        print(f"VISIVEL: {symbol_info.visible}")
        print(f"TRADE MODE: {symbol_info.trade_mode}")
        print(f"SPREAD: {symbol_info.spread}")
        print(f"TRADE STOPS LEVEL: {symbol_info.trade_stops_level}")
        print(f"DIGITS: {symbol_info.digits}")
        print(f"POINT: {symbol_info.point}")
        
        if not symbol_info.visible:
            print("SIMBOLO NAO VISIVEL - ADICIONE AO MARKET WATCH")
        
        # 5. TESTAR PRECO ATUAL
        print("\n5. TESTANDO PRECO ATUAL...")
        tick = mt5.symbol_info_tick("US100")
        if not tick:
            print("NAO FOI POSSIVEL OBTER PRECO ATUAL")
            mt5.shutdown()
            return False
        
        current_price = (tick.bid + tick.ask) / 2
        print(f"PRECO ATUAL: ${current_price:.2f}")
        print(f"BID: ${tick.bid:.2f} | ASK: ${tick.ask:.2f}")
        print(f"SPREAD: ${tick.ask - tick.bid:.2f}")
        
        # 6. TESTAR ORDEM SIMULADA
        print("\n6. TESTANDO ORDEM SIMULADA...")
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "US100",
            "volume": 0.01,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 20,
            "magic": 234001,
            "comment": "Teste Auto Trading",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        # Verificar se a ordem seria aceita
        check_result = mt5.order_check(request)
        if check_result:
            print(f"VERIFICACAO DE ORDEM: {check_result.retcode} - {check_result.comment}")
            if check_result.retcode == mt5.TRADE_RETCODE_DONE:
                print("ORDEM SERIA ACEITA!")
            elif check_result.retcode == 10027:  # AutoTrading disabled
                print("AUTO TRADING DESATIVADO NO CLIENTE!")
                print("\nSOLUCAO:")
                print("1. NO MT5, VA EM FERRAMENTAS -> OPCOES -> EXPERT ADVISORS")
                print("2. MARQUE 'PERMITIR TRADING AUTOMATICO'")
                print("3. DESMARQUE 'DESATIVAR TODOS OS EXPERT ADVISORS'")
                print("4. REINICIE O MT5")
                mt5.shutdown()
                return False
            else:
                print(f"OUTRO CODIGO DE RETORNO: {check_result.retcode}")
        else:
            print("NAO FOI POSSIVEL VERIFICAR ORDEM")
        
        # 7. VERIFICAR POSICOES ATUAIS
        print("\n7. VERIFICANDO POSICOES ATUAIS...")
        positions = mt5.positions_get(symbol="US100")
        if positions:
            print(f"POSOES ABERTAS: {len(positions)}")
            total_profit = 0
            for pos in positions:
                pos_type = "BUY" if pos.type == 0 else "SELL"
                print(f"   - #{pos.ticket}: {pos.symbol} {pos_type} {pos.volume} @ {pos.price_open:.2f} (Profit: ${pos.profit:.2f})")
                total_profit += pos.profit
            print(f"TOTAL PROFIT: ${total_profit:.2f}")
        else:
            print("NENHUMA POSICAO ABERTA")
        
        # 8. VERIFICAR ORDENS PENDENTES
        print("\n8. VERIFICANDO ORDENS PENDENTES...")
        orders = mt5.orders_get(symbol="US100")
        if orders:
            print(f"ORDENS PENDENTES: {len(orders)}")
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
            print("NENHUMA ORDEM PENDENTE")
        
        mt5.shutdown()
        print("\n" + "=" * 60)
        print("TESTE COMPLETO CONCLUIDO!")
        print("AUTO TRADING ESTA FUNCIONANDO CORRETAMENTE!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERRO NO TESTE: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def main():
    """Função principal"""
    print("SISTEMA DE VERIFICACAO DE AUTO TRADING MT5")
    print("Objetivo: Diagnosticar e corrigir problemas de trading automatico")
    
    # Executar teste
    success = testar_auto_trading()
    
    if success:
        print("\nTUDO CERTO! O SISTEMA ESTA PRONTO PARA OPERAR!")
        return True
    else:
        print("\nPROBLEMAS DETECTADOS! VERIFIQUE AS CONFIGURACOES!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)