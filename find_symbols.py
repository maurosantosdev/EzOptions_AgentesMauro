#!/usr/bin/env python3
import MetaTrader5 as mt5
import os

def main():
    print("PROCURANDO SIMBOLOS ALTERNATIVOS")
    print("=" * 40)

    if not mt5.initialize():
        print("ERRO MT5")
        return

    login = int(os.getenv('MT5_LOGIN', '103486755'))
    server = os.getenv('MT5_SERVER', 'FBS-Demo')
    password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')

    if not mt5.login(login, password, server):
        print("ERRO LOGIN")
        mt5.shutdown()
        return

    print("CONECTADO")

    # Testar simbolos
    simbolos = ['DE40', 'US30', 'US500', 'DE30', 'DAX', 'SP500']

    for simbolo in simbolos:
        info = mt5.symbol_info(simbolo)
        if info:
            print(f"ENCONTRADO: {simbolo}")
        else:
            print(f"NAO: {simbolo}")

    mt5.shutdown()

if __name__ == "__main__":
    main()