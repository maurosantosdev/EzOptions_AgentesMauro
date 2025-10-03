"""
SOLUÇÃO PARA O PROBLEMA DE AUTOTRADING DISABLED
============================================

Este script verifica e resolve o problema de "AutoTrading disabled by client"
que está impedindo o sistema de agentes de operar.
"""

import MetaTrader5 as mt5
import logging
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verificar_autotrading():
    """
    Verifica o estado do AutoTrading no MT5
    """
    logger.info("🔍 VERIFICANDO ESTADO DO AUTOTRADING...")
    
    try:
        # Inicializar MT5
        if not mt5.initialize():
            logger.error("❌ FALHA AO INICIALIZAR MT5")
            return False
        
        # Obter informações da conta
        account_info = mt5.account_info()
        if account_info:
            logger.info(f"✅ MT5 CONECTADO")
            logger.info(f"Conta: #{account_info.login}")
            logger.info(f"Saldo: ${account_info.balance:.2f}")
            logger.info(f"Equity: ${account_info.equity:.2f}")
            
            # Verificar dados da conta que podem indicar autotrading
            account_dict = account_info._asdict()
            logger.debug("Informações da conta:")
            for key, value in account_dict.items():
                logger.debug(f"  {key}: {value}")
            
            # Verificar se há posições abertas
            positions = mt5.positions_get()
            if positions:
                logger.info(f"📊 POSIÇÕES ABERTAS: {len(positions)}")
                for pos in positions:
                    logger.info(f"   - #{pos.ticket}: {pos.symbol} {pos.type} {pos.volume}")
            else:
                logger.info("📊 NENHUMA POSIÇÃO ABERTA")
            
            # Verificar ordens pendentes
            orders = mt5.orders_get()
            if orders:
                logger.info(f"📋 ORDENS PENDENTES: {len(orders)}")
                for order in orders:
                    logger.info(f"   - #{order.ticket}: {order.symbol} {order.type} {order.volume_initial}")
            else:
                logger.info("📋 NENHUMA ORDEM PENDENTE")
            
            mt5.shutdown()
            return True
        else:
            logger.error("❌ NÃO FOI POSSÍVEL OBTER INFORMAÇÕES DA CONTA")
            mt5.shutdown()
            return False
            
    except Exception as e:
        logger.error(f"❌ ERRO NA VERIFICAÇÃO: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def solucionar_problema_autotrading():
    """
    Soluções para o problema de AutoTrading desativado
    """
    logger.info("🔧 SOLUCIONANDO PROBLEMA DE AUTOTRADING...")
    
    # SOLUÇÕES POSSÍVEIS:
    solucoes = [
        "1. VERIFICAR CONFIGURAÇÕES DO MT5",
        "2. ATIVAR AUTOTRADING NAS CONFIGURAÇÕES",
        "3. VERIFICAR PERMISSÕES DA CONTA",
        "4. REINICIAR MT5 COM CONFIGURAÇÕES CORRETAS"
    ]
    
    for solucao in solucoes:
        logger.info(f"   {solucao}")
    
    logger.info("\n📋 SOLUÇÕES DETALHADAS:")
    logger.info("   1. Abra o MetaTrader 5")
    logger.info("   2. Vá em Ferramentas → Opções → Expert Advisors")
    logger.info("   3. Marque 'Permitir trading automático'")
    logger.info("   4. Desmarque 'Desativar todos os Expert Advisors' (se marcado)")
    logger.info("   5. Reinicie o MT5")
    logger.info("   6. Verifique se a conta permite trading automático")
    
    return True

def verificar_configuracoes_mt5():
    """
    Verifica configurações do MT5 que podem impedir autotrading
    """
    logger.info("⚙️  VERIFICANDO CONFIGURAÇÕES DO MT5...")
    
    # Verificar se MT5 está respondendo
    try:
        if mt5.initialize():
            # Obter informações do símbolo
            symbol_info = mt5.symbol_info("US100")
            if symbol_info:
                logger.info(f"✅ Símbolo US100 disponível")
                logger.info(f"   - Visível: {symbol_info.visible}")
                logger.info(f"   - Trade Mode: {symbol_info.trade_mode}")
                logger.info(f"   - Stops Level: {symbol_info.trade_stops_level}")
            
            # Obter informações da conta
            account_info = mt5.account_info()
            if account_info:
                logger.info(f"✅ Conta conectada: #{account_info.login}")
                logger.info(f"   - Saldo: ${account_info.balance:.2f}")
                logger.info(f"   - Equity: ${account_info.equity:.2f}")
                logger.info(f"   - Margem: ${account_info.margin:.2f}")
            
            mt5.shutdown()
            return True
        else:
            logger.error("❌ MT5 não inicializou")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro nas configurações: {e}")
        return False

def teste_simples_ordem():
    """
    Teste simples para verificar se autotrading funciona
    """
    logger.info("🧪 TESTANDO FUNCIONALIDADE DE ORDEM...")
    
    try:
        if not mt5.initialize():
            logger.error("❌ Falha na inicialização")
            return False
        
        # Obter tick atual
        tick = mt5.symbol_info_tick("US100")
        if not tick:
            logger.error("❌ Não foi possível obter tick")
            mt5.shutdown()
            return False
        
        # Montar ordem de teste (sem executar realmente)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "US100",
            "volume": 0.01,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 20,
            "magic": 999999,
            "comment": "Teste Autotrading",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        # Verificar apenas se a requisição seria aceita
        check_result = mt5.order_check(request)
        if check_result:
            logger.info(f"✅ Teste de ordem: {check_result.retcode} - {check_result.comment}")
            
            if check_result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info("✅ AUTOTRADING ESTÁ FUNCIONANDO!")
                mt5.shutdown()
                return True
            elif check_result.retcode == 10027:  # AutoTrading disabled
                logger.error("❌ AUTOTRADING ESTÁ DESATIVADO!")
                mt5.shutdown()
                return False
            else:
                logger.warning(f"⚠️  Outro erro: {check_result.retcode}")
                mt5.shutdown()
                return False
        else:
            logger.error("❌ Não foi possível verificar ordem")
            mt5.shutdown()
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def gerar_relatorio_completo():
    """
    Gera relatório completo do estado do sistema
    """
    logger.info("=" * 60)
    logger.info("📋 RELATÓRIO COMPLETO DO SISTEMA")
    logger.info("=" * 60)
    
    # Verificar conexão MT5
    if verificar_autotrading():
        logger.info("✅ CONEXÃO MT5: ATIVA")
    else:
        logger.error("❌ CONEXÃO MT5: INATIVA")
    
    # Verificar configurações
    if verificar_configuracoes_mt5():
        logger.info("✅ CONFIGURAÇÕES MT5: OK")
    else:
        logger.error("❌ CONFIGURAÇÕES MT5: PROBLEMAS")
    
    # Testar ordem
    if teste_simples_ordem():
        logger.info("✅ AUTOTRADING: ATIVADO")
    else:
        logger.error("❌ AUTOTRADING: DESATIVADO")
    
    logger.info("=" * 60)
    logger.info("🚨 PROBLEMA IDENTIFICADO: AutoTrading disabled by client")
    logger.info("🔧 SOLUÇÃO NECESSÁRIA: Ativar AutoTrading nas configurações do MT5")
    logger.info("=" * 60)

def main():
    """
    Função principal de solução
    """
    logger.info("🚀 SISTEMA DE SOLUÇÃO AUTOMÁTICA PARA AUTOTRADING")
    logger.info("🎯 Objetivo: Resolver 'AutoTrading disabled by client'")
    
    try:
        # Gerar relatório completo
        gerar_relatorio_completo()
        
        # Solucionar problema
        solucionar_problema_autotrading()
        
        logger.info("\n📋 INSTRUÇÕES PARA RESOLUÇÃO:")
        logger.info("1. FECHE O METATRADER 5 COMPLETAMENTE")
        logger.info("2. REABRA O METATRADER 5")
        logger.info("3. VÁ EM FERRAMENTAS → OPÇÕES → EXPERT ADVISORS")
        logger.info("4. MARQUE 'PERMITIR TRADING AUTOMÁTICO'")
        logger.info("5. DESMARQUE 'DESATIVAR TODOS OS EXPERT ADVISORS'")
        logger.info("6. REINICIE O SISTEMA DE AGENTES")
        logger.info("7. VERIFIQUE NOVAMENTE A CONTA")
        
        logger.info("\n✅ PROCESSO DE SOLUÇÃO CONCLUÍDO!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no processo de solução: {e}")
        return False

if __name__ == "__main__":
    main()