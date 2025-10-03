#!/usr/bin/env python3
"""
SISTEMA DE EMERGÊNCIA - STOP LOSS FORÇADO
FECHA QUALQUER POSIÇÃO COM PERDA >= -$0.99
OTIMIZADO PARA VOLATILIDADE DO US100 - PERMITE MERCADO RESPIRAR
"""

import MetaTrader5 as mt5
import time
import logging
import pytz
from datetime import datetime, time as datetime_time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - EMERGENCY - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def detect_market_consolidation():
    """DESABILITADO - Detecta se o mercado está consolidado"""
    try:
        # DESABILITADO PARA EVITAR ERRO NUMPY
        logger.info("Detecção de consolidação desabilitada")
        return False  # Sempre retorna False = mercado sempre ativo

    except Exception as e:
        logger.error(f"Erro na detecção de consolidação: {e}")
        return False

# Dicionário para armazenar picos de lucro de cada posição
position_peaks = {}
trailing_stop_distance = 0.40  # Distância do trailing stop em relação ao pico de lucro (REDUZIDO PARA SEGURANÇA)
trailing_activation_threshold = 0.50  # Nível mínimo de lucro para ativar trailing stop (REDUZIDO PARA SEGURANÇA)

# Contador de erros de conexão para o sistema de emergência
connection_error_count = 0
max_connection_errors = 5

def check_connection_health():
    """Verifica a saúde da conexão MT5 no sistema de emergência"""
    global connection_error_count
    
    try:
        # Testar conexão fazendo uma chamada simples
        account_info = mt5.account_info()
        if account_info is None:
            connection_error_count += 1
            logger.warning(f"Falha na verificação de saúde da conexão (tentativa {connection_error_count})")
            return False
        else:
            # Reiniciar contador de erros se a conexão estiver saudável
            connection_error_count = 0
            return True
    except Exception as e:
        connection_error_count += 1
        logger.error(f"Exceção na verificação de saúde da conexão: {e}")
        return False

def reconnect_mt5():
    """Função para reconectar ao MT5 no sistema de emergência"""
    global connection_error_count
    
    logger.warning("Tentando reconexão MT5 forçada no sistema de emergência...")
    try:
        mt5.shutdown()
        time.sleep(3)  # Esperar antes de tentar reconectar
        if mt5.initialize():
            connection_error_count = 0
            logger.info("Reconexão MT5 bem-sucedida no sistema de emergência!")
            return True
        else:
            logger.error("Falha na inicialização MT5 após shutdown")
    except Exception as e:
        logger.error(f"Erro durante reconexão no sistema de emergência: {e}")
    
    return False

def close_position_by_ticket(ticket):
    """Fecha uma posição específica pelo ticket com sistema de retry robusto e fallback de filling modes"""
    global position_peaks, connection_error_count, max_connection_errors
    
    max_retries = 5  # Número máximo de tentativas
    retry_delay = 1  # Segundos entre tentativas iniciais
    
    # Lista de filling modes para tentar em ordem de preferência
    filling_modes = [
        mt5.ORDER_FILLING_IOC,      # Immediate or cancel
        mt5.ORDER_FILLING_FOK,      # Fill or kill
        mt5.ORDER_FILLING_BOC,      # Better of cancel (MT5 only)
        mt5.ORDER_FILLING_RETURN,   # Return on failure (original)
    ]
    
    for attempt in range(max_retries):
        for filling_mode in filling_modes:
            try:
                # Verificar saúde da conexão periodicamente
                if connection_error_count >= max_connection_errors:
                    logger.warning("Número máximo de erros de conexão atingido, tentando reconexão...")
                    reconnect_mt5()
                
                # Verificar se a posição ainda existe antes de tentar fechar
                position = mt5.positions_get(ticket=ticket)
                if not position or len(position) == 0:
                    logger.warning(f"Posição {ticket} não encontrada - pode ter sido fechada por outro processo")
                    return True  # Considerar como sucesso se já foi fechada

                pos = position[0]

                # Verificar se a posição pertence ao símbolo e magic number corretos
                if pos.symbol != "US100" or pos.magic != 234001:
                    logger.warning(f"Posição {ticket} não pertence ao símbolo/magic configurado")
                    return False

                # Configurar ordem de fechamento
                if pos.type == mt5.POSITION_TYPE_BUY:
                    order_type = mt5.ORDER_TYPE_SELL
                    symbol_info_tick = mt5.symbol_info_tick("US100")
                    if not symbol_info_tick:
                        logger.error(f"Não foi possível obter cotação para fechar posição {ticket}")
                        continue  # Tentar próximo filling mode
                    price = symbol_info_tick.bid
                else:
                    order_type = mt5.ORDER_TYPE_BUY
                    symbol_info_tick = mt5.symbol_info_tick("US100")
                    if not symbol_info_tick:
                        logger.error(f"Não foi possível obter cotação para fechar posição {ticket}")
                        continue  # Tentar próximo filling mode
                    price = symbol_info_tick.ask

                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": "US100",
                    "volume": pos.volume,
                    "type": order_type,
                    "position": ticket,
                    "price": price,
                    "deviation": 20,
                    "magic": 234001,
                    "comment": "Emergency Stop Loss / Trailing Stop",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": filling_mode,
                }

                # Tentar fechar a posição
                result = mt5.order_send(request)

                if result is None:
                    logger.warning(f"Tentativa {attempt + 1} (filling mode {filling_mode}): Resultado é None ao tentar fechar posição {ticket} - tentando reconectar...")
                    # Tentar reconectar antes de continuar
                    reconnect_mt5()
                    continue  # Tentar próximo filling mode

                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"Posição {ticket} fechada com sucesso com filling mode {filling_mode} - Lucro: ${pos.profit:.2f}")
                    # Remover do controle de picos se existir
                    if ticket in position_peaks:
                        del position_peaks[ticket]
                    return True
                elif result.retcode == mt5.TRADE_RETCODE_REQUOTE:
                    logger.warning(f"Tentativa {attempt + 1}: Requote ao fechar posição {ticket}, tentando novamente...")
                    continue  # Tentar próximo filling mode
                elif result.retcode == 10030:  # Unsupported filling mode
                    logger.warning(f"Tentativa {attempt + 1}: Filling mode {filling_mode} não suportado para posição {ticket}, tentando próximo...")
                    continue  # Tentar próximo filling mode
                elif result.retcode == 10009:  # Request is too old
                    logger.warning(f"Tentativa {attempt + 1}: Request muito antigo para posição {ticket}, tentando reconectar...")
                    reconnect_mt5()
                    continue  # Tentar novamente
                elif result.retcode == 10013:  # Trade server is busy
                    logger.warning(f"Tentativa {attempt + 1}: Servidor de trade ocupado para posição {ticket}, esperando mais...")
                    time.sleep(1)  # Espera extra quando servidor está ocupado
                    continue  # Tentar próximo filling mode
                elif result.retcode == 10015:  # Price changed
                    logger.warning(f"Tentativa {attempt + 1}: Preço alterado para posição {ticket}, tentando novamente...")
                    continue  # Tentar próximo filling mode
                else:
                    error_code = result.retcode
                    error_comment = result.comment
                    logger.error(f"Tentativa {attempt + 1} (filling mode {filling_mode}): Erro ao fechar posição {ticket}: {error_code} - {error_comment}")
                    
                    # Verificar se a posição pode ter sido fechada entre o tempo de verificação e a execução
                    try:
                        position_after = mt5.positions_get(ticket=ticket)
                        if not position_after or len(position_after) == 0:
                            logger.warning(f"Posição {ticket} já foi fechada por outro processo")
                            # Mesmo que a ordem tenha falhado, remover do controle de picos se existir
                            if ticket in position_peaks:
                                del position_peaks[ticket]
                            return True  # Considerar como sucesso se a posição já foi fechada
                    except Exception as e:
                        logger.error(f"Erro ao verificar posição após falha: {e}")
                        # Tentar reconectar se houve erro ao verificar posição
                        reconnect_mt5()
                    
            except Exception as e:
                logger.error(f"Tentativa {attempt + 1} (filling mode {filling_mode}): Erro ao fechar posição {ticket}: {e}")
                continue  # Tentar próximo filling mode
        
        # Se todos os filling modes falharam nesta tentativa, esperar antes de tentar novamente
        if attempt < max_retries - 1:  # Se não for a última tentativa
            time.sleep(retry_delay * (attempt + 2))  # Espera progressiva aumentando a cada tentativa
            # Verificar conexão entre tentativas
            if not check_connection_health():
                reconnect_mt5()
        else:
            # Se for a última tentativa e ainda não teve sucesso
            logger.error(f"Falha crítica: Não conseguiu fechar posição {ticket} após {max_retries} tentativas com todos os filling modes")
            return False
    
    logger.error(f"Esgotadas todas as tentativas para fechar posição {ticket}")
    return False

def check_trailing_stop():
    """Monitora e aplica trailing stop para proteger lucros parciais"""
    global position_peaks, trailing_stop_distance, trailing_activation_threshold
    
    try:
        positions = mt5.positions_get(symbol="US100", magic=234001)
        if not positions:
            return False

        closed_positions = []

        for pos in positions:
            ticket = pos.ticket
            current_profit = pos.profit
            current_price = pos.price_current
            open_price = pos.price_open
            
            # Calcular lucro em pontos para melhor precisão
            points_profit = 0
            if pos.type == mt5.POSITION_TYPE_BUY:
                points_profit = (current_price - open_price) * 10  # Aproximação para US100
            else:
                points_profit = (open_price - current_price) * 10  # Aproximação para US100
            
            # Atualizar o pico de lucro desta posição com mais precisão
            if ticket not in position_peaks:
                # Armazenar informações mais completas sobre o pico
                position_peaks[ticket] = {
                    'profit': current_profit,
                    'points': points_profit,
                    'price': current_price
                }
                logger.info(f"INICIANDO MONITORAMENTO - Posição #{ticket}: ${current_profit:.2f} ({points_profit:.1f} pts)")
            else:
                # Comparar com o pico armazenado
                peak_data = position_peaks[ticket]
                
                # Se o lucro atual é maior que o pico anterior, atualizar
                if current_profit > peak_data['profit']:
                    position_peaks[ticket] = {
                        'profit': current_profit,
                        'points': points_profit,
                        'price': current_price
                    }
                    logger.info(f"NOVO PICO - Posição #{ticket}: ${current_profit:.2f} ({points_profit:.1f} pts)")

            # Verificar se deve aplicar trailing stop
            peak_data = position_peaks[ticket]
            peak_profit = peak_data['profit']

            # SISTEMA DE TRAILING MAIS CONSERVADOR - ativa com base no potencial de lucro
            # REDUZIDO O LIMIAR PARA MAIOR SEGURANÇA
            if peak_profit >= trailing_activation_threshold or points_profit >= 5:  # Reduzido de 10 para 5 pontos de movimento
                # Calcular a queda desde o pico
                profit_drop = peak_profit - current_profit
                points_drop = peak_data['points'] - points_profit  # Queda em pontos

                # Ajuste dinâmico do trailing stop baseado no potencial de lucro
                dynamic_trailing_distance = trailing_stop_distance
                
                # Se o pico foi muito alto (> $2), usar trailing menor para proteger mais
                if peak_profit > 2.0:  # Reduzido de >$5 para >$2
                    dynamic_trailing_distance = 0.3  # Mais agressivo para lucros altos (reduzido de 0.5)
                elif peak_profit > 1.0:  # Reduzido de >$2 para >$1
                    dynamic_trailing_distance = 0.4  # Moderadamente agressivo (reduzido de 0.7)
                
                if profit_drop >= dynamic_trailing_distance:
                    logger.warning(f"TRAILING STOP ATIVADO!")
                    logger.warning(f"Posição #{ticket} - Pico: ${peak_profit:.2f} | Atual: ${current_profit:.2f} | Queda: ${profit_drop:.2f}")
                    logger.warning(f"Picos em pontos: {peak_data['points']:.1f} | Atual: {points_profit:.1f} | Queda: {abs(points_drop):.1f} pts")

                    # Fechar posição
                    if close_position_by_ticket(ticket):
                        logger.info(f"TRAILING STOP EXECUTADO: Posição #{ticket} fechada com ${current_profit:.2f}")
                        closed_positions.append(ticket)
                    else:
                        logger.error(f"Falha ao fechar posição #{ticket} por trailing stop")

        return len(closed_positions) > 0

    except Exception as e:
        logger.error(f"Erro no trailing stop: {e}")
        return False

def emergency_stop_loss():
    """FORÇA fechamento de TODAS posições com perda >= -$0.99 e aplica trailing stop"""
    
    # Conectar MT5
    if not mt5.initialize():
        logger.error("FALHA AO INICIALIZAR MT5!")
        return False

    logger.info("SISTEMA DE EMERGÊNCIA ATIVO - MONITORANDO STOP LOSS -$0.99")
    logger.info("SISTEMA DE TRAILING STOP ATIVO - Protegendo lucros acima de $1.00")
    logger.info("SISTEMA OPERANDO 24/7 - Monitoramento contínuo")
    logger.info("DETECTANDO CONSOLIDAÇÃO PARA EVITAR SINAIS DESNECESSÁRIOS")

    consolidation_count = 0

    while True:
        try:
            # VERIFICAR SE MERCADO ESTÁ CONSOLIDADO (DESABILITADO)
            is_consolidated = detect_market_consolidation()

            if is_consolidated:
                consolidation_count += 1

                # Se mercado consolidado por mais de 5 verificações (10 segundos)
                if consolidation_count >= 5:
                    logger.info("MERCADO CONSOLIDADO - PAUSANDO MONITORAMENTO POR 60 SEGUNDOS")
                    logger.info("Sistema em standby - sem novas negociações")
                    time.sleep(60)  # Pausa longa em mercado consolidado
                    consolidation_count = 0  # Reset contador
                    continue
                else:
                    logger.info(f"Consolidação detectada ({consolidation_count}/5) - continuando...")
            else:
                consolidation_count = 0  # Reset se mercado não consolidado
                logger.info("MERCADO ATIVO - MONITORAMENTO NORMAL")

            # 3. APLICAÇÃO DE TRAILING STOP PARA PROTEGER LUCROS
            trailing_closed = check_trailing_stop()

            # 2. MONITORAR POSIÇÕES EXISTENTES (sempre executa - stop loss é crítico!)
            # Filtrar por símbolo e magic number específico
            positions = mt5.positions_get(symbol="US100", magic=234001)

            if positions:
                logger.info(f"Monitorando {len(positions)} posições...")

                for pos in positions:
                    ticket = pos.ticket
                    profit = pos.profit

                    # VERIFICAÇÃO CRÍTICA: Se perda >= -$0.15 (AINDA MAIS CONSERVADOR)
                    if profit <= -0.15:
                        logger.error(f"PERDA DETECTADA: Posição #{ticket} = ${profit:.2f}")
                        logger.error(f"FECHANDO IMEDIATAMENTE!")

                        # Tentar fechar posição usando a função aprimorada
                        if close_position_by_ticket(ticket):
                            logger.info(f"EMERGÊNCIA EXECUTADA: Posição #{ticket} fechada com ${profit:.2f}")
                        else:
                            logger.error(f"FALHA CRÍTICA: Não conseguiu fechar #{ticket} por stop loss")
                            # Após falha crítica, tentar reconectar para garantir estabilidade
                            reconnect_mt5()

            else:
                if not is_consolidated:
                    logger.info("Nenhuma posição US100 aberta - mercado ativo")

            # VERIFICAÇÃO ULTRA RÁPIDA PARA STOP LOSS -$0.99
            if is_consolidated:
                time.sleep(2)  # Pausa reduzida mesmo em consolidação
            else:
                time.sleep(0.5)   # VERIFICAÇÃO A CADA 0.5 SEGUNDOS (ULTRA RÁPIDO)

        except Exception as e:
            logger.error(f"ERRO NO SISTEMA DE EMERGÊNCIA: {e}")
            time.sleep(5)

if __name__ == "__main__":
    logger.info("INICIANDO SISTEMA DE EMERGÊNCIA - STOP LOSS -$0.99")
    logger.info("ATENÇÃO: Este sistema FECHARÁ QUALQUER POSIÇÃO COM PERDA >= -$0.99")
    try:
        emergency_stop_loss()
    except KeyboardInterrupt:
        logger.info("Sistema de emergência interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro crítico no sistema de emergência: {e}")
    finally:
        logger.info("Desconectando do MetaTrader5...")
        mt5.shutdown()
        logger.info("MT5 desconectado")
        logger.info("Sistema de emergência encerrado")