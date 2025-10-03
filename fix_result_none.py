"""
CORREÇÃO ESPECÍFICA PARA O ERRO "Result = None"
Este arquivo implementa uma solução robusta para o problema de conexão MT5
"""

import MetaTrader5 as mt5
import time
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MT5ConnectionFix:
    """Classe específica para corrigir problemas de conexão MT5"""

    def __init__(self, symbol='US100'):
        self.symbol = symbol
        self.is_connected = False
        self.connection_attempts = 0
        self.max_connection_attempts = 10

    def shutdown_mt5(self):
        """Força o shutdown completo do MT5"""
        try:
            logger.info("🔄 Fazendo shutdown do MT5...")
            mt5.shutdown()
            time.sleep(2)
            logger.info("✅ Shutdown concluído")
            return True
        except Exception as e:
            logger.error(f"❌ Erro no shutdown: {e}")
            return False

    def initialize_mt5(self):
        """Inicializa MT5 com verificações extras"""
        try:
            logger.info("🔄 Inicializando MT5...")

            # Tentar inicialização
            if not mt5.initialize():
                logger.error("❌ Falha na inicialização do MT5")
                return False

            logger.info("✅ MT5 inicializado com sucesso")
            time.sleep(1)
            return True

        except Exception as e:
            logger.error(f"❌ Exceção na inicialização: {e}")
            return False

    def login_mt5(self, login, password, server):
        """Faz login no MT5 com retry"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                logger.info(f"🔑 Tentativa de login {attempt + 1}/{max_retries}")

                if mt5.login(login, password, server):
                    logger.info("✅ Login MT5 bem-sucedido")
                    return True
                else:
                    logger.error("❌ Falha no login MT5")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue

            except Exception as e:
                logger.error(f"❌ Exceção no login: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue

        return False

    def test_comprehensive_connection(self):
        """Teste abrangente da conexão MT5"""
        logger.info("🧪 Iniciando teste abrangente de conexão...")

        try:
            # Teste 1: Verificar informações da conta
            logger.info("Teste 1: Verificando informações da conta...")
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("❌ Não foi possível obter informações da conta")
                return False
            logger.info(f"✅ Conta OK - Saldo: ${account_info.balance:.2f}")

            # Teste 2: Verificar informações do símbolo
            logger.info("Teste 2: Verificando informações do símbolo...")
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                logger.error(f"❌ Não foi possível obter informações do símbolo {self.symbol}")
                return False
            logger.info(f"✅ Símbolo OK - Spread: {symbol_info.spread}")

            # Teste 3: Verificar tick atual
            logger.info("Teste 3: Verificando tick atual...")
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                logger.error("❌ Não foi possível obter tick do símbolo")
                return False
            logger.info(f"✅ Tick OK - Preço: {tick.last}")

            # Teste 4: Verificar histórico
            logger.info("Teste 4: Verificando histórico...")
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 5)
            if rates is None or len(rates) == 0:
                logger.error("❌ Não foi possível obter histórico")
                return False
            logger.info(f"✅ Histórico OK - {len(rates)} candles obtidos")

            # Teste 5: Verificar se símbolo está visível
            if not symbol_info.visible:
                logger.error("❌ Símbolo não está visível no Market Watch")
                return False
            logger.info("✅ Símbolo visível no Market Watch")

            logger.info("🎉 TODOS OS TESTES PASSARAM!")
            return True

        except Exception as e:
            logger.error(f"❌ Erro no teste abrangente: {e}")
            return False

    def fix_connection_issue(self):
        """Método principal para corrigir problemas de conexão"""
        logger.info("🔧 INICIANDO CORREÇÃO DE CONEXÃO MT5")
        logger.info("=" * 50)

        # 1. Shutdown completo
        self.shutdown_mt5()

        # 2. Inicializar
        if not self.initialize_mt5():
            logger.error("❌ Falha na inicialização")
            return False

        # 3. Login (usar variáveis de ambiente)
        import os
        from dotenv import load_dotenv
        load_dotenv()

        login = os.getenv("MT5_LOGIN")
        server = os.getenv("MT5_SERVER")
        password = os.getenv("MT5_PASSWORD")

        if not all([login, server, password]):
            logger.error("❌ Variáveis de ambiente MT5 não configuradas")
            return False

        if not self.login_mt5(login, password, server):
            logger.error("❌ Falha no login")
            return False

        # 4. Teste abrangente
        if not self.test_comprehensive_connection():
            logger.error("❌ Teste abrangente falhou")
            return False

        self.is_connected = True
        logger.info("✅ CONEXÃO MT5 TOTALMENTE FUNCIONAL!")
        return True

    def send_test_order(self):
        """Enviar uma ordem de teste para verificar se tudo está funcionando"""
        logger.info("📋 Enviando ordem de teste...")

        try:
            # Obter preço atual
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                logger.error("❌ Não foi possível obter preço para ordem de teste")
                return False

            # Configurar ordem de teste (volume muito pequeno)
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": 0.01,  # Volume muito pequeno
                "type": mt5.ORDER_TYPE_BUY,
                "price": tick.ask,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic": 999999,  # Magic number único para teste
                "comment": "TESTE DE CONEXÃO - NÃO EXECUTAR"
            }

            # Verificar se a ordem seria aceita (sem executar)
            check_result = mt5.order_check(request)
            if check_result:
                logger.info(f"✅ Verificação de ordem OK - Retcode: {check_result.retcode}")
                return True
            else:
                logger.error("❌ Verificação de ordem falhou")
                return False

        except Exception as e:
            logger.error(f"❌ Erro na ordem de teste: {e}")
            return False

def main():
    """Função principal"""
    logger.info("🚀 INICIANDO CORREÇÃO COMPLETA DO MT5")
    logger.info("=" * 60)

    fix = MT5ConnectionFix()

    # Tentar correção
    if fix.fix_connection_issue():
        logger.info("🎉 CORREÇÃO BEM-SUCEDIDA!")
        logger.info("✅ MT5 está funcionando perfeitamente")

        # Teste final de ordem
        fix.send_test_order()

        logger.info("💡 Sistema pronto para operar!")
        logger.info("Você pode agora executar:")
        logger.info("- python sistema_lucro_final.py")
        logger.info("- python real_agent_system.py")

    else:
        logger.error("💥 FALHA NA CORREÇÃO!")
        logger.error("❌ Verifique:")
        logger.error("   - Credenciais MT5 no arquivo .env")
        logger.error("   - Conexão com a internet")
        logger.error("   - MT5 instalado e funcionando")
        logger.error("   - Corretora online")

    logger.info("=" * 60)
    input("Pressione ENTER para sair...")

if __name__ == "__main__":
    main()