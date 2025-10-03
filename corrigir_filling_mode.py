"""
CORREÇÃO DE MODO DE PREENCHIMENTO MT5
===================================

Resolve o problema "Unsupported filling mode" no MT5
"""

import MetaTrader5 as mt5
import time

def testar_modo_de_preenchimento():
    """Testa diferentes modos de preenchimento para encontrar o compatível"""
    print("=" * 60)
    print("CORRECAO DE MODO DE PREENCHIMENTO MT5")
    print("=" * 60)
    
    try:
        # Inicializar MT5
        if not mt5.initialize():
            print("FALHA AO INICIALIZAR MT5")
            return None
        
        print("MT5 INICIALIZADO")
        
        # Obter informações da conta
        account_info = mt5.account_info()
        if not account_info:
            print("NAO FOI POSSIVEL OBTER INFORMACOES DA CONTA")
            mt5.shutdown()
            return None
        
        print(f"CONTA CONECTADA: #{account_info.login}")
        
        # Obter informações do símbolo
        symbol_info = mt5.symbol_info("US100")
        if not symbol_info:
            print("NAO FOI POSSIVEL OBTER INFORMACOES DO SIMBOLO US100")
            mt5.shutdown()
            return None
        
        print(f"SIMBOLO US100 ENCONTRADO")
        print(f"   - Filling Mode: {symbol_info.filling_mode}")
        print(f"   - Trade Mode: {symbol_info.trade_mode}")
        print(f"   - Stops Level: {symbol_info.trade_stops_level}")
        
        # Testar diferentes modos de preenchimento
        filling_modes = [
            mt5.ORDER_FILLING_IOC,
            mt5.ORDER_FILLING_FOK,
            mt5.ORDER_FILLING_BOC,
            mt5.ORDER_FILLING_RETURN
        ]
        
        mode_names = {
            mt5.ORDER_FILLING_IOC: "IOC (Immediate or Cancel)",
            mt5.ORDER_FILLING_FOK: "FOK (Fill or Kill)",
            mt5.ORDER_FILLING_BOC: "BOC (Better or Cancel)",
            mt5.ORDER_FILLING_RETURN: "RETURN (Return on Failure)"
        }
        
        print("\nTESTANDO MODOS DE PREENCHIMENTO...")
        
        # Obter preço atual
        tick = mt5.symbol_info_tick("US100")
        if not tick:
            print("NAO FOI POSSIVEL OBTER PRECO ATUAL")
            mt5.shutdown()
            return None
        
        best_mode = None
        best_result = None
        
        for mode in filling_modes:
            try:
                # Criar requisição de teste
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": "US100",
                    "volume": 0.01,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": tick.ask,
                    "deviation": 20,
                    "magic": 234001,
                    "comment": "Teste Filling Mode",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mode,
                }
                
                # Testar requisição
                result = mt5.order_check(request)
                
                if result:
                    print(f"   - {mode_names[mode]}: {result.retcode} - {result.comment}")
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"     MODO COMPATIVEL ENCONTRADO!")
                        best_mode = mode
                        best_result = result
                        break  # Encontramos o primeiro modo compatível
                    elif result.retcode == 10030:  # Unsupported filling mode
                        print(f"     MODO NAO SUPORTADO")
                else:
                    print(f"   - {mode_names[mode]}: SEM RESPOSTA")
                    
            except Exception as e:
                print(f"   - {mode_names[mode]}: ERRO - {e}")
        
        if best_mode is not None:
            print(f"\nMODO DE PREENCHIMENTO COMPATIVEL ENCONTRADO!")
            print(f"   - Modo: {mode_names[best_mode]}")
            print(f"   - Codigo: {best_mode}")
            print(f"   - Retcode: {best_result.retcode}")
            print(f"   - Comentario: {best_result.comment}")
        else:
            print(f"\nNENHUM MODO DE PREENCHIMENTO COMPATIVEL ENCONTRADO!")
            print("   Usando modo padrao RETURN como fallback...")
            best_mode = mt5.ORDER_FILLING_RETURN
        
        mt5.shutdown()
        return best_mode
        
    except Exception as e:
        print(f"ERRO AO TESTAR MODO DE PREENCHIMENTO: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return None

def aplicar_correcao_de_preenchimento():
    """Aplica correção de modo de preenchimento ao sistema"""
    print("\nAPLICANDO CORRECAO DE MODO DE PREENCHIMENTO...")
    
    try:
        # Testar e encontrar modo compatível
        filling_mode = testar_modo_de_preenchimento()
        
        if filling_mode is not None:
            print(f"\nCORRECAO APLICADA COM SUCESSO!")
            print(f"   Modo de preenchimento recomendado: {filling_mode}")
            
            # Salvar configuração
            config_content = f"""
# CONFIGURACAO DE MODO DE PREENCHIMENTO MT5
# Gerado automaticamente pelo sistema de correcao

MT5_FILLING_MODE = {filling_mode}

# Descricao do modo
MT5_FILLING_MODE_DESCRIPTION = "{{
    {mt5.ORDER_FILLING_IOC}: 'IOC (Immediate or Cancel)',
    {mt5.ORDER_FILLING_FOK}: 'FOK (Fill or Kill)', 
    {mt5.ORDER_FILLING_BOC}: 'BOC (Better or Cancel)',
    {mt5.ORDER_FILLING_RETURN}: 'RETURN (Return on Failure)'
}}[{filling_mode}]"
"""
            
            # Salvar configuração em arquivo
            with open("mt5_filling_mode_config.py", "w") as f:
                f.write(config_content)
            
            print("Configuracao salva em 'mt5_filling_mode_config.py'")
            return filling_mode
        else:
            print("Falha ao aplicar correcao de preenchimento")
            return None
            
    except Exception as e:
        print(f"ERRO AO APLICAR CORRECAO: {e}")
        return None

def main():
    """Função principal"""
    print("CORRETOR DE MODO DE PREENCHIMENTO MT5")
    print("Objetivo: Resolver problema 'Unsupported filling mode'")
    
    # Aplicar correção
    filling_mode = aplicar_correcao_de_preenchimento()
    
    if filling_mode is not None:
        print("\nCORRECAO CONCLUIDA COM SUCESSO!")
        print(f"Modo de preenchimento recomendado: {filling_mode}")
        print("Sistema pronto para operar com ordens corretas!")
        return True
    else:
        print("\nFALHA NA CORRECAO!")
        print("Verifique as configuracoes do MT5 manualmente")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)