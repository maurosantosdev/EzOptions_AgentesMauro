"""
DIAGNÓSTICO MT5 - Sistema para identificar problemas de conexão e execução de ordens
Executar este arquivo para diagnosticar problemas antes de operar
"""

import MetaTrader5 as mt5
import time
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MT5Diagnostics:
    def __init__(self):
        load_dotenv()
        self.symbol = 'US100'
        self.test_results = {}

    def test_connection(self):
        """Testa conexão básica com MT5"""
        logger.info("=== TESTE 1: CONEXÃO MT5 ===")

        try:
            # Verificar se MT5 já está inicializado
            if not mt5.initialize():
                logger.error("❌ MT5 não conseguiu inicializar")
                return False
            else:
                logger.info("✅ MT5 inicializado com sucesso")

            # Teste de login
            login = int(os.getenv("MT5_LOGIN"))
            server = os.getenv("MT5_SERVER")
            password = os.getenv("MT5_PASSWORD")

            logger.info(f"🔍 Tentando login: {login}@{server}")

            if mt5.login(login, password, server):
                logger.info("✅ Login MT5 bem-sucedido")
                self.test_results['connection'] = True
                return True
            else:
                logger.error("❌ Falha no login MT5")
                self.test_results['connection'] = False
                return False

        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            self.test_results['connection'] = False
            return False

    def test_account_info(self):
        """Testa obtenção de informações da conta"""
        logger.info("\n=== TESTE 2: INFORMAÇÕES DA CONTA ===")

        try:
            account_info = mt5.account_info()
            if account_info:
                logger.info("✅ Informações da conta obtidas:")
                logger.info(f"   Saldo: ${account_info.balance:.2f}")
                logger.info(f"   Equity: ${account_info.equity:.2f}")
                logger.info(f"   Lucro: ${account_info.profit:.2f}")
                logger.info(f"   Servidor: {account_info.server}")
                self.test_results['account'] = True
                return True
            else:
                logger.error("❌ Não foi possível obter informações da conta")
                self.test_results['account'] = False
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao obter informações da conta: {e}")
            self.test_results['account'] = False
            return False

    def test_symbol_info(self):
        """Testa informações do símbolo"""
        logger.info(f"\n=== TESTE 3: INFORMAÇÕES DO SÍMBOLO {self.symbol} ===")

        try:
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info:
                logger.info("✅ Informações do símbolo obtidas:")
                logger.info(f"   Visível: {symbol_info.visible}")
                logger.info(f"   Modo de trading: {symbol_info.trade_mode}")
                logger.info(f"   Point: {symbol_info.point}")
                logger.info(f"   Stops Level: {symbol_info.trade_stops_level}")
                logger.info(f"   Bid: {symbol_info.bid}")
                logger.info(f"   Ask: {symbol_info.ask}")
                self.test_results['symbol'] = True
                return True
            else:
                logger.error(f"❌ Símbolo {self.symbol} não encontrado")
                self.test_results['symbol'] = False
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao obter informações do símbolo: {e}")
            self.test_results['symbol'] = False
            return False

    def test_price_tick(self):
        """Testa obtenção de preços em tempo real"""
        logger.info("\n=== TESTE 4: DADOS DE PREÇO EM TEMPO REAL ===")

        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick:
                logger.info("✅ Tick obtido com sucesso:")
                logger.info(f"   Último preço: {tick.last}")
                logger.info(f"   Bid: {tick.bid}")
                logger.info(f"   Ask: {tick.ask}")
                logger.info(f"   Spread: {tick.ask - tick.bid}")
                logger.info(f"   Volume: {tick.volume}")
                logger.info(f"   Tempo: {tick.time}")
                self.test_results['tick'] = True
                return True
            else:
                logger.error("❌ Não foi possível obter tick do símbolo")
                self.test_results['tick'] = False
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao obter tick: {e}")
            self.test_results['tick'] = False
            return False

    def test_order_validation(self):
        """Testa se ordens podem ser validadas sem executar"""
        logger.info("\n=== TESTE 5: VALIDAÇÃO DE ORDENS ===")

        try:
            # Obter preço atual
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                logger.error("❌ Não foi possível obter preço para teste de ordem")
                return False

            # Criar requisição de teste (ordem de compra)
            test_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": 0.01,
                "type": mt5.ORDER_TYPE_BUY,
                "price": tick.ask,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic": 999999
            }

            # Testar se a ordem seria aceita
            check_result = mt5.order_check(test_request)

            if check_result:
                if check_result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info("✅ Ordem pode ser executada:")
                    logger.info(f"   Comentário: {check_result.comment}")
                    self.test_results['order_validation'] = True
                    return True
                else:
                    logger.warning(f"⚠️  Ordem seria rejeitada: {check_result.comment} (Código: {check_result.retcode})")
                    self.test_results['order_validation'] = False
                    return False
            else:
                logger.error("❌ Erro na validação da ordem")
                self.test_results['order_validation'] = False
                return False

        except Exception as e:
            logger.error(f"❌ Erro no teste de validação: {e}")
            self.test_results['order_validation'] = False
            return False

    def test_positions_and_orders(self):
        """Testa obtenção de posições e ordens existentes"""
        logger.info("\n=== TESTE 6: POSIÇÕES E ORDENS ===")

        try:
            # Verificar posições
            positions = mt5.positions_get()
            if positions:
                logger.info(f"✅ {len(positions)} posições encontradas")
                for pos in positions[:3]:  # Mostrar apenas primeiras 3
                    logger.info(f"   Posição: {pos.symbol} {pos.type} {pos.volume} @ {pos.price_open}")
            else:
                logger.info("ℹ️  Nenhuma posição aberta")

            # Verificar ordens pendentes
            orders = mt5.orders_get()
            if orders:
                logger.info(f"✅ {len(orders)} ordens pendentes encontradas")
                for order in orders[:3]:  # Mostrar apenas primeiras 3
                    logger.info(f"   Ordem: {order.symbol} {order.type} {order.volume_initial}")
            else:
                logger.info("ℹ️  Nenhuma ordem pendente")

            self.test_results['positions_orders'] = True
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao verificar posições/ordens: {e}")
            self.test_results['positions_orders'] = False
            return False

    def run_full_diagnostic(self):
        """Executa diagnóstico completo"""
        logger.info("🚀 INICIANDO DIAGNÓSTICO COMPLETO DO MT5")
        logger.info("=" * 50)

        # Executar todos os testes
        tests = [
            ("Conexão MT5", self.test_connection),
            ("Informações da Conta", self.test_account_info),
            ("Informações do Símbolo", self.test_symbol_info),
            ("Dados de Preço", self.test_price_tick),
            ("Validação de Ordens", self.test_order_validation),
            ("Posições e Ordens", self.test_positions_and_orders)
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                logger.error(f"❌ Erro no teste {test_name}: {e}")
                results.append((test_name, False))

        # Resumo final
        logger.info("\n" + "=" * 50)
        logger.info("📊 RESUMO DO DIAGNÓSTICO:")

        passed = 0
        total = len(results)

        for test_name, result in results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            logger.info(f"   {test_name}: {status}")
            if result:
                passed += 1

        logger.info(f"\n🎯 RESULTADO GERAL: {passed}/{total} testes passaram")

        if passed == total:
            logger.info("🎉 MT5 está funcionando perfeitamente!")
            logger.info("✅ Sistema pronto para operar")
        elif passed >= total * 0.8:
            logger.warning("⚠️  MT5 funcionando com problemas menores")
            logger.warning("🔧 Verifique as configurações antes de operar")
        else:
            logger.error("❌ MT5 com problemas graves")
            logger.error("🛑 NÃO OPERE até resolver os problemas")

        # Recomendações
        self.print_recommendations(results)

        return passed == total

    def print_recommendations(self, results):
        """Imprime recomendações baseadas nos resultados"""
        logger.info("\n💡 RECOMENDAÇÕES:")

        failed_tests = [name for name, result in results if not result]

        if "Conexão MT5" in failed_tests:
            logger.error("   🔴 Verifique suas credenciais MT5 (login, senha, servidor)")
            logger.error("   🔴 Certifique-se de que o MT5 está instalado e funcionando")

        if "Informações da Conta" in failed_tests:
            logger.error("   🔴 Verifique se sua conta MT5 está ativa")
            logger.error("   🔴 Certifique-se de que você está logado na conta correta")

        if "Informações do Símbolo" in failed_tests:
            logger.error(f"   🔴 Verifique se o símbolo {self.symbol} existe na sua conta")
            logger.error("   🔴 Certifique-se de que o símbolo está habilitado para trading")

        if "Dados de Preço" in failed_tests:
            logger.error("   🔴 Verifique se o mercado está aberto")
            logger.error("   🔴 Verifique sua conexão com a internet")

        if "Validação de Ordens" in failed_tests:
            logger.error("   🔴 Verifique se sua conta permite ordens deste tipo")
            logger.error("   🔴 Verifique se há restrições na sua conta")

        if not failed_tests:
            logger.info("   ✅ Sistema MT5 funcionando perfeitamente")
            logger.info("   🚀 Pronto para iniciar operações")

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO MT5 - EzOptions Trading System")
    print("=" * 60)

    diagnostic = MT5Diagnostics()
    success = diagnostic.run_full_diagnostic()

    print("\n" + "=" * 60)
    if success:
        print("✅ DIAGNÓSTICO: SISTEMA OK - Pronto para operar!")
        return True
    else:
        print("❌ DIAGNÓSTICO: PROBLEMAS DETECTADOS - Verifique as recomendações acima")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Diagnóstico interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n💥 Erro crítico no diagnóstico: {e}")
        exit(1)