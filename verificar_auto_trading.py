"""
VERIFICADOR DE AUTO TRADING MT5
==============================

Este script verifica se o Auto Trading está habilitado no MT5
e fornece instruções para corrigir caso esteja desativado.
"""

import MetaTrader5 as mt5
import os
import sys

def check_auto_trading():
    """Verifica se Auto Trading está habilitado"""
    print("VERIFICANDO AUTO TRADING NO MT5...")
    print("=" * 50)
    
    try:
        # Inicializar MT5
        if not mt5.initialize():
            print("FALHA NA INICIALIZAÇÃO DO MT5")
            return False
        
        print("MT5 INICIALIZADO")
        
        # Obter informações da conta
        account_info = mt5.account_info()
        if not account_info:
            print("NÃO FOI POSSÍVEL OBTER INFORMAÇÕES DA CONTA")
            mt5.shutdown()
            return False
        
        print(f"CONTA CONECTADA: #{account_info.login}")
        print(f"SALDO: ${account_info.balance:.2f}")
        
        # Verificar Auto Trading
        trade_expert = account_info.trade_expert
        trade_allowed = account_info.trade_allowed
        
        print(f"\n=== STATUS DO AUTO TRADING ===")
        print(f"Trade Expert (Auto Trading): {trade_expert}")
        print(f"Trade Allowed: {trade_allowed}")
        
        if trade_expert and trade_allowed:
            print("AUTO TRADING HABILITADO!")
            print("SISTEMA PRONTO PARA OPERAR!")
            mt5.shutdown()
            return True
        else:
            print("AUTO TRADING DESATIVADO!")
            print("\nSOLUÇÃO NECESSÁRIA:")
            print("1. ABRA O MT5 MANUALMENTE")
            print("2. VÁ EM FERRAMENTAS → OPÇÕES → EXPERT ADVISORS")
            print("3. MARQUE 'PERMITIR TRADING AUTOMÁTICO'")
            print("4. DESMARQUE 'DESATIVAR TODOS OS EXPERT ADVISORS'")
            print("5. REINICIE O MT5")
            print("6. EXECUTE ESTE SCRIPT NOVAMENTE")
            
            mt5.shutdown()
            return False
            
    except Exception as e:
        print(f"ERRO NA VERIFICAÇÃO: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def enable_auto_trading_instructions():
    """Fornece instruções detalhadas para habilitar Auto Trading"""
    print("\nINSTRUÇÕES DETALHADAS PARA HABILITAR AUTO TRADING")
    print("=" * 60)
    
    instructions = [
        "1. FECHE O MT5 COMPLETAMENTE (se estiver aberto)",
        "2. ABRA O MT5 NOVAMENTE",
        "3. NO MENU SUPERIOR, CLIQUE EM 'FERRAMENTAS'",
        "4. SELECIONE 'OPÇÕES'",
        "5. NA JANELA QUE ABRIR, CLIQUE EM 'EXPERT ADVISORS'",
        "6. MARQUE A CAIXA 'PERMITIR TRADING AUTOMÁTICO'",
        "7. DESMARQUE A CAIXA 'DESATIVAR TODOS OS EXPERT ADVISORS'",
        "8. CLIQUE EM 'OK'",
        "9. REINICIE O MT5",
        "10. EXECUTE O SISTEMA NOVAMENTE"
    ]
    
    for i, instruction in enumerate(instructions, 1):
        print(f"   {instruction}")
    
    print("\nIMPORTANTE:")
    print("   - O SISTEMA NÃO FUNCIONARÁ SEM AUTO TRADING HABILITADO")
    print("   - SEM AUTO TRADING, NENHUMA ORDEM SERÁ EXECUTADA")
    print("   - MESMO QUE O SISTEMA ANÁLISE O MERCADO CORRETAMENTE")

def main():
    """Função principal"""
    print("VERIFICADOR DE AUTO TRADING MT5")
    print("Objetivo: Garantir que o sistema possa executar ordens")
    print()
    
    # Verificar Auto Trading
    auto_trading_enabled = check_auto_trading()
    
    if auto_trading_enabled:
        print("\nTUDO CERTO! O SISTEMA ESTÁ PRONTO PARA OPERAR!")
        print("Agora você pode iniciar os agentes de trading")
        return True
    else:
        print("\nPROBLEMA DETECTADO: AUTO TRADING DESATIVADO")
        enable_auto_trading_instructions()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)