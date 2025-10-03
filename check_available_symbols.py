#!/usr/bin/env python3
import MetaTrader5 as mt5
import os

def verificar_simbolos_disponiveis():
    print("VERIFICANDO SIMBOLOS DISPONIVEIS NA FBS-DEMO")
    print("=" * 50)

    # Inicializar MT5
    if not mt5.initialize():
        print("ERRO: Nao foi possivel inicializar MT5")
        return []

    # Login
    login = int(os.getenv('MT5_LOGIN', '103486755'))
    server = os.getenv('MT5_SERVER', 'FBS-Demo')
    password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')

    if not mt5.login(login, password, server):
        print("ERRO: Falha no login MT5")
        mt5.shutdown()
        return []

    print("MT5 conectado com sucesso")

    # Simbolos que queremos encontrar
    simbolos_procurados = {
        'US100': ['US100', 'NAS100', 'NASDAQ', 'NQ100'],
        'DAX30': ['DAX30', 'DE30', 'GER30', 'DAX', 'DE40'],
        'SPX500': ['SPX500', 'US500', 'SP500', 'ES100'],
        'DJ30': ['DJ30', 'US30', 'DOW30', 'DJIA']
    }

    encontrados = {}

    print("\nProcurando simbolos...")
    print("=" * 50)

    for ativo, variacoes in simbolos_procurados.items():
        print(f"\n{ativo}:")
        for variacao in variacoes:
            try:
                symbol_info = mt5.symbol_info(variacao)
                if symbol_info:
                    print(f"  ENCONTRADO: {variacao}")
                    if ativo not in encontrados:
                        encontrados[ativo] = []
                    encontrados[ativo].append(variacao)
            except:
                pass

        if ativo not in encontrados:
            print(f"  Nenhum encontrado para {ativo}")

    # Verificar simbolos populares disponiveis
    print("\n" + "=" * 50)
    print("OUTROS SIMBOLOS POPULARES DISPONIVEIS:")
    print("=" * 50)

    simbolos_populares = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD',
        'XAUUSD', 'XAGUSD', 'BTCUSD', 'ETHUSD',
        'US100', 'US500', 'US30', 'DE40', 'FR40', 'GB100'
    ]

    disponiveis_populares = []

    for simbolo in simbolos_populares:
        symbol_info = mt5.symbol_info(simbolo)
        if symbol_info:
            disponiveis_populares.append(simbolo)
            print(f"  {simbolo}")

    print(f"\nTotal de simbolos populares disponiveis: {len(disponiveis_populares)}")

    # Resumo final
    print("\n" + "=" * 50)
    print("RESUMO FINAL:")
    print("=" * 50)

    for ativo, variacoes in encontrados.items():
        print(f"{ativo}: {', '.join(variacoes)}")

    print("
RECOMENDACOES:")
    print("  Para DAX30: Use DE40 (se disponivel)")
    print("  Para SPX500: Use US500 (ja adicionado)")
    print("  Para DJ30: Verifique US30")

    mt5.shutdown()
    return encontrados

if __name__ == "__main__":
    verificar_simbolos_disponiveis()