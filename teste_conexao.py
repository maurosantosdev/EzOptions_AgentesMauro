import MetaTrader5 as mt5
import os

# Credenciais
login = int(os.getenv('MT5_LOGIN', '103486755'))
server = os.getenv('MT5_SERVER', 'FBS-Demo')
password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')

print(f'Usando credenciais: {login}, {server}')

# Tenta inicializar e obter versão
print('Tentando mt5.initialize()...')
result = mt5.initialize()
print(f'mt5.initialize() result: {result}')

if result:
    version = mt5.version()
    print(f'mt5.version(): {version}')
    
    # Tenta login
    print('Tentando login...')
    login_result = mt5.login(login, password, server)
    print(f'mt5.login() result: {login_result}')
    
    if login_result:
        account_info = mt5.account_info()
        print(f'mt5.account_info(): {account_info}')
        
        if account_info:
            print(f'Conta: #{account_info.login}, Saldo: ${account_info.balance:.2f}')
        else:
            print('Não foi possível obter informações da conta')
    else:
        print('Falha no login')
        print(f'Erro: {mt5.last_error()}')
        
    # Testar símbolo
    print('Testando símbolo US100...')
    symbol_select_result = mt5.symbol_select('US100', True)
    print(f'mt5.symbol_select("US100", True): {symbol_select_result}')
    
    symbol_info = mt5.symbol_info('US100')
    print(f'mt5.symbol_info("US100"): {symbol_info}')
    if symbol_info:
        print(f'  Visível: {symbol_info.visible}')
        print(f'  Nome: {symbol_info.name}')
        
        tick = mt5.symbol_info_tick('US100')
        print(f'mt5.symbol_info_tick("US100"): {tick}')
        if tick:
            print(f'  Preço: {tick.bid}/{tick.ask}')
else:
    print('Falha na inicialização')
    print(f'Erro: {mt5.last_error()}')

# Fecha conexão
mt5.shutdown()