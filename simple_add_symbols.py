#!/usr/bin/env python3
import MetaTrader5 as mt5
import os

def adicionar_ativos():
    print("ADICIONANDO ATIVOS NO MT5")
    print("=" * 40)

    # Inicializar MT5
    if not mt5.initialize():
        print("ERRO: Nao foi possivel inicializar MT5")
        return False

    # Login
    login = int(os.getenv('MT5_LOGIN', '103486755'))
    server = os.getenv('MT5_SERVER', 'FBS-Demo')
    password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')

    if not mt5.login(login, password, server):
        print("ERRO: Falha no login MT5")
        mt5.shutdown()
        return False

    print("MT5 conectado com sucesso")

    # Ativos para adicionar (símbolos encontrados na FBS-Demo)
    simbolos = ['US100', 'US500', 'US30', 'DE30']  # Símbolos confirmados disponíveis

    print(f"\nTentando adicionar {len(simbolos)} ativos...")
    print("=" * 40)

    adicionados = 0

    for simbolo in simbolos:
        try:
            # Verificar se existe
            symbol_info = mt5.symbol_info(simbolo)

            if symbol_info is None:
                print(f"{simbolo:<8} - NAO ENCONTRADO")
                continue

            # Tentar adicionar no Market Watch
            if mt5.symbol_select(simbolo, True):
                print(f"{simbolo:<8} - ADICIONADO")
                adicionados += 1
            else:
                print(f"{simbolo:<8} - PROBLEMA AO ADICIONAR")

        except Exception as e:
            print(f"{simbolo:<8} - ERRO: {e}")

    print("\n" + "=" * 40)
    print(f"RESUMO: {adicionados}/{len(simbolos)} ativos adicionados")

    if adicionados > 0:
        print("\nPROXIMOS PASSOS:")
        print("1. Abra o MT5")
        print("2. Verifique o Market Watch (Ctrl+M)")
        print("3. Os simbolos devem estar la")
        print("4. Arraste para criar graficos separados")
        print("5. Configure timeframe M1 para cada")

        print("\nDICA: Use Window > Tile Windows para organizar")

    mt5.shutdown()
    return adicionados > 0

if __name__ == "__main__":
    adicionar_ativos()