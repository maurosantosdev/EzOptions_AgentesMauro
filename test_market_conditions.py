#!/usr/bin/env python3
"""
TESTE DAS CONDIÇÕES DE MERCADO - US100
Verifica volatilidade, preço e condições para operação
"""

import MetaTrader5 as mt5
import numpy as np
import pandas as pd
from datetime import datetime, time as dt_time
import pytz

def testar_condicoes_mercado():
    """Testa todas as condições que os agentes verificam"""

    print("TESTE COMPLETO DAS CONDICOES DE MERCADO")
    print("=" * 60)

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

    print("MT5 conectado com sucesso")

    # Verificar horário NY
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz)
    print(f"🕐 Horário Nova York: {now_ny.strftime('%H:%M:%S')}")

    # Verificar se é dia útil
    is_weekday = 0 <= now_ny.weekday() <= 4
    print(f"📅 É dia útil: {'✅ SIM' if is_weekday else '❌ NÃO'}")

    # Verificar se está no horário de operação (8:00-17:00)
    is_trading_hours = dt_time(8, 0) <= now_ny.time() < dt_time(17, 0)
    print(f"⏰ Dentro do horário: {'✅ SIM' if is_trading_hours else '❌ NÃO'}")

    # Obter dados do US100
    print("\n📊 ANALISANDO US100...")

    # Último tick
    tick = mt5.symbol_info_tick("US100")
    if tick:
        print(f"💰 Preço atual: {tick.last:.2f}")
        print(f"📈 Bid: {tick.bid:.2f}")
        print(f"📉 Ask: {tick.ask:.2f}")
        print(f"📊 Spread: {tick.ask - tick.bid:.2f}")
        print(f"📈 Volume: {tick.volume}")
    else:
        print("❌ ERRO: Não foi possível obter tick")
        mt5.shutdown()
        return False

    # Dados históricos (últimas 100 velas M1)
    rates = mt5.copy_rates_from_pos("US100", mt5.TIMEFRAME_M1, 0, 100)

    if rates is None or len(rates) < 40:
        print("❌ ERRO: Dados históricos insuficientes")
        mt5.shutdown()
        return False

    print(f"📈 Velas obtidas: {len(rates)} (últimas 100 minutos)")

    # Calcular volatilidade (exigida: > 0.05%)
    prices = rates['close']
    volatilidade = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
    print(f"📊 Volatilidade (20 velas): {volatilidade:.3f}%")

    volatilidade_minima = volatilidade > 0.05
    print(f"⚡ Volatilidade suficiente: {'✅ SIM' if volatilidade_minima else '❌ NÃO (min: 0.05%)'}")

    # Análise de tendência
    short_ma = np.mean(prices[-5:])
    long_ma = np.mean(prices[-20:])
    tendencia = "ALCISTA" if short_ma > long_ma else "BAIXISTA"
    forca_tendencia = abs(short_ma - long_ma) / long_ma * 100
    print(f"📈 Tendência: {tendencia} (força: {forca_tendencia:.2f}%)")

    # RSI básico
    delta = np.diff(prices[-14:])
    gain = np.sum(delta[delta > 0]) / len(delta[delta > 0]) if np.any(delta > 0) else 0
    loss = abs(np.sum(delta[delta < 0]) / len(delta[delta < 0])) if np.any(delta < 0) else 0
    rs = gain / loss if loss != 0 else 100
    rsi = 100 - (100 / (1 + rs))
    print(f"📊 RSI (14): {rsi:.2f}")

    # Verificar se é horário ótimo
    hora_atual = now_ny.hour
    horarios_a_evitar = [(12, 13), (15, 16)]
    horarios_ideais = [(8, 10), (15, 16)]

    evitando = any(start <= hora_atual < end for start, end in horarios_a_evitar)
    ideal = any(start <= hora_atual < end for start, end in horarios_ideais)

    print(f"🚫 Evitando horário: {'⚠️ SIM' if evitando else '✅ NÃO'}")
    print(f"⭐ Horário ideal: {'✅ SIM' if ideal else '❌ NÃO'}")

    # Resumo das condições
    print("\n" + "=" * 60)
    print("📋 RESUMO DAS CONDIÇÕES:")
    print("=" * 60)

    condicoes = [
        ("Horário de operação", is_trading_hours, "✅ OK"),
        ("Dia útil", is_weekday, "✅ OK"),
        ("Volatilidade mínima", volatilidade_minima, "✅ OK" if volatilidade_minima else "❌ BAIXA"),
        ("MT5 conectado", True, "✅ OK"),
        ("Dados históricos", len(rates) >= 40, "✅ OK"),
    ]

    for nome, valor, status in condicoes:
        print(f"{nome:<25} {status}")

    print(f"\n📊 Volatilidade atual: {volatilidade:.3f}% (mín: 0.05%)")
    print(f"💰 Preço US100: {tick.last:.2f}")
    print(f"📈 Tendência: {tendencia}")

    # Verificar por que agentes não operam
    print("\n🔍 ANÁLISE: Por que os agentes não operam?")
    print("-" * 50)

    if not volatilidade_minima:
        print("❌ Volatilidade muito baixa - mercado muito estável")
    if evitando:
        print("⚠️ Horário de almoço ou período a evitar")
    if not ideal:
        print("⚠️ Não está no horário considerado 'ideal'")
    if rsi > 70:
        print("⚠️ Mercado sobrecomprado (RSI > 70)")
    elif rsi < 30:
        print("⚠️ Mercado sobrevendido (RSI < 30)")

    print(f"\n🎯 Confiança mínima atual: 65%")
    print(f"📊 Para operar, precisa de sinais fortes dos agentes")

    mt5.shutdown()
    return volatilidade_minima and is_trading_hours and is_weekday

if __name__ == "__main__":
    testar_condicoes_mercado()