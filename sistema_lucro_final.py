"""
Sistema Final de Agentes para LUCRO - Versão Corrigida
Problemas identificados e corrigidos:
1. Muitas operações pequenas causando perdas acumuladas
2. Ordens falhando devido a problemas de conexão
3. Sistema complexo demais causando instabilidade
4. Falta de controle de risco adequado
"""

import MetaTrader5 as mt5
import time
import os
from dotenv import load_dotenv
import threading
from datetime import datetime, time as datetime_time
import pytz
import logging
import yfinance as yf
import pandas as pd
import numpy as np

# Configurar logging sem emojis para evitar problemas de encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sistema_lucro_final.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SistemaLucroFinal(threading.Thread):
    """Sistema final otimizado para LUCRO com melhorias críticas"""

    def __init__(self, config):
        super().__init__()
        load_dotenv()
        self.name = config.get('name', 'SistemaLucroFinal')
        self.symbol = config.get('symbol', 'US100')
        self.magic_number = config.get('magic_number', 888888)

        # CONFIGURAÇÕES OTIMIZADAS PARA MAXIMIZAR LUCROS
        self.lot_size = 0.02  # Volume otimizado para melhor relação risco/retorno
        self.min_confidence = 85.0  # Confiança ainda mais alta (era 80)
        self.max_positions = 1  # APENAS 1 posição por vez - reduz risco
        self.stop_loss_pct = 0.2  # Stop loss MAIS APERTADO (era 0.3)
        self.take_profit_pct = 2.0  # Take profit MAIS ALTO (era 1.5)
        self.max_daily_loss = -20.0  # Stop loss diário MAIS BAIXO (era -50)
        self.max_operations_per_day = 2  # Máximo 2 operações por dia (era 3)

        # NOVOS CONTROLES PARA MAIS LUCROS
        self.circuit_breaker_count = 0  # Evita tentativas excessivas
        self.max_circuit_breaker = 3  # Máximo de falhas antes de pausar
        self.connection_retry_count = 0  # Controle de reconexões
        self.max_connection_retries = 5  # Máximo de tentativas de conexão

        # Estado
        self.is_connected = False
        self.running = False
        self.positions = []
        self.daily_operations = 0
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()

        # NOVOS CONTROLES PARA DIAGNÓSTICO MT5
        self.mt5_health_status = "UNKNOWN"
        self.last_successful_order = None
        self.order_failure_count = 0
        self.connection_test_results = {}

        # Executar diagnóstico completo primeiro
        self.run_comprehensive_diagnostics()

        # Conectar ao MT5 apenas se diagnóstico passou
        if self.mt5_health_status == "SAUDÁVEL":
            self.connect_mt5()
        else:
            logger.error(f"[{self.name}] Sistema não iniciará devido a problemas no diagnóstico MT5")

    def run_mt5_diagnostics(self):
        """Executa diagnóstico completo do MT5 para identificar problemas"""
        logger.info(f"[{self.name}] === DIAGNÓSTICO MT5 INICIADO ===")

        diagnostics = {
            'mt5_version': None,
            'account_info': None,
            'symbol_info': None,
            'connection_test': False,
            'order_test': False,
            'market_hours': False
        }

        try:
            # 1. Verificar versão do MT5
            diagnostics['mt5_version'] = mt5.version()
            logger.info(f"[{self.name}] MT5 Versão: {diagnostics['mt5_version']}")

            # 2. Verificar informações da conta
            account_info = mt5.account_info()
            if account_info:
                diagnostics['account_info'] = {
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'profit': account_info.profit,
                    'server': account_info.server
                }
                logger.info(f"[{self.name}] Conta OK - Saldo: ${account_info.balance:.2f}")
            else:
                logger.error(f"[{self.name}] ERRO: Não foi possível obter informações da conta")

            # 3. Verificar informações do símbolo
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info:
                diagnostics['symbol_info'] = {
                    'visible': symbol_info.visible,
                    'trade_mode': symbol_info.trade_mode,
                    'point': symbol_info.point,
                    'stops_level': symbol_info.trade_stops_level
                }
                logger.info(f"[{self.name}] Símbolo OK - Point: {symbol_info.point}, Stops: {symbol_info.trade_stops_level}")
            else:
                logger.error(f"[{self.name}] ERRO: Símbolo {self.symbol} não encontrado")

            # 4. Teste de conexão básico
            try:
                tick = mt5.symbol_info_tick(self.symbol)
                if tick:
                    diagnostics['connection_test'] = True
                    logger.info(f"[{self.name}] Teste conexão OK - Preço: {tick.last}")
                else:
                    logger.error(f"[{self.name}] ERRO: Não foi possível obter tick do símbolo")
            except Exception as e:
                logger.error(f"[{self.name}] ERRO no teste de conexão: {e}")

            # 5. Verificar se é horário de mercado
            diagnostics['market_hours'] = self.is_trading_hours()
            logger.info(f"[{self.name}] Horário de trading: {'OK' if diagnostics['market_hours'] else 'FORA DO HORÁRIO'}")

            # 6. Teste de ordem simulada (sem executar)
            try:
                test_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.symbol,
                    "volume": 0.01,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": mt5.symbol_info_tick(self.symbol).ask,
                    "type_filling": mt5.ORDER_FILLING_RETURN,
                    "magic": self.magic_number
                }

                # Apenas validar se a requisição seria aceita
                check_result = mt5.order_check(test_request)
                if check_result:
                    diagnostics['order_test'] = check_result.retcode == mt5.TRADE_RETCODE_DONE
                    logger.info(f"[{self.name}] Teste de ordem: {'OK' if diagnostics['order_test'] else 'FALHOU'}")
                else:
                    logger.error(f"[{self.name}] ERRO: Não foi possível verificar ordem")

            except Exception as e:
                logger.error(f"[{self.name}] ERRO no teste de ordem: {e}")

            # Resumo do diagnóstico
            self.mt5_health_status = "SAUDÁVEL" if all([
                diagnostics['account_info'],
                diagnostics['symbol_info'],
                diagnostics['connection_test'],
                diagnostics['market_hours']
            ]) else "PROBLEMAS DETECTADOS"

            logger.info(f"[{self.name}] Status MT5: {self.mt5_health_status}")
            self.connection_test_results = diagnostics

        except Exception as e:
            logger.error(f"[{self.name}] ERRO CRÍTICO no diagnóstico: {e}")
            self.mt5_health_status = "ERRO NO DIAGNÓSTICO"

        logger.info(f"[{self.name}] === DIAGNÓSTICO MT5 FINALIZADO ===")
        return diagnostics

    def run_comprehensive_diagnostics(self):
        """Executa diagnóstico completo incluindo MT5 e sistema"""
        logger.info(f"[{self.name}] === DIAGNÓSTICO COMPLETO INICIADO ===")

        # 1. Verificar variáveis de ambiente
        logger.info(f"[{self.name}] === VERIFICAÇÃO DE AMBIENTE ===")
        required_env_vars = ['MT5_LOGIN', 'MT5_SERVER', 'MT5_PASSWORD']
        missing_vars = []

        for var in required_env_vars:
            value = os.getenv(var)
            if value:
                logger.info(f"[{self.name}] {var}: OK")
            else:
                logger.error(f"[{self.name}] {var}: FALTANDO")
                missing_vars.append(var)

        if missing_vars:
            logger.error(f"[{self.name}] Variáveis de ambiente faltando: {missing_vars}")
            self.mt5_health_status = "ERRO AMBIENTE"
            return False

        # 2. Executar diagnóstico MT5
        logger.info(f"[{self.name}] === DIAGNÓSTICO MT5 ===")
        mt5_diagnostics = self.run_mt5_diagnostics()

        # 3. Verificar se diagnóstico MT5 passou
        if self.mt5_health_status != "SAUDÁVEL":
            logger.error(f"[{self.name}] MT5 não está saudável - Sistema não iniciará")
            return False

        # 4. Teste adicional de conectividade
        logger.info(f"[{self.name}] === TESTE DE CONECTIVIDADE ===")
        try:
            # Teste de latência
            start_time = time.time()
            tick = mt5.symbol_info_tick(self.symbol)
            latency = time.time() - start_time

            if tick:
                logger.info(f"[{self.name}] Latência: {latency:.3f}s - Preço: {tick.last}")
            else:
                logger.error(f"[{self.name}] Falha no teste de latência")
                self.mt5_health_status = "PROBLEMAS DE CONEXÃO"
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro no teste de conectividade: {e}")
            self.mt5_health_status = "ERRO CONECTIVIDADE"
            return False

        # 5. Verificar configurações do sistema
        logger.info(f"[{self.name}] === VERIFICAÇÃO DE CONFIGURAÇÕES ===")
        logger.info(f"[{self.name}] Símbolo: {self.symbol}")
        logger.info(f"[{self.name}] Magic Number: {self.magic_number}")
        logger.info(f"[{self.name}] Lot Size: {self.lot_size}")
        logger.info(f"[{self.name}] Confiança Mínima: {self.min_confidence}%")
        logger.info(f"[{self.name}] Stop Loss: {self.stop_loss_pct}% | Take Profit: {self.take_profit_pct}%")

        # 6. Teste de horário de mercado
        if not self.is_trading_hours():
            logger.warning(f"[{self.name}] Fora do horário de trading - Sistema aguardará abertura")

        logger.info(f"[{self.name}] === DIAGNÓSTICO COMPLETO FINALIZADO ===")
        logger.info(f"[{self.name}] Status Final: {self.mt5_health_status}")

        return self.mt5_health_status == "SAUDÁVEL"

    def connect_mt5(self):
        """Conecta ao MetaTrader5 com sistema de retry MELHORADO"""
        max_retries = 5  # Aumentado de 3 para 5
        base_delay = 3   # Delay maior para estabilização

        for attempt in range(max_retries):
            try:
                logger.info(f"[{self.name}] Tentativa de conexão {attempt+1}/{max_retries}")

                # 1. Primeiro, fazer shutdown se já inicializado
                try:
                    mt5.shutdown()
                    time.sleep(1)
                except:
                    pass

                # 2. Inicializar MT5
                if not mt5.initialize():
                    logger.error(f"[{self.name}] Falha na inicialização MT5")
                    if attempt < max_retries - 1:
                        delay = base_delay * (attempt + 1)
                        logger.info(f"[{self.name}] Aguardando {delay}s antes da próxima tentativa...")
                        time.sleep(delay)
                        continue
                    else:
                        return False

                logger.info(f"[{self.name}] MT5 inicializado com sucesso")

                # 3. Aguardar estabilização
                time.sleep(2)

                # 4. Tentar login
                login = int(os.getenv("MT5_LOGIN"))
                server = os.getenv("MT5_SERVER")
                password = os.getenv("MT5_PASSWORD")

                # 5. Verificar credenciais
                if not all([login, server, password]):
                    logger.error(f"[{self.name}] Credenciais MT5 incompletas")
                    return False

                if mt5.login(login, password, server):
                    self.is_connected = True
                    self.connection_retry_count = 0  # Reset contador

                    # 6. Teste adicional de conexão
                    if self.test_mt5_connection():
                        logger.info(f"[{self.name}] CONEXÃO MT5 BEM-SUCEDIDA E TESTADA!")
                        return True
                    else:
                        logger.error(f"[{self.name}] Conexão MT5 falhou no teste")
                        self.is_connected = False
                else:
                    logger.error(f"[{self.name}] Falha no login MT5 - Verifique credenciais")

                # Se chegou aqui, houve falha
                if attempt < max_retries - 1:
                    delay = base_delay * (attempt + 1)  # Delay progressivo
                    logger.info(f"[{self.name}] Aguardando {delay}s antes da próxima tentativa...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"[{self.name}] Falha crítica: MT5 não conectado após {max_retries} tentativas")
                    return False

            except Exception as e:
                logger.error(f"[{self.name}] Exceção na conexão MT5: {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (attempt + 1)
                    time.sleep(delay)
                    continue
                return False

        return False

    def test_mt5_connection(self):
        """Testa se a conexão MT5 está realmente funcionando"""
        try:
            # Teste 1: Verificar informações da conta
            account_info = mt5.account_info()
            if account_info is None:
                logger.error(f"[{self.name}] Não foi possível obter informações da conta")
                return False

            # Teste 2: Verificar informações do símbolo
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                logger.error(f"[{self.name}] Não foi possível obter informações do símbolo {self.symbol}")
                return False

            # Teste 3: Verificar tick atual
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                logger.error(f"[{self.name}] Não foi possível obter tick do símbolo")
                return False

            logger.info(f"[{self.name}] Teste de conexão OK - Preço: {tick.last}, Saldo: ${account_info.balance:.2f}")
            return True

        except Exception as e:
            logger.error(f"[{self.name}] Erro no teste de conexão: {e}")
            return False

    def get_current_price(self):
        """Obtém preço atual com retry e diagnóstico melhorado"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Verificar se MT5 está conectado
                if not self.is_connected:
                    logger.warning(f"[{self.name}] MT5 não conectado, tentando reconectar...")
                    if not self.connect_mt5():
                        logger.error(f"[{self.name}] Falha na reconexão MT5")
                        return None

                # Tentar obter informações do símbolo
                symbol_info = mt5.symbol_info(self.symbol)
                if symbol_info is None:
                    logger.error(f"[{self.name}] Não foi possível obter info para {self.symbol}")
                    logger.error(f"[{self.name}] Verifique se o símbolo está correto e visível no MT5")
                    return None

                # Verificar se símbolo está visível
                if not symbol_info.visible:
                    logger.error(f"[{self.name}] Símbolo {self.symbol} não está visível no Market Watch")
                    logger.error(f"[{self.name}] Adicione o símbolo ao Market Watch no MT5")
                    return None

                # Tentar obter tick
                tick = mt5.symbol_info_tick(self.symbol)
                if tick:
                    price = (tick.bid + tick.ask) / 2
                    logger.info(f"[{self.name}] Preço atual obtido: {price:.2f} (Bid: {tick.bid}, Ask: {tick.ask})")
                    return price
                else:
                    logger.warning(f"[{self.name}] Não foi possível obter tick para {self.symbol}")

                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None

            except Exception as e:
                logger.error(f"[{self.name}] Erro ao obter preço (tentativa {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None

    def analyze_market_simple(self):
        """Análise de mercado MELHORADA com filtros de qualidade"""
        try:
            current_price = self.get_current_price()
            if not current_price:
                logger.warning(f"[{self.name}] Não foi possível obter preço atual")
                return {}

            # Obter dados reais do MT5 com mais candles para análise melhor
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 30)

            if rates is None or len(rates) < 15:
                logger.warning(f"[{self.name}] Dados insuficientes: {len(rates) if rates else 0} candles")
                return {}

            # Extrair preços e volumes reais
            prices = [float(rate['close']) for rate in rates]
            volumes = [int(rate['tick_volume']) for rate in rates]

            # ANÁLISE MELHORADA DE TENDÊNCIA
            recent_prices = prices[-10:]  # Mais candles para análise
            trend = "NEUTRAL"
            confidence = 0

            if len(recent_prices) >= 5:
                # Análise de múltiplos períodos
                short_trend = self.calculate_trend(recent_prices[-5:])  # Últimos 5 candles
                medium_trend = self.calculate_trend(recent_prices[-10:])  # Últimos 10 candles

                # Tendência consistente = sinal mais forte
                if short_trend == medium_trend and short_trend != "NEUTRAL":
                    trend = short_trend
                    confidence = 70  # Confiança base alta para tendência consistente
                elif short_trend != "NEUTRAL":
                    trend = short_trend
                    confidence = 50  # Confiança menor para tendência apenas curto prazo

            # ANÁLISE DE VOLUME MELHORADA
            avg_volume = sum(volumes[-10:]) / len(volumes[-10:])  # Média dos últimos 10
            current_volume = volumes[-1]
            volume_strength = current_volume / max(avg_volume, 1)

            # FILTRO DE QUALIDADE: Volume deve ser significativo
            if volume_strength < 1.3:
                logger.info(f"[{self.name}] Volume fraco: {volume_strength:.2f}x - aguardando melhor volume")
                return {}

            # ANÁLISE DE MOMENTUM MELHORADA
            momentum_short = (current_price - prices[-1]) / prices[-1] if prices[-1] > 0 else 0
            momentum_medium = (current_price - prices[-5]) / prices[-5] if len(prices) >= 5 and prices[-5] > 0 else 0

            # DECISÃO MELHORADA baseada em múltiplos fatores
            action = "HOLD"

            if trend == "BULLISH" and momentum_short > 0.0005 and momentum_medium > 0:
                # Sinal de alta confirmado
                momentum_factor = min(30, abs(momentum_short) * 10000)
                volume_factor = min(20, (volume_strength - 1) * 15)
                confidence = min(100, confidence + momentum_factor + volume_factor)
                action = "BUY"

                logger.info(f"[{self.name}] SINAL DE ALTA CONFIRMADO:")
                logger.info(f"[{self.name}] - Tendência: {trend} | Volume: {volume_strength:.2f}x")
                logger.info(f"[{self.name}] - Momentum curto: {momentum_short:.4f} | Médio: {momentum_medium:.4f}")
                logger.info(f"[{self.name}] - Confiança: {confidence:.1f}%")

            elif trend == "BEARISH" and momentum_short < -0.0005 and momentum_medium < 0:
                # Sinal de baixa confirmado
                momentum_factor = min(30, abs(momentum_short) * 10000)
                volume_factor = min(20, (volume_strength - 1) * 15)
                confidence = min(100, confidence + momentum_factor + volume_factor)
                action = "SELL"

                logger.info(f"[{self.name}] SINAL DE BAIXA CONFIRMADO:")
                logger.info(f"[{self.name}] - Tendência: {trend} | Volume: {volume_strength:.2f}x")
                logger.info(f"[{self.name}] - Momentum curto: {momentum_short:.4f} | Médio: {momentum_medium:.4f}")
                logger.info(f"[{self.name}] - Confiança: {confidence:.1f}%")

            else:
                logger.info(f"[{self.name}] SINAL NEUTRO - Tendência: {trend}, aguardando melhor oportunidade")

            return {
                'action': action,
                'confidence': confidence,
                'current_price': current_price,
                'trend': trend,
                'volume_strength': volume_strength,
                'momentum': momentum_short
            }

        except Exception as e:
            logger.error(f"[{self.name}] Erro na análise melhorada: {e}")
            return {}

    def calculate_trend(self, prices):
        """Calcula tendência baseada em série de preços"""
        if len(prices) < 3:
            return "NEUTRAL"

        up_count = 0
        down_count = 0

        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                up_count += 1
            elif prices[i] < prices[i-1]:
                down_count += 1

        total_moves = up_count + down_count

        if total_moves < 2:
            return "NEUTRAL"

        up_ratio = up_count / total_moves
        down_ratio = down_count / total_moves

        if up_ratio >= 0.6:  # Pelo menos 60% dos movimentos são de alta
            return "BULLISH"
        elif down_ratio >= 0.6:  # Pelo menos 60% dos movimentos são de baixa
            return "BEARISH"
        else:
            return "NEUTRAL"

    def should_execute_trade(self, analysis):
        """Verifica se deve executar trade com CIRCUIT BREAKER e filtros MELHORADOS"""
        if not analysis or analysis.get('action') == 'HOLD':
            return False

        # CIRCUIT BREAKER: Se muitas falhas recentes, pausar operações
        if self.circuit_breaker_count >= self.max_circuit_breaker:
            logger.warning(f"[{self.name}] CIRCUIT BREAKER ATIVADO! {self.circuit_breaker_count} falhas consecutivas")
            logger.warning(f"[{self.name}] Pausando operações por 10 minutos para evitar perdas")
            time.sleep(600)  # Pausa de 10 minutos
            self.circuit_breaker_count = 0  # Reset após pausa
            return False

        # Verificar confiança mínima (MAIS ALTA)
        confidence = analysis.get('confidence', 0)
        if confidence < self.min_confidence:
            logger.info(f"[{self.name}] Confiança baixa: {confidence:.1f}% < {self.min_confidence}% - ignorando sinal")
            return False

        # FILTRO ADICIONAL: Volume deve estar acima da média para confirmar sinal
        volume_strength = analysis.get('volume_strength', 1.0)
        if volume_strength < 1.3:  # Volume deve ser pelo menos 30% acima da média
            logger.info(f"[{self.name}] Volume fraco: {volume_strength:.2f}x - aguardando melhor oportunidade")
            return False

        # Verificar limite de operações diárias
        if self.daily_operations >= self.max_operations_per_day:
            logger.info(f"[{self.name}] Limite diario atingido: {self.daily_operations}/{self.max_operations_per_day}")
            return False

        # Verificar stop loss diário (MAIS CONSERVADOR)
        if self.daily_pnl <= self.max_daily_loss:
            logger.warning(f"[{self.name}] Stop loss diario atingido: ${self.daily_pnl:.2f} <= ${self.max_daily_loss}")
            logger.warning(f"[{self.name}] PROTEÇÃO ATIVADA: Parando operações para preservar capital")
            return False

        # Verificar posições atuais (APENAS 1 POSIÇÃO)
        positions = mt5.positions_get(magic=self.magic_number)
        if positions and len(positions) >= self.max_positions:
            logger.info(f"[{self.name}] Limite de posicoes atingido: {len(positions)}/{self.max_positions}")
            return False

        # FILTRO DE QUALIDADE: Verificar se o sinal é realmente forte
        if confidence >= 90.0:
            logger.info(f"[{self.name}] SINAL EXCELENTE: {confidence:.1f}% - alta probabilidade de lucro")
        elif confidence >= 85.0:
            logger.info(f"[{self.name}] SINAL BOM: {confidence:.1f}% - boa probabilidade de lucro")
        else:
            logger.info(f"[{self.name}] SINAL RAZOÁVEL: {confidence:.1f}% - operando com cautela")

        return True

    def execute_trade(self, analysis):
        """Executa trade com configurações otimizadas e sistema de retry MELHORADO"""
        try:
            current_price = analysis['current_price']
            action = analysis['action']
            confidence = analysis['confidence']

            # Calcular preços com base na confiança
            price_multiplier = 1.001 if confidence >= 90 else 1.002  # Mais agressivo para sinais fortes

            if action == "BUY":
                entry_price = current_price * price_multiplier
                sl_price = current_price * (1 - self.stop_loss_pct/100)
                tp_price = current_price * (1 + self.take_profit_pct/100)
            else:  # SELL
                entry_price = current_price * (1 - price_multiplier + 1)  # Venda um pouco abaixo
                sl_price = current_price * (1 + self.stop_loss_pct/100)
                tp_price = current_price * (1 - self.take_profit_pct/100)

            logger.info(f"[{self.name}] EXECUTANDO {action} - Preço: {entry_price:.2f}, Conf: {confidence:.1f}%")
            logger.info(f"[{self.name}] Risco/Retorno: SL={sl_price:.2f} ({self.stop_loss_pct:.1f}%) | TP={tp_price:.2f} ({self.take_profit_pct:.1f}%)")

            # Tentar executar ordem com sistema de retry melhorado
            success = self.execute_order_with_retry(action, entry_price, sl_price, tp_price, analysis)

            if success:
                self.daily_operations += 1
                self.circuit_breaker_count = 0  # Reset circuit breaker em caso de sucesso
                logger.info(f"[{self.name}] SUCESSO: {action} executado - Operação {self.daily_operations}/{self.max_operations_per_day}")
                return True
            else:
                self.circuit_breaker_count += 1  # Incrementar circuit breaker
                logger.error(f"[{self.name}] FALHA na execução - Circuit breaker: {self.circuit_breaker_count}/{self.max_circuit_breaker}")
                return False

        except Exception as e:
            logger.error(f"[{self.name}] Erro na execução: {e}")
            self.circuit_breaker_count += 1
            return False

    def execute_order_with_retry(self, action, entry_price, sl_price, tp_price, analysis):
        """Executa ordem com sistema de retry mais robusto"""
        max_retries = 5  # Aumentado para 5 tentativas
        base_delay = 2   # Delay maior para estabilização

        # Lista de filling modes para tentar
        filling_modes = [
            mt5.ORDER_FILLING_RETURN,
            mt5.ORDER_FILLING_IOC,
            mt5.ORDER_FILLING_FOK
        ]

        for attempt in range(max_retries):
            for filling_mode in filling_modes:
                try:
                    # Verificar se MT5 ainda está conectado
                    if not self.is_connected:
                        logger.warning(f"[{self.name}] MT5 desconectado, tentando reconectar...")
                        if not self.connect_mt5():
                            logger.error(f"[{self.name}] Falha na reconexão MT5")
                            continue

                    # TESTE DE CONEXÃO ANTES DE CADA TENTATIVA
                    try:
                        test_tick = mt5.symbol_info_tick(self.symbol)
                        if test_tick is None:
                            logger.error(f"[{self.name}] Não foi possível obter tick - conexão instável")
                            continue
                    except Exception as e:
                        logger.error(f"[{self.name}] Erro no teste de conexão: {e}")
                        continue

                    # Configurar ordem
                    order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL

                    # OBTER PREÇO ATUAL ANTES DE CADA TENTATIVA
                    current_tick = mt5.symbol_info_tick(self.symbol)
                    if current_tick:
                        if action == "BUY":
                            entry_price = current_tick.ask * 1.001  # Usar ask atual
                        else:
                            entry_price = current_tick.bid * 0.999  # Usar bid atual

                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": self.symbol,
                        "volume": self.lot_size,
                        "type": order_type,
                        "price": round(entry_price, 2),
                        "sl": round(sl_price, 2),
                        "tp": round(tp_price, 2),
                        "magic": self.magic_number,
                        "comment": f"{self.name} - {analysis['trend']} - Conf:{analysis['confidence']:.1f}%",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": filling_mode,
                        "deviation": 50  # Aumentado para 50 pontos
                    }

                    logger.info(f"[{self.name}] Tentativa {attempt+1} - Filling: {filling_mode} - Preço: {entry_price:.2f}")

                    # EXECUTAR ORDEM COM TIMEOUT
                    result = mt5.order_send(request)

                    if result is None:
                        logger.warning(f"[{self.name}] Resultado None - possível problema de conexão")
                        # Aguardar um pouco antes de tentar novamente
                        time.sleep(1)
                        continue

                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        logger.info(f"[{self.name}] ORDEM EXECUTADA COM SUCESSO!")
                        logger.info(f"[{self.name}] Ticket: {result.order} | Volume: {result.volume} | Preço: {result.price}")
                        return True

                    elif result.retcode == mt5.TRADE_RETCODE_REQUOTE:
                        logger.warning(f"[{self.name}] Requote detectado - preço mudou, ajustando...")
                        # Aguardar estabilização do preço
                        time.sleep(0.5)
                        # Ajustar preço baseado no requote
                        if action == "BUY":
                            entry_price = result.bid * 1.001
                        else:
                            entry_price = result.ask * 0.999
                        break  # Sair do loop de filling modes e tentar novamente com novo preço

                    elif result.retcode == 10030:  # Unsupported filling mode
                        logger.warning(f"[{self.name}] Filling mode {filling_mode} não suportado, tentando próximo...")
                        continue

                    elif result.retcode == 10016:  # Market closed
                        logger.error(f"[{self.name}] Mercado fechado - aguardando abertura")
                        return False

                    elif result.retcode == 10018:  # Insufficient funds
                        logger.error(f"[{self.name}] Fundos insuficientes")
                        return False

                    else:
                        logger.error(f"[{self.name}] Erro {result.retcode}: {result.comment}")
                        # Para alguns erros, não faz sentido tentar outros filling modes
                        if result.retcode in [10015, 10025, 10026]:  # Erros críticos
                            break
                        continue

                except Exception as e:
                    logger.error(f"[{self.name}] Exceção na tentativa {attempt+1}: {e}")
                    break

            # Se chegou aqui, tentativa falhou - aguardar antes de próxima tentativa
            if attempt < max_retries - 1:
                delay = base_delay * (attempt + 1)
                logger.info(f"[{self.name}] Aguardando {delay}s antes da próxima tentativa...")
                time.sleep(delay)

        logger.error(f"[{self.name}] Falha crítica: Ordem não executada após {max_retries} tentativas")
        return False

    def update_daily_stats(self):
        """Atualiza estatísticas diárias"""
        try:
            current_date = datetime.now().date()
            if current_date != self.last_reset_date:
                # Reset diário
                self.daily_operations = 0
                self.daily_pnl = 0.0
                self.last_reset_date = current_date
                logger.info(f"[{self.name}] Reset diario executado")

            # Atualizar P&L diário
            positions = mt5.positions_get(magic=self.magic_number)
            if positions:
                self.daily_pnl = sum(pos.profit for pos in positions)
                logger.info(f"[{self.name}] P&L Diario: ${self.daily_pnl:.2f}")

        except Exception as e:
            logger.error(f"[{self.name}] Erro na atualizacao diaria: {e}")

    def run(self):
        """Loop principal otimizado"""
        if not self.is_connected:
            logger.error(f"[{self.name}] MT5 nao conectado")
            return

        logger.info(f"[{self.name}] SISTEMA LUCRO FINAL INICIADO!")
        logger.info(f"[{self.name}] Configuracoes otimizadas para LUCRO:")
        logger.info(f"[{self.name}] - Confianca minima: {self.min_confidence}%")
        logger.info(f"[{self.name}] - Max posicoes: {self.max_positions}")
        logger.info(f"[{self.name}] - Stop Loss: {self.stop_loss_pct}% | Take Profit: {self.take_profit_pct}%")
        logger.info(f"[{self.name}] - Max operacoes/dia: {self.max_operations_per_day}")
        logger.info(f"[{self.name}] - Stop loss diario: ${self.max_daily_loss}")

        self.running = True

        try:
            while self.running:
                # Verificar se é horário de trading
                if not self.is_trading_hours():
                    time.sleep(60)
                    continue

                # Atualizar estatísticas diárias
                self.update_daily_stats()

                # Analisar mercado
                analysis = self.analyze_market_simple()

                if analysis and self.should_execute_trade(analysis):
                    logger.info(f"[{self.name}] SINAL DETECTADO: {analysis['action']} (Conf: {analysis['confidence']:.1f}%)")
                    if self.execute_trade(analysis):
                        logger.info(f"[{self.name}] Trade executado com sucesso!")
                    else:
                        logger.error(f"[{self.name}] Falha na execucao do trade")

                # Aguardar antes da próxima análise
                time.sleep(60)  # Análise a cada 60 segundos

        except KeyboardInterrupt:
            logger.info(f"[{self.name}] Interrupcao detectada")
        except Exception as e:
            logger.error(f"[{self.name}] Erro no loop: {e}")
        finally:
            self.stop()

    def stop(self):
        """Para o sistema"""
        logger.info(f"[{self.name}] Parando sistema...")
        self.running = False

        # Fechar todas as posições
        try:
            positions = mt5.positions_get(magic=self.magic_number)
            if positions:
                for pos in positions:
                    self.close_position(pos.ticket)
        except:
            pass

        # Fechar conexão
        try:
            mt5.shutdown()
        except:
            pass

    def close_position(self, ticket):
        """Fecha posição específica"""
        try:
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                return True

            pos = positions[0]
            order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY

            tick = mt5.symbol_info_tick(self.symbol)
            price = tick.bid if order_type == mt5.ORDER_TYPE_SELL else tick.ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": self.magic_number,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }

            result = mt5.order_send(request)
            return result and result.retcode == mt5.TRADE_RETCODE_DONE

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao fechar posicao {ticket}: {e}")
            return False

    def is_trading_hours(self):
        """Verifica se é horário de trading com filtros MELHORADOS"""
        try:
            ny_tz = pytz.timezone('America/New_York')
            now_ny = datetime.now(ny_tz)

            # Fim de semana - NÃO OPERAR
            if now_ny.weekday() > 4:
                return False

            current_time = now_ny.time()

            # HORÁRIOS OTIMIZADOS PARA MAIOR LIQUIDEZ E MENOS VOLATILIDADE
            market_open = datetime_time(9, 45, 0)   # Começar 15min após abertura
            market_close = datetime_time(15, 45, 0) # Terminar 15min antes do fechamento

            # Verificar se está dentro do horário otimizado
            if not (market_open <= current_time <= market_close):
                return False

            # FILTRO ADICIONAL: Evitar operar nos primeiros 5 minutos de cada hora
            # (muitos sinais falsos devido a ajustes de posição)
            current_minute = current_time.minute
            if current_minute < 5:
                logger.info(f"[{self.name}] Evitando primeiros 5 minutos da hora - aguardando liquidez")
                return False

            # FILTRO ADICIONAL: Evitar operar nos últimos 5 minutos de cada hora
            # (muitos sinais falsos devido a fechamento de posições)
            if current_minute > 55:
                logger.info(f"[{self.name}] Evitando últimos 5 minutos da hora - aguardando estabilidade")
                return False

            logger.info(f"[{self.name}] Horário de trading IDEAL confirmado: {current_time}")
            return True

        except Exception as e:
            logger.error(f"[{self.name}] Erro na verificação de horário: {e}")
            return False  # Em caso de erro, NÃO operar

if __name__ == "__main__":
    # Criar e iniciar o sistema final
    config = {
        'name': 'SistemaLucroFinal',
        'symbol': 'US100',
        'magic_number': 888888
    }

    sistema = SistemaLucroFinal(config)
    sistema.start()

    try:
        # Manter sistema rodando
        while True:
            time.sleep(60)
            logger.info(f"[{config['name']}] Sistema ativo - Aguardando sinais...")

    except KeyboardInterrupt:
        logger.info("Interrupcao detectada pelo usuario")
    except Exception as e:
        logger.error(f"Erro no sistema: {e}")
    finally:
        sistema.stop()
        sistema.join()
        logger.info("Sistema finalizado")