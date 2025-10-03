"""
VERIFICADOR DE AUTO TRADING MT5
==============================

Verifica se o Auto Trading está realmente habilitado no MT5
e se as ordens podem ser executadas.
"""

import MetaTrader5 as mt5
import time

def verificar_auto_trading():
    """Verifica se Auto Trading está habilitado"""
    print("=" * 60)
    print("VERIFICADOR DE AUTO TRADING MT5")
    print("=" * 60)
    
    try:
        # Inicializar MT5
        if not mt5.initialize():
            print("FALHA AO INICIALIZAR MT5")
            return False
        
        print("MT5 INICIALIZADO")
        
        # Verificar informações da conta
        account_info = mt5.account_info()
        if not account_info:
            print("NAO FOI POSSIVEL OBTER INFORMACOES DA CONTA")
            mt5.shutdown()
            return False
        
        print(f"\n=== INFORMACOES DA CONTA ===")
        print(f"Conta: #{account_info.login}")
        print(f"Saldo: ${account_info.balance:.2f}")
        print(f"Equity: ${account_info.equity:.2f}")
        print(f"Trade Expert (Auto Trading): {account_info.trade_expert}")
        print(f"Trade Allowed: {account_info.trade_allowed}")
        
        # Verificar se Auto Trading está habilitado
        if account_info.trade_expert and account_info.trade_allowed:
            print("\nAUTO TRADING HABILITADO!")
            print("SISTEMA PRONTO PARA OPERAR!")
        else:
            print("\nAUTO TRADING DESATIVADO!")
            print("\nSOLUCAO NECESSARIA:")
            print("1. ABRA O MT5 MANUALMENTE")
            print("2. VA EM FERRAMENTAS -> OPCOES -> EXPERT ADVISORS")
            print("3. MARQUE 'PERMITIR TRADING AUTOMATICO'")
            print("4. DESMARQUE 'DESATIVAR TODOS OS EXPERT ADVISORS'")
            print("5. REINICIE O MT5")
            mt5.shutdown()
            return False
        
        # Verificar símbolo US100
        print(f"\n=== VERIFICANDO SIMBOLO US100 ===")
        symbol_info = mt5.symbol_info("US100")
        if not symbol_info:
            print("SIMBOLO US100 NAO ENCONTRADO")
            mt5.shutdown()
            return False
        
        print(f"SIMBOLO US100 ENCONTRADO")
        print(f"   - Nome: {symbol_info.name}")
        print(f"   - Visivel: {symbol_info.visible}")
        print(f"   - Trade Mode: {symbol_info.trade_mode}")
        print(f"   - Filling Mode: {symbol_info.filling_mode}")
        
        # Verificar tick atual
        print(f"\n=== VERIFICANDO TICK ATUAL ===")
        tick = mt5.symbol_info_tick("US100")
        if not tick:
            print("NAO FOI POSSIVEL OBTER TICK ATUAL")
            mt5.shutdown()
            return False
        
        print(f"TICK ATUAL OBTIDO")
        print(f"   - Bid: ${tick.bid:.2f}")
        print(f"   - Ask: ${tick.ask:.2f}")
        print(f"   - Last: ${tick.last:.2f}")
        print(f"   - Volume: {tick.volume}")
        
        # Testar ordem simulada
        print(f"\n=== TESTANDO ORDEM SIMULADA ===")
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
            "type_filling": mt5.ORDER_FILLING_RETURN,  # Modo corrigido
        }
        
        # Verificar se a ordem seria aceita
        check_result = mt5.order_check(request)
        if check_result:
            print(f"VERIFICACAO DE ORDEM REALIZADA")
            print(f"   - Retcode: {check_result.retcode}")
            print(f"   - Comment: {check_result.comment}")
            
            if check_result.retcode == mt5.TRADE_RETCODE_DONE:
                print("ORDEM SERIA ACEITA!")
                print("SISTEMA PRONTO PARA OPERAR!")
                mt5.shutdown()
                return True
            elif check_result.retcode == 10027:  # AutoTrading disabled
                print("AUTO TRADING DESATIVADO NO CLIENTE!")
                print("\nSOLUCAO:")
                print("1. NO MT5, VA EM FERRAMENTAS -> OPCOES -> EXPERT ADVISORS")
                print("2. MARQUE 'PERMITIR TRADING AUTOMATICO'")
                print("3. DESMARQUE 'DESATIVAR TODOS OS EXPERT ADVISORS'")
                print("4. REINICIE O MT5")
                mt5.shutdown()
                return False
            elif check_result.retcode == 10030:  # Unsupported filling mode
                print("MODO DE PREENCHIMENTO NAO SUPORTADO!")
                print("USANDO MODO CORRIGIDO...")
                
                # Tentar com modo FOK (Fill or Kill) que foi identificado como compatível
                request["type_filling"] = mt5.ORDER_FILLING_FOK
                check_result_fok = mt5.order_check(request)
                if check_result_fok and check_result_fok.retcode == mt5.TRADE_RETCODE_DONE:
                    print("ORDEM SERIA ACEITA COM MODO FOK!")
                    print("SISTEMA PRONTO PARA OPERAR COM MODO CORRIGIDO!")
                    mt5.shutdown()
                    return True
                else:
                    print("ORDEM NAO SERIA ACEITA NEM COM MODO FOK!")
                    mt5.shutdown()
                    return False
            else:
                print(f"OUTRO ERRO: {check_result.retcode} - {check_result.comment}")
                mt5.shutdown()
                return False
        else:
            print("NAO FOI POSSIVEL VERIFICAR ORDEM")
            mt5.shutdown()
            return False
            
    except Exception as e:
        print(f"ERRO NA VERIFICACAO: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def main():
    """Função principal"""
    print("VERIFICADOR DE AUTO TRADING MT5")
    print("Objetivo: Garantir que o sistema possa executar ordens")
    
    # Verificar Auto Trading
    success = verificar_auto_trading()
    
    if success:
        print("\nVERIFICACAO CONCLUIDA COM SUCESSO!")
        print("AUTO TRADING HABILITADO")
        print("SISTEMA PRONTO PARA OPERAR")
        print("Agora voce pode iniciar os agentes de trading")
    else:
        print("\nVERIFICACAO CONCLUIDA COM PROBLEMAS!")
        print("AUTO TRADING DESATIVADO OU COM ERROS")
        print("Siga as instrucoes acima para corrigir")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)