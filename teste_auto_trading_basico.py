"""
TESTE DE AUTO TRADING MT5 BASICO
================================

Script minimalista para verificar se Auto Trading esta funcionando
"""

import MetaTrader5 as mt5
import time

def teste_basico_auto_trading():
    """Teste basico de Auto Trading"""
    print("=" * 50)
    print("TESTE BASICO DE AUTO TRADING MT5")
    print("=" * 50)
    
    try:
        # 1. INICIALIZAR MT5
        print("1. INICIALIZANDO MT5...")
        if not mt5.initialize():
            print("FALHA AO INICIALIZAR MT5")
            return False
        
        print("MT5 INICIALIZADO")
        
        # 2. VERIFICAR INFORMACOES DA CONTA
        print("\n2. VERIFICANDO INFORMACOES DA CONTA...")
        account_info = mt5.account_info()
        if not account_info:
            print("NAO FOI POSSIVEL OBTER INFORMACOES DA CONTA")
            mt5.shutdown()
            return False
        
        print(f"CONTA CONECTADA: #{account_info.login}")
        print(f"SALDO: ${account_info.balance:.2f}")
        print(f"EQUITY: ${account_info.equity:.2f}")
        print(f"FREE MARGIN: ${account_info.margin_free:.2f}")
        print(f"TRADE EXPERT (AUTO TRADING): {account_info.trade_expert}")
        print(f"TRADE ALLOWED: {account_info.trade_allowed}")
        
        # 3. VERIFICAR AUTO TRADING
        print("\n3. VERIFICANDO STATUS DO AUTO TRADING...")
        if account_info.trade_expert and account_info.trade_allowed:
            print("AUTO TRADING HABILITADO!")
        else:
            print("AUTO TRADING DESATIVADO!")
            print("\nSOLUCAO NECESSARIA:")
            print("1. ABRA O MT5 MANUALMENTE")
            print("2. VA EM FERRAMENTAS -> OPCOES -> EXPERT ADVISORS")
            print("3. MARQUE 'PERMITIR TRADING AUTOMATICO'")
            print("4. DESMARQUE 'DESATIVAR TODOS OS EXPERT ADVISORS'")
            print("5. REINICIE O MT5")
            mt5.shutdown()
            return False
        
        # 4. VERIFICAR SIMBOLO
        print("\n4. VERIFICANDO SIMBOLO US100...")
        symbol_info = mt5.symbol_info("US100")
        if not symbol_info:
            print("SIMBOLO US100 NAO ENCONTRADO")
            mt5.shutdown()
            return False
        
        print("SIMBOLO US100 ENCONTRADO")
        print(f"   - Nome: {symbol_info.name}")
        print(f"   - Visivel: {symbol_info.visible}")
        print(f"   - Trade Mode: {symbol_info.trade_mode}")
        print(f"   - Filling Mode: {symbol_info.filling_mode}")
        
        # 5. VERIFICAR TICK ATUAL
        print("\n5. VERIFICANDO TICK ATUAL...")
        tick = mt5.symbol_info_tick("US100")
        if not tick:
            print("NAO FOI POSSIVEL OBTER TICK")
            mt5.shutdown()
            return False
        
        print("TICK OBTIDO")
        print(f"   - Bid: ${tick.bid:.2f}")
        print(f"   - Ask: ${tick.ask:.2f}")
        print(f"   - Last: ${tick.last:.2f}")
        
        # 6. TESTAR ORDEM SIMULADA COM MODO PADRAO
        print("\n6. TESTANDO ORDEM SIMULADA...")
        
        # Usar o modo de preenchimento padrao do simbolo
        filling_mode = symbol_info.filling_mode
        print(f"   - Filling Mode do simbolo: {filling_mode}")
        
        # Tentar diferentes modos de preenchimento
        filling_modes_to_try = [
            mt5.ORDER_FILLING_RETURN,  # Modo padrao mais compativel
            mt5.ORDER_FILLING_IOC,     # Immediate or Cancel
            mt5.ORDER_FILLING_FOK,     # Fill or Kill
            mt5.ORDER_FILLING_BOC      # Better or Cancel
        ]
        
        # Mapear modos para nomes legiveis
        mode_names = {
            mt5.ORDER_FILLING_RETURN: "RETURN",
            mt5.ORDER_FILLING_IOC: "IOC",
            mt5.ORDER_FILLING_FOK: "FOK",
            mt5.ORDER_FILLING_BOC: "BOC"
        }
        
        best_mode = None
        best_result = None
        
        for mode in filling_modes_to_try:
            try:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": "US100",
                    "volume": 0.01,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": tick.ask,
                    "deviation": 20,
                    "magic": 234001,
                    "comment": f"Teste {mode_names[mode]}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mode,
                }
                
                result = mt5.order_check(request)
                if result:
                    print(f"   - {mode_names[mode]}: Retcode {result.retcode} - {result.comment}")
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"     MODO COMPATIVEL ENCONTRADO: {mode_names[mode]}")
                        best_mode = mode
                        best_result = result
                        break
                    elif result.retcode == 10030:  # Unsupported filling mode
                        print(f"     MODO NAO SUPORTADO: {mode_names[mode]}")
                else:
                    print(f"   - {mode_names[mode]}: SEM RESPOSTA")
                    
            except Exception as e:
                print(f"   - {mode_names[mode]}: ERRO - {e}")
        
        if best_mode is not None:
            print(f"\nMODO COMPATIVEL ENCONTRADO: {mode_names[best_mode]}")
            print("AUTO TRADING ESTA FUNCIONANDO!")
        else:
            print(f"\nNENHUM MODO COMPATIVEL ENCONTRADO!")
            print("VERIFICAR CONFIGURACOES DO MT5:")
            print("   - Expert Advisors -> Permitir trading automatico")
            print("   - Expert Advisors -> Desativar todos os Expert Advisors (desmarcar)")
            mt5.shutdown()
            return False
        
        # 7. VERIFICAR POSICOES ATUAIS
        print("\n7. VERIFICANDO POSICOES ATUAIS...")
        positions = mt5.positions_get()
        if positions:
            print(f"POSICOES ABERTAS: {len(positions)}")
            for pos in positions:
                pos_type = "BUY" if pos.type == 0 else "SELL"
                print(f"   - #{pos.ticket}: {pos.symbol} {pos_type} {pos.volume} @ {pos.price_open:.2f} (Profit: ${pos.profit:.2f})")
        else:
            print("NENHUMA POSICAO ABERTA")
        
        # 8. VERIFICAR ORDENS PENDENTES
        print("\n8. VERIFICANDO ORDENS PENDENTES...")
        orders = mt5.orders_get()
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
        print("\n" + "=" * 50)
        print("TESTE CONCLUIDO COM SUCESSO!")
        print("AUTO TRADING HABILITADO E FUNCIONANDO!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\nERRO NO TESTE: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def main():
    """Funcao principal"""
    print("TESTE DE AUTO TRADING MT5 BASICO")
    print("Objetivo: Verificar se Auto Trading esta funcionando")
    
    success = teste_basico_auto_trading()
    
    if success:
        print("\nTUDO CERTO!")
        print("AUTO TRADING HABILITADO")
        print("SISTEMA PRONTO PARA OPERAR")
    else:
        print("\nPROBLEMAS DETECTADOS!")
        print("AUTO TRADING DESATIVADO OU COM ERROS")
        print("VERIFIQUE AS CONFIGURACOES DO MT5")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)