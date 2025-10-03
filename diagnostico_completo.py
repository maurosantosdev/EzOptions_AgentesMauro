"""
DIAGNÓSTICO COMPLETO DO SISTEMA DE TRADING
Executar este arquivo antes de iniciar qualquer sistema de trading
"""

import MetaTrader5 as mt5
import time
import os
from dotenv import load_dotenv
import logging
import sys
import psutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnostico_completo.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SistemaDiagnostico:
    """Sistema completo de diagnóstico para MT5 e ambiente"""

    def __init__(self):
        load_dotenv()
        self.symbol = 'US100'
        self.diagnostics_results = {}

    def check_environment_variables(self):
        """Verificar variáveis de ambiente"""
        logger.info("=== VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE ===")

        required_vars = {
            'MT5_LOGIN': 'Login MT5',
            'MT5_SERVER': 'Servidor MT5',
            'MT5_PASSWORD': 'Senha MT5'
        }

        all_ok = True
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                logger.info(f"✅ {description}: OK")
            else:
                logger.error(f"❌ {description}: FALTANDO")
                all_ok = False

        return all_ok

    def check_system_resources(self):
        """Verificar recursos do sistema"""
        logger.info("=== VERIFICAÇÃO DE RECURSOS DO SISTEMA ===")

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            logger.info(f"CPU: {cpu_percent}%")
            logger.info(f"Memória: {memory.percent}% ({memory.available / 1024**3:.1f} GB disponível)")
            logger.info(f"Disco: {disk.percent}% ({disk.free / 1024**3:.1f} GB disponível)")

            # Avisos se recursos estiverem altos
            if cpu_percent > 80:
                logger.warning("⚠️  CPU acima de 80% - pode afetar performance")
            if memory.percent > 80:
                logger.warning("⚠️  Memória acima de 80% - pode causar travamentos")
            if disk.percent > 90:
                logger.warning("⚠️  Disco acima de 90% - pode causar problemas")

            return True

        except Exception as e:
            logger.error(f"Erro ao verificar recursos: {e}")
            return False

    def check_mt5_installation(self):
        """Verificar instalação do MT5"""
        logger.info("=== VERIFICAÇÃO DE INSTALAÇÃO MT5 ===")

        try:
            # Tentar importar
            import MetaTrader5
            logger.info("✅ MetaTrader5: Importado com sucesso")

            # Verificar versão
            version = mt5.version()
            logger.info(f"✅ MT5 Versão: {version}")

            return True

        except ImportError:
            logger.error("❌ MetaTrader5: Não instalado")
            logger.error("Instale com: pip install MetaTrader5")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar MT5: {e}")
            return False

    def test_mt5_connection(self):
        """Testar conexão MT5 completa"""
        logger.info("=== TESTE DE CONEXÃO MT5 ===")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1}/{max_retries}")

                # 1. Shutdown se já inicializado
                try:
                    mt5.shutdown()
                    time.sleep(1)
                except:
                    pass

                # 2. Inicializar
                if not mt5.initialize():
                    logger.error("❌ Falha na inicialização MT5")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return False

                logger.info("✅ MT5 inicializado")

                # 3. Aguardar estabilização
                time.sleep(2)

                # 4. Login
                login = int(os.getenv("MT5_LOGIN"))
                server = os.getenv("MT5_SERVER")
                password = os.getenv("MT5_PASSWORD")

                if mt5.login(login, password, server):
                    logger.info("✅ Login MT5: Sucesso")

                    # 5. Teste de informações da conta
                    account_info = mt5.account_info()
                    if account_info:
                        logger.info(f"✅ Conta OK - Saldo: ${account_info.balance:.2f}")
                        logger.info(f"✅ Servidor: {account_info.server}")
                    else:
                        logger.error("❌ Não foi possível obter informações da conta")
                        return False

                    # 6. Teste de informações do símbolo
                    symbol_info = mt5.symbol_info(self.symbol)
                    if symbol_info:
                        logger.info(f"✅ Símbolo OK - Spread: {symbol_info.spread}")
                        logger.info(f"✅ Stops Level: {symbol_info.trade_stops_level}")
                    else:
                        logger.error(f"❌ Símbolo {self.symbol} não encontrado")
                        return False

                    # 7. Teste de tick
                    tick = mt5.symbol_info_tick(self.symbol)
                    if tick:
                        logger.info(f"✅ Tick OK - Preço: {tick.last}")
                        logger.info(f"✅ Bid: {tick.bid} | Ask: {tick.ask}")
                    else:
                        logger.error("❌ Não foi possível obter tick")
                        return False

                    # 8. Teste de histórico
                    rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 10)
                    if rates is not None and len(rates) > 0:
                        logger.info(f"✅ Histórico OK - {len(rates)} candles obtidos")
                    else:
                        logger.error("❌ Não foi possível obter histórico")
                        return False

                    # 9. Teste de ordem simulada
                    try:
                        test_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": self.symbol,
                            "volume": 0.01,
                            "type": mt5.ORDER_TYPE_BUY,
                            "price": tick.ask,
                            "type_filling": mt5.ORDER_FILLING_RETURN,
                            "magic": 999999
                        }

                        check_result = mt5.order_check(test_request)
                        if check_result:
                            logger.info(f"✅ Verificação de ordem OK - Retcode: {check_result.retcode}")
                        else:
                            logger.warning("⚠️  Não foi possível verificar ordem")

                    except Exception as e:
                        logger.warning(f"⚠️  Erro no teste de ordem: {e}")

                    logger.info("✅ CONEXÃO MT5 TOTALMENTE FUNCIONAL!")
                    return True

                else:
                    logger.error("❌ Falha no login MT5")
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    return False

            except Exception as e:
                logger.error(f"❌ Exceção no teste: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return False

        return False

    def check_market_hours(self):
        """Verificar horário de mercado"""
        logger.info("=== VERIFICAÇÃO DE HORÁRIO DE MERCADO ===")

        try:
            from datetime import datetime, time as dt_time
            import pytz

            ny_tz = pytz.timezone('America/New_York')
            now_ny = datetime.now(ny_tz)
            current_time = now_ny.time()

            # Horário de NY (US100)
            market_open = dt_time(9, 30, 0)
            market_close = dt_time(16, 0, 0)

            logger.info(f"Horário atual NY: {current_time}")

            if market_open <= current_time <= market_close:
                logger.info("✅ Mercado ABERTO - Operação permitida")
                return True
            else:
                logger.info("❌ Mercado FECHADO - Fora do horário de operação")
                return False

        except Exception as e:
            logger.error(f"Erro ao verificar horário: {e}")
            return False

    def run_full_diagnostics(self):
        """Executar diagnóstico completo"""
        logger.info("🚀 INICIANDO DIAGNÓSTICO COMPLETO DO SISTEMA")
        logger.info("=" * 60)

        results = {
            'environment': False,
            'system_resources': False,
            'mt5_installation': False,
            'mt5_connection': False,
            'market_hours': False,
            'overall_status': "FALHOU"
        }

        # 1. Variáveis de ambiente
        results['environment'] = self.check_environment_variables()

        # 2. Recursos do sistema
        results['system_resources'] = self.check_system_resources()

        # 3. Instalação MT5
        results['mt5_installation'] = self.check_mt5_installation()

        # 4. Conexão MT5 (só se instalação OK)
        if results['mt5_installation']:
            results['mt5_connection'] = self.test_mt5_connection()
        else:
            logger.error("Pulando teste de conexão - MT5 não instalado")

        # 5. Horário de mercado
        results['market_hours'] = self.check_market_hours()

        # 6. Status geral
        all_critical_ok = all([
            results['environment'],
            results['mt5_installation'],
            results['mt5_connection']
        ])

        if all_critical_ok:
            results['overall_status'] = "✅ SISTEMA OK - PRONTO PARA OPERAR"
            logger.info("🎉 DIAGNÓSTICO COMPLETO: SISTEMA OPERACIONAL!")
        else:
            results['overall_status'] = "❌ SISTEMA COM PROBLEMAS - VERIFIQUE LOGS"
            logger.error("💥 DIAGNÓSTICO COMPLETO: PROBLEMAS DETECTADOS!")

        # Resumo final
        logger.info("=" * 60)
        logger.info("RESUMO DO DIAGNÓSTICO:")
        for key, value in results.items():
            status = "✅ OK" if value is True else "❌ FALHOU" if value is False else value
            logger.info(f"{key.upper()}: {status}")

        logger.info("=" * 60)

        return results['overall_status'] == "✅ SISTEMA OK - PRONTO PARA OPERAR"

if __name__ == "__main__":
    diagnostico = SistemaDiagnostico()
    sistema_ok = diagnostico.run_full_diagnostics()

    if sistema_ok:
        logger.info("🎯 Sistema aprovado! Você pode iniciar os sistemas de trading.")
        logger.info("Comandos sugeridos:")
        logger.info("1. python emergency_stop_loss.py")
        logger.info("2. python sistema_lucro_final.py")
        logger.info("3. python -m streamlit run dashboard_completo.py --server.port 8502")
    else:
        logger.error("🚫 Sistema NÃO aprovado! Corrija os problemas antes de operar.")
        logger.error("Verifique o arquivo 'diagnostico_completo.log' para detalhes.")

    # Manter janela aberta
    input("Pressione ENTER para sair...")