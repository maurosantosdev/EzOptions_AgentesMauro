#!/usr/bin/env python3
"""
SCRIPT PARA ADICIONAR ATIVOS NO MT5
Adiciona DAX30, SPX500 e outros ativos recomendados no Market Watch
"""

import MetaTrader5 as mt5
import time

def adicionar_ativos_mt5():
    """Adiciona os ativos recomendados no MT5"""

    print("ADICIONANDO ATIVOS NO METATRADER 5")
    print("=" * 50)

    # Inicializar MT5
    if not mt5.initialize():
        print("❌ ERRO: Não foi possível inicializar MT5")
        return False

    # Login
    login = int(os.getenv('MT5_LOGIN', '103486755'))
    server = os.getenv('MT5_SERVER', 'FBS-Demo')
    password = os.getenv('MT5_PASSWORD', 'gPo@j6*V')

    if not mt5.login(login, password, server):
        print("❌ ERRO: Falha no login MT5")
        mt5.shutdown()
        return False

    print("✅ MT5 conectado com sucesso")

    # Ativos recomendados para os 6 setups + greeks
    ativos_recomendados = {
        # ATIVOS PRINCIPAIS
        'US100': {
            'nome': 'US100',
            'descricao': 'NASDAQ 100 - Principal',
            'grupo': 'INDICES'
        },
        'DAX30': {
            'nome': 'DAX30',
            'descricao': 'DAX Alemão - Pullbacks',
            'grupo': 'INDICES'
        },
        'SPX500': {
            'nome': 'SPX500',
            'descricao': 'S&P 500 - Consolidação',
            'grupo': 'INDICES'
        },

        # BACKUP/ALTERNATIVAS
        'DE40': {
            'nome': 'DE40',
            'descricao': 'DAX Alternativo',
            'grupo': 'INDICES'
        },
        'US500': {
            'nome': 'US500',
            'descricao': 'S&P 500 Alternativo',
            'grupo': 'INDICES'
        },
        'DJ30': {
            'nome': 'DJ30',
            'descricao': 'Dow Jones - Backup',
            'grupo': 'INDICES'
        },

        # FOREX MAIS LIQUIDOS
        'EURUSD': {
            'nome': 'EURUSD',
            'descricao': 'Euro/Dólar - Liquidez',
            'grupo': 'FOREX'
        },
        'GBPUSD': {
            'nome': 'GBPUSD',
            'descricao': 'Libra/Dólar - Volatilidade',
            'grupo': 'FOREX'
        }
    }

    print(f"\n📊 TENTANDO ADICIONAR {len(ativos_recomendados)} ATIVOS...")
    print("=" * 50)

    ativos_adicionados = []
    ativos_nao_encontrados = []

    for simbolo, info in ativos_recomendados.items():
        try:
            # Verificar se o símbolo existe
            symbol_info = mt5.symbol_info(simbolo)

            if symbol_info is None:
                print(f"❌ {simbolo"8"} - Não encontrado na corretora")
                ativos_nao_encontrados.append(simbolo)
                continue

            # Tentar adicionar no Market Watch
            if mt5.symbol_select(simbolo, True):
                print(f"✅ {simbolo"8"} - Adicionado com sucesso")
                ativos_adicionados.append(simbolo)

                # Aguardar um pouco entre adições
                time.sleep(0.5)
            else:
                print(f"⚠️  {simbolo"8"} - Problema ao adicionar")
                ativos_nao_encontrados.append(simbolo)

        except Exception as e:
            print(f"❌ {simbolo"8"} - Erro: {e}")
            ativos_nao_encontrados.append(simbolo)

    # Resumo
    print("\n" + "=" * 50)
    print("📋 RESUMO DA ADIÇÃO:")
    print("=" * 50)

    print(f"✅ Ativos adicionados: {len(ativos_adicionados)}")
    for simbolo in ativos_adicionados:
        info = ativos_recomendados[simbolo]
        print(f"   • {simbolo} - {info['descricao']}")

    if ativos_nao_encontrados:
        print(f"\n⚠️ Ativos não encontrados: {len(ativos_nao_encontrados)}")
        print("   💡 Possíveis soluções:")
        print("      • Verificar se a corretora oferece esses símbolos")
        print("      • Tentar variações (ex: GER40 ao invés de DAX30)")
        print("      • Contatar suporte da FBS-Demo")

        for simbolo in ativos_nao_encontrados:
            print(f"   • {simbolo} - Não disponível")

    # Verificar símbolos disponíveis similares
    print("\n🔍 VERIFICANDO ALTERNATIVAS...")
    alternativas = ['GER40', 'DE30', 'US30', 'US500', 'NAS100', 'DAX', 'SP500']

    for alt in alternativas:
        try:
            symbol_info = mt5.symbol_info(alt)
            if symbol_info:
                print(f"✅ ALTERNATIVA ENCONTRADA: {alt}")
        except:
            pass

    print("\n🎯 RECOMENDAÇÕES FINAIS:")
    print("=" * 50)

    if ativos_adicionados:
        print("✅ ATIVOS PRINCIPAIS ADICIONADOS:")
        for simbolo in ativos_adicionados:
            if simbolo in ['US100', 'DAX30', 'SPX500']:
                info = ativos_recomendados[simbolo]
                print(f"   📈 {simbolo} - {info['descricao']}")

    print("\n📊 PRÓXIMOS PASSOS:")
    print("   1. Abra o MT5 e verifique o Market Watch")
    print("   2. Os símbolos devem aparecer na lista")
    print("   3. Arraste os gráficos para criar janelas separadas")
    print("   4. Configure cada gráfico no timeframe M1")

    print("\n💡 DICAS PARA ORGANIZAR:")
    print("   • US100: Janela principal (maior)")
    print("   • DAX30: Janela secundária")
    print("   • SPX500: Janela terciária")
    print("   • Use 'Window' > 'Tile Windows' para organizar")

    mt5.shutdown()
    return len(ativos_adicionados) > 0

def verificar_ativos_disponiveis():
    """Verifica quais ativos estão disponíveis na corretora"""

    print("\n🔍 VERIFICANDO ATIVOS DISPONÍVEIS...")
    print("=" * 50)

    if not mt5.initialize():
        print("❌ ERRO: MT5 não inicializado")
        return []

    # Lista de símbolos para verificar
    simbolos_para_verificar = [
        'US100', 'DAX30', 'SPX500', 'DE40', 'US500',
        'DJ30', 'NAS100', 'DAX', 'SP500', 'US30',
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'
    ]

    disponiveis = []

    for simbolo in simbolos_para_verificar:
        symbol_info = mt5.symbol_info(simbolo)
        if symbol_info and symbol_info.visible:
            disponiveis.append(simbolo)
            print(f"✅ {simbolo} - Disponível e visível")

    print(f"\n📊 Total disponível: {len(disponiveis)} ativos")
    return disponiveis

if __name__ == "__main__":
    import os

    print("🚀 SISTEMA DE ADIÇÃO DE ATIVOS NO MT5")
    print("🎯 Para os 6 Setups + Greeks com características de trader sênior")

    # Primeiro verificar o que está disponível
    disponiveis = verificar_ativos_disponiveis()

    # Tentar adicionar os ativos
    sucesso = adicionar_ativos_mt5()

    if sucesso:
        print("\n🎉 SUCESSO! Ativos adicionados no MT5")
        print("📈 Agora você pode configurar o sistema multi-ativos")
    else:
        print("\n⚠️ Alguns ativos podem não estar disponíveis na FBS-Demo")
        print("💡 Contate o suporte da corretora para solicitar os símbolos")