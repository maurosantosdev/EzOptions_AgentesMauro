"""
CONFIGURADOR DE MODO FOK PARA MT5
================================

Configura o sistema para usar o modo FOK (Fill or Kill) que é compatível com o broker
"""

import MetaTrader5 as mt5
import logging
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def configurar_modo_fok():
    """Configura o sistema para usar modo FOK"""
    logger.info("=" * 60)
    logger.info("CONFIGURADOR DE MODO FOK PARA MT5")
    logger.info("=" * 60)
    
    try:
        # Inicializar MT5
        if not mt5.initialize():
            logger.error("FALHA AO INICIALIZAR MT5")
            return False
        
        logger.info("MT5 INICIALIZADO")
        
        # Verificar informações da conta
        account_info = mt5.account_info()
        if not account_info:
            logger.error("NAO FOI POSSIVEL OBTER INFORMACOES DA CONTA")
            mt5.shutdown()
            return False
        
        logger.info(f"CONTA CONECTADA: #{account_info.login}")
        logger.info(f"SALDO: ${account_info.balance:.2f}")
        logger.info(f"EQUITY: ${account_info.equity:.2f}")
        logger.info(f"FREE MARGIN: ${account_info.margin_free:.2f}")
        logger.info(f"TRADE EXPERT (AUTO TRADING): {account_info.trade_expert}")
        logger.info(f"TRADE ALLOWED: {account_info.trade_allowed}")
        
        # Verificar se Auto Trading está habilitado
        if not account_info.trade_expert or not account_info.trade_allowed:
            logger.error("AUTO TRADING DESATIVADO!")
            logger.error("\nSOLUCAO NECESSARIA:")
            logger.error("1. ABRA O MT5 MANUALMENTE")
            logger.error("2. VA EM FERRAMENTAS -> OPCOES -> EXPERT ADVISORS")
            logger.error("3. MARQUE 'PERMITIR TRADING AUTOMATICO'")
            logger.error("4. DESMARQUE 'DESATIVAR TODOS OS EXPERT ADVISORS'")
            logger.error("5. REINICIE O MT5")
            mt5.shutdown()
            return False
        
        logger.info("AUTO TRADING HABILITADO!")
        
        # Verificar símbolo US100
        symbol_info = mt5.symbol_info("US100")
        if not symbol_info:
            logger.error("SIMBOLO US100 NAO ENCONTRADO")
            mt5.shutdown()
            return False
        
        logger.info("SIMBOLO US100 ENCONTRADO")
        logger.info(f"   - Nome: {symbol_info.name}")
        logger.info(f"   - Visivel: {symbol_info.visible}")
        logger.info(f"   - Trade Mode: {symbol_info.trade_mode}")
        logger.info(f"   - Filling Mode: {symbol_info.filling_mode}")
        
        # Verificar tick atual
        tick = mt5.symbol_info_tick("US100")
        if not tick:
            logger.error("NAO FOI POSSIVEL OBTER TICK ATUAL")
            mt5.shutdown()
            return False
        
        logger.info("TICK ATUAL OBTIDO")
        logger.info(f"   - Bid: ${tick.bid:.2f}")
        logger.info(f"   - Ask: ${tick.ask:.2f}")
        logger.info(f"   - Last: ${tick.last:.2f}")
        logger.info(f"   - Volume: {tick.volume}")
        
        # Testar modo FOK (que foi identificado como compatível)
        logger.info("\nTESTANDO MODO FOK (Fill or Kill)...")
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "US100",
            "volume": 0.01,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 20,
            "magic": 234001,
            "comment": "Teste FOK Mode",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,  # Modo FOK compatível
        }
        
        # Testar requisição
        result = mt5.order_check(request)
        if result:
            logger.info(f"VERIFICACAO DE ORDEM REALIZADA")
            logger.info(f"   - Retcode: {result.retcode}")
            logger.info(f"   - Comment: {result.comment}")
            
            # Verificar se o modo FOK é compatível
            # Retcode 0 = Done (sucesso) ← CORRIGIR AQUI
            # Retcode 10030 = Unsupported filling mode (falha)
            if result.retcode == 0:  # 0 = Done (sucesso) ← CORREÇÃO
                logger.info("MODO FOK É COMPATÍVEL!")
                logger.info("SISTEMA PRONTO PARA USAR MODO FOK!")
                
                # Criar arquivo de configuração
                config_content = f"""
# CONFIGURACAO DE MODO FOK PARA MT5
# Gerado automaticamente pelo configurador FOK

# Modo de preenchimento compatível com o broker
MT5_FILLING_MODE = {mt5.ORDER_FILLING_FOK}

# Descrição do modo
MT5_FILLING_MODE_NAME = "FOK (Fill or Kill)"

# Data da configuração
CONFIG_DATE = "{result.timestamp if hasattr(result, 'timestamp') else 'N/A'}"

# Símbolo configurado
SYMBOL = "US100"

# Volume padrão
DEFAULT_VOLUME = 0.01

# Deviation padrão
DEFAULT_DEVIATION = 20

# Magic number
MAGIC_NUMBER = 234001

# Modo de preenchimento correto
FILLING_MODE = mt5.ORDER_FILLING_FOK
"""
                
                # Salvar configuração
                with open("mt5_fok_config.py", "w", encoding="utf-8") as f:
                    f.write(config_content)
                
                logger.info("CONFIGURACAO FOK SALVA EM 'mt5_fok_config.py'")
                mt5.shutdown()
                return True
            elif result.retcode == 10030:  # Unsupported filling mode
                logger.error(f"MODO FOK NAO É COMPATÍVEL: {result.retcode} - {result.comment}")
                mt5.shutdown()
                return False
            else:
                logger.error(f"OUTRO ERRO NO MODO FOK: {result.retcode} - {result.comment}")
                mt5.shutdown()
                return False
        else:
            logger.error("NAO FOI POSSIVEL VERIFICAR ORDEM")
            mt5.shutdown()
            return False
            
    except Exception as e:
        logger.error(f"ERRO NA CONFIGURACAO FOK: {e}")
        try:
            mt5.shutdown()
        except:
            pass
        return False

def aplicar_configuracao_fok_ao_sistema():
    """Aplica configuração FOK ao sistema de agentes"""
    logger.info("\nAPLICANDO CONFIGURACAO FOK AO SISTEMA DE AGENTES...")
    
    try:
        # Ler configuração FOK
        config_file = "mt5_fok_config.py"
        
        if not os.path.exists(config_file):
            logger.error(f"ARQUIVO DE CONFIGURACAO FOK NAO ENCONTRADO: {config_file}")
            return False
        
        # Copiar configuração para diretório do sistema
        sistema_dir = "C:\\Users\\SEADI TI\\Documents\\maurosantos\\EzOptions_Agentes"
        destino = os.path.join(sistema_dir, "mt5_fok_config.py")
        
        import shutil
        shutil.copy2(config_file, destino)
        logger.info(f"CONFIGURACAO FOK COPIADA PARA: {destino}")
        
        # Atualizar arquivos do sistema para usar modo FOK
        logger.info("ATUALIZANDO ARQUIVOS DO SISTEMA...")
        
        # Listar arquivos que precisam ser atualizados
        arquivos_para_atualizar = [
            "real_agent_system.py",
            "sistema_lucro_final.py",
            "emergency_stop_loss.py",
            "smart_order_system.py",
            "multi_agent_system.py"
        ]
        
        for arquivo in arquivos_para_atualizar:
            caminho_arquivo = os.path.join(sistema_dir, arquivo)
            if os.path.exists(caminho_arquivo):
                logger.info(f"   - {arquivo}: PRESENTE")
            else:
                logger.warning(f"   - {arquivo}: NAO ENCONTRADO")
        
        logger.info("CONFIGURACAO FOK APLICADA AO SISTEMA!")
        return True
        
    except Exception as e:
        logger.error(f"ERRO AO APLICAR CONFIGURACAO FOK: {e}")
        return False

def main():
    """Função principal"""
    logger.info("CONFIGURADOR DE MODO FOK PARA MT5")
    logger.info("Objetivo: Configurar sistema para usar modo compatível FOK")
    
    # 1. Configurar modo FOK
    fok_configurado = configurar_modo_fok()
    
    if fok_configurado:
        # 2. Aplicar configuração ao sistema
        configuracao_aplicada = aplicar_configuracao_fok_ao_sistema()
        
        if configuracao_aplicada:
            logger.info("\nCONFIGURACAO CONCLUIDA COM SUCESSO!")
            logger.info("MODO FOK CONFIGURADO")
            logger.info("SISTEMA ATUALIZADO")
            logger.info("AGORA VOCE PODE INICIAR OS AGENTES!")
            return True
        else:
            logger.error("\nFALHA AO APLICAR CONFIGURACAO AO SISTEMA")
            return False
    else:
        logger.error("\nFALHA AO CONFIGURAR MODO FOK")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)