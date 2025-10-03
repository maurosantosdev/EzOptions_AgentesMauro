"""
TESTE DE CONEXÃO MT5 - VERSÃO SIMPLIFICADA
Para diagnosticar problemas específicos de conexão
"""

import MetaTrader5 as mt5
import time
import os
from dotenv import load_dotenv

def testar_conexao_basica():
    """Teste básico de conexão MT5"""
    print("🔧 TESTE BÁSICO DE CONEXÃO MT5")
    print("=" * 50)

    # Carregar variáveis de ambiente
    load_dotenv()

    # Verificar credenciais
    login = os.getenv("MT5_LOGIN")
    server = os.getenv("MT5_SERVER")
    password = os.getenv("MT5_PASSWORD")

    print(f"Login: {login}")
    print(f"Server: {server}")
    print(f"Password: {'*' * len(password) if password else 'NÃO CONFIGURADO'}")

    if not all([login, server, password]):
        print("❌ Credenciais não configuradas!")
        return False

    # Fechar conexão se já existe
    try:
        mt5.shutdown()
        time.sleep(1)
    except:
        pass

    # Inicializar MT5
    print("\n📡 Inicializando MT5...")
    if not mt5.initialize():
        print("❌ Falha na inicialização do MT5")
        return False

    print("✅ MT5 inicializado com sucesso")

    # Login
    print("🔑 Tentando login...")
    if mt5.login(int(login), password, server):
        print("✅ Login bem-sucedido")
    else:
        print("❌ Falha no login")
        return False

    return True

def testar_simbolo():
    """Testar se o símbolo US100 está disponível"""
    print("\n🔍 TESTANDO SÍMBOLO US100")
    print("=" * 50)

    # Lista de possíveis nomes para US100
    simbolos_teste = [
        'US100', 'US100.cash', 'US100cash', 'US100.CASH',
        'US100_INDEX', 'US100-INDEX', 'US100.CASH-INDEX',
        'NASDAQ100', 'NQ100', 'USTEC', 'USATECH'
    ]

    # Obter todos os símbolos disponíveis
    symbols = mt5.symbols_get()

    if symbols is None:
        print("❌ Não foi possível obter lista de símbolos")
        return None

    print(f"📊 Total de símbolos disponíveis: {len(symbols)}")

    # Procurar por símbolos relacionados a US100
    simbolos_encontrados = []
    for symbol in symbols:
        nome = str(symbol.name).upper()
        for teste in simbolos_teste:
            if teste.upper() in nome or nome in teste.upper():
                simbolos_encontrados.append(symbol.name)
                break

    if simbolos_encontrados:
        print("✅ Símbolos relacionados a US100 encontrados:")
        for simbolo in simbolos_encontrados:
            print(f"   - {simbolo}")
        return simbolos_encontrados[0]  # Retorna o primeiro encontrado
    else:
        print("❌ Nenhum símbolo relacionado a US100 encontrado")
        print("\n💡 Possíveis soluções:")
        print("   1. Abra o MT5 manualmente")
        print("   2. No MT5, vá em 'Market Watch'")
        print("   3. Clique com botão direito > 'Símbolos'")
        print("   4. Procure por 'US100' ou 'NASDAQ'")
        print("   5. Arraste o símbolo para o Market Watch")
        return None

def testar_preco_simbolo(simbolo):
    """Testar se consegue obter preço do símbolo"""
    print(f"\n💰 TESTANDO PREÇO DO SÍMBOLO: {simbolo}")
    print("=" * 50)

    # Verificar informações do símbolo
    symbol_info = mt5.symbol_info(simbolo)
    if symbol_info is None:
        print(f"❌ Não foi possível obter informações do símbolo {simbolo}")
        return False

    print("✅ Informações do símbolo obtidas:")
    print(f"   - Nome: {symbol_info.name}")
    print(f"   - Visível: {symbol_info.visible}")
    print(f"   - Spread: {symbol_info.spread}")
    print(f"   - Dígitos: {symbol_info.digits}")

    if not symbol_info.visible:
        print("⚠️  Símbolo não está visível no Market Watch")
        print("💡 Solução: Arraste o símbolo para o Market Watch no MT5")
        return False

    # Tentar obter tick
    tick = mt5.symbol_info_tick(simbolo)
    if tick:
        print("✅ Tick obtido com sucesso:")
        print(f"   - Preço: {tick.last}")
        print(f"   - Bid: {tick.bid}")
        print(f"   - Ask: {tick.ask}")
        print(f"   - Spread: {tick.ask - tick.bid}")
        return True
    else:
        print(f"❌ Não foi possível obter tick do símbolo {simbolo}")
        return False

def testar_ordem_simulada(simbolo):
    """Testar se consegue simular uma ordem"""
    print(f"\n📋 TESTANDO ORDEM SIMULADA: {simbolo}")
    print("=" * 50)

    # Obter preço atual
    tick = mt5.symbol_info_tick(simbolo)
    if not tick:
        print("❌ Não foi possível obter preço para teste de ordem")
        return False

    # Criar requisição de teste
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": simbolo,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "type_filling": mt5.ORDER_FILLING_RETURN,
        "magic": 999999
    }

    # Testar se a ordem seria aceita
    check_result = mt5.order_check(request)
    if check_result:
        print("✅ Verificação de ordem OK")
        print(f"   - Retcode: {check_result.retcode}")
        print(f"   - Comentário: {check_result.comment}")
        return True
    else:
        print("❌ Verificação de ordem falhou")
        return False

def main():
    """Função principal"""
    print("🚀 INICIANDO TESTE COMPLETO DE CONEXÃO MT5")
    print("=" * 60)

    # Teste 1: Conexão básica
    if not testar_conexao_basica():
        print("\n💥 Falha no teste básico de conexão!")
        input("Pressione ENTER para sair...")
        return

    # Teste 2: Encontrar símbolo
    simbolo = testar_simbolo()
    if not simbolo:
        print("\n💥 Símbolo US100 não encontrado!")
        input("Pressione ENTER para sair...")
        return

    # Teste 3: Testar preço
    if not testar_preco_simbolo(simbolo):
        print(f"\n💥 Falha no teste de preço do símbolo {simbolo}!")
        input("Pressione ENTER para sair...")
        return

    # Teste 4: Testar ordem simulada
    if not testar_ordem_simulada(simbolo):
        print(f"\n💥 Falha no teste de ordem do símbolo {simbolo}!")
        input("Pressione ENTER para sair...")
        return

    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("✅ MT5 está funcionando perfeitamente")
    print(f"✅ Símbolo correto: {simbolo}")
    print("✅ Conexão: OK")
    print("✅ Preços: OK")
    print("✅ Ordens: OK")

    print("\n💡 Agora você pode usar este símbolo nos sistemas:")
    print(f"   simbolo = '{simbolo}'")

    # Fechar conexão
    mt5.shutdown()

    input("Pressione ENTER para sair...")

if __name__ == "__main__":
    main()