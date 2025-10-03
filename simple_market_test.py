#!/usr/bin/env python3
import MetaTrader5 as mt5
import numpy as np
import os
from datetime import datetime, time as dt_time
import pytz

def testar_mercado():
    print("TESTE DAS CONDICOES DE MERCADO - US100")
    print("=" * 50)

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

    # Verificar horario NY
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz)
    print(f"Horario Nova York: {now_ny.strftime('%H:%M:%S')}")

    # Verificar se e dia util
    is_weekday = 0 <= now_ny.weekday() <= 4
    print(f"E dia util: {'SIM' if is_weekday else 'NAO'}")

    # Verificar se esta no horario de operacao (8:00-17:00)
    is_trading_hours = dt_time(8, 0) <= now_ny.time() < dt_time(17, 0)
    print(f"Dentro do horario: {'SIM' if is_trading_hours else 'NAO'}")

    # Obter dados do US100
    print("\nANALISANDO US100...")

    # Ultimo tick
    tick = mt5.symbol_info_tick("US100")
    if tick:
        print(f"Preco atual: {tick.last:.2f}")
        print(f"Bid: {tick.bid:.2f}")
        print(f"Ask: {tick.ask:.2f}")
        print(f"Spread: {tick.ask - tick.bid:.2f}")
        print(f"Volume: {tick.volume}")
    else:
        print("ERRO: Nao foi possivel obter tick")
        mt5.shutdown()
        return False

    # Dados historicos (ultimas 100 velas M1)
    rates = mt5.copy_rates_from_pos("US100", mt5.TIMEFRAME_M1, 0, 100)

    if rates is None or len(rates) < 40:
        print("ERRO: Dados historicos insuficientes")
        mt5.shutdown()
        return False

    print(f"Velas obtidas: {len(rates)} (ultimas 100 minutos)")

    # Calcular volatilidade (exigida: > 0.05%)
    prices = rates['close']
    volatilidade = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
    print(f"Volatilidade (20 velas): {volatilidade:.3f}%")

    volatilidade_minima = volatilidade > 0.05
    print(f"Volatilidade suficiente: {'SIM' if volatilidade_minima else 'NAO (min: 0.05%)'}")

    # Analise de tendencia
    short_ma = np.mean(prices[-5:])
    long_ma = np.mean(prices[-20:])
    tendencia = "ALCISTA" if short_ma > long_ma else "BAIXISTA"
    forca_tendencia = abs(short_ma - long_ma) / long_ma * 100
    print(f"Tendencia: {tendencia} (forca: {forca_tendencia:.2f}%)")

    # RSI basico
    delta = np.diff(prices[-14:])
    gain = np.sum(delta[delta > 0]) / len(delta[delta > 0]) if np.any(delta > 0) else 0
    loss = abs(np.sum(delta[delta < 0]) / len(delta[delta < 0])) if np.any(delta < 0) else 0
    rs = gain / loss if loss != 0 else 100
    rsi = 100 - (100 / (1 + rs))
    print(f"RSI (14): {rsi:.2f}")

    # Verificar se e horario otimo
    hora_atual = now_ny.hour
    horarios_a_evitar = [(12, 13), (15, 16)]
    horarios_ideais = [(8, 10), (15, 16)]

    evitando = any(start <= hora_atual < end for start, end in horarios_a_evitar)
    ideal = any(start <= hora_atual < end for start, end in horarios_ideais)

    print(f"Evitando horario: {'SIM' if evitando else 'NAO'}")
    print(f"Horario ideal: {'SIM' if ideal else 'NAO'}")

    # Resumo das condicoes
    print("\n" + "=" * 50)
    print("RESUMO DAS CONDICOES:")
    print("=" * 50)

    condicoes = [
        ("Horario de operacao", is_trading_hours, "OK"),
        ("Dia util", is_weekday, "OK"),
        ("Volatilidade minima", volatilidade_minima, "OK" if volatilidade_minima else "BAIXA"),
        ("MT5 conectado", True, "OK"),
        ("Dados historicos", len(rates) >= 40, "OK"),
    ]

    for nome, valor, status in condicoes:
        print(f"{nome:<25} {status}")

    print(f"\nVolatilidade atual: {volatilidade:.3f}% (min: 0.05%)")
    print(f"Preco US100: {tick.last:.2f}")
    print(f"Tendencia: {tendencia}")

    # Verificar por que agentes nao operam
    print("\nANALISE: Por que os agentes nao operam?")
    print("-" * 50)

    if not volatilidade_minima:
        print("Volatilidade muito baixa - mercado muito estavel")
    if evitando:
        print("Horario de almoco ou periodo a evitar")
    if not ideal:
        print("Nao esta no horario considerado 'ideal'")
    if rsi > 70:
        print("Mercado sobrecomprado (RSI > 70)")
    elif rsi < 30:
        print("Mercado sobrevendido (RSI < 30)")

    print(f"\nConfianca minima atual: 65%")
    print("Para operar, precisa de sinais fortes dos agentes")

    mt5.shutdown()
    return volatilidade_minima and is_trading_hours and is_weekday

if __name__ == "__main__":
    testar_mercado()